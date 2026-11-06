#!/usr/bin/env python3
"""
05_macro_boundaries.py: Macro Scale Aggregation & Discrepancy Model
-------------------------------------------------------------------
Implements Section 4.C of the academic implementation plan:
1. Ingests documented external administrative tables from CSV:
   - Path A: 22 GAM Administrative Districts (data/macro/gam_district_licenses_baseline.csv)
   - Path B: 9 Administrative Liwas of Amman Governorate (data/macro/dos_census_2018_liwas.csv)
2. Spatially aggregates H3 hexagon metrics (Population, Commercial Area, Radiance, Vendors)
   into each macro administrative unit via pre-registered Voronoi-proximate aggregation.
3. Estimates Macro Discrepancy Index (Residual nu_d for Districts; Activity-to-Establishment Ratio for Liwas).
4. Computes exact statistical ranks via scipy.stats.rankdata (fixing index-permutation argsort).
5. Exports tidy GeoJSON layers and updates econometric_summary.json.

Output Files:
- data/boundaries/amman_macro_districts_22.geojson
- data/boundaries/amman_macro_liwas_9.geojson
- dashboard/server/data/amman_macro_boundaries.geojson
"""

import json
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from scipy.stats import rankdata
import statsmodels.api as sm

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "boundaries"
MACRO_DATA_DIR = BASE_DIR / "data" / "macro"
SERVER_DATA_DIR = BASE_DIR / "dashboard" / "server" / "data"

HEX_FILE = DATA_DIR / "amman_hexagons_scored_res8.geojson"
SUMMARY_FILE = SERVER_DATA_DIR / "econometric_summary.json"

GAM_CSV_FILE = MACRO_DATA_DIR / "gam_district_licenses_baseline.csv"
DOS_CSV_FILE = MACRO_DATA_DIR / "dos_census_2018_liwas.csv"

DISTRICTS_22_FILE = DATA_DIR / "amman_macro_districts_22.geojson"
LIWAS_9_FILE = DATA_DIR / "amman_macro_liwas_9.geojson"
SERVER_MACRO_FILE = SERVER_DATA_DIR / "amman_macro_boundaries.geojson"

def load_macro_reference_data():
    """Loads documented external CSV tables for 22 GAM districts and 9 DoS Liwas."""
    if not GAM_CSV_FILE.exists() or not DOS_CSV_FILE.exists():
        print(f"[!] Error: Missing CSV baseline files in {MACRO_DATA_DIR}")
        sys.exit(1)
        
    df_gam = pd.read_csv(GAM_CSV_FILE, comment="#")
    df_dos = pd.read_csv(DOS_CSV_FILE, comment="#")
    
    print(f"[✓] Ingested {len(df_gam)} GAM districts from: {GAM_CSV_FILE.name}")
    print(f"[✓] Ingested {len(df_dos)} DoS Liwas from:      {DOS_CSV_FILE.name}")
    return df_gam, df_dos

def build_boundary_polygons(df_centers, hex_gdf):
    """
    Constructs clean, contiguous administrative polygons by grouping H3 hexagons 
    to their nearest administrative center (preserving exact urban hexagon tessellation).
    """
    centers_records = df_centers.to_dict(orient="records")
    
    # Assign each hexagon to nearest administrative center
    assigned_ids = []
    for _, row in hex_gdf.iterrows():
        c_lng, c_lat = row["centroid_lng"], row["centroid_lat"]
        dists = [
            (np.sqrt(((c_lat - c["centroid_lat"]) * 111.0) ** 2 + ((c_lng - c["centroid_lng"]) * 94.0) ** 2), c["id"])
            for c in centers_records
        ]
        dists.sort(key=lambda x: x[0])
        assigned_ids.append(dists[0][1])
        
    hex_gdf_copy = hex_gdf.copy()
    hex_gdf_copy["macro_id"] = assigned_ids
    
    # Dissolve hexagons into administrative polygons
    dissolved = hex_gdf_copy.dissolve(by="macro_id", aggfunc={
        "res_pop": "sum",
        "ambient_pop": "sum",
        "comm_area_m2": "sum",
        "viirs_mean_radiance": "mean",
        "osm_vendor_count": "sum"
    }).reset_index()
    
    # Merge metadata attributes
    merged = dissolved.merge(df_centers, left_on="macro_id", right_on="id")
    merged["lat"] = merged["centroid_lat"]
    merged["lng"] = merged["centroid_lng"]
    
    return gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:4326")

