# BI Graduation Project: Econometric & Geospatial Framework for Estimating Shadow Economic Activity in Amman
*Working Title: A Business Intelligence Framework for Estimating Neighborhood-Level Shadow Economy Activity in Amman Using Open Geospatial Data & a High-Contrast 3D/2D Spatial Interface*  
*Temporal Benchmark: 2023–2024 Geospatial Data, 2018 Census Baseline*  
*Academic Institution: German Jordanian University (GJU) — School of Management and Logistics Sciences / Department of Business Analytics (BI & Data Analytics Graduation Project)*

---

## Executive Summary & Methodological Specifications

> [!IMPORTANT]
> This plan formalizes the econometric architecture, spatial data engineering, and dual-mode analytical dashboard implementation for the graduation project:
>
> 1. **Zero-Inflation Handling & 50% Go/No-Go Gate**:
>    - Because micro-vendor tags (`stall=*`, `street_vendor=*`) are sparse in Amman, log-transformation leaves many hexes at zero.
>    - A strict **50% Go/No-Go Gate** is enforced: if $\ge 50\%$ of urban hexagons contain zero qualifying vendor features, the continuous vendor count is replaced with a **binary Presence/Absence indicator** ($\mathbb{I}(\text{Vendors}_h > 0)$) in the composite, or vendor counts are elevated exclusively to the macro scale while micro-hexes rely on continuous VIIRS radiance anomalies.
> 2. **Mathematical Specification & Residual Scoring**:
>    - Indicators are log-transformed *first*, then standardized: $Y_h = \sum_{k \in \mathcal{K}} \alpha_k \cdot \text{Std}(f_k(\text{Ind}_{k,h}))$, with equal weights $\alpha_k = 1/|\mathcal{K}|$ as baseline.
>    - $Y_h$ is regressed directly on scale controls without an outer log, preventing $\log(\le 0)$ domain errors.
>    - Hexagon scores are computed from the **OLS residual ($e_h$)** (preserving localized, spatially clustered informal hotspots). The **Spatial Error Model (SEM)** is used strictly for **coefficient and standard error inference**, ensuring that spatial autocorrelation does not artificially inflate predictor significance ($t$-statistics).
> 3. **Multicollinearity, VIF Logging & Dual Reporting**:
>    - Variance Inflation Factors (VIF) are computed for all predictors. If $\text{VIF} \ge 5$ (due to commercial footprint appearing in ambient population), the model automatically selects unadjusted residential census population ($\text{Res\_Pop}_h$).
>    - The selected specification is programmatically recorded in `econometric_summary.json`, and **both specifications (Ambient Pop vs. Res Pop) are reported side-by-side** in the sensitivity table of the thesis.
> 4. **Clean Multi-Residual Dashboard Gap Model**:
>    - Eliminates double-counting in the multi-criteria gap model. The system weights independent scale residuals:
>      $$SPI_h^{\text{gap}} = \sum_{k \in \mathcal{K}} w_k \cdot \text{MinMax}(\text{Residual}_{k, h}), \quad \sum_{k \in \mathcal{K}} w_k = 1.0$$
>      where $\mathbf{X}_{\text{scale}, h} = [\log(\text{Pop}_h + 1), \log(A_{\text{comm}, h} + 1)]$ uses the exact same predictors as the primary econometric model.
> 5. **Macro Baseline Decision Tree & Unit Consistency**:
>    - Macro observed activity standardizes constituent indicators across macro units before averaging.
>    - **Primary Path (If GAM Data Released)**: Exploratory 22-district OLS regression ($n = 22$) benchmarking observed district activity against registered municipal commercial licenses.
>    - **Fallback Path (If GAM Data Stalls)**: Aggregation to the **9 Administrative Liwas of Amman Governorate** using the Department of Statistics (DoS) 2018 Economic Census. Explicitly labeled as **"Activity-to-Establishment Ratio (Observed Commercial Presence vs. Census-Enumerated Establishments)"** (descriptive only, $n = 9$).
> 6. **Verified Primary Citations & Data Terms**:
>    - *Shadow Economy Benchmark*: Medina, L. & Schneider, F. (2018), *Shadow Economies Around the World: What Did We Learn Over the Last 20 Years?*, IMF Working Paper WP/18/17, Country Dataset (Jordan shadow economy averaged **17.38% of GDP over 1991–2015**).
>    - *Informal Employment*: OECD (2024), *Informality and Structural Transformation in Egypt, Iraq and Jordan*, OECD Publishing, Paris, documenting informal worker shares of **44.7% (2017), 53.5% (2020), and 51.6% (2021)**.
>    - *Places API Caching*: Cited under **Google Maps Platform Service Specific Terms (Section 5.4 "Places API - Caching")**: Place IDs stored indefinitely; latitude and longitude cached up to 30 calendar days; other Place attributes prohibited from persistent storage.
>    - *VIIRS Annual Composites*: Earth Observation Group (EOG), Payne Institute, Colorado School of Mines (*VNL v2.2*, 2023). Downloaded via registered HTTPS access on `eogdata.mines.edu` (Elvidge et al., 2021).
>    - *DoS Data*: Public statistical publications from the Jordan Department of Statistics, accessed for non-commercial academic research.
> 7. **Empirical Ground-Truth Audit Power & Tie-Aware Statistics**:
>    - Stratified random sampling ($N = 9$ hexes: 3 High, 3 Medium, 3 Low predicted terciles) surveyed during uniform peak windows (Wednesday or Thursday 16:00–18:00).
>    - Low-tercile fallback: if a sampled hex has no commercial street, surveyors audit the **busiest street or primary pedestrian thoroughfare**.
>    - All rank correlations ($\rho_{\text{LOIO}}$, $\rho_{\text{MAUP}}$, and $\rho_{\text{audit}}$) are computed using `scipy.stats.spearmanr` to account for fractional tied ranks. The exact two-tailed critical cutoff for $\alpha = 0.05, N = 9$ is **$r_{s, \text{crit}} = 0.700$**.
> 8. **Dynamic Urban Extent Masking & Dynamic Camera Frustum**:
>    - Urban hexagon counts are computed dynamically from the spatial intersection with the urban built-up mask (OSM building density threshold $\ge 5$ structures/hex).
>    - Dashboard camera boundaries are dynamically calculated from the convex hull bounding box of the urban hexagon extent plus a **10% spatial margin**, preventing edge clipping in southern or eastern Amman (such as Sahab, Al-Jizah, or Marka fringes).
> 9. **Tiered Indicator Framework & Inclusion Pre-Registration (Section 4.E)**:
>    - Strict role separation: Outcome indicators (I1–I4) enter $Y_h$; context covariates (I5–I7) enter only the *extended* regression specification.
>    - All indicators must satisfy four pre-registered inclusion rules: coverage $\ge 50\%$, pairwise $|r| < 0.80$, declared theoretical sign, and verified open license.
>    - Ratio indicators apply Empirical Bayes shrinkage ($m = 10$). Sensitivity is audited across equal weights, core-heavy, and 1,000 Dirichlet weight draws.
> 10. **Dual-Mode 3D/2D Interface, Ethical Framing & Week 4 Go/No-Go Gate (Section 7)**:
>    - Adapts the high-contrast analytical UI of **God's Eye View (GEV)** into a municipal decision-support console for urban planning, commercial formalization, and social protection programs (strictly non-punitive, non-enforcement framing).
>    - All planetary tracking modules (commercial/military flights, maritime AIS, CCTV, seismographs) are purged.
>    - **Week 4 Go/No-Go Fallback Gate**: If the 3D Cesium GEV fork fails to render H3 hexagons over Amman's terrain smoothly by the end of Week 4, the frontend immediately switches to a 2D **MapLibre GL JS vector choropleth**.
>    - **Mandatory 2D Top-Down Viewport Toggle**: Preserved alongside 3D column extrusions to eliminate perspective occlusion from Amman's steep hills and provide publication-standard figures for the academic thesis.
>    - **Dynamic Navigation & Transparent Attribution**: Quick-zoom navigation targets are generated dynamically from top-ranked empirical model output. Complete legal attribution is restored for OSM, WorldPop, EOG, Overture, Cesium, and Esri/CartoDB.

