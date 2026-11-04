# Sumida Ward context

This folder adds Sumida Ward, directly north of Koto Ward, to the Kajicho macro context. `Sumida_Context_GSI_2026.gpkg` uses EPSG:6677 and contains buildings, road centre lines, railway centre lines and tracks, water polygons and edges, the ward boundary, and an English ward-label point.

The building layer has 52,105 cartographic building polygons. Road, rail and water counts are source features or tile segments. This is a mapped snapshot, not an inventory of every building currently standing.

The source is the [GSI optimal vector-tile archive](https://cyberjapandata.gsi.go.jp/xyz/optimal_bvmap-v1/optimal_bvmap-v1.pmtiles), source snapshot 1 July 2026, downloaded 31 October 2026. Its archive metadata matched the existing six-ward and Koto context release. All 84 zoom-16 tiles intersecting Sumida Ward were obtained. Source use follows the [GSI content-use terms](https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html); credit the Geospatial Information Authority of Japan when publishing maps.

The ward boundary comes from [MLIT National Land Numerical Information N03](https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2026/N03-20260101_13_GML.zip), reference date 1 January 2026, downloaded 25 October 2026; it is provided under CC BY 4.0 with MLIT attribution. `Sumida_Ward_N03_2026.geojson` retains the source ward geometry. Building fragments are rejoined at tile seams and assigned using their representative points; other features are clipped to the ward. `Scripts/build_sumida_context.py` reproduces the process and `Build_Receipt.json` records acquisition and processing.

The GeoPackage passed SQLite integrity and GDAL found no invalid building geometries. The boundary comparison in `Boundary_Overlap_QA.json` found no exact duplicate building polygons and no building polygons with at least 99% overlap with the existing Koto or six-ward context near the Sumida boundary.
