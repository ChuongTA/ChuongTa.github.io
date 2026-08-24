import os
import numpy as np
import pandas as pd
import pyomo.environ as pyo
import warnings
warnings.filterwarnings("ignore")

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRICE_CSV = os.path.normpath(os.path.join(SCRIPT_DIR, "../04_Electricity_Price/Data.csv"))
LOAD_CSV = os.path.normpath(os.path.join(SCRIPT_DIR, "../01_Load/Community_Load_Profiles.csv"))
PV_CSV = os.path.normpath(os.path.join(SCRIPT_DIR, "../02_PV_Generation/ERA5_PV_Generation_50MW.csv"))
OUTPUT_REPORT = os.path.join(SCRIPT_DIR, "sizing_results.txt")

# GLPK Solver path (downloaded winglpk package)
GLPK_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "../00_Required_Package/winglpk-4.65/glpk-4.65/w64/glpsol.exe"))

# Constants
EUR_TO_DKK = 7.46
MWH_TO_KWH = 1000.0

def optimize_bess_size_pyomo(df_slice, E_nom, P_max, P_grid_limit=500.0):
    """Simulate BESS scheduling using Pyomo and GLPK for a specific battery size."""
    num_hours = len(df_slice)
    
    # BESS parameters
    eta_ch = 0.95
    eta_dis = 0.95
    C_deg = 0.40 # DKK/kWh
    SoC_min = 0.15
    SoC_max = 0.95
    SoC_init = 0.50
    
    # Initialize Pyomo Concrete Model
    model = pyo.ConcreteModel()
    model.T = pyo.RangeSet(1, num_hours)
    
    # Variables
    model.P_ch = pyo.Var(model.T, domain=pyo.NonNegativeReals, bounds=(0, P_max))
    model.P_dis = pyo.Var(model.T, domain=pyo.NonNegativeReals, bounds=(0, P_max))
    model.P_import = pyo.Var(model.T, domain=pyo.NonNegativeReals, bounds=(0, P_grid_limit))
    model.P_export = pyo.Var(model.T, domain=pyo.NonNegativeReals, bounds=(0, P_grid_limit))
    model.E = pyo.Var(model.T, domain=pyo.NonNegativeReals, bounds=(E_nom * SoC_min, E_nom * SoC_max))

    # Objective: Minimize net electricity import bill + battery degradation costs
    def obj_rule(m):
        return sum(
            df_slice.iloc[t-1]["price_dkk_kwh"] * m.P_import[t] +
            C_deg * (m.P_ch[t] + m.P_dis[t]) -
            df_slice.iloc[t-1]["price_dkk_kwh"] * m.P_export[t]
            for t in m.T
        )
    model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

    # Constraints
    # 1. Power balance with PV curtailment: P_ch - P_dis - P_import + P_export <= PV - load
    def power_balance_rule(m, t):
        load_val = df_slice.iloc[t-1]["total_load_kw"]
        pv_val = df_slice.iloc[t-1]["pv_output_kw"]
        return m.P_ch[t] - m.P_dis[t] - m.P_import[t] + m.P_export[t] <= pv_val - load_val
    model.power_balance = pyo.Constraint(model.T, rule=power_balance_rule)

    # 2. BESS Energy State Transition
    def soc_dynamics_rule(m, t):
        if t == 1:
            return m.E[t] == (E_nom * SoC_init) + (m.P_ch[t] * eta_ch - m.P_dis[t] / eta_dis)
        return m.E[t] == m.E[t-1] + (m.P_ch[t] * eta_ch - m.P_dis[t] / eta_dis)
    model.soc_dynamics = pyo.Constraint(model.T, rule=soc_dynamics_rule)

    # Solve using Pyomo's GLPK interface pointing to the local winglpk executable
    solver = pyo.SolverFactory('glpk', executable=GLPK_PATH)
    results = solver.solve(model)
    
    if (results.solver.status == pyo.SolverStatus.ok) and (results.solver.termination_condition == pyo.TerminationCondition.optimal):
        # Extract variables
        p_import_opt = np.array([model.P_import[t].value for t in model.T])
        p_export_opt = np.array([model.P_export[t].value for t in model.T])
        
        # Calculate actual net grid cost (excluding degradation costs)
        electricity_cost = sum(
            (p_import_opt[t] - p_export_opt[t]) * df_slice.iloc[t]["price_dkk_kwh"]
            for t in range(num_hours)
        )
        return electricity_cost
    else:
        return None

