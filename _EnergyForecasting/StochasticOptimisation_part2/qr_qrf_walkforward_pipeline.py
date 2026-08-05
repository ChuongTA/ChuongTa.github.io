"""
Quantile Regression (QR) and Quantile Regression Forest (QRF) for
probabilistic day-ahead forecasting of DK1 electricity prices, with
walk-forward (expanding-window) cross-validation instead of a single
train/test split.

All plotting lives in plot.py; this file only loads data, engineers
features, fits models, and computes metrics.

Speed notes vs. the earlier single-split version:
  - QRF prediction is vectorized with sparse-matrix leaf weights
    instead of a per-test-row Python loop (the previous bottleneck).
  - Feature engineering runs once per lead time, then folds are just
    index slices into that frame (no recomputation per fold).
  - QRF's min_samples_leaf is chosen from a small 2-candidate grid on
    the validation split; QR's regularization is fixed (already cheap
    to fit), so the validation set is used for honest reporting there
    rather than a search.
"""
import os
import numpy as np
import pandas as pd
from scipy import sparse
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

from forecasting_plots import plot_split_diagram, plot_forecast_fan, plot_reliability_diagram

# ── Paths ────────────────────────────────────────────────────────────────────
# Data.csv lives alongside this script, so results are resolved relative to
# this file's own directory rather than the caller's current working directory.
script_dir = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(script_dir, "Results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── Load data ────────────────────────────────────────────────────────────────
csv_path = os.path.join(script_dir, "Data.csv")

print(f"Loading data from: {csv_path}")
df_raw = pd.read_csv(csv_path, sep=";", decimal=",", parse_dates=["HourUTC"])
df_raw = df_raw.sort_values("HourUTC").reset_index(drop=True)

TARGET = "DK1_EUR/MWh"
DATE_COL = "HourUTC"

FEATURE_COLS = [
    "LocalPowerMWhDK1",
    "LocalPowerSelfConMWhDK1",
    "CentralPowerMWhDK1",
    "CommercialPowerMWhDK1",
    "HydroPowerMWhDK1",
    "OffshoreWindGe100MW_MWhDK1",
    "OffshoreWindLt100MW_MWhDK1",
    "OnshoreWindGe50kW_MWhDK1",
    "OnshoreWindLt50kW_MWhDK1",
    "SolarPowerGe10Lt40kW_MWhDK1",
    "SolarPowerGe40kW_MWhDK1",
    "SolarPowerLt10kW_MWhDK1",
    "SolarPowerSelfConMWhDK1",
    "PowerToHeatMWhDK1",
    "GrossConsumptionMWhDK1",
]

df_raw = df_raw.dropna(subset=[TARGET]).reset_index(drop=True)
for col in FEATURE_COLS:
    df_raw[col] = df_raw[col].interpolate(method="linear").ffill().bfill()

QUANTILES = [0.025, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.975]
INTERVALS = [(80, 0.10, 0.90), (90, 0.05, 0.95), (95, 0.025, 0.975)]

N_FOLDS = 4
TEST_LEN_H = 24 * 14   # 2 weeks per test window
VAL_LEN_H = 24 * 7     # 1 week validation buffer before each test window
MIN_TRAIN_FRAC = 0.4   # first fold's training window covers this fraction of the timeline


# ── Evaluation helpers ───────────────────────────────────────────────────────
def pinball_loss(y_true, q_hat, alpha):
    err = y_true - q_hat
    return float(np.mean(np.where(err >= 0, alpha * err, (alpha - 1) * err)))


def empirical_coverage(y_true, lower, upper):
    return float(np.mean((y_true >= lower) & (y_true <= upper)))


def mean_interval_width(lower, upper):
    return float(np.mean(upper - lower))


def crps_from_pinball(y_true, quantile_preds, quantiles):
    losses = [pinball_loss(y_true, quantile_preds[a], a) for a in quantiles]
    mean_pinball = float(np.mean(losses))
    return 2.0 * mean_pinball, mean_pinball


# ── Walk-forward fold boundaries (date-based, independent of lead time) ──────
def generate_walk_forward_folds(min_date, max_date, n_folds, test_len_h, val_len_h, min_train_frac):
    total_hours = (max_date - min_date) / pd.Timedelta(hours=1)
    min_train_len = total_hours * min_train_frac
    remaining = total_hours - min_train_len
    step = remaining / n_folds

    folds = []
    for k in range(n_folds):
        train_start = min_date
        val_start = min_date + pd.Timedelta(hours=min_train_len + k * step)
        val_end = val_start + pd.Timedelta(hours=val_len_h)
        test_start = val_end
        test_end = test_start + pd.Timedelta(hours=test_len_h)
        if test_end > max_date:
            test_end = max_date
        if test_start >= max_date:
            break
        folds.append(dict(
            fold=k + 1,
            train_start=train_start, train_end=val_start,
            val_start=val_start, val_end=val_end,
            test_start=test_start, test_end=test_end,
        ))
    return folds


# ── Quantile Regression Forest (vectorized) ──────────────────────────────────
class QuantileRandomForest:
    """
    Meinshausen (2006) Quantile Regression Forest.

    A standard Random Forest is grown as usual; the only change is
    that every leaf keeps *all* the training samples that land in it,
    not just their mean. Prediction is vectorized with sparse
    matrices instead of a Python loop over test rows and trees:
    for each tree, a (n_test x n_train) sparse weight matrix is built
    via one-hot leaf memberships, summed across trees, then quantiles
    are read off the resulting weighted empirical CDF in one batched
    cumsum/argmax over the whole test set.
    """

    def __init__(self, n_estimators=200, max_depth=None, min_samples_leaf=30,
                 random_state=42, n_jobs=-1):
        self.rf = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=n_jobs,
        )

    def fit(self, X, y):
        X = np.asarray(X)
        self.y_train_ = np.asarray(y)
        self.rf.fit(X, self.y_train_)
        self.train_leaves_ = self.rf.apply(X)  # (n_train, n_trees)
        self.n_trees_ = self.train_leaves_.shape[1]
        self.n_train_ = X.shape[0]
        return self

    def _tree_weight_matrix(self, t, test_leaf_ids):
        train_leaf_ids = self.train_leaves_[:, t]
        leaves, train_inv = np.unique(train_leaf_ids, return_inverse=True)
        n_leaves = len(leaves)

        train_onehot = sparse.csr_matrix(
            (np.ones(self.n_train_, dtype=np.float32), (np.arange(self.n_train_), train_inv)),
            shape=(self.n_train_, n_leaves),
        )
        leaf_counts = np.asarray(train_onehot.sum(axis=0)).ravel()
        inv_counts = np.divide(1.0, leaf_counts, out=np.zeros_like(leaf_counts), where=leaf_counts > 0)
        train_onehot_norm = train_onehot.multiply(inv_counts).tocsr()

        leaf_to_col = {leaf: i for i, leaf in enumerate(leaves)}
        test_col = np.fromiter(
            (leaf_to_col.get(l, -1) for l in test_leaf_ids), dtype=int, count=len(test_leaf_ids)
        )
        valid = test_col >= 0
        n_test = len(test_leaf_ids)
        test_onehot = sparse.csr_matrix(
            (np.ones(int(valid.sum()), dtype=np.float32), (np.where(valid)[0], test_col[valid])),
            shape=(n_test, n_leaves),
        )
        return test_onehot @ train_onehot_norm.T  # (n_test, n_train), sparse

    def predict_quantiles(self, X, quantiles):
        X = np.asarray(X)
        test_leaves = self.rf.apply(X)  # (n_test, n_trees)
        n_test = X.shape[0]

        W = sparse.csr_matrix((n_test, self.n_train_), dtype=np.float32)
        for t in range(self.n_trees_):
            W = W + self._tree_weight_matrix(t, test_leaves[:, t])
        W = (W / self.n_trees_).toarray().astype(np.float32)

        order = np.argsort(self.y_train_)
        y_sorted = self.y_train_[order]
        W_sorted = W[:, order]
        cdf = np.cumsum(W_sorted, axis=1)
        cdf[:, -1] = 1.0  # guard against floating-point residue

        out = {}
        for a in quantiles:
            idx = np.argmax(cdf >= a, axis=1)
            out[a] = y_sorted[idx]
        del W, W_sorted, cdf
        return out


