# CFD status

Current work is [fieldwork → geometry → shade/radiation → conditional wind](Environmental_Work_Plan_2026-10-20/README.md). No new mesh, solver, radiation calculation or benchmark was started on 20 October 2026.

The current course priorities are in [Project plan](PROJECT_PLAN.md). This page preserves the completed wind/heat trials and their diagnostic state. Further local wind studies require a specific design question and a separate analysis pilot.

2026-10-15: both trial pairs have ended without passing every numerical acceptance check. The shared website and six QGIS wind/heat rasters retain the unconverged iteration-100 snapshot. No final wind/heat field in this batch supports a verified planning benefit.

| Check | Reference: baseline / cool roof | Light: baseline / cool roof |
| --- | --- | --- |
| Air cells | 8,079,968 | 2,512,453 |
| Final iterations | 6000 / 6000 | 2000 / 2000 |
| Normal completion | Yes / Yes | Yes / Yes |
| Outer pressure and temperature convergence | Fail / Fail | Fail / Fail |
| Maximum heat imbalance over last 200 iterations | 5.48% / 2.24% | 0.91% / 1.75% |
| Street-probe tail stability | Fail / Fail | Pass / Pass |
| Full numerical acceptance | Fail / Fail | Fail / Fail |

Project acceptance requires heat imbalance below 1% for 200 consecutive iterations, outer convergence and stable street probes. The rules are in `03_Theme_B/Simulation_V3/CFD_Acceptance_v4.json`. These are project numerical criteria, separate from prediction accuracy and comfort standards.

Individual checks and actual heat-imbalance histories are in `06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data/cfd-numerical-checks.json`. An offline diagnosis of the fixed reference end state checked flux units, signs, areas and parallel external-boundary sums. The original budget matched the independent calculation. The actual bounded correction was below 0.1% of the physical heat imbalance; the remaining deficit was consistent with a temperature equation that had not reached steady balance. It does not represent physical heat storage in this steady model.

20 October 2026: obsolete full native checkpoints, parallel partitions, meshes and post-processing folders were removed after checking that no active process used them. The old cases cannot resume from full fields. Inputs, logs, diagnostic reviews and exported unconverged teaching fields remain; see the [cleanup record](Environmental_Work_Plan_2026-10-20/CLEANUP.md) and [Data access](../DATA_ACCESS.md).

The physical comparison prescribes sensible heat from core roofs. Weather, geometry and mesh are shared; roof albedo is the changed parameter. Other surfaces are adiabatic, so temperature rise represents this prescribed source's contribution. Mesh, domain, inlet-preservation and field validation remain open. The trials do not provide a verified estimate of the small cool-roof benefit.