def main():
    print("--- Running BESS Capacity Sizing Optimization (Pyomo + GLPK) ---")
    
    # Load and merge historical data
    df_price = pd.read_csv(PRICE_CSV, sep=";", decimal=",", parse_dates=["HourUTC"])
    df_load = pd.read_csv(LOAD_CSV, parse_dates=["timestamp"])
    df_pv = pd.read_csv(PV_CSV, parse_dates=["timestamp"])
    
    df_price = df_price.rename(columns={"HourUTC": "timestamp", "DK1_EUR/MWh": "price_eur_mwh"})
    df_price["price_dkk_kwh"] = (df_price["price_eur_mwh"] * EUR_TO_DKK) / MWH_TO_KWH
    
    df_all = pd.merge(df_price[["timestamp", "price_dkk_kwh"]], df_load, on="timestamp", how="inner")
    df_all = pd.merge(df_all, df_pv[["timestamp", "pv_output_kw"]], on="timestamp", how="inner")
    
    sizing_mask = (df_all["timestamp"] >= "2024-01-01") & (df_all["timestamp"] <= "2025-06-06 23:00:00")
    df_slice = df_all[sizing_mask].sort_values("timestamp").reset_index(drop=True)
    num_hours = len(df_slice)
    
    if num_hours == 0:
        print("Error: No data available for the selected sizing period.")
        return
        
    print(f"Sizing evaluation period: {df_slice['timestamp'].min()} to {df_slice['timestamp'].max()} ({num_hours} hours)")

    # Baseline cost without BESS
    net_load = df_slice["total_load_kw"] - df_slice["pv_output_kw"]
    no_bess_import = np.where(net_load > 0, net_load, 0.0)
    no_bess_export = np.where(net_load < 0, np.minimum(500.0, np.abs(net_load)), 0.0)
    no_bess_cost = np.sum(no_bess_import * df_slice["price_dkk_kwh"] - no_bess_export * df_slice["price_dkk_kwh"])

    # Test BESS Capacities (in kWh)
    capacities = [250.0, 500.0, 1000.0, 1500.0, 2000.0]
    results = []

    # Financial Assumptions
    usd_per_kwh = 250.0
    usd_to_dkk = 7.46
    capex_per_kwh = usd_per_kwh * usd_to_dkk
    lifespan_years = 10.0
    annual_opex_rate = 0.015

    for E_nom in capacities:
        # Match power capacity (0.5C rate, e.g. 500kW BESS for 1000kWh capacity)
        P_max = E_nom * 0.5
        
        print(f"Solving Pyomo model via GLPK for capacity = {E_nom} kWh...")
        cost_with_bess = optimize_bess_size_pyomo(df_slice, E_nom, P_max)
        
        if cost_with_bess is None:
            print(f"Capacity {E_nom} kWh is Infeasible.")
            continue
            
        period_savings = no_bess_cost - cost_with_bess
        annualized_savings = period_savings * (8760.0 / num_hours)
        
        total_capex = E_nom * capex_per_kwh
        annual_opex = total_capex * annual_opex_rate
        annual_amortized = total_capex / lifespan_years
        annual_bess_cost = annual_amortized + annual_opex
        
        net_annual_benefit = annualized_savings - annual_bess_cost
        payback_years = total_capex / annualized_savings if annualized_savings > 0 else float('inf')
        
        results.append({
            "Capacity (kWh)": E_nom,
            "Power (kW)": P_max,
            "CAPEX (DKK)": total_capex,
            "Annual OPEX (DKK)": annual_opex,
            "Annual Cost (DKK)": annual_bess_cost,
            "Annual Savings (DKK)": annualized_savings,
            "Net Benefit (DKK)": net_annual_benefit,
            "Payback (Years)": payback_years
        })

    df_results = pd.DataFrame(results)
    
    # Save text report
    with open(OUTPUT_REPORT, "w") as f:
        f.write("=========================================================\n")
        f.write("      BESS SIZING AND ECONOMIC FEASIBILITY REPORT (PYOMO)\n")
        f.write("=========================================================\n\n")
        f.write(f"Evaluation Period: {df_slice['timestamp'].min()} to {df_slice['timestamp'].max()}\n")
        f.write(f"Baseline No-BESS Grid Cost: {no_bess_cost:,.2f} DKK\n\n")
        f.write(df_results.to_string(index=False))
        f.write("\n\nSizing Recommendation:\n")
        
        if len(df_results) > 0:
            best_row = df_results.loc[df_results["Net Benefit (DKK)"].idxmax()]
            f.write(f"Recommended Capacity: {best_row['Capacity (kWh)']:.1f} kWh ({best_row['Power (kW)']:.1f} kW inverter)\n")
            f.write(f"Expected Payback Period: {best_row['Payback (Years)']:.2f} years\n")
            f.write(f"Net Annual Benefit: {best_row['Net Benefit (DKK)']:,.2f} DKK/year\n")
        else:
            f.write("No feasible sizing configurations found.\n")

    print(f"Saved BESS sizing report to: {OUTPUT_REPORT}")
    print(df_results)

if __name__ == "__main__":
    main()
