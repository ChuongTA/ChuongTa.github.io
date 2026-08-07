"""
Stacking Ensemble of Ridge, Random Forest, and LightGBM for ERA5 Ocean Parameter Forecasting

This script builds a stacking ensemble using three base models:
1. Ridge Regression (linear, regularization-tuned)
2. Random Forest Regressor (bagging ensemble of deep decision trees)
3. LightGBM Regressor (boosting ensemble of shallow decision trees)

It uses the pre-computed optimized lag values from LightGBM_ERA5_3.py and performs RFE to
select the best features for each target (swh, mwp) and lead time (1, 3, 6, 12, 24, 48 hours).
"""

import warnings
warnings.filterwarnings("ignore")

import os
import numpy as np
import pandas as pd
import lightgbm as lgb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def smape(y_true, y_pred):
    """Symmetric MAPE: bounded and stable near y_true == 0, unlike plain MAPE."""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2
    denom = np.where(denom == 0, 1e-8, denom)
    return np.mean(np.abs(y_true - y_pred) / denom)

def nrmse(y_true, y_pred):
    """RMSE normalized by the range of y_true, so error magnitude is comparable across targets/lead times."""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    rng = y_true.max() - y_true.min()
    return rmse / rng if rng > 0 else np.nan

# Directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "Results_Stacking")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Path to the data and results from notebook 3
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "0_Data_Acquisition", "0_ERA5_Data", "ERA5_Ocean_2024_01_to_2026_07.csv")
BEST_LAGS_PATH = os.path.join(SCRIPT_DIR, "..", "3_Light_GBM_with_ERA5_Data", "Results_3", "2.2_best_lags_full.csv")

TARGETS = ["swh", "mwp"]
LEAD_STEPS = [1, 3, 6, 12, 24, 48]
N_FOLDS = 6
VALID_WINDOW = pd.DateOffset(months=1)
TEST_WINDOW = pd.DateOffset(months=1)

RIDGE_ALPHA_CANDIDATES = [0.1, 1.0, 10.0, 100.0]
RF_MAX_DEPTH_CANDIDATES = [4, 8, 12, 16]

# 1. Load Data
# ---------------------------------------------------------------------------
print("Loading ERA5 dataset...")
raw = pd.read_csv(DATA_PATH, parse_dates=["valid_time"])
raw = raw.sort_values("valid_time").reset_index(drop=True)
raw = raw.ffill()
print("Loaded dataset shape:", raw.shape)

# Load best lags
print("Loading optimized lags from step 3...")
best_lags_df = pd.read_csv(BEST_LAGS_PATH)

# Build best_lags dictionary structure: best_lags[target][lead][variable] = lag
best_lags = {}
for target in TARGETS:
    best_lags[target] = {}
    for lead in LEAD_STEPS:
        best_lags[target][lead] = {}
        subset = best_lags_df[(best_lags_df["target"] == target) & (best_lags_df["lead_h"] == lead)]
        for _, row in subset.iterrows():
            best_lags[target][lead][row["variable"]] = int(row["lag"])

# 2. Build splits (Active fold)
# ---------------------------------------------------------------------------
t_idx = raw["valid_time"]
data_start = t_idx.min()
data_end = t_idx.max()

def build_walk_forward_folds(t_idx, data_start, data_end, n_folds, valid_window, test_window):
    fold_test_ends = sorted(data_end - i * test_window for i in range(n_folds))
    folds = []
    for test_end in fold_test_ends:
        test_start = test_end - test_window + pd.Timedelta(hours=1)
        valid_end = test_start - pd.Timedelta(hours=1)
        valid_start = valid_end - valid_window + pd.Timedelta(hours=1)
        train_end = valid_start - pd.Timedelta(hours=1)

        train_mask = (t_idx >= data_start) & (t_idx <= train_end)
        valid_mask = (t_idx >= valid_start) & (t_idx <= valid_end)
        test_mask = (t_idx >= test_start) & (t_idx <= test_end)

        folds.append({
            "train_mask": train_mask, "valid_mask": valid_mask, "test_mask": test_mask,
        })
    return folds

