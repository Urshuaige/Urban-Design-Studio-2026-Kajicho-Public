# Environmental methods for the next studio stage

Prepared 20 October 2026. Targeted primary-source verification of the existing integrative review. This document prepares decisions; no mesh, radiation calculation, benchmark or solver was started.

## Recommended route

Start with a timed walking route or a small group of public spaces in the Kajicho primary area. Record who uses it, the relevant hours, the design action and the organisation able to maintain it. The verified Figure 5 outlines and current whole-footprint building inventory remain the reporting basis. A wind or shade model also needs surrounding obstacles outside these outlines.

**Survey → geometry → shade/radiation → optional mean-wind pilot → paired design comparison.** Use the simplest model that can answer the selected question and retain the same places, times and forcing when comparing alternatives. A complete district CFD run is not a prerequisite for choosing a useful shade intervention.

## Methods and resolution

| Task | Proposed first method | Resolution and scope | Verification |
|---|---|---|---|
| Field survey（场地调研） | A fixed reference station plus repeated route observations; georeferenced photos and a street/trees/materials checklist | Choose stations at exposed, shaded, narrow and sheltered locations; document height, clock, instrument and obstruction | Co-locate instruments first; retain a separate check visit; compare time-matched rather than differently timed points |
| Shade（遮阴） | Solar obstruction from verified building and tree geometry | Proposed 2 m district screen, 1 m pilot; use 0.5 m only as a local sensitivity check where walkway or shade-edge width needs it | Check observed shadow edges at surveyed times and compare route-level shaded duration across grids |
| Radiant heat（辐射热） | SOLWEIG with aligned DSM/DEM, canopy/trunk grids, weather and surface parameters | Pin the stable release documented in the manual; start from the verified pilot geometry/grid | Check weather timestamps, material assumptions and measured radiation/exposure; report mean radiant temperature separately from air temperature |
| Wind screening（风环境筛查） | URock where flat-terrain and empirical-obstacle assumptions fit | Proposed 2 m start and 1 m pilot comparison; these are starting values, not validated accuracy | Check street wind observations and sensitive tree/wake locations before interpreting a cluster |
| Mean wind（平均风） | Optional steady, isothermal RANS pilot after the wind question is selected | Local refinement around the pilot, coarser surroundings and free air; set spacing by obstacle/gap dimensions, receptor height and wall model | Benchmark, three mesh levels, domain/inlet tests, convergence of target values and mass balance, independent field observations |
| Gusts or coupled heat（阵风或风热耦合） | A separate escalation decision | LES for a transient-turbulence question; a thermal solver when buoyancy/air-temperature change is the target and thermal inputs exist | Additional inflow, time-step/sampling and thermal-boundary evidence; heat balance for a thermal calculation |

The shade/radiation grid lengths above are studio proposals. They are not an academic standard. A 2 m grid cannot resolve every narrow pavement; use the field dimensions to decide whether a finer pilot grid or explicit geometry is necessary. An overhang or railway undercroft can be important despite being poorly represented by a single-height raster.

### CFD mesh selection

