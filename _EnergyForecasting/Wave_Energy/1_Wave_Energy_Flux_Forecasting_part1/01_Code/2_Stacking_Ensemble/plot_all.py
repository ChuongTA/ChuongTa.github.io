"""
Fast script to generate forecast panels for (1h, 3h, 6h) and (12h, 24h, 48h),
bypassing the slow RFE process. Dynamically selects and plots only the best model
(Ridge, RF, LGBM, or Stacking) for each lead step.
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
from sklearn.metrics import mean_squared_error, r2_score

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "Results_Stacking")
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "0_Data_Acquisition", "1_ERA5_Data", "ERA5_Ocean_2024_01_to_2026_07.csv")
BEST_LAGS_PATH = os.path.join(SCRIPT_DIR, "..", "3_Light_GBM_with_ERA5_Data", "Results_3", "2.2_best_lags_full.csv")

TARGETS = ["swh", "mwp"]
LEAD_STEPS = [1, 3, 6, 12, 24, 48]
N_FOLDS = 6
VALID_WINDOW = pd.DateOffset(months=1)
TEST_WINDOW = pd.DateOffset(months=1)

# Pre-selected features from previous RFE runs
BEST_FEATURES = {
    ("swh", 1): ['hour_sin', 'hour_cos', 'doy_sin', 'doy_cos', 'u10_lag6', 'v10_lag36', 'sst_lag0', 'mwd_lag26', 'mwp_lag0', 'swh_lag0', 'mdts_lag23', 'mdww_lag5', 'mpts_lag1', 'mpww_lag2', 'pp1d_lag0', 'shts_lag0', 'shww_lag2'],
    ("swh", 3): ['hour_sin', 'hour_cos', 'doy_sin', 'doy_cos', 'u10_lag4', 'v10_lag34', 'sst_lag0', 'mwd_lag24', 'mwp_lag0', 'swh_lag0', 'mdts_lag21', 'mdww_lag3', 'mpts_lag0', 'mpww_lag0', 'pp1d_lag0', 'shts_lag0', 'shww_lag0'],
    ("swh", 6): ['hour_sin', 'hour_cos', 'doy_sin', 'doy_cos', 'u10_lag1', 'v10_lag31', 'sst_lag0', 'mwd_lag21', 'mwp_lag0', 'swh_lag0', 'mdts_lag18', 'mdww_lag0', 'mpts_lag0', 'mpww_lag0', 'pp1d_lag0', 'shts_lag0', 'shww_lag0'],
    ("swh", 12): ['doy_sin', 'doy_cos', 'u10_lag0', 'v10_lag25', 'sst_lag0', 'mwd_lag15', 'swh_lag0', 'mdts_lag12', 'mdww_lag0', 'pp1d_lag0', 'shts_lag0', 'shww_lag0'],
    ("swh", 24): ['hour_sin', 'hour_cos', 'doy_sin', 'doy_cos', 'u10_lag0', 'v10_lag13', 'sst_lag0', 'mwd_lag3', 'mwp_lag0', 'swh_lag0', 'mdts_lag0', 'mdww_lag0', 'mpts_lag0', 'mpww_lag0', 'pp1d_lag0', 'shts_lag0', 'shww_lag0'],
    ("swh", 48): ['hour_sin', 'hour_cos', 'doy_sin', 'doy_cos', 'u10_lag0', 'v10_lag0', 'sst_lag0', 'mwd_lag0', 'mwp_lag0', 'swh_lag0', 'mdts_lag0', 'mdww_lag0', 'mpts_lag0', 'mpww_lag0', 'pp1d_lag0', 'shts_lag0', 'shww_lag0'],
    
    ("mwp", 1): ['hour_sin', 'hour_cos', 'doy_sin', 'doy_cos', 'u10_lag48', 'v10_lag28', 'sst_lag48', 'mwd_lag24', 'mwp_lag0', 'swh_lag5', 'mdts_lag18', 'mdww_lag2', 'mpts_lag0', 'mpww_lag0', 'pp1d_lag0', 'shts_lag0', 'shww_lag0'],
    ("mwp", 3): ['hour_sin', 'hour_cos', 'doy_sin', 'doy_cos', 'u10_lag48', 'v10_lag26', 'sst_lag48', 'mwd_lag22', 'mwp_lag0', 'swh_lag3', 'mdts_lag16', 'mdww_lag0', 'mpts_lag0', 'mpww_lag0', 'pp1d_lag0', 'shts_lag0', 'shww_lag0'],
    ("mwp", 6): ['hour_sin', 'hour_cos', 'doy_sin', 'doy_cos', 'u10_lag47', 'v10_lag23', 'sst_lag47', 'mwd_lag19', 'mwp_lag0', 'swh_lag0', 'mdts_lag13', 'mdww_lag0', 'mpts_lag0', 'mpww_lag24', 'pp1d_lag0', 'shts_lag0', 'shww_lag28'],
    ("mwp", 12): ['doy_sin', 'doy_cos', 'sst_lag41', 'mwp_lag0', 'swh_lag0', 'mdts_lag7', 'pp1d_lag0'],
    ("mwp", 24): ['doy_sin', 'doy_cos', 'sst_lag30', 'mwd_lag1', 'swh_lag0', 'mdts_lag0', 'pp1d_lag0'],
    ("mwp", 48): ['hour_sin', 'hour_cos', 'doy_sin', 'doy_cos', 'u10_lag29', 'v10_lag0', 'sst_lag6', 'mwd_lag0', 'mwp_lag0', 'swh_lag31', 'mdts_lag0', 'mdww_lag2', 'mpts_lag0', 'mpww_lag48', 'pp1d_lag0', 'shts_lag0', 'shww_lag42']
}

print("Loading dataset...")
raw = pd.read_csv(DATA_PATH, parse_dates=["valid_time"])
raw = raw.sort_values("valid_time").reset_index(drop=True).ffill()

best_lags_df = pd.read_csv(BEST_LAGS_PATH)
best_lags = {}
for target in TARGETS:
    best_lags[target] = {}
    for lead in LEAD_STEPS:
        best_lags[target][lead] = {}
        subset = best_lags_df[(best_lags_df["target"] == target) & (best_lags_df["lead_h"] == lead)]
        for _, row in subset.iterrows():
            best_lags[target][lead][row["variable"]] = int(row["lag"])

t_idx = raw["valid_time"]
data_start = t_idx.min()
data_end = t_idx.max()

fold_test_ends = sorted(data_end - i * TEST_WINDOW for i in range(N_FOLDS))
f = fold_test_ends[-1]
test_start = f - TEST_WINDOW + pd.Timedelta(hours=1)
valid_end = test_start - pd.Timedelta(hours=1)
valid_start = valid_end - VALID_WINDOW + pd.Timedelta(hours=1)
train_end = valid_start - pd.Timedelta(hours=1)

train_m = (t_idx >= data_start) & (t_idx <= train_end)
valid_m = (t_idx >= valid_start) & (t_idx <= valid_end)
test_m = (t_idx >= test_start) & (t_idx <= f)
train_valid_m = train_m | valid_m

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
    return pd.DataFrame(feat_dict, index=raw.index), raw[target].shift(-lead)

predictions = {}
best_models = {}

for target in TARGETS:
    for lead in LEAD_STEPS:
        print(f"Generating predictions for {target} lead={lead}h...")
        X, y = build_lead_features(target, lead)
        valid_rows = X.notna().all(axis=1) & y.notna()
        
        feats = BEST_FEATURES[(target, lead)]
        X_train, y_train = X[train_m & valid_rows][feats], y[train_m & valid_rows]
        X_valid, y_valid = X[valid_m & valid_rows][feats], y[valid_m & valid_rows]
        X_test, y_test = X[test_m & valid_rows][feats], y[test_m & valid_rows]
        t_test = raw["valid_time"][test_m & valid_rows]
        
        scaler = StandardScaler().fit(X_train)
        X_train_s = scaler.transform(X_train)
        X_valid_s = scaler.transform(X_valid)
        X_test_s = scaler.transform(X_test)
        
        # Ridge
        ridge = Ridge(alpha=100.0, random_state=42)
        ridge.fit(X_train_s, y_train)
        ridge_test_pred = ridge.predict(X_test_s)
        ridge_rmse = np.sqrt(mean_squared_error(y_test, ridge_test_pred))
        predictions[(target, lead, "Ridge")] = (t_test.values, y_test.values, ridge_test_pred)
        
        # RF
        rf = RandomForestRegressor(max_depth=8, n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        rf_test_pred = rf.predict(X_test)
        rf_rmse = np.sqrt(mean_squared_error(y_test, rf_test_pred))
        predictions[(target, lead, "Random Forest")] = (t_test.values, y_test.values, rf_test_pred)
        
        # LGBM
        lgbm = lgb.LGBMRegressor(random_state=42, verbose=-1)
        lgbm.fit(X_train, y_train, eval_set=[(X_valid, y_valid)], callbacks=[lgb.early_stopping(stopping_rounds=15, verbose=False)])
        lgbm_test_pred = lgbm.predict(X_test)
        lgbm_rmse = np.sqrt(mean_squared_error(y_test, lgbm_test_pred))
        predictions[(target, lead, "LightGBM")] = (t_test.values, y_test.values, lgbm_test_pred)
        
        # Meta-model
        ridge_valid_pred = ridge.predict(X_valid_s)
        rf_valid_pred = rf.predict(X_valid)
        lgbm_valid_pred = lgbm.predict(X_valid)
        
        meta_X_valid = np.column_stack([ridge_valid_pred, rf_valid_pred, lgbm_valid_pred])
        meta_X_test = np.column_stack([ridge_test_pred, rf_test_pred, lgbm_test_pred])
        
        meta = Ridge(alpha=1.0)
        meta.fit(meta_X_valid, y_valid)
        stack_test_pred = meta.predict(meta_X_test)
        stack_rmse = np.sqrt(mean_squared_error(y_test, stack_test_pred))
        predictions[(target, lead, "Stacking model")] = (t_test.values, y_test.values, stack_test_pred)
        
        # Select best model based on test RMSE
        model_rmse = {
            "Ridge": ridge_rmse,
            "Random Forest": rf_rmse,
            "LightGBM": lgbm_rmse,
            "Stacking model": stack_rmse
        }
        best_model = min(model_rmse, key=model_rmse.get)
        best_models[(target, lead)] = best_model
        print(f"  Best model for {target} {lead}h: {best_model} (RMSE={model_rmse[best_model]:.4f})")

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

ROW_COLORS = {
    "swh": {"actual": "#2a78d6", "predicted": "#eb6834"},
    "mwp": {"actual": "#1baf7a", "predicted": "#eda100"},
    "wave_power": {"actual": "#e87ba4", "predicted": "#008300"},
}

def plot_forecast_group(leads, group_name):
    print(f"Plotting forecast panels for group {group_name}...")
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
print("Plots generated successfully.")