folds = build_walk_forward_folds(t_idx, data_start, data_end, N_FOLDS, VALID_WINDOW, TEST_WINDOW)
active_fold = folds[-1]
train_m, valid_m, test_m = active_fold["train_mask"], active_fold["valid_mask"], active_fold["test_mask"]
train_valid_m = train_m | valid_m

# 3. Helper Functions for Stacking Base Models
# ---------------------------------------------------------------------------
def fit_ridge(X_train, y_train, X_valid, y_valid):
    best_alpha = None
    best_mae = np.inf
    best_model = None

    for alpha in RIDGE_ALPHA_CANDIDATES:
        model = Ridge(alpha=alpha, random_state=42)
        model.fit(X_train, y_train)
        pred = model.predict(X_valid)
        mae = mean_absolute_error(y_valid, pred)
        if mae < best_mae:
            best_mae = mae
            best_alpha = alpha
            best_model = model

    return best_model, best_alpha

def fit_random_forest(X_train, y_train, X_valid, y_valid):
    best_depth = None
    best_mae = np.inf
    best_model = None

    for depth in RF_MAX_DEPTH_CANDIDATES:
        model = RandomForestRegressor(max_depth=depth, n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        pred = model.predict(X_valid)
        mae = mean_absolute_error(y_valid, pred)
        if mae < best_mae:
            best_mae = mae
            best_depth = depth
            best_model = model

    return best_model, best_depth

def fit_lightgbm(X_train, y_train, X_valid, y_valid):
    model = lgb.LGBMRegressor(random_state=42, verbose=-1)
    model.fit(
        X_train, y_train,
        eval_set=[(X_valid, y_valid)],
        callbacks=[lgb.early_stopping(stopping_rounds=15, verbose=False)]
    )
    return model

# 4. Feature Selection using RFE
# ---------------------------------------------------------------------------
def build_lead_features(target, lead):
    lag_info = best_lags[target][lead]
    feat_dict = {
        "hour_sin": np.sin(2 * np.pi * raw["valid_time"].dt.hour / 24),
        "hour_cos": np.cos(2 * np.pi * raw["valid_time"].dt.hour / 24),
        "doy_sin": np.sin(2 * np.pi * raw["valid_time"].dt.dayofyear / 365.25),
        "doy_cos": np.cos(2 * np.pi * raw["valid_time"].dt.dayofyear / 365.25),
    }
    for col, info in lag_info.items():
        feat_dict[f"{col}_lag{info}"] = raw[col].shift(info)
    X = pd.DataFrame(feat_dict, index=raw.index)
    y = raw[target].shift(-lead)
    return X, y

def evaluate_rfe(target, lead):
    X, y = build_lead_features(target, lead)
    valid_rows = X.notna().all(axis=1) & y.notna()

    X_train, y_train = X[train_m & valid_rows], y[train_m & valid_rows]
    X_valid, y_valid = X[valid_m & valid_rows], y[valid_m & valid_rows]

    current_features = list(X.columns)
    history = []

    while True:
        model = lgb.LGBMRegressor(random_state=42, verbose=-1)
        model.fit(X_train[current_features], y_train)
        pred = model.predict(X_valid[current_features])

        history.append({
            "n_features": len(current_features),
            "features": tuple(current_features),
            "rmse": np.sqrt(mean_squared_error(y_valid, pred)),
            "r2": r2_score(y_valid, pred),
        })

        if len(current_features) <= 1:
            break

        importances = model.feature_importances_
        weakest_idx = np.argsort(importances)[:min(5, len(current_features) - 1)]
        weakest = [current_features[i] for i in weakest_idx]
        current_features = [f for f in current_features if f not in weakest]

    history_df = pd.DataFrame(history)
    best_idx = history_df["r2"].idxmax()
    best_features = list(history_df.loc[best_idx, "features"])
    return best_features

# 5. Stacking Staging
# ---------------------------------------------------------------------------
results_table = []
predictions = {}
best_models = {}

# Dictionary to hold test metrics for base models and stacking model for the spider plots
radar_metrics = {
    target: {
        "Ridge": {"MSE": [], "NRMSE": [], "SMAPE": []},
        "Random Forest": {"MSE": [], "NRMSE": [], "SMAPE": []},
        "LightGBM": {"MSE": [], "NRMSE": [], "SMAPE": []},
        "Stacking model": {"MSE": [], "NRMSE": [], "SMAPE": []}
    } for target in TARGETS
}

for target in TARGETS:
    for lead in LEAD_STEPS:
        print(f"\n=======================================================")
        print(f"Stacking Ensemble for target={target}, lead={lead}h")
        print(f"=======================================================")
        
        # 5.1 Build features & select
        print("Selecting best RFE features...")
        best_features = evaluate_rfe(target, lead)
        print(f"Selected {len(best_features)} features: {best_features}")
        
        X, y = build_lead_features(target, lead)
        valid_rows = X.notna().all(axis=1) & y.notna()
        
        X_train, y_train = X[train_m & valid_rows][best_features], y[train_m & valid_rows]
        X_valid, y_valid = X[valid_m & valid_rows][best_features], y[valid_m & valid_rows]
        X_test, y_test = X[test_m & valid_rows][best_features], y[test_m & valid_rows]
        t_test = raw["valid_time"][test_m & valid_rows]
        
        # Scale for Ridge
        scaler = StandardScaler().fit(X_train)
        X_train_s = scaler.transform(X_train)
        X_valid_s = scaler.transform(X_valid)
        X_test_s = scaler.transform(X_test)
        
        # 5.2 Fit Ridge Base Model
        print("Training Ridge base model...")
        ridge_model, ridge_alpha = fit_ridge(X_train_s, y_train, X_valid_s, y_valid)
        ridge_valid_pred = ridge_model.predict(X_valid_s)
        ridge_test_pred = ridge_model.predict(X_test_s)
        ridge_mse = mean_squared_error(y_test, ridge_test_pred)
        ridge_rmse = np.sqrt(ridge_mse)
        ridge_r2 = r2_score(y_test, ridge_test_pred)
        print(f"   Ridge (alpha={ridge_alpha}) validation MAE: {mean_absolute_error(y_valid, ridge_valid_pred):.4f}")
        
        # 5.3 Fit Random Forest Base Model
        print("Training Random Forest base model...")
        rf_model, rf_depth = fit_random_forest(X_train, y_train, X_valid, y_valid)
        rf_valid_pred = rf_model.predict(X_valid)
        rf_test_pred = rf_model.predict(X_test)
        rf_mse = mean_squared_error(y_test, rf_test_pred)
        rf_rmse = np.sqrt(rf_mse)
        rf_r2 = r2_score(y_test, rf_test_pred)
        print(f"   Random Forest (max_depth={rf_depth}) validation MAE: {mean_absolute_error(y_valid, rf_valid_pred):.4f}")
        
        # 5.4 Fit LightGBM Base Model
        print("Training LightGBM base model...")
        lgbm_model = fit_lightgbm(X_train, y_train, X_valid, y_valid)
        lgbm_valid_pred = lgbm_model.predict(X_valid)
        lgbm_test_pred = lgbm_model.predict(X_test)
        lgbm_mse = mean_squared_error(y_test, lgbm_test_pred)
        lgbm_rmse = np.sqrt(lgbm_mse)
        lgbm_r2 = r2_score(y_test, lgbm_test_pred)
        print(f"   LightGBM validation RMSE: {np.sqrt(mean_squared_error(y_valid, lgbm_valid_pred)):.4f}")
        
        # 5.5 Fit Stacking Meta-Model
        print("Training Stacking Meta-model (Ridge)...")
        meta_X_valid = np.column_stack([ridge_valid_pred, rf_valid_pred, lgbm_valid_pred])
        meta_X_test = np.column_stack([ridge_test_pred, rf_test_pred, lgbm_test_pred])
        
        meta_model = Ridge(alpha=1.0)
        meta_model.fit(meta_X_valid, y_valid)
        stack_test_pred = meta_model.predict(meta_X_test)
        stack_mse = mean_squared_error(y_test, stack_test_pred)
        stack_rmse = np.sqrt(stack_mse)
        stack_r2 = r2_score(y_test, stack_test_pred)
        
        # Save predictions for all models
        predictions[(target, lead, "Ridge")] = (t_test.values, y_test.values, ridge_test_pred)
        predictions[(target, lead, "Random Forest")] = (t_test.values, y_test.values, rf_test_pred)
        predictions[(target, lead, "LightGBM")] = (t_test.values, y_test.values, lgbm_test_pred)
        predictions[(target, lead, "Stacking model")] = (t_test.values, y_test.values, stack_test_pred)
        
        # Determine the best model based on test RMSE
        model_rmse = {
            "Ridge": ridge_rmse,
            "Random Forest": rf_rmse,
            "LightGBM": lgbm_rmse,
            "Stacking model": stack_rmse
        }
        best_model = min(model_rmse, key=model_rmse.get)
        best_models[(target, lead)] = best_model
        
        # Store metrics in radar_metrics dict
        radar_metrics[target]["Ridge"]["MSE"].append(ridge_mse)
        radar_metrics[target]["Ridge"]["NRMSE"].append(nrmse(y_test, ridge_test_pred))
        radar_metrics[target]["Ridge"]["SMAPE"].append(smape(y_test, ridge_test_pred))

        radar_metrics[target]["Random Forest"]["MSE"].append(rf_mse)
        radar_metrics[target]["Random Forest"]["NRMSE"].append(nrmse(y_test, rf_test_pred))
        radar_metrics[target]["Random Forest"]["SMAPE"].append(smape(y_test, rf_test_pred))

        radar_metrics[target]["LightGBM"]["MSE"].append(lgbm_mse)
        radar_metrics[target]["LightGBM"]["NRMSE"].append(nrmse(y_test, lgbm_test_pred))
        radar_metrics[target]["LightGBM"]["SMAPE"].append(smape(y_test, lgbm_test_pred))

        radar_metrics[target]["Stacking model"]["MSE"].append(stack_mse)
        radar_metrics[target]["Stacking model"]["NRMSE"].append(nrmse(y_test, stack_test_pred))
        radar_metrics[target]["Stacking model"]["SMAPE"].append(smape(y_test, stack_test_pred))

        # Compute final test metrics
        mae = mean_absolute_error(y_test, stack_test_pred)
        stack_nrmse = nrmse(y_test, stack_test_pred)
        stack_smape = smape(y_test, stack_test_pred)

        print(f"--> STACKED test set metrics: MAE={mae:.4f}, RMSE={stack_rmse:.4f}, "
              f"NRMSE={stack_nrmse:.4f}, SMAPE={stack_smape:.4f}, R2={stack_r2:.4f}")
        print(f"--> BEST MODEL: {best_model} (RMSE={model_rmse[best_model]:.4f})")

        results_table.append({
            "target": target,
            "lead_h": lead,
            "MAE": mae,
            "RMSE": stack_rmse,
            "NRMSE": stack_nrmse,
            "SMAPE": stack_smape,
            "R2": stack_r2,
            "ridge_coef": meta_model.coef_[0],
            "rf_coef": meta_model.coef_[1],
            "lgbm_coef": meta_model.coef_[2],
            "intercept": meta_model.intercept_
        })

# 6. Save and Report Stacking Results
# ---------------------------------------------------------------------------
results_df = pd.DataFrame(results_table)
numeric_cols = results_df.select_dtypes(include="number").columns.drop(["lead_h"])
results_df[numeric_cols] = results_df[numeric_cols].round(2)
print("\nFinal Stacking Ensemble Test Results:")
print(results_df)
results_df.to_csv(os.path.join(RESULTS_DIR, "stacking_ensemble_results.csv"), index=False)

# 7. Compute Stacked Wave Power Predictions
# ---------------------------------------------------------------------------
def compute_power_series(lead):
    best_model_swh = best_models[("swh", lead)]
    best_model_mwp = best_models[("mwp", lead)]
    
    tt_h, actual_h, pred_h = predictions[("swh", lead, best_model_swh)]
    tt_t, actual_t, pred_t = predictions[("mwp", lead, best_model_mwp)]

    s_actual_h = pd.Series(actual_h, index=tt_h)
    s_pred_h = pd.Series(pred_h, index=tt_h)
    s_actual_t = pd.Series(actual_t, index=tt_t)
    s_pred_t = pd.Series(pred_t, index=tt_t)

    common_idx = s_actual_h.index.intersection(s_actual_t.index).sort_values()

    actual_power = 0.5 * s_actual_h.loc[common_idx].values ** 2 * s_actual_t.loc[common_idx].values
    pred_power = 0.5 * s_pred_h.loc[common_idx].values ** 2 * s_pred_t.loc[common_idx].values
    return common_idx.values, actual_power, pred_power

power_predictions = {lead: compute_power_series(lead) for lead in LEAD_STEPS}

# 8. Plots
# ---------------------------------------------------------------------------
ROW_COLORS = {
    "swh": {"actual": "#2a78d6", "predicted": "#eb6834"},        # blue / orange
    "mwp": {"actual": "#1baf7a", "predicted": "#eda100"},        # aqua / yellow
    "wave_power": {"actual": "#e87ba4", "predicted": "#008300"}, # magenta / green
}

def plot_forecast_group(leads, group_name):
    row_labels = TARGETS + ["wave_power"]
    fig, axes = plt.subplots(len(row_labels), len(leads), figsize=(18, 12))
    
    for i, target in enumerate(TARGETS):
        colors = ROW_COLORS[target]
        for j, lead in enumerate(leads):
            best_m = best_models[(target, lead)]
            tt, actual, pred = predictions[(target, lead, best_m)]
            r2 = r2_score(actual, pred)
            ax = axes[i, j]
            ax.plot(tt[-400:], actual[-400:], label="Actual", color=colors["actual"], alpha=0.9)
            ax.plot(tt[-400:], pred[-400:], label=f"Predicted ({best_m})", color=colors["predicted"], alpha=0.9)
            ax.set_title(f"{target.upper()} - Lead = {lead}h\n(Best: {best_m} | R² = {r2:.4f})")
            ax.set_ylabel("Value")
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.grid(True)
            ax.legend()
            
    power_row = len(TARGETS)
    power_colors = ROW_COLORS["wave_power"]
    for j, lead in enumerate(leads):
        tt, actual_power, pred_power = power_predictions[lead]
        r2_power = r2_score(actual_power, pred_power)
        ax = axes[power_row, j]
        ax.plot(tt[-400:], actual_power[-400:], label="Actual", color=power_colors["actual"], alpha=0.9)
        ax.plot(tt[-400:], pred_power[-400:], label="Predicted", color=power_colors["predicted"], alpha=0.9)
        
        best_swh = best_models[("swh", lead)]
        best_mwp = best_models[("mwp", lead)]
        ax.set_title(f"Wave Power - Lead = {lead}h\n(R² = {r2_power:.4f} | SWH: {best_swh} | MWP: {best_mwp})")
        ax.set_ylabel("Power")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.grid(True)
        ax.legend()
        
    plt.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, f"stacking_forecast_{group_name}.png"), dpi=150, bbox_inches="tight")
    plt.close()

