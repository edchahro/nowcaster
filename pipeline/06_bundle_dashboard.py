#!/usr/bin/env python3
"""
06_bundle_dashboard.py: Re-bundle updated GeoJSON & Econometric data into data_bundle.js
----------------------------------------------------------------------------------------
Updates dashboard/public/data_bundle.js with the latest real VIIRS, OSM, and WorldPop metrics.
Enables offline loading in cesium_3d.html and index.html without local server requirements.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SERVER_DATA = BASE_DIR / "dashboard" / "server" / "data"
BUNDLE_FILE = BASE_DIR / "dashboard" / "public" / "data_bundle.js"

HEX_FILE = SERVER_DATA / "amman_hexagons_res8.geojson"
MACRO_FILE = SERVER_DATA / "amman_macro_boundaries.geojson"
SUMMARY_FILE = SERVER_DATA / "econometric_summary.json"
BOUNDS_FILE = SERVER_DATA / "amman_bounds.json"

def main():
    print("=" * 70)
    print("06_bundle_dashboard.py: Refreshing dashboard/public/data_bundle.js")
    print("=" * 70)
    
    with open(HEX_FILE, "r", encoding="utf-8") as f:
        hex_data = json.load(f)
    print(f"[*] Ingested {len(hex_data.get('features', []))} scored hexagons.")
    
    with open(MACRO_FILE, "r", encoding="utf-8") as f:
        macro_data = json.load(f)
    print(f"[*] Ingested {len(macro_data.get('features', []))} macro district boundaries.")
    
    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        summary_data = json.load(f)
    print("[*] Ingested econometric summary data.")
    
    with open(BOUNDS_FILE, "r", encoding="utf-8") as f:
        bounds_data = json.load(f)
    print("[*] Ingested Amman bounds.")
    
    with open(BUNDLE_FILE, "w", encoding="utf-8") as f:
        f.write(f"window.AMMAN_HEXAGONS_GEOJSON = {json.dumps(hex_data)};\n")
        f.write(f"window.AMMAN_MACRO_BOUNDARIES = {json.dumps(macro_data)};\n")
        f.write(f"window.AMMAN_ECONOMETRIC_SUMMARY = {json.dumps(summary_data)};\n")
        f.write(f"window.AMMAN_BOUNDS = {json.dumps(bounds_data)};\n")
        
    print(f"[✓] Successfully re-bundled: {BUNDLE_FILE} ({BUNDLE_FILE.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()
