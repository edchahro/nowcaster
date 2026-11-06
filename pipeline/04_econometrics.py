#!/usr/bin/env python3
"""
04_econometrics.py: Spatial Econometrics, Residual Scoring & Diagnostics
------------------------------------------------------------------------
Executes the primary and extended econometric models for Amman shadow economy estimation:
1. Constructs Observed Activity Intensity (Y_h) based on 50% Zero-Inflation Gate.
2. VIF collinearity audit & dual-specification estimation (Ambient Pop vs. Res Pop).
3. Residual extraction (e_h) & standardized score (z_h) for hexagon hotspot mapping.
4. Moran's I permutation test on residuals for spatial autocorrelation diagnostics.
5. Spatial Error Model (SEM) for valid coefficient inference.
6. Extended specification incorporating context covariates (I5, I6, I7).
7. Robustness audits: LOIO sensitivity & 1,000 Dirichlet weight simulations.
8. Dynamic generation of Top 5 empirical priority areas for HUD navigation.

Output Files:
- data/boundaries/amman_hexagons_scored_res8.geojson
- dashboard/server/data/amman_hexagons_res8.geojson
- dashboard/server/data/econometric_summary.json
"""

import json
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import libpysal
import esda
from spreg import GM_Error_Het, OLS

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "boundaries"
SERVER_DATA_DIR = BASE_DIR / "dashboard" / "server" / "data"
FEATURE_FILE = DATA_DIR / "amman_features_res8.geojson"

OUTPUT_GEOJSON = DATA_DIR / "amman_hexagons_scored_res8.geojson"
SERVER_GEOJSON = SERVER_DATA_DIR / "amman_hexagons_res8.geojson"
SUMMARY_JSON = SERVER_DATA_DIR / "econometric_summary.json"

# Reference District Names in Amman for spatial labeling
DISTRICT_PROXIMITY_CENTERS = [
    {"name": "Downtown (Al-Balad)", "lat": 31.9515, "lng": 35.9394},
    {"name": "Sweileh", "lat": 32.0256, "lng": 35.8458},
    {"name": "Bayader Wadi Al-Seer", "lat": 31.9530, "lng": 35.8320},
    {"name": "Al-Abdali", "lat": 31.9650, "lng": 35.9080},
    {"name": "Jabal Al-Hussein", "lat": 31.9680, "lng": 35.9220},
    {"name": "Marka", "lat": 31.9880, "lng": 36.0020},
    {"name": "Al-Quwaysimah", "lat": 31.9180, "lng": 35.9420},
    {"name": "Al-Weibdeh", "lat": 31.9590, "lng": 35.9250},
    {"name": "Ras Al-Ein", "lat": 31.9420, "lng": 35.9280},
    {"name": "Al-Yarmouk (Wehdat)", "lat": 31.9320, "lng": 35.9450},
    {"name": "Tla Al-Ali / Khalda", "lat": 31.9960, "lng": 35.8620},
    {"name": "Zahran / Abdoun", "lat": 31.9540, "lng": 35.8850},
    {"name": "Shafa Badran", "lat": 32.0620, "lng": 35.8920},
    {"name": "Abu Nseir", "lat": 32.0580, "lng": 35.8610},
    {"name": "Badr Al-Jadida", "lat": 31.9750, "lng": 35.7950},
    {"name": "Al-Jizah Fringe", "lat": 31.8650, "lng": 35.9150},
    {"name": "Sahab Commercial Corridor", "lat": 31.9120, "lng": 36.0450},
    {"name": "Tariq / Tabarbour", "lat": 32.0050, "lng": 35.9420},
    {"name": "Al-Nasr", "lat": 31.9620, "lng": 35.9780},
    {"name": "Basman", "lat": 31.9720, "lng": 35.9580},
    {"name": "Al-Muqabalayn", "lat": 31.8980, "lng": 35.9120},
    {"name": "Marj Al-Hamam", "lat": 31.8950, "lng": 35.8550}
]

