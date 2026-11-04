# Contributing

## Tasks and submissions

Start with [Team start](docs/TEAM_START.md) and choose a task from the [task queue](07_Team/Task_Queue.csv). Owners and reviewers remain unassigned until the team agrees. This stage adds no CFD runs.

State the place, question, deliverable, owner and reviewer in an issue. Use a separate branch for each task. A pull request should describe the change, sources and checks; update the shared baseline after review and merge. Members may choose their own editor, AI tools and compute environment.

Keep personal `AGENTS.md`, `CLAUDE.md`, tool folders, SSH aliases, host logs, continuation settings and upload receipts locally. Store actual configuration in ignored `local/`; share examples in `config/`. Shared scientific and data agreements are defined here, in the [data guide](docs/DATA_GUIDE.md) and in the method documents.

## Language and maps

Use English for new filenames, documentation, comments and project-authored descriptions. Keep Chinese and Japanese README options and website translations. Preserve official source titles, quoted text, place names, IDs and data field names; provide English explanations alongside them. See [Language guide](docs/LANGUAGE_GUIDE.md).

Export maps as PNG. Keep lightweight JPEG previews, GIS sources, scripts and provenance with the delivery. Do not generate or distribute SVG maps.

## Data changes

Reserve editing time for a shared QGIS project or GeoPackage in an issue. One person writes the main file at a time. Others return separate GeoPackages, GeoJSON or CSV for the data lead to merge. Resolve binary conflicts from saved copies, rather than trying to combine them in Git. Join added attributes through stable source IDs such as `building_id`; retain unmatched records and their sources.

Register source URL, provider, survey year, publication year, download date, spatial unit, CRS, licence and processing. Preserve source IDs and fields; use separate fields for reprojection, repairs and derived values. After adding or changing a GeoPackage, run `python3 08_Scripts/build_layer_catalog.py` and commit both catalogs.

Keep dated baselines. Save new results under a new date and identify the previous version and changed scope. Leave missing values missing; distinguish source/model attributes, floor-area proxies, energy estimates and measurements.

## Code and calculation

Record input version, assumptions, software, parameters, resource allocation and acceptance criteria. The person running a job configures host paths and CPU/GPU allocation under the host or scheduler rules. Team members need not use the same host.

CFD baseline and intervention cases share geometry, mesh, weather, sample locations and comparison definitions. Explain parameter changes in the PR. Record normal completion, CI status and scientific acceptance separately. Final comparisons require the corresponding numerical checks to pass. Store full meshes, partitioned fields and logs in the agreed external storage; keep reproducible code, source manifests and compact checks here.

The website can be previewed locally. A maintainer publishes it through the deployment environment. Private hosting IDs and login configuration are not required in shared PRs.

## Review

Run checks relevant to the changed behaviour. CI checks QGIS paths, key joins, CFD acceptance logic and website formulas. For GIS changes, also open the project and inspect extent, styles and fields. Review methods, units and whether the evidence supports the conclusions.

The root AGENTS.md and docs/COMPUTE_POLICY.md are shared policy. Personal agent settings belong in ignored AGENTS.local.md or local/. Shared rules, governance, templates and rule checkers change only through a dedicated PR against main.
