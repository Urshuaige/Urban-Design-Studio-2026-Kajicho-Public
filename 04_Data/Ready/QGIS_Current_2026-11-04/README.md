# Kajicho wider boundary GIS data

This delivery uses the current **wider boundary, 42.43712 ha**, to select local data. Buildings intersecting any part of the boundary retain their complete source footprints, including parts outside the line. It uses the `study_area` polygon saved on 29 October 2026. Kanto-wide original population and migration tables are excluded.

Clone the repository or download its ZIP. Keep this folder intact and open `Kajicho_Current_Data.qgz` in QGIS. All delivered files are ordinary Git files; Git LFS is not required. This is a data browsing project with relative paths. The original slide layouts remain in their dated local projects.

## Primary buildings · 26 November 2026

[Download the ArcMap-ready building ZIP](https://raw.githubusercontent.com/Urshuaige/Urban-Design-Studio-2026-Kajicho-Public/main/04_Data/Ready/QGIS_Current_2026-11-04/shp/Primary_Building_Age_2026-11-13/Kajicho_Primary_Buildings_ArcMap.zip). Extract it and add `Buildings_Kajicho_BYear0.shp`. The 2D layer contains one horizontal model projection for each of the 277 Primary Area records. Use `Byear` for unique values. The 221 recorded years retain their source values. Label `0` as unknown for the remaining 56 buildings.

The SHP contains all 47 supplied fields and additional public building attributes. It includes building use, height, floor area, planning, energy, population allocation and renewal evidence by building ID. See the [field map](shp/Primary_Building_Age_2026-11-13/Building_Fields.csv) for shortened ArcMap field names. Four separate theme tables match 256 of the 277 IDs. The remaining 21 have missing values for those joins. [Release counts](shp/Primary_Building_Age_2026-11-13/Release.json)

- [Full building attributes](data/Primary_Buildings_Full.gpkg) retains all 741 source and joined fields, long strings and null values. The dBASE limits for a Shapefile restrict its columns and record width.
- [Appearance surfaces](data/Primary_Building_Surfaces.gpkg) keeps the original Z values for 6,949 faces. The Base, Roof and Wall classes use face slope and height above the model base. Use this layer to style the 3D model.
- [Current QGIS map](Kajicho_Current_Data.qgz) colors the 2D SHP by year. The full attribute layer and styled 3D faces are in the optional Primary buildings group. The older age views provide context outside the Primary Area.

The supplied age file arrived on 13 November 2026. It did not specify the underlying survey date, method or reuse licence. The 2D outlines can include roof overhangs. Published energy and population estimates retain their source definitions. The [original projected PolygonZ](https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho-Public/blob/cb212c2236dd802bbe6bd597443c982536df453b/04_Data/Ready/QGIS_Current_2026-11-04/shp/Primary_Building_Age_2026-11-13/Buildings_Kajicho_BYear0.shp) is available at its dated revision.

## Contents

The package contains **179 SHP datasets**, **14 nonspatial tables**, **194 GeoPackage tables** and **17 cropped rasters**. The QGIS project has 354 vector views plus the rasters. [Find data by layer name](metadata/Layer_Index.csv) or [browse sources and methods](SOURCES.md).

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

All current spatial layers use EPSG:6677, including the Primary building-age SHP from 13 November. The Primary SHP codes 56 unknown years as `0`. The full GeoPackage stores them as nulls. The 4 November SHP exports use at most 255 DBF fields. Each `_fields.csv` maps original field names to short DBF names and identifies fields retained only in the full CSV. Join `_full.csv` to SHP through `ROW_ID`. GeoPackage retains full field names, text, types and nulls. Complete building geometry matches the saved source exactly. One employment-allocation SHP record retains all ring coordinates but its microscopic rings are regrouped by the SHP reader; use its GeoPackage for the exact ring structure. The record is identified in `metadata/Validation.json`.

`NUL_BITS` marks missing values using bit positions in the field map. Numeric `-9999` and text `<NULL>` are placeholders only where the corresponding bit is set. CSV nulls use `<NULL>`; exact null/string distinctions remain in GeoPackage. Numeric SHP values have eight decimal places.

## Sources and interpretation

The saved inputs cover building use and age evidence, renewal screening, energy and carbon estimates, vegetation and shade screening, street-network measures, walking access, population and employment allocation, planning, festival routes, POIs and fine grids. Building energy values remain estimates; age years, intervals and unresolved evidence remain separate; proposal layers remain proposals. A pre/post-2011 class records timing and does not establish earthquake causation.

Source date, survey year, model edition, acquisition date and this 4 November export date remain separate. Source registers retain their license and attribution information. Missing dates or licenses remain unrecorded. Archived methods describe their original extents and are not rewritten as results for the clipped area. The source files were read without editing them. The live QGIS connection was unavailable, so the input is the saved current master plus saved complementary analyses.
