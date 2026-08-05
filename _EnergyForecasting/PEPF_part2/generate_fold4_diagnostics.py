"""
Fold 4 (4-18 July 2025), 1h-ahead tail diagnostics: does QRF's visibly
higher upper tail on the fan chart reflect better tail calibration, or
just over-dispersion?

Reuses the exact same fold boundaries, feature engineering, and model
fitting as qr_qrf_walkforward_pipeline.py, restricted to fold 4 only, so
the QR/QRF predictions here are identical to the ones behind the
published fan chart and results tables.
"""
import os
import numpy as np

import qr_qrf_walkforward_pipeline as pipeline
from forecasting_plots import plot_local_exceedance_rate, plot_interval_width_over_time

script_dir = os.path.dirname(os.path.abspath(__file__))

LEAD_TIME = 1
TAU_UPPER = 0.95
INTERVAL_95 = (0.025, 0.975)

# ── Reproduce the same fold boundaries used everywhere else in the post ─────
valid_dates = pipeline.df_raw[pipeline.DATE_COL]
fold_boundaries = pipeline.generate_walk_forward_folds(
    valid_dates.min(), valid_dates.max(),
    pipeline.N_FOLDS, pipeline.TEST_LEN_H, pipeline.VAL_LEN_H, pipeline.MIN_TRAIN_FRAC,
)
fold4 = fold_boundaries[-1]
print(f"Fold 4 test window: {fold4['test_start']} -> {fold4['test_end']}")

df, all_features = pipeline.build_feature_frame(LEAD_TIME)
dates = df[pipeline.DATE_COL]

train_mask = (dates >= fold4["train_start"]) & (dates < fold4["train_end"])
val_mask = (dates >= fold4["val_start"]) & (dates < fold4["val_end"])
test_mask = (dates >= fold4["test_start"]) & (dates < fold4["test_end"])

X_train, y_train = df.loc[train_mask, all_features].values, df.loc[train_mask, pipeline.TARGET].values
X_val, y_val = df.loc[val_mask, all_features].values, df.loc[val_mask, pipeline.TARGET].values
X_test, y_test = df.loc[test_mask, all_features].values, df.loc[test_mask, pipeline.TARGET].values
test_dates = dates.loc[test_mask].values

print(f"train={len(y_train)}  val={len(y_val)}  test={len(y_test)}")

# ── QR: fit once, predict on test ───────────────────────────────────────────
qr_fitted = pipeline.fit_quantile_regression_models(X_train, y_train, pipeline.QUANTILES)
qr_raw = pipeline.predict_quantile_regression(qr_fitted, X_test)
qr_preds, _ = pipeline.enforce_monotonicity(qr_raw, pipeline.QUANTILES)

# ── QRF: select min_samples_leaf on validation, exactly as in the pipeline ──
best_leaf, best_val_pinball, best_model = None, np.inf, None
for leaf_size in (20, 40):
    candidate = pipeline.QuantileRandomForest(n_estimators=200, min_samples_leaf=leaf_size,
                                               random_state=42, n_jobs=-1)
    candidate.fit(X_train, y_train)
    val_preds = candidate.predict_quantiles(X_val, pipeline.QUANTILES)
    _, val_pinball = pipeline.crps_from_pinball(y_val, val_preds, pipeline.QUANTILES)
    if val_pinball < best_val_pinball:
        best_leaf, best_val_pinball, best_model = leaf_size, val_pinball, candidate

qrf_preds = best_model.predict_quantiles(X_test, pipeline.QUANTILES)
print(f"QRF selected min_samples_leaf={best_leaf} (val pinball={best_val_pinball:.3f})")

preds_by_model = {"QR": qr_preds, "QRF": qrf_preds}

# ── Numeric diagnostics ──────────────────────────────────────────────────────
print(f"\n{'Model':<6}{'Exceed count':<14}{'Exceed rate':<14}{'Upper coverage':<16}{'Deviation from 0.95':<20}")
for name, preds in preds_by_model.items():
    exceed_mask = y_test > preds[TAU_UPPER]
    exceed_count = int(exceed_mask.sum())
    exceed_rate = exceed_mask.mean()
    upper_coverage = float(np.mean(y_test <= preds[TAU_UPPER]))
    deviation = upper_coverage - TAU_UPPER
    print(f"{name:<6}{exceed_count:<14}{exceed_rate:<14.3f}{upper_coverage:<16.3f}{deviation:+.3f}")

print(f"\n{'Model':<6}{'Mean 95% width':<16}{'Cov 95%':<10}")
for name, preds in preds_by_model.items():
    lo, hi = INTERVAL_95
    width = float(np.mean(preds[hi] - preds[lo]))
    cov = float(np.mean((y_test >= preds[lo]) & (y_test <= preds[hi])))
    print(f"{name:<6}{width:<16.2f}{cov:<10.3f}")

# ── Figures ──────────────────────────────────────────────────────────────────
plot_local_exceedance_rate(
    test_dates, y_test, preds_by_model, TAU_UPPER,
    os.path.join(script_dir, "QRQRF_fold4_exceedance_95.png"),
)
plot_interval_width_over_time(
    test_dates, y_test, preds_by_model, INTERVAL_95[0], INTERVAL_95[1],
    os.path.join(script_dir, "QRQRF_fold4_width95_timeline.png"),
    spike_z=1.5,
)

print("\nDone.")
