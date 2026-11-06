# Research Ethics, Intended Use & Methodological Disclosures
**Project**: A Business Intelligence Framework for Estimating Neighborhood-Level Shadow Economy Activity in Amman Using Open Geospatial Data  
**Author / Department**: Department of Business Analytics, German Jordanian University (GJU)  
**Audience**: Academic Reviewers, Municipal Planners & Policy Stakeholders  

---

## 1. Intended Purpose & Ethical Orientation

The primary objective of this Business Intelligence (BI) framework is to provide municipal decision-makers, social protection planners, and urban researchers with granular spatial intelligence regarding the distribution of informal and unrecorded economic vitality across Amman.

### Ethical Commitments:
1. **Supportive, Non-Punitive Municipal Planning**:
   - The framework is designed to inform **affirmative urban policy**: identifying where municipal authorities (Greater Amman Municipality - GAM) can provide legal street vending infrastructure, organized municipal souqs, public sanitation facilities, waste management, and sidewalk widening.
   - It is intended to guide micro-credit, business formalization incentives, and social safety net enrollment (such as Social Security Corporation coverage for informal workers), as advocated by international labor and development organizations (OECD, 2024; World Bank).
2. **Strict Prohibition Against Punitive Targeting**:
   - The analytical outputs and hotspot maps **must not** be utilized by municipal inspection teams or security authorities as targeting mechanisms for punitive crackdowns, arbitrary confiscation of informal goods, aggressive evictions, or regressive micro-taxation of vulnerable informal workers.
3. **Protection of Neighborhood Dignity & Non-Stigmatization**:
   - Informal economic activity in Jordan represents a vital survival mechanism and socio-economic buffer absorbing over 50% of the active labor force. 
   - High informal presence indicates unmet economic demand, pedestrian vitality, and entrepreneurial resilience—not criminality or civic decay. Terminology throughout this project deliberately avoids stigmatizing or carceral phrasing.

---

## 2. Methodological Disclosures & Epistemic Limitations

1. **Proxy Estimation, Not Direct Measurement**:
   - The indices produced by this framework are **econometrically derived spatial proxies** based on open geospatial indicators (nocturnal light anomalies, micro-vendor OpenStreetMap tags, building footprints, and sector compositions).
   - They do **not** constitute an exhaustive, verified census of informal business entities or exact shadow economy GDP transactions.
2. **Digital Divide & Open Data Coverage Asymmetry**:
   - OpenStreetMap (OSM) and digital point-of-interest databases exhibit spatial contributor bias. Affluent commercial areas in West Amman often feature higher digital mapping completeness than peripheral or dense residential communities in East Amman.
   - The model addresses this through the **50% Zero-Inflation Gate**, **Empirical Bayes Shrinkage**, and scale controls, but residual mapper bias remains an inherent epistemic limitation of open volunteer geographic information (VGI).
3. **Bilateral Baseline Reliance**:
   - If official district-level GAM commercial license counts are delayed or restricted, the macro model relies upon the 2018 Department of Statistics (DoS) Economic Census, which is explicitly labeled as an **Activity-to-Establishment Ratio** rather than a true regulatory discrepancy.