---

## 1. Research Aim & Theoretical Grounding

### Academic Problem Statement
Informal economic activity in Jordan represents an average of **17.38% of GDP (1991–2015)** (Medina & Schneider, 2018), while informal employment constitutes over **50% of the active labor force** (51.6% in 2021; OECD, 2024). 

Because informal transactions operate without formal administrative registration, municipal authorities (Greater Amman Municipality - GAM), urban economists, and social development agencies lack granular spatial intelligence detailing where informal economic vitality concentrates.

### Ethical Orientation & Intended End-Users
The analytical outputs of this BI framework are designed strictly for **constructive, non-punitive public policy applications**:
- Supporting GAM municipal planners in identifying spatial deficits in formal retail infrastructure, market stalls, and sanitary facilities.
- Guiding the Ministry of Social Development and NGO livelihood programs to target informal worker social safety nets, micro-finance, and vocational formalization incentives.
- Assisting urban transport authorities in integrating informal transit hubs with pedestrian micro-commerce.
*Academic Disclosure*: The model produces relative proxy estimates of spatial economic density, not legal, fiscal, or regulatory audit records. It must never be used for punitive code enforcement or regressive taxation targeting.

### Research Aim
To design, implement, and evaluate an end-to-end Business Intelligence (BI) framework that:
1. Ingests and harmonizes open geospatial indicators (OpenStreetMap micro-commerce, EOG VIIRS nocturnal radiance, WorldPop population, Overture Maps Places, and formal administrative records).
2. Deploys an econometrically grounded **Dual-Scale Discrepancy Model**:
   - **Micro Scale (H3 Hexagons)**: Standardized residual of observed economic activity unexplained by urban physical scale (commercial building footprints, ambient population, and urban form covariates).
   - **Macro Scale (GAM Districts or DoS Liwas)**: Discrepancy index benchmarking observed activity against registered commercial licenses (or census-enumerated establishments).
