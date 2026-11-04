# Sources and methods

The links below come from the project's saved source registers. Their original access dates and source years remain in the archived records. The export date is 4 November 2026; it is not a new access date for every source.

| Data | Source entry | Interpretation |
| --- | --- | --- |
| Building models and use | [PLATEAU Chiyoda 2025](https://www.geospatial.jp/ckan/dataset/plateau-13101-chiyoda-ku-2025), [PLATEAU open data](https://www.mlit.go.jp/plateau/open-data/) | Model edition and attribute survey years are separate |
| Base maps, terrain and aerial photographs | [GSI maps](https://maps.gsi.go.jp/), [GSI dated aerial layers](https://maps-cf.gsi.go.jp/help/intro/looklist/2-nendai.html), [GSI photograph archive](https://service.gsi.go.jp/map-photos/app/help) | Preserve image year ranges, resolution and acquisition evidence |
| Population and administrative areas | [e-Stat GIS](https://www.e-stat.go.jp/gis), [National Land Numerical Information](https://nlftp.mlit.go.jp/ksj/) | Census areas and allocated building values have different spatial units |
| Parks and street trees | [Tokyo park data](https://data.storage.data.metro.tokyo.lg.jp/toshiseibi/01_kouenryokuchi.zip), [Tokyo street-tree data](https://data.storage.data.metro.tokyo.lg.jp/toshiseibi/02_gairoju.zip) | Source coverage and field observations remain distinct |
| Energy benchmarks | [Tokyo benchmark ranges](https://www.kankyo.metro.tokyo.lg.jp/documents/d/kankyo/benchmark_range_202503), [DECC overview](https://www.jsbc.or.jp/decc/outline_level1.html) | Read the saved methods for the factors actually used and pending inputs |
| Roads and points of interest | [OpenStreetMap](https://www.openstreetmap.org/), [Overpass API](https://overpass-api.de/) | Query dates and tags remain in source records; retain OpenStreetMap attribution |
| Building-age evidence | [Chiyoda building-plan summaries](https://www.city.chiyoda.lg.jp/koho/machizukuri/kenchiku/shome/etsuran-copy.html), [register certificates](https://www.city.chiyoda.lg.jp/koho/machizukuri/kenchiku/kakunin/shome.html) | Public records, property listings and image-based bounds retain separate confidence |

## Dataset-level links

- [Source_Links.csv](metadata/Source_Links.csv): links extracted from dataset attributes and QGIS metadata, with dataset and field identifiers.
- [Document_Links.csv](metadata/Document_Links.csv): links extracted from the archived source and method records.
- [Source_Documents.json](metadata/Source_Documents.json): original document paths, archived filenames and SHA-256 checksums.
- [Datasets.json](metadata/Datasets.json): source table, CRS, original field names, source-year and method samples, export details and validation.

Each source keeps its own license and attribution terms. Where a source record lacks a license or acquisition date, that information remains unknown. The original source register and complete native fields take precedence over sampled metadata values.
