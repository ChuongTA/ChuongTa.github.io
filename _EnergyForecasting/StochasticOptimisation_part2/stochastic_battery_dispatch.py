"""
Two-stage stochastic battery dispatch on real DK1 day-ahead prices, using
real quantile forecasts (not hand-picked historical days) to build the
scenario set.

Reuses qr_qrf_walkforward_pipeline.py's data loading and feature
engineering (from the PEPF series) to fit Quantile Regression models at
five quantile levels, one model per hour of the target day, trained on
everything known before a fixed forecast origin (noon the day before
delivery, matching real day-ahead market timing).

Scenario construction: fixing the same quantile level across every hour
of the day gives one internally-consistent 24-hour price path per level
(a "low" scenario throughout the day, a "median" scenario throughout the
day, and so on), a standard simplification for turning marginal quantile
forecasts into a joint scenario set. Each of the five scenarios is given
equal probability (0.2), since the levels [0.10, 0.30, 0.50, 0.70, 0.90]
are evenly spaced.

The battery-dispatch problem itself is a two-stage stochastic program,
formulated and solved in Pyomo:
  - First-stage decision x = (charge, discharge) for every hour of the
    target day, committed once, shared across all scenarios.
  - Second-stage "decision" is just the realized profit under whichever
    scenario turns out to hold, there is no intraday recourse in this
    version (see the "What Is Simplified Here" section in the write-up).

Three schedules are computed and compared on the REAL realized price for
the target day: the stochastic (5-scenario) schedule, a naive schedule
built from the median forecast alone, and a perfect-foresight schedule
(an upper bound, computed using the actual realized prices).
"""
import os
import numpy as np
import pandas as pd
import pyomo.environ as pyo
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings("ignore")

import qr_qrf_walkforward_pipeline as base

script_dir = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(script_dir, "Results")
os.makedirs(RESULTS_DIR, exist_ok=True)

HOURS = 24
TARGET_DAY_START = pd.Timestamp("2025-07-10 00:00:00")
FORECAST_ORIGIN = pd.Timestamp("2025-07-09 12:00:00")  # day-ahead auction closes at noon
SCENARIO_QUANTILES = [0.10, 0.30, 0.50, 0.70, 0.90]
SCENARIO_PROB = {q: 0.2 for q in SCENARIO_QUANTILES}

BATTERY = {
    "power_mw": 1.0,
    "capacity_mwh": 2.0,
    "soc_min_frac": 0.10,
    "soc_max_frac": 0.90,
    "charge_efficiency": 0.95,
    "discharge_efficiency": 0.95,
    "initial_soc_frac": 0.50,
}


