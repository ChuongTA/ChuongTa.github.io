import os
import pandas as pd

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Raw weather data path
WEATHER_DATA_CSV = os.path.normpath(os.path.join(
    SCRIPT_DIR,
    "WeatherData_Acquisition/ERA5_DK1_Merged.csv"
))
# Output PV generation path
OUTPUT_PV_CSV = os.path.join(SCRIPT_DIR, "ERA5_PV_Generation_50MW.csv")

def main():
    print(f"Loading weather data from: {WEATHER_DATA_CSV}")
    if not os.path.exists(WEATHER_DATA_CSV):
        print(f"Error: Weather data file not found at {WEATHER_DATA_CSV}")
        return

    # Ingest historical ERA5 weather data
    df_raw = pd.read_csv(WEATHER_DATA_CSV)
    
    # 1. Spatial Aggregation: Average grid point values for each timestamp
    print("Aggregating grid-level data (averaging across coordinates)...")
    df_hourly = df_raw.groupby("valid_time").agg({
        "ssrd": "mean",      # Solar radiation downwards (J/m^2)
        "t": "mean",         # Air temperature (K)
        "cc": "mean"         # Cloud cover fraction (0-1)
    }).reset_index()

    # Sort chronologically
    df_hourly["valid_time"] = pd.to_datetime(df_hourly["valid_time"])
    df_hourly = df_hourly.sort_values("valid_time").reset_index(drop=True)

    # 2. PV Plant Parameters (50 MWp plant)
    capacity_kw = 50000.0                # 50 MW in kW
    area_per_kw = 5.0                    # 5 m^2 panel area per kWp
    total_area = capacity_kw * area_per_kw  # 250,000 m^2
    eta_pv = 0.20                        # PV module efficiency (20%)
    eta_system = 0.90                    # System losses (10% losses, 90% efficiency)
    eta_temp = 0.95                      # Temperature losses factor (95% efficiency)

    # Combined constant scaling factor (kW output per 1 W/m^2 of irradiance)
    scaling_factor = (total_area * eta_pv * eta_system * eta_temp) / 1000.0  # 42.75

    # 3. Apply physical calculations
    print("Applying solar conversion and scaling logic...")
    
    # Convert accumulated J/m^2 to average irradiance (W/m^2)
    # 1 W/m^2 = 1 J/m^2/3600 seconds
    df_hourly["irradiance_w_m2"] = (df_hourly["ssrd"] / 3600.0).round(2)
    
    # Calculate electrical output in kW and MW
    df_hourly["pv_output_kw"] = (df_hourly["irradiance_w_m2"] * scaling_factor).round(2)
    df_hourly["pv_output_mw"] = (df_hourly["pv_output_kw"] / 1000.0).round(4)
    
    # Format columns for output
    df_output = df_hourly[[
        "valid_time", 
        "ssrd", 
        "irradiance_w_m2", 
        "pv_output_kw", 
        "pv_output_mw"
    ]].rename(columns={
        "valid_time": "timestamp",
        "ssrd": "ssrd_j_m2"
    })

    # 4. Save to CSV
    print(f"Saving scaled 50 MW PV generation profile to: {OUTPUT_PV_CSV}")
    df_output.to_csv(OUTPUT_PV_CSV, index=False)
    
    # 5. Display statistics
    total_hours = len(df_output)
    total_generation_mwh = df_output["pv_output_kw"].sum() / 1000.0
    peak_generation_mw = df_output["pv_output_mw"].max()
    capacity_factor = (total_generation_mwh / (50.0 * total_hours)) * 100.0
    
    print("\n--- Simulation Summary ---")
    print(f"Total simulated hours: {total_hours} (covering {df_output['timestamp'].min()} to {df_output['timestamp'].max()})")
    print(f"Total energy generated: {total_generation_mwh:.2f} MWh")
    print(f"Peak generation power:   {peak_generation_mw:.2f} MW")
    print(f"Average capacity factor: {capacity_factor:.2f}%")

if __name__ == "__main__":
    main()
