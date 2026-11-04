# Historical Urban Fabric（片区历史肌理）

## Outputs / 编辑入口

- `Kajicho_Historical_District_2026-11-02.qgz`: independent editable QGIS project; original saved project and user styles unchanged.
- `maps/Interpreted_prewar.png`, `Interpreted_postwar.png`, `Interpreted_recent.png`: district comparison.
- Matching `Aerial_*.png`: unclassified source views for checking.
- `data/Historical_District.gpkg`: per-period street axes, selected roof forms, water and railway corridor interpretation. All styles/layouts editable.
- Figma: https://www.figma.com/slides/hh16ci0VeM3JQj2tZFvdbX?node-id=2-91 . New body182:12; previous four-block body167:2 and earlier102:2 remain hidden, recoverable.

## Extent / 范围

EPSG:6677: (-6010,-34850)–(-4890,-33550), 1120 ×1300m. North up; identical extent and1:7000 native QGIS map scale across all periods. Covers the entire current wider-study bounding box with surrounding context. No primary/wider polygon clips the image or the interpretation. Streets and blocks continue to the outer map frame; peripheral context is naturally cropped by the rectangular image view. This replaces the rejected225×170m four-block comparison.

The view runs from the Kanda River through Kajicho to the southern Nihonbashi-side fabric. The railway and six legible principal street axes orient the comparison. Full aerial texture remains available throughout the district; this is not a reconstruction of every building or every historic street edge.

## Image processing / 处理

Existing GSI mosaics only; no new basemap downloads. Original data unchanged. Reprojection uses nearest-neighbour at1m, consistent with nominal ~1m ground source pixels. No blur, sharpening, smoothing, AI generation, model segmentation, modern-building substitution, or rectangle regularization. Weighted luminance0.2126R+0.7152G+0.0722B; each period has its own P2–P98 display stretch mapped to65–255. Values/parameters inProcessing_Receipt.json. The oldest effective visual detail is poorer than the nominal pixel size.

Selective manual interpretation is based on separate enlarged same-period aerial reviews. First draft minor-street lines and ambiguous small roofs were rejected during visual QA. Final output retains6 principal street axes per period, the legible school roof form (1prewar,1postwar,2recent roof parts), railway corridor and visible waterways. The script retains discarded draft coordinates for audit; they are not exported features. Roof counts here describe selected annotations, not building totals. Axes have a graphic line width rather than a measured road width. Water and rail polygons indicate corridors, not surveyed bank/property boundaries. Courtyards are excluded from the selected school roof shapes.

## Reading / 可支持的观察

- Broad rail/street framework is recognizable across all three images.
- The1945–1950 image shows more fragmented roof patterns and pale gaps east of the railway than the earlier view. No percentage of destruction or coverage is computed from tones.
- An open canal corridor is visible in the earlier two views and absent in theFY2019 view.
- The recent image shows larger roof forms in the southern part of the frame. These are visible image observations, not inferred parcel ownership or development approvals.

Prewar1936–1942 and postwar1945–1950 are source acquisition windows, not exact photograph dates. Recent is theFY2019 layer, not a substituted2026 building dataset. The other local1974–1978 layer is not used. Original course-boundary RMSE7.43m and25m screening band do not describe historical-image registration accuracy. No independent local image RMSE has been established.

## Cartography / 版式

Native QGIS maps160×185.714mm; page160×208mm includes a clean footer outside geographic content. North arrow8×8mm at(4,189); scale directly below at(4,199),0/100/200m. All backgrounds and frames off. Legend at(60,188), Arial7pt. No white-backed component covers rivers/buildings. Figma includes a larger native shared legend22px; findings26Regular, dates30Bold, title44Bold. All map deliveries PNG. Sources, scripts, original views and editable vectors are retained.

This is a project-relative QGIS copy within the existing shared folder tree, not a standalone ZIP. Offscreen QGIS exports and saved layer file/table checks pass. Desktop GUI reopen has not been performed; no locked desktop was bypassed.

## Reference workflow

Re-read the existing Chinese Xiaohongshu per-page review and visually inspectedR12_typology_matrix.webp. Adopted equal-scale three-column comparison and concise findings; did not copy any reference image asset or its project facts. Local index:/Users/shichao/Documents/Codex/2026-10-31/task/reference-research/per-page-reference-index.md.
