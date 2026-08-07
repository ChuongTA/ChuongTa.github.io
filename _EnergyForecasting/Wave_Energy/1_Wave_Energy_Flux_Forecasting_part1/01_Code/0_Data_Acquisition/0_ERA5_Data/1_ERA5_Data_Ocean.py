"""
Download ERA5 reanalysis ocean/wave data month-by-month from January 2024
through July 2026, then merge everything into a single CSV file.
"""

import os
import calendar
import zipfile
# pyrefly: ignore [missing-import]
import cdsapi
import pandas as pd
import xarray as xr

# ---------------------------------------------------------------------------
# CDS API credentials
# ---------------------------------------------------------------------------
# Prefer keeping credentials in %USERPROFILE%\.cdsapirc instead of hardcoding
# them here. They are set explicitly below only because they were provided
# directly for this script.
CDS_URL = "https://cds.climate.copernicus.eu/api"
CDS_KEY = "Add your API in here"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATASET = "reanalysis-era5-single-levels"

VARIABLES = [
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "mean_wave_direction",
    "mean_wave_period",
    "sea_surface_temperature",
    "significant_height_of_combined_wind_waves_and_swell",
    "total_precipitation",
    "mean_direction_of_total_swell",
    "mean_direction_of_wind_waves",
    "mean_period_of_total_swell",
    "mean_period_of_wind_waves",
    "model_bathymetry",
    "peak_wave_period",
    "significant_height_of_total_swell",
    "significant_height_of_wind_waves",
]

AREA = [41.51, -9.01, 41.49, -8.99]  # North, West, South, East
# Tight 0.25-deg box around the ERA5 grid point (41.50, -9.00), confirmed by
# a test request to be a sea point (ocean-masked variables like wave height
# return data there). Nearby candidates (41.50,-8.75), (41.25,-8.75) and
# (41.25,-9.00) all failed with a MARS "non-empty area crop/mask" error
# because they fall on land.

TIMES = [f"{h:02d}:00" for h in range(24)]

START_YEAR, START_MONTH = 2022, 1
END_YEAR, END_MONTH = 2026, 7

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "raw_netcdf")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "ERA5_Ocean_2024_01_to_2026_07.csv")

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


def download_month(client, year, month):
    """Download one month of ERA5 data as NetCDF, skipping if already present."""
    nc_path = os.path.join(RAW_DIR, f"ERA5_Ocean_{year}_{month:02d}.nc")
    if os.path.exists(nc_path):
        print(f"[skip] {nc_path} already exists")
        return nc_path

    days_in_month = calendar.monthrange(year, month)[1]
    days = [f"{d:02d}" for d in range(1, days_in_month + 1)]

    request = {
        "product_type": ["reanalysis"],
        "variable": VARIABLES,
        "year": [str(year)],
        "month": [f"{month:02d}"],
        "day": days,
        "time": TIMES,
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": AREA,
    }

    print(f"[download] {year}-{month:02d} -> {nc_path}")
    client.retrieve(DATASET, request).download(nc_path)
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
        return [nc_path]

    extract_dir = os.path.splitext(nc_path)[0] + "_extracted"
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(nc_path) as z:
        z.extractall(extract_dir)
        return [os.path.join(extract_dir, name) for name in z.namelist()]


def convert_to_csv(nc_paths, output_csv):
    """Merge all downloaded NetCDF files (unzipping any bundled ones first)
    and write them out as a single CSV."""
    print(f"[convert] merging {len(nc_paths)} monthly files into {output_csv}")
    monthly_frames = []
    for nc_path in nc_paths:
        member_paths = _extract_if_zip(nc_path)
        datasets = [xr.open_dataset(p) for p in member_paths]
        # The different streams can have slightly different time coordinates
        # (e.g. accumulated precipitation vs. instantaneous fields); merge with
        # an outer join so no timestamp is dropped, and override on conflicts
        # rather than hard-failing.
        merged = xr.merge(datasets, compat="override", join="outer")
        monthly_frames.append(merged.to_dataframe().reset_index())
        merged.close()
        for d in datasets:
            d.close()

    df = pd.concat(monthly_frames, ignore_index=True)
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].round(2)
    df.to_csv(output_csv, index=False)
    print(f"[done] wrote {output_csv}")


def main():
    client = cdsapi.Client(url=CDS_URL, key=CDS_KEY)

    nc_paths = []
    for year, month in month_range(START_YEAR, START_MONTH, END_YEAR, END_MONTH):
        nc_path = download_month(client, year, month)
        nc_paths.append(nc_path)

    convert_to_csv(nc_paths, OUTPUT_CSV)


if __name__ == "__main__":
    main()
