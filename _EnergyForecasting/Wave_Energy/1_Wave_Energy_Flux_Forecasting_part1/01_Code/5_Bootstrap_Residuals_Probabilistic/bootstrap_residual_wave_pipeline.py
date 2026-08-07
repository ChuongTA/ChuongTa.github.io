"""
Bootstrapped-residual probabilistic forecasting of significant wave height
(swh / Hs) and mean wave period (mwp / Te), with walk-forward
(expanding-window) cross-validation.

Same evaluation as the QR/QRF pipeline in ../4_QR_QRF_Probabilistic (pinball
loss, CRPS approximation, empirical coverage, mean interval width), but a
much cheaper way to get there: fit ONE point-forecast model (LightGBM) per
fold instead of 13 separate quantile regressions (QR) or a leaf-size grid
search over a full random forest (QRF), then turn that single model into a
full predictive distribution by bootstrapping its validation residuals.

Method (the "vanilla" / unconditional residual bootstrap):
  1. Fit a point model f on the training window.
  2. Compute residuals r = y_valid - f(X_valid) on the *validation* window
     (out-of-sample, so the residual spread isn't optimistic from fitting noise).
  3. Draw B bootstrap resamples of r (with replacement) and take the
     empirical quantile of that resampled pool at each tau in QUANTILES.
     Because the same residual pool is reused for every test row, this
     gives every test point the *same* interval width, it does not adapt
     width to the local prediction (e.g. wider intervals for stormier
     conditions). That's the trade-off for speed: no per-quantile model,
     no forest to keep in memory, just one point model plus array
     arithmetic. See README in this folder for when that matters.
  4. Quantile forecast = point forecast + that residual quantile offset.

This is what makes it fast: bootstrapping the *residuals* of one fitted
model, not refitting the model itself B times.
"""
import os
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

from bootstrap_plots import plot_split_diagram, plot_forecast_fan, plot_reliability_diagram

# ── Paths ────────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(script_dir, "Results")
os.makedirs(RESULTS_DIR, exist_ok=True)

DATA_PATH = os.path.join(script_dir, "..", "0_Data_Acquisition", "0_ERA5_Data",
                          "ERA5_Ocean_2024_01_to_2026_07.csv")
BEST_LAGS_PATH = os.path.join(script_dir, "..", "3_Light_GBM_with_ERA5_Data",
                               "Results_3", "2.2_best_lags_full.csv")

# ── Load data ────────────────────────────────────────────────────────────────
print(f"Loading data from: {DATA_PATH}")
raw = pd.read_csv(DATA_PATH, parse_dates=["valid_time"])
raw = raw.sort_values("valid_time").reset_index(drop=True)
raw = raw.ffill()
print("Loaded dataset shape:", raw.shape)

DATE_COL = "valid_time"
TARGETS = ["swh", "mwp"]
LEAD_STEPS = [1, 3, 6, 12, 24, 48]
QUANTILES = [0.025, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.975]
INTERVALS = [(80, 0.10, 0.90), (90, 0.05, 0.95), (95, 0.025, 0.975)]
N_BOOTSTRAP = 5000

N_FOLDS = 6
VALID_WINDOW = pd.DateOffset(months=1)
TEST_WINDOW = pd.DateOffset(months=1)

print("Loading precomputed best lags (from 3_Light_GBM_with_ERA5_Data)...")
best_lags_df = pd.read_csv(BEST_LAGS_PATH)
best_lags = {}
for target in TARGETS:
    best_lags[target] = {}
    for lead in LEAD_STEPS:
        subset = best_lags_df[(best_lags_df["target"] == target) & (best_lags_df["lead_h"] == lead)]
        best_lags[target][lead] = {row["variable"]: int(row["lag"]) for _, row in subset.iterrows()}


# ── Evaluation helpers (identical to the QR/QRF pipeline) ───────────────────
def pinball_loss(y_true, q_hat, alpha):
    err = y_true - q_hat
    return float(np.mean(np.where(err >= 0, alpha * err, (alpha - 1) * err)))


def empirical_coverage(y_true, lower, upper):
    return float(np.mean((y_true >= lower) & (y_true <= upper)))


def mean_interval_width(lower, upper):
    return float(np.mean(upper - lower))


def crps_from_pinball(y_true, quantile_preds, quantiles):
    losses = [pinball_loss(y_true, quantile_preds[a], a) for a in quantiles]
    return 2.0 * float(np.mean(losses)), float(np.mean(losses))


