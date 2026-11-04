# Team start

Current Mapping follows [official brief Figure 5](COURSE_BOUNDARIES.md): primary 10.70383 ha / 277 models / 178 POIs; approximate wider area 41.98967 ha / 1,074 models / 353 POIs. Both source outlines appear in one shared view. Earlier simulations retain their dated inputs.

Use the [single current team package](https://drive.google.com/file/d/1zSJaSWM6WXMdMsgJQJG5Nd6M9kechosz/view) and [current delivery guide](CURRENT_DELIVERY.md). Building analysis uses full-footprint containment; crossing and exterior models remain grey context.

2026-10-20 · Theme B membership confirmed. The map/GIS package remains dated 18 October because its scope and membership are unchanged. Read the [current environmental work plan](Environmental_Work_Plan_2026-10-20/README.md) and inspect the [source LOD2 model](https://kajicho-wind-heat-carbon-demo.specialgooood.chatgpt.site/studies.html). Main work covers building energy/carbon, street shade/radiation, and planning/implementation. The team will agree transport scope, pilot, actions, metric weights and roles. No new CFD runs are planned at this stage.

## First visit

1. Read [Project plan](PROJECT_PLAN.md) for course aims, methods and open decisions.
2. Clone the complete repository or use GitHub **Code → Download ZIP** and extract everything. A QGIS project alone is insufficient.
3. Open `05_QGIS/Projects/Kanda_Nihonbashi_Study_2026-10-18.qgz` for the 21 current study tables (20 spatial layers and one membership attribute table). Keep the companion GeoPackage in `04_Data/Ready/Study_Area_2026-10-18/`. Earlier baseline and CFD projects remain dated evidence.
4. Use [Data guide](DATA_GUIDE.md), [Layer catalog](../04_Data/Metadata/Layer_Catalog.csv) and [Layer fields](../04_Data/Metadata/Layer_Fields.csv).
5. Choose an unassigned [task](../07_Team/Task_Queue.csv), then record its owner, reviewer and deliverable in an issue before editing.

```sh
git clone https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho.git
cd Urban-Design-Studio-2026-Kajicho
```

The repository is private. Drive and the hosted Site have separate permissions; see [Data access](../DATA_ACCESS.md). Local data and the local website can be used independently.

## QGIS

The current course project was saved with QGIS 3.44.12. Earlier projects used QGIS 3.32.3. Record your version and check layers, styles and layouts before saving. Layer data use EPSG:6677 in metres; projects use relative paths.

| Action | How | Check |
| --- | --- | --- |
| Find the study area | Zoom to `study_area` | Figure 5 dashed approximate wider + solid primary source traces |
| Inspect buildings | Use `analysis_buildings_wider` or `analysis_buildings_primary` | 1,074 wider / 277 primary model objects; full-footprint containment; no selected crossing or exterior objects |
| Read land use/planning | Inspect current `land_use` and `zones` separately | Observed use and legal reference zones differ; FAR is a percentage |
| Read provenance/gaps | Open dated source and quality records and catalogs | Missing stays missing; record survey year and generation method |
| Save personal work | Save to `local/` or `05_QGIS/Projects/<name>_<date>.qgz` | Recheck relative paths; keep the shared project intact |
| Deliver a map | Add title, date/time, legend, scale, north arrow, CRS and sources; export PNG | Identify measured/model/estimated/scenario values and label old CFD rasters unconverged |

For missing layers, check the complete download and the relative positions of `04_Data` and `05_QGIS`. Keep local absolute paths out of shared projects. One person edits each shared project/GeoPackage; others return separate layers or CSV.

## Materials

The [handover manifest](HANDOVER_MANIFEST.csv) identifies resources and uses; the catalogs provide full field details.

| Work | Start with | Gap/action |
| --- | --- | --- |
| Building energy/carbon | current `06_Outputs/Study_Area_2026-10-18/tables/buildings.csv` and `building_use.csv`, uses/floor proxies, `Building_Energy_Input.csv`, `DECC_EUI_Input_Template.csv` | Await DECC, actual energy and floor area. Check original units, energy scope and year |
| Shade/radiation | Heights, `Tokyo_2025_hourly.csv`, trees and parks | Background-station weather; survey core tree positions/crowns/heights. Handle and document two missing wind hours among 8760 |
| Planning/implementation | Zones, `FAR26_Official_Review.csv`, `FAR26_Legal_Site_Check.csv`, actor/action forms | 26 objects have official-map reference checks; legal sites, frontage and effective capacity still need review |
| Mobility | Roads, stations, passages and field records | Record walking, delivery and vehicle observation times and scope; network is not actual flow |
| Wind/heat diagnostics | [CFD status](CFD_STATUS.md), website checks/methods | Reference6000 and light2000 remain unaccepted; no rerun or verified-benefit export at this stage |

Keep sources in dated folders and save new outputs separately with URL, year, CRS, licence, processing and quality issues. Check permissions before committing DECC raw samples or actual energy details.

## First tasks

- Data/GIS: review source coverage and IDs within the defined study area; map field checks.
- Buildings/carbon: review use, proxy-area gaps and DECC matching; enter sourced inputs without assumed savings.
- Shade/radiation: prepare a candidate-route form, observation periods and tree survey for team discussion.
- Planning/implementation: connect applicable policies, legal conditions, actors and rights to action cards.
- Mobility: identify passages, deliveries and observation points; propose activity-data collection.
- Integration: align drawings, resource entry points and first-meeting questions.

These are starting tasks, not assigned teams. Before option calculations, complete an [analysis pilot](../07_Team/Templates/Analysis_Pilot.md) with the owner and reviewer.

## Local website

From the repository root, using standard Python 3:

```sh
python3 06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/serve_demo.py
```

On Windows with Python Launcher, use `py -3` instead of `python3`. The terminal prints the local address and opens a browser. `index.html` is the portfolio, `team.html` the team desk, `studies.html` parameter studies, and `cfd.html` the old field and diagnostics. Stop the server with Ctrl+C. No npm or OpenFOAM installation is needed for preview.

2D wind, geometric shade, assumed energy and 3D CFD have different methods. Parameter changes are not newly validated designs. A maintainer publishes the hosted Site; contributors submit source and checks.

## Return work

1. Claim the place/question in an issue and coordinate shared GIS editing.
2. Branch from current main: `git switch main`, `git pull --ff-only`, `git switch -c <your-branch>`. ZIP users return separate files for a maintainer to commit.
3. Return UTF-8 attribute CSV with stable building/tree/route IDs, or separate GeoPackage/GeoJSON layers. Store photos/maps under `06_Outputs/<topic>/<date>/` with relative paths.
4. Document new field types, units, nulls and sources. After GeoPackage changes, run `python3 08_Scripts/build_layer_catalog.py`.
5. Open a PR with question, input version, processing, checks, findings and remaining gaps. Merge after review.

```sh
python3 08_Scripts/check_team_repository.py
```

This checks shared files, catalogs, project paths and joins without running CFD. For CFD logic or formula changes, use the relevant [script checks](../08_Scripts/README.md). CI establishes software/file checks; members review data meaning, maps and scientific conclusions. Keep personal editor, agent, host and login settings local; see [Contributing](../CONTRIBUTING.md).

## First meeting and portfolio

Use [First meeting](../07_Team/Meetings/First_Meeting.md) for users/issues, pilot, transport scope, tools, roles, access and next delivery. Leave choices open until discussed.

The [live portfolio](https://kajicho-wind-heat-carbon-demo.specialgooood.chatgpt.site) connects context, maps, design questions and team resources. One overview and nine thematic maps share the same study area and extent; downloads include PNG and sources. See [Portfolio guide](PORTFOLIO_GUIDE.md).

## Sunday field visit / 周日调研 / 日曜の現地調査

[Community map and field companion](https://kajicho-wind-heat-carbon-demo.specialgooood.chatgpt.site/fieldwork) · [Source-backed guide / 中日提问与路线 / 調査ガイド](Sunday_Fieldwork_2026-10-25/README.md)

25 October 2026 / JST. Five proposed morning stops, contact leads, Chinese–Japanese prompts and a spatial field record. Check watage opening first. Browser drafts are not uploaded or automatically shared.
