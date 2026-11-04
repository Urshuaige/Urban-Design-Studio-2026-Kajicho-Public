# Project plan

For saved GIS data through 4 November 2026, use the [current delivery](CURRENT_DELIVERY.md). The planning and numerical statements below retain their stated dates.

Use the [assignment-led research review](Research_Review_2026-10-18/REPORT.md) to compare six technical paths and eight practice mechanisms. Its [visual version](https://kajicho-wind-heat-carbon-demo.specialgooood.chatgpt.site/research.html) provides a common vocabulary for the team.

Current Mapping follows [official brief Figure 5](COURSE_BOUNDARIES.md): primary 10.70383 ha / 277 models / 178 POIs; approximate wider area 41.98967 ha / 1,074 models / 353 POIs. Both source outlines appear in one shared view. Earlier simulations retain their dated inputs.

2026-10-20 · Theme B membership confirmed. Use the [current environmental work plan](Environmental_Work_Plan_2026-10-20/README.md) for fieldwork, reusable inputs, source LOD2 geometry, shade/radiation and conditional CFD. Pilot location, interventions, weights and roles remain team decisions after fieldwork and course discussion.

## Course purpose

Build an area-management model for decarbonisation and climate resilience towards 2050 in Kanda–Nihonbashi, with detailed work in Kajicho 1 & 2. Which combinations of actions can improve energy use and environmental conditions for priority users within existing spatial, ownership, planning and participation conditions, and how can they be delivered and maintained?

The official brief, pp.2,4,7, requires Planning Support and Implementation Support together, explained in a booklet and PowerPoint. The platform on p.2 covers building and vehicle energy/carbon. Page 5 introduces local organisations including Watage and CWL. Page 6 places fieldwork, plans and stakeholders before concepts and drawings.

The working sequence is **issues and beneficiaries → plans and spatial constraints → metrics → suitable analysis → action combinations → actors, investment, maintenance and monitoring**. Calculations support the choice and order of actions.

POI functions now support survey-route and pilot discussions: 353 wider-area destinations and 178 primary-area destinations, with food/services concentrated around the Kajicho–Kanda middle band. Confirm operating hours, pedestrian use and geometry in the field before selecting a design intervention.

## Main work

| Work | Prepare now | After the team selects a pilot | Main outputs |
| --- | --- | --- | --- |
| Buildings and carbon | Use, floor-area proxies and missingness for 1,074 current study objects; use-specific energy ranges and accounting scope | Add DECC/metered energy; choose representative prototypes; use the course platform first, adding building models where needed | kWh/year, purchased-electricity tCO₂/year, before/after ranges, service and cost |
| Shade and radiation | Building shade, routes, nodes and tree survey; dates, times and background weather | Shade duration and radiation on selected streets; UMEP/SOLWEIG when inputs are adequate | Shaded length/area/duration, route exposure, mean radiant temperature Tmrt |
| Mobility | Roads, access points, walking/delivery observations and flow-data gaps | Agree vehicle energy/carbon scope with the course and available data | Activity, mobility service, energy/carbon or explicit gaps |
| Planning and implementation | Plan responses, legal conditions to verify, actors, rights and existing actions | Link each measure to responsibility, participation, permits, capital/operating costs, maintenance and stages | Action cards, actor relationships, a 2050 pathway and monitoring |

Building carbon and street radiation are the main quantitative preparation routes. Implementation support and transport scope proceed alongside them as parts of the course model.

## Choose methods for questions

| Question | Method | Inputs and interpretation |
| --- | --- | --- |
| Which building uses demand more energy? | Use-matched energy-use intensity (EUI) ranges × area; representative building models when inputs arrive | Separate purchased electricity, fuels and primary energy, with year. Retain area and intensity uncertainty in a public-data estimate |
| Where is walking shade missing? | Solar geometry and building obstruction; add measured/recorded crown locations, spread and height | Building shade can be assessed first. Missing tree records do not imply no trees; check resolution for narrow pavements and small shelters |
| How do shade/greenery affect radiant exposure? | SOLWEIG is the preferred candidate, subject to course software and inputs | Consistent DSM/surface/weather extents and pixels. Output radiation and Tmrt; shade share is not air cooling, and this tool is not used here for roof heat flux [S2] |
| Which streets need ventilation checks? | URock as an optional rapid diagnostic | Building heights, wind direction/speed/reference height and actual vegetation inputs. Empirical wind zones with mass-conservation correction support screening; key sites need further checks [S3] |
| Do massing, openings or spacing change local wind? | Local 3D neutral steady RANS when justified | Specific design variables, evaluation points and metrics; empty-domain/public benchmarks, mesh and domain checks; consistent methods and targeted changes |
| Do cool roofs or insulation save energy? | Materials/construction and building-energy models; course platform first, EnergyPlus as a conditional supplement | Operating schedules, envelope and equipment. Halving prescribed roof sensible heat does not establish electricity savings; a single-surface algebraic example is not a building simulation [S4] |
| Which facilities intersect published flood scenarios? | GIS exposure overlays and entrance/equipment surveys | Explicit scenario, year and depth classes. A hydrodynamic model is considered only for a specific design question |

These are project method choices. Tool capability and scientific validation are recorded separately. UMEP/SOLWEIG, URock and building models have not produced newly accepted site results. Confirm tools/versions after the Week 2 software introduction.

## Metrics and interpretation

- Building estimate: `Eᵢ = Aᵢ × EUIᵢ`; A in m², purchased-electricity EUI in kWh/(m²·year), E in kWh/year. `C_grid = Σ(E_grid,i × EF_i)/1000`; EF in kgCO₂/kWh, C in tCO₂/year. Record fuels separately. Annual electricity carbon, local waste heat in W and outdoor CO₂ concentration need separate system boundaries.
- Report district totals and the building groups, routes or nodes actually affected. State area, participation, time and denominators. Where floor area or service changes, compare totals and intensities.
- Energy management without a massing change can reasonably leave neutral wind speed unchanged. Metrics should follow the mechanism changed.
- Radiation comparisons may share background air temperature. Tmrt expresses combined shortwave/longwave radiation around a person, in °C. It differs from air temperature and thermal-comfort indices. Report shade/radiation first if comfort inputs or height conventions are incomplete.
- Use sourced ranges for prototypes, EUI, materials, crowns and implementation rates. If reasonable inputs repeatedly reverse option rankings, report that the evidence cannot yet distinguish them reliably.
- Present-day hot-weather results and the 2050 planning horizon are separate. Future grid factors, demand and climate require sourced scenarios; fixed current weather is not a 2050 climate forecast.

Distinguish source records (including measurement/modelling method), estimates, scenarios and illustrations. Building-model attributes retain survey years and methods rather than being treated uniformly as field measurements.

## Scale and effort

Choose a pilot street and adjacent representative building group before paired option calculations. Record intervention, evaluation, model-context and computational extents separately; radiation, building energy and wind need not share one compulsory domain.

Existing coarse inputs can support district screening. Detailed-street pixels of 1–2 m are only a starting point to test against facility scale, input precision and sensitivity. SOLWEIG rasters must share extent and pixel size; retain surrounding geometry that may obstruct sunlight or affect sky view [S2].

For baseline maps, check source, year, CRS, joins and coverage. Add validation proportionate to a quantitative ranking. Complete an [analysis pilot](../07_Team/Templates/Analysis_Pilot.md) before a new calculation: question, variables, inputs, metrics, scientific scope, checkpoints and diagnostic conditions. Scope concerns comparisons and methods rather than a runtime limit. Keep running and review responsibilities separate.

Retain the unaccepted labels on existing 6000/2000-iteration CFD and add no iterations. Local CFD, passive heat transport and detailed building models need a specific question, suitable data and a new protocol. One-way heat transport also needs a justified treatment of neglected buoyancy feedback; an illustrative Richardson number is not site evidence. Define the scientific scope of repairs and diagnose failures before continuing. No mesh, solver, radiation calculation or timing benchmark is authorized by this planning update.

## Team decisions

1. Priority users, building groups and street issues, checked through fieldwork, sources and interviews.
2. Vehicles, activities and space included in transport accounting; network data do not supply actual flows.
3. Options to compare: retrofit/operation, shade/greenery, combined actions or conditional massing renewal. Existing cool-roof examples do not select the final design.
4. Weights, service levels, cost definitions, owners, reviewers and external contacts.
5. Sites requiring parcel, frontage, road-use, ownership and management permission checks. Existing FAR overlays do not complete legal-capacity review.

Use `07_Team/Demo_Workstreams.csv` and the field, stakeholder and action forms. Leave people and task status open until agreed. Actual-energy input uses `Building_Energy_Input.csv`; dated Public Baseline files include the DECC range template.

## Course stages

| Stage | Course schedule | Project delivery |
| --- | --- | --- |
| Preparation → kick-off | 2026-10-21, 17:00–18:30 JST | Shared maps, sources, gaps, methods and open questions; preserved originals |
| Week 1, 10/26–10/30 | Site, conditions, plans and initiatives; brief lists 10/24–25 as candidate visits | Trees, streets, uses, access and management; observation times recorded, autumn visits separate from summer heat validation |
| Week 2, 11/2–11/6 | Stakeholders, measures, model definition, data/software | Use the mapped study area; agree tools, pilot and roles; reuse course platform first |
| Week 3, 11/9–11/13 | Issues, visions, actions, concepts and drawings | Select comparisons and fix pilot protocol/metrics |
| Interim, 11/18 | 17:00–18:30 JST | Diagnosis, action logic, completed paired evidence and delivery/data gaps |
| Refinement → final | 2026-12-16, 17:00–18:30 JST | Booklet, PowerPoint, 2050 pathway, actors/upkeep and reproducible evidence |

Dates are from brief p.6; follow later course notices for changes. The brief supplies 2050 as the horizon; the team proposes other stages.

## Sources

- **S1:** [Official Theme B brief](https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view), pp.2,4–7. The saved original was reviewed; course requirements and studio method choices are distinguished above.
- **S2:** [Official UMEP SOLWEIG manual](https://umep-docs.readthedocs.io/en/latest/processor/Outdoor%20Thermal%20Comfort%20SOLWEIG.html), for radiation/Tmrt scope, inputs, raster consistency and roof-use limits. Record installed versions separately.
- **S3:** [Bernard, Lindberg & Oswald, URock 2023a](https://gmd.copernicus.org/articles/16/5703/2023/), original method and validation paper, supporting its screening role and limits.
- **S4:** [EnergyPlus](https://energyplus.net/), for building-energy model scope; application needs building and operation inputs.
- Spatial data and old calculation status: [Data guide](DATA_GUIDE.md), [CFD status](CFD_STATUS.md), [Domain](CFD_DOMAIN.md). Official plans and response matrices are in external project storage and must be matched to their areas/sites.
- The supplied `Kajicho_Method_Review_2026-10-15.zip` reviews repository version `5622dc1`. Its five cited diagnostic files were checked against retained originals. Six single-roof tests remain explicitly assumed examples. The original package is in the research archive, available through a maintainer; this repository retains the plan and required protocols.
