# Data guide

Use the [official Figure 5 scopes](COURSE_BOUNDARIES.md): solid primary **10.70383 ha / 277 model objects**, dashed approximate wider **41.98967 ha / 1,074 objects**. Both share one Mapping view.

Open [Kanda_Nihonbashi_Study_2026-10-18.qgz](../05_QGIS/Projects/Kanda_Nihonbashi_Study_2026-10-18.qgz), keeping the folder tree intact. It contains **20 spatial layers and one membership attribute table**, saved and provider-read with QGIS 3.44.12. Use one editor per shared project/GeoPackage.

| Layer or file | Read it as |
| --- | --- |
| study_area | Figure 5 dashed approximate secondary trace |
| primary_brief | Figure 5 solid primary trace |
| analysis_buildings_wider / analysis_buildings_primary | Physical analysis subsets: 1,074 / 277 full footprints, strict containment, original IDs and attributes |
| study_membership | Composite key: scope + asset_id; original footprints fully covered by the selected outline |
| buildings.in_study_area / in_primary_area | Independent wider / primary model flags |
| poi | OSM functional destinations; original IDs/tags and independent scope flags |
| land_use | Observed 2021 survey classes in the 2025 model, separate from legal zones |
| zones | Planning reference FAR/BCR percentages; parcel-specific rules need checking |
| census | Full 2020 source town records; intersections never allocate the full population to a partial polygon |
| flood | Four separately dated source scenarios |
| trees / tree_routes / parks | Different source units and coverage; point gaps remain gaps |
| stations | Separate JR/Ginza Kanda records; no name-only merge |

[Layer catalog](../04_Data/Metadata/Layer_Catalog.csv), [field catalog](../04_Data/Metadata/Layer_Fields.csv) and [glossary](../04_Data/Metadata/Field_Name_Glossary.csv) describe 126 current and dated tables and 1,665 fields. Distinguish them by dataset path.

## Units and methods

Source counts represent PLATEAU LOD1 model objects, not surveyed individual buildings. Wider selection has 764 Chiyoda and 310 Chuo objects. The primary has 277 Chiyoda objects. Only full footprints covered by the chosen trace enter building analysis. Original geometry is retained; crossing and exterior models are grey context. Source measured heights and proxy heights remain separate. Floor proxy（楼面代理量）is projected area × source/proxy levels, not metered floor occupancy or energy.

Analysis and GIS use EPSG:6677 in metres; exchange GeoJSON uses EPSG:4326. Each trace retains its source pixels, affine controls and 25 m screening band. Boundary-sensitive counts are in statistics.json.

## POI semantics（功能语义）

Raw OSM query, full geometry and provenance are in [Raw/POI_OSM_2026-10-18](../04_Data/Raw/POI_OSM_2026-10-18). Processed records and audits are in [Ready/POI_OSM_2026-10-18](../04_Data/Ready/POI_OSM_2026-10-18). Source snapshot: 2026-10-18; license: ODbL 1.0, © OpenStreetMap contributors.

Explicit tags classify food/drink, shops/daily needs, work/services, health, stays, civic/learning, culture/leisure and mobility. Other named objects remain an explicit fallback. Seats, bins, signs and similar support records are retained separately. Source type+ID is the key; a node/area merge needs identical name/function/level/branch and node containment. No such pair was merged in this extract.

The wider area has **353** destinations; primary **178**. Food/drink: **139 (39.4%)** wider, **86 (48.3%)** primary. Primary density is **1.98 times** the wider-area density. Source building attributes independently assign **71.9% of the wider floor proxy to offices**, supporting a business district with strong food, shopping and service activity.

Three equal northing bands compare per-hectare density and functional mix. A 100 m grid reports descriptive specialization where there are ≥5 POIs, ≥3 of a category and local share / wider share ≥1.5. This is not a significance test. OSM is not a complete business, employment or opening-hours census.

## Hazards and simulations

Earthquake values are full official 2022 town values: 23 wider intersections and 13 primary intersections, derived from 2020 census geometry. Overlap selects source rows; it never scales risk values. No recorded flood overlap establishes safety.

Actual energy and carbon remain missing. Existing CFD fields keep their dated geometry and unaccepted numerical status. See [simulation scope plan](Simulation_Scope_Plan_2026-10-18.md).

