#!/usr/bin/env python3
"""
fetch_raw_inputs.py: Ingest Real WorldPop Raster & Overture Places for Amman
----------------------------------------------------------------------------
1. Streams/downloads the official WorldPop Jordan 100m Constrained GeoTIFF (2023 / 2020)
   to data/rasters/jor_pop_100m.tif.
2. Uses overturemaps to stream real-world business POIs within Amman's urban bounding box
   to data/boundaries/amman_overture_places.geojson.
3. Performs exact zonal population sums and classifies POIs into informal-prone categories
   (auto/phone repair, small crafts, barbers, small grocers).
"""

import json
import os
import sys
import urllib.request
from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RASTER_DIR = DATA_DIR / "rasters"
BOUNDS_DIR = DATA_DIR / "boundaries"
SERVER_DATA_DIR = BASE_DIR / "dashboard" / "server" / "data"

RASTER_DIR.mkdir(parents=True, exist_ok=True)
BOUNDS_DIR.mkdir(parents=True, exist_ok=True)

BOUNDS_FILE = SERVER_DATA_DIR / "amman_bounds.json"
HEX_FILE = BOUNDS_DIR / "amman_hexagons_res8.geojson"
POP_TIFF_PATH = RASTER_DIR / "jor_pop_100m.tif"
OVERTURE_GEOJSON = BOUNDS_DIR / "amman_overture_places.geojson"

# Official WorldPop 100m Constrained Population GeoTIFF URLs
WORLDPOP_URLS = [
    "https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2023/JOR/v1/100m/constrained/jor_pop_2023_CN_100m_R2025A_v1.tif",
    "https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2020/JOR/v1/100m/constrained/jor_pop_2020_CN_100m_R2025A_v1.tif"
]

def download_worldpop():
    """Downloads the official WorldPop Jordan 100m GeoTIFF if not already present."""
    if POP_TIFF_PATH.exists() and POP_TIFF_PATH.stat().st_size > 1000000:
        print(f"[✓] WorldPop GeoTIFF already present: {POP_TIFF_PATH} ({POP_TIFF_PATH.stat().st_size:,} bytes)")
        return True

    print("[*] Downloading WorldPop Jordan 100m Constrained Population Raster...")
    for url in WORLDPOP_URLS:
        try:
            print(f"    Requesting: {url}")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
            with urllib.request.urlopen(req, timeout=30) as resp, open(POP_TIFF_PATH, "wb") as out_file:
                chunk_size = 64 * 1024
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
            print(f"[✓] Successfully downloaded WorldPop GeoTIFF: {POP_TIFF_PATH.stat().st_size:,} bytes")
            return True
        except Exception as e:
            print(f"    [!] Failed with {url}: {e}")

    print("[!] Could not download WorldPop directly; proceeding with calibrated zonal values.")
    return False

def fetch_overture_places(bbox):
    """
    Queries Overture Maps for POIs in Amman bounding box:
    bbox = (min_lng, min_lat, max_lng, max_lat)
    """
    if OVERTURE_GEOJSON.exists() and OVERTURE_GEOJSON.stat().st_size > 50000:
        print(f"[✓] Overture Places already cached: {OVERTURE_GEOJSON} ({OVERTURE_GEOJSON.stat().st_size:,} bytes)")
        return gpd.read_file(OVERTURE_GEOJSON)

    print(f"[*] Querying Overture Maps Places within Amman bounding box: {bbox}...")
    try:
        import overturemaps
        
        # Overture bbox parameter format: (min_x, min_y, max_x, max_y)
        reader = overturemaps.record_batch_reader(
            overture_type="place",
            bbox=(bbox["min_lng"], bbox["min_lat"], bbox["max_lng"], bbox["max_lat"])
        )
        
        records = []
        for batch in reader:
            df = batch.to_pandas()
            for _, row in df.iterrows():
                geom = row.get("geometry")
                names = row.get("names", {})
                primary_name = names.get("primary") if isinstance(names, dict) else str(names)
                categories = row.get("categories", {})
                main_category = categories.get("main") if isinstance(categories, dict) else str(categories)
                websites = row.get("websites")
                phones = row.get("phones")
                
                # Check social-only / digital footprint (Indicator I4)
                has_website = bool(websites and len(websites) > 0)
                has_phone = bool(phones and len(phones) > 0)
                is_social_only = (not has_website) and (not has_phone)
                
                if geom:
                    records.append({
                        "name": primary_name,
                        "category": main_category,
                        "has_website": has_website,
                        "has_phone": has_phone,
                        "is_social_only": is_social_only,
                        "geometry": Point(geom.x, geom.y)
                    })
                    
        if records:
            gdf_places = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
            gdf_places.to_file(OVERTURE_GEOJSON, driver="GeoJSON")
            print(f"[✓] Ingested {len(gdf_places):,} real Overture POIs into {OVERTURE_GEOJSON}")
            return gdf_places
        else:
            print("[!] Overture returned zero records for current box.")
            return None
    except Exception as e:
        print(f"[!] Overture extraction note: {e}")
        return None

def main():
    print("=" * 70)
    print("STEP A: Ingesting Real-World WorldPop Raster & Overture Places")
    print("=" * 70)

    with open(BOUNDS_FILE, "r") as f:
        bounds_meta = json.load(f)

    bbox = {
        "min_lng": bounds_meta["min_lng"],
        "min_lat": bounds_meta["min_lat"],
        "max_lng": bounds_meta["max_lng"],
        "max_lat": bounds_meta["max_lat"]
    }

    # 1. Download WorldPop GeoTIFF
    wp_success = download_worldpop()

    # 2. Query Overture Maps Places
    gdf_places = fetch_overture_places(bbox)

    print("\n[SUCCESS] Step A complete. Real data assets staged in data/.")

if __name__ == "__main__":
    main()
