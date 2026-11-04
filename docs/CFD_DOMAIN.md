# CFD domain and boundaries

The design evaluation area is Kajicho 1 & 2. Explicit building coverage determines which obstacles enter the model. The air domain also includes upstream, downstream, lateral and top buffers; an air buffer does not imply that every building within it is modelled explicitly.

COST 732 (2007), §5.5, printed p.16, uses each building's own height Hn when screening distant buildings; distance below 6Hn is a minimum inclusion recommendation. Sections 5.4–5.6 also call for geometry, boundary and inflow-preservation checks. These recommendations mainly concern neutral steady wind. They provide an initial extent here; the non-isothermal roof-heat model needs its own validation.

Original geometry combined fixed 500 m coverage with building-specific 6Hn screening. The 500 m distance is a project setting; continuous 750 m coverage and 10Hn are comparison settings. They are not universal urban-model distances. The tallest retained building has H=235.2 m, giving 5H=1176 m, 15H=3528 m and 6H=1411.2 m. Upstream 5H, downstream 15H and a top 5H above the tallest building were conservative starting choices around retained geometry.

| Input/candidate | Building objects | Air domain, km | Status |
| --- | ---: | --- | --- |
| Legacy published input | 3805 | About 6.18 × 7.30 × 1.41 | Website/QGIS iteration-100 field |
| Completed 6H, wide domain | 3806 | 8.640 × 7.552 × 1.472 | Used by reference and light trials; neither fully accepted |
| Continuous 750 m + 10H, wide domain | 6520 | 8.640 × 7.552 × 1.472 | Prepared; comparison not run |
| Same 6H buildings, closer lateral boundary | 3806 | 6.272 × 7.552 × 1.472 | Prepared; comparison not run |

Trial domains align with the same 64 m global grid. The blockage proxy divides the union of wind-facing projections by air-domain cross-section, counting overlaps once. Meeting this geometric ratio alone does not establish sufficiently small wind or temperature error.

Retaining all valid positive-height, positive-area objects added one approximately 0.534 m² object. Its boundary exists in the reference mesh; the light mesh does not resolve an independent roof and records it as unresolved. Local mesh and extent checks are needed for designs involving narrow streets or differences close to numerical variation.

Exact coordinates, screening and candidates are in `04_Data/Ready/CFD_Domain_Audit_2026-10-14/Domain_Audit.json`, `Wider_Building_Screen.json`, `Small_Object_Review.json`, `Sensitivity_Plan.json` and `Next_Run_Inputs/`. The [layer catalog](../04_Data/Metadata/Layer_Catalog.csv) identifies GeoPackage layers. Code: `08_Scripts/audit_cfd_domain_v4.py` and `prepare_cfd_domain_case_v4.py`.

Sources: [COST 732](https://www.airshed.co.uk/wp-content/uploads/2018/03/COST-732-Best-Practice-Guideline-May-2007.pdf), [University of Hamburg index](https://www.mi.uni-hamburg.de/en/arbeitsgruppen/windkanallabor/documents.html), [OpenFOAM 2412 solver](https://api.openfoam.com/2412/buoyantBoussinesqSimpleFoam_8C.html). Current findings: [CFD status](CFD_STATUS.md).