# Plot groups
plot_forecast_group([1, 3, 6], "1_3_6h")
plot_forecast_group([12, 24, 48], "12_24_48h")

# 9. Stacking Performance Bar Charts
# ---------------------------------------------------------------------------
def plot_bar_charts(target, metrics_data, filename):
    model_names = ["Ridge", "Random Forest", "LightGBM", "Stacking model"]
    metrics = ["MSE", "NRMSE", "SMAPE"]
    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # blue, orange, aqua, yellow
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    x = np.arange(len(LEAD_STEPS))
    width = 0.2  # width of each bar
    
    for ax, metric in zip(axes, metrics):
        for i, model in enumerate(model_names):
            values = metrics_data[model][metric]
            ax.bar(x + i * width, values, width, label=model, color=colors[i])
            
        ax.set_ylabel(metric)
        ax.set_title(f"{metric} Comparison by Lead Time", fontsize=14, fontweight='bold')
        ax.set_xticks(x + 1.5 * width)
        ax.set_xticklabels([f"{lead}h" for lead in LEAD_STEPS])
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend()
        
    plt.suptitle(f"Performance Comparison for {target.upper()} by Lead Time", fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

print("Generating performance bar charts...")
for target in TARGETS:
    plot_bar_charts(target, radar_metrics[target], os.path.join(RESULTS_DIR, f"{target}_performance_bars.png"))

print("Stacking execution completed successfully. Plots and results saved in Results_Stacking folder.")
