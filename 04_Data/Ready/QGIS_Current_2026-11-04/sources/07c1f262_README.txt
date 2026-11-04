# Transport lines beyond the wider boundary

The QGIS group `05 Base map in boundary / Transport — wider area` now uses the extended network. The inner lines stay in place. Roads that reach the wider boundary continue on source roads beyond the A4 map frame. The line data extends about 300 m beyond each side of the larger history map frame.

Choose one layer under `Roads — choose classification`. The GSI layer uses administrative road classes. The OSM layer uses functional road types. Both layers use the same geometry. Roads use solid lines. The elevated JR corridor uses a purple long-short dash. The expressway and underground railway layers stay off by default.

| GeoPackage table | Features | Content |
| --- | ---: | --- |
| `roads_ground` | 1,092 | Existing and extended surface-road axes |
| `roads_expressway` | 1 | One elevated Route 1 Ueno axis |
| `rail_ground` | 1 | One representative elevated JR corridor |
| `rail_underground` | 72 | Inner and extended underground rail segments |

## Sources

The GSI optimal vector map has a source date of 2026-07-01. It is retained in `../Master_Context_GSI_2026.gpkg`. The [source PMTiles](https://cyberjapandata.gsi.go.jp/xyz/optimal_bvmap-v1/optimal_bvmap-v1.pmtiles), [GSI terms](https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html), and [road specification](https://www.gsi.go.jp/common/000271707.pdf) describe the original data. Source tile and feature identifiers remain in the attributes.

OpenStreetMap data was downloaded on 2026-11-01 at 22:56 JST. The source snapshot time was 2026-11-01 at 13:55 UTC. The download used the [Overpass API](https://overpass-api.de/) and is retained in `04_Data/Raw/Transport_Extension_2026-11-01/osm_transport_overpass.json` in the project workspace. It is © OpenStreetMap contributors and is available under [ODbL 1.0](https://www.openstreetmap.org/copyright). The request and SHA-256 hash are in `sources/osm_download.json`.

The processing rectangle is `[-6622, -35655, -4599, -33115]` in EPSG:6677, in metres. The boundary is the existing wider `study_area` polygon. The source date and the download date describe the datasets. They do not establish a field-survey date for each road.

## Method

The 434 existing inner road features remain in the table. Source lines outside the boundary were followed from boundary crossings. Direction, source identity, road name and proximity helped choose each continuation. OSM source ways supplement gaps in the official road data. The result is an illustrative network and does not include every road in the surrounding rectangle.

Showa-dori uses one approximate axis between its two carriageways. The elevated expressway also uses one axis. Expressway ramps and link branches are excluded. Where two source lines almost overlap along the boundary, the duplicate outer line is removed. Short diagram joins are recorded in `junction_conn_m` and `notes`.

One Yamanote track represents the nearby JR corridor. The listed railway names occur along at least part of that corridor. They do not mean that every service uses the whole representative track. The underground rail layer uses GSI lines with nearby OSM line-name matches.

The lines support maps and spatial interpretation. They do not preserve all lanes, turn restrictions or vehicle-access rules. They are not a verified routing network. A real road can end or change direction before the edge of the map.

## Files and checks

The GeoPackage is `Transport_Extended_Context_2026-11-01.gpkg`. The previous boundary-clipped GeoPackage remains in `../Transport_Network_2026-11-01/`.

All five QGIS layers opened with the saved relative path. The GeoPackage passed `PRAGMA integrity_check`. There are no OSM `_link` classes in `roads_ground`. All 67 boundary-crossing endpoints in the earlier core network have an extended line within 1 m. This last check measures distance and does not verify routing connections. The JR line extends beyond the larger history frame at both ends. The A4 and larger map previews were rendered and inspected.

The source extracts and GeoJSON outputs are in `sources/`. `scripts/build_extended_transport.py` contains the processing. To run it in an isolated directory, place the script beside an `inputs/` folder with the seven source GeoJSON files, `osm_download.json`, and the retained `osm_transport_overpass.json`. The script writes its outputs and processing receipt to `outputs/`. The recorded run used Shapely 2.0.7 and pyproj 3.6.1 on `mdx1`.
