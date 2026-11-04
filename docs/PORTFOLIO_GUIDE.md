# Mapping and source readings

The current [Figure 5 release](COURSE_BOUNDARIES.md) has one overview and nine thematic PNG maps. Every map uses one common view with the official solid primary and dashed approximate wider outlines. No separate map is repeated for another boundary.

The ninth theme maps classified OSM destinations. Native HTML bars and tables compare both scopes, three equal northing bands and descriptive 100 m function concentrations. Their methods and full IDs are linked on the page. Building use and POI functions are separate source measures.

Web previews are map-only JPEGs. Native legends use 17 px text, just below the 18 px body. PNG legends use 17 pt and station labels 18 pt. Document requirements use source → local check → design action boxes; source links use 19 px / weight 750. Full source quotations remain in context.json.

New visits start in English; explicit language choices persist. Asset URLs use the current release revision to avoid stale cached maps and tables. All map geometry and analysis use EPSG:6677; exchange GeoJSON uses EPSG:4326.

## Reproduce

Use build_study_boundary.py to reproduce Figure 5 source pixels and controls. build_study_atlas.py prepares both scope tables, nine themes plus overview, POI data and portable GIS. build_poi_semantics.py records the function rules, geometry locations and duplicate audit. build_study_risk.py joins full official-town values separately by scope. assemble_study_site.py calls assemble_figure5_view.py so current labels and data always follow Figure 5.

Dependencies: Python, Shapely 2, PyProj, Matplotlib, Pillow, Noto CJK and QGIS 3.44+ for GIS export/provider validation. Use the project’s fresh compute-host inspection before batch work. Current maps were calculated remotely; GIS was saved/read on the compatible QGIS 3.44 host. No results are copied to local Downloads.

check_study_area_release.py validates source-pixel transforms, hashes, both scopes, model joins, footprint crossings, POI counts/ratios, common view, PNG/JPEG dimensions, legends, English default, policy panels, risk rows and portable GIS paths. Historical scripts and simulations keep their dated roles.

The [simulation plan](Simulation_Scope_Plan_2026-10-18.md) defines input changes for a future selected pilot. No new CFD is part of this map/POI release.

