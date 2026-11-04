# Scripts

This folder holds the authoritative shared code. Project paths come from script location, arguments or personal configuration; the operator chooses hosts and resource allocation. See [Data access](../DATA_ACCESS.md) for originals/full fields and [Data guide](../docs/DATA_GUIDE.md) for definitions.

## Current study area and Mapping

The active 2026-10-18 sequence uses one street-block boundary and complete building model projections. Set `task_root` to the prepared remote task folder containing `team/`, `assets/assets.gpkg`, `registration/` and Site source. Inspect live compute capacity and coordinate the single GIS writer before processing.

```sh
python3 08_Scripts/build_study_boundary.py --task-root /path/to/task-root
python3 08_Scripts/build_study_atlas.py --task-root /path/to/task-root --workers 9
python3 08_Scripts/build_layer_catalog.py --root /path/to/task-root/team
python3 08_Scripts/assemble_study_site.py --task-root /path/to/task-root
```

The atlas writes `Study_Area_2026-10-18`, the current GeoPackage and portable QGIS project. The assembler writes `study-atlas` Site assets. Catalog generation reads GeoPackages only after their rebuild completes. `--gis-only` is reserved for rebuilding current GIS from an already checked, unchanged study atlas.

Earlier `build_portfolio_maps.py`, `build_boundary_atlas.py`, `consolidate_mapping.py`, `assemble_boundary_site.py` and `finalize_boundary_repository.py` reproduce dated releases. They must not overwrite current Mapping, membership or manifests. See [the current study guide](../docs/COURSE_BOUNDARIES.md) and [simulation scope plan](../docs/Simulation_Scope_Plan_2026-10-18.md).

## Data and GIS

| Task | Scripts |
| --- | --- |
| JMA weather | `acquire_jma_baseline.py`, `prepare_jma_baseline.py` |
| CityGML attributes and floods | `extract_public_citygml.py`, `acquire_plateau_flood.py` |
| PLATEAU 3D Tiles projection | `extract_plateau_demo.py` |
| Shared spatial data/projects | `build_common_qgis.py`, `build_public_baseline_qgis.py`, `integrate_cfd_domain_qgis_v3.py` |
| Official zones and trees | `integrate_official_zoning_v3.py`, `integrate_tree_inventory_v3.py` |
| Sources and metadata | `register_public_baseline.py`, `build_layer_catalog.py` |
| Carbon scenarios and source report | `prepare_carbon_foundation.py` |

Python dependencies are in `requirements-cfd.txt`; PDF/3D Tiles extraction also uses `requirements-data.txt`. Project generators run in QGIS's PyQGIS environment; QGIS is not installed with ordinary pip. Preserve downloads and rebuild derived files in separate folders.

## Geometry and CFD

`prepare_cfd_geometry_v3.py` and `repair_cfd_surface_v3.py` generate geometry. `audit_cfd_domain_v4.py`, `screen_plateau_context_v4.py` and `audit_wider_bldg_metadata_v4.py` check surrounding buildings. `build_openfoam_v3.py`, `prepare_cfd_pair_v3.py` and `prepare_cfd_light_case_v5.py` create isolated cases.

Current generic runners are `run_cfd_light_mesh_v5.py`, `run_cfd_light_checkpoint_v5.py` and `run_cfd_snapshot_budget_v4.py`. See `--help` for paths, image, processes and CPU allocation. They run on a configured host without personal agent-state inputs. `prepare_cfd_domain_case_v4.py` retains earlier reference-trial numerics; check decomposition against the intended resources.

Native `checkMesh`, street prechecks and `check_cfd_pair_v4.py` inspect meshes/results. `export_cfd_checked_pair_v5.py` rejects unaccepted pairs and selects each case's final passing state. Historical `export_cfd_pair_v3.py` does not enforce that final-publication gate. See [CFD status](../docs/CFD_STATUS.md).

`collect_cfd_numerical_history_v5.py --config …` reads local/SSH history without advancing calculation; see [config](../config/README.md). `inspect_compute_hosts.py --hosts …` queries only the specified hosts; save personal outputs in `local/`.

## Parameter studies

`demo_wind_v2.cpp` is a 2D D2Q9 example. `demo_shade_v2.py` and `demo_shade_v2_sun.cjs` precompute building shade. Preparation, post-processing and packaging scripts are here too. 2D wind, geometric shade, assumed energy and 3D CFD use different inputs/methods; see the website README and protocol.

## Checks

```sh
python3 08_Scripts/check_team_repository.py
python3 08_Scripts/test_cfd_acceptance_v4.py
python3 08_Scripts/test_cfd_checked_export_v5.py
python3 08_Scripts/test_cfd_history_v5.py
python3 08_Scripts/check_repository_language.py
node 08_Scripts/check_cfd_guide.mjs
node 08_Scripts/check_cfd_numerical_guide.mjs
```

After adding a GeoPackage or fields, run `python3 08_Scripts/build_layer_catalog.py`, then relevant checks. CI checks software/data structure; members also review map presentation and scientific interpretation.

The current native earthquake-risk table is built with `build_study_risk.py --census-csv <study tables/census_intersections.csv> --risk-csv <unchanged official all2.csv> --output <earthquake_risk_by_town.json> --boundary-geojson <study_boundary_6677.geojson>`. It joins all 23 intersecting official town units, merges repeated census geometry parts, and retains whole-town risk values. The source hash and the single verified town-name crosswalk are in the JSON. Rebuild it after changing the study area, before assembling the Site.

Figure 5 / POI: build_study_boundary.py, build_study_atlas.py, build_poi_semantics.py, build_study_risk.py --scope study_area|primary_brief, assemble_study_site.py → assemble_figure5_view.py. GIS export requires QGIS 3.44+. Inspect current compute hosts before batch work. Maps use PNG; previews JPEG. Current source boundaries are Figure 5 strokes with stored affine controls; never reshape them to retain models.
