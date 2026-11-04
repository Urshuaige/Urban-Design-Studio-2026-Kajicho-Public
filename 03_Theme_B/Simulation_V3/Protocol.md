# CFD protocol

## Question

With weather, geometry, background conditions and mesh held fixed, how does reducing prescribed core-roof sensible heat affect pedestrian wind and the temperature rise from that source? The model uses steady Reynolds-averaged flow (RANS), Boussinesq buoyancy and k-epsilon turbulence. Actual building energy and the complete surface thermal environment require additional inputs.

## Shared inputs

Kajicho 1 & 2 contains 277 core building model objects. Chiyoda/Chuo 2025 CityGML supplies LOD1 volumes. Legacy geometry contains 3,805 objects; the completed 6H candidate contains 3,806. [Domain](../../docs/CFD_DOMAIN.md) explains their air domains. Horizontal GIS CRS is EPSG:6677; the CFD origin is `[-5600,-34320] m`. Ground is currently flat.

Fixed JMA Tokyo weather: 2025-08-30 13:00 JST, 38.4 °C, southerly wind 2.5 m/s at 35.3 m reference height, hourly mean global horizontal radiation 866.67 W/m². Dated weather CSV and [baseline methods](../Public_Baseline/Methods.md) retain quality flags and conversions.

Core-roof albedo is 0.20 or 0.60. Prescribed sensible heat is `qH = (1 − albedo) × GHI × fH`, with assumed `fH=0.20`, giving 138.67 and 69.33 W/m². Other walls, ground and surrounding roofs are adiabatic. Temperature rise represents the prescribed core-roof contribution, not the complete summer thermal environment or electricity savings.

## Numerical method

OpenCFD OpenFOAM 2412 `buoyantBoussinesqSimpleFoam` uses a neutral logarithmic inflow and near-ground roughness `z0=0.1 m`. Upstream conditions and stability remain assumptions to check. Derived building volumes undergo solid-union checks; the current mesh uses stepped/adaptive Cartesian boundaries.

The reference mesh has 8,079,968 cells and switches from 50 upwind startup iterations to second-order advection. The light trial has 2,512,453 cells and first-order upwind advection, with approximately 1 m minimum core-surface/pedestrian resolution and 4 m core-volume resolution. Mesh size reflects a compute budget; concave cells, unresolved tiny objects and narrow-street limits remain documented.

The incompressible temperature equation uses kinematic thermal diffusivity. Heat-flux input to `atmTurbulentHeatFluxTemperature` is first divided by air density, then by Cp in the boundary condition. Physical sensible heat is separately recorded in W/m². Integrate using native face areas and a consistent outward-normal sign. Parallel sums include physical external boundaries only, avoiding duplicate processor interfaces.

## Acceptance and comparison

`CFD_Acceptance_v4.json` specifies normal completion, outer convergence, heat imbalance below 1% for 200 consecutive iterations and stable street probes. The fourth heat-CSV column already includes the roof term; do not subtract roof power twice. A steady-budget deficit is not physical heat storage.

Use each case's numerically accepted state, allowing different iteration counts. Keep sampling positions, building masks and common valid points consistent. Shared display sampling is 1.5 m high at 5 m spacing. Wind uses m/s and temperature differences use K. Colour scaling and a linear solver's final residual do not change acceptance status.

Record domain, mesh, empty-domain inflow preservation and field validation separately. Report final option differences only after their checks pass. Current results remain unaccepted; see [CFD status](../../docs/CFD_STATUS.md).

## Running

See [Scripts](../../08_Scripts/README.md) for data and geometry preparation. Mesh, solver and offline heat-budget runners require explicit case directory, container image, process count and CPU set. Use an isolated directory on a suitable host or scheduler and retain input versions and checkpoints. `config/` provides examples; personal paths, hosts and state stay in `local/`.

Preserve original data. The two roof cases share mesh and weather; explain model or parameter changes in a PR. Full fields are available through [Data access](../../DATA_ACCESS.md).
