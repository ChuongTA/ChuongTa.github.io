import os
import numpy as np
import pandas as pd
import pyomo.environ as pyo
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

# Output file paths
OUTPUT_PLOT_1D = os.path.join(SCRIPT_DIR, "daily_schedule_single_day.png")
OUTPUT_PLOT_7D = os.path.join(SCRIPT_DIR, "daily_schedule_7_days.png")
OUTPUT_HTML = os.path.join(SCRIPT_DIR, "daily_schedule_interactive.html")
OUTPUT_SUMMARY = os.path.join(SCRIPT_DIR, "optimization_summary.txt")

# GLPK Solver path (downloaded winglpk package)
GLPK_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "../00_Required_Package/winglpk-4.65/glpk-4.65/w64/glpsol.exe"))

# Constants
EUR_TO_DKK = 7.46
MWH_TO_KWH = 1000.0

def generate_interactive_html(df_results, out_path):
    """Write a standalone HTML file that loads Plotly.js from a CDN and renders
    an interactive, zoomable chart of BESS operations with P10/P90 price quantiles."""
    
    time_list = df_results["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
    soc_list = df_results["bess_soc_percent"].tolist()
    charge_list = df_results["bess_charge_kw"].tolist()
    discharge_list = df_results["bess_discharge_kw"].tolist()
    price_list = df_results["price_forecast_dkk_kwh"].tolist()
    p10_list = df_results["price_P10"].tolist()
    p90_list = df_results["price_P90"].tolist()
    load_list = df_results["load_forecast_kw"].tolist()
    pv_list = df_results["pv_forecast_kw"].tolist()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>BESS Operations Interactive Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
            h1 {{ text-align: center; color: #2c3e50; }}
            #chart1, #chart2 {{ width: 100%; height: 400px; margin-bottom: 20px; }}
            .container {{ max-width: 1200px; margin: auto; background: white; padding: 20px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>BESS Operational Scheduling & Forecast Dashboard</h1>
            <div id="chart1"></div>
            <div id="chart2"></div>
        </div>

        <script>
            const timestamps = {repr(time_list)};
            const prices = {repr(price_list)};
            const p10 = {repr(p10_list)};
            const p90 = {repr(p90_list)};
            const soc = {repr(soc_list)};
            const charge = {repr(charge_list)};
            const discharge = {repr(discharge_list)};
            const net_discharge = discharge.map((d, i) => d - charge[i]);
            const load = {repr(load_list)};
            const pv = {repr(pv_list)};

            // Chart 1: Spot Price (Median + P10/P90 Uncertainty Band) & Solar / Load Profiles
            const traceP10 = {{
                x: timestamps,
                y: p10,
                type: 'scatter',
                mode: 'lines',
                line: {{ width: 0 }},
                showlegend: false
            }};

            const traceP90 = {{
                x: timestamps,
                y: p90,
                fill: 'tonexty',
                fillcolor: 'rgba(0, 0, 255, 0.1)',
                type: 'scatter',
                mode: 'lines',
                line: {{ width: 0 }},
                name: 'Price Uncertainty Band (P10-P90)'
            }};

            const tracePrice = {{
                x: timestamps,
                y: prices,
                name: 'Price Forecast (Median)',
                type: 'scatter',
                line: {{ color: 'blue', width: 2.5 }}
            }};

            const traceLoad = {{
                x: timestamps,
                y: load,
                name: 'Load Forecast (kW)',
                type: 'scatter',
                yaxis: 'y2',
                line: {{ color: 'black', width: 1.5, dash: 'dash' }}
            }};

            const tracePV = {{
                x: timestamps,
                y: pv,
                name: 'PV Forecast (kW)',
                type: 'scatter',
                yaxis: 'y2',
                line: {{ color: 'orange', width: 1.5 }}
            }};

            const layout1 = {{
                title: 'Market Prices (with Quantile Bands) and Demand/Solar Profiles',
                xaxis: {{ title: 'Timestamp', rangeslider: {{}} }},
                yaxis: {{ title: 'Price (DKK/kWh)', titlefont: {{color: 'blue'}}, tickfont: {{color: 'blue'}} }},
                yaxis2: {{
                    title: 'Power (kW)',
                    titlefont: {{color: 'black'}},
                    tickfont: {{color: 'black'}},
                    overlaying: 'y',
                    side: 'right'
                }}
            }};

            Plotly.newPlot('chart1', [traceP10, traceP90, tracePrice, traceLoad, tracePV], layout1);

            // Chart 2: BESS Actions and State of Charge
            const traceBESS = {{
                x: timestamps,
                y: net_discharge,
                name: 'BESS Power (kW, + Disch / - Charge)',
                type: 'bar',
                marker: {{ color: net_discharge.map(v => v >= 0 ? 'red' : 'green') }}
            }};

            const traceSoC = {{
                x: timestamps,
                y: soc,
                name: 'BESS SoC (%)',
                type: 'scatter',
                yaxis: 'y2',
                line: {{ color: 'purple', width: 2, shape: 'hv', dash: 'dot' }}
            }};

            const layout2 = {{
                title: 'BESS Operations Setpoints & State of Charge (SoC)',
                xaxis: {{ title: 'Timestamp' }},
                yaxis: {{ title: 'BESS Power (kW) [Positive is Discharge, Negative is Charge]' }},
                yaxis2: {{
                    title: 'State of Charge (%)',
                    titlefont: {{color: 'purple'}},
                    tickfont: {{color: 'purple'}},
                    overlaying: 'y',
                    side: 'right',
                    range: [0, 100]
                }}
            }};

            Plotly.newPlot('chart2', [traceBESS, traceSoC], layout2);
        </script>
    </body>
    </html>
    """
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated zoomable interactive HTML plot with price quantiles: {out_path}")

def run_daily_optimization_pyomo(start_date_str="2025-06-07", end_date_str="2025-06-13"):
    print(f"--- Running Daily Optimization from {start_date_str} to {end_date_str} (Pyomo + GLPK) ---")
    
    # Load data
    df_price = pd.read_csv(PRICE_CSV, sep=";", decimal=",", parse_dates=["HourUTC"])
    df_load = pd.read_csv(LOAD_CSV, parse_dates=["timestamp"])
    df_pv = pd.read_csv(PV_CSV, parse_dates=["timestamp"])
    
    df_price = df_price.rename(columns={"HourUTC": "timestamp", "DK1_EUR/MWh": "price_eur_mwh"})
    df_price["price_dkk_kwh"] = (df_price["price_eur_mwh"] * EUR_TO_DKK) / MWH_TO_KWH
    
    df_all = pd.merge(df_price[["timestamp", "price_dkk_kwh"]], df_load, on="timestamp", how="inner")
    df_all = pd.merge(df_all, df_pv[["timestamp", "pv_output_kw"]], on="timestamp", how="inner")
    df_all = df_all.sort_values("timestamp").reset_index(drop=True)
    
    # Train Price Model (LightGBM) on all data prior to the start of scheduling
    train_end = pd.Timestamp(start_date_str) - pd.Timedelta(days=1)
    
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
    
    model = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.05, num_leaves=31, random_state=42, verbose=-1)
    model.fit(X_train, y_train)
    
    # Filter schedule period
    schedule_mask = (df_all["timestamp"] >= start_date_str) & (df_all["timestamp"] <= end_date_str + " 23:00:00")
    df_sched = df_all[schedule_mask].copy().reset_index(drop=True)
    num_hours = len(df_sched)
    
    if num_hours == 0:
        print("Error: No data in specified scheduling date range.")
        return
        
    print(f"Scheduling horizon: {num_hours} hours total.")
    
    # Predict Price & Apply Binned Residual Bootstrapping
    df_sched["price_forecast_dkk_kwh"] = model.predict(df_sched[features])
    
    train_preds = model.predict(X_train)
    residuals = y_train - train_preds
    
    bin_edges = np.percentile(train_preds, np.linspace(0, 100, 6))
    bin_edges[0], bin_edges[-1] = -np.inf, np.inf
    train_bin_idx = np.digitize(train_preds, bin_edges[1:-1])
    
    p10_offsets = []
    p90_offsets = []
    for h_pred in df_sched["price_forecast_dkk_kwh"]:
        b = np.digitize([h_pred], bin_edges[1:-1])[0]
        bin_res = residuals[train_bin_idx == b]
        p10_offsets.append(np.percentile(bin_res, 10))
        p90_offsets.append(np.percentile(bin_res, 90))
        
    df_sched["price_P10"] = (df_sched["price_forecast_dkk_kwh"] + p10_offsets).round(2)
    df_sched["price_P90"] = (df_sched["price_forecast_dkk_kwh"] + p90_offsets).round(2)
    df_sched["price_forecast_dkk_kwh"] = df_sched["price_forecast_dkk_kwh"].round(2)
    
    np.random.seed(42)
    df_sched["load_forecast_kw"] = (df_sched["total_load_kw"] * (1.0 + np.random.normal(0, 0.05, num_hours))).round(2)
    df_sched["pv_forecast_kw"] = (df_sched["pv_output_kw"] * (1.0 + np.random.normal(0, 0.12, num_hours))).round(2)
    df_sched.loc[df_sched["pv_forecast_kw"] < 0, "pv_forecast_kw"] = 0.0
    
    # BESS Parameters (Using the 1500 kWh feasible sizing)
    E_nom = 1500.0
    P_max = 750.0
    SoC_min = 0.15
    SoC_max = 0.95
    SoC_init = 0.50
    eta_ch = 0.95
    eta_dis = 0.95
    C_deg = 0.40
    P_grid_limit = 500.0
    
    # Initialize Pyomo Concrete Model
    pyo_model = pyo.ConcreteModel()
    pyo_model.T = pyo.RangeSet(1, num_hours)
    
    # Variables
    pyo_model.P_ch = pyo.Var(pyo_model.T, domain=pyo.NonNegativeReals, bounds=(0, P_max))
    pyo_model.P_dis = pyo.Var(pyo_model.T, domain=pyo.NonNegativeReals, bounds=(0, P_max))
    pyo_model.P_import = pyo.Var(pyo_model.T, domain=pyo.NonNegativeReals, bounds=(0, P_grid_limit))
    pyo_model.P_export = pyo.Var(pyo_model.T, domain=pyo.NonNegativeReals, bounds=(0, P_grid_limit))
    pyo_model.E = pyo.Var(pyo_model.T, domain=pyo.NonNegativeReals, bounds=(E_nom * SoC_min, E_nom * SoC_max))

    # Objective: Minimize net electricity import bill + BESS wear-and-tear degradation costs
    def obj_rule(m):
        return sum(
            df_sched.iloc[t-1]["price_forecast_dkk_kwh"] * m.P_import[t] +
            C_deg * (m.P_ch[t] + m.P_dis[t]) -
            df_sched.iloc[t-1]["price_forecast_dkk_kwh"] * m.P_export[t]
            for t in m.T
        )
    pyo_model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

    # Constraints
    # 1. Power balance with PV curtailment: P_ch - P_dis - P_import + P_export <= PV - load
    def power_balance_rule(m, t):
        load_val = df_sched.iloc[t-1]["load_forecast_kw"]
        pv_val = df_sched.iloc[t-1]["pv_forecast_kw"]
        return m.P_ch[t] - m.P_dis[t] - m.P_import[t] + m.P_export[t] <= pv_val - load_val
    pyo_model.power_balance = pyo.Constraint(pyo_model.T, rule=power_balance_rule)

    # 2. BESS Energy State Transition
    def soc_dynamics_rule(m, t):
        if t == 1:
            return m.E[t] == (E_nom * SoC_init) + (m.P_ch[t] * eta_ch - m.P_dis[t] / eta_dis)
        return m.E[t] == m.E[t-1] + (m.P_ch[t] * eta_ch - m.P_dis[t] / eta_dis)
    pyo_model.soc_dynamics = pyo.Constraint(pyo_model.T, rule=soc_dynamics_rule)

    # Solve using GLPK solver pointing to local winglpk executable
    print("Solving Pyomo model using local GLPK solver...")
    solver = pyo.SolverFactory('glpk', executable=GLPK_PATH)
    res = solver.solve(pyo_model)
    
    if not ((res.solver.status == pyo.SolverStatus.ok) and (res.solver.termination_condition == pyo.TerminationCondition.optimal)):
        print("Optimization failed.")
        return
        
    df_sched["bess_charge_kw"] = np.round([pyo_model.P_ch[t].value for t in pyo_model.T], 2)
    df_sched["bess_discharge_kw"] = np.round([pyo_model.P_dis[t].value for t in pyo_model.T], 2)
    df_sched["grid_import_kw"] = np.round([pyo_model.P_import[t].value for t in pyo_model.T], 2)
    df_sched["grid_export_kw"] = np.round([pyo_model.P_export[t].value for t in pyo_model.T], 2)
    df_sched["bess_energy_kwh"] = np.round([pyo_model.E[t].value for t in pyo_model.T], 2)
    df_sched["bess_soc_percent"] = np.round((df_sched["bess_energy_kwh"] / E_nom) * 100, 2)
    
    # Save Interactive HTML Dashboard
    generate_interactive_html(df_sched, OUTPUT_HTML)
    
    # Save Metrics Summary Report
    net_load = df_sched["load_forecast_kw"] - df_sched["pv_forecast_kw"]
    no_bess_import = np.where(net_load > 0, net_load, 0.0)
    no_bess_export = np.where(net_load < 0, np.minimum(P_grid_limit, np.abs(net_load)), 0.0)
    no_bess_cost = np.sum(no_bess_import * df_sched["price_forecast_dkk_kwh"] - no_bess_export * df_sched["price_forecast_dkk_kwh"])
    opt_bess_cost = np.sum(df_sched["grid_import_kw"] * df_sched["price_forecast_dkk_kwh"] - df_sched["grid_export_kw"] * df_sched["price_forecast_dkk_kwh"])
    total_savings = no_bess_cost - opt_bess_cost

    with open(OUTPUT_SUMMARY, "w") as f:
        f.write("=========================================================\n")
        f.write("    BESS DAILY SCHEDULE OPTIMIZATION SUMMARY (PYOMO)\n")
        f.write("=========================================================\n\n")
        f.write(f"Scheduling Period: {start_date_str} to {end_date_str}\n")
        f.write(f"Baseline Grid Cost (No BESS): {no_bess_cost:,.2f} DKK\n")
        f.write(f"Optimized Grid Cost (With BESS): {opt_bess_cost:,.2f} DKK\n")
        f.write(f"Total Period Savings: {total_savings:,.2f} DKK\n")
        f.write(f"Grid Import Peak: {df_sched['grid_import_kw'].max():.2f} kW\n")
        f.write(f"Grid Export Peak: {df_sched['grid_export_kw'].max():.2f} kW\n")
        f.write(f"Total Battery Charging: {df_sched['bess_charge_kw'].sum():,.2f} kWh\n")
        f.write(f"Total Battery Discharging: {df_sched['bess_discharge_kw'].sum():,.2f} kWh\n")

    print(f"Saved text summary to: {OUTPUT_SUMMARY}")
    
    # 9. Plot PNG Charts
    # Plot 1: Single Day (first 24 hours)
    df_1d = df_sched.iloc[:24]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax1.plot(df_1d["timestamp"].dt.hour, df_1d["price_forecast_dkk_kwh"], color="blue", lw=2, label="Price Forecast (Median)")
    ax1.fill_between(df_1d["timestamp"].dt.hour, df_1d["price_P10"], df_1d["price_P90"], color="blue", alpha=0.15, label="Uncertainty Band")
    ax1.set_ylabel("Price (DKK/kWh)", fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(loc="upper left")
    ax1.set_title(f"Operational Schedule: Single Day ({start_date_str}) (Pyomo + GLPK)", fontsize=12, fontweight="bold")
    
    ax2.bar(df_1d["timestamp"].dt.hour, df_1d["bess_charge_kw"], color="green", alpha=0.6, label="Charge")
    ax2.bar(df_1d["timestamp"].dt.hour, -df_1d["bess_discharge_kw"], color="red", alpha=0.6, label="Discharge")
    ax2_soc = ax2.twinx()
    ax2_soc.plot(df_1d["timestamp"].dt.hour, df_1d["bess_soc_percent"], color="purple", lw=2, label="SoC (%)", linestyle="--")
    ax2.set_xlabel("Hour of Day", fontweight="bold")
    ax2.set_ylabel("Power (kW)", fontweight="bold")
    ax2_soc.set_ylabel("SoC (%)", color="purple", fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT_1D, dpi=150)
    plt.close()
    print(f"Saved 1-day PNG plot to: {OUTPUT_PLOT_1D}")

    # Plot 2: 7 Days (or entire period if smaller)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    ax1.plot(df_sched["timestamp"], df_sched["price_forecast_dkk_kwh"], color="blue", lw=1.5, label="Price Forecast (Median)")
    ax1.fill_between(df_sched["timestamp"], df_sched["price_P10"], df_sched["price_P90"], color="blue", alpha=0.1, label="Uncertainty Band")
    ax1.set_ylabel("Price (DKK/kWh)", fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(loc="upper left")
    ax1.set_title(f"Operational Schedule: 7-Day Rolling Horizon (Pyomo + GLPK)", fontsize=12, fontweight="bold")
    
    ax2.fill_between(df_sched["timestamp"], df_sched["bess_charge_kw"], color="green", alpha=0.4, label="Charge")
    ax2.fill_between(df_sched["timestamp"], -df_sched["bess_discharge_kw"], color="red", alpha=0.4, label="Discharge")
    ax2_soc = ax2.twinx()
    ax2_soc.plot(df_sched["timestamp"], df_sched["bess_soc_percent"], color="purple", lw=1.5, label="SoC (%)", linestyle="--")
    ax2.set_ylabel("Power (kW)", fontweight="bold")
    ax2_soc.set_ylabel("SoC (%)", color="purple", fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.3)
    
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT_7D, dpi=150)
    plt.close()
    print(f"Saved 7-day PNG plot to: {OUTPUT_PLOT_7D}")

if __name__ == "__main__":
    run_daily_optimization_pyomo()
