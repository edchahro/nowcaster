#!/usr/bin/env python3
"""
01_tessellation.py: H3 Spatial Tessellation & Dynamic Extent Generation
-----------------------------------------------------------------------
Generates H3 hexagonal grids (Resolutions 8 & 7) for Greater Amman Municipality (GAM).
Computes exact cell boundaries, centroids, and exports dynamic bounding box with a 10% buffer.

Output Files:
- data/boundaries/amman_hexagons_res8.geojson
- data/boundaries/amman_hexagons_res7.geojson
- dashboard/server/data/amman_hexagons_res8.geojson
- dashboard/server/data/amman_hexagons_res7.geojson
- dashboard/server/data/amman_bounds.json
"""

import json
import os
import sys
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, mapping
import h3

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "boundaries"
SERVER_DATA_DIR = BASE_DIR / "dashboard" / "server" / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)
SERVER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Greater Amman Municipality (GAM) Metropolitan Extent
# Covering core urban districts from Sweileh & Abu Nseir in the north to Quwaysimah in the south,
# and Wadi Al-Seer in the west to Marka & Sahab fringe in the east.
AMMAN_URBAN_BBOX = {
    "min_lat": 31.85,
    "max_lat": 32.10,
    "min_lng": 35.75,
    "max_lng": 36.08
}

def create_bounding_polygon(bbox):
    """Creates a Shapely Polygon from bounding box coordinates."""
    return Polygon([
        (bbox["min_lng"], bbox["min_lat"]),
        (bbox["max_lng"], bbox["min_lat"]),
        (bbox["max_lng"], bbox["max_lat"]),
        (bbox["min_lng"], bbox["max_lat"]),
        (bbox["min_lng"], bbox["min_lat"])
    ])

def generate_h3_grid(polygon, resolution):
    """Generates a GeoDataFrame of H3 cells covering the polygon."""
    cells = h3.geo_to_cells(polygon, res=resolution)
    records = []
    
    for cell in cells:
        # cell_to_boundary returns list of (lat, lng) tuples
        boundary_lat_lng = h3.cell_to_boundary(cell)
        # Convert to GeoJSON standard (lng, lat)
        boundary_lng_lat = [(lng, lat) for lat, lng in boundary_lat_lng]
        # Close the polygon ring
        if boundary_lng_lat[0] != boundary_lng_lat[-1]:
            boundary_lng_lat.append(boundary_lng_lat[0])
            
        cell_poly = Polygon(boundary_lng_lat)
        centroid = cell_poly.centroid
        
        records.append({
            "hex_id": str(cell),
            "resolution": resolution,
            "centroid_lng": round(centroid.x, 6),
            "centroid_lat": round(centroid.y, 6),
            "geometry": cell_poly
        })
        
    gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
    return gdf

def export_bounds(gdf_res8, buffer_pct=0.10):
    """Computes convex hull bounding box plus a 10% buffer to prevent camera clipping."""
    min_lng, min_lat, max_lng, max_lat = gdf_res8.total_bounds
    delta_lng = (max_lng - min_lng) * buffer_pct
    delta_lat = (max_lat - min_lat) * buffer_pct
    
    bounds_payload = {
        "min_lng": round(min_lng - delta_lng, 5),
        "min_lat": round(min_lat - delta_lat, 5),
        "max_lng": round(max_lng + delta_lng, 5),
        "max_lat": round(max_lat + delta_lat, 5),
        "center_lng": round((min_lng + max_lng) / 2.0, 5),
        "center_lat": round((min_lat + max_lat) / 2.0, 5),
        "buffer_percentage": buffer_pct,
        "empirical_hex_count_res8": len(gdf_res8),
        "urban_envelope": {
            "raw_min_lng": round(min_lng, 5),
            "raw_min_lat": round(min_lat, 5),
            "raw_max_lng": round(max_lng, 5),
            "raw_max_lat": round(max_lat, 5)
        }
    }
    
    bounds_file = SERVER_DATA_DIR / "amman_bounds.json"
    with open(bounds_file, "w", encoding="utf-8") as f:
        json.dump(bounds_payload, f, indent=2)
    return bounds_payload

def main():
    print("=" * 70)
    print("01_tessellation.py: Generating H3 Hexagonal Grid for Amman")
    print("=" * 70)
    
    envelope_poly = create_bounding_polygon(AMMAN_URBAN_BBOX)
    
    # Generate Resolution 8 (~0.74 km2 micro scale)
    print("[*] Generating H3 Resolution 8 cells...")
    gdf_res8 = generate_h3_grid(envelope_poly, resolution=8)
    print(f"    Total Res 8 Hexagons: {len(gdf_res8)}")
    
    # Generate Resolution 7 (~5.16 km2 macro scale)
    print("[*] Generating H3 Resolution 7 cells...")
    gdf_res7 = generate_h3_grid(envelope_poly, resolution=7)
    print(f"    Total Res 7 Hexagons: {len(gdf_res7)}")
    
    # Export Dynamic Bounds
    bounds = export_bounds(gdf_res8, buffer_pct=0.10)
    print(f"[✓] Dynamic Bounding Box exported to: {SERVER_DATA_DIR / 'amman_bounds.json'}")
    print(f"    Buffered Extent: [{bounds['min_lng']}, {bounds['min_lat']}] to [{bounds['max_lng']}, {bounds['max_lat']}]")
    print(f"    Center: Lat {bounds['center_lat']}, Lng {bounds['center_lng']}")
    
    # Save GeoJSON artifacts
    res8_file = DATA_DIR / "amman_hexagons_res8.geojson"
    res7_file = DATA_DIR / "amman_hexagons_res7.geojson"
    server_res8_file = SERVER_DATA_DIR / "amman_hexagons_res8.geojson"
    server_res7_file = SERVER_DATA_DIR / "amman_hexagons_res7.geojson"
    
    gdf_res8.to_file(res8_file, driver="GeoJSON")
    gdf_res8.to_file(server_res8_file, driver="GeoJSON")
    print(f"[✓] Res 8 GeoJSON saved: {res8_file} ({os.path.getsize(res8_file):,} bytes)")
    
    gdf_res7.to_file(res7_file, driver="GeoJSON")
    gdf_res7.to_file(server_res7_file, driver="GeoJSON")
    print(f"[✓] Res 7 GeoJSON saved: {res7_file} ({os.path.getsize(res7_file):,} bytes)")
    
    print("\n[SUCCESS] Spatial Tessellation complete.")

if __name__ == "__main__":
    main()