def score_quantile_preds(y_true, preds):
    crps, mean_pinball = crps_from_pinball(y_true, preds, QUANTILES)
    row = {"MAE_median": mean_absolute_error(y_true, preds[0.50]),
           "RMSE_median": np.sqrt(mean_squared_error(y_true, preds[0.50])),
           "MeanPinball": mean_pinball, "CRPS_approx": crps}
    for cov, lo_a, hi_a in INTERVALS:
        row[f"Cov_{cov}"] = empirical_coverage(y_true, preds[lo_a], preds[hi_a])
        row[f"Width_{cov}"] = mean_interval_width(preds[lo_a], preds[hi_a])
    return row


# ── Walk-forward fold boundaries (same convention as the rest of this project) ──
def build_walk_forward_folds(t_idx, data_start, data_end, n_folds, valid_window, test_window):
    fold_test_ends = sorted(data_end - i * test_window for i in range(n_folds))
    folds = []
    for k, test_end in enumerate(fold_test_ends):
        test_start = test_end - test_window + pd.Timedelta(hours=1)
        valid_end = test_start - pd.Timedelta(hours=1)
        valid_start = valid_end - valid_window + pd.Timedelta(hours=1)
        train_end = valid_start - pd.Timedelta(hours=1)
        folds.append(dict(
            fold=k + 1,
            train_start=data_start, train_end=train_end,
            valid_start=valid_start, valid_end=valid_end,
            test_start=test_start, test_end=test_end,
        ))
    return folds


t_idx = raw[DATE_COL]
fold_boundaries = build_walk_forward_folds(t_idx, t_idx.min(), t_idx.max(), N_FOLDS, VALID_WINDOW, TEST_WINDOW)


# ── Feature engineering: cyclical time features + this target/lead's best lags ──
def build_lead_features(target, lead):
    lag_info = best_lags[target][lead]
    feat_dict = {
        "hour_sin": np.sin(2 * np.pi * raw[DATE_COL].dt.hour / 24),
        "hour_cos": np.cos(2 * np.pi * raw[DATE_COL].dt.hour / 24),
        "doy_sin": np.sin(2 * np.pi * raw[DATE_COL].dt.dayofyear / 365.25),
        "doy_cos": np.cos(2 * np.pi * raw[DATE_COL].dt.dayofyear / 365.25),
    }
    for col, lag in lag_info.items():
        feat_dict[f"{col}_lag{lag}"] = raw[col].shift(lag)
    X = pd.DataFrame(feat_dict, index=raw.index)
    y = raw[target].shift(-lead)
    return X, y


# ── Point model + residual bootstrap ─────────────────────────────────────────
def fit_point_model(X_train, y_train, X_valid, y_valid):
    model = lgb.LGBMRegressor(random_state=42, verbose=-1)
    model.fit(
        X_train, y_train,
        eval_set=[(X_valid, y_valid)],
        callbacks=[lgb.early_stopping(stopping_rounds=15, verbose=False)],
    )
    return model


def bootstrap_quantiles(point_pred_test, residuals_valid, quantiles, n_bootstrap, rng):
    """Every test row gets the same residual-quantile offsets (unconditional
    bootstrap): point_pred_test + quantile(bootstrap-resampled residuals, tau)."""
    boot_resid = rng.choice(residuals_valid, size=n_bootstrap, replace=True)
    offsets = {a: float(np.quantile(boot_resid, a)) for a in quantiles}
    return {a: point_pred_test + offsets[a] for a in quantiles}