# ── Quantile Regression (linear) ─────────────────────────────────────────────
# Fit once per fold, with one statsmodels QuantReg model per quantile level
# (IRLS-based), then reuse the fitted models to predict on any X. This is
# both far faster and cheaper than sklearn's QuantileRegressor, which solves
# a linear program per quantile and scales poorly with the number of rows
# (~20s per quantile fit at this project's fold sizes, vs ~2-4s with IRLS).
def fit_quantile_regression_models(X_train, y_train, quantiles, max_iter=1000, p_tol=1e-6):
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_train_c = sm.add_constant(X_train_s, has_constant="add")

    models = {}
    for a in quantiles:
        models[a] = QuantReg(y_train, X_train_c).fit(q=a, max_iter=max_iter, p_tol=p_tol)
    return {"scaler": scaler, "models": models}


def predict_quantile_regression(fitted, X):
    X_s = fitted["scaler"].transform(X)
    X_c = sm.add_constant(X_s, has_constant="add")
    return {a: np.asarray(res.predict(X_c)) for a, res in fitted["models"].items()}


def enforce_monotonicity(preds, quantiles):
    sorted_q = np.sort(quantiles)
    stacked = np.vstack([preds[a] for a in sorted_q])
    before_cross = float(np.mean(np.any(np.diff(stacked, axis=0) < 0, axis=0)))
    stacked_sorted = np.sort(stacked, axis=0)
    fixed = {a: stacked_sorted[k] for k, a in enumerate(sorted_q)}
    return fixed, before_cross


