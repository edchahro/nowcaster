# Amman Shadow Economy Spatial Nowcaster (2023–2024)
*A Business Intelligence Framework for Estimating Neighborhood-Level Informal Economic Activity in Greater Amman Municipality (GAM) Using Open Geospatial Data & a High-Contrast Dual 3D/2D Spatial Interface*

**Institution**: German Jordanian University (GJU) — School of Management and Logistics Sciences  
**Department**: Business Analytics / Graduation Project  
**Author**: Graduation Project Team  
**Supervision**: Department of Business Analytics  

---

## 1. Executive Summary & Research Motivation

Informal economic activity in Jordan constitutes an average of **17.38% of GDP (1991–2015)** ([Medina & Schneider, 2018](https://www.imf.org/en/Publications/WP/Issues/2018/01/25/Shadow-Economies-Around-the-World-What-Did-We-Learn-Over-the-Last-20-Years-45583)), while informal employment represents over **50% of the active labor force** (51.6% in 2021; [OECD, 2024](https://www.oecd.org/en/publications/informality-and-structural-transformation-in-egypt-iraq-and-jordan_3e5c9b68-en.html)). 

Because informal transactions operate outside formal administrative registries, municipal urban planners at the **Greater Amman Municipality (GAM)** and social protection agencies lack granular, neighborhood-level intelligence identifying where unrecorded commerce concentrates. 

This project provides an end-to-end, empirical Business Intelligence (BI) framework that combines open satellite observations, crowdsourced urban footprints, and spatial econometrics to estimate spatial shadow economic vitality across **1,035 H3 hexagonal urban units (Resolution 8, ~0.74 km²)** in Amman.

### Ethical Orientation & Non-Punitive Policy Framing
The outputs of this platform are engineered strictly for **constructive municipal planning and livelihood support**:
* Prioritizing municipal commercial infrastructure, public sanitary facilities, and organized marketplace stalls in high-vitality informal hubs.
* Guiding social protection programs, micro-finance initiatives, and vocational formalization incentives toward informal micro-entrepreneurs.
* Assisting public transport authorities in integrating transit corridors with pedestrian micro-commerce.
* **Disclaimer**: This framework generates relative proxy estimates for urban planning; it is **not** an audit registry and must never be utilized for punitive tax targeting or code enforcement.

---

## 2. Spatial Econometric Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               EMPIRICAL PIPELINE FLOW                                  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
   ┌───────────────────────┬────────────────┴──────────────────┬───────────────────────┐
   ▼                       ▼                                   ▼                       ▼
WorldPop 2023       OSM Jordan PBF                    EOG VIIRS 2023 DNB        DoS 2018 Census
(100m Population)   (85k Buildings & Footprints)      (Cropped Zonal Radiance)  (Liwa & GAM Baselines)
   │                       │                                   │                       │
   └───────────────────────┼───────────────────────────────────┴───────────────────────┘
                           ▼
             H3 Resolution 8 Spatial Tessellation (1,035 Hexagons)
                           │
                           ▼
             Econometric Discrepancy Formulation:
             Y_h = 0.40 * Std(I_vendors > 0) + 0.60 * Std(log(VIIRS + 1))
             Scale Controls: log(Ambient_Pop + 1) + log(Commercial_Area + 1)
                           │
                           ▼
             Primary OLS Specification: R² = 0.6144, F = 822.20
             Spatial Diagnostic: Global Moran's I = 0.1443 (z = 8.09, p < 0.001)
                           │
                           ▼
             Standardized Residual Hotspot Scoring (z_h)
             Top 5: Downtown Al-Balad (+9.61σ), Badr Al-Jadida (+8.80σ),
                    Abu Nseir (+8.72σ), Al-Quwaysimah (+8.39σ), Marka (+8.09σ)
```

### Econometric Formulation
Observed economic vitality ($Y_h$) is regressed against physical scale controls:
$$Y_h = \beta_0 + \beta_1 \log(\text{Ambient\_Pop}_h + 1) + \beta_2 \log(A_{\text{comm}, h} + 1) + \varepsilon_h$$

* **Ambient Population**: Dynamically scales sleeping residential population by commercial building area to account for daytime economic commuters.
* **50% Zero-Inflation Gate**: Triggered due to sparse micro-vendor tags (98.9% zeroes), substituting continuous count with a pre-registered binary presence indicator $\mathbb{I}(\text{Vendors}_h > 0)$.
* **OLS Residual Scoring**: Standardized residuals ($z_h = (e_h - \bar{e})/\sigma_e$) represent economic activity unexplained by formal physical infrastructure.
* **Spatial Autocorrelation**: Global Moran's $I = 0.1443$ ($p < 0.001$) confirms spatial clustering; Spatial Error Model (SEM) is estimated for valid parameter inference.

---

## 3. Repository Structure

```
caster-v1/
├── dashboard/
│   └── public/
│       ├── index.html              # 2D MapLibre Continuous Spatial Heatmap Console
│       ├── cesium_3d.html          # 3D Cesium Draped Terrain Heatmap & Column Console
│       ├── data_bundle.js          # Pre-bundled offline dataset (1.47 MB, zero-server)
│       ├── config.example.js       # Safe public template for Cesium Ion access token
│       └── config.js               # (Local only, ignored by Git) Active personal token
├── data/
│   ├── boundaries/                 # Scored H3 GeoJSONs (1,035 units, 22 GAM districts, 9 Liwas)
│   └── rasters/
│       └── viirs_2023_amman.tif    # Permanent cropped 2023 VIIRS radiance raster (33 KB)
├── pipeline/                       # Python 3.9+ reproducible spatial data pipeline
│   ├── 01_tessellation.py          # H3 grid generation & dynamic urban envelope
│   ├── 02c_extract_real_worldpop.py# WorldPop 100m zonal aggregation
│   ├── 02d_crop_and_extract_viirs.py# VIIRS radiance crop & zonal mean extraction
│   ├── 03d_process_real_osm.py     # OSM building footprints & POI feature extraction
│   ├── 04_econometrics.py          # Primary & Extended OLS, Moran's I, LOIO & Dirichlet
│   ├── 05_macro_boundaries.py      # GAM 22 Districts & 9 DoS Liwas aggregation
│   ├── 06_bundle_dashboard.py      # Refreshes data_bundle.js for offline dashboard
│   └── requirements.txt            # Python dependencies
├── docs/                           # Academic decision records & methodology notes
│   ├── DECISIONS.md                # Pre-registered hypotheses and inclusion gates
│   └── ETHICS_AND_DISCLOSURES.md   # Ethical charter and data provenance
├── .gitignore                      # Safeguards private tokens and large binaries
└── README.md
```

---

## 4. Quick Start & Execution

### Option A: Instant Offline Dashboard (No Web Server Required)
The platform is pre-bundled into `dashboard/public/data_bundle.js` for instant execution:
1. **2D Heatmap & Macro Console**:
   Double-click `dashboard/public/index.html` or open in any web browser (`file:///...`).
2. **3D Terrain Console**:
   * Copy `dashboard/public/config.example.js` to `dashboard/public/config.js`:
     ```bash
     cp dashboard/public/config.example.js dashboard/public/config.js
     ```
   * Open `dashboard/public/config.js` and paste your free Cesium Ion access token (from [ion.cesium.com](https://ion.cesium.com/tokens)).
   * Double-click `dashboard/public/cesium_3d.html`.

### Option B: Re-Running the Python Spatial Pipeline
To reproduce the econometric model from raw spatial inputs:
```bash
# 1. Activate Python virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r pipeline/requirements.txt

# 3. Execute spatial econometric estimation
python pipeline/04_econometrics.py

# 4. Generate macro boundary aggregations
python pipeline/05_macro_boundaries.py

# 5. Refresh client-side bundle
python pipeline/06_bundle_dashboard.py
```

---

## 5. Security & GitHub Secret Hygiene

This repository strictly separates public code from private credentials:
* **Private API Tokens**: Stored locally in `dashboard/public/config.js`, which is explicitly blocked by `.gitignore`.
* **Public Template**: `config.example.js` contains only dummy placeholder strings.
* **Large Files**: The `.gitignore` excludes temporary global satellite rasters and raw `.pbf` archives, keeping repository size under 15 MB for clean GitHub commits and fast cloning.

---

## 6. Citations & Data Attribution

* **OpenStreetMap**: © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), licensed under Open Database License (ODbL 1.0).
* **WorldPop**: [WorldPop Jordan Population Distribution (2023)](https://www.worldpop.org/), licensed under Creative Commons Attribution 4.0 International (CC-BY 4.0).
* **VIIRS Nocturnal Radiance**: Earth Observation Group (EOG), Payne Institute for Public Policy, Colorado School of Mines (*VNL v2.2*, 2023).
* **Economic Census**: Hashemite Kingdom of Jordan Department of Statistics (DoS), *Economic Census 2018*.
* **Academic References**:
  * Medina, L., & Schneider, F. (2018). *Shadow economies around the world: What did we learn over the last 20 years?* IMF Working Paper WP/18/17.
  * OECD. (2024). *Informality and structural transformation in Egypt, Iraq and Jordan*. OECD Publishing, Paris.
  * Elvidge, C. D., Zhizhin, M., Ghosh, T., Hsu, F. C., & Taneja, J. (2021). *Annual time series of global VIIRS nighttime lights*. Remote Sensing, 13(5), 922.
