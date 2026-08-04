"""
Bootstrapped Residuals and Conformal Prediction for probabilistic
day-ahead forecasting of DK1 electricity prices, evaluated on the
same walk-forward folds as main_pipeline.py's QR/QRF comparison.

Both methods here wrap a single XGBoost point-forecast model (same
family as forecast.py's) with two different ways of turning its
residuals into prediction intervals:

  - BootstrappedPI: resamples calibration-set residuals with
    replacement and adds them back to the point forecast. Fixed here
    to calibrate on a held-out validation split (out-of-sample
    residuals), unlike forecast.py's BootstrappedPI, which fits on
    training-set residuals and was found to understate the true error
    spread by about 5x on this data (see the write-up referenced
    below).
  - ConformalPI: reads calibration-set residual quantiles directly,
    no resampling. Both classes support optional binning by predicted
    value, which the write-up found calibrates at least as well as no
    binning and better than hour-of-day binning on this data.

See "../01_Boostrapped Residual and Conformal/03_Final_Bootstrap_and_Conformal.md"
for the full write-up, skforecast references, and the reasoning
behind these design choices.
"""
import os
import time
import numpy as np
import xgboost as xgb
import warnings
warnings.filterwarnings("ignore")

from qr_qrf_walkforward_pipeline import (
    TARGET, DATE_COL, QUANTILES, INTERVALS,
    N_FOLDS, TEST_LEN_H, VAL_LEN_H, MIN_TRAIN_FRAC,
    df_raw, build_feature_frame, generate_walk_forward_folds,
    pinball_loss, empirical_coverage, mean_interval_width, crps_from_pinball,
)
from forecasting_plots import plot_forecast_fan, plot_reliability_diagram, plot_timing_comparison

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                           "Results", "Bootstrap_Conformal_CV")
os.makedirs(RESULTS_DIR, exist_ok=True)

