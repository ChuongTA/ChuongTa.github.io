"""
Download ERA5 hourly reanalysis data month-by-month from January 2024 through
September 2025, for the DK1 bounding box (Option 2). Pulls two datasets per
month: pressure-level variables (temperature, wind, humidity, cloud cover at
950 hPa) and single-level variables (solar radiation, snow). Each month/
dataset pair is saved as its own NetCDF file.
"""

import os
import calendar
import zipfile
import tempfile
# pyrefly: ignore [missing-import]
import cdsapi
import xarray as xr
import pandas as pd


CDS_URL = "https://cds.climate.copernicus.eu/api"
CDS_KEY = "YOUR API KEY"


PRESSURE_DATASET = "reanalysis-era5-pressure-levels"

PRESSURE_VARIABLES = [
    "temperature",
    "u_component_of_wind",
    "v_component_of_wind",
    "relative_humidity",
    "fraction_of_cloud_cover",
]

PRESSURE_LEVELS = ["950"]

SINGLE_LEVEL_DATASET = "reanalysis-era5-single-levels"

SINGLE_LEVEL_VARIABLES = [
    "surface_solar_radiation_downwards",
    "surface_solar_radiation_downward_clear_sky",
    "snow_depth",
    "snowfall",
]

# DK1 bounding box: North, West, South, East
AREA = [57.5, 7.0, 54.5, 11.5]

TIMES = [f"{h:02d}:00" for h in range(24)]

START_YEAR, START_MONTH = 2024, 1
END_YEAR, END_MONTH = 2025, 9

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "raw_netcdf")

os.makedirs(RAW_DIR, exist_ok=True)


def month_range(start_year, start_month, end_year, end_month):
    """Yield (year, month) tuples from start to end, inclusive."""
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        yield year, month
        month += 1
        if month > 12:
            month = 1
            year += 1


def clip_days(year, month):
    """Clip the day range to the 2025-09-30 end date for the final month."""
    days_in_month = calendar.monthrange(year, month)[1]
    if (year, month) == (END_YEAR, END_MONTH):
        days_in_month = min(days_in_month, 30)
    return [f"{d:02d}" for d in range(1, days_in_month + 1)]


def download_pressure_month(client, year, month):
    """Download one month of ERA5 pressure-level data as NetCDF, skipping if
    already present."""
    nc_path = os.path.join(RAW_DIR, f"ERA5_Atmospheric_{year}_{month:02d}.nc")
    if os.path.exists(nc_path):
        print(f"[skip] {nc_path} already exists")
        return nc_path

    days = clip_days(year, month)

    request = {
        "product_type": ["reanalysis"],
        "variable": PRESSURE_VARIABLES,
        "pressure_level": PRESSURE_LEVELS,
        "year": [str(year)],
        "month": [f"{month:02d}"],
        "day": days,
        "time": TIMES,
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": AREA,
    }

    print(f"[download] {year}-{month:02d} -> {nc_path}")
    client.retrieve(PRESSURE_DATASET, request).download(nc_path)
    return nc_path


def download_single_level_month(client, year, month):
    """Download one month of ERA5 single-level data as NetCDF, skipping if
    already present."""
    nc_path = os.path.join(RAW_DIR, f"ERA5_SingleLevel_{year}_{month:02d}.nc")
    if os.path.exists(nc_path):
        print(f"[skip] {nc_path} already exists")
        return nc_path

    days = clip_days(year, month)

    request = {
        "product_type": ["reanalysis"],
        "variable": SINGLE_LEVEL_VARIABLES,
        "year": [str(year)],
        "month": [f"{month:02d}"],
        "day": days,
        "time": TIMES,
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": AREA,
    }

    print(f"[download] {year}-{month:02d} -> {nc_path}")
    client.retrieve(SINGLE_LEVEL_DATASET, request).download(nc_path)
    return nc_path


def _extract_if_zip(nc_path):
    """CDS sometimes bundles a month's multi-variable request into a zip of
    several NetCDF files -- one per data stream (oper/instant, oper/accum,
    wave/instant) -- even with download_format='unarchived'. Detect that via
    the ZIP magic number and extract the members; otherwise the file is
    already a plain NetCDF and is returned as-is."""
    with open(nc_path, "rb") as f:
        magic = f.read(4)
    if magic != b"PK\x03\x04":
        return [nc_path], None

    extract_dir = os.path.splitext(nc_path)[0] + "_extracted"
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(nc_path) as z:
        z.extractall(extract_dir)
        return [os.path.join(extract_dir, name) for name in z.namelist()], extract_dir


def convert_to_csv(output_csv):
    """Merge all downloaded NetCDF files (unzipping any bundled ones first)
    and write them out as a single CSV."""
    import shutil
    print(f"[convert] merging monthly files into {output_csv}")
    monthly_frames = []
    
    for year, month in month_range(START_YEAR, START_MONTH, END_YEAR, END_MONTH):
        print(f"Processing {year}-{month:02d}...")
        datasets = []
        
        # 1. Atmospheric pressure level file
        atmo_path = os.path.join(RAW_DIR, f"ERA5_Atmospheric_{year}_{month:02d}.nc")
        if os.path.exists(atmo_path):
            with xr.open_dataset(atmo_path) as ds_atmo:
                ds_atmo_loaded = ds_atmo.load()
                # Squeeze or select pressure level, drop unwanted coords
                if 'pressure_level' in ds_atmo_loaded.coords:
                    ds_atmo_loaded = ds_atmo_loaded.sel(pressure_level=950.0, drop=True)
                ds_atmo_loaded = ds_atmo_loaded.drop_vars(['expver', 'number'], errors='ignore')
                datasets.append(ds_atmo_loaded)
        else:
            print(f"Warning: {atmo_path} not found.")
            
        # 2. Single level file
        sl_path = os.path.join(RAW_DIR, f"ERA5_SingleLevel_{year}_{month:02d}.nc")
        sl_dir_to_clean = None
        if os.path.exists(sl_path):
            sl_members, sl_dir_to_clean = _extract_if_zip(sl_path)
            for member in sl_members:
                with xr.open_dataset(member) as ds_sl:
                    ds_sl_loaded = ds_sl.load()
                    ds_sl_loaded = ds_sl_loaded.drop_vars(['expver', 'number'], errors='ignore')
                    datasets.append(ds_sl_loaded)
        else:
            print(f"Warning: {sl_path} not found.")
            
        if datasets:
            merged = xr.merge(datasets, compat="override", join="outer")
            df_month = merged.to_dataframe().reset_index()
            monthly_frames.append(df_month)
            
            merged.close()
            for d in datasets:
                d.close()
            
            # Clean up the extracted temporary folder immediately after closing datasets
            if sl_dir_to_clean and os.path.exists(sl_dir_to_clean):
                shutil.rmtree(sl_dir_to_clean)
                
    if monthly_frames:
        df = pd.concat(monthly_frames, ignore_index=True)
        numeric_cols = df.select_dtypes(include="number").columns
        df[numeric_cols] = df[numeric_cols].round(2)
        df.to_csv(output_csv, index=False)
        print(f"[done] wrote {output_csv}")
    else:
        print("No datasets were successfully loaded.")


def main():
    client = cdsapi.Client(url=CDS_URL, key=CDS_KEY)

    for year, month in month_range(START_YEAR, START_MONTH, END_YEAR, END_MONTH):
        download_pressure_month(client, year, month)
        download_single_level_month(client, year, month)

    output_csv = os.path.join(SCRIPT_DIR, "ERA5_DK1_Merged.csv")
    convert_to_csv(output_csv)


if __name__ == "__main__":
    main()