3. Delivers a high-contrast decision-support application featuring a **Dual-Mode 3D/2D Spatial Interface** (adapted from the God's Eye View architecture), equipped with dynamic multi-criteria sensitivity analysis, spatial diagnostics, and academic disclosures.

---

## 2. System Architecture & Repository Structure

The project is structured as a single unified repository partitioning the Python spatial pipeline from the analytical frontend application:

```
amman-shadow-economy-bi/
├── pipeline/                         # Python 3.10+ Spatial & Econometric Pipeline
│   ├── 01_tessellation.py            # H3 grid, urban masking & dynamic bounding box export
│   ├── 02_zonal_stats.py             # Raster extraction (WorldPop & EOG VIIRS)
│   ├── 03_osm_ingestion.py           # Filtered OSM extraction & 50% sparsity audit
│   ├── 03b_overture_ingestion.py     # Overture Places: sector share & digital footprint
│   ├── 03c_urban_form.py             # Building fabric, street network & anchor accessibility
│   ├── 04_econometrics.py            # OLS, VIF check, Moran's I & SEM inference
│   └── requirements.txt              # geopandas, h3, rasterio, statsmodels, spreg, esda, osmnx, overturemaps, scipy
├── dashboard/                        # Full-Stack BI Application (Dual-Engine: 3D Cesium / 2D MapLibre)
│   ├── server/                       # Node.js / Express analytical serving layer
│   │   ├── index.ts                  # API routes & in-memory caching
│   │   └── data/                     # Output artifacts generated by /pipeline
│   │       ├── amman_hexagons_res8.geojson
│   │       ├── amman_hexagons_res7.geojson
│   │       ├── amman_macro_boundaries.geojson
│   │       ├── amman_bounds.json     # Dynamic convex hull bounding box + 10% buffer
│   │       └── econometric_summary.json
│   ├── src/                          # Vite + React Analytical Frontend
│   │   ├── components/               # UI components with neutral, planning-oriented naming
│   │   │   ├── HeaderHUD.tsx         # Telemetry header: coordinates, elevation, active spec
│   │   │   ├── Viewport3D.tsx        # CesiumJS 3D extruded prism viewport (Amman-bounded)
│   │   │   ├── Viewport2D.tsx        # MapLibre GL JS 2D planar choropleth (Fallback & Thesis Export)
│   │   │   ├── ControlRail.tsx       # Specification selector & multi-residual weight sliders
│   │   │   ├── DiagnosticsCard.tsx   # Global Moran's I & SEM parameter readout
│   │   │   ├── PriorityNav.tsx       # Dynamic fly-to navigation for top empirical hotspots
│   │   │   ├── AreaInspector.tsx     # Selected hex profile & actual-vs-predicted scatterplot
│   │   │   └── AttributionFooter.tsx # Comprehensive open data & library legal citations
│   │   ├── config/
│   │   │   └── tokens.ts             # Verified tile provider tokens & fallback endpoints
│   │   ├── App.tsx                   # Main dashboard layout with 3D/2D mode switcher
│   │   └── index.css                 # Clean dark slate / translucent HUD styling
│   └── package.json
└── docs/                             # Academic thesis documentation & decision logs
    └── DECISIONS.md                  # Methodological assumptions & audit notes
```

---

## 3. Data Source Matrix, Provenance & Legal Compliance

| Source | Target Phenomenon | Spatial & Temporal Resolution | Pipeline & Ingestion | License, Attribution & Compliance | Cost | Limitations & Academic Defenses |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenStreetMap (Micro-Retail)** | Micro-commercial presence: kiosks, market stalls, open bazaars, informal repair clusters. | Point coordinates; 2024 snapshot | `/pipeline/03_osm_ingestion.py` with strict tag filters: `amenity=marketplace`, `shop=kiosk`, `stall=*`, `street_vendor=*`. | Open Database License (ODbL 1.0). Attribution required: *"© OpenStreetMap contributors"*. Bulk local caching permitted. | Free | **Zero-Inflation & Mapper Bias**: Tags like `stall=*` are sparse in Amman. *Defense*: Subject to **50% Go/No-Go gate**; if sparse, switch to binary presence indicator. |
| **VIIRS Day/Night Band (DNB)** | Anthropogenic nocturnal radiance, proxying nighttime economic vitality. | 500m $\times$ 500m grid; 2023 Annual Composite (VNL v2.2) | Earth Observation Group (EOG), Payne Institute. Extracted via HTTPS script from `eogdata.mines.edu`. | Open Access for Research with academic citation (Elvidge et al., 2021). Requires free EOG registration. | Free | **Radiance Blooming**: High-radiance commercial hubs spill light into adjacent streets. *Defense*: Modeled as intensive **zonal mean radiance** ($\text{nW}\cdot\text{cm}^{-2}\cdot\text{sr}^{-1}$); controlled by commercial footprint area. |
| **WorldPop Jordan** | High-resolution residential population distribution. | 100m $\times$ 100m grid; 2020 constrained raster (scaled to 2023) | Zonal sum extracted per H3 hexagon in `/pipeline/02_zonal_stats.py`. | Creative Commons Attribution 4.0 International (CC-BY 4.0). Attribution: *"WorldPop (www.worldpop.org)"*. | Free | **Sleeping vs. Daytime Population**: Low sleeping count in central commercial cores. *Defense*: Formulated **Dual Normalization** (Ambient Population incorporating commercial building area). |
| **GAM Registered Licenses (Primary Baseline)** | Formally licensed, inspected commercial enterprises. | 22 GAM Administrative Districts; 2023–2024 | Requested via official GJU letter to GAM GIS/Licensing. | Bilateral Academic Data Agreement (Not an open public dataset; subject to GAM approval). | Free | Potential administrative refusal or delay. *Defense*: Enters only if released; fallback to DoS 2018 census layer. |
| **Jordan DoS Economic Census (Fallback Baseline)** | Census-enumerated establishments and employment. | 9 Administrative Liwas of Amman; 2018 Census | Department of Statistics publications transcribed into structured JSON. | Non-commercial academic research use (Jordan Public Statistics). Attribution: *"Jordan Department of Statistics (DoS)"*. | Free | Broader administrative granularity. *Defense*: Formally relabeled as **"Activity-to-Establishment Ratio"**, descriptive only ($n = 9$). |
| **Overture Maps Places** | Micro-business presence, sector mix, and digital footprint (indicators I3–I4). | Point coordinates; quarterly release (record release ID) | `/pipeline/03b_overture_ingestion.py` using `overturemaps` Python client, clipped to Amman bounding box. | CDLA Permissive 2.0; Foursquare-sourced records Apache 2.0. Attribution: *"© Overture Maps Foundation"*. | Free | **Category Noise & Coverage**: Jordan coverage must be empirically audited. *Defense*: Empirical shrinkage, coverage gate, and exploratory flag on I4. |
| **OSM / Overture Buildings & Transit (Urban Form)** | Context covariates: small-footprint building share, intersection density, anchor accessibility (I5–I7). | Vector features; 2024 snapshot | `/pipeline/03c_urban_form.py` (`osmnx`, `geopandas`). | ODbL 1.0 for OSM-derived data. Attribution required. | Free | **Physical Context, Not Economic Trade**: Describes enabling conditions. *Defense*: Used exclusively as right-hand covariates in extended model. |
| **Satellite Base Imagery (Esri / CartoDB)** | Visual context for 3D/2D viewports. | Sub-meter imagery / vector tiles | Loaded in client: Esri World Imagery (ArcGIS Online REST service) or CartoDB Dark Matter. | **Terms of Service**: Non-commercial academic evaluation use. Mandatory visual attribution: *"Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"*. | Free Tier | Not downloaded in bulk; streamed as standard web map tiles strictly within viewport. |
| **3D Elevation / Terrain (Cesium Ion / OpenTopography)** | Topographic elevation mesh for 3D column anchoring. | 30m worldwide terrain | Client Cesium viewer initialized with `Cesium.createWorldTerrainAsync()`. | **Cesium Ion Terms**: Free personal academic token includes 50,000 monthly tile requests for non-commercial projects. Attribution: *"© Cesium"*. | Free Academic Tier | If token limit or network blocks occur, client gracefully falls back to flat ellipsoidal 3D or 2D MapLibre. |
| **Google Places API (Spot Verification Only)** | Commercial establishment verification for field audit sample hexes. | Point coordinates; On-demand live query | Node.js backend proxy. No bulk caching or persistent storage. | **Google Maps Platform Service Specific Terms (Section 5.4)**: Place IDs stored indefinitely; lat/lng cached up to 30 days. Other attributes not stored. | Free Tier per SKU | High digital-first formal bias. Used strictly for spot-checking sampled validation hexes. |

---

## 4. Methodological Framework: Dual-Scale Discrepancy Modeling

### A. Dual Normalization (Ambient / Effective Population)
To prevent commercial downtown cores from blowing up due to low sleeping populations:
$$\text{Ambient\_Pop}_h = \text{Res\_Pop}_h + \phi \cdot \left( \frac{A_{\text{comm}, h}}{\overline{A}_{\text{comm}}} \times \overline{\text{Res\_Pop}} \right)$$
Where $A_{\text{comm}, h}$ is total formal commercial building footprint area ($\text{m}^2$) from OSM building polygons. Baseline $\phi = 0.4$, subjected to parameter sensitivity testing ($\phi \in [0.1, 0.6]$).

---

### B. Micro Scale (H3 Hexagon Level): Unexplained Spatial Activity Index
Hexagons are generated over Amman and masked dynamically to the urban built-up extent in `/pipeline/01_tessellation.py` (yielding an empirical count $N_{\text{urban}}$ of urbanized hexagons).

At the hexagon level, formal registration counts do not natively exist. Spreading district numbers by commercial area creates mathematical collinearity. Therefore, the hexagon-level model measures **Activity Unexplained by Physical Scale**:

1. **Observed Activity Intensity ($Y_h$) & 50% Go/No-Go Gate**:
   - In `/pipeline/03_osm_ingestion.py`, compute the fraction of urban hexagons where $\text{OSM\_Vendors}_h = 0$.
   - **Gate Decision**:
     - *If zero-fraction $< 50\%$*: Compute continuous log-standardized composite:
       $$Y_h = \sum_{k \in \mathcal{K}} \alpha_k \cdot \text{Std}(f_k(\text{Ind}_{k,h})), \quad \alpha_k = \frac{1}{|\mathcal{K}|}$$
       For the two core indicators (OSM vendors and VIIRS radiance), $\alpha_{\text{osm}} = 0.50$ and $\alpha_{\text{viirs}} = 0.50$.
     - *If zero-fraction $\ge 50\%$*: Replace raw vendor count with a **binary presence/absence indicator** $\mathbb{I}(\text{OSM\_Vendors}_h > 0)$:
       $$Y_h = 0.40 \cdot \text{Std}(\mathbb{I}(\text{OSM\_Vendors}_h > 0)) + 0.60 \cdot \text{Std}(\log(\text{VIIRS\_MeanRadiance}_h + 1))$$
       (or rely exclusively on standardized log radiance if vendor presence is near-universally zero).

2. **Econometric Specification (OLS & SEM)**:
   $Y_h$ is regressed directly on the log-transformed scale controls:
   $$Y_h = \beta_0 + \beta_1 \log(\text{Ambient\_Pop}_h + 1) + \beta_2 \log(A_{\text{comm}, h} + 1) + \varepsilon_h$$
   - **VIF Check & Contingency**: Compute Variance Inflation Factors for $\log(\text{Ambient\_Pop} + 1)$ and $\log(A_{\text{comm}} + 1)$. If $\text{VIF} \ge 5$ (due to $A_{\text{comm}}$ being embedded in $\text{Ambient\_Pop}$), the regression automatically reverts to unadjusted residential census population:
     $$Y_h = \beta_0 + \beta_1 \log(\text{Res\_Pop}_h + 1) + \beta_2 \log(A_{\text{comm}, h} + 1) + \varepsilon_h$$
     breaking the structural correlation completely. The selected specification is programmatically recorded in `econometric_summary.json`, and **both specifications are reported side-by-side** in the thesis sensitivity table.

3. **Scoring via OLS Residual**:
   The hexagon score is computed from the **OLS residual $e_h$**:
   $$e_h = Y_h - \widehat{Y}_h$$
   $$SPI_h = \frac{e_h - \bar{e}}{\sigma_e}$$
   - **$SPI_h > 0$ (Priority Focus Areas)**: Hexagons exhibiting observed micro-retail and nocturnal radiance *significantly higher* than what urban population and commercial footprint predict.
   - **$SPI_h \approx 0$**: Activity closely conforms to expected physical infrastructure scale.
   - **$SPI_h < 0$ (Low Informal Presence)**: Areas with low observed informal activity relative to their built infrastructure.

4. **Role of the Spatial Error Model (SEM)**:
   - Compute Global Moran’s I on OLS residuals $e_h$. A significant $I$ ($p < 0.05$) diagnoses leftover spatial autocorrelation / neighborhood spillovers.
   - Estimate a **Spatial Error Model (SEM)** in Python (`spreg.GM_Error_Het`):
     $$Y_h = \mathbf{X}_h \boldsymbol{\beta} + u_h, \quad u_h = \lambda \mathbf{W} u_h + \epsilon_h$$
     Where $\mathbf{W}$ is the row-standardized H3 Queen contiguity weight matrix.
   - **Inference Rule**: The SEM is used **strictly for valid statistical inference on $\boldsymbol{\beta}$** (ensuring standard errors are not deflated by spatial clustering). The hexagon scores themselves remain based on the **OLS residual $e_h$**, preserving localized spatial clusters rather than stripping them away.

---

### C. Macro Scale: Formal Baseline Decision Tree

```
                       ┌──────────────────────────────────────────────┐
                       │          MACRO BASELINE DECISION TREE        │
                       └──────────────────────┬───────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
         [PATH A: GAM DATA GRANTED]                         [PATH B: GAM DATA STALLED]
         - 22 GAM Administrative Districts                  - 9 Administrative Liwas of Amman
         - Registered Commercial Licenses ($L_d$)           - DoS 2018 Economic Census Establishments ($E_l$)
         - Exploratory OLS Model ($n = 22$):                - Descriptive cross-tabulation ($n = 9$):
           $\text{Obs}_d = \gamma_0 + \gamma_1 L_d + \nu_d$    $\text{Ratio}_l = \text{Obs}_l / E_l$
         - Standardized Residual: $\nu_d / \sigma_\nu$      - Relabeled: "Activity-to-Establishment Ratio"
```

1. **Definition of Macro Observed Activity ($\text{Observed\_Activity}_m$)**:
   To prevent unit mixing, constituent metrics are standardized across macro units before averaging:
   $$\text{Observed\_Activity}_m = 0.50 \cdot \text{Std}\left(\sum_{h \in m} \text{OSM\_Vendors}_h\right) + 0.50 \cdot \text{Std}\left(\overline{\text{VIIRS\_MeanRadiance}}_m\right)$$
   *(If vendor tags are sparse, $\text{Observed\_Activity}_m = \text{Std}(\overline{\text{VIIRS\_MeanRadiance}}_m)$).*

2. **Path A (GAM 22 Districts - Exploratory Model)**:
   If GAM commercial license counts ($L_d$) are obtained:
   $$\text{Observed\_Activity}_d = \gamma_0 + \gamma_1 \cdot L_d + \gamma_2 \cdot \text{District\_Pop}_d + \nu_d \quad (n = 22)$$
   The standardized residual $\nu_d / \sigma_\nu$ is the **District Shadow Discrepancy Index**.

3. **Path B (DoS 9 Liwas - Descriptive Fallback)**:
   If GAM data stalls, aggregate observed indicators to the 9 Liwas and compare with the 2018 DoS Economic Census. Explicitly reported as an **"Activity-to-Establishment Ratio"**, descriptive only ($n = 9$), acknowledging that it reflects both informal presence and spatial data coverage rather than a true regulatory discrepancy.

---

### D. Interactive Multi-Residual Gap Model (Dashboard)
To eliminate double-counting and maintain consistency with the regression framework, the interactive dashboard evaluates independent univariate scale residuals using the exact predictor set $\mathbf{X}_{\text{scale}, h} = [\log(\text{Pop}_h + 1), \log(A_{\text{comm}, h} + 1)]$:
1. $\text{OSM\_Residual}_h = \log(\text{OSM\_Vendors}_h + 1) - \widehat{\log(\text{OSM\_Vendors}_h + 1)}(\mathbf{X}_{\text{scale}, h})$
2. $\text{VIIRS\_Residual}_h = \log(\text{VIIRS\_MeanRadiance}_h + 1) - \widehat{\log(\text{VIIRS\_MeanRadiance}_h + 1)}(\mathbf{X}_{\text{scale}, h})$
3. *(If I3 is retained)*: $\text{Sector\_Residual}_h = \tilde{s}_h - \widehat{\tilde{s}_h}(\mathbf{X}_{\text{scale}, h})$
4. *(If I4 is retained)*: $\text{Footprint\_Residual}_h = \tilde{d}_h - \widehat{\tilde{d}_h}(\mathbf{X}_{\text{scale}, h})$

The composite interactive gap score is:
$$SPI_h^{\text{gap}} = \sum_{k \in \mathcal{K}} w_k \cdot \text{MinMax}(\text{Residual}_{k, h}), \quad \sum_{k \in \mathcal{K}} w_k = 1.0$$
In the dashboard UI, each retained outcome indicator receives an interactive weight slider ($w_k$). Modifying sliders triggers instant client-side recalculation of $SPI_h^{\text{gap}}$, updating the 2D choropleth palette and 3D column heights in real time.

---

### E. Extended Indicator Framework (Tiered)

A single pair of indicators gives an incomplete picture. Adding indicators improves **robustness** only if each carries a distinct signal. Because no neighborhood-level ground truth exists, added indicators are judged by **ranking stability** (Leave-One-Indicator-Out) and **convergence** (independent signals agreeing), not by an ungrounded accuracy score.

#### E.1 Indicator Register
Expected sign means the expected theoretical relationship with informal activity after controlling for physical scale: `+` means a higher value is expected where informal activity is higher; `−` means lower.

| ID | Indicator | Role | Definition | Expected sign | Source | Feasibility |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| I1 | Micro-vendor density | Outcome (core) | Count of qualifying OSM features (`amenity=marketplace`, `shop=kiosk`, `stall=*`, `street_vendor=*`); subject to 50% gate | + | OSM | High |
| I2 | Night-time radiance | Outcome (core) | EOG VIIRS zonal mean radiance | + | EOG VNL v2.2 | High |
| I3 | Informal-prone sector share | Outcome | Shrunk share of POIs in informal-prone categories (auto/phone repair, small workshops, barbers, used goods, small grocers) | + | OSM + Overture | High |
| I4 | Micro-business digital footprint | Outcome (exploratory) | Shrunk share of places with a social page but no formal website or business phone | + | Overture Places | Medium |
| I5 | Small-footprint building share | Context covariate | Share of buildings under 100 m² (sensitivity at 75 and 150 m²) | + | OSM / Overture buildings | High |
| I6 | Street-network fine grain | Context covariate | Intersections per km² (`osmnx`) | + | OSM | High |
| I7 | Footfall-anchor accessibility | Context covariate | Negative log distance to nearest transit stop, market, mosque, or university | + | OSM | High |
| I8 | Built-up growth | Context layer (not scored) | Change in built-up area over time | n/a | Sentinel-2 / GHSL | Medium |
| I9 | Search interest | Macro or time only | Google Trends index for Arabic informal-work and second-hand terms | + | Google Trends | Medium |
| I10 | Formal-baseline ratio | Macro | Observed activity vs. GAM licenses or census establishments (Section 4.C) | − | GAM / DoS | Depends on release |

#### E.2 Role Separation: Outcomes vs. Context Covariates
- **Outcome indicators (I1–I4)** are direct traces of economic activity and enter the dependent variable $Y_h$.
- **Context covariates (I5–I7)** describe the physical built environment that enables street-level trade. Putting them in $Y_h$ creates endogeneity (confounding physical form with economic trade); therefore, they enter exclusively on the right-hand side of the *extended* specification.
- **I8–I10** are never scored at the hex level.

#### E.3 Pre-Registered Inclusion Rules
An indicator is retained in the econometric specifications only if all four conditions hold:
1. **Coverage**: At least 50% of urban hexagons contain non-zero or non-missing observations.
2. **Non-Redundancy**: Pairwise Spearman correlation $|r| < 0.80$ with every other retained indicator. If violated, drop the indicator with lower spatial coverage.
3. **Declared Sign**: Expected theoretical relationship must be recorded in `DECISIONS.md` prior to model estimation; counter-intuitive signs trigger collinearity diagnostics.
4. **License Verified**: Explicit compliance with open data terms (free redistribution, academic use) recorded in the provenance matrix.

#### E.4 Ratio Indicators: Empirical Bayes Shrinkage
For share indicators (I3, I4), low-count hexagons produce extreme ratio volatility. An empirical Bayes shrinkage formulation pulls sparse hexes toward the citywide mean:
$$\tilde{s}_h = \frac{x_h + m \cdot \bar{s}}{n_h + m}$$
where $x_h$ is the target category count in hexagon $h$, $n_h$ is total POIs in the hex, $\bar{s}$ is the unweighted citywide category share, and $m = 10$ pseudo-observations (subjected to sensitivity testing at $m \in \{5, 20\}$).

#### E.5 Primary and Extended Specifications
Let $\mathcal{K}$ be the set of retained outcome indicators among I1–I4. The 50% zero-inflation gate applies to every count-type outcome.

The composite dependent variable is strictly defined as:
$$Y_h = \sum_{k \in \mathcal{K}} \alpha_k \cdot \text{Std}(f_k(\text{Ind}_{k,h})), \quad \alpha_k = \frac{1}{|\mathcal{K}|}$$
where $f_k$ is the log transform for counts and radiance, and the shrunk share for I3–I4.

- **Primary Specification** (scale controls only):
  $$Y_h = \beta_0 + \beta_1 \log(\text{Pop}_h + 1) + \beta_2 \log(A_{\text{comm}, h} + 1) + \varepsilon_h$$
- **Extended Specification** (context-adjusted):
  $$Y_h = \beta_0 + \beta_1 \log(\text{Pop}_h + 1) + \beta_2 \log(A_{\text{comm}, h} + 1) + \gamma_1 \text{Std}(\text{I5}_h) + \gamma_2 \text{Std}(\text{I6}_h) + \gamma_3 \text{Std}(\text{I7}_h) + \varepsilon_h$$

Both specifications are reported side-by-side in the thesis. Hexagons that rank as priority areas under both models represent high-confidence findings. The Spearman rank correlation between the two residual vectors ($\rho_{\text{specs}}$) is reported as an explicit robustness statistic.

#### E.6 Weight Sensitivity & Dirichlet Simulation
To verify that residual rankings are not an artifact of arbitrary equal weights ($\alpha_k = 1/|\mathcal{K}|$):
1. **Equal Weights (Baseline)**: $\alpha_k = 1/|\mathcal{K}|$.
2. **Core-Heavy Weighting**: Core indicators (I1, I2) receive a combined 60% of total weight, while secondary outcomes (I3, I4) share the remaining 40%.
3. **Dirichlet Monte Carlo Simulation**: Draw 1,000 random weight vectors from a uniform Dirichlet distribution $\boldsymbol{\alpha}^{(s)} \sim \text{Dir}(\mathbf{1}_{|\mathcal{K}|})$. Re-estimate $Y_h^{(s)}$ and compute the OLS residual rank vector for each iteration.
4. Report each hexagon's median rank along with its 5th-to-95th percentile rank confidence interval.

#### E.7 Execution Priority Order
If data ingestion timelines compress, implement indicators strictly in this order:
$$\text{I3 (Sector Share)} \longrightarrow \text{I7 (Anchor Accessibility)} \longrightarrow \text{I5 (Small Footprints)} \longrightarrow \text{I6 (Street Density)} \longrightarrow \text{I4 (Digital Footprint)}$$
Indicators I8–I10 are purely contextual/macro and can be omitted without altering the core micro-econometric model. Google Places is restricted exclusively to spot-checking field audit hexes to respect caching terms.

---

## 5. Sensitivity, Scale (MAUP) & Empirical Validation

### A. Leave-One-Indicator-Out (LOIO) Sensitivity for Regression
To test whether any single observed indicator dictates the econometric rankings:
1. Re-estimate OLS dropping one retained outcome indicator at a time; extract residual rank vectors $R_h^{(-k)}$.
2. Compute **Spearman Rank Correlation ($\rho_k$)** using `scipy.stats.spearmanr` (with fractional tied rank correction). A value of $\rho_k \ge 0.80$ confirms ranking stability.

### B. MAUP Scale Sensitivity Test (Resolution 8 vs. Resolution 7)
Computes the cross-resolution Spearman rank correlation (`scipy.stats.spearmanr`) between:
- **H3 Resolution 8** ($\sim 0.74\text{ km}^2$, dynamic urban mask)
- **H3 Resolution 7** ($\sim 5.16\text{ km}^2$, dynamic urban mask)
Reporting the empirical scale effect fulfills academic rigor regarding the Modifiable Areal Unit Problem.

### C. Parameter Sensitivity ($\phi$ Ambient Weight)
Evaluates ranking shifts as $\phi$ varies across $\{0.1, 0.2, 0.4, 0.6\}$. If downtown ranking remains stable across the range, the ambient population specification is robust.

### D. Unbiased Stratified Random Field Audit
1. **Sampling Strategy**: Partition all urban hexagons into 3 model-predicted score terciles (High, Medium, Low). Draw **3 hexagons at random** from each stratum ($N = 9$).
2. **Controlled Audit Conditions**:
   - 45-minute pedestrian transect along the primary commercial street in each sampled hexagon (or busiest thoroughfare in low-tercile areas).
   - Uniform peak hours (Wednesday or Thursday, 16:00–18:00).
   - Count visible informal street stalls, mobile carts, unlicensed kiosks, and cash-only pavement displays.
3. **Statistical Power**: Evaluated via `scipy.stats.spearmanr` against predicted ranks. Two-tailed critical value for $\alpha = 0.05, N = 9$ is **$r_{s, \text{crit}} = 0.700$**.

---

## 6. Comprehensive 8-Week Graduation Project Roadmap

```
WEEK 1: Foundation, Codebase Audit & Literature Inception
├── Codebase Audit (1 hour): Clone bilawalsidhu/gods-eye-view; inspect package.json, src/data/ layer
│   modules (flights.js, vessels.js, cctv.js), Cesium Viewer mount, and verify required tokens.
├── Literature Review initiated: Medina & Schneider (2018), OECD (2024), Schneider (2015)
├── Official GJU letter submitted to GAM for 22-district commercial license data
├── Draft GJU Research Ethics Statement (confirming non-punitive, planning-support use)
├── Download DoS 2018 Economic Census Liwa tables (Fallback preparation)
└── Milestone 1 Defense Check: Econometric specification & baseline decision tree approved.

WEEK 2: Spatial Tessellation, Urban Masking & Raster Ingestion (/pipeline)
├── Script 01_tessellation.py: Generate H3 Hexagons (Res 7 & 8) dynamically clipped to urban fabric
│   (Export amman_bounds.json: convex hull of urban hex extent + 10% spatial buffer)
├── Ingest official GAM 22 District and 9 DoS Liwa boundary GeoJSON
├── Script 02_zonal_stats.py: Zonal extraction of WorldPop 100m raster (Ambient Population denominator)
├── Script 02_zonal_stats.py: Zonal extraction of EOG VIIRS VNL v2.2 (2023) mean radiance
└── Thesis Drafting: Draft Chapter 1 (Introduction, Ethical Framework & Research Aims).

WEEK 3: OSM Sparsity Audit, Overture Ingestion & Econometric Modeling (/pipeline)
├── Script 03_osm_ingestion.py: Query Amman informal tags (`amenity=marketplace`, `shop=kiosk`, etc.)
├── Script 03b_overture_ingestion.py: Overture Places for I3 (sector share) and I4 (digital footprint)
├── Script 03c_urban_form.py: I5 small-footprint share, I6 intersection density, I7 anchor accessibility
├── Extract formal commercial building footprints (`building=commercial|retail|office`)
├── DECISION GATE (50% Sparsity Gate): Evaluate zero-fraction; select continuous vs binary indicator.
├── DECISION GATE: Check GAM license status. If delayed/denied, activate DoS Fallback.
├── Script 04_econometrics.py:
│   - Log-log OLS & VIF verification (revert to Res_Pop if VIF >= 5; record both specs)
│   - Estimate Primary vs Extended Specifications; extract OLS residuals e_h
│   - Run Dirichlet weight simulation (1,000 draws) and LOIO sensitivity audit
│   - Permutation Moran's I diagnostic test on residuals (esda)
│   - Spatial Error Model (SEM) for valid coefficient inference
│   - Macro Model (22-district exploratory OLS or 9-Liwa descriptive ratio)
├── Export tidy GeoJSON, bounding box, and summary JSON to `/dashboard/server/data/`
└── Thesis Drafting: Draft Chapter 2 (Literature Review, Institutional Context & Data Sources).

WEEK 4: Analytical Serving Layer, GEV Fork & WEEK 4 GO/NO-GO GATE (/dashboard)
├── Configure Node.js / Express backend with in-memory caching and REST endpoints
├── Fork/Clone God's Eye View (GEV) React 3D repository into `/dashboard`
├── PURGE UNNECESSARY MODULES:
│   - Delete live commercial ADS-B flight tracker & military aircraft modules
│   - Delete AIS maritime vessel tracker, public CCTV camera feeds, and earthquake feeds
│   - Delete missile launch trajectories and squawk alert listeners
├── CONFIGURE AMMAN BOUNDS:
│   - Load amman_bounds.json (convex hull + 10% padding); lock camera to Amman extent
│   - Initialize Cesium World Terrain (with free academic token) or CartoDB/Esri raster tiles
├── WEEK 4 GO/NO-GO GATE (Friday, 18:00):
│   - Test H3 hexagon rendering performance over Amman 3D terrain.
│   - IF Cesium 3D fork renders smoothly without WebGL crashes: Proceed with 3D/2D dual interface.
│   - IF Cesium 3D fork exhibits rendering bugs, token blocks, or performance stalls:
│     IMMEDIATELY EXECUTE 2D FALLBACK (Deploy MapLibre GL JS 2D vector choropleth as primary viewport).
└── Thesis Drafting: Draft Chapter 3 (Methodology & Spatial Econometric Formulation).

WEEK 5: Dashboard MVP & Dual-Mode 3D/2D Viewport Implementation (/dashboard/src)
├── Implement Dashboard MVP:
│   - Primary Viewport: Amman 3D extruded H3 hexagonal prisms on terrain OR MapLibre 2D choropleth
│   - Viewport Toggle: One-click switch between 3D Oblique View and 2D Planar Orthographic View
│   - Jenks natural break color palette with neutral planning labels
│   - Bivariate encoding: 3D height encodes residual z_h; color encodes specification consensus
│   - Dynamic Priority Navigation: Fly-to buttons generated from top empirical model hexes
│   - Control Rail: Dynamic multi-residual weight sliders with instant recalculation
│   - Spatial Diagnostics Card: Global Moran's I readout and SEM parameter table
│   - Mandatory Attribution Footer: Permanent credits for OSM, WorldPop, EOG, Overture, Cesium, Esri
│   - Prominent academic disclosure: "PLANNING PROXY ESTIMATE · NOT A DIRECT MEASUREMENT"
└── Thesis Drafting: Synthesize Chapter 3 figures, methodology flowcharts, and 2D/3D map plates.

WEEK 6: Unbiased Stratified Field Validation Audit & Dashboard Extensions
├── Conduct standardized 45-minute pedestrian field audits in 9 randomly sampled hexes
│   (3 High, 3 Medium, 3 Low score terciles) during peak Wednesday/Thursday hours
├── Log informal vendor counts, mobile carts, and pavement displays
├── Calculate descriptive Spearman rank correlation (scipy.stats.spearmanr, critical cutoff: 0.700)
├── Implement Dashboard Extensions:
│   - Area Inspector drawer: Selected hex profile & actual-vs-predicted scatterplot
│   - LOIO sensitivity stability gauge & MAUP cross-resolution comparison
└── Thesis Drafting: Draft Chapter 4 (Empirical Findings & Econometric Results).

WEEK 7: Usability Testing, Academic Polish & Thesis Finalization
├── Conduct peer/advisor usability evaluation of the planning decision-support interface
├── Export publication-quality 2D orthographic choropleths and 3D oblique views for thesis report
├── Write Chapter 5 (Discussion, Limitations, Policy Recommendations for GAM, and Ethics)
└── Advisor Review: Submit complete thesis draft for supervisory feedback.

WEEK 8: Thesis Defense Rehearsal & Final Deliverables Package
├── Final audit of data provenance, attributions (OSM ODbL, EOG VIIRS, WorldPop, Overture, Cesium, Esri)
├── Finalize graduation thesis report and defense slide deck
├── Rehearse defense responses:
│   - Why decouple hex scale from district formal baseline? (collinearity resolution)
│   - Why use OLS residuals for scoring and SEM for inference?
│   - How the 2D/3D dual interface supports infrastructure planning without perspective bias
└── Deliverable frozen: Interactive 3D/2D Spatial BI Dashboard & Reproducible Python Spatial Pipeline.
```

---

## 7. Frontend Interface & Dual-Mode Visual Design Architecture

### A. Architectural Concept: Turning God's Eye View into a Municipal Planning Console
The dashboard adapts the high-contrast aesthetic and 3D rendering pipeline of the open-source **God's Eye View (GEV)** application. Rather than tracking planetary military assets, it is repurposed into an **Urban Planning & Economic Support Console** dedicated strictly to Greater Amman Municipality.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [● URBAN PLANNING CONSOLE]  AMMAN SHADOW ECONOMY PROXY   31°57'N 35°56'E · ELEV: 890m │
├─────────────────┬───────────────────────────────────────────────────┬──────────────────┤
│ MODEL CONTROLS  │     VIEWPORT: [3D Topographic] / [2D Planar Map]  │  AREA INSPECTOR  │
│                 │                                                   │                  │
│ [Spec Selector] │  • Dynamic Amman Extent (Bounds Hull + 10% Pad)   │ Zone: Downtown   │
│  ◉ Primary OLS  │  • 3D Extruded H3 Columns (Height = Residual z)   │ Hex: 882ea46...  │
│  ○ Extended     │  • Dual-Encoding: Height = z_h; Color = Consensus │                  │
│                 │                                                   │ Pop: 42,100      │
│ [Weight Sliders]│   [PRIORITY AREA QUICK-ZOOM (DYNAMIC EMPIRICAL)]  │ Comm Area: 18.2k │
│  OSM:   [====]  │   [Rank 1: Al-Balad] [Rank 2: Sweileh] [Rank 3...]│ Residual: +2.41σ │
│  VIIRS: [====]  │                                                   │                  │
│  Sector:[====]  │                                                   │ [Actual vs Pred] │
│                 │                                                   │    *  /          │
│ [Diagnostics]   │                                                   │   / *            │
│  Moran's I: *   │                                                   │  /               │
│  p-value:   *   │                                                   │                  │
├─────────────────┴───────────────────────────────────────────────────┴──────────────────┤
│ DATA ATTRIBUTION: © OpenStreetMap · WorldPop · EOG VIIRS · Overture Maps · Cesium · Esri│
└────────────────────────────────────────────────────────────────────────────────────────┘
* ILLUSTRATIVE MOCK-UP ONLY — SYNTHETIC VALUES FOR INTERFACE PROTOTYPING
```

### B. What Is Purged from the Standard God's Eye View Build
To eliminate clutter and focus exclusively on Amman's urban economy, the following GEV modules are stripped:
1. **Commercial & Military Aviation Tracking**: All ADS-B plane listeners (`flights.js`), flight telemetry, and military aircraft radar layers are deleted.
2. **Maritime & Naval Tracking**: AIS vessel trackers (`vessels.js`) and port feeds are removed.
3. **Public CCTV & Surveillance Cameras**: External traffic camera feeds (`cctv.js`) and RTSP video streams are removed.
4. **Planetary Disasters & Geophysics**: Global earthquake seismographs (`earthquakes.js`), active wildfire perimeters, and rocket launch trajectories are deleted.
5. **Emergency Radio & Squawks**: Emergency transponder squawk listeners and audio feeds are disabled.

### C. What Is Added & Scoped Strictly to Amman
1. **Dynamic Spatial Bounding & Camera Constraint**:
   - Camera bounds are not hard-coded; they are dynamically loaded from `amman_bounds.json`, generated during tessellation as the convex hull bounding box of the urban hexagon extent plus a **10% spatial buffer**:
     $$\text{Lat} \in [\text{MinLat} - \Delta_{\text{lat}}, \text{MaxLat} + \Delta_{\text{lat}}], \quad \text{Lng} \in [\text{MinLng} - \Delta_{\text{lng}}, \text{MaxLng} + \Delta_{\text{lng}}]$$
     This guarantees that eastern and southern fringes (such as Sahab, Al-Jizah, and Marka) are never clipped.
   - Camera minimum altitude locked to $200\text{ m}$ (street-level overview) and maximum altitude locked to $25\text{ km}$ (metropolitan overview), preventing zooming out to a planetary globe.
2. **Dual-Mode Viewport: 3D Topographic vs. 2D Planar Orthographic Toggle**:
   - **3D Oblique View**: H3 hexagonal cells are rendered as vertical polygonal columns rising from Amman's 3D terrain elevation mesh. Height is proportional to the OLS residual score ($z_h$), scaling from $50\text{ m}$ to $600\text{ m}$.
   - **2D Planar View (Mandatory)**: A top-down, distortion-free orthographic choropleth. This solves the cartographic limitation of 3D extrusions (where steep hills hide neighboring columns) and provides publication-ready figures for the academic thesis.
3. **Visual Encoding & Uncertainty Separation**:
   - To avoid redundant encoding (where height and color both represent the same single variable), the interface supports **bivariate visual encoding**:
     - In 3D: Column **height** represents the point estimate ($z_h$), while column **color** represents estimation consensus across Primary vs. Extended specifications (or standard error $\text{SE}(e_h)$).
     - In 2D: Planar choropleth uses a 5-class Jenks natural break palette (Charcoal `#1E293B` $\rightarrow$ Amber Gold `#F59E0B` $\rightarrow$ High-Priority Red `#EF4444`).
4. **Neutral, Planning-Oriented UI Language**:
   - Replaces adversarial or military phrasing with constructive planning terms:
     - *"Target Inspector"* $\longrightarrow$ **Area Inspector Drawer**
     - *"Hotspot Target Fly-To"* $\longrightarrow$ **Priority Area Quick-Zoom**
     - *"Military-tactical HUD"* $\longrightarrow$ **High-Contrast Spatial Console**
     - User persona defined as **municipal planners, infrastructure engineers, and informal livelihood support programs** (strictly non-punitive).
5. **Dynamic Priority Navigation (Empirically Generated)**:
   - Quick-zoom buttons are not based on prior geographic assumptions. They are generated dynamically from the **top 5 highest-residual hexagons** produced by `04_econometrics.py`, with neighborhood names assigned via spatial join with official GAM district boundaries.
6. **Mandatory Legal Attribution Footer**:
   - Permanent, legible footer rendered on all viewports:
     `© OpenStreetMap contributors (ODbL) · WorldPop (CC-BY 4.0) · EOG VIIRS (Payne Institute) · Overture Maps Foundation (CDLA Permissive 2.0 / Apache 2.0) · CesiumJS / Cesium Ion · Esri / CartoDB`
