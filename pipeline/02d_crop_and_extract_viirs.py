#!/usr/bin/env python3
"""
02d_crop_and_extract_viirs.py: Crop Amman Window & Extract Zonal VIIRS Radiance
-------------------------------------------------------------------------------
1. Reads the global VIIRS average_masked GeoTIFF in data/rasters/.
2. Crops the exact Amman metropolitan bounding box (from amman_bounds.json).
3. Saves a lightweight local GeoTIFF: data/rasters/viirs_2023_amman.tif.
4. Performs zonal mean radiance aggregation for all 1,035 H3 hexagons.
5. Updates data/boundaries/amman_zonal_res8.geojson and amman_features_res8.geojson.
"""

import json
import os
import sys
from pathlib import Path
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds
from rasterio.mask import mask

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RASTER_DIR = DATA_DIR / "rasters"
BOUNDS_DIR = DATA_DIR / "boundaries"
SERVER_DATA_DIR = BASE_DIR / "dashboard" / "server" / "data"

BOUNDS_FILE = SERVER_DATA_DIR / "amman_bounds.json"
HEX_PATH = BOUNDS_DIR / "amman_hexagons_res8.geojson"
ZONAL_PATH = BOUNDS_DIR / "amman_zonal_res8.geojson"
FEATURES_PATH = BOUNDS_DIR / "amman_features_res8.geojson"
SERVER_FEATURES = SERVER_DATA_DIR / "amman_features_res8.geojson"

# Find uncompressed or compressed VIIRS file in data/rasters/
RAW_VIIRS_CANDIDATES = list(RASTER_DIR.glob("*average_masked*.tif")) + list(RASTER_DIR.glob("*average_masked*.tif.gz"))
AMMAN_VIIRS_TIF = RASTER_DIR / "viirs_2023_amman.tif"

def crop_amman_raster(raw_tif_path, bbox):
    """Crops the Amman bounding box from the global raster using rasterio windowing."""
    print(f"[*] Reading global raster header: {raw_tif_path.name}")
    min_lng, min_lat, max_lng, max_lat = bbox
    
    with rasterio.open(raw_tif_path) as src:
        print(f"    Global Dimensions: {src.width:,} x {src.height:,}, CRS: {src.crs}")
        window = from_bounds(min_lng, min_lat, max_lng, max_lat, transform=src.transform)
        
        # Read the cropped pixel window
        data = src.read(1, window=window)
        win_transform = rasterio.windows.transform(window, src.transform)
        
        out_meta = src.meta.copy()
        out_meta.update({
            "height": data.shape[0],
            "width": data.shape[1],
            "transform": win_transform,
            "compress": "lzw"
        })
        
        print(f"    Cropped Amman Dimensions: {data.shape[1]} x {data.shape[0]} pixels")
        with rasterio.open(AMMAN_VIIRS_TIF, "w", **out_meta) as dst:
            dst.write(data, 1)
            
    print(f"[✓] Saved cropped Amman GeoTIFF: {AMMAN_VIIRS_TIF} ({AMMAN_VIIRS_TIF.stat().st_size:,} bytes)")

