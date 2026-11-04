# Field and action templates

Use [Team start](../../docs/TEAM_START.md) for collection and handover steps and [Task queue](../Task_Queue.csv) for starting tasks. Fill a copy of each template and keep the source template empty. Use [First meeting](../Meetings/First_Meeting.md) for initial decisions.

`Field_Observations.csv` records date/time, coordinates, building/street ID, use, storeys, shade and access. Longitude/latitude uses EPSG:4326; record the actual CRS for other coordinates. Use relative photo paths and distinguish observation from inference.

`Stakeholder_Register.csv` records roles, management/decision rights, data access, investment, upkeep and supporting evidence. Leave `contact_status` empty until the team agrees external contact.

`Action_Cards.csv` links place, issue, evidence, baseline, option, carbon scope, climate metric, beneficiaries, delivery actors, cost, upkeep and checks. Leave uncalculated CO₂ values empty. Put assumptions in `assumptions`; name each climate metric, unit and time window.

`Analysis_Pilot.md` fixes the question, options, metrics, scope, budget and stopping conditions before calculation. Read it with [Project plan](../../docs/PROJECT_PLAN.md).

`Building_Energy_Input.csv` is the empty metered-energy form. The use-specific DECC range form is `04_Data/Ready/Public_Baseline_2026-10-14/DECC_EUI_Input_Template.csv` from the repository root. Record `period`, `supplier`, `tariff_menu`, `factor`, `source` and `privacy_and_share_scope`. Keep raw details in authorised local/external storage and share only the permitted level of detail. Fill `owner` and `reviewer` after the team agrees roles.
