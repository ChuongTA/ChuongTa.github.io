"""
Deep dive on bootstrapped-residual prediction intervals for wave height
(swh / Hs), 24h ahead, on the most recent walk-forward fold.

Mirrors the structure of the skforecast tutorial "Probabilistic Forecasting:
Bootstrapped Residuals" (https://skforecast.org/0.15.0/user_guides/
probabilistic-forecasting-bootstrapped-residuals), adapted to our own
LightGBM point model and wave dataset instead of skforecast's ForecasterRecursive
and the bike-sharing dataset. Three residual strategies are compared on the
same train/validation/test split:

  1. In-sample residuals   : residuals computed on the TRAINING data itself.
                              Usually overoptimistic (intervals too narrow),
                              because the model already fit those points.
  2. Out-sample residuals  : residuals computed on the VALIDATION data
                              (out-of-fit). What bootstrap_residual_wave_pipeline.py
                              already uses. Wider, closer to nominal coverage,
                              but the same width for every test row regardless
                              of conditions (unconditional).
  3. Binned residuals      : out-of-sample residuals, but binned by the
                              point model's predicted value. A test row's
                              interval is built from the residuals of
                              validation rows whose predictions fell in the
                              same bin, so calm-condition predictions get a
                              narrower interval than storm-condition ones.
                              This is the fix for the "flat width" limitation
                              of method 2.

Only one target/lead/fold is used here (swh, 24h ahead, fold 6, the same
demo case as the fan chart in the main pipeline), since the point of this
script is to compare *methods*, not to repeat the full 72-combo grid.
"""
import os
import numpy as np
import pandas as pd
import lightgbm as lgb
import warnings
warnings.filterwarnings("ignore")

from bootstrap_deepdive_plots import (
    plot_prediction_interval, plot_residuals_by_bin,
    plot_method_comparison, plot_multiple_intervals_coverage,
)

# Reuse data loading, fold boundaries, and feature building from the main
# pipeline (importing this module only loads data and defines functions,
# it does not run the full 72-combo grid, that's guarded by __main__).
import bootstrap_residual_wave_pipeline as base

script_dir = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(script_dir, "Results", "DeepDive")
os.makedirs(RESULTS_DIR, exist_ok=True)

TARGET = "swh"
LEAD_H = 24
N_BINS = 15
N_BOOTSTRAP = 5000
NOMINAL_LEVELS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95]  # coverage %, central intervals


def empirical_coverage(y_true, lower, upper):
    return float(np.mean((y_true >= lower) & (y_true <= upper)))


def interval_area(lower, upper):
    return float(np.sum(upper - lower))


# ── Build the single demo split (fold 6, the most recent) ───────────────────
fold = base.fold_boundaries[-1]
X, y = base.build_lead_features(TARGET, LEAD_H)
valid_rows = X.notna().all(axis=1) & y.notna()
dates = base.t_idx

train_mask = (dates >= fold["train_start"]) & (dates <= fold["train_end"]) & valid_rows
valid_mask = (dates >= fold["valid_start"]) & (dates <= fold["valid_end"]) & valid_rows
test_mask = (dates >= fold["test_start"]) & (dates <= fold["test_end"]) & valid_rows

X_train, y_train = X.loc[train_mask].values, y.loc[train_mask].values
X_val, y_val = X.loc[valid_mask].values, y.loc[valid_mask].values
X_test, y_test = X.loc[test_mask].values, y.loc[test_mask].values
test_dates = dates.loc[test_mask].values

print(f"Demo case: target={TARGET}, lead={LEAD_H}h, fold {fold['fold']}")
print(f"train={len(y_train)}  valid={len(y_val)}  test={len(y_test)}")

# ── Fit ONE point model (same as the main bootstrap pipeline) ───────────────
model = lgb.LGBMRegressor(random_state=42, verbose=-1)
model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    callbacks=[lgb.early_stopping(stopping_rounds=15, verbose=False)],
)

pred_train = model.predict(X_train)
pred_val = model.predict(X_val)
pred_test = model.predict(X_test)

resid_train = y_train - pred_train
resid_val = y_val - pred_val

rng = np.random.default_rng(42)
LO, HI = 0.10, 0.90  # 80% central interval, matching the skforecast example


def bootstrap_offsets(residual_pool, quantiles, n_bootstrap, rng):
    boot = rng.choice(residual_pool, size=n_bootstrap, replace=True)
    return {q: float(np.quantile(boot, q)) for q in quantiles}


# ── 1. In-sample residuals ───────────────────────────────────────────────────
offsets_in_sample = bootstrap_offsets(resid_train, [LO, HI], N_BOOTSTRAP, rng)
lower_in, upper_in = pred_test + offsets_in_sample[LO], pred_test + offsets_in_sample[HI]
cov_in = empirical_coverage(y_test, lower_in, upper_in)
area_in = interval_area(lower_in, upper_in)
print(f"\n[1] In-sample residuals    | coverage={cov_in:.2%}  area={area_in:.2f}")

# ── 2. Out-sample residuals (non-conditioned) ───────────────────────────────
offsets_out_sample = bootstrap_offsets(resid_val, [LO, HI], N_BOOTSTRAP, rng)
lower_out, upper_out = pred_test + offsets_out_sample[LO], pred_test + offsets_out_sample[HI]
cov_out = empirical_coverage(y_test, lower_out, upper_out)
area_out = interval_area(lower_out, upper_out)
print(f"[2] Out-sample residuals   | coverage={cov_out:.2%}  area={area_out:.2f}")

