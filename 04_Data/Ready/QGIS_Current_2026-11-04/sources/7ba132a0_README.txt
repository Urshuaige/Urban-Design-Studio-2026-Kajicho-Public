# Historical layers: Kajicho

The open project contains three comparable aerial layouts and three optional fabric-review layouts. Each uses the same map extent and scale. The study boundaries and legend are not drawn. The north arrow and scale bar have transparent backgrounds.

## Layers

Open `00 Analysis & sources > Historical Layers — three periods`. The group is off by default so it does not change the main map. Turn on a period's image, labels, and candidate layers as needed. The `History` layouts show aerial images and place, river, and road names. The `Fabric` layouts add optional interpreted outlines.

- `Estimated buildings`: approximate, editable rectangles generated from model-detected image regions. They are review suggestions, not a complete inventory or surveyed footprints.
- `Built-up groups`: clusters of detected image texture. Current road geometry was used to split groups; these are not independently surveyed historical street-block boundaries.
- `Raw model mask`: original thresholded detection before rectangularization. The stored probability raster is an 8-bit diagnostic, and its score is not calibrated for these old images.
- `Surviving buildings dated ...`: current footprints linked to a published completion year before the start of the relevant image period. The historic footprint shape and continued existence at the photograph date require image and source review.
- `Current buildings`: the existing project layer. Most features have a 2021 survey year and 2025 model year; 82 have no survey year and one has no model year. Their reviewed status dates are retained in the source layer.

The 1945–1950 and 1974–1978 building layers contain 308 and 276 regularized candidate features respectively. These counts describe the software output, not historical building totals. Detection is incomplete and varies between the photographs. Do not compare candidate counts or apparent density with the current building dataset.

## Source and dates

| Layer | Source | Spatial details | Date meaning |
| --- | --- | --- | --- |
| Postwar aerial | [GSI ort_USA10](https://cyberjapandata.gsi.go.jp/xyz/ort_USA10/{z}/{x}/{y}.png) | z17, EPSG:3857, about 1 m ground pixels at Kajicho | 1945–1950 source window; exact site capture date not determined |
| Growth aerial | [GSI gazo1](https://cyberjapandata.gsi.go.jp/xyz/gazo1/{z}/{x}/{y}.jpg) | z17, EPSG:3857, about 1 m ground pixels | 1974–1978 source window; exact site capture date not determined |
| Latest aerial | [GSI seamlessphoto](https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg) | z17, EPSG:3857 | The GSI map reported June–November 2019 at the Kajicho site centre on 1 November 2026. Adjacent tiles may use other dates. |
| Street and river labels | Existing OSM/GSI project data | EPSG:6677 | Current names and positions are orientation references; they are not asserted to be period-specific names. |
| Station and place labels | Existing project station references | EPSG:6677 | Approximate reference points. Shin-Nihombashi is omitted from the postwar layout. JR is used only on the current layout. |

The source tile list, URLs, download date, bounds and mosaics are in `aerial_sources.json`. Original downloads are in `04_Data/Raw/Historical_Layers_2026-11-01`. GSI use follows the [GSI content terms](https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html). OSM-derived road names use the [ODbL attribution](https://www.openstreetmap.org/copyright).

## Recognition

The model is [HOTOSM DINOv3s building segmentation](https://huggingface.co/hotosm/dinov3s-buildings), revision `f7254545dfbbf10a40594d5a5fb62136902000ae`; model file SHA-256 `9a28e28403accc06c70a3104aedb31eca50401ed23c8ba4314b26357c25e9043`. The model card states CC BY 4.0 for its trained model and separate DINOv3 backbone terms. Cite the model and its training data when reusing the derived candidate layers.

The 256-pixel overlapping model windows were run on the two historic images. The output was thresholded, split with masked watershed, and regularized to rotated rectangles. Very small, highly overlapping, road-centred or poorly filled boxes were removed. The wider study area was used as an analysis mask, but its outline is not shown in the layouts. Group polygons aggregate detected texture using current roads as separators.

Manual inspection showed omissions and merged roofs. Old image resolution, shadows, changes in roads, and the model's modern-image training affect the result. The CPU result was finite; GPU inference returned non-finite values on this host and was discarded. Detailed run and regularization receipts are stored beside this file. The historical candidates are a starting point for interpretation, not a measurement of historic density or an exhaustive reconstruction.

## Project and outputs

- Project: `06_Outputs/Slides/Development_Review_2026-11-01/Kajicho_Development_Review_2026-11-01.qgz`
- PNG maps: `06_Outputs/Historical_Layers_2026-11-01/maps/`
- Vector candidates: `Historic_Fabric_Candidates_Regularized.gpkg` in this folder, EPSG:6677. The earlier candidate GeoPackage remains available for recovery and is not used in the current layouts.
- Reference labels and dated survivors: `Historical_Context.gpkg` in this folder, EPSG:6677.
- Task record and pre-edit project backup: `07_Team/Historical_Layers_2026-11-01/`. Restore the backup to the original project folder if needed, so its relative paths resolve.
