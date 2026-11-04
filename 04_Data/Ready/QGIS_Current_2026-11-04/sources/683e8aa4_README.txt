# Building evidence around 11 March 2011

Checked 4 November 2026. This is a source audit and ten-building feasibility pilot, not a completed building-age reassessment.

## Findings

The existing slide dataset contains 1,064 research building models. Its original construction-year field has no valid years. Supplementary public records provide 273 single years: 249 before 2011 and 24 after 2011. These supplementary records include property listings and name/spatial matches; they are not all official building-register records. Another documented opening in 2005 establishes a pre-2011 upper bound without supplying an exact completion year.

The derived 2011 classification therefore contains 250 before-2011 records, 24 after-2011 records and 790 unresolved records. Within the existing primary-area age dataset, the corresponding counts are 72, 7 and 178 (257 models). These are the supports of the age slide dataset, not the different current-stock or renewal denominators.

No new exact completion years were assigned. The original database, live QGIS project, Google Slides and Figma were not modified.

## What the pilot tested

Ten unknown-year models near the center of the primary area were selected from footprints of 30–180 m² and heights below 30 m. Their footprints were overlaid on cached GSI FY2009, FY2014 and FY2019 orthophotos and an existing January 2026 Esri reference. The selection is a local feasibility sample, not a representative estimate of the unknown stock.

The images show substantial roof displacement relative to ground footprints, different viewing directions, shadows and roof-surface changes. A building footprint intersecting visible roof pixels is insufficient to establish that the current building is the same structure. The pilot is useful for locating candidates and visible changes; it did not justify filling exact ages for these ten objects.

All four PNGs use the same EPSG:6677 extent. Yellow polygons and numbers are current building models, not historical footprints. Source raster resampling to 0.5 m and export enlargement do not improve the original image resolution. FY2009 identifies a fiscal-year interval, not an exact capture day. Full input paths, selection rule and extent are in pilot_method.json. The current Esri/Vantor reference is for local analysis and is not a public slide asset.

## New source route verified on the site

Google Maps Street View was inspected at the former Imagawa school, approximately 35.69194 N, 139.77323 E. The visible timeline contains December 2009, June 2013, April 2014, April 2015, March 2016, October 2017, April 2018, May 2019, February 2020, February/June 2021 and August 2022. December 2009 was opened and its date label visually confirmed. This verifies availability at one observation point; it does not establish coverage of every alley or identify each pilot polygon's façade.

Observed December 2009 panorama ID: `qIt_VSlzgYT1pMewCawjyQ`. August 2022 panorama ID: `xpJGOrk0reNWHRQKhamwEw`.

Use dated façade views to match floors, openings, side walls and entrances to the current building. Cross-check them with aerial roof form and a source address. Follow intermediate dates when the form changes. A new form first seen in June 2013 after an old form in December 2009 has a construction interval spanning the earthquake; it cannot be assigned to the post-earthquake category from those two frames alone.

## Recommended evidence fields

Keep exact years and observed intervals separate. Record `asset_id`, source-reported completion year/month, last old-form date, first current-form date, pre/post-2011 class, building-identity match, source URL/panorama ID, and review note. Retain the original source-confidence field.

For unknown small buildings, use this order:

1. Match the current ground-floor address and façade to the model.
2. Compare dated pre-2011 Street View with later views and the current façade.
3. Use GSI dated aerials to check roof form and redevelopment boundaries. Consider GSI's high-resolution online viewing if the ordinary imagery is insufficient.
4. Check owner/architect completion records or building-plan/register records for priority cases.
5. Assign an exact year only from an explicit source tied to the same building; otherwise keep the supported interval or pre-2011 existence category.

Use 11 March 2011 as a temporal reference. The classification does not attribute rebuilding to the earthquake.

## Official records and access

Chiyoda permits free inspection of building-plan summaries within its confirmation authority, including privately confirmed buildings. Summaries pre-dating 1971 are not available through this system, and some 1971–April 1999 records were not retained. Its website describes office inspection and a small, roughly five-location inquiry route, not a downloadable ward-wide age dataset. Confirmation and inspection-certificate dates are useful evidence but should not be relabelled as exact construction completion dates.

GSI's online service offers high-resolution viewing after login and ordinary 400 dpi photograph downloads. Its example distinguishes a 20 cm ground pixel at 1,200 dpi from 60 cm at the downloadable 400 dpi. Coverage, capture date and camera/image geometry must be checked for each source image; higher nominal resolution alone does not solve identity matching.

Google's documentation supports historical Street View via “See more dates”. Historical availability varies by location. Google Earth image dates can be ranges or mosaics, and 3D building imagery combines dates; use dated 2D/history views for temporal evidence.

## Files

- `Building_2011_Evidence.gpkg`: 1,064 original model geometries and attributes copied into `building_2011_evidence`, with derived epoch/basis fields and ten pilot markers. Source attributes retained.
- `Building_2011_Classification.csv`: joinable evidence classification keyed by asset_id.
- `pilot_candidates.csv` / `.json`: ten selected footprints and persistent IDs.
- `FY2009.png`, `FY2014.png`, `FY2019.png`: local review maps, source GSI.
- `Jan2026_local_reference.png`: local-only Esri/Vantor review map.
- `Audit.json`, `pilot_method.json`: counts, rules and provenance.

## Sources checked

- Google historical Street View: https://support.google.com/maps/answer/3093484?hl=en
- Google imagery acquisition dates: https://support.google.com/earth/answer/6327779?hl=en
- GSI aerial archive, resolution and access: https://service.gsi.go.jp/map-photos/app/help
- GSI dated aerial layers: https://maps-cf.gsi.go.jp/help/intro/looklist/2-nendai.html
- Chiyoda building-plan summaries: https://www.city.chiyoda.lg.jp/koho/machizukuri/kenchiku/shome/etsuran-copy.html
- Chiyoda register certificates: https://www.city.chiyoda.lg.jp/koho/machizukuri/kenchiku/kakunin/shome.html

Sources were checked on 4 November 2026; webpage update dates, image acquisition intervals and dataset release years are distinct. Existing GSI imagery was cached on 28 October 2026 and reused. The GSI and Google sources above describe access and interpretation; they do not supply an exact completion year for the ten pilot buildings.
