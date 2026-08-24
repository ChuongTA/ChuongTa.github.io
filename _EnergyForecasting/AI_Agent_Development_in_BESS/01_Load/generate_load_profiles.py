import os
import numpy as np
import pandas as pd

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_LOAD_CSV = os.path.join(SCRIPT_DIR, "Community_Load_Profiles.csv")

def main():
    print("Generating synthetic load profiles...")
    
    # 1. Create hourly timeline matching the weather data timeline
    timestamps = pd.date_range(
        start="2024-01-01 00:00:00", 
        end="2025-09-30 23:00:00", 
        freq="h"
    )
    
    # Seed for reproducibility
    np.random.seed(42)
    
    records = []
    
    for dt in timestamps:
        hour = dt.hour
        dayofweek = dt.dayofweek  # 0=Monday, 6=Sunday
        is_weekday = dayofweek < 5
        is_saturday = dayofweek == 5
        
        # --- A. Office Load ---
        office_base = 10.0
        office_diurnal = 80.0 * (
            0.5 * np.exp(-((hour - 10.0) ** 2) / (2.0 * (1.5 ** 2))) +
            0.5 * np.exp(-((hour - 15.0) ** 2) / (2.0 * (1.5 ** 2)))
        )
        office_mult = 1.0 if is_weekday else 0.1
        office_noise = np.random.normal(0.0, 2.0)
        office_load = max(0.0, (office_base + office_diurnal) * office_mult + office_noise)
        
        # --- B. Logistics Load ---
        logistics_base = 20.0
        logistics_mult = 0.15 if dayofweek == 6 else 1.0  # Sunday shutdown
        if 5 <= hour <= 10:
            logistics_diurnal = 120.0 * np.exp(-((hour - 7.5) ** 2) / (2.0 * (1.0 ** 2)))
        elif 16 <= hour <= 21:
            logistics_diurnal = 150.0 * np.exp(-((hour - 18.5) ** 2) / (2.0 * (1.0 ** 2)))
        elif 10 < hour < 16:
            logistics_diurnal = 15.0
        else:
            logistics_diurnal = 0.0
        logistics_noise = np.random.normal(0.0, 4.0)
        logistics_load = max(0.0, (logistics_base + logistics_diurnal) * logistics_mult + logistics_noise)
        
        # --- C. Manufacturing Load ---
        mfg_base = 80.0
        mfg_mult = 1.0 if is_weekday else 0.15
        if 6 <= hour < 22:
            mfg_diurnal = 220.0
        else:
            mfg_diurnal = 120.0
        mfg_noise = np.random.normal(0.0, 6.0)
        mfg_load = max(0.0, (mfg_base + mfg_diurnal) * mfg_mult + mfg_noise)
        
        # --- D. Passenger EV Load ---
        ev_pass_load = 0.0
        if is_weekday and (8 <= hour <= 13):
            ev_pass_diurnal = 200.0 * np.exp(-((hour - 9.5) ** 2) / (2.0 * (1.2 ** 2)))
            ev_pass_noise = np.random.normal(0.0, 1.0)
            ev_pass_load = max(0.0, ev_pass_diurnal + ev_pass_noise)
            
        # --- E. HGV EV Load ---
        ev_hgv_load = 0.0
        if is_weekday and (18 <= hour <= 23):
            ev_hgv_diurnal = 600.0 * np.exp(-((hour - 20.5) ** 2) / (2.0 * (1.0 ** 2)))
            ev_hgv_noise = np.random.normal(0.0, 3.0)
            ev_hgv_load = max(0.0, ev_hgv_diurnal + ev_hgv_noise)
            
        # --- Aggregation ---
        office_load = round(office_load, 2)
        logistics_load = round(logistics_load, 2)
        mfg_load = round(mfg_load, 2)
        ev_pass_load = round(ev_pass_load, 2)
        ev_hgv_load = round(ev_hgv_load, 2)
        
        total_load = round(office_load + logistics_load + mfg_load + ev_pass_load + ev_hgv_load, 2)
        
        records.append({
            "timestamp": dt,
            "office_load_kw": office_load,
            "logistics_load_kw": logistics_load,
            "manufacturing_load_kw": mfg_load,
            "ev_passenger_load_kw": ev_pass_load,
            "ev_hgv_load_kw": ev_hgv_load,
            "total_load_kw": total_load
        })
        
    df = pd.DataFrame(records)
    print(f"Saving load profiles to: {OUTPUT_LOAD_CSV}")
    df.to_csv(OUTPUT_LOAD_CSV, index=False)
    
    # Print metrics
    total_hours = len(df)
    total_mwh = df["total_load_kw"].sum() / 1000.0
    peak_kw = df["total_load_kw"].max()
    avg_kw = df["total_load_kw"].mean()
    
    print("\n--- Load Simulation Summary ---")
    print(f"Total simulated hours: {total_hours}")
    print(f"Total energy consumed: {total_mwh:.2f} MWh")
    print(f"Peak demand spike:     {peak_kw:.2f} kW")
    print(f"Average community load: {avg_kw:.2f} kW")

if __name__ == "__main__":
    main()
