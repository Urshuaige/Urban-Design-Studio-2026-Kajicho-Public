# Wind, heat and shared data

Current course geography: [registered boundary release](../../docs/COURSE_BOUNDARIES.md). This dated package records the earlier census ROI; use the current course atlas for source-area totals.

This module compares baseline and cool roofs under the same weather. Inputs, methods and acceptance criteria are shared; members configure their own run directories and hardware.

- [Protocol](Protocol.md): model, weather, heat flux and sampling.
- [CFD status](../../docs/CFD_STATUS.md): completed trials, acceptance checks and result use.
- [Domain](../../docs/CFD_DOMAIN.md): evaluation area, explicit buildings and air domain.
- [Data guide](../../docs/DATA_GUIDE.md): shared layers and fields.

Open `05_QGIS/Projects/Kajicho_CFD_Baseline_2026-10-14.qgz` from the repository root, keeping relative folder locations. Its 45 vector layers include buildings, planning, greenery and flood information; six CFD rasters retain the unconverged iteration-100 field. Source data and survey forms are in `04_Data/Ready/CFD_Baseline_2026-10-14`. Originals are in external project storage.

Calculation code is in `08_Scripts`. `Case_Settings` is a saved OpenFOAM configuration snapshot from the first trial. Generate separate, versioned cases for new inputs; configuration files alone do not establish accepted results. DECC energy data, reliable individual core street-tree positions and legal site conditions are still needed.
