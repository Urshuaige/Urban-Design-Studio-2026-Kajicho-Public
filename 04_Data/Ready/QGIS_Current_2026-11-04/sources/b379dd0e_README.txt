# Koto Ward context

This folder contains a standalone Koto Ward addition to the existing Kajicho macro context. `Koto_Context_GSI_2026.gpkg` is in EPSG:6677 and contains buildings, road centre lines, railway centre lines and tracks, water polygons and edges, the ward boundary, and a ward label point.

The building layer has 63,418 cartographic building polygons. The transport and water layers contain source features or tile segments, rather than counts of unique roads or waterways. This is a mapped snapshot, not an inventory of every building currently standing.

The source is the [GSI optimal vector-tile archive](https://cyberjapandata.gsi.go.jp/xyz/optimal_bvmap-v1/optimal_bvmap-v1.pmtiles), source snapshot 1 July 2026, downloaded 31 October 2026. Its archive metadata matched the existing six-ward context release. All 267 zoom-16 tiles intersecting Koto Ward were obtained. Source use follows the [GSI content-use terms](https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html); credit the Geospatial Information Authority of Japan when publishing maps.

The ward boundary comes from [MLIT National Land Numerical Information N03](https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2026/N03-20260101_13_GML.zip), reference date 1 January 2026, downloaded 25 October 2026; it is provided under CC BY 4.0 with MLIT attribution. `Koto_Ward_N03_2026.geojson` retains the 75 source ward parts. Building fragments are rejoined at tile seams and assigned using their representative points; other features are clipped to the ward. `Scripts/build_koto_context.py` reproduces the process and `Build_Receipt.json` records the acquisition and processing.

The GeoPackage passed SQLite integrity and all 63,418 building geometries passed GDAL validity checks. Five Koto building polygons near the ward border overlap an existing six-ward polygon by at least 99%; both are retained so that the Koto layer remains complete when used on its own. The comparison is recorded in `Boundary_Overlap_QA.json`.
