# God's Eye View (GEV) Codebase Audit & Architectural Extraction
**Audit Target**: `bilawalsidhu/gods-eye-view` (Cloned snapshot, November 2026)  
**Location**: `/dashboard/archive_gev`  
**Auditor**: GJU Business Analytics Graduation Project Team  
**Date**: November 6, 2026  

---

## 1. Executive Findings: Framework & Core Runtimes

1. **Frontend Engine**:
   - The original GEV repository is **Vue 3 (`^3.5.44`) + Pinia (`^2.3.1`) + Vite (`^6.4.4`)**, with CesiumJS (`cesium ^1.124.0`, `vite-plugin-cesium ^1.2.23`).
   - *Node Engine Requirement*: The `package.json` specifies `"node": ">=24.14.0 <25 || >=26 <27"`. Attempting to run the full un-pruned GEV project out-of-the-box requires a modern Node 24+ environment and heavy dependencies (`@jtarrio/webrtlsdr`, `puppeteer`, `sharp`, `mapillary-js`).
   - *Architectural Recommendation*: Rather than wrestling with GEV's full 137k-line dependency tree, our dashboard can directly **cherry-pick the Cesium viewer configuration, shader styling, and camera controller** while running a clean, lightweight analytical dashboard.

2. **Tile & Terrain Provider Architecture (Zero-Key Discoveries)**:
   - **Keyless Terrain**: In `src/maps/terrain.js`, GEV already implements a **keyless terrain provider**:
     `KEYLESS_TERRAIN_URL = 'https://terrain.reearth.land/cesium-mesh/ellipsoid'` (Re:Earth / Mapterhorn quantized mesh, CC BY 4.0). It gracefully falls back to `Cesium.EllipsoidTerrainProvider()`.
   - **Keyless Satellite Imagery**: In `src/maps/defaultSources.js`, GEV defaults to `esri-imagery` (`createEsriImagery` via ArcGIS Online tile endpoint) with an automatic fallback to `osm` (`createOsmImagery`).
   - **Google Photorealistic 3D Tiles**: Only activated if a `googleApiKey` or Google 3D Tileset is explicitly provided (`src/maps/google3d.js`).
   - *Conclusion*: **We can run 3D satellite imagery and terrain over Amman without requiring any paid tokens or Google Maps keys!**

3. **Data Layer Decoupling**:
   - Every external planetary layer is completely isolated in `src/layers/`:
     - `src/layers/flights/`: OpenSky / adsb.lol aircraft tracking.
     - `src/layers/military/`: Military transponder tracking.
     - `src/layers/vessels/`: AISStream maritime vessel tracking.
     - `src/layers/cctv/`: Traffic cameras and RTSP streams.
     - `src/layers/earthquakes/`: USGS seismograph feeds.
     - `src/layers/satellites/`: Space-track TLE orbital elements.
     - `src/layers/launches/`: Rocket launch telemetry.
   - *Purge Action*: These directories are completely self-contained and can be excised without breaking the Cesium camera or base terrain renderer.

---

## 2. Adaptation Blueprint for Amman Shadow Economy BI

1. **Bounding & Frustum Restraint**:
   - Instead of initializing a full planetary globe in `src/app/viewer.js`, initialize camera destination with:
     ```javascript
     viewer.camera.flyTo({
       destination: Cesium.Rectangle.fromDegrees(minLng, minLat, maxLng, maxLat),
       orientation: {
         pitch: Cesium.Math.toRadians(-45.0),
         heading: Cesium.Math.toRadians(0.0),
         roll: 0.0
       }
     });
     ```
   - Restrict maximum zoom distance: `viewer.scene.screenSpaceCameraController.maximumZoomDistance = 35000;` (35 km, strictly metropolitan scale).

2. **H3 Extruded Polygon Ingestion**:
   - Create a clean custom layer: `src/layers/amman_shadow_economy/index.js`.
   - Ingest `amman_hexagons_res8.geojson` via `Cesium.GeoJsonDataSource.load()`.
   - Extrude each polygon dynamically using the `extrudedHeight` property:
     ```javascript
     entity.polygon.extrudedHeight = Math.max(50, (entity.properties.residual_z.getValue() + 3) * 100);
     entity.polygon.material = getChoroplethColor(entity.properties.residual_z.getValue());
     ```

3. **Week 4 Go/No-Go Contingency**:
   - If Cesium setup experiences any WebGL shader compatibility issues on the target browser, the `amman_hexagons_res8.geojson` artifact is already 100% compatible with MapLibre GL JS (`fill-color` / `fill-extrusion`).
