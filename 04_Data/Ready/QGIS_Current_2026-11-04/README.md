# Kajicho wider boundary GIS data

This delivery uses the current **wider boundary, 42.43712 ha**, to select local data. Buildings intersecting any part of the boundary retain their complete source footprints, including parts outside the line. It uses the `study_area` polygon saved on 29 October 2026. Kanto-wide original population and migration tables are excluded.

Clone the repository or download its ZIP. Keep this folder intact and open `Kajicho_Current_Data.qgz` in QGIS. All delivered files are ordinary Git files; Git LFS is not required. This is a data browsing project with relative paths. The original slide layouts remain in their dated local projects.

## Primary building age update — 13 November 2026

The QGIS project displays the [supplied primary building-age layer](shp/Primary_Building_Age_2026-11-13/) above the earlier age views. It contains 277 building models: 221 have a `Byear` value and 56 have no year. These are user-supplied values; the underlying age source, survey year and licence were not identified in the supplied file. The layer retains EPSG:4326 and 3D polygon coordinates. Its [field mapping](shp/Primary_Building_Age_2026-11-13/README.txt) records SHP field-name changes.

The five older age and chronology views in the QGIS project exclude their original `in_primary = 1` records, so the new layer supplies the primary-area display. Their underlying historical datasets remain available for provenance and retain their original attributes; outside the primary area the old views are unchanged. Matching by building ID identifies 256 common models, 21 new-layer models absent from the old 2011 evidence layer, and one old primary model absent from the new file. The source data are separate historical records, so the match is not a statement of changes to physical buildings.

The 4 November counts and dataset descriptions below describe the dated release; this update adds one SHP layer. Older static maps and website source retain their publication dates.

## Contents

The package contains **179 SHP datasets**, **14 nonspatial tables**, **192 GeoPackage tables** and **17 cropped rasters**. The QGIS project has 352 vector views plus the rasters. [Find data by layer name](metadata/Layer_Index.csv) or [browse sources and methods](SOURCES.md).

| Folder | Contents |
| --- | --- |
| `shp/` | SHP, SHX, DBF, PRJ and UTF-8 CPG files; full attribute CSVs and field maps |
| `data/` | Complete retained attributes in GeoPackage; rasters cropped to the wider cutline |
| `07_Tables/` | Supporting nonspatial records as CSV |
| `metadata/` | Boundary, before/after counts, processing, source links, joins and validation |
| `sources/` | Verbatim dated source and method records; historical Markdown files use `.txt` |

## Scope and values

Building records are selected by intersection with the wider polygon and retain complete source geometry in EPSG:6677. This applies to the southern edge and every other boundary edge, including reference, historical and analytical building layers. `delivery_geometry` distinguishes `whole_building_inside_wider` from `whole_building_intersects_wider`. Original source attributes and analysis-membership fields are preserved. Crossing buildings remain identifiable as boundary context; their inclusion in this delivery does not reclassify them as fully contained analysis buildings.

Other vector layers and rasters keep their existing wider-area clipping. `delivery_source_fid` identifies the input feature, and `delivery_value_scope` records the original meaning of its values. These fields are available in the native data and full CSVs. [Whole-building correction](metadata/Whole_Buildings_Correction.json) records each affected dataset and the geometry checks.

**Clipping changes geometry, not the meaning of an existing statistic.** A clipped census-town polygon still carries whole-town counts. A clipped analysis cell still carries the original cell result. Complete building footprints keep their original area, floor-area proxy and energy estimate. Use the original source-unit fields and the clip flags when comparing values. No population totals, coverage ratios, energy estimates or renewal grades were recomputed for this delivery.

Building and town-linked nonspatial tables are filtered by retained identifiers. Dated source registers, terminology and reference documents support the local data. Raster exports use the wider cutline, nearest-neighbour resampling and an alpha band outside the boundary. [Boundary.json](metadata/Boundary.json) gives the exact polygon; [Datasets.json](metadata/Datasets.json) records source counts, retained counts, coordinate systems and processing.

The building-to-town attribute join is restored in QGIS and recorded in [Joins.json](metadata/Joins.json). SHP and GeoPackage table exports keep the underlying tables separate, with their join keys. Different input versions remain separate. [Excluded_Layers.json](metadata/Excluded_Layers.json) records empty extracts, excluded regional tables and unavailable saved memory-layer placeholders.

## SHP fields

The 4 November SHP exports use EPSG:6677 and at most 255 DBF fields; the 13 November primary building-age layer retains EPSG:4326 and its original nulls. Each `_fields.csv` maps original field names to short DBF names and identifies fields retained only in the full CSV. Join `_full.csv` to SHP through `ROW_ID`. GeoPackage retains full field names, text, types and nulls. Complete building geometry matches the saved source exactly. One employment-allocation SHP record retains all ring coordinates but its microscopic rings are regrouped by the SHP reader; use its GeoPackage for the exact ring structure. The record is identified in `metadata/Validation.json`.

`NUL_BITS` marks missing values using bit positions in the field map. Numeric `-9999` and text `<NULL>` are placeholders only where the corresponding bit is set. CSV nulls use `<NULL>`; exact null/string distinctions remain in GeoPackage. Numeric SHP values have eight decimal places.

## Sources and interpretation

The saved inputs cover building use and age evidence, renewal screening, energy and carbon estimates, vegetation and shade screening, street-network measures, walking access, population and employment allocation, planning, festival routes, POIs and fine grids. Building energy values remain estimates; age years, intervals and unresolved evidence remain separate; proposal layers remain proposals. A pre/post-2011 class records timing and does not establish earthquake causation.

Source date, survey year, model edition, acquisition date and this 4 November export date remain separate. Source registers retain their license and attribution information. Missing dates or licenses remain unrecorded. Archived methods describe their original extents and are not rewritten as results for the clipped area. The source files were read without editing them. The live QGIS connection was unavailable, so the input is the saved current master plus saved complementary analyses.