def compute_macro_discrepancy(gdf_districts, gdf_liwas):
    """
    Estimates the Macro Discrepancy Index for both GAM Districts (Path A) and DoS Liwas (Path B).
    """
    print("\n[*] Estimating Macro Scale Econometric Models...")
    
    # -------------------------------------------------------------
    # Path A: GAM 22 Districts - Exploratory OLS Regression
    # -------------------------------------------------------------
    std_rad_d = (gdf_districts["viirs_mean_radiance"] - gdf_districts["viirs_mean_radiance"].mean()) / gdf_districts["viirs_mean_radiance"].std()
    std_ven_d = (gdf_districts["osm_vendor_count"] - gdf_districts["osm_vendor_count"].mean()) / gdf_districts["osm_vendor_count"].std()
    obs_activity_d = 0.50 * std_ven_d + 0.50 * std_rad_d
    gdf_districts["observed_activity_score"] = np.round(obs_activity_d, 4)
    
    X_d = pd.DataFrame({
        "const": 1.0,
        "est_licenses": gdf_districts["est_licenses"],
        "ambient_pop": gdf_districts["ambient_pop"]
    })
    y_d = obs_activity_d
    
    ols_macro = sm.OLS(y_d, X_d).fit()
    nu_d = ols_macro.resid
    discrepancy_z = (nu_d - nu_d.mean()) / (nu_d.std() + 1e-9)
    gdf_districts["discrepancy_residual_z"] = np.round(discrepancy_z, 4)
    
    # FIXED: Use scipy rankdata for true mathematical ranking (1 = highest positive residual)
    gdf_districts["macro_rank"] = rankdata(-discrepancy_z, method="min").astype(int)
    
    print(f"    Path A (GAM 22 Districts OLS, n=22): R2 = {ols_macro.rsquared:.4f}, F = {ols_macro.fvalue:.2f}")

    # -------------------------------------------------------------
    # Path B: DoS 9 Liwas - Activity-to-Establishment Ratio (n=9)
    # -------------------------------------------------------------
    std_rad_l = (gdf_liwas["viirs_mean_radiance"] - gdf_liwas["viirs_mean_radiance"].mean()) / gdf_liwas["viirs_mean_radiance"].std()
    std_ven_l = (gdf_liwas["osm_vendor_count"] - gdf_liwas["osm_vendor_count"].mean()) / gdf_liwas["osm_vendor_count"].std()
    obs_activity_l = 0.50 * std_ven_l + 0.50 * std_rad_l
    gdf_liwas["observed_activity_score"] = np.round(obs_activity_l, 4)
    
    ratio_l = (gdf_liwas["comm_area_m2"] / gdf_liwas["census_2018_est"])
    ratio_z = (ratio_l - ratio_l.mean()) / (ratio_l.std() + 1e-9)
    gdf_liwas["activity_establishment_ratio"] = np.round(ratio_l, 2)
    gdf_liwas["discrepancy_residual_z"] = np.round(ratio_z, 4)
    
    # FIXED: Use scipy rankdata for true mathematical ranking (1 = highest ratio)
    gdf_liwas["macro_rank"] = rankdata(-ratio_z, method="min").astype(int)
    
    print(f"    Path B (DoS 9 Liwas Ratio, n=9): Computed Activity-to-Establishment Ratios.")

    return gdf_districts, gdf_liwas, ols_macro

def main():
    print("=" * 70)
    print("05_macro_boundaries.py: Macro Scale Aggregation & Discrepancy Model")
    print("=" * 70)
    
    if not HEX_FILE.exists():
        print(f"[!] Error: {HEX_FILE} not found. Run previous pipeline steps first.")
        sys.exit(1)
        
    hex_gdf = gpd.read_file(HEX_FILE)
    print(f"[*] Ingested {len(hex_gdf)} H3 hexagons for macro aggregation.")
    
    # Load documented CSV reference tables
    df_gam, df_dos = load_macro_reference_data()
    
    # Build 22 Districts
    print("[*] Generating 22 GAM Administrative Districts boundaries...")
    gdf_districts = build_boundary_polygons(df_gam, hex_gdf)
    
    # Build 9 Liwas
    print("[*] Generating 9 DoS Administrative Liwas boundaries...")
    gdf_liwas = build_boundary_polygons(df_dos, hex_gdf)
    
    # Run Macro Discrepancy Models
    gdf_districts, gdf_liwas, ols_macro = compute_macro_discrepancy(gdf_districts, gdf_liwas)
    
    # Save GeoJSON files
    gdf_districts.to_file(DISTRICTS_22_FILE, driver="GeoJSON")
    gdf_districts.to_file(SERVER_MACRO_FILE, driver="GeoJSON")
    gdf_liwas.to_file(LIWAS_9_FILE, driver="GeoJSON")
    
    print(f"\n[✓] Exported 22 GAM Districts: {DISTRICTS_22_FILE} ({os.path.getsize(DISTRICTS_22_FILE):,} bytes)")
    print(f"[✓] Exported 9 DoS Liwas:       {LIWAS_9_FILE} ({os.path.getsize(LIWAS_9_FILE):,} bytes)")
    print(f"[✓] Mirrored to analytical server: {SERVER_MACRO_FILE}")
    
    # Update econometric_summary.json with macro findings
    if SUMMARY_FILE.exists():
        with open(SUMMARY_FILE, "r") as f:
            summary = json.load(f)
            
        summary["macro_scale_models"] = {
            "path_a_gam_22_districts": {
                "n_units": 22,
                "r_squared": float(ols_macro.rsquared),
                "f_statistic": float(ols_macro.fvalue),
                "p_value": float(ols_macro.f_pvalue),
                "top_discrepancy_districts": [
                    {
                        "rank": int(row["macro_rank"]),
                        "district_name": row["name_en"],
                        "name_ar": row["name_ar"],
                        "residual_z": float(row["discrepancy_residual_z"]),
                        "registered_licenses": int(row["est_licenses"]),
                        "observed_activity": float(row["observed_activity_score"])
                    }
                    for _, row in gdf_districts.sort_values(by="discrepancy_residual_z", ascending=False).head(5).iterrows()
                ]
            },
            "path_b_dos_9_liwas": {
                "n_units": 9,
                "method": "Activity-to-Establishment Ratio (Descriptive Only)",
                "top_ratio_liwas": [
                    {
                        "rank": int(row["macro_rank"]),
                        "liwa_name": row["name_en"],
                        "name_ar": row["name_ar"],
                        "ratio_z": float(row["discrepancy_residual_z"]),
                        "census_establishments_2018": int(row["census_2018_est"])
                    }
                    for _, row in gdf_liwas.sort_values(by="discrepancy_residual_z", ascending=False).head(5).iterrows()
                ]
            }
        }
        
        with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"[✓] Updated {SUMMARY_FILE} with macro discrepancy tables.")

if __name__ == "__main__":
    main()
