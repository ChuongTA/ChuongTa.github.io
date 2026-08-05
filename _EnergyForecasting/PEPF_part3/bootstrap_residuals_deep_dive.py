"""
Bootstrapped-residual prediction intervals for DK1 day-ahead electricity
prices, 1h ahead, on the most recent walk-forward fold.

Mirrors the structure of the skforecast tutorial "Probabilistic Forecasting:
Bootstrapped Residuals" (https://skforecast.org/0.15.0/user_guides/
probabilistic-forecasting-bootstrapped-residuals), adapted to this
project's own XGBoost point model and DK1 data instead of skforecast's
ForecasterRecursive and the bike-sharing dataset. Three residual
strategies are compared on the same train/validation/test split:

  1. In-sample residuals   : residuals computed on the TRAINING data itself.
                              skforecast's docs warn this is usually
                              overoptimistic (intervals too narrow), since
                              the model already fit those points.
  2. Out-sample residuals  : residuals computed on the VALIDATION data
                              (out-of-fit), non-conditioned, i.e. the same
                              residual pool is used for every test row
                              regardless of the predicted value.
  3. Binned residuals      : out-of-sample residuals, binned by the point
                              model's predicted value (skforecast's
                              QuantileBinner idea). A test row's interval
                              is built from the residuals of validation
                              rows whose predictions fell in the same bin,
                              so the interval narrows or widens depending
                              on how volatile the predicted price level is.

Only one lead time and fold are used here (1h ahead, the last walk-forward
fold), matching this post's original single-fold demonstration, since the
point of this script is to compare *residual strategies* on one clear
example, not to repeat the full walk-forward grid Part 2 already covers.
"""
import os
import numpy as np
import pandas as pd
import xgboost as xgb
import warnings
warnings.filterwarnings("ignore")

from bootstrap_deepdive_plots import (
    plot_prediction_interval, plot_residuals_by_bin,
    plot_method_comparison, plot_multiple_intervals_coverage,
)

# Reuse data loading, fold boundaries, and feature building from the shared
# Part 2 module (importing this only loads data and defines functions, it
# does not run the QR/QRF grid, that's guarded by __main__ in that file).
import qr_qrf_walkforward_pipeline as base

script_dir = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(script_dir, "Results", "DeepDive")
os.makedirs(RESULTS_DIR, exist_ok=True)

LEAD_H = 1
N_BINS = 5
N_BOOTSTRAP = 1000
NOMINAL_LEVELS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95]  # coverage %, central intervals
XGB_PARAMS = dict(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)


def empirical_coverage(y_true, lower, upper):
    return float(np.mean((y_true >= lower) & (y_true <= upper)))


def interval_area(lower, upper):
    return float(np.sum(upper - lower))


def bootstrap_offsets(residual_pool, quantiles, n_bootstrap, rng):
    boot = rng.choice(residual_pool, size=n_bootstrap, replace=True)
    return {q: float(np.quantile(boot, q)) for q in quantiles}


# ── Build the single demo split (most recent walk-forward fold) ────────────
valid_dates = base.df_raw[base.DATE_COL]
fold_boundaries = base.generate_walk_forward_folds(
    valid_dates.min(), valid_dates.max(), base.N_FOLDS, base.TEST_LEN_H, base.VAL_LEN_H, base.MIN_TRAIN_FRAC
)
fold = fold_boundaries[-1]
print(f"Demo case: {base.TARGET}, lead={LEAD_H}h, fold {fold['fold']} "
      f"(test {fold['test_start'].date()} -> {fold['test_end'].date()})")

df, all_features = base.build_feature_frame(LEAD_H)
dates = df[base.DATE_COL]

train_mask = (dates >= fold["train_start"]) & (dates < fold["val_start"])
val_mask = (dates >= fold["val_start"]) & (dates < fold["test_start"])
test_mask = (dates >= fold["test_start"]) & (dates < fold["test_end"])

X_train, y_train = df.loc[train_mask, all_features].values, df.loc[train_mask, base.TARGET].values
X_val, y_val = df.loc[val_mask, all_features].values, df.loc[val_mask, base.TARGET].values
X_test, y_test = df.loc[test_mask, all_features].values, df.loc[test_mask, base.TARGET].values
test_dates = dates.loc[test_mask].values

print(f"train={len(y_train)}  valid={len(y_val)}  test={len(y_test)}")

# ── Fit ONE point model ──────────────────────────────────────────────────────
model = xgb.XGBRegressor(**XGB_PARAMS)
model.fit(X_train, y_train)

pred_train = model.predict(X_train)
pred_val = model.predict(X_val)
pred_test = model.predict(X_test)

resid_train = y_train - pred_train
resid_val = y_val - pred_val

rng = np.random.default_rng(42)
LO, HI = 0.10, 0.90  # 80% central interval, matching the skforecast example

# ── 1. In-sample residuals ───────────────────────────────────────────────────
offsets_in_sample = bootstrap_offsets(resid_train, [LO, HI], N_BOOTSTRAP, rng)
lower_in = pred_test + offsets_in_sample[LO]
upper_in = pred_test + offsets_in_sample[HI]
cov_in = empirical_coverage(y_test, lower_in, upper_in)
area_in = interval_area(lower_in, upper_in)
print(f"\n[1] In-sample residuals    | coverage={cov_in:.2%}  area={area_in:.2f}  "
      f"resid_std_train={resid_train.std():.2f}")

# ── 2. Out-sample residuals (non-conditioned) ───────────────────────────────
offsets_out_sample = bootstrap_offsets(resid_val, [LO, HI], N_BOOTSTRAP, rng)
lower_out = pred_test + offsets_out_sample[LO]
upper_out = pred_test + offsets_out_sample[HI]
cov_out = empirical_coverage(y_test, lower_out, upper_out)
area_out = interval_area(lower_out, upper_out)
print(f"[2] Out-sample residuals   | coverage={cov_out:.2%}  area={area_out:.2f}  "
      f"resid_std_val={resid_val.std():.2f}")

# ── 3. Binned / conditional residuals (binned by predicted value) ──────────
bin_edges = np.unique(np.percentile(pred_val, np.linspace(0, 100, N_BINS + 1)))
bin_edges[0], bin_edges[-1] = -np.inf, np.inf
val_bin_idx = np.digitize(pred_val, bin_edges[1:-1], right=False)
test_bin_idx = np.digitize(pred_test, bin_edges[1:-1], right=False)

residuals_by_bin = {b: resid_val[val_bin_idx == b] for b in range(len(bin_edges) - 1)}
for b, res in residuals_by_bin.items():
    if len(res) < 15:
        residuals_by_bin[b] = resid_val  # fall back to the global pool if a bin is too small

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
ylabel = "DK1 price (EUR/MWh)"

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
                       os.path.join(RESULTS_DIR, "residuals_by_bin.png"), ylabel="Residual (EUR/MWh)")

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