# ── Forecast each hour of the target day, from information at FORECAST_ORIGIN ──
def forecast_target_day():
    quantile_paths = {q: np.full(HOURS, np.nan) for q in SCENARIO_QUANTILES}
    actual_prices = np.full(HOURS, np.nan)

    for h in range(HOURS):
        target_time = TARGET_DAY_START + pd.Timedelta(hours=h)
        lead = int((target_time - FORECAST_ORIGIN).total_seconds() // 3600)

        df, all_features = base.build_feature_frame(lead)
        dates = df[base.DATE_COL]

        train_mask = dates < FORECAST_ORIGIN
        test_mask = dates == target_time

        X_train = df.loc[train_mask, all_features].values
        y_train = df.loc[train_mask, base.TARGET].values
        X_test = df.loc[test_mask, all_features].values

        fitted = base.fit_quantile_regression_models(X_train, y_train, SCENARIO_QUANTILES)
        preds = base.predict_quantile_regression(fitted, X_test)
        preds, _ = base.enforce_monotonicity(preds, SCENARIO_QUANTILES)

        for q in SCENARIO_QUANTILES:
            quantile_paths[q][h] = preds[q][0]

        actual_prices[h] = df.loc[test_mask, base.TARGET].values[0]

        print(f"  Hour {h:>2} (lead {lead}h): median forecast={preds[0.50][0]:.2f}  actual={actual_prices[h]:.2f}")

    return quantile_paths, actual_prices


# ── Two-stage stochastic dispatch, solved in Pyomo ───────────────────────────
def solve_dispatch(scenario_prices, probabilities):
    """
    scenario_prices: dict {scenario_label: array of length HOURS}
    probabilities: dict {scenario_label: probability}, must sum to 1.
    Returns (pc, pd_) arrays of length HOURS, the shared first-stage schedule.
    """
    scenarios = list(scenario_prices.keys())
    eta_c = BATTERY["charge_efficiency"]
    eta_d = BATTERY["discharge_efficiency"]
    p_max = BATTERY["power_mw"]
    e_max = BATTERY["capacity_mwh"] * BATTERY["soc_max_frac"]
    e_min = BATTERY["capacity_mwh"] * BATTERY["soc_min_frac"]
    e0 = BATTERY["capacity_mwh"] * BATTERY["initial_soc_frac"]

    m = pyo.ConcreteModel()
    m.T = pyo.RangeSet(0, HOURS - 1)

    m.pc = pyo.Var(m.T, bounds=(0, p_max))   # first-stage: charging power, shared across scenarios
    m.pd = pyo.Var(m.T, bounds=(0, p_max))   # first-stage: discharging power, shared across scenarios
    m.soc = pyo.Var(m.T, bounds=(e_min, e_max))

    def soc_rule(m, t):
        prev = e0 if t == 0 else m.soc[t - 1]
        return m.soc[t] == prev + eta_c * m.pc[t] - m.pd[t] / eta_d
    m.soc_con = pyo.Constraint(m.T, rule=soc_rule)

    expected_profit = sum(
        probabilities[s] * sum(scenario_prices[s][t] * (m.pd[t] - m.pc[t]) for t in range(HOURS))
        for s in scenarios
    )
    m.obj = pyo.Objective(expr=expected_profit, sense=pyo.maximize)

    solver = pyo.SolverFactory("appsi_highs")
    result = solver.solve(m)
    if str(result.solver.termination_condition) != "optimal":
        raise RuntimeError(f"Solve failed: {result.solver.termination_condition}")

    pc = np.array([pyo.value(m.pc[t]) for t in range(HOURS)])
    pd_ = np.array([pyo.value(m.pd[t]) for t in range(HOURS)])
    return pc, pd_


def realized_profit(pc, pd_, price_curve):
    return float(np.sum(price_curve * (pd_ - pc)))


def main():
    print(f"Forecast origin: {FORECAST_ORIGIN} (day-ahead auction close)")
    print(f"Target day: {TARGET_DAY_START.date()}")
    print("\nFitting Quantile Regression per hour and forecasting the target day...")
    quantile_paths, actual_prices = forecast_target_day()

    # ── Schedule 1: stochastic, 5 quantile-forecast scenarios ──────────────
    pc_stoch, pd_stoch = solve_dispatch(quantile_paths, SCENARIO_PROB)

    # ── Schedule 2: naive, median forecast treated as certain ──────────────
    naive_scenario = {"median": quantile_paths[0.50]}
    pc_naive, pd_naive = solve_dispatch(naive_scenario, {"median": 1.0})

    # ── Schedule 3: perfect foresight, actual realized prices (upper bound) ─
    perfect_scenario = {"actual": actual_prices}
    pc_perfect, pd_perfect = solve_dispatch(perfect_scenario, {"actual": 1.0})

    schedules = {
        "Stochastic (5 scenarios)": (pc_stoch, pd_stoch),
        "Naive (median forecast)": (pc_naive, pd_naive),
        "Perfect foresight": (pc_perfect, pd_perfect),
    }

    print("\n--- Expected profit in-sample (own scenario set) ---")
    exp_profit_stoch = sum(SCENARIO_PROB[q] * realized_profit(pc_stoch, pd_stoch, quantile_paths[q])
                            for q in SCENARIO_QUANTILES)
    print(f"Stochastic schedule, expected profit across its 5 scenarios: {exp_profit_stoch:.2f} EUR")

    print("\n--- Realized profit on the REAL target-day price ---")
    realized = {}
    for name, (pc, pd_) in schedules.items():
        profit = realized_profit(pc, pd_, actual_prices)
        realized[name] = profit
        print(f"{name:<28}: {profit:.2f} EUR")

    vss = realized["Stochastic (5 scenarios)"] - realized["Naive (median forecast)"]
    gap_to_perfect = realized["Perfect foresight"] - realized["Stochastic (5 scenarios)"]
    print(f"\nValue of the stochastic solution (stochastic - naive), realized: {vss:.2f} EUR")
    print(f"Gap to perfect foresight (upper bound - stochastic): {gap_to_perfect:.2f} EUR")

    # ── Save results ─────────────────────────────────────────────────────────
    hours_index = [TARGET_DAY_START + pd.Timedelta(hours=h) for h in range(HOURS)]
    schedule_df = pd.DataFrame({"datetime": hours_index, "actual_price": actual_prices})
    for q in SCENARIO_QUANTILES:
        schedule_df[f"forecast_q{int(q * 100)}"] = quantile_paths[q]
    for name, (pc, pd_) in schedules.items():
        col = name.split(" (")[0].lower().replace(" ", "_")
        schedule_df[f"pc_{col}"] = pc
        schedule_df[f"pd_{col}"] = pd_
    schedule_df.to_csv(os.path.join(RESULTS_DIR, "dispatch_schedules.csv"), index=False)

    summary_df = pd.DataFrame([
        {"schedule": name, "realized_profit_eur": profit}
        for name, profit in realized.items()
    ])
    summary_df.to_csv(os.path.join(RESULTS_DIR, "dispatch_summary.csv"), index=False)
    print(f"\nSaved: {RESULTS_DIR}/dispatch_schedules.csv")
    print(f"Saved: {RESULTS_DIR}/dispatch_summary.csv")

    # ── Plot 1: the five scenario paths vs. the real realized price ────────
    fig, ax = plt.subplots(figsize=(9, 4.5))
    colors = {0.10: "#c8d6e8", 0.30: "#8ca0c4", 0.50: "#1f3b57", 0.70: "#8ca0c4", 0.90: "#c8d6e8"}
    for q in SCENARIO_QUANTILES:
        lw = 2.2 if q == 0.50 else 1.3
        ax.plot(hours_index, quantile_paths[q], color=colors[q], linewidth=lw,
                label=f"q{int(q * 100)} forecast" if q != 0.50 else "Median forecast")
    ax.plot(hours_index, actual_prices, color="#d1495b", linewidth=2.2, linestyle="--", label="Actual price")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_xlabel("Hour of target day")
    ax.set_ylabel("Price (EUR/MWh)")
    ax.set_title(f"Quantile-forecast scenarios vs. actual price, {TARGET_DAY_START.date()}")
    ax.legend(loc="upper left", frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig_scenarios_vs_actual.png"), dpi=160)
    plt.close(fig)

    # ── Plot 2: dispatch comparison on the real price ───────────────────────
    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    ax1.plot(hours_index, actual_prices, color="#1f3b57", linewidth=2, label="Actual price")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax1.set_xlabel("Hour of target day")
    ax1.set_ylabel("Price (EUR/MWh)")
    ax2 = ax1.twinx()
    line_styles = {"Stochastic (5 scenarios)": ("-", "#d1495b"),
                   "Naive (median forecast)": ("--", "#2a9d8f"),
                   "Perfect foresight": (":", "#555555")}
    for name, (pc, pd_) in schedules.items():
        ls, color = line_styles[name]
        ax2.step(hours_index, pd_ - pc, where="mid", color=color, linewidth=1.8, linestyle=ls, label=name)
    ax2.axhline(0, color="gray", linewidth=0.8)
    ax2.set_ylabel("Net power (MW), + = discharge")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False, fontsize=8)
    ax1.set_title(f"Battery dispatch on {TARGET_DAY_START.date()}: stochastic vs. naive vs. perfect foresight")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "fig_dispatch_comparison.png"), dpi=160)
    plt.close(fig)

    print(f"Saved: {RESULTS_DIR}/fig_scenarios_vs_actual.png")
    print(f"Saved: {RESULTS_DIR}/fig_dispatch_comparison.png")


if __name__ == "__main__":
    main()