def extract_zonal_radiance():
    """Extracts exact zonal mean radiance for each H3 hexagon."""
    if not AMMAN_VIIRS_TIF.exists():
        print(f"[!] Error: {AMMAN_VIIRS_TIF} not found.")
        sys.exit(1)
        
    gdf = gpd.read_file(HEX_PATH)
    n = len(gdf)
    print(f"[*] Loaded {n} H3 hexagons. Extracting zonal mean radiance...")
    
    with rasterio.open(AMMAN_VIIRS_TIF) as src:
        if gdf.crs != src.crs:
            gdf = gdf.to_crs(src.crs)
            
        nodata = src.nodata if src.nodata is not None else -999.0
        mean_rads = np.zeros(n)
        max_rads = np.zeros(n)
        
        for i, geom in enumerate(gdf.geometry):
            try:
                # Use filled=False so pixels outside the polygon are masked out (Audit Finding 1)
                out_img, _ = mask(src, [geom], crop=True, filled=False)
                data = out_img[0]
                if np.ma.count(data) > 0:
                    mean_val = float(np.ma.mean(data))
                    max_val = float(np.ma.max(data))
                else:
                    mean_val = 0.0
                    max_val = 0.0
                mean_rads[i] = round(mean_val, 4)
                max_rads[i] = round(max_val, 4)
            except Exception as e:
                mean_rads[i] = 0.0
                max_rads[i] = 0.0
                
    gdf["real_viirs_mean_radiance"] = mean_rads
    gdf["real_viirs_max_radiance"] = max_rads
    # In urban Amman, minimum background radiance baseline is ~1.0 nW/cm2/sr
    # Pure unfloored empirical zonal mean radiance (addressing audit finding 4)
    gdf["viirs_mean_radiance"] = mean_rads
    
    print("\n--- Real VIIRS Zonal Radiance Summary (Amman H3 Hexagons) ---")
    print(f"Mean Hex Radiance:  {gdf['viirs_mean_radiance'].mean():.2f} nW/cm²/sr")
    print(f"Max Hex Radiance:   {gdf['viirs_mean_radiance'].max():.2f} nW/cm²/sr (Core commercial hubs)")
    print(f"Min Hex Radiance:   {gdf['viirs_mean_radiance'].min():.2f} nW/cm²/sr")
    print(f"Median Hex Radiance:{gdf['viirs_mean_radiance'].median():.2f} nW/cm²/sr")
    
    # Update zonal GeoJSON
    if ZONAL_PATH.exists():
        zonal_gdf = gpd.read_file(ZONAL_PATH)
        zonal_gdf["viirs_mean_radiance"] = gdf["viirs_mean_radiance"]
        zonal_gdf.to_file(ZONAL_PATH, driver="GeoJSON")
        print(f"[✓] Updated zonal GeoJSON: {ZONAL_PATH}")
        
    # Update features GeoJSON
    if FEATURES_PATH.exists():
        feat_gdf = gpd.read_file(FEATURES_PATH)
        feat_gdf["viirs_mean_radiance"] = gdf["viirs_mean_radiance"]
        feat_gdf.to_file(FEATURES_PATH, driver="GeoJSON")
        feat_gdf.to_file(SERVER_FEATURES, driver="GeoJSON")
        print(f"[✓] Updated feature GeoJSON: {FEATURES_PATH}")
        print(f"[✓] Mirrored to analytical server: {SERVER_FEATURES}")

def main():
    print("=" * 70)
    print("02d_crop_and_extract_viirs.py: Ingesting Real VIIRS Nighttime Radiance")
    print("=" * 70)
    
    if not BOUNDS_FILE.exists():
        print(f"[!] Error: {BOUNDS_FILE} not found.")
        sys.exit(1)
        
    with open(BOUNDS_FILE, "r") as f:
        bounds_meta = json.load(f)
        
    bbox = (
        bounds_meta["min_lng"],
        bounds_meta["min_lat"],
        bounds_meta["max_lng"],
        bounds_meta["max_lat"]
    )
    print(f"[*] Amman Bounding Box: {bbox}")
    
    if not AMMAN_VIIRS_TIF.exists():
        if not RAW_VIIRS_CANDIDATES:
            print("[!] Error: No global VIIRS average_masked file found in data/rasters/.")
            sys.exit(1)
        raw_path = RAW_VIIRS_CANDIDATES[0]
        crop_amman_raster(raw_path, bbox)
    else:
        print(f"[✓] Cropped Amman GeoTIFF already exists: {AMMAN_VIIRS_TIF} ({AMMAN_VIIRS_TIF.stat().st_size:,} bytes)")
        
    extract_zonal_radiance()
    print("\n[SUCCESS] Real VIIRS nocturnal radiance extracted successfully.")

if __name__ == "__main__":
    main()
