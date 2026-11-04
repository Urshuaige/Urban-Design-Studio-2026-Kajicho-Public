# Code map

| Work | Entry points | Inputs and outputs |
| --- | --- | --- |
| Current study boundary and Mapping | `build_study_boundary.py`, `build_study_atlas.py`, `assemble_study_site.py` | Explicit `--task-root` → one street-block boundary, complete model membership, current GIS, nine maps and Site assets; see [Study area](docs/COURSE_BOUNDARIES.md) |
| Data and GIS | `08_Scripts/README.md` | CityGML, planning, greenery, flood and weather processing; QGIS projects and GeoPackages |
| 3D geometry | `prepare_cfd_geometry_v3.py`, `repair_cfd_surface_v3.py`, `audit_cfd_domain_v4.py` | Building models and attributes → geometry in a common CRS, extent and provenance |
| Mesh and wind/heat | `build_openfoam_v3.py`, `prepare_cfd_pair_v3.py`, `prepare_cfd_light_case_v5.py` | Explicit input directories → OpenFOAM cases; `run_cfd_light_mesh_v5.py` and `run_cfd_light_checkpoint_v5.py` accept directories, image, process count and CPU allocation |
| Acceptance and export | `check_cfd_pair_v4.py`, `export_cfd_checked_pair_v5.py` | Native logs, heat balance and probes → individual checks; final export requires both cases to pass and uses each passing state |
| Heat-budget diagnosis | `prepare_cfd_snapshot_budget_v4.py`, `run_cfd_snapshot_budget_v4.py` | Read-only fixed checkpoint → offline boundary and discrete-operator checks |
| Check histories | `collect_cfd_numerical_history_v5.py --config … --output …` | Personal local/SSH configuration → website diagnostic JSON; examples in `config/` |
| Compute capacity | `inspect_compute_hosts.py --hosts …` | Explicit SSH host list → read-only CPU/GPU capacity report |
| 2D wind and shade | `demo_wind_v2.cpp`, `demo_shade_v2.py`, `demo_shade_v2_sun.cjs` | Historical teaching scenarios; methods and limits in the website guide |
| Website | `06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/` | `dist/` source and compact data; `serve_demo.py` previews with standard Python |
| Data catalogs | `build_layer_catalog.py` | Read-only GeoPackage scan → `Layer_Catalog.csv`, `Layer_Fields.csv` |

Script names are relative to `08_Scripts`, except the website path. See [Scripts](08_Scripts/README.md) for the data/GIS list. Keep one authoritative copy of each script. Personal agent files, host state, deployment credentials and automation history stay outside shared source. [Data access](DATA_ACCESS.md) locates large originals and full fields; [CFD status](docs/CFD_STATUS.md) explains the numerical evidence.

## Figure 5 and POI update

build_study_boundary.py retains the two official source-pixel traces. build_study_atlas.py uses one view for both scopes. build_poi_semantics.py classifies OSM destinations and describes functional mix/concentration. assemble_study_site.py calls assemble_figure5_view.py to replace the active Site content. check_study_area_release.py validates the coupled release. No solver is invoked.

Current website assembly: assemble_study_site.py runs the Figure 5 view, delivery refresh, stable global navigation and local page outline installers. Strict membership is implemented in build_study_atlas.py and independently verified against saved geometry by check_study_area_release.py. Current package assembly: prepare_current_team_package.py and the manual Current team package workflow.
