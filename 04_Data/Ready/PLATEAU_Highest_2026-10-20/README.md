# Current PLATEAU building geometry · 20 October 2026

The current display contains **1,074 original LOD2 building objects**, including **277 in the primary area**. Every object matches an original CityGML gml_id and the fixed Figure 5 GIS asset_id. No fallback LOD, exterior object, crossing object or texture is added.

LOD2 adds source roof and wall detail. It does not imply a new survey or better measured positional accuracy. The dataset release is 2025; source creation dates and use-survey years remain separate in the per-building index.

## Files

- kajicho-current-untextured.glb: 68,554 original-surface triangles, about 6.6 MiB. One named node per GIS asset_id, with source ID, actual LOD and primary flag in node extras.
- geometry-index.json: original IDs, membership, source surfaces, elevations and provenance.
- geometry-summary.json: source checks, actual coverage and coordinate definitions.
- geometry_quality.json: edge screening for each object.
- projection_boundary_quality.json: all source LOD2 horizontal projections checked against the unchanged corresponding Figure5 traces; zero outside projection area for1,074 wider and277 primary models.
- detail_examples.json: five primary-area examples comparing source geometry with the previous flat extrusion.
- source_triangles_local.npz: full-precision local source vertices for inspection and later preparation, without textures.

## Coordinates

Original CityGML declares **EPSG:6697**, with latitude, longitude and orthometric elevation. Horizontal coordinates are projected from JGD2011 geographic coordinates (EPSG:6668) to Japan Plane Rectangular CS IX (EPSG:6677). The original elevation is kept unchanged.

Three.js / glTF uses metres:

- x = easting + 5600
- y = original CityGML elevation
- z = -(northing + 34320)

No ellipsoid-to-geoid conversion, per-building vertical adjustment or terrain surface is used in the final asset. The original 3D Tiles were downloaded and their per-feature LOD was checked, then the final model was built directly from the original CityGML surface polygons to retain their coordinates.

## Quality and use

All 1,074 objects match current GIS membership and have finite coordinates. Edge screening after welding at 0.1 mm found no boundary edge and no edge incident to more than two triangles. This check does not establish freedom from self-intersections, correct terrain contact or CFD solver suitability.

Use this model for visual field preparation and geometry review. Prepare a separate simplified numerical model for CFD. Keep historical CFD fields with their original geometry.

For example, primary building bldg_969fc1c3-0999-4673-b863-efa7b3aa4d13 has 258 source triangles and 14 distinct elevation levels at centimetre grouping. Its previous flat extrusion used 76 triangles and two elevation levels. This is added geometric detail, not a positional accuracy estimate.

## Reproduction on the remote host

Use the current GIS package and the original CityGML members recorded in geometry-summary.json. Raw originals remain on the server.

1. Run acquire_current_plateau_geometry.py to preserve the official current catalog queries and untextured leaf tiles.
2. Run extract_plateau_tile_geometry.py to check per-feature tile LOD and preserve the temporary index under raw/plateau/Highest_Geometry_2026-10-20/Tile_Extraction.
3. Run build_source_plateau_geometry.py to triangulate original CityGML LOD2 surfaces and write the final display asset.

The source-surface builder checkpoints each completed source file. No solver, shadow calculation or thermal simulation is run.

## Sources and rights

- [Official PLATEAU delivery API](https://docs.plateauview.mlit.go.jp/api/rest/operations/datacatalog3dtilesspectilesetjson/): maximum-LOD queries and current-year selection.
- [PLATEAU visualization conversion specification](https://docs.plateauview.mlit.go.jp/spec/visualization/): LOD bundles may contain lower-detail fallback objects, so actual LOD is checked per feature.
- [PLATEAU development guide](https://www.mlit.go.jp/plateau/learning/plateau-development-chart/): LOD and building identifiers.
- [PLATEAU site policy](https://www.mlit.go.jp/plateau/site-policy/): public-data terms compatible with CC BY 4.0; original municipality copyright remains.

The official catalog queried on 20 October 2026 resolves maximum outdoor building LOD for both Chiyoda and Chuo to 2025 LOD2. LOD3 and LOD4 return no dataset. Original CityGML source files and the new raw tile downloads are retained remotely. No result is copied to the local computer.
