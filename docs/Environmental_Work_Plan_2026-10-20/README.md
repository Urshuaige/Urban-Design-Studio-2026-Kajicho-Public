# Next environmental work / 后续环境研究

20 October 2026 · Theme B membership confirmed. This update prepares fieldwork and modelling choices. No environmental solver, mesh, shade/radiation calculation or timing benchmark was started.

Read the [visual work plan](https://kajicho-wind-heat-carbon-demo.specialgooood.chatgpt.site/plan.html), inspect the [current source LOD2 scene](https://kajicho-wind-heat-carbon-demo.specialgooood.chatgpt.site/studies.html), then use [Methods and source evidence](METHODS.md) for technical detail. The [18 October integrative review](../Research_Review_2026-10-18/REPORT.md) remains the broader framework linking climate, energy, mobility, area management and practice cases. This update verifies the environmental calculation choices against primary sources; it is not a new systematic review.

## Scope and current inputs

Keep the official Figure 5 outlines and the original full-footprint membership. The approximate wider study area has 41.98967 ha, 1,074 models and 353 POIs; the primary Kajicho area has 10.70383 ha, 277 models and 178 POIs. The source outlines are registered traces, not a cadastral survey. Modelling uncertainty does not justify redrawing them to preserve buildings.

The scene now reads original CityGML LOD2 roof, wall and ground surfaces for all 1,074 selected objects, including all 277 primary objects. The official catalogue returned no LOD3/4 delivery for Chiyoda or Chuo when checked. The previously available raw source contained this roof detail; the earlier platform scene used extruded footprints. The new scene replaces that default scene, with no textures. See [acquisition and geometry record](../../04_Data/Ready/PLATEAU_Highest_2026-10-20/README.md).

The model preserves source IDs and orthometric heights. Its complete horizontal projection, including represented roof overhangs, stays within the corresponding fixed outlines: zero outside area for wider and primary sets. At 0.1 mm coordinate welding tolerance, edge screening found no boundary edges or edges incident to more than two triangles. Self-intersection, terrain contact, tree/canopy completeness and current street changes still need checks for the chosen physics. LOD2 describes geometric detail; it does not establish new survey accuracy.

## Reuse or rebuild

| Input | Reuse | Rebuild or verify |
|---|---|---|
| Reporting scope | Figure 5 traces, GIS joins, source IDs, current 1,074 / 277 inventory | Model masks, route samples and surrounding obstacles for each physical question |
| Building data | Original CityGML, use attributes, source dates and source LOD2 surfaces | Separate display scene, radiation occluders and repaired CFD solids, linked by ID |
| Weather | Existing JMA 2025 observations and quality flags | Relevant hours, two missing wind hours, time zone, solar inputs, wind reference height and local exposure |
| Street and POI leads | Current classified POIs, roads, existing tree records and planning sources | Operating hours, users, deliveries, access, crowns, trunk clearance, canopies and surface materials in the field |
| Analysis code | Checked parsers, coordinate joins, diagnostics and plots | Model versions, input manifests, mesh, probes, sky view and all outputs affected by revised geometry or forcing |
| Old CFD | Reports, inputs, logs, numerical checks and exported teaching fields | A future model starts with the selected question and current physical inputs. Obsolete native fields/meshes are deleted and cannot resume |

The unchanged map/GIS delivery remains dated 18 October. This update adds the plan and detailed scene to GitHub and the Site; it does not silently relabel that GIS package or treat its old teaching CFD as current-scope evidence.

## Sequence and deliverables

| Order | Work | Output | Ready for the next step when |
|---|---|---|---|
| 1 | Select one Kajicho route or small public-space cluster, its users, hours and one plausible action | Timed route, photo points, object IDs, street/tree/material/access checklist | Team can explain the issue, the people affected and who can allow and maintain the action |
| 2 | Co-locate instruments; combine a fixed reference station with repeat observations and an independent check visit | Sensor metadata, clocks/heights, raw observations, weather and missingness | Comparisons use coincident observations, not a warmer hour mistaken for a hotter place |
| 3 | Prepare three linked geometries | Source LOD2 display scene, radiation occluders, CFD solids if needed | CRS, vertical datum, roofs, passages, trees, terrain and external context match the pilot |
| 4 | Compare shade timing first; prepare SOLWEIG only when radiation matters to the decision | Route shade duration; later mean radiant temperature, with input manifest | Shadow edges match timed observations and rankings remain usable under grid/input checks |
| 5 | Add wind screening or a mean-wind CFD pilot when the design mechanism requires it | Wind question, receptor points, inlet/context/domain/mesh plan | Relevant benchmark, inlet/domain and three-grid checks, stable target values, conservation and field agreement are planned |
| 6 | Compare a fixed baseline with one action at the same places, hours and forcing | Paired evidence and implementation card | Difference is interpretable against measured uncertainty and access/maintenance conditions |

Autumn field visits can verify geometry, use and sensor procedure. They do not alone validate summer extreme-heat predictions. A representative summer-hour study and annual wind comfort are different questions and need different weather sampling.

## Resolution and physics

- **Shade / radiation:** proposed 2 m district screen and 1 m route pilot. Test 0.5 m locally only where narrow paths or shadow edges make it necessary. These values are studio starting proposals, not a published accuracy standard. SOLWEIG grids require common extent and pixel size; overhangs and undercrofts may need a method that represents their geometry.
- **Wind screening:** URock is a candidate empirical, mass-balanced diagnostic when flat-terrain and obstacle assumptions fit. Check measured wind and sensitive tree/wake locations. A 2 m to 1 m pilot comparison is a proposal.
- **Mean-wind CFD:** steady, isothermal RANS is a candidate for an explicit mean-wind question. Set local cells from important gaps and receptor heights. COST 732's initial ten-cells-across-gap guidance gives roughly 1–2 m in 10–20 m gaps, about 0.5 m in a 5 m passage. Critical corners may need approximately 0.3–0.5 m locally; London practice is a precedent, not a Tokyo-wide rule. Keep the outer context coarser after sensitivity checks.
- **Gusts and heat coupling:** choose a separate transient/thermal protocol when those mechanisms are the question. The February 2026 AIJ LES guideline was verified from publication metadata; read its full numerical recommendations before planning LES.
- **Computational feasibility:** after a run is authorized, measure one representative unit on compatible free hardware and estimate the full comparison. Fix scope, idle hardware and unnecessary detail before scaling. No runtime limit or arbitrary memory cap is part of this plan.

## Verification

Separate geometry/forcing, numerical solution, predictive agreement and the design decision. For CFD, plan a relevant published benchmark, three systematically refined meshes, inlet preservation and a second domain. Track mass balance and target values alongside residuals. Add heat balance only for a thermal calculation. Report time-matched bias and RMSE（均方根误差；同单位、越小表示误差越小）by place and weather when observations allow.

Choose acceptance against instrument uncertainty and the design effect the team needs to distinguish. A small residual is not field validation. If refinement or plausible inputs reverse the option ranking, investigate before recommending the action. Mean radiant temperature, air temperature, surface temperature and UTCI are separate outputs; UTCI's official approximation uses 10 m wind and needs a recorded height conversion and calm-wind treatment.

## Platform and next team discussion

The platform is a shared digital site model and scenario workspace. A digital twin also needs defined physical observations, an update interval, validated decisions and a link back to site management.

The next discussion should settle three items: the route/users/hours; one physical action plus access, instruments and maintenance actor; and whether the decision is about shade/radiation, average wind, gusts or air-temperature change. Suggested first direction: a primary-area walking-route shade study, supported by the classified POIs and field observations. A CFD domain remains unset until a wind-dependent design question is chosen.

## Records

- [Technical methods and source locators](METHODS.md) · [primary-source evidence](Methods_Evidence.json)
- [Structured three-language plan](Plan.json)
- [Model provenance and checks](../../04_Data/Ready/PLATEAU_Highest_2026-10-20/README.md)
- [Obsolete CFD cleanup](CLEANUP.md) · [current CFD status](../CFD_STATUS.md)

[Publication and validation receipt](RELEASE.json): Site v22 and the feature merge on main passed their respective checks.
