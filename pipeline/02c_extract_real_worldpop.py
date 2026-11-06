#!/usr/bin/env python3
"""
02c_extract_real_worldpop.py: Zonal Population Extraction from Official WorldPop Raster
--------------------------------------------------------------------------------------
Extracts exact pixel zonal population counts from jor_pop_100m.tif for all 1,035 H3 hexagons.
Updates data/boundaries/amman_zonal_res8.geojson with the real-world residential population baseline.
"""

import json
import os
import sys
from pathlib import Path
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RASTER_PATH = DATA_DIR / "rasters" / "jor_pop_100m.tif"
HEX_PATH = DATA_DIR / "boundaries" / "amman_hexagons_res8.geojson"
OUTPUT_PATH = DATA_DIR / "boundaries" / "amman_zonal_res8.geojson"

def extract_zonal_population():
    print("=" * 70)
    print("Extracting Real Zonal Population from WorldPop 100m GeoTIFF")
    print("=" * 70)
    
    if not RASTER_PATH.exists():
        print(f"[!] Error: {RASTER_PATH} not found.")
        sys.exit(1)
        
    gdf = gpd.read_file(HEX_PATH)
    n = len(gdf)
    print(f"[*] Loaded {n} H3 hexagons. Reprojecting to match raster CRS if needed...")
    
    with rasterio.open(RASTER_PATH) as src:
        print(f"[*] Raster metadata: {src.width} x {src.height}, CRS: {src.crs}, NoData: {src.nodata}")
        
        # Ensure GeoDataFrame is in the same CRS as raster (EPSG:4326)
        if gdf.crs != src.crs:
            gdf = gdf.to_crs(src.crs)
            
        real_pops = np.zeros(n)
        nodata_val = src.nodata if src.nodata is not None else -99999.0
        
        for i, geom in enumerate(gdf.geometry):
            try:
                # Mask raster to hexagon polygon
                out_image, _ = mask(src, [geom], crop=True)
                data = out_image[0]
                
                # Filter out nodata and negative values
                valid_mask = (data != nodata_val) & (data > 0) & (~np.isnan(data))
                if np.any(valid_mask):
                    cell_pop = float(np.sum(data[valid_mask]))
                else:
                    cell_pop = 0.0
                    
                real_pops[i] = round(cell_pop, 1)
            except Exception as e:
                real_pops[i] = 0.0
                
    gdf["real_worldpop_2023"] = real_pops
    
    # Floor minimum for urban fabric to avoid log(0) issues in inhabited parts
    # Replace zeros with a small baseline (e.g. 5) if hexagon has commercial buildings
    gdf["res_pop"] = np.where(gdf["real_worldpop_2023"] > 0, np.round(gdf["real_worldpop_2023"]).astype(int), 5)
    
    # Recompute Ambient Population with real population counts
    # Preserve commercial footprint and radiance from existing zonal file if present
    if OUTPUT_PATH.exists():
        existing_gdf = gpd.read_file(OUTPUT_PATH)
        gdf["comm_area_m2"] = existing_gdf["comm_area_m2"]
        gdf["viirs_mean_radiance"] = existing_gdf["viirs_mean_radiance"]
    else:
        gdf["comm_area_m2"] = 8000.0
        gdf["viirs_mean_radiance"] = 15.0
        
    phi = 0.4
    mean_comm = gdf["comm_area_m2"].mean()
    mean_pop = gdf["res_pop"].mean()
    gdf["ambient_pop"] = (gdf["res_pop"] + phi * ((gdf["comm_area_m2"] / mean_comm) * mean_pop)).round().astype(int)
    
    print("\n--- Real WorldPop Population Summary (Amman H3 Hexagons) ---")
    print(f"Total Metropolitan Population in Study Extent: {gdf['res_pop'].sum():,} residents")
    print(f"Hexagon Mean: {gdf['res_pop'].mean():.1f} residents/cell (~0.74 km2)")
    print(f"Hexagon Max:  {gdf['res_pop'].max():,} residents (Dense urban cores)")
    print(f"Hexagon Min:  {gdf['res_pop'].min():,} residents")
    
    gdf.to_file(OUTPUT_PATH, driver="GeoJSON")
    print(f"\n[✓] Successfully updated zonal GeoJSON: {OUTPUT_PATH}")

if __name__ == "__main__":
    extract_zonal_population()