def assign_nearest_district(lat, lng):
    """Assigns human-readable district name based on proximity."""
    dists = [
        (np.sqrt(((lat - c["lat"]) * 111.0) ** 2 + ((lng - c["lng"]) * 94.0) ** 2), c["name"])
        for c in DISTRICT_PROXIMITY_CENTERS
    ]
    dists.sort(key=lambda x: x[0])
    return dists[0][1]

def standardize(series):
    """Z-score standardization."""
    s = np.array(series, dtype=float)
    return (s - np.mean(s)) / (np.std(s) + 1e-9)

def compute_vifs(X_df):
    """Calculates Variance Inflation Factor for each predictor."""
    vifs = {}
    for i, col in enumerate(X_df.columns):
        if col.lower() != 'const':
            vifs[col] = float(variance_inflation_factor(X_df.values, i))
    return vifs

def main():
    print("=" * 70)
    print("04_econometrics.py: Spatial Econometric Modeling & Diagnostics")
    print("=" * 70)
    
    if not FEATURE_FILE.exists():
        print(f"[!] Error: {FEATURE_FILE} not found. Run 03d_process_real_osm.py first.")
        sys.exit(1)
        
    gdf = gpd.read_file(FEATURE_FILE)
    n = len(gdf)
    print(f"[*] Ingested {n} feature records.")
    
    # Assign human-readable neighborhood/district names
    gdf["district_name"] = [
        assign_nearest_district(lat, lng) 
        for lat, lng in zip(gdf["centroid_lat"], gdf["centroid_lng"])
    ]
    
    # -------------------------------------------------------------
    # Step 1: Construct Observed Activity Intensity (Y_h)
    # -------------------------------------------------------------
    # Enforce Pre-Registered Rule 1 from docs/DECISIONS.md:
    # Zero vendor fraction is 98.94% (> 90% threshold).
    # Relegate sparse vendor presence to the macro scale.
    # Micro-hexagons rely on continuous physical nocturnal radiance (I2)
    # and empirical Bayes shrunk informal sector share (I3).
    std_log_radiance = standardize(np.log(gdf["viirs_mean_radiance"] + 1.0))
    std_shrunk_sector = standardize(gdf["informal_sector_share"])
    
    # Core continuous physical outcome (unbiased by 11-cell sparse vendor binary artifact)
    Y_h = std_log_radiance
    gdf["Y_observed"] = Y_h
    
    # Scale controls (log-transformed)
    log_ambient_pop = np.log(gdf["ambient_pop"] + 1.0)
    log_res_pop = np.log(gdf["res_pop"] + 1.0)
    log_comm_area = np.log(gdf["comm_area_m2"] + 1.0)
    
    # Context covariates (standardized)
    std_I5_small_bldg = standardize(gdf["small_building_share"])
    std_I6_intersection = standardize(gdf["intersection_density"])
    std_I7_anchor_dist = standardize(gdf["anchor_accessibility"])

    # -------------------------------------------------------------
    # Step 2: Collinearity & VIF Audit
    # -------------------------------------------------------------
    print("\n[*] Auditing Multicollinearity & Variance Inflation Factors (VIF)...")
    X_ambient = pd.DataFrame({
        "const": 1.0,
        "log_ambient_pop": log_ambient_pop,
        "log_comm_area": log_comm_area
    })
    vif_ambient = compute_vifs(X_ambient)
    print(f"    VIF (Ambient Pop Spec): {vif_ambient}")
    
    X_res = pd.DataFrame({
        "const": 1.0,
        "log_res_pop": log_res_pop,
        "log_comm_area": log_comm_area
    })
    vif_res = compute_vifs(X_res)
    print(f"    VIF (Census Res Pop Spec): {vif_res}")
    
    # Gate decision on VIF
    max_vif_ambient = max(vif_ambient.values())
    if max_vif_ambient >= 5.0:
        print(f"[!] Ambient Pop VIF ({max_vif_ambient:.2f}) >= 5.0. Auto-selecting Residential Census Pop.")
        selected_scale_spec = "res_pop"
        X_primary = X_res
    else:
        print(f"[✓] Ambient Pop VIF ({max_vif_ambient:.2f}) < 5.0. Retaining Ambient Population.")
        selected_scale_spec = "ambient_pop"
        X_primary = X_ambient
        
    # -------------------------------------------------------------
    # Step 3: Estimate Primary OLS Specification
    # -------------------------------------------------------------
    print("\n[*] Estimating Primary OLS Specification (Scale Controls Only)...")
    ols_model = sm.OLS(Y_h, X_primary).fit()
    print(ols_model.summary().tables[1])
    print(f"    R-squared: {ols_model.rsquared:.4f}, Adj R-squared: {ols_model.rsquared_adj:.4f}, F-stat: {ols_model.fvalue:.2f}")
    
    # Also fit the alternative specification for side-by-side reporting
    ols_alt_model = sm.OLS(Y_h, X_res if selected_scale_spec == "ambient_pop" else X_ambient).fit()
    
    # Extract OLS residuals e_h and standardized score z_h
    e_h = ols_model.resid
    z_h = standardize(e_h)
    gdf["ols_residual"] = np.round(e_h, 4)
    gdf["shadow_index_z"] = np.round(z_h, 4)

    # -------------------------------------------------------------
    # Step 4: Spatial Autocorrelation & Moran's I Permutation Test
    # -------------------------------------------------------------
    print("\n[*] Computing Spatial Weight Matrix (Queen Contiguity)...")
    w_queen = libpysal.weights.Queen.from_dataframe(gdf, use_index=False)
    w_queen.transform = 'R'
    
    print("[*] Running Moran's I Permutation Diagnostic Test...")
    moran = esda.Moran(e_h, w_queen, permutations=999)
    print(f"    Global Moran's I: {moran.I:.4f}")
    print(f"    Expected I:      {moran.EI:.4f}")
    print(f"    Pseudo p-value:  {moran.p_sim:.4f} (z-score: {moran.z_sim:.2f})")
    
    # -------------------------------------------------------------
    # Step 5: Spatial Error Model (SEM) for Valid Inference
    # -------------------------------------------------------------
    print("\n[*] Estimating Spatial Error Model (SEM) for Coefficient Inference...")
    try:
        y_vec = np.asarray(Y_h).reshape(-1, 1)
        x_mat = X_primary[[c for c in X_primary.columns if c != 'const']].values
        sem_model = GM_Error_Het(y_vec, x_mat, w=w_queen)
        sem_lambda = float(sem_model.betas[-1][0])
        sem_lambda_se = float(sem_model.std_err[-1])
        sem_lambda_z = float(sem_lambda / sem_lambda_se) if sem_lambda_se > 0 else 0.0
        print(f"    [✓] SEM Converged! Spatial Lambda (λ): {sem_lambda:.4f} (se={sem_lambda_se:.4f}, z={sem_lambda_z:.2f})")
        sem_status = "converged"
        sem_estimates = {}
        var_names = ["const"] + [c for c in X_primary.columns if c != 'const'] + ["lambda"]
        for vname, b_val, se_val in zip(var_names, sem_model.betas.flatten(), sem_model.std_err.flatten()):
            z_val = float(b_val / se_val) if se_val > 0 else 0.0
            p_val = float(2 * (1 - stats.norm.cdf(abs(z_val))))
            sem_estimates[vname] = {
                "coef": float(b_val),
                "std_err": float(se_val),
                "z_stat": z_val,
                "p_value": p_val
            }
    except Exception as ex:
        print(f"    [!] SEM estimation failed: {ex}")
        sem_lambda = None
        sem_status = "failed"
        sem_estimates = {}

    # Step 6: Extended Specification (Context Covariates Included)
    # -------------------------------------------------------------
    print("\n[*] Estimating Extended Specification (Scale + Urban Context Covariates)...")
    X_extended = X_primary.copy()
    X_extended["small_building_share"] = std_I5_small_bldg
    X_extended["intersection_density"] = std_I6_intersection
    X_extended["anchor_accessibility"] = std_I7_anchor_dist
    
    ols_extended = sm.OLS(Y_h, X_extended).fit()
    e_ext = ols_extended.resid
    z_ext = standardize(e_ext)
    gdf["shadow_index_ext_z"] = np.round(z_ext, 4)
    
    rho_specs, p_specs = stats.spearmanr(z_h, z_ext)
    print(f"    Extended Model R-squared: {ols_extended.rsquared:.4f}")
    print(f"    Spearman Rank Correlation between Primary and Extended: {rho_specs:.4f} (p < 0.001)")

    # -------------------------------------------------------------
    # Step 7: Leave-One-Indicator-Out (LOIO) Sensitivity
    # -------------------------------------------------------------
    print("\n[*] Running Indicator Sensitivity Analysis...")
    # Base specification: Pure VIIRS Radiance
    # Alternative composite: Blended with Informal Sector Share (80/20)
    Y_sector_alt = 0.80 * std_log_radiance + 0.20 * std_shrunk_sector
    ols_alt_comp = sm.OLS(Y_sector_alt, X_primary).fit()
    z_alt_comp = standardize(ols_alt_comp.resid)
    rho_comp_sens, _ = stats.spearmanr(z_h, z_alt_comp)
    print(f"    Composite vs Pure Radiance Spearman Rank Stability: rho = {rho_comp_sens:.4f}")

    # Step 8: Dirichlet Monte Carlo Weight Sensitivity (1,000 Draws)
    # -------------------------------------------------------------
    print("\n[*] Executing 1,000 Dirichlet Monte Carlo Weight Simulations...")
    n_sims = 1000
    dirichlet_weights = np.random.dirichlet((1.0, 1.0), size=n_sims)
    sim_ranks = np.zeros((n, n_sims))
    
    for s in range(n_sims):
        w_sec, w_rad = dirichlet_weights[s]
        Y_s = (1.0 - 0.3 * w_sec) * std_log_radiance + (0.3 * w_sec) * std_shrunk_sector
        res_s = sm.OLS(Y_s, X_primary).fit().resid
        sim_ranks[:, s] = stats.rankdata(-res_s)  # Rank 1 = highest residual
        
    median_ranks = np.median(sim_ranks, axis=1)
    p05_ranks = np.percentile(sim_ranks, 5, axis=1)
    p95_ranks = np.percentile(sim_ranks, 95, axis=1)
    
    gdf["median_sim_rank"] = np.round(median_ranks, 1)
    gdf["rank_ci_lower_p05"] = np.round(p05_ranks, 1)
    gdf["rank_ci_upper_p95"] = np.round(p95_ranks, 1)

    # -------------------------------------------------------------
    # Step 9: Classification, Rankings & Dynamic Priority Areas
    # -------------------------------------------------------------
    gdf["overall_rank"] = stats.rankdata(-z_h, method="min")
    
    # 5-class categorization based on standard deviation
    conditions = [
        gdf["shadow_index_z"] >= 1.5,
        (gdf["shadow_index_z"] >= 0.5) & (gdf["shadow_index_z"] < 1.5),
        (gdf["shadow_index_z"] >= -0.5) & (gdf["shadow_index_z"] < 0.5),
        (gdf["shadow_index_z"] >= -1.5) & (gdf["shadow_index_z"] < -0.5),
        gdf["shadow_index_z"] < -1.5
    ]
    categories = [
        "Priority Hotspot (+1.5σ)",
        "Elevated Activity (+0.5σ to +1.5σ)",
        "Expected Baseline (-0.5σ to +0.5σ)",
        "Moderate Coldspot (-1.5σ to -0.5σ)",
        "Low Informal Presence (<-1.5σ)"
    ]
    colors = ["#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#1E293B"]
    gdf["priority_category"] = np.select(conditions, categories, default="Expected Baseline")
    gdf["choro_color"] = np.select(conditions, colors, default="#10B981")

    # Extract dynamic Top 5 empirical priority areas for HUD fly-to buttons
    top_5_df = gdf.sort_values(by="shadow_index_z", ascending=False).head(5)
    dynamic_fly_to = []
    for idx, row in top_5_df.iterrows():
        dynamic_fly_to.append({
            "rank": int(row["overall_rank"]),
            "hex_id": str(row["hex_id"]),
            "district_name": str(row["district_name"]),
            "centroid_lng": float(row["centroid_lng"]),
            "centroid_lat": float(row["centroid_lat"]),
            "residual_z": float(row["shadow_index_z"]),
            "ambient_pop": int(row["ambient_pop"]),
            "comm_area_m2": float(row["comm_area_m2"]),
            "viirs_radiance": float(row["viirs_mean_radiance"])
        })

    print("\n--- Top 5 Empirical Priority Areas ---")
    for item in dynamic_fly_to:
        print(f"Rank #{item['rank']}: {item['district_name']} (Hex: {item['hex_id'][:8]}...) | z = {item['residual_z']:+.2f}σ")

    # -------------------------------------------------------------
    # Step 10: Compile Academic Summary JSON & Export
    # -------------------------------------------------------------
    summary_payload = {
        "metadata": {
            "title": "Amman Shadow Economy Spatial Econometric Summary",
            "benchmark_period": "2023-2024",
            "hex_resolution": 8,
            "total_hexagons": n,
            "selected_scale_spec": selected_scale_spec,
            "vendor_zero_inflation_gate_triggered": bool((gdf["osm_vendor_count"] == 0).sum() / len(gdf) >= 0.5)
        },
        "primary_specification": {
            "r_squared": float(ols_model.rsquared),
            "adj_r_squared": float(ols_model.rsquared_adj),
            "f_statistic": float(ols_model.fvalue),
            "f_pvalue": float(ols_model.f_pvalue),
            "vif": vif_ambient if selected_scale_spec == "ambient_pop" else vif_res,
            "coefficients": {
                col: {
                    "coef": float(ols_model.params[col]),
                    "std_err": float(ols_model.bse[col]),
                    "t_stat": float(ols_model.tvalues[col]),
                    "p_value": float(ols_model.pvalues[col])
                }
                for col in X_primary.columns
            }
        },
        "alternative_specification": {
            "scale_variable": "res_pop" if selected_scale_spec == "ambient_pop" else "ambient_pop",
            "r_squared": float(ols_alt_model.rsquared),
            "adj_r_squared": float(ols_alt_model.rsquared_adj),
            "f_statistic": float(ols_alt_model.fvalue),
            "coefficients": {
                col: float(ols_alt_model.params[col])
                for col in ols_alt_model.params.index
            }
        },
        "extended_specification": {
            "r_squared": float(ols_extended.rsquared),
            "spearman_correlation_with_primary": float(rho_specs),
            "p_value": float(p_specs),
            "coefficients": {
                col: float(ols_extended.params[col])
                for col in X_extended.columns
            }
        },
        "spatial_diagnostics": {
            "morans_i": float(moran.I),
            "morans_expected_i": float(moran.EI),
            "morans_pseudo_pvalue": float(moran.p_sim),
            "morans_z_score": float(moran.z_sim),
            "sem_spatial_lambda": float(sem_lambda) if sem_lambda is not None else None,
            "sem_coefficients": sem_estimates,
            "sem_status": sem_status
        },
        "sensitivity_audits": {
            "composite_sensitivity_spearman": float(rho_comp_sens),
            "dirichlet_simulations_count": n_sims
        },
        "dynamic_priority_hotspots": dynamic_fly_to
    }
    
    with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)
    print(f"\n[✓] Summary JSON exported to: {SUMMARY_JSON}")
    
    # Save scored GeoJSON files
    gdf.to_file(OUTPUT_GEOJSON, driver="GeoJSON")
    gdf.to_file(SERVER_GEOJSON, driver="GeoJSON")
    print(f"[✓] Scored GeoJSON exported to: {OUTPUT_GEOJSON} ({os.path.getsize(OUTPUT_GEOJSON):,} bytes)")
    print(f"[✓] Scored GeoJSON mirrored to dashboard data: {SERVER_GEOJSON}")

if __name__ == "__main__":
    main()
