"""
Quantile Regression (QR) and Quantile Regression Forest (QRF) for
probabilistic forecasting of significant wave height (swh / Hs) and mean
wave period (mwp / Te), with walk-forward (expanding-window) cross-validation.

Same methodology as the DK1 electricity-price QR/QRF pipeline
(01_Code is a sibling repo section; see 00_Energy/04_Wave_Energy's blog
equivalent, Probabilistic Electricity Price Forecasting Part 2): fit one
model per quantile level (QR) and a Quantile Regression Forest (QRF), score
both with pinball loss, a CRPS approximation, empirical coverage, and mean
interval width, averaged across folds with a standard deviation.

Reuses this project's own conventions rather than copying the electricity
post's numbers verbatim:
  - Walk-forward folds: 6 folds, 1-month validation + 1-month test windows,
    expanding training window (same as LightGBM_ERA5_3.py / Stacking_Ensemble_ERA5.py).
  - Targets: swh and mwp, lead times 1/3/6/12/24/48h (same as those scripts).
  - Features: 4 cyclical time features + one lag per variable, using the
    already-optimised lags from 3_Light_GBM_with_ERA5_Data/Results_3/2.2_best_lags_full.csv,
    with no RFE trimming (this reproduces that project's own "all 17 features,
    no RFE" baseline, which the RFE step already found is what's best or tied-best
    for most target/lead combinations in 2.3_rfe_best_per_lead.csv).
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

from wave_forecasting_plots import plot_split_diagram, plot_forecast_fan, plot_reliability_diagram

# ── Paths ────────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(script_dir, "Results")
os.makedirs(RESULTS_DIR, exist_ok=True)

DATA_PATH = os.path.join(script_dir, "..", "..", "1_Wave_Energy_Flux_Forecasting_part1", "01_Code", "0_Data_Acquisition", "0_ERA5_Data",
                          "ERA5_Ocean_2024_01_to_2026_07.csv")
BEST_LAGS_PATH = os.path.join(script_dir, "..", "..", "1_Wave_Energy_Flux_Forecasting_part1", "01_Code", "3_Light_GBM_with_ERA5_Data",
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


# ── Evaluation helpers (identical to the electricity-price pipeline) ────────
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


# ── Quantile Regression Forest (vectorized, identical to the electricity pipeline) ──
class QuantileRandomForest:
    def __init__(self, n_estimators=200, min_samples_leaf=30, random_state=42, n_jobs=-1):
        self.rf = RandomForestRegressor(
            n_estimators=n_estimators, min_samples_leaf=min_samples_leaf,
            random_state=random_state, n_jobs=n_jobs,
        )

    def fit(self, X, y):
        self.y_train_ = np.asarray(y)
        self.rf.fit(X, self.y_train_)
        self.train_leaves_ = self.rf.apply(X)
        self.n_trees_ = self.train_leaves_.shape[1]
        self.n_train_ = X.shape[0]
        return self

    def _tree_weight_matrix(self, t, test_leaf_ids):
        train_leaf_ids = self.train_leaves_[:, t]
        leaves, train_inv = np.unique(train_leaf_ids, return_inverse=True)
        train_onehot = sparse.csr_matrix(
            (np.ones(self.n_train_, dtype=np.float32), (np.arange(self.n_train_), train_inv)),
            shape=(self.n_train_, len(leaves)),
        )
        leaf_counts = np.asarray(train_onehot.sum(axis=0)).ravel()
        inv_counts = np.divide(1.0, leaf_counts, out=np.zeros_like(leaf_counts), where=leaf_counts > 0)
        train_onehot_norm = train_onehot.multiply(inv_counts).tocsr()

        leaf_to_col = {leaf: i for i, leaf in enumerate(leaves)}
        test_col = np.fromiter((leaf_to_col.get(l, -1) for l in test_leaf_ids), dtype=int, count=len(test_leaf_ids))
        valid = test_col >= 0
        test_onehot = sparse.csr_matrix(
            (np.ones(int(valid.sum()), dtype=np.float32), (np.where(valid)[0], test_col[valid])),
            shape=(len(test_leaf_ids), len(leaves)),
        )
        return test_onehot @ train_onehot_norm.T

    def predict_quantiles(self, X, quantiles):
        test_leaves = self.rf.apply(X)
        n_test = X.shape[0]
        W = sparse.csr_matrix((n_test, self.n_train_), dtype=np.float32)
        for t in range(self.n_trees_):
            W = W + self._tree_weight_matrix(t, test_leaves[:, t])
        W = (W / self.n_trees_).toarray().astype(np.float32)

        order = np.argsort(self.y_train_)
        y_sorted, cdf = self.y_train_[order], np.cumsum(W[:, order], axis=1)
        cdf[:, -1] = 1.0

        return {a: y_sorted[np.argmax(cdf >= a, axis=1)] for a in quantiles}


# ── Quantile Regression (linear, identical to the electricity pipeline) ─────
def fit_quantile_regression_models(X_train, y_train, quantiles, max_iter=1000, p_tol=1e-6):
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_train_c = sm.add_constant(X_train_s, has_constant="add")

    models = {}
    for a in quantiles:
        models[a] = QuantReg(y_train, X_train_c).fit(q=a, max_iter=max_iter, p_tol=p_tol)
    return {"scaler": scaler, "models": models}


def predict_quantile_regression(fitted, X):
    X_c = sm.add_constant(fitted["scaler"].transform(X), has_constant="add")
    return {a: np.asarray(res.predict(X_c)) for a, res in fitted["models"].items()}


def enforce_monotonicity(preds, quantiles):
    sorted_q = np.sort(quantiles)
    stacked = np.vstack([preds[a] for a in sorted_q])
    before_cross = float(np.mean(np.any(np.diff(stacked, axis=0) < 0, axis=0)))
    stacked_sorted = np.sort(stacked, axis=0)
    fixed = {a: stacked_sorted[k] for k, a in enumerate(sorted_q)}
    return fixed, before_cross


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


def score_quantile_preds(y_true, preds):
    crps, mean_pinball = crps_from_pinball(y_true, preds, QUANTILES)
    row = {"MAE_median": mean_absolute_error(y_true, preds[0.50]),
           "RMSE_median": np.sqrt(mean_squared_error(y_true, preds[0.50])),
           "MeanPinball": mean_pinball, "CRPS_approx": crps}
    for cov, lo_a, hi_a in INTERVALS:
        row[f"Cov_{cov}"] = empirical_coverage(y_true, preds[lo_a], preds[hi_a])
        row[f"Width_{cov}"] = mean_interval_width(preds[lo_a], preds[hi_a])
    return row


# ── Main walk-forward pipeline for one target/lead time ─────────────────────
def run_target_lead(target, lead_h, dates):
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

        # ---- QR ----
        qr_fitted = fit_quantile_regression_models(X_train, y_train, QUANTILES)
        qr_val_raw = predict_quantile_regression(qr_fitted, X_val)
        qr_val, _ = enforce_monotonicity(qr_val_raw, QUANTILES)
        qr_test_raw = predict_quantile_regression(qr_fitted, X_test)
        qr_test, qr_cross_rate = enforce_monotonicity(qr_test_raw, QUANTILES)

        # ---- QRF: pick min_samples_leaf on validation ----
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

        print(f"  Fold {fold['fold']}: train={len(y_train)} val={len(y_val)} test={len(y_test)} "
              f"| QRF leaf={best_leaf} | QR crossing={qr_cross_rate:.1%}")

        for name, preds in [("QR", qr_test), ("QRF", qrf_test)]:
            row = score_quantile_preds(y_test, preds)
            row.update({"Model": name, "Target": target, "LeadTime": f"{lead_h}h", "Fold": fold["fold"]})
            if name == "QR":
                row["CrossingRate_before_fix"] = qr_cross_rate
            if name == "QRF":
                row["SelectedMinSamplesLeaf"] = best_leaf
            fold_rows.append(row)

            for cov, lo_a, hi_a in INTERVALS:
                reliability_rows.append({
                    "target": target, "lead_time": lead_h, "model": name, "fold": fold["fold"],
                    "nominal_coverage": cov / 100.0,
                    "empirical_coverage": empirical_coverage(y_test, preds[lo_a], preds[hi_a]),
                })

        last_fold_fan_data = (test_dates, y_test, {"QR": qr_test, "QRF": qrf_test}, fold["fold"])

    if last_fold_fan_data is not None:
        test_dates, y_test, preds_by_model, fold_num = last_fold_fan_data
        unit = "m" if target == "swh" else "s"
        label = "Hs (swh)" if target == "swh" else "Te (mwp)"
        plot_forecast_fan(
            test_dates, y_test, preds_by_model, lead_h, f"fold {fold_num}",
            os.path.join(RESULTS_DIR, f"qrqrf_forecast_{target}_{lead_h}h.png"),
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

    all_fold_rows = []
    all_reliability_rows = []

    for target in TARGETS:
        for lead in LEAD_STEPS:
            print(f"\n{'=' * 70}")
            print(f"  QR / QRF WALK-FORWARD — target={target}, lead={lead}h ahead")
            print(f"{'=' * 70}")
            fold_rows, reliability_rows = run_target_lead(target, lead, t_idx)
            all_fold_rows.extend(fold_rows)
            all_reliability_rows.extend(reliability_rows)

    per_fold_df = pd.DataFrame(all_fold_rows)
    per_fold_path = os.path.join(RESULTS_DIR, "qrqrf_wave_per_fold_metrics.csv")
    per_fold_df.to_csv(per_fold_path, index=False)
    print(f"\nSaved per-fold metrics to: {per_fold_path}")

    metric_cols = ["MAE_median", "RMSE_median", "MeanPinball", "CRPS_approx",
                   "Cov_80", "Width_80", "Cov_90", "Width_90", "Cov_95", "Width_95"]
    summary_df = per_fold_df.groupby(["Target", "LeadTime", "Model"])[metric_cols].agg(["mean", "std"])
    summary_path = os.path.join(RESULTS_DIR, "qrqrf_wave_cv_summary.csv")
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

    print("\nWalk-forward QR/QRF wave forecasting complete!")
