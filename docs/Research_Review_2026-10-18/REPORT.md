# Kajicho research review
## A shared basis for district decarbonisation and climate resilience

**Review form:** integrative review. **Search and reading date:** 18 October 2026. **Purpose:** help an interdisciplinary studio choose questions, technical paths and implementation arrangements.

### 中文提要

任务书要求建立“规划支持＋实施支持”的地区管理模式。研究应把建筑、街道和使用者的实际问题，与可比较的方案、可信的评价方法及能够行动的主体连接起来。本综述提出六条可讨论的技术路径：能源与碳、热与遮阴、风与 CFD、街道与出行、雨洪绿化、协作实施。全球案例用于理解技术、组织和维护如何配合；各地的效果数值不直接移用于鍛冶町。后续可以从一组建筑、一条步行路线或一个共用空间开始，同时记录物理效果和实施条件。具体试点、权重与方案由团队讨论确定。

## 1. Read the assignment as a linked decision process

The brief asks for an area-management model with both **planning support** and **implementation support**, applied to Kanda–Nihonbashi with Kajicho 1 & 2 as the detailed primary area, toward 2050. Planning support connects issues, visions and actions through analysis and simulation. Implementation support connects businesses, government, academics and residents through organisation, individual and collective action, and public support. The booklet and presentation must explain that model and its application. [Murayama et al. (2026)](https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view)<!--ref:brief-2026--><!--anchor:section:Assignment; Output-->

A useful common question for the studio is: **Which building and street changes could reduce emissions and climate exposure, and what arrangements would make those changes feasible?** This is a proposed organising question. It leaves the pilot location and design choice open. Each candidate action should carry two records: a performance comparison and an implementation account naming rights, actors, resources and maintenance.

Figure 5 remains the spatial authority. Its solid primary and dashed approximate wider outlines serve different reporting levels. Physical models may need surrounding geometry beyond either outline. A reporting polygon, a catchment, an energy service area and a computational fluid dynamics (CFD) air domain answer different questions; their relationships should be documented before comparing results.

## 2. How this review was assembled

The starting corpus is the six references printed in the brief. These were supplemented by primary method papers, official technical documentation and eight contrasting practice cases. The source register contains **38 records**: the course brief, its six references, an additional urban-systems editorial, ten method/standard records, and twenty case-related records. This is a purposive integrative selection organised around the assignment. It supports a technical discussion rather than estimating a pooled intervention effect.

Search strings, source annotations and actual reading scopes are retained in [phase2_sources](phase2_sources/), [Sources.json](Sources.json) and the [reading matrix](Read_Matrix.md). DOI/title matching identified distinct records; no database-wide hit count or exhaustive retrieval claim is made. Some materials were read only as abstracts, institutional synopses or search-delivered extracts. These distinctions remain visible in the register. The review was prepared with AI-assisted retrieval, source checking and synthesis.

### What the six course references contribute

| Reference | Contribution to the studio | Reading boundary |
| --- | --- | --- |
| Yamagata & Yang, 2020 | A systems view connecting urban form, energy, movement and comfort | Institutional synopsis and metadata; book chapters unavailable |
| JICA, 2022 | Issue-led technology selection, local transfer conditions, roles, finance and operation | Selected report sections |
| Morrish, 2021 | Interdisciplinary geodesign and the studio's educational context | Practice article; not a validation study |
| Ramnarine et al., 2025 | CANVAS links representation, modelling, intervention and decision cycles | Publisher abstract only |
| Alorabi et al., 2025 | Baseline → generated alternatives → interactive comparison, using UBEM | Selected full-paper sections |
| Zeng et al., 2025 | Description → evaluation → prediction → prescription for heat/network planning | Selected full-paper sections, including limitations |

