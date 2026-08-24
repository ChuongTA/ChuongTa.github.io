import os
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import lightgbm as lgb
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings("ignore")

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRICE_CSV = os.path.normpath(os.path.join(SCRIPT_DIR, "../04_Electricity_Price/Data.csv"))
LOAD_CSV = os.path.normpath(os.path.join(SCRIPT_DIR, "../01_Load/Community_Load_Profiles.csv"))
PV_CSV = os.path.normpath(os.path.join(SCRIPT_DIR, "../02_PV_Generation/ERA5_PV_Generation_50MW.csv"))

OUTPUT_PLOT = os.path.join(SCRIPT_DIR, "bess_schedule_simulation.png")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "bess_schedule_tomorrow.csv")

# Constants
EUR_TO_DKK = 7.46   # 1 EUR = 7.46 DKK (Denmark)
MWH_TO_KWH = 1000.0 # 1 MWh = 1000 kWh

def main():
    print("--- Starting Price Forecasting & BESS Optimization Pipeline ---")
    
    # 1. Load Datasets
    print("Loading data files...")
    df_price = pd.read_csv(PRICE_CSV, sep=";", decimal=",", parse_dates=["HourUTC"])
    df_load = pd.read_csv(LOAD_CSV, parse_dates=["timestamp"])
    df_pv = pd.read_csv(PV_CSV, parse_dates=["timestamp"])
    
    # Align price column names
    df_price = df_price.rename(columns={"HourUTC": "timestamp", "DK1_EUR/MWh": "price_eur_mwh"})
    df_price = df_price.sort_values("timestamp").reset_index(drop=True)
    df_price["price_dkk_kwh"] = (df_price["price_eur_mwh"] * EUR_TO_DKK) / MWH_TO_KWH
    
    # Merge datasets on timestamp
    df_all = pd.merge(df_price[["timestamp", "price_dkk_kwh"]], df_load, on="timestamp", how="inner")
    df_all = pd.merge(df_all, df_pv[["timestamp", "pv_output_kw"]], on="timestamp", how="inner")
    df_all = df_all.sort_values("timestamp").reset_index(drop=True)
    
    # 2. Set Up Date Horizon Splits
    train_end = pd.Timestamp("2025-06-06 23:00:00")
    test_date = pd.Timestamp("2025-06-08") # Tomorrow
    
    print(f"Split Config: Training up to {train_end.date()}, Evaluating decision for {test_date.date()}")
    
    # 3. Train Price Forecasting Model (LightGBM)
    # Simple feature engineering
    df_all["hour"] = df_all["timestamp"].dt.hour
    df_all["dayofweek"] = df_all["timestamp"].dt.dayofweek
    df_all["month"] = df_all["timestamp"].dt.month
    df_all["price_lag_24"] = df_all["price_dkk_kwh"].shift(24)
    df_all["price_lag_168"] = df_all["price_dkk_kwh"].shift(168)
    
    df_all = df_all.dropna().reset_index(drop=True)
    
    train_mask = df_all["timestamp"] <= train_end
    df_train = df_all[train_mask]
    
    features = ["hour", "dayofweek", "month", "price_lag_24", "price_lag_168"]
    X_train, y_train = df_train[features], df_train["price_dkk_kwh"]
    
    print("Training LightGBM Day-Ahead price forecast model...")
    model = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.05, num_leaves=31, random_state=42, verbose=-1)
    model.fit(X_train, y_train)
    
    # Predict for tomorrow (2025-06-08)
    tomorrow_mask = df_all["timestamp"].dt.date == test_date.date()
    df_tomorrow = df_all[tomorrow_mask].copy()
    
    if len(df_tomorrow) != 24:
        print(f"Error: Did not find exactly 24 hours for {test_date.date()}. Found {len(df_tomorrow)} hours.")
        return
        
    X_tomorrow = df_tomorrow[features]
    df_tomorrow["price_forecast_dkk_kwh"] = model.predict(X_tomorrow)
    
    # 4. Uncertainty Estimation (Binned Residuals)
    # Get out-of-fold validation residuals (simulated as training residuals here)
    train_preds = model.predict(X_train)
    residuals = y_train - train_preds
    
    # Group residuals into 5 price prediction bins to simulate value-binned bootstrap
    bin_edges = np.percentile(train_preds, np.linspace(0, 100, 6))
    bin_edges[0], bin_edges[-1] = -np.inf, np.inf
    train_bin_idx = np.digitize(train_preds, bin_edges[1:-1])
    
    p10_offsets = []
    p90_offsets = []
    for h_pred in df_tomorrow["price_forecast_dkk_kwh"]:
        b = np.digitize([h_pred], bin_edges[1:-1])[0]
        bin_res = residuals[train_bin_idx == b]
        p10_offsets.append(np.percentile(bin_res, 10))
        p90_offsets.append(np.percentile(bin_res, 90))
        
    df_tomorrow["price_P10"] = (df_tomorrow["price_forecast_dkk_kwh"] + p10_offsets).round(2)
    df_tomorrow["price_P90"] = (df_tomorrow["price_forecast_dkk_kwh"] + p90_offsets).round(2)
    df_tomorrow["price_forecast_dkk_kwh"] = df_tomorrow["price_forecast_dkk_kwh"].round(2)

    # 5. Load and PV Forecasts (Injected 5% and 12% errors)
    np.random.seed(42)
    df_tomorrow["load_forecast_kw"] = (df_tomorrow["total_load_kw"] * (1.0 + np.random.normal(0, 0.05, 24))).round(2)
    df_tomorrow["pv_forecast_kw"] = (df_tomorrow["pv_output_kw"] * (1.0 + np.random.normal(0, 0.12, 24))).round(2)
    df_tomorrow.loc[df_tomorrow["pv_forecast_kw"] < 0, "pv_forecast_kw"] = 0.0 # Clamp negative solar

    # 6. Sizing and BESS Parameters
    E_nom = 1000.0       # 1000 kWh nominal energy capacity
    P_max = 500.0        # 500 kW max charge/discharge power
    SoC_min = 0.15       # 15% SoC minimum limit
    SoC_max = 0.95       # 95% SoC maximum limit
    SoC_init = 0.50      # Start tomorrow at 50% SoC
    eta_ch = 0.95        # Inverter charging efficiency
    eta_dis = 0.95       # Inverter discharging efficiency
    C_deg = 0.40         # BESS wear-and-tear degradation penalty (0.40 DKK/kWh)
    P_grid_limit = 500.0 # Max grid import/export limit (kW)

    # 7. Linear Programming Optimization (scipy.optimize.linprog)
    # Variables for each hour t: [P_ch(t), P_dis(t), P_import(t), P_export(t), E(t)]
    # Total variables = 24 hours * 5 = 120 variables
    num_hours = 24
    num_vars = num_hours * 5

    # Objective coefficients: minimize cost
    # sum( price_forecast * P_import + C_deg * P_ch + C_deg * P_dis - price_forecast * P_export )
    c = np.zeros(num_vars)
    for t in range(num_hours):
        price = df_tomorrow.iloc[t]["price_forecast_dkk_kwh"]
        c[t*5 + 0] = C_deg           # P_ch
        c[t*5 + 1] = C_deg           # P_dis
        c[t*5 + 2] = price           # P_import
        c[t*5 + 3] = -price          # P_export
        c[t*5 + 4] = 0.0             # E

    # Bounds for variables
    bounds = []
    for t in range(num_hours):
        bounds.append((0, P_max))            # P_ch
        bounds.append((0, P_max))            # P_dis
        bounds.append((0, P_grid_limit))     # P_import
        bounds.append((0, P_grid_limit))     # P_export
        bounds.append((E_nom * SoC_min, E_nom * SoC_max)) # E (SoC limits: 150 kWh to 950 kWh)

    # Constraints setup
    # 1. Power balance (Inequality for PV curtailment): P_ch - P_dis - P_import + P_export <= PV - load
    A_ub = []
    b_ub = []
    # 2. State transition (Equality): E(t) = E(t-1) + P_ch * eta_ch - P_dis / eta_dis
    A_eq = []
    b_eq = []

    for t in range(num_hours):
        # 1. Power balance inequality (allows PV curtailment when PV > load + charge + export limits)
        eq_pb = np.zeros(num_vars)
        eq_pb[t*5 + 0] = 1.0  # +P_ch
        eq_pb[t*5 + 1] = -1.0 # -P_dis
        eq_pb[t*5 + 2] = -1.0 # -P_import
        eq_pb[t*5 + 3] = 1.0  # +P_export
        A_ub.append(eq_pb)
        
        load_val = df_tomorrow.iloc[t]["load_forecast_kw"]
        pv_val = df_tomorrow.iloc[t]["pv_forecast_kw"]
        b_ub.append(pv_val - load_val)

        # 2. State transition constraint (Equality)
        eq_st = np.zeros(num_vars)
        eq_st[t*5 + 0] = -eta_ch   # -P_ch * eta_ch
        eq_st[t*5 + 1] = 1.0/eta_dis # +P_dis / eta_dis
        eq_st[t*5 + 4] = 1.0       # +E(t)
        if t > 0:
            eq_st[(t-1)*5 + 4] = -1.0 # -E(t-1)
            b_eq.append(0.0)
        else:
            # First hour boundary constraint (E_init)
            b_eq.append(E_nom * SoC_init)
            
        A_eq.append(eq_st)

    # Solve the Linear Program
    print("Optimizing BESS operations schedule...")
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    
    if not res.success:
        print("Optimization failed:", res.message)
        return

    # Extract results
    x = res.x
    df_results = df_tomorrow[["timestamp", "price_forecast_dkk_kwh", "price_P10", "price_P90", "load_forecast_kw", "pv_forecast_kw"]].copy()
    
    p_ch_opt = []
    p_dis_opt = []
    p_import_opt = []
    p_export_opt = []
    e_opt = []
    
    for t in range(num_hours):
        p_ch_opt.append(x[t*5 + 0])
        p_dis_opt.append(x[t*5 + 1])
        p_import_opt.append(x[t*5 + 2])
        p_export_opt.append(x[t*5 + 3])
        e_opt.append(x[t*5 + 4])
        
    df_results["bess_charge_kw"] = np.round(p_ch_opt, 2)
    df_results["bess_discharge_kw"] = np.round(p_dis_opt, 2)
    df_results["grid_import_kw"] = np.round(p_import_opt, 2)
    df_results["grid_export_kw"] = np.round(p_export_opt, 2)
    df_results["bess_energy_kwh"] = np.round(e_opt, 2)
    df_results["bess_soc_percent"] = np.round((df_results["bess_energy_kwh"] / E_nom) * 100, 2)

    # Save to CSV
    df_results.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved optimal schedule table to: {OUTPUT_CSV}")
    
    # 8. Economic and Sizing Calculations (CAPEX, OPEX, LCOS, Payback)
    # Unit Cost DKK/kWh
    usd_per_kwh = 250.0
    usd_to_dkk = 7.46
    capex_per_kwh = usd_per_kwh * usd_to_dkk # 1865 DKK/kWh
    
    total_capex_dkk = E_nom * capex_per_kwh
    annual_opex_dkk = total_capex_dkk * 0.015 # 1.5% of CAPEX
    lifespan_years = 10.0
    annualized_capex_dkk = total_capex_dkk / lifespan_years
    total_annual_cost_dkk = annualized_capex_dkk + annual_opex_dkk

    # Calculate "No-BESS" baseline cost for tomorrow
    df_results["net_load_kw"] = df_results["load_forecast_kw"] - df_results["pv_forecast_kw"]
    
    # No BESS: load is met by imports, excess PV is exported up to grid limit
    no_bess_import = np.where(df_results["net_load_kw"] > 0, df_results["net_load_kw"], 0.0)
    no_bess_export = np.where(df_results["net_load_kw"] < 0, np.minimum(P_grid_limit, np.abs(df_results["net_load_kw"])), 0.0)
    
    no_bess_cost_dkk = (no_bess_import * df_results["price_forecast_dkk_kwh"] - no_bess_export * df_results["price_forecast_dkk_kwh"]).sum()
    
    # Optimized BESS cost for tomorrow (only actual electricity buy/sell cost)
    opt_bess_cost_dkk = (df_results["grid_import_kw"] * df_results["price_forecast_dkk_kwh"] - df_results["grid_export_kw"] * df_results["price_forecast_dkk_kwh"]).sum()
    
    daily_savings_dkk = no_bess_cost_dkk - opt_bess_cost_dkk
    annualized_savings_dkk = daily_savings_dkk * 365.0
    net_annual_benefit_dkk = annualized_savings_dkk - total_annual_cost_dkk
    payback_years = total_capex_dkk / annualized_savings_dkk if annualized_savings_dkk > 0 else float('inf')

    # LCOS Calculation
    cycle_life = 6000.0
    dod = 0.80
    eta_rt = eta_ch * eta_dis
    capital_lcos_dkk = total_capex_dkk / (E_nom * cycle_life * dod * eta_rt)
    
    # Weighted average charging price
    charge_hours = df_results["bess_charge_kw"] > 0
    if charge_hours.any():
        avg_charge_price = np.average(df_results.loc[charge_hours, "price_forecast_dkk_kwh"], 
                                      weights=df_results.loc[charge_hours, "bess_charge_kw"])
    else:
        avg_charge_price = df_results["price_forecast_dkk_kwh"].min()
        
    total_lcos_dkk = capital_lcos_dkk + avg_charge_price

    # Print Sizing & Economic Summary
    print("\n--- Sizing & Economic Analysis (1 MWh System) ---")
    print(f"Sized Battery Capacity:  {E_nom:.1f} kWh ({E_nom/1000.0:.2f} MWh)")
    print(f"BESS CAPEX:             {total_capex_dkk:,.2f} DKK (${total_capex_dkk/usd_to_dkk:,.2f} USD)")
    print(f"Annual OPEX (1.5%):      {annual_opex_dkk:,.2f} DKK/year")
    print(f"Annualized BESS Cost:   {total_annual_cost_dkk:,.2f} DKK/year (Amortized over {lifespan_years} years)")
    print(f"Baseline Cost Tomorrow:  {no_bess_cost_dkk:.2f} DKK (No BESS)")
    print(f"Optimized Cost Tomorrow: {opt_bess_cost_dkk:.2f} DKK (With BESS)")
    print(f"Daily BESS Savings:     {daily_savings_dkk:.2f} DKK/day")
    print(f"Annualized BESS Savings:{annualized_savings_dkk:,.2f} DKK/year")
    print(f"Net Annual Benefit:     {net_annual_benefit_dkk:,.2f} DKK/year")
    print(f"Simple Payback Period:  {payback_years:.2f} years")
    print(f"Levelized Cost of Storage (LCOS): {total_lcos_dkk:.2f} DKK/kWh (Capital portion: {capital_lcos_dkk:.2f} DKK/kWh)")

    # 9. Plot Simulation Chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    hours = df_results["timestamp"].dt.hour
    
    # Plot Prices
    ax1.plot(hours, df_results["price_forecast_dkk_kwh"], label="Price Forecast (Median)", color="blue", lw=2)
    ax1.fill_between(hours, df_results["price_P10"], df_results["price_P90"], color="blue", alpha=0.15, label="Uncertainty Band (P10-P90)")
    ax1.set_ylabel("Price (DKK/kWh)", fontsize=11, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(loc="upper left")
    ax1.set_title("Operational Schedule Forecast & Optimization for Tomorrow (June 8, 2025)", fontsize=12, fontweight="bold")

    # Plot BESS Action & SoC
    ax2.bar(hours, df_results["bess_charge_kw"], label="BESS Charge (kW)", color="green", alpha=0.6)
    ax2.bar(hours, -df_results["bess_discharge_kw"], label="BESS Discharge (kW)", color="red", alpha=0.6)
    ax2_soc = ax2.twinx()
    ax2_soc.plot(hours, df_results["bess_soc_percent"], label="BESS SoC (%)", color="purple", lw=2, linestyle="--")
    
    ax2.set_xlabel("Hour of Day", fontsize=11, fontweight="bold")
    ax2.set_ylabel("BESS Power (kW)", fontsize=11, fontweight="bold")
    ax2_soc.set_ylabel("State of Charge (%)", fontsize=11, fontweight="bold", color="purple")
    ax2_soc.tick_params(axis='y', labelcolor='purple')
    
    # Merge legends for the second plot
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_soc.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    
    ax2.grid(True, linestyle="--", alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=150)
    plt.close()
    print(f"Saved simulation plot to: {OUTPUT_PLOT}")

if __name__ == "__main__":
    main()
