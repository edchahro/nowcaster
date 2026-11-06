# Academic Decision Register & Pre-Registration Log
**Project Title**: A Business Intelligence Framework for Estimating Neighborhood-Level Shadow Economy Activity in Amman Using Open Geospatial Data  
**Institution**: German Jordanian University (GJU) — Department of Business Analytics  
**Date**: November 2026  

---

## 1. Pre-Registered Econometric Hypotheses & Expected Signs

Before running spatial regressions on Amman's urban hexagons, the expected theoretical signs for all candidate indicators are formally pre-registered to prevent p-hacking and exploratory bias:

| ID | Indicator Name | Role | Operationalization | Expected Theoretical Sign ($\beta$) | Economic & Spatial Justification |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **I1** | Micro-vendor density | Outcome (Core) | $\log(1 + \text{OSM\_Vendors}_h)$ | **$+$** | Direct physical traces of informal sidewalk peddling, stalls, and open kiosks. |
| **I2** | Nocturnal radiance | Outcome (Core) | $\log(1 + \text{VIIRS\_MeanRadiance}_h)$ | **$+$** | Night-time economic and social vitality unaccounted for by formal daytime offices. |
| **I3** | Informal-prone sector share | Outcome | Shrunk POI share: vehicle/phone repair, small crafts, barbers, small grocers | **$+$** | Sectors dominated by high cash transactions, sole proprietorships, and informal apprenticeships in Jordan. |
| **I4** | Micro-business digital footprint | Outcome (Exploratory) | Shrunk share of POIs with social presence but no formal website/phone | **$+$** | Informal home-based or social-commerce enterprises operating outside commercial registries. |
| **I5** | Small-footprint building share | Context Covariate | Proportion of buildings with footprint $< 100\text{ m}^2$ | **$+$** | Fine-grained, vernacular urban fabric offering affordable micro-scale commercial frontage. |
| **I6** | Street-network fine grain | Context Covariate | Pedestrian intersection density ($\text{intersections}/\text{km}^2$) | **$+$** | High street connectivity and permeability creating pedestrian footfall necessary for curb trade. |
| **I7** | Footfall-anchor accessibility | Context Covariate | $-\log(1 + \text{Distance to transit/market/mosque/campus})$ | **$+$** | Proximity to public transit nodes and civic anchors generates captive pedestrian flows for informal micro-retailers. |

---

## 2. Pre-Declared Methodological Rules & Inclusion Gates

1. **50% Zero-Inflation Go/No-Go Gate (OSM Micro-Vendors)**:
   - If $\ge 50\%$ of urban hexagons contain zero qualifying vendor features (`stall=*`, `street_vendor=*`, `shop=kiosk`, `amenity=marketplace`), continuous vendor count is replaced with a **binary Presence/Absence indicator** ($\mathbb{I}(\text{Vendors}_h > 0)$).
   - If near-universally zero ($> 90\%$), vendor counts are relegated exclusively to the macro district scale, and micro-hexes rely on continuous VIIRS radiance and Overture sector shares.

2. **Multicollinearity & VIF Rule**:
   - Variance Inflation Factor threshold is strictly set to **$\text{VIF} < 5.0$**.
   - If $\log(\text{Ambient\_Pop} + 1)$ exhibits $\text{VIF} \ge 5.0$ due to commercial building area ($A_{\text{comm}}$) collinearity, the model automatically reverts to unadjusted residential census population ($\text{Res\_Pop}$). Both models are reported side-by-side in the thesis.

3. **Empirical Bayes Shrinkage for Shares (I3 & I4)**:
   - To eliminate extreme ratio volatility in low-POI hexagons, shrinkage is fixed at:
     $$\tilde{s}_h = \frac{x_h + m \cdot \bar{s}}{n_h + m}, \quad m = 10$$
   - Sensitivity audited at $m = 5$ and $m = 20$.

4. **Inference vs. Scoring Rule**:
   - **Hexagon residual scores ($SPI_h$)** are derived exclusively from the **OLS residual ($e_h$)** to preserve localized informal clusters and spatial hotspots.
   - The **Spatial Error Model (SEM)** is used exclusively for **valid parameter and standard error inference**, ensuring standard errors are not deflated by spatial autocorrelation.

5. **Weight Sensitivity Pre-Registration**:
   - Baseline weights: Equal shares $\alpha_k = 1/|\mathcal{K}|$.
   - Robustness audited against:
     - Core-heavy weighting (60% to I1 & I2; 40% to secondary outcomes).
     - 1,000 Dirichlet Monte Carlo simulations $\boldsymbol{\alpha}^{(s)} \sim \text{Dir}(\mathbf{1}_{|\mathcal{K}|})$, reporting median rank and 5th–95th percentile confidence intervals.

6. **Week 4 Dashboard Go/No-Go Fallback Gate**:
   - If the Cesium 3D GEV fork does not render H3 hexagons over Amman's terrain smoothly without WebGL crashes by Friday of Week 4, the primary dashboard viewport automatically falls back to **2D MapLibre GL JS vector choropleth**.
