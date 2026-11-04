# Kajicho public baseline

Current course geography: [registered boundary release](../../docs/COURSE_BOUNDARIES.md). This dated package records the earlier census ROI; use the current course atlas for source-area totals.

2026-10-14 · Kajicho 1 & 2 and the surrounding technical window.

This version joins building attributes, planning GIS, greenery, flood scenarios and Tokyo-station weather in an EPSG:6677 GeoPackage. DECC registration is pending; actual electricity, gas and CO₂ fields remain null. Existing v2 default electricity estimates remain separate `scenario` fields for reconciliation.

## Open

- [QGIS project](../../05_QGIS/Projects/Kajicho_Public_Baseline_2026-10-14.qgz): 36 layers, three print layouts, relative paths.
- [GeoPackage](../../04_Data/Ready/Public_Baseline_2026-10-14/Kajicho_Public_Baseline.gpkg).
- [Building table](../../04_Data/Ready/Public_Baseline_2026-10-14/Kajicho_Buildings.csv) and [use summary](../../04_Data/Ready/Public_Baseline_2026-10-14/Kajicho_Use_Mix.csv).
- [Hourly weather](../../04_Data/Ready/Public_Baseline_2026-10-14/Tokyo_2025_hourly.csv) and [summer sample days](../../04_Data/Ready/Public_Baseline_2026-10-14/Tokyo_2025_sample_days.csv).
- [Source register](../../04_Data/Ready/Public_Baseline_2026-10-14/Source_Register.csv), [spatial checks](../../04_Data/Ready/Public_Baseline_2026-10-14/Spatial_Quality.json), [weather checks](../../04_Data/Ready/Public_Baseline_2026-10-14/Weather_Quality.json).
- [Handoff](Team_Handoff.md) and [methods](Methods.md).

Extract the complete Ready ZIP from Drive before opening QGIS. Keep relative folders. One GIS lead writes the main GeoPackage; other members return separate files/CSV.

## Findings and gaps

| Topic | Acquired/checked | Use |
| --- | --- | --- |
| Buildings | All 1,981 existing objects joined by GML ID; 250 of 277 core objects have use and source storeys, 27 unknown | Group by use/structure/height; field-check unknowns |
| Years | Known core attributes mainly surveyed in 2021; model published 2025; construction year unavailable | Model creation date is not construction year |
| Planning | Full Tokyo reference GeoJSON downloaded; Chiyoda/Chuo zones, district/fire plans clipped; 251 single-FAR matches, 26 cross-zone objects | [Review table](../../04_Data/Ready/Public_Baseline_2026-10-14/Building_FAR_Review.csv), then legal-site/official-map checks |
| Land/roads | 1,314 land-use objects and 968 LOD1 road objects within technical window | Land structure and road surfaces; LOD3 sub-surfaces not extracted |
| Trees | 320 context points, 156 positive crown spreads; no individual core points, seven intersecting route records | Survey core positions/crowns; full-route counts are not clipped-segment counts |
| Parks | Three urban and five other context park records; no core park intersections | Identify nearby cooling nodes; park area is not full canopy coverage |
| Floods | 14 raw GML files, 59 clipped scenario objects; 144 core projections intersect Kanda L2 | Exposure screening, then entrance/basement/evacuation checks |
| Weather | 8,760 Tokyo hours in 2025; two missing wind hours; other selected variables normal quality | Background conditions with direction, humidity, rain, radiation and flags |
| Energy | Reproducible scenarios and empty use-specific DECC form | Check original units, sample year and energy scope before calibration |

Tree publication in 2026 and survey in 2020 are recorded separately. Parks and Chiyoda/Chuo tree routes mainly refer to 2024-04-01; see [Tokyo definitions](https://data.storage.data.metro.tokyo.lg.jp/toshiseibi/green_teigisho.pdf).

## Analysis use

1. Join attributes to v2 geometry on `building_id`, preserving core IDs. Default floor-area proxy remains 229,754.943 m².
2. Check wind origin, time and radiation units with prepared samples. They include 2025-08-30 (highest summer hourly temperature) and 2025-07-31 (daily hourly maximum near the summer median). These selected days are not a typical meteorological year.
3. Generate crown circles only for positive recorded spread. Survey core trees; missing points are a data gap.
4. Use DECC by-use ranges, then actual bills/BEMS for calibration. Uniform EUI=120 yields the existing scenario of 27.57 GWh and 11,607 t CO₂/year.
5. New physical wind/heat work requires mesh, reference height, roughness, turbulence and heat boundaries to be defined. Existing demos retain their own methods. The current project stage adds no CFD runs.

## Originals

Originals are under `04_Data/Raw/Public_Baseline_2026-10-14` in external storage. The 387 MB CityGML Pack was delivered as four byte-preserving parts under `PLATEAU/chiyoda_bbox_pack.zip.parts` because the upload route used a 100 MiB file limit. Download all four parts, `Parts.json` and `Join_Archive.py` together, then run `python Join_Archive.py` to reconstruct the parent ZIP. Normal QGIS use does not require this large source pack.

Sources: [PLATEAU CityGML service](https://docs.plateauview.mlit.go.jp/datasets/citygml/), [MLIT planning GIS](https://www.mlit.go.jp/toshi/tosiko/toshi_tosiko_tk_000182.html), [JMA](https://www.data.jma.go.jp/risk/obsdl/index.php). Derived files retain sources, scripts and checks. After DECC registration/download, keep originals and terms in `04_Data/Raw/DECC`; distinguish electricity kWh, fuels and primary-energy MJ.