XGB_PARAMS = dict(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
N_BOOT = 1000


# ── Bootstrapped residual prediction intervals (corrected: out-of-sample) ───
class BootstrappedPI:
    """
    Bootstraps from a held-out calibration set's residuals (out-of-
    sample), optionally binned by predicted-value quantile or hour.
    This is the fix for forecast.py's BootstrappedPI, which calibrates
    on training-set (in-sample) residuals instead.
    """

    def __init__(self, quantiles, n_boot=1000, bin_by=None, n_bins=5, min_bin_size=15, random_state=42):
        self.quantiles = quantiles
        self.n_boot = n_boot
        self.bin_by = bin_by
        self.n_bins = n_bins
        self.min_bin_size = min_bin_size
        self.rng = np.random.default_rng(random_state)

    def fit(self, cal_residuals, cal_point_preds=None, cal_hours=None):
        self._residuals = np.asarray(cal_residuals)
        self._bin_edges = None
        if self.bin_by == "value":
            self._bin_edges = np.quantile(cal_point_preds, np.linspace(0, 1, self.n_bins + 1))
            bins = np.clip(np.digitize(cal_point_preds, self._bin_edges[1:-1]), 0, self.n_bins - 1)
        elif self.bin_by == "hour":
            bins = np.asarray(cal_hours, dtype=int)
        else:
            bins = np.zeros(len(self._residuals), dtype=int)

        self._pools = {}
        for b in np.unique(bins):
            pool = self._residuals[bins == b]
            self._pools[b] = pool if len(pool) >= self.min_bin_size else self._residuals
        self._bins_seen = set(self._pools)
        return self

    def predict_quantiles(self, point_preds, point_or_hour=None):
        point_preds = np.asarray(point_preds)
        n = len(point_preds)
        if self.bin_by == "value":
            bins = np.clip(np.digitize(point_or_hour, self._bin_edges[1:-1]), 0, self.n_bins - 1)
        elif self.bin_by == "hour":
            bins = np.asarray(point_or_hour, dtype=int)
        else:
            bins = np.zeros(n, dtype=int)

        out = {a: np.empty(n) for a in self.quantiles}
        for i in range(n):
            b = bins[i]
            b_use = b if b in self._bins_seen else min(self._bins_seen, key=lambda x: abs(x - b))
            draws = point_preds[i] + self.rng.choice(self._pools[b_use], size=self.n_boot, replace=True)
            q_vals = np.quantile(draws, self.quantiles)
            for a, v in zip(self.quantiles, q_vals):
                out[a][i] = v
        return out


# ── Split conformal prediction intervals ─────────────────────────────────────
class ConformalPI:
    """
    Split Conformal Prediction (SCP), adapted from skforecast's approach
    (https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-conformal-prediction).

    Fits once on a held-out calibration set's residuals, no resampling:
    reads the residual quantile directly and adds it to the point
    forecast. Optionally binned by predicted-value quantile or hour.
    """

    def __init__(self, quantiles, bin_by=None, n_bins=5, min_bin_size=15):
        self.quantiles = quantiles
        self.bin_by = bin_by
        self.n_bins = n_bins
        self.min_bin_size = min_bin_size

    def fit(self, cal_residuals, cal_point_preds=None, cal_hours=None):
        self._residuals = np.asarray(cal_residuals)
        self._bin_edges = None
        if self.bin_by == "value":
            self._bin_edges = np.quantile(cal_point_preds, np.linspace(0, 1, self.n_bins + 1))
            bins = np.clip(np.digitize(cal_point_preds, self._bin_edges[1:-1]), 0, self.n_bins - 1)
        elif self.bin_by == "hour":
            bins = np.asarray(cal_hours, dtype=int)
        else:
            bins = np.zeros(len(self._residuals), dtype=int)

        self._offsets = {}
        for b in np.unique(bins):
            pool = self._residuals[bins == b]
            pool = pool if len(pool) >= self.min_bin_size else self._residuals
            for a in self.quantiles:
                self._offsets[(b, a)] = np.quantile(pool, a)
        self._bins_seen = set(np.unique(bins))
        return self

    def predict_quantiles(self, point_preds, point_or_hour=None):
        point_preds = np.asarray(point_preds)
        n = len(point_preds)
        if self.bin_by == "value":
            bins = np.clip(np.digitize(point_or_hour, self._bin_edges[1:-1]), 0, self.n_bins - 1)
        elif self.bin_by == "hour":
            bins = np.asarray(point_or_hour, dtype=int)
        else:
            bins = np.zeros(n, dtype=int)

        out = {}
        for a in self.quantiles:
            vals = np.empty(n)
            for i in range(n):
                b = bins[i]
                b_use = b if b in self._bins_seen else min(self._bins_seen, key=lambda x: abs(x - b))
                vals[i] = point_preds[i] + self._offsets[(b_use, a)]
            out[a] = vals
        return out


def score_quantile_preds(y_true, preds):
    crps, mean_pinball = crps_from_pinball(y_true, preds, QUANTILES)
    row = {"MAE_median": mean_absolute_error(y_true, preds[0.50]),
           "RMSE_median": np.sqrt(mean_squared_error(y_true, preds[0.50])),
           "MeanPinball": mean_pinball, "CRPS_approx": crps}
    for cov, lo_a, hi_a in INTERVALS:
        row[f"Cov_{cov}"] = empirical_coverage(y_true, preds[lo_a], preds[hi_a])
        row[f"Width_{cov}"] = mean_interval_width(preds[lo_a], preds[hi_a])
    return row


def run_lead_time(lead_time_hours, fold_boundaries):
    print(f"\n{'=' * 70}")
    print(f"  Bootstrap / Conformal WALK-FORWARD PIPELINE, LEAD TIME {lead_time_hours}h AHEAD")
    print(f"{'=' * 70}")

    df, all_features = build_feature_frame(lead_time_hours)
    dates = df[DATE_COL]

    fold_rows = []
    reliability_rows = []
    timing_rows = []
    last_fold_fan_data = None

    for fold in fold_boundaries:
        train_mask = (dates >= fold["train_start"]) & (dates < fold["train_end"])
        val_mask = (dates >= fold["val_start"]) & (dates < fold["val_end"])
        test_mask = (dates >= fold["test_start"]) & (dates < fold["test_end"])

        if train_mask.sum() < 500 or val_mask.sum() < 20 or test_mask.sum() < 20:
            print(f"  Fold {fold['fold']}: skipped (not enough rows in one of the splits)")
            continue

        X_train, y_train = df.loc[train_mask, all_features].values, df.loc[train_mask, TARGET].values
        X_val, y_val = df.loc[val_mask, all_features].values, df.loc[val_mask, TARGET].values
        X_test, y_test = df.loc[test_mask, all_features].values, df.loc[test_mask, TARGET].values
        test_dates = dates.loc[test_mask].values

        print(f"  Fold {fold['fold']}: train={len(y_train)}  val={len(y_val)}  test={len(y_test)}")

        # ---- Point-forecast model, same family as forecast.py ----
        model = xgb.XGBRegressor(**XGB_PARAMS)
        model.fit(X_train, y_train)

        point_val = model.predict(X_val)
        point_test = model.predict(X_test)
        cal_residuals = y_val - point_val  # out-of-sample: fixes forecast.py's in-sample bug

        # ---- Bootstrapped residuals (value-binned, out-of-sample) ----
        t0 = time.time()
        bootstrap = BootstrappedPI(QUANTILES, n_boot=N_BOOT, bin_by="value", n_bins=5, random_state=42)
        bootstrap.fit(cal_residuals, cal_point_preds=point_val)
        boot_preds = bootstrap.predict_quantiles(point_test, point_or_hour=point_test)
        t_boot = (time.time() - t0) * 1000

        # ---- Conformal prediction (value-binned, out-of-sample) ----
        t0 = time.time()
        conformal = ConformalPI(QUANTILES, bin_by="value", n_bins=5)
        conformal.fit(cal_residuals, cal_point_preds=point_val)
        conf_preds = conformal.predict_quantiles(point_test, point_or_hour=point_test)
        t_conf = (time.time() - t0) * 1000

        timing_rows.append({"method": "Bootstrap", "time_ms": t_boot})
        timing_rows.append({"method": "Conformal", "time_ms": t_conf})

        for name, preds in [("Bootstrap", boot_preds), ("Conformal", conf_preds)]:
            row = score_quantile_preds(y_test, preds)
            row.update({"Model": name, "LeadTime": f"{lead_time_hours}h", "Fold": fold["fold"]})
            fold_rows.append(row)

            for cov, lo_a, hi_a in INTERVALS:
                reliability_rows.append({
                    "lead_time": lead_time_hours, "model": name, "fold": fold["fold"],
                    "nominal_coverage": cov / 100.0,
                    "empirical_coverage": empirical_coverage(y_test, preds[lo_a], preds[hi_a]),
                })

        last_fold_fan_data = (test_dates, y_test, {"Bootstrap": boot_preds, "Conformal": conf_preds}, fold["fold"])

    if last_fold_fan_data is not None:
        test_dates, y_test, preds_by_model, fold_num = last_fold_fan_data
        plot_forecast_fan(
            test_dates, y_test, preds_by_model, lead_time_hours, f"fold {fold_num}",
            os.path.join(RESULTS_DIR, f"bootstrap_conformal_forecast_{lead_time_hours}h.png"),
        )

    return fold_rows, reliability_rows, timing_rows


if __name__ == "__main__":
    valid_dates = df_raw[DATE_COL]
    fold_boundaries = generate_walk_forward_folds(
        valid_dates.min(), valid_dates.max(), N_FOLDS, TEST_LEN_H, VAL_LEN_H, MIN_TRAIN_FRAC
    )
    print(f"Using the same {len(fold_boundaries)} walk-forward folds as main_pipeline.py")

    lead_times = [1, 6, 12, 24]
    all_fold_rows, all_reliability_rows, all_timing_rows = [], [], []

    for lt in lead_times:
        fold_rows, reliability_rows, timing_rows = run_lead_time(lt, fold_boundaries)
        all_fold_rows.extend(fold_rows)
        all_reliability_rows.extend(reliability_rows)
        all_timing_rows.extend(timing_rows)

    per_fold_df = pd.DataFrame(all_fold_rows)
    per_fold_path = os.path.join(RESULTS_DIR, "bootstrap_conformal_per_fold_metrics.csv")
    per_fold_df.to_csv(per_fold_path, index=False)
    print(f"\nSaved per-fold metrics to: {per_fold_path}")

    metric_cols = ["MAE_median", "RMSE_median", "MeanPinball", "CRPS_approx",
                   "Cov_80", "Width_80", "Cov_90", "Width_90", "Cov_95", "Width_95"]
    summary_df = per_fold_df.groupby(["LeadTime", "Model"])[metric_cols].agg(["mean", "std"])
    summary_path = os.path.join(RESULTS_DIR, "bootstrap_conformal_cv_summary.csv")
    summary_df.to_csv(summary_path)
    print(f"Saved cross-fold summary (mean/std) to: {summary_path}")

    print("\n" + "=" * 100)
    print(f"{'LeadTime':<9}|{'Model':<10}|{'MAE':<8}|{'RMSE':<8}|{'Pinball':<9}|{'CRPS':<8}|{'Cov_80':<8}|{'Cov_95':<8}")
    print("-" * 100)
    for (lt, model), row in summary_df.iterrows():
        print(f"{lt:<9}|{model:<10}|{row[('MAE_median', 'mean')]:<8.2f}|{row[('RMSE_median', 'mean')]:<8.2f}|"
              f"{row[('MeanPinball', 'mean')]:<9.3f}|{row[('CRPS_approx', 'mean')]:<8.3f}|"
              f"{row[('Cov_80', 'mean')]:<8.3f}|{row[('Cov_95', 'mean')]:<8.3f}")
    print("=" * 100)

    rel_df = pd.DataFrame(all_reliability_rows)
    rel_avg = (
        rel_df.groupby(["lead_time", "model", "nominal_coverage"])["empirical_coverage"]
        .mean().reset_index().to_dict("records")
    )
    plot_reliability_diagram(rel_avg, os.path.join(RESULTS_DIR, "bootstrap_conformal_reliability_diagram.png"))

    timing_df = pd.DataFrame(all_timing_rows)
    timing_summary = timing_df.groupby("method")["time_ms"].agg(["mean", "std"]).reset_index()
    timing_rows_for_plot = [
        {"method": r["method"], "mean_ms": r["mean"], "std_ms": r["std"]}
        for _, r in timing_summary.iterrows()
    ]
    plot_timing_comparison(timing_rows_for_plot, os.path.join(RESULTS_DIR, "bootstrap_conformal_timing.png"))
    timing_summary.to_csv(os.path.join(RESULTS_DIR, "bootstrap_conformal_timing_summary.csv"), index=False)
    print("\nTiming summary (ms per fold, averaged across all folds and lead times):")
    print(timing_summary)

    print("\nBootstrap/Conformal walk-forward comparison complete!")