# ── Feature engineering (computed once per lead time, reused across folds) ──
def build_feature_frame(lead_time_hours):
    df = df_raw.copy()
    df["hour"] = df[DATE_COL].dt.hour
    df["dayofweek"] = df[DATE_COL].dt.dayofweek
    df["month"] = df[DATE_COL].dt.month
    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)
    df["is_peak"] = df["hour"].between(7, 20).astype(int)

    df[f"price_lag_{lead_time_hours}"] = df[TARGET].shift(lead_time_hours)
    df[f"price_lag_{lead_time_hours + 24}"] = df[TARGET].shift(lead_time_hours + 24)
    df["price_lag_168"] = df[TARGET].shift(168)
    df["price_rolling_24h"] = df[TARGET].shift(lead_time_hours).rolling(24).mean()
    df = df.dropna().reset_index(drop=True)

    all_features = FEATURE_COLS + [
        "hour", "dayofweek", "month", "is_weekend", "is_peak",
        f"price_lag_{lead_time_hours}", f"price_lag_{lead_time_hours + 24}",
        "price_lag_168", "price_rolling_24h",
    ]
    return df, all_features


def score_quantile_preds(y_true, preds):
    crps, mean_pinball = crps_from_pinball(y_true, preds, QUANTILES)
    row = {"MAE_median": mean_absolute_error(y_true, preds[0.50]),
           "RMSE_median": np.sqrt(mean_squared_error(y_true, preds[0.50])),
           "MeanPinball": mean_pinball, "CRPS_approx": crps}
    for cov, lo_a, hi_a in INTERVALS:
        row[f"Cov_{cov}"] = empirical_coverage(y_true, preds[lo_a], preds[hi_a])
        row[f"Width_{cov}"] = mean_interval_width(preds[lo_a], preds[hi_a])
    return row


# ── Main walk-forward pipeline for one lead time ─────────────────────────────
def run_lead_time(lead_time_hours, fold_boundaries):
    print(f"\n{'=' * 70}")
    print(f"  QR / QRF WALK-FORWARD PIPELINE — LEAD TIME {lead_time_hours}h AHEAD")
    print(f"{'=' * 70}")

    df, all_features = build_feature_frame(lead_time_hours)
    dates = df[DATE_COL]

    fold_rows = []
    reliability_rows = []
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

        # ---- Quantile Regression: fit once, predict on both val and test ----
        qr_fitted = fit_quantile_regression_models(X_train, y_train, QUANTILES)
        qr_val_raw = predict_quantile_regression(qr_fitted, X_val)
        qr_val, _ = enforce_monotonicity(qr_val_raw, QUANTILES)
        qr_test_raw = predict_quantile_regression(qr_fitted, X_test)
        qr_test, qr_cross_rate = enforce_monotonicity(qr_test_raw, QUANTILES)

        # ---- Quantile Regression Forest: pick min_samples_leaf on validation ----
        best_leaf, best_val_pinball, best_model = None, np.inf, None
        for leaf_size in (20, 40):
            candidate = QuantileRandomForest(n_estimators=200, min_samples_leaf=leaf_size,
                                              random_state=42, n_jobs=-1)
            candidate.fit(X_train, y_train)
            val_preds = candidate.predict_quantiles(X_val, QUANTILES)
            _, val_pinball = crps_from_pinball(y_val, val_preds, QUANTILES)
            if val_pinball < best_val_pinball:
                best_leaf, best_val_pinball, best_model = leaf_size, val_pinball, candidate

        qrf_test = best_model.predict_quantiles(X_test, QUANTILES)
        print(f"    QRF selected min_samples_leaf={best_leaf} (val pinball={best_val_pinball:.3f})")

        for name, preds in [("QR", qr_test), ("QRF", qrf_test)]:
            row = score_quantile_preds(y_test, preds)
            row.update({"Model": name, "LeadTime": f"{lead_time_hours}h", "Fold": fold["fold"]})
            if name == "QR":
                row["CrossingRate_before_fix"] = qr_cross_rate
            if name == "QRF":
                row["SelectedMinSamplesLeaf"] = best_leaf
            fold_rows.append(row)

            for cov, lo_a, hi_a in INTERVALS:
                reliability_rows.append({
                    "lead_time": lead_time_hours, "model": name, "fold": fold["fold"],
                    "nominal_coverage": cov / 100.0,
                    "empirical_coverage": empirical_coverage(y_test, preds[lo_a], preds[hi_a]),
                })

        last_fold_fan_data = (test_dates, y_test, {"QR": qr_test, "QRF": qrf_test}, fold["fold"])

    # ── Fan chart for the most recent fold's test window ───────────────────
    if last_fold_fan_data is not None:
        test_dates, y_test, preds_by_model, fold_num = last_fold_fan_data
        plot_forecast_fan(
            test_dates, y_test, preds_by_model, lead_time_hours, f"fold {fold_num}",
            os.path.join(RESULTS_DIR, f"qr_qrf_forecast_{lead_time_hours}h.png"),
        )

    return fold_rows, reliability_rows


