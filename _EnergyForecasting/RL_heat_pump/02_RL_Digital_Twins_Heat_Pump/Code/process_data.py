import os
import glob
import pandas as pd
import xarray as xr

# Base paths
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CODE_DIR, "Data")
TEMP_DIR = os.path.join(DATA_DIR, "01_Temperature_Data")
PRICE_DIR = os.path.join(DATA_DIR, "00_Electricity_price")

print("--- Step 1: Processing NetCDF Temperature Data ---")
nc_files = glob.glob(os.path.join(TEMP_DIR, "*.nc"))
temp_dfs = []

for file_path in nc_files:
    print(f"Reading: {os.path.basename(file_path)}")
    ds = xr.open_dataset(file_path)
    
    # Extract valid_time and t (temperature)
    # The temperature variable 't' typically has dimensions (valid_time, pressure_level, latitude, longitude)
    # We average over latitude and longitude grid points to get a representative Stockholm area temperature
    t_avg = ds['t'].mean(dim=['latitude', 'longitude'])
    
    # If pressure_level exists, select the first level (950 hPa)
    if 'pressure_level' in t_avg.dims:
        t_avg = t_avg.isel(pressure_level=0)
        
    df = t_avg.to_dataframe().reset_index()
    
    # Convert Kelvin to Celsius
    df['temperature'] = df['t'] - 273.15
    
    # Keep only relevant columns
    df = df[['valid_time', 'temperature']].rename(columns={'valid_time': 'datetime'})
    temp_dfs.append(df)

# Combine, drop duplicates, sort by datetime, and save
combined_temp = pd.concat(temp_dfs, ignore_index=True)
combined_temp = combined_temp.drop_duplicates(subset=['datetime']).sort_values('datetime').reset_index(drop=True)
out_temp_path = os.path.join(DATA_DIR, "Stockholm_temperature.csv")
combined_temp.to_csv(out_temp_path, index=False)
print(f"Successfully combined temperature data. Saved to: {out_temp_path}")
print(combined_temp.head())
print(combined_temp.tail())

print("\n--- Step 2: Processing ENTSO-E Electricity Price Data ---")
csv_files = glob.glob(os.path.join(PRICE_DIR, "GUI_ENERGY_PRICES_*.csv"))
price_dfs = []

for file_path in csv_files:
    print(f"Reading: {os.path.basename(file_path)}")
    df = pd.read_csv(file_path)
    
    # We need to parse the time interval 'MTU (CET/CEST)'
    # Example formats: "01/01/2024 00:00:00 - 01/01/2024 01:00:00" or with (CET)
    # We will extract the start time of each interval as the datetime index
    df['datetime_str'] = df['MTU (CET/CEST)'].apply(lambda x: x.split(" - ")[0].strip())
    # Strip any timezone details like (CET) or (CEST)
    df['datetime_str'] = df['datetime_str'].str.replace(r'\s*\([^)]*\)', '', regex=True).str.strip()
    df['datetime'] = pd.to_datetime(df['datetime_str'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    
    # Clean price column and convert to numeric
    df['price'] = pd.to_numeric(df['Day-ahead Price (EUR/MWh)'], errors='coerce')
    
    # Keep only relevant columns
    df = df[['datetime', 'price']]
    price_dfs.append(df)

# Combine, drop duplicates, sort by datetime, and save
combined_price = pd.concat(price_dfs, ignore_index=True)
combined_price = combined_price.drop_duplicates(subset=['datetime']).sort_values('datetime').reset_index(drop=True)
out_price_path = os.path.join(DATA_DIR, "SE3_electricity_sport_price_ENTSO_E.csv")
combined_price.to_csv(out_price_path, index=False)
print(f"Successfully combined price data. Saved to: {out_price_path}")
print(combined_price.head())
print(combined_price.tail())