# ── 3. Binned / conditional residuals ───────────────────────────────────────
# Quantile-based bin edges from the validation set's own predictions
bin_edges = np.unique(np.percentile(pred_val, np.linspace(0, 100, N_BINS + 1)))
bin_edges[0], bin_edges[-1] = -np.inf, np.inf
val_bin_idx = np.digitize(pred_val, bin_edges[1:-1], right=False)
test_bin_idx = np.digitize(pred_test, bin_edges[1:-1], right=False)

residuals_by_bin = {b: resid_val[val_bin_idx == b] for b in range(len(bin_edges) - 1)}
# Guard against near-empty bins by falling back to the global pool
for b, res in residuals_by_bin.items():
    if len(res) < 10:
        residuals_by_bin[b] = resid_val

lower_bin = np.empty_like(pred_test)
upper_bin = np.empty_like(pred_test)
for b in np.unique(test_bin_idx):
    mask = test_bin_idx == b
    offsets_b = bootstrap_offsets(residuals_by_bin[b], [LO, HI], N_BOOTSTRAP, rng)
    lower_bin[mask] = pred_test[mask] + offsets_b[LO]
    upper_bin[mask] = pred_test[mask] + offsets_b[HI]

cov_bin = empirical_coverage(y_test, lower_bin, upper_bin)
area_bin = interval_area(lower_bin, upper_bin)
print(f"[3] Binned residuals       | coverage={cov_bin:.2%}  area={area_bin:.2f}")

# ── Save comparison table ───────────────────────────────────────────────────
comparison_df = pd.DataFrame([
    {"Method": "In-sample residuals", "NominalCoverage": 0.80, "EmpiricalCoverage": cov_in, "IntervalArea": area_in},
    {"Method": "Out-sample residuals (non-conditioned)", "NominalCoverage": 0.80, "EmpiricalCoverage": cov_out, "IntervalArea": area_out},
    {"Method": "Out-sample residuals (binned)", "NominalCoverage": 0.80, "EmpiricalCoverage": cov_bin, "IntervalArea": area_bin},
])
comparison_path = os.path.join(RESULTS_DIR, "method_comparison.csv")
comparison_df.to_csv(comparison_path, index=False)
print(f"\nSaved method comparison to: {comparison_path}")

# ── Plots ────────────────────────────────────────────────────────────────────
unit, label = ("m", "Hs (swh)") if TARGET == "swh" else ("s", "Te (mwp)")
ylabel = f"{label} ({unit})"

plot_prediction_interval(test_dates, y_test, lower_in, upper_in, pred_test,
                          "In-sample residuals (overconfident)",
                          os.path.join(RESULTS_DIR, "interval_in_sample.png"), ylabel=ylabel, color="#EF9A9A")
plot_prediction_interval(test_dates, y_test, lower_out, upper_out, pred_test,
                          "Out-sample residuals (non-conditioned)",
                          os.path.join(RESULTS_DIR, "interval_out_sample.png"), ylabel=ylabel, color="#90CAF9")
plot_prediction_interval(test_dates, y_test, lower_bin, upper_bin, pred_test,
                          "Out-sample residuals (binned / conditional)",
                          os.path.join(RESULTS_DIR, "interval_binned.png"), ylabel=ylabel, color="#A5D6A7")

plot_method_comparison(test_dates, y_test, {
    "In-sample residuals": (lower_in, upper_in, pred_test, "#EF9A9A"),
    "Out-sample residuals (non-conditioned)": (lower_out, upper_out, pred_test, "#90CAF9"),
    "Out-sample residuals (binned)": (lower_bin, upper_bin, pred_test, "#A5D6A7"),
}, os.path.join(RESULTS_DIR, "method_comparison_stacked.png"), ylabel=ylabel)

bin_labels = sorted(residuals_by_bin.keys())
plot_residuals_by_bin(bin_labels, residuals_by_bin,
                       os.path.join(RESULTS_DIR, "residuals_by_bin.png"), ylabel=f"Residual ({unit})")

# ── Multiple intervals (using the binned method) ────────────────────────────
print("\nMultiple interval levels (binned method):")
multi_rows = []
for cov_pct in NOMINAL_LEVELS:
    alpha = (100 - cov_pct) / 100
    lo_q, hi_q = alpha / 2, 1 - alpha / 2

    lower_m = np.empty_like(pred_test)
    upper_m = np.empty_like(pred_test)
    for b in np.unique(test_bin_idx):
        mask = test_bin_idx == b
        offsets_b = bootstrap_offsets(residuals_by_bin[b], [lo_q, hi_q], N_BOOTSTRAP, rng)
        lower_m[mask] = pred_test[mask] + offsets_b[lo_q]
        upper_m[mask] = pred_test[mask] + offsets_b[hi_q]

    emp_cov = empirical_coverage(y_test, lower_m, upper_m)
    multi_rows.append({"NominalCoverage": cov_pct / 100, "EmpiricalCoverage": emp_cov,
                        "IntervalArea": interval_area(lower_m, upper_m)})
    print(f"  Nominal {cov_pct:>2}%  ->  empirical {emp_cov:.1%}")

multi_df = pd.DataFrame(multi_rows)
multi_path = os.path.join(RESULTS_DIR, "multiple_intervals_coverage.csv")
multi_df.to_csv(multi_path, index=False)
print(f"Saved multiple-intervals coverage to: {multi_path}")

plot_multiple_intervals_coverage(multi_df["NominalCoverage"], multi_df["EmpiricalCoverage"],
                                  os.path.join(RESULTS_DIR, "multiple_intervals_coverage.png"))

print("\nBootstrap residuals deep dive complete!")
