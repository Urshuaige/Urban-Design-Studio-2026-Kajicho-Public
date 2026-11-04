# Official brief Figure 5

Current Mapping follows the **two outlines in the official Theme B brief, page 4, Figure 5**. Both appear in the same view on every theme.

| Source line | Meaning | Registered area | Building model objects | OSM destinations |
| --- | --- | ---: | ---: | ---: |
| Solid black（黑实线） | Kajicho 1 & 2 primary area | 10.70383 ha | 277 | 178 |
| Dashed black（黑虚线） | Kanda–Nihonbashi approximate secondary area | 41.98967 ha | 1,074 | 353 |

The primary area is nested within the wider area. Its counts are a subset, so do not add the two columns together. Poster, historical census-core and inferred street-block outlines are excluded from current Mapping.

## Source fidelity and precision

The original page-4 map is 917 × 1495 pixels. The 12 primary and 22 secondary source-pixel vertices reproduce the stored affine transform exactly. The original PDF and visible bends were independently checked. Six road-intersection controls give RMSE 7.43 m, maximum residual 12.40 m and maximum leave-one-control-out error 20.17 m. A **25 m screening band（制图筛查带）** reports membership sensitivity; it is not a confidence interval.

These are registered source-stroke traces, not course-supplied cadastral GIS. The wider caption explicitly says “Approximate Secondary Area”. Neither line is moved to retain buildings, follow a railway branch, close whole blocks or meet a historical count.

A building enters analysis only when the source outline covers its full original footprint (covers). No footprint is clipped and no boundary is moved to retain it. Crossing and exterior objects remain pale grey context in every map. Analysis counts are **1,074 wider / 277 primary**, with **zero selected crossings or exterior objects**. The northern mixed-use model has 43.65% of its footprint outside the wider trace and is excluded. The raw wider pool still records 22 crossing PLATEAU projections for source review. Footprint coverage is the union of admitted full footprints divided by the selected area.

## Files

- [Portable QGIS project](../05_QGIS/Projects/Kanda_Nihonbashi_Study_2026-10-18.qgz): 20 spatial layers and one membership table; saved and read with QGIS 3.44.12.
- [GeoPackage](../04_Data/Ready/Study_Area_2026-10-18/Kanda_Nihonbashi_Study.gpkg): full source records, two source-outline layers, classified POIs and membership flags.
- Analysis layers: analysis_buildings_wider and analysis_buildings_primary. The raw buildings layer is context. [Excluded-building audit](../06_Outputs/Study_Area_2026-10-18/tables/excluded_buildings.csv) records source IDs, scope and outside area.
- [Source traces and controls](../06_Outputs/Study_Area_2026-10-18/study_boundary_6677.geojson), [statistics](../06_Outputs/Study_Area_2026-10-18/statistics.json), [tables](../06_Outputs/Study_Area_2026-10-18/tables), [POI reading](../06_Outputs/Study_Area_2026-10-18/poi_semantics.json), [quality checks](../06_Outputs/Study_Area_2026-10-18/quality_checks.json).
- [Source review](Study_Boundary_Source_Review_2026-10-18.md) and [simulation update plan](Simulation_Scope_Plan_2026-10-18.md).

All ten map exports are PNG: one overview and nine themes, including POI functions. Web previews are JPEG with native readable legends. No SVG maps or new CFD runs were generated.

Source: [Official Theme B brief, p.4 Figure 5](https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view). The figure’s English “Higashi-Nihonbashi” caption conflicts with its underlying Shin-Nihonbashi map location; current station coordinates follow the source station records. JR Kanda and Ginza Line Kanda remain separate.

