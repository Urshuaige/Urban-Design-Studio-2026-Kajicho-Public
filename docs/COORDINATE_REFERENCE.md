# Coordinate reference for Kajicho

Use **EPSG:6677** (JGD2011 / Japan Plane Rectangular CS IX) for local QGIS analysis, spatial joins, planar distances and areas. Easting and northing use metres. The five QGIS projects use this CRS, and the spatial layers displayed by the current project use it as well. [Japan zone IX](https://www.gsi.go.jp/LAW/heimencho.html) · [Current GIS guide](../04_Data/Ready/QGIS_Current_2026-11-04/README.md)

| Data | Coordinates and access |
| --- | --- |
| Primary building age | The supplied file used EPSG:4326 (WGS 84 longitude and latitude). The [current PolygonZ Shapefile](../04_Data/Ready/QGIS_Current_2026-11-04/shp/Primary_Building_Age_2026-11-13/) uses EPSG:6677. The update transforms the horizontal vertices and retains feature order, ring parts, attributes and Z values. |
| Building height, older age views and current GIS | Use the existing EPSG:6677 layers from the [current QGIS project](../04_Data/Ready/QGIS_Current_2026-11-04/Kajicho_Current_Data.qgz). |
| PLATEAU source extents | The four saved excerpts use EPSG:6668 (JGD2011 geographic). For these same records in metres, use the [EPSG:6677 GeoPackage](../04_Data/Ready/Public_Baseline_2026-10-14/Source_Extents_6677.gpkg). It contains 60 flood, 1,315 land-use, 969 transport and 37 planning records with their source fields and IDs. |
| Browser maps | The standard [GeoJSON](https://www.rfc-editor.org/rfc/rfc7946#section-4) display exports use WGS 84 longitude and latitude. The website mirror includes those exports. GeoJSON files named with `6677` are projected GIS products with an explicit CRS. |
| CFD and 3D model files | Model coordinates are measured in metres from their recorded origins. The model metadata defines how they align with the EPSG:6677 map. [CFD domain and origin](CFD_DOMAIN.md) |

## Primary building-age source

`Buildings_Kajicho_BYear0.geojson` was supplied on 13 November 2026. The original source, data year and reuse licence for the supplied construction years are unrecorded. Identify the supplied layer and this provenance gap when citing it. It contains 277 models, with 221 supplied `Byear` values and 56 missing values.

The 24 November update uses GDAL and PROJ for the horizontal transformation. The original record and ring order, DBF attributes and Z and M values were verified byte for byte. Source numeric fields retain their supplied values and units. Derive planar areas and distances from the projected geometry. [CRS update record](../04_Data/Ready/QGIS_Current_2026-11-04/metadata/CRS_Update_2026-11-24.json) · [Esri PolygonZ format](https://content.esri.com/support/whitepapers/ao_/shapefile.pdf)