# ── Main walk-forward pipeline for one target/lead time ─────────────────────
def run_target_lead(target, lead_h, dates, rng):
    X, y = build_lead_features(target, lead_h)
    valid_rows = X.notna().all(axis=1) & y.notna()

    fold_rows = []
    reliability_rows = []
    last_fold_fan_data = None

    for fold in fold_boundaries:
        train_mask = (dates >= fold["train_start"]) & (dates <= fold["train_end"]) & valid_rows
        valid_mask = (dates >= fold["valid_start"]) & (dates <= fold["valid_end"]) & valid_rows
        test_mask = (dates >= fold["test_start"]) & (dates <= fold["test_end"]) & valid_rows

        if train_mask.sum() < 500 or valid_mask.sum() < 20 or test_mask.sum() < 20:
            print(f"  Fold {fold['fold']}: skipped (not enough rows)")
            continue

        X_train, y_train = X.loc[train_mask].values, y.loc[train_mask].values
        X_val, y_val = X.loc[valid_mask].values, y.loc[valid_mask].values
        X_test, y_test = X.loc[test_mask].values, y.loc[test_mask].values
        test_dates = dates.loc[test_mask].values

        model = fit_point_model(X_train, y_train, X_val, y_val)
        pred_val = model.predict(X_val)
        pred_test = model.predict(X_test)
        residuals_val = y_val - pred_val

        preds_test = bootstrap_quantiles(pred_test, residuals_val, QUANTILES, N_BOOTSTRAP, rng)

        print(f"  Fold {fold['fold']}: train={len(y_train)} val={len(y_val)} test={len(y_test)} "
              f"| val RMSE={np.sqrt(np.mean((y_val - pred_val) ** 2)):.4f}")

        row = score_quantile_preds(y_test, preds_test)
        row.update({"Model": "Bootstrap", "Target": target, "LeadTime": f"{lead_h}h", "Fold": fold["fold"]})
        fold_rows.append(row)

        for cov, lo_a, hi_a in INTERVALS:
            reliability_rows.append({
                "target": target, "lead_time": lead_h, "model": "Bootstrap", "fold": fold["fold"],
                "nominal_coverage": cov / 100.0,
                "empirical_coverage": empirical_coverage(y_test, preds_test[lo_a], preds_test[hi_a]),
            })

        last_fold_fan_data = (test_dates, y_test, {"Bootstrap": preds_test}, fold["fold"])

    if last_fold_fan_data is not None:
        test_dates, y_test, preds_by_model, fold_num = last_fold_fan_data
        unit = "m" if target == "swh" else "s"
        label = "Hs (swh)" if target == "swh" else "Te (mwp)"
        plot_forecast_fan(
            test_dates, y_test, preds_by_model, lead_h, f"fold {fold_num}",
            os.path.join(RESULTS_DIR, f"bootstrap_forecast_{target}_{lead_h}h.png"),
            ylabel=f"{label} ({unit})",
        )

    return fold_rows, reliability_rows


# ── Run everything ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generated {len(fold_boundaries)} walk-forward folds:")
    for f in fold_boundaries:
        print(f"  Fold {f['fold']}: train [{f['train_start'].date()} -> {f['train_end'].date()}], "
              f"valid [{f['valid_start'].date()} -> {f['valid_end'].date()}], "
              f"test [{f['test_start'].date()} -> {f['test_end'].date()}]")
    plot_split_diagram(fold_boundaries, os.path.join(RESULTS_DIR, "wave_train_val_test_split.png"))

    rng = np.random.default_rng(42)
    all_fold_rows = []
    all_reliability_rows = []

    for target in TARGETS:
        for lead in LEAD_STEPS:
            print(f"\n{'=' * 70}")
            print(f"  BOOTSTRAP RESIDUAL WALK-FORWARD — target={target}, lead={lead}h ahead")
            print(f"{'=' * 70}")
            fold_rows, reliability_rows = run_target_lead(target, lead, t_idx, rng)
            all_fold_rows.extend(fold_rows)
            all_reliability_rows.extend(reliability_rows)

    per_fold_df = pd.DataFrame(all_fold_rows)
    per_fold_path = os.path.join(RESULTS_DIR, "bootstrap_wave_per_fold_metrics.csv")
    per_fold_df.to_csv(per_fold_path, index=False)
    print(f"\nSaved per-fold metrics to: {per_fold_path}")

    metric_cols = ["MAE_median", "RMSE_median", "MeanPinball", "CRPS_approx",
                   "Cov_80", "Width_80", "Cov_90", "Width_90", "Cov_95", "Width_95"]
    summary_df = per_fold_df.groupby(["Target", "LeadTime", "Model"])[metric_cols].agg(["mean", "std"])
    summary_path = os.path.join(RESULTS_DIR, "bootstrap_wave_cv_summary.csv")
    summary_df.to_csv(summary_path)
    print(f"Saved cross-fold summary to: {summary_path}")

    for target in TARGETS:
        rel_df = pd.DataFrame([r for r in all_reliability_rows if r["target"] == target])
        rel_avg = (
            rel_df.groupby(["lead_time", "model", "nominal_coverage"])["empirical_coverage"]
            .mean().reset_index().to_dict("records")
        )
        plot_reliability_diagram(rel_avg, os.path.join(RESULTS_DIR, f"wave_reliability_diagram_{target}.png"),
                                  title_suffix=f"({'Hs' if target == 'swh' else 'Te'})")

    print("\nBootstrap residual wave forecasting complete!")
