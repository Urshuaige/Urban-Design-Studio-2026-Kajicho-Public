Kajicho Primary Area buildings
26 November 2026

Extract Kajicho_Primary_Buildings_ArcMap.zip and add Buildings_Kajicho_BYear0.shp.
Keep the SHP, SHX, DBF, PRJ and CPG files together.
In ArcMap open Layer Properties > Symbology > Categories > Unique values.
Set Value Field to Byear, click Add All Values, then Apply.
The layer contains 277 building models. Label Byear = 0 as Unknown.
The supplied register gives 221 years and leaves 56 unknown.

The 2D layer carries the 47 original fields and linked public attributes.
Use Building_Fields.csv to look up the short ArcMap field names.
The population and energy values are published estimates. A building ID
without a matched thematic record has missing values. Use the companion
Primary_Buildings_Full.gpkg for all source columns and native null values.
Shape_Leng and Shape_Area retain their original source values. Measure
the new geometry directly when you need planar lengths or areas.

The map footprints combine horizontal projections per model. They can
include roof overhangs. Ground, wall and roof appearance faces are in
Primary_Building_Surfaces.gpkg. Face classes use surface slope and height
above each model base. They describe display groups from source geometry.
Open the 2D SHP for analysis and ArcMap fills. Open the separate surface
layer for 3D display. Each layer uses EPSG:6677, metres.

The supplied age source date, method and licence are unrecorded.
Prior projected PolygonZ source, 24 November 2026:
https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho-Public/blob/cb212c2236dd802bbe6bd597443c982536df453b/04_Data/Ready/QGIS_Current_2026-11-04/shp/Primary_Building_Age_2026-11-13/Buildings_Kajicho_BYear0.shp