# ── Run everything ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    valid_dates = df_raw[DATE_COL]
    fold_boundaries = generate_walk_forward_folds(
        valid_dates.min(), valid_dates.max(), N_FOLDS, TEST_LEN_H, VAL_LEN_H, MIN_TRAIN_FRAC
    )
    print(f"Generated {len(fold_boundaries)} walk-forward folds:")
    for f in fold_boundaries:
        print(f"  Fold {f['fold']}: train [{f['train_start'].date()} -> {f['train_end'].date()}), "
              f"val [{f['val_start'].date()} -> {f['val_end'].date()}), "
              f"test [{f['test_start'].date()} -> {f['test_end'].date()})")

    plot_split_diagram(fold_boundaries, os.path.join(RESULTS_DIR, "train_val_test_split.png"))

    lead_times = [1, 6, 12, 24]
    all_fold_rows = []
    all_reliability_rows = []

    for lt in lead_times:
        fold_rows, reliability_rows = run_lead_time(lt, fold_boundaries)
        all_fold_rows.extend(fold_rows)
        all_reliability_rows.extend(reliability_rows)

    per_fold_df = pd.DataFrame(all_fold_rows)
    per_fold_path = os.path.join(RESULTS_DIR, "qr_qrf_per_fold_metrics.csv")
    per_fold_df.to_csv(per_fold_path, index=False)
    print(f"\nSaved per-fold metrics to: {per_fold_path}")

    metric_cols = ["MAE_median", "RMSE_median", "MeanPinball", "CRPS_approx",
                   "Cov_80", "Width_80", "Cov_90", "Width_90", "Cov_95", "Width_95"]
    summary_df = (
        per_fold_df.groupby(["LeadTime", "Model"])[metric_cols]
        .agg(["mean", "std"])
    )
    summary_path = os.path.join(RESULTS_DIR, "qr_qrf_cv_summary.csv")
    summary_df.to_csv(summary_path)
    print(f"Saved cross-fold summary (mean/std) to: {summary_path}")

    print("\n" + "=" * 100)
    print(f"{'LeadTime':<9}|{'Model':<6}|{'MAE':<8}|{'RMSE':<8}|{'Pinball':<9}|{'CRPS':<8}|{'Cov_80':<8}|{'Cov_95':<8}")
    print("-" * 100)
    for (lt, model), row in summary_df.iterrows():
        print(f"{lt:<9}|{model:<6}|{row[('MAE_median','mean')]:<8.2f}|{row[('RMSE_median','mean')]:<8.2f}|"
              f"{row[('MeanPinball','mean')]:<9.3f}|{row[('CRPS_approx','mean')]:<8.3f}|"
              f"{row[('Cov_80','mean')]:<8.3f}|{row[('Cov_95','mean')]:<8.3f}")
    print("=" * 100)

    # Average reliability across folds before plotting
    rel_df = pd.DataFrame(all_reliability_rows)
    rel_avg = (
        rel_df.groupby(["lead_time", "model", "nominal_coverage"])["empirical_coverage"]
        .mean().reset_index().to_dict("records")
    )
    plot_reliability_diagram(rel_avg, os.path.join(RESULTS_DIR, "qr_qrf_reliability_diagram.png"))

    print("\nWalk-forward QR/QRF comparison complete!")
