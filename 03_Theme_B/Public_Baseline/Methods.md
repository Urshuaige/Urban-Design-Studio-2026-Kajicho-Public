# Public-baseline methods

## Geometry

Core statistics retain the v2 Demo `core` ID set: 277 PLATEAU building objects whose representative points fall within the 2020 Kajicho 1 & 2 town boundaries. The existing surrounding set contains 1,981 objects. New thematic layers use a technical window of 139.767–139.776 E, 35.687–35.695 N. Area-intersection counts, representative-point counts and legal-site counts have different meanings.

CityGML EPSG:6697 coordinates are read as latitude, longitude and height. Horizontal JGD2011 coordinates pass through EPSG:6668 to EPSG:6677. Building projections reuse existing LOD1 geometry. Flood triangles are dissolved, repaired and clipped before area-intersection analysis; repair counts and original GML IDs are retained.

## Building attributes

`height_m` and `levels` reuse v2 source or proxy values with `height_source` and `levels_source`. Raw sentinels—height `-9999`, storeys `9999`, survey year `0001`—remain in raw attribute JSON and become unknown in analysis fields. `creation_date` is the model creation date; `construction_year` is missing throughout this extraction.

`floor_proxy_m2 = plan_area_m2 × levels`. Projection area and proxy storeys differ from measured total floor area. The CityGML floor-area conversion factor is retained as `source_floor_factor` but was not applied, preserving reconciliation with v2. Check its definition against source geometry and actual floor area before future use.

`actual_electricity_kwh`, `actual_gas_m3` and `actual_co2_t` are null. `scenario_*` records assumptions: floor proxy × 120 kWh/m²/year; purchased electricity × 0.421 kg CO₂/kWh ÷ 1,000. The factor is the common-foundation TEPCO 2024 adjusted factor. Update it for the actual contract and year before applied accounting.

## Planning overlays

`source_far_pct` and `source_bcr_pct` come from CityGML. `mlit_far_pct_set` retains all reference-zone FAR values with building-projection intersection above 0.01 m². A consistent single value is `match`; several values are `multiple_zones`. This identifies cross-zone objects. Legal capacity still requires site boundaries, road width, frontage, district plans and other applicable conditions.

## Greenery

A circular crown uses half the recorded positive crown spread as its radius. Zero/missing spreads produce no circle. A clipped route retains the original route's tree count, which cannot be assigned to the clipped segment. Park polygons describe facilities rather than continuous tree canopy.

## Weather

Tokyo station `s47662`: 2025-01-01 01:00 to 2026-01-01 00:00 JST, 8,760 hours. JMA's literal-date mode records 24:00 as the following day's 00:00; `observation_day` and `observation_hour` retain the original day and hours 1–24. [JMA CSV guidance](https://www.data.jma.go.jp/risk/obsdl/top/help3.html) defines quality codes: 8 normal, 5 quasi-normal, 4 insufficient data, 2 suspect, 1 missing, 0 not observed. Quality codes and homogeneity IDs remain available.

Wind direction is clockwise from north and denotes origin: `u_east = -speed × sin(direction)`, `v_north = -speed × cos(direction)`. Calm direction is empty; missing wind speed is not filled. Solar radiation in MJ/m² is energy accumulated over the preceding hour. Multiply by 1,000,000/3,600 for the hourly mean W/m². The station is a background record; account for observation height and local roughness before street-canyon use.

## Reproduce

Scripts under `08_Scripts`: `acquire_jma_baseline.py`, `prepare_jma_baseline.py`, `extract_public_citygml.py`, `build_public_baseline_qgis.py`, `register_public_baseline.py`. Acquisition scripts query current official services. Use saved originals, requests and versions for exact reproduction.

QGIS Python example:

```sh
PROJ_LIB=/Applications/QGIS.app/Contents/Resources/proj QT_QPA_PLATFORM=offscreen \
/Applications/QGIS.app/Contents/MacOS/bin/python3 -u 08_Scripts/build_public_baseline_qgis.py
```

`acquire_plateau_flood.py` selects members from a saved complete official ZIP listing and preserves original bytes. The acquisition notes record missing flood URL paths in the extent API and flood members absent from the Pack ZIP.