COST 732 makes grid choice dependent on the problem. Its initial guidance uses at least ten cells per cube root of building volume and ten across a building separation, followed by refinement. For RANS it describes three systematic grids for an error estimate where extrapolation assumptions hold. It permits local refinement when global refinement is impractical. Its geometry/domain discussion includes distance-dependent detail and context buildings within six times their own height of the interest area; urban boundary distances still need sensitivity checks. [COST 732, §§5.4–5.5, 5.8](https://www.theairshed.com/wp-content/uploads/2018/03/COST-732-Best-Practice-Guideline-May-2007.pdf)

For this studio, 1–2 m local horizontal cells may be a starting envelope in ordinary 10–20 m gaps. A 5 m passage needs about 0.5 m spacing to obtain ten cells across it. Vertical near-ground layers must resolve the receptor independently of that horizontal spacing. These are conditional examples, not fixed mesh settings.

Fine local cells are established practice when the question requires them: the City of London specifies cells no larger than 0.3 m at critical entrances/corners, at least ten across street canyons and three prism layers below 1.5 m, while allowing coarser geometry farther away. It identifies realizable k-epsilon as an industry option and allows suitable alternatives. This is a useful practice precedent; its climate, direction count, domain inventory and compliance thresholds are specific to London. [Wind Microclimate Guidelines, pp.13–15](https://www.cityoflondon.gov.uk/assets/Services-Environment/wind-microclimate-guidelines.pdf)

Thus the proposed pilot can refine a small critical patch to approximately 0.3–0.5 m when necessary. The whole 41.99 ha district should not receive that spacing by default. The actual grid remains unset until the street widths, relevant details, domain and decision variable are known.

### Choosing wind physics

URock initializes empirical obstacle zones and mass-balances the flow. Its original evaluation identifies tree-wake problems and a general bias in compact districts; the presented version assumes flat terrain. It is appropriate to test as a screening tool, with those conditions checked. Its results are not interchangeable with a validated Navier–Stokes solution. [Bernard et al., 2023, §§2, 4.6–5](https://gmd.copernicus.org/articles/16/5703/2023/)

The AIJ lineage includes the benchmark-based 2008 guideline, an expanded Japanese guidebook in 2020, and a new LES guideline in February 2026. The last item's existence and scope were verified from publisher/author metadata; its full numerical prescriptions were not accessible. Before any LES work, read that full guideline. Selecting RANS for an initial mean-wind question is a studio choice; a gust/transient question calls for a different plan. [AIJ benchmark index](https://www.aij.or.jp/jpn/publish/cfdguide/index_e.htm), [Okaze et al., 2026](https://doi.org/10.1016/j.jweia.2025.106321)

A single chosen hot afternoon is a scenario, not an annual pedestrian wind-comfort assessment. Annual/seasonal comfort requires a climate distribution and a declared assessment method, including treatment of gusts where relevant. The London guidance illustrates that distinction; its local wind statistics cannot be transferred to Tokyo.

### Thermal outputs

The official SOLWEIG manual lists 2025a as stable and 2026a as development in the documentation checked on 20 October. Its geometry grids require common extent and resolution. Required forcing includes temperature, humidity and solar radiation; thermal indices also require wind. Keep the model version and material parameters in the input manifest. [SOLWEIG manual, §§12.2.1–12.2.3, 12.2.10](https://umep-docs.readthedocs.io/en/latest/OtherManuals/SOLWEIG.html)

A new wall-temperature scheme has a final 2026 paper. Its evaluation uses two white wall materials in a small Gothenburg courtyard, at 0.5 m resolution; that case does not prescribe a 0.5 m Tokyo district model. The paper reports remaining transition/storage effects and explains its simplified heat treatment. New material inputs should be checked where they change the intervention comparison. [Wallenberg et al., 2026, §§2–4](https://gmd.copernicus.org/articles/19/1321/2026/gmd-19-1321-2026.html)

Use mean radiant temperature（平均辐射温度）and shaded route duration as direct outputs for a shade question. Add UTCI（通用热气候指数）only with a documented wind-height convention and applicability checks: the official polynomial expects 10 m wind and lists 0.5–17 m/s. Do not silently substitute a pedestrian-height value or hide calm-wind clamping. If a tool converts heights internally, apply that conversion once and record it. [UTCI calculator](https://www.utci.org/utci_calc.php)

Coincident weather, wind and radiation are also used in planning practice. The City of London's thermal guidance provides an example of hourly, seasonal analysis with stated early-stage simplifications; Tokyo needs its own local weather and use patterns. [Thermal Comfort Guidelines, §§7–9](https://newsite.cityoflondon.gov.uk/assets/Services-Environment/thermal-comfort-guidelines-for-developments-in-the-city-of-london.pdf)

## Reuse and rebuild

| Reuse after a source check | Rebuild for the revised physical model |
|---|---|
| Official source files, original object IDs, source metadata and current Figure 5 traces | Per-object highest available LOD coverage and geometry quality audit |
| JMA source observations and quality flags | Common-grid surface/canopy inputs, sky view, shade masks and exposure samples |
| Checked parsers, GIS joins and conservation diagnostics | Wind context, wind-aligned air domain, boundary conditions, mesh and probes |
| Existing survey/POI records as leads for a field visit | Physics outputs when geometry, weather, materials or model assumptions change |

The current 1,074 wider-area and 277 primary-area objects describe the frozen 18 October inventory. Keep those source IDs and explain any count changes caused by a new official data version or footprint interpretation. Crossing/exterior buildings remain excluded from the reported building analysis while remaining eligible physical context for wind and shading.

Keep three geometry products linked by IDs: an untextured scene using the highest verified available official LOD; radiation occluders suited to the chosen method; and repaired CFD solids. Preserve roof forms, setbacks, passages and local details that affect the question. Resolve self-intersections, duplicates and tiny slivers rather than sending the maximum triangle count directly to a flow mesh. COST 732 supports testing which omitted details affect the local result.

The archived CFD fields are not numerically accepted for the current scope. A reporting-mask-only change could reuse an accepted field only if its coverage and physical inputs remain valid; that condition has not been established for these legacy trials. Their old iteration counts and displayed precision do not provide new-scope validation.

## Validation and feasible execution

Before future execution, record the effect the team needs to distinguish and the uncertainty that would change the design decision. Choose common probe locations and comparison hours. Separate four checks: geometry/forcing, numerical solution, field/benchmark agreement, and the design comparison.

For CFD, use a relevant AIJ benchmark with documented inlet and measurement locations, then compare the site pilot with independent time-matched observations. Track target values and conservation balances alongside residuals; COST 732 explicitly distinguishes these. The old project residual/imbalance screens can remain recorded screens, but their numbers are not universal physical-validation thresholds. Report RMSE（误差幅度）, bias（平均偏差）and the spread by location/weather where observations allow. Acceptance should reflect instrument uncertainty and the decision's required effect.

After execution is separately authorised, inspect live host resources and measure one representative unit for the actual software/geometry. Record cells, memory, iterations or time steps, throughput and I/O, then estimate the complete comparison. Use free compatible GPUs when supported and faster, distribute independent units together, and checkpoint completed units. No timing benchmark is run by this plan, and no wall-clock cap or arbitrary fixed memory cap is proposed. Select the least costly model/grid that preserves the decision within the measured uncertainty; extra detail is justified by a changed conclusion or a required physical process.

## Digital model and digital twin

A clearer untextured scene can improve geometry inspection and communication now. To develop it into a digital twin, specify the physical counterpart, the observations that refresh it, the decisions returned to the site, the update interval and the validation range. The UK government's 2025 definition uses those links and assumptions; it is an operational reference, rather than a universal definition. Until these links exist, describe the platform as a shared digital site model and scenario workspace. [Digital Twin (official)](https://www.gov.uk/government/publications/digital-twin-definition/digital-twin-official)

## Team discussion before a run

Select one route or public-space cluster, its users and hours, and one physical action. Check which instruments and site access are available. Decide whether the question is primarily shade/radiation, mean ventilation or gust safety; that choice determines the next model and its verification. The current task authorises planning, source/geometry work and cleanup; it does not authorise a new environmental simulation.