The book and ESRI article provide context at their recorded reading depth. CANVAS supplies a relevant framework from the abstract; its reported reduction percentages are not transferred into this studio. The two open Nihonbashi papers offer more inspectable workflows. [Yamagata and Yang (2020)](https://keio.elsevierpure.com/en/publications/urban-systems-design-creating-sustainable-smart-cities-in-the-int/)<!--ref:yamagata-yang-2020--><!--anchor:section:Institutional synopsis--> [Morrish (2021)](https://www.esri.com/about/newsroom/blog/georgia-tech-students-smart-city-tokyo/)<!--ref:morrish-2021-tokyo--><!--anchor:section:Placemakers--> [Ramnarine et al. (2025)](https://journals.sagepub.com/doi/10.1177/23998083251318142)<!--ref:ramnarine-2025-canvas--><!--anchor:section:Abstract-->

## 3. Three theoretical connections

### Systems: relate places to stocks, flows and choices

Urban-systems design joins questions about desirable places with analysis of how urban processes function. Energy, materials, water, movement and social relationships connect across spatial and temporal scales. A district platform can make those relationships discussable through a common representation and explicit scenarios. [Yang and Yamagata (2019)](https://journals.sagepub.com/doi/10.1177/2399808319877770)<!--ref:yang-yamagata-2019--><!--anchor:section:Introduction; Cities as flows; The theme issue on urban systems design-->

For Kajicho, this suggests a shared scenario record: the place and time, physical change, input assumptions, performance measures and responsible actors. A visually detailed model becomes useful when these links can be inspected and revised.

### Exposure: connect physical conditions with people and time

A hot surface, warm air, radiant exposure and physiological thermal stress are different constructs. SOLWEIG estimates directional radiation and mean radiant temperature; UTCI combines air temperature, radiation, humidity and wind in an equivalent-temperature procedure. Together they support a clearer separation between a geometric shade map and a pedestrian exposure assessment. [UMEP/SOLWEIG development team (n.d.)](https://umep-docs.readthedocs.io/en/latest/OtherManuals/SOLWEIG.html)<!--ref:umep-solweig-manual--><!--anchor:section:12.2.1;12.2.6--> [Bröde et al. (2012)](https://link.springer.com/article/10.1007/s00484-011-0454-1)<!--ref:broede-2012-utci--><!--anchor:section:Abstract-->

The studio implication is to name the user, route or resting place and the relevant hours before selecting an indicator. A lunchtime worker, an older resident and a delivery worker may occupy the same street differently. Their needs should inform sampling and access assumptions.

### Collective action: connect performance with institutions

Ansell and Gash organise collaborative governance around starting conditions, institutional design, facilitative leadership and an iterative process. Their case-based model highlights power, resources and incentives. Ostrom adds a multilevel perspective in which partly independent authorities can cooperate and learn, while also facing coordination and free-riding problems. These are analytical frames for organising action; they do not predict a carbon saving from participation alone. [Ansell and Gash (2008)](https://academic.oup.com/jpart/article/18/4/543/1090370)<!--ref:ansell-gash-2008-collaborative--><!--anchor:section:A Model of Collaborative Governance;Figure1--> [Ostrom (2010)](https://doi.org/10.1016/j.gloenvcha.2010.07.004)<!--ref:ostrom-2010-polycentric--><!--anchor:section:4;6-->

A studio action card should therefore record who owns the asset, who permits or operates it, who benefits, who pays and who maintains it. The brief identifies Watage and CWL as local initiatives to consider in the area-management model. [Murayama et al. (2026)](https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view)<!--ref:brief-2026--><!--anchor:section:About Kajicho-->

## 4. Six technical paths

### A. Building energy and carbon

**Question:** Which retention, retrofit, operation or replacement options are worth comparing for a willing building group?

UBEM assembles climate, geometry, constructions, systems and use schedules into building models. Archetypes help fill a district inventory, but their assumptions need checking at the scale of the intended decision. Aggregate agreement can conceal individual-building errors. [Reinhart and Cerezo Davila (2016)](https://dspace.mit.edu/entities/publication/9cb85b0f-e4fd-4399-b5eb-4dccd719a550)<!--ref:reinhart-cerezo-2016-ubem--><!--anchor:section:2.1;2.3;3-->

**Recipe proposed for the studio:**

1. Check the building inventory, usable floor areas, uses, construction information and available bills.
2. Define a small common set of options: operation, envelope/equipment retrofit, rooftop generation, and retention/replacement where relevant.
3. Build archetypes, run common-weather scenarios and test sensitive inputs such as schedules and envelope properties.
4. Compare annual and hourly energy, peak demand, carbon, cost ranges and disruption. Keep modelled values separate from bills.

Alorabi et al. connect a UBEM baseline with design generation and multi-objective comparison, using URBANopt/OpenStudio/EnergyPlus. Their age-based intervention categories are case assumptions. Kajicho choices need condition, ownership and parcel checks before reuse. [Alorabi et al. (2025)](https://isprs-archives.copernicus.org/articles/XLVIII-4-W16-2025/1/2025/)<!--ref:alorabi-2025-net-zero--><!--anchor:section:2;3.1–3.3-->

For operational accounting, keep energy carriers and dated emission factors explicit: **carbon = sum of activity × matching factor**. A district inventory boundary differs from an asset life-cycle assessment. Whole-life comparisons need a common study period and retained/new-element scope, with module D reported separately under RICS. This matters when lower operating energy requires substantial new material. [WRI, C40 and ICLEI (2021)](https://ghgprotocol.org/ghg-protocol-cities)<!--ref:wri-c40-iclei-2021-gpc11--><!--anchor:section:3.5;5.1--> [RICS (2023/2024)](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf)<!--ref:rics-2023-wlca-v3--><!--anchor:section:3.3-->

**Useful first output:** a building-group option table with units, assumptions, ranges, validation evidence and the owner/operation conditions for each option.

### B. Heat, shade and accessible cool places

**Question:** Where and when would shade or a usable refuge improve a particular everyday route?

Begin with solar obstruction and users' hours. If radiant exposure is material, prepare common-grid ground/building and canopy geometry, weather and surface assumptions for a radiation model. Add a thermal-stress indicator only when its required weather and wind inputs are defensible. SOLWEIG's manual identifies these inputs and outputs, including pedestrian mean radiant temperature, radiation and shadow fields. [UMEP/SOLWEIG development team (n.d.)](https://umep-docs.readthedocs.io/en/latest/OtherManuals/SOLWEIG.html)<!--ref:umep-solweig-manual--><!--anchor:section:12.2.2;12.2.6-->

Compare options at common places and times: shaded walking minutes, mean radiant temperature, selected thermal-stress categories, and access to resting or cooled spaces. Proposed field checks include fixed reference measurements with repeated route observations; sensor height, shielding, timing and weather changes need documenting.

Zeng et al. link heat-index categories, vulnerability overlays and routes. Their discussion identifies static road/shelter inputs and a traffic-density vulnerability proxy, while distinguishing an envisioned interface from current outputs. This is a useful workflow prototype. Its classifier accuracy does not validate street-level thermal comfort or health outcomes. [Zeng et al. (2025)](https://isprs-archives.copernicus.org/articles/XLVIII-4-W16-2025/135/2025/)<!--ref:zeng-2025-heat--><!--anchor:section:3.1;4;5.1–5.2-->

**Useful first output:** a timed route/refuge map with verified entrances, opening hours, shade conditions, exposure measures and the operator of each proposed resting place.

### C. Wind and CFD

**Question:** Does a particular spatial change alter the wind conditions that matter for the chosen street users?

Select weather cases and the target measure before constructing a new numerical domain. Preserve relevant surrounding buildings; define inflow, surface roughness, physical assumptions and output locations. Separate changes caused by geometry from those caused by weather or modelling choices.

COST732 distinguishes physical-model uncertainty from discretisation and iterative error, and calls for monitoring target variables as well as residuals. Its main scope is neutral, statistically steady Reynolds-averaged Navier–Stokes (RANS). AIJ provides a Japanese benchmark-based guideline for pedestrian wind, although this review read its abstract rather than its numerical prescriptions. [Franke et al. (2007)](https://www.mi.uni-hamburg.de/en/arbeitsgruppen/windkanallabor/documents.html)<!--ref:franke-2007-cost732--><!--anchor:section:1–4;5.1--> [Tominaga et al. (2008)](https://www.aij.or.jp/jpn/publish/cfdguide/index_e.htm)<!--ref:tominaga-2008-aij-cfd--><!--anchor:section:Abstract-->

A proposed evidence sequence is: geometry/inlet checks → mesh and domain sensitivity → convergence of target values and conservation checks → comparison with suitable benchmark or field evidence → paired design comparison. Coupled heat analysis also needs an explicit thermal model and energy-budget checks. Wind-only guidance cannot establish those thermal assumptions.

**Useful first output:** a numerical study plan stating the question, geometry, weather cases, target heights/locations, physical model, validation evidence and stopping criteria. The retained earlier CFD trials keep their recorded acceptance status; this review starts no new solver run.

### D. Streets, activities and movement

**Question:** How can everyday access, loading, business activity and climate comfort work together?

Use points of interest (POIs) to describe mapped destinations and functional mix, then verify entrances, operating times, street restrictions and route continuity. Destination counts, jobs, footfall and building floor area have different units. Network analysis can compare access to actual destinations; observed trips or defensible demand assumptions are needed for flow or transport-emission claims.

The heat/network paper supplies an example of graph construction and route comparison. Its proxy and static-data limitations show why route quality needs local checks. [Zeng et al. (2025)](https://isprs-archives.copernicus.org/articles/XLVIII-4-W16-2025/135/2025/)<!--ref:zeng-2025-heat--><!--anchor:section:3.1;4.2;5.2-->

For a proposed street pilot, record pedestrian routes and resting activity alongside delivery windows, vehicle access and adjacent streets. Compare the same network boundary before and after a change. Barcelona's evaluation illustrates that street interventions and outcomes differ by site and user group. [Pérez et al. (2025)](https://link.springer.com/article/10.1186/s12889-025-21835-z)<!--ref:barcelona-superblocks-bcn2--><!--anchor:section:Methods;Results;Strengths and limitations-->

**Useful first output:** a service-and-access map with observed use periods, a loading/access account, and a route comparison whose demand and comfort assumptions are visible.

### E. Water, vegetation and multi-purpose space

**Question:** Can a small public-space intervention address rainfall and daily use while providing maintainable vegetation?

Start with topography, catchments, runoff pathways, drains/outfalls and the selected rainfall scenario. Tree points, canopy shade and infiltration capacity need separate evidence. The U.S. Environmental Protection Agency's Storm Water Management Model (SWMM) represents rainfall–runoff, drainage routing and green-infrastructure controls through connected subcatchments and network elements. Its capability page supplies a candidate modelling route, not a calibrated Kajicho drainage model. [U.S. EPA (2026)](https://www.epa.gov/water-research/storm-water-management-model-swmm)<!--ref:epa-swmm--><!--anchor:section:Capabilities;Accounting for Hydrologic Processes;Green Infrastructure as LID Controls-->

A suitable early comparison may be a surveyed runoff-path and storage concept. Quantitative hydraulic claims require appropriate drainage inputs, boundary conditions and checks. Everyday access, safe overflow, irrigation, growing space and maintenance belong in the same option record.

**Useful first output:** a catchment-linked planting/storage concept with an overflow route, maintenance owner and a clear distinction between design capacity and observed performance.

### F. People, delivery and learning

**Question:** What would allow a promising action to be adopted, operated and revised?

Map actors' assets, authority, knowledge, incentives and constraints. Specify who convenes discussion and how disagreement is recorded. Compare alternatives with a small set of clearly defined measures; show trade-offs and sensitivity to weights rather than allowing one unexplained score to settle the choice.

JICA connects visions and policy with organisational responsibility, finance, monitoring and operation. These process ideas need local interpretation because the report principally addresses cooperation with developing-country cities. [JICA et al. (2022)](https://openjicareport.jica.go.jp/618/618/618_000_12342515.html)<!--ref:jica-2022-smart-city--><!--anchor:section:1-1–1-2;5-5;6-2-->

**Useful first output:** a pilot agreement outline naming participants, responsibilities, funding/maintenance arrangements, data sharing, a monitoring period and a review point. This is a proposed team tool, not evidence of stakeholder consent.

## 5. Global practice: mechanisms and transfer conditions

The cases below illustrate different combinations of physical change and delivery. “Transfer” is the review's interpretation. Programme descriptions, design targets and empirical evaluations remain distinct.

| Case | Mechanism and evidence | Question for Kajicho |
| --- | --- | --- |
| Barcelona Superblocks | Street-space change with mixed environmental and social evaluation; outcomes vary across sites | How will adjacent traffic, loading and different users be included? |
| Paris Oasis | Co-designed shaded/permeable schoolyards; one-site thermal field methods | Who can access a refuge, at what hours, and who maintains it? |
| Melbourne urban forest | Street planting priorities tied to precinct plans and delivery | Are growing space, services, water and long-term care feasible? |
| Punggol Digital District | Shared cooling and digital interfaces under coordinated development | Can separate owners agree on demand, rights, cost and operation? |
| Copenhagen Enghaveparken | Multi-purpose public space linked to stormwater works and funding | What catchment, outlet and safe overflow make the space functional? |
| Better Bankside | Continuing area management plus small public-realm projects | What locally legitimate membership, finance and maintenance arrangement is possible? |
| Freiburg Vauban | Energy requirements linked to development contracts and shared infrastructure | Which mechanisms depend on control of land development? |
| New York Cool Neighborhoods | Heat-vulnerability targeting, physical works and cooling access | Which local exposure, vulnerability and service-access evidence should guide priorities? |

**Barcelona.** The published evaluation reports heterogeneous environmental and perceived outcomes. Some measurements have reference locations, while health comparisons and some baseline observations are limited; pandemic disruption also matters. Borrow the combined evaluation design, with local access and adjacent streets in the boundary. [Pérez et al. (2025)](https://link.springer.com/article/10.1186/s12889-025-21835-z)<!--ref:barcelona-superblocks-bcn2--><!--anchor:section:Results;Discussion;Strengths and limitations-->

**Paris.** Municipal records describe co-design and schoolyard transformation. The Maryse Hilsz study combines fixed/control stations, mobile surveys and GIS; its spatial findings are preliminary and methodological. A possible lesson is to connect refuge design with access arrangements and repeated measurements. [Ville de Paris (2025)](https://www.paris.fr/pages/les-cours-oasis-7389)<!--ref:paris-oasis-par1--><!--anchor:section:La méthode oasis;Évaluation--> [Karam et al. (2023)](https://arxiv.org/pdf/2408.07284)<!--ref:paris-oasis-par2--><!--anchor:section:Methods;Results;Conclusions-->

**Melbourne.** The precinct approach connects planting priorities, consultation and a delivery timeline. This is programme evidence, not a measured cooling effect in the reviewed material. Transfer the street-level prioritisation process while checking services, water, rooting volume and maintenance. [City of Melbourne (n.d.)](https://participate.melbourne.vic.gov.au/urban-forest)<!--ref:melbourne-urban-forest-mel1--><!--anchor:section:Programme overview;FAQs--> [City of Melbourne (n.d.)](https://participate.melbourne.vic.gov.au/cbd-urban-forest)<!--ref:melbourne-urban-forest-mel2--><!--anchor:section:Timeline;FAQs-->

**Punggol.** JTC's account describes a shared cooling system and coordinated building interfaces. Reported savings are estimates/comparisons, not an annual monitored dataset inspected here. Its relevance is the coordination requirement; Kajicho's dispersed ownership would need its own technical, rights and operating agreement. [JTC (n.d.)](https://www.jtc.gov.sg/punggoldigitaldistrict/story-articles/what-to-know-about-engie-dcs-at-pdd)<!--ref:punggol-digital-district-pdd1--><!--anchor:section:Cooling a district the smart way;A collective effort-->

**Copenhagen.** Municipal records document Enghaveparken's adaptation works and financing. The reviewed park description links daily public space with temporary stormwater handling. Design service levels do not establish avoided losses in a real event. Transfer requires catchment routing, outlet capacity, safe overflow and an appropriate funding agreement. [Københavns Kommune (2021)](https://www.kk.dk/dagsordener-og-referater/%C3%98konomiudvalget/m%C3%B8de-12012021/referat/punkt-9)<!--ref:copenhagen-enghaveparken-cph1--><!--anchor:section:Solution;Construction accounts;Economy--> [Københavns Kommune (n.d.)](https://www.kk.dk/sites/default/files/agenda/d60ae350-a195-42f4-a5ef-be2863612f1b/5c60882a-b958-42c8-a8f1-2674a8e99d5a-bilag-2.pdf)<!--ref:copenhagen-enghaveparken-cph2--><!--anchor:section:Enghaveparken case extract-->

**London.** Better Bankside describes a levy/ballot area-management structure; Southwark records the Keppel Row Garden transformation. The useful mechanism is a continuing organisation working through small projects and multiple partners. UK BID law is context-specific; a Tokyo arrangement needs its own legitimate basis. [Better Bankside (n.d.)](https://betterbankside.co.uk/who-we-are/what-is-a-bid/)<!--ref:london-better-bankside-lon1--><!--anchor:section:What is a BID--> [Southwark Council (2019)](https://www.southwark.gov.uk/news/2019/alleyway-transformed-creation-keppel-row-garden)<!--ref:london-better-bankside-lon2--><!--anchor:section:Article body-->

**Freiburg.** Historical municipal material describes energy requirements, district infrastructure and development contracts. Reading is limited to the recorded search-delivered material. The case helps distinguish a redevelopment setting with contractual land controls from an existing district in which owner agreements must be assembled. [Stadt Freiburg (n.d.)](https://www.freiburg.de/pb/208752.html)<!--ref:freiburg-vauban-fre1--><!--anchor:section:Energie;Freiraum/Wasser-->

**New York.** The city plan and health portal connect environmental exposure with social/access factors and targeted actions. These records support a targeting and service framework; no causal programme effect is estimated here. Local worker, resident and visitor evidence should guide any Kajicho adaptation of the idea. [City of New York (2017)](https://www.nyc.gov/assets/orr/pdf/Cool_Neighborhoods_NYC_Report.pdf)<!--ref:new-york-cool-neighborhoods-nyc1--><!--anchor:section:Introduction;Targeted street-tree planting--> [NYC Department of Health and Mental Hygiene (n.d.)](https://a816-dohbesp.nyc.gov/IndicatorPublic/data-features/hvi/)<!--ref:new-york-cool-neighborhoods-nyc2--><!--anchor:section:Index description;Factors-->

## 6. A practical discussion sequence

Three candidate starting paths can share the same area-management frame:

- **A building group:** an energy/whole-life-carbon comparison with owners willing to share a small verified input set.
- **A daily route:** shade, exposure, access and loading observations, with a maintainable spatial change.
- **A shared space:** a refuge or green/water intervention with an identifiable operator and access agreement.

These are discussion options, not a selected design. The initial question and available evidence should determine model complexity. Start with a common baseline and a few explicit alternatives; more elaborate optimisation becomes useful when feasible variables, input ranges and decision criteria are known.

| Contribution | Shared task |
| --- | --- |
| Planning and social research | Actors, rights, access, participation and policy-to-action logic |
| Architecture and building science | Stock, condition, envelopes, systems and spatial alternatives |
| Environmental/civil engineering | Thermal, wind and drainage assumptions; field and model checks |
| Data/GIS | Reproducible geometry, joins, source years, coverage and sensitivity |
| Economics/management | Cost ranges, incentives, operating responsibilities and delivery sequence |

The booklet can connect these through a repeated page structure: **issue → evidence → options → comparison → action/actor → monitoring**. The presentation can show the decisions and supporting drawings from that same record. [Murayama et al. (2026)](https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view)<!--ref:brief-2026--><!--anchor:section:Assignment;Output-->

## 7. Tensions and open work

Two comparisons are particularly useful. First, weather-based heat alerts and pedestrian radiation/thermal measures address different constructs. Use each at its intended scale, then test the route-specific bridge. Second, operating-energy improvement and whole-life carbon can favour different options when material replacement is substantial. Compare a common horizon and preserve module boundaries before drawing a design conclusion.

The selected cases are concentrated in Europe, with additional examples from Asia, Australia and North America. They illustrate mechanisms rather than a representative global sample. Detailed access was uneven, especially for the book, the CANVAS article and some municipal extracts. The unresolved local work is specific: reliable building inputs, street-level user/exposure evidence, drainage/planting conditions, and a legitimate delivery arrangement. Those gaps define useful student tasks.

The website presents this review as linked frameworks, method paths and case cards. The full account and source-reading records remain here for inspection.

## References

- Murayama, A., Yang, P. P.-J., & Yoshida, T. (2026). Building an area management model for decarbonization and climate resilience: Kanda–Nihonbashi Area, Tokyo [Theme B official studio brief]. The University of Tokyo. [Source](https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view). Reading: sections.
- Yamagata, Y., & Yang, P. P. J. (Eds.). (2020). Urban systems design: Creating sustainable smart cities in the Internet of Things era. Elsevier. https://doi.org/10.1016/C2017-0-04401-4 [Source](https://keio.elsevierpure.com/en/publications/urban-systems-design-creating-sustainable-smart-cities-in-the-int/). Reading: metadata and synopsis.
- Japan International Cooperation Agency, Pacific Consultants, & Mitsubishi UFJ Research and Consulting. (2022). Data collection survey on the application of smart city approach: Final report. [Source](https://openjicareport.jica.go.jp/618/618/618_000_12342515.html). Reading: sections.
- Morrish, K. (2021, December 7). Tokyo: Reimagining the world’s largest city with advanced analytics. Esri. [Source](https://www.esri.com/about/newsroom/blog/georgia-tech-students-smart-city-tokyo/). Reading: article.
- Ramnarine, I. D., Sherif, T. A., Alorabi, A. H., Helmy, H., Yoshida, T., Murayama, A., & Yang, P. P.-J. (2025). Urban revitalization pathways toward zero carbon emissions through systems architecting of urban digital twins. Environment and Planning B: Urban Analytics and City Science, 52(8), 1920–1948. https://doi.org/10.1177/23998083251318142 [Source](https://journals.sagepub.com/doi/10.1177/23998083251318142). Reading: abstract only.
- Alorabi, A. H., Shen, J., Smith, J. M., Hawkins, M., Fatemifar, K., Yoshida, T., Murayama, A., & Yang, P. P.-J. (2025). A data-driven smart district toward net zero using generative design and urban digital twins: A use case of Nihonbashi, Tokyo. The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences, XLVIII-4/W16-2025, 1–8. https://doi.org/10.5194/isprs-archives-XLVIII-4-W16-2025-1-2025 [Source](https://isprs-archives.copernicus.org/articles/XLVIII-4-W16-2025/1/2025/). Reading: sections.
- Zeng, Q., Nation, R. T., Ahmed, H. I., Ma, H.-C., Zhou, K., Gu, J., Yoshida, T., Murayama, A., & Yang, P. P.-J. (2025). Enhancing urban heat risk resilience in Tokyo’s Nihonbashi through urban digital twins of 4-step scenario planning. The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences, XLVIII-4/W16-2025, 135–142. https://doi.org/10.5194/isprs-archives-XLVIII-4-W16-2025-135-2025 [Source](https://isprs-archives.copernicus.org/articles/XLVIII-4-W16-2025/135/2025/). Reading: sections.
- Yang, P. P. J., & Yamagata, Y. (2019). Urban systems design: From “science for design” to “design in science”. Environment and Planning B: Urban Analytics and City Science, 46(8), 1381–1386. https://doi.org/10.1177/2399808319877770 [Source](https://journals.sagepub.com/doi/10.1177/2399808319877770). Reading: sections.
- U.S. Environmental Protection Agency. (2026, October 7). Storm Water Management Model (SWMM). [Source](https://www.epa.gov/water-research/storm-water-management-model-swmm). Reading: sections.
- Reinhart, C. F., & Cerezo Davila, C. (2016). Urban building energy modeling – A review of a nascent field. Building and Environment, 97, 196–202. https://doi.org/10.1016/j.buildenv.2015.12.001 [Source](https://dspace.mit.edu/entities/publication/9cb85b0f-e4fd-4399-b5eb-4dccd719a550). Reading: sections.
- Bröde, P., Fiala, D., Błażejczyk, K., Holmér, I., Jendritzky, G., Kampmann, B., Tinz, B., & Havenith, G. (2012). Deriving the operational procedure for the Universal Thermal Climate Index (UTCI). International Journal of Biometeorology, 56, 481–494. https://doi.org/10.1007/s00484-011-0454-1 [Source](https://link.springer.com/article/10.1007/s00484-011-0454-1). Reading: abstract only.
- UMEP/SOLWEIG development team. (n.d.). SOLWEIG manual. UMEP Manual. Retrieved October 18, 2026, from https://umep-docs.readthedocs.io/en/latest/OtherManuals/SOLWEIG.html [Source](https://umep-docs.readthedocs.io/en/latest/OtherManuals/SOLWEIG.html). Reading: sections.
- Tominaga, Y., Mochida, A., Yoshie, R., Kataoka, H., Nozu, T., Yoshikawa, M., & Shirasawa, T. (2008). AIJ guidelines for practical applications of CFD to pedestrian wind environment around buildings. Journal of Wind Engineering and Industrial Aerodynamics, 96(10–11), 1749–1761. https://doi.org/10.1016/j.jweia.2008.02.058 [Source](https://www.aij.or.jp/jpn/publish/cfdguide/index_e.htm). Reading: abstract only.
- Franke, J., Hellsten, A., Schlünzen, H., & Carissimo, B. (Eds.). (2007). Best practice guideline for the CFD simulation of flows in the urban environment. COST Action 732. COST Office. [Source](https://www.mi.uni-hamburg.de/en/arbeitsgruppen/windkanallabor/documents.html). Reading: sections.
- Royal Institution of Chartered Surveyors. (2023). Whole life carbon assessment for the built environment (2nd ed., Version 3, August 2024). [Source](https://www.rics.org/content/dam/ricsglobal/documents/standards/Whole_life_carbon_assessment_PS_Sept23.pdf). Reading: sections.
- World Resources Institute, C40 Cities Climate Leadership Group, & ICLEI – Local Governments for Sustainability. (2021). Global protocol for community-scale greenhouse gas emission inventories: An accounting and reporting standard for cities (Version 1.1). [Source](https://ghgprotocol.org/ghg-protocol-cities). Reading: sections.
- Ansell, C., & Gash, A. (2008). Collaborative governance in theory and practice. Journal of Public Administration Research and Theory, 18(4), 543–571. https://doi.org/10.1093/jopart/mum032 [Source](https://academic.oup.com/jpart/article/18/4/543/1090370). Reading: sections.
- Ostrom, E. (2010). Polycentric systems for coping with collective action and global environmental change. Global Environmental Change, 20(4), 550–557. https://doi.org/10.1016/j.gloenvcha.2010.07.004 [Source](https://doi.org/10.1016/j.gloenvcha.2010.07.004). Reading: sections.
- Agència de Salut Pública de Barcelona. (n.d.). Avaluació de les Superilles. [Source](https://dades.aspb.cat/obsip/avaluacions/superilles). Reading: sections.
- Pérez, K., Palència, L., López, M. J., León-Gómez, B. B., Puig-Ribera, A., Gómez-Gutiérrez, A., Nieuwenhuijsen, M., Carrasco-Turigas, G., & Borrell, C. (2025). Environmental and health effects of the Barcelona superblocks. BMC Public Health, 25, Article 634. https://doi.org/10.1186/s12889-025-21835-z [Source](https://link.springer.com/article/10.1186/s12889-025-21835-z). Reading: sections.
- Ville de Paris. (2025, January 15). Les cours oasis. [Source](https://www.paris.fr/pages/les-cours-oasis-7389). Reading: sections.
- Karam, G., Chanial, M., Parison, S., Hendel, M., & Royon, L. (2023). Spatial microclimatic characterization of a Parisian “Oasis” schoolyard. In Proceedings of the 5th International Conference on Building Energy and Environment (pp. 2957–2965). Springer. https://doi.org/10.1007/978-981-19-9822-5_315 [Source](https://arxiv.org/pdf/2408.07284). Reading: sections.
- Karam, G., Chanial, M., Grados, A., Hendel, M., & Royon, L. (2024). Thermal and microclimatic behavior of OASIS schoolyard paving materials [Preprint]. arXiv. https://arxiv.org/abs/2408.08317 [Source](https://arxiv.org/abs/2408.08317). Reading: abstract only.
- City of Melbourne. (n.d.). Plan the urban forest in your neighbourhood. [Source](https://participate.melbourne.vic.gov.au/urban-forest). Reading: sections.
- City of Melbourne. (n.d.). CBD urban forest precinct plan 2025–2035. [Source](https://participate.melbourne.vic.gov.au/cbd-urban-forest). Reading: sections.
- JTC. (n.d.). What to know about ENGIE DCS at PDD. Punggol Digital District. [Source](https://www.jtc.gov.sg/punggoldigitaldistrict/story-articles/what-to-know-about-engie-dcs-at-pdd). Reading: sections.
- JTC. (2018, July 9). First-of-its-kind open digital platform for smart city solutions in Punggol Digital District. [Source](https://www.jtc.gov.sg/about-jtc/news-and-stories/press-releases/first-of-its-kind-open-digital-platform-for-smart-city-solutions-in-punggol-digital-district). Reading: limited extract.
- Københavns Kommune. (2021, January 12). Lånoptag til klimatilpasningsprojekt i Enghaveparken, Vesterbro/Kgs. Enghave. [Source](https://www.kk.dk/dagsordener-og-referater/%C3%98konomiudvalget/m%C3%B8de-12012021/referat/punkt-9). Reading: sections.
- Københavns Kommune. (n.d.). [Climate adaptation report, Enghaveparken section]. [Source](https://www.kk.dk/sites/default/files/agenda/d60ae350-a195-42f4-a5ef-be2863612f1b/5c60882a-b958-42c8-a8f1-2674a8e99d5a-bilag-2.pdf). Reading: limited extract.
- Københavns Kommune. (2012, November 19). Endelig vedtagelse af skybrudsplan. [Source](https://www.kk.dk/dagsordener-og-referater/Teknik-%20og%20Milj%C3%B8udvalget/m%C3%B8de-19112012/referat/punkt-14). Reading: limited extract.
- Better Bankside. (n.d.). What is a BID? [Source](https://betterbankside.co.uk/who-we-are/what-is-a-bid/). Reading: limited extract.
- Southwark Council. (2019, April 2). Alleyway transformed by creation of Keppel Row Garden. [Source](https://www.southwark.gov.uk/news/2019/alleyway-transformed-creation-keppel-row-garden). Reading: sections.
- Greater London Authority. (n.d.). Community green space grants 2018. [Source](https://www.london.gov.uk/programmes-and-strategies/environment-and-climate-change/parks-green-spaces-and-biodiversity/greener-city-fund/community-green-space-grants-2018). Reading: limited extract.
- Stadt Freiburg im Breisgau. (n.d.). Umwelt und Energie. [Source](https://www.freiburg.de/pb/208752.html). Reading: limited extract.
- Stadt Freiburg im Breisgau, Stadtplanungsamt. (2008). Quartier Vauban: Energie / Energy [Poster]. [Source](https://www.freiburg.de/pb/site/Freiburg/get/documents/freiburg/daten/bauen/vauban/Vauban_Energie.pdf). Reading: limited extract.
- City of New York, Mayor's Office of Recovery and Resiliency. (2017). Cool neighborhoods NYC: A comprehensive approach to keep communities safe in extreme heat. [Source](https://www.nyc.gov/assets/orr/pdf/Cool_Neighborhoods_NYC_Report.pdf). Reading: sections.
- NYC Department of Health and Mental Hygiene. (n.d.). Interactive heat vulnerability index. [Source](https://a816-dohbesp.nyc.gov/IndicatorPublic/data-features/hvi/). Reading: sections.
- NYC Mayor's Office. (2026, June). Mayor Mamdani releases PSA to ready New Yorkers for extreme heat throughout the summer. [Source](https://www.nyc.gov/mayors-office/news/2026/06/mayor-mamdani-releases-psa-to-ready-new-yorkers-for-extreme-heat). Reading: limited extract.
