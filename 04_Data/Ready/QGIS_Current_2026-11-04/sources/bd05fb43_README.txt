# Kajicho: QGIS analysis foundation

This package brings together the current study boundaries, the 2025 Kanda Festival route records, thematic QGIS exports, a 50 m analysis grid and a first functional concept informed by Kevin Lynch's five elements of city image. All new maps are PNG exports from QGIS layouts.

## Open the work

Open `Kajicho_Analysis_Foundation.qgz` in QGIS with T7 mounted at its usual path. The project refers to existing source data on T7; the `.qgz` alone is not a portable copy of those sources. The new layouts begin with `Foundation —` and the new layers are grouped under `Analysis foundation — 30 Oct 2026`. The two current study boundaries are used: solid for the primary area and dashed for the wider area.

`Kajicho_Analysis_50m_and_Concept.gpkg` contains the editable grid, concept districts, paths, railway edge, nodes and landmarks. The grid is clipped to the current wider boundary. The four concept districts are broad working areas, not statutory zones or individual plots.

## Maps

- `maps/01_Festival_All_17_Routes.png`: all 17 recorded route features, grouped by event. Lines can overlap; read the event maps alongside it.
- `maps/02_Festival_Shinkosai.png`, `03_Festival_Mikoshi.png`, `04_Festival_Tsukematsuri.png`: separate maps for the three event groups.
- `maps/05_Festival_Kajicho_Detail.png`: Kajicho's Group 7 at a local scale.
- `maps/06_Concept_Districts_and_Lynch.png`: a first discussion drawing combining the five elements with proposed functions and green links.
- `maps/07_Grid_Mapped_Building_Use.png`: dominant mapped building use in each 50 m cell.
- `maps/08_Grid_Flood_and_Parking.png`: the 2018 Kanda River basin maximum flood scenario and 2021 mapped outdoor parking.
- `maps/09_Town_Population_Density.png` and `10_Town_Employment_Density.png`: whole-town statistics for 2026 and 2021 respectively.
- `maps/11_Festival_Map_For_Slide.png`: QGIS map-only export for the presentation.
- `maps/qgis_existing_layouts/`: exports of the existing project layouts. Layouts 11–13 are earlier pilot results based on an earlier boundary; do not use them as current-boundary analysis without updating them.

See `Findings_and_Concept.md` for findings, proposed functions, methods and sources. Scripts and export receipts are in `work/`.

The current [Figma Slides](https://www.figma.com/slides/LVGelE7YnrzIXn5ySzE7XX), `Kajicho_Site_Analysis_Review_2026-10-30.pdf` and `Kajicho_Site_Analysis_Review_2026-10-30.pptx` include the updated festival page. The functional concept remains a separate draft map and is not yet a slide. The PPTX keeps editable text and shapes; maps and photos are images.

`tables/50m_cell_attributes.csv` is an attribute-only copy of the 50 m layer; whole-town totals repeat and must not be summed over cells. `tables/concept_districts.csv` lists the four broad working districts.
