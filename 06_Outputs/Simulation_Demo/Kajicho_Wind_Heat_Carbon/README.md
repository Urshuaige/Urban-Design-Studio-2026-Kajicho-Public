2026-10-16: Current source maps and data use the registered course primary, approximate wider and independent poster outlines. See dist/boundary-atlas/registration.json and statistics.json. Historical simulations retain their census geometry.

# Kajicho Urban Design Studio website

`dist/index.html` is the portfolio, with source context, seven original site maps, design questions and downloads. `dist/studies.html` contains parameter studies, `dist/cfd.html` the retained CFD results/checks, `dist/team.html` the team guide, and `dist/style-guide.html` the typography/colour guide. Later context-study additions are versioned alongside the portfolio. This stage adds no CFD calculations.

## Team stage and language

2026-10-15: before design. Main quantitative routes are building energy/carbon and street shade/radiation, with planning/implementation and transport-scope work alongside them. The team has not selected final options or roles. Shared instructions are in root `docs/TEAM_START.md` and `docs/PROJECT_PLAN.md`.

English is the initial language. Chinese, English and Japanese share parameters, geometry and results; an explicit browser language choice is retained. The 3D view still uses the unconverged iteration-100 field; reference/light trials have not passed all checks. See root `docs/CFD_STATUS.md`.

## Open

[Private Site](https://kajicho-wind-heat-carbon-demo.specialgooood.chatgpt.site)

Run `python3 serve_demo.py` in this folder, or `py -3 serve_demo.py` on Windows with Python Launcher. The browser opens a local page; Ctrl+C stops the server. Libraries are bundled in `dist/vendor`, and portfolio fonts are local. No npm installation is needed. System fonts provide fallback.

## Parameter studies

Select a starting point and change one setting at a time. Both views share baseline conditions and colour scales; the right view is the option. Dragging either model rotates both, scrolling zooms, and selecting a building shows its source. Language and parameters are stored in the browser. Export saves parameters, selected scenarios and current metrics as JSON.

| Layer | Calculation variables | Display settings |
| --- | --- | --- |
| Wind | Eight incoming directions; 0/24/48 crowns; 2/4/6 m radius | Speed/difference, contrast, building opacity, animation speed, pause |
| Shade | Spring/summer/winter dates; 09–16 JST; crown count/radius/centre height; core-building height ×0.75/1/1.25/1.5 | Top/synchronised views |
| Carbon | Electricity intensity, saving share, self-used PV share, grid factor | Building colour scale and selection |

Display settings leave values unchanged. Building height affects Shade only. PV applies to electricity remaining after savings; direct use-stage emissions are set to zero, excluding equipment life-cycle emissions.

## Data

The v2 studies use 1,981 PLATEAU LOD1 objects; 277 representative points fall in the draft Kajicho 1 & 2 core. Model publication: 2025; main survey: 2021; source creation: 2024-03-15; download: 2026-10-13. Source heights exist for 1,928 objects and geometric height differences for 53. Source storeys exist for 1,807; others use rounded height/3.3 m. CRS is EPSG:6677, local origin (-5600,-34320) m, with flat ground.

## Calculations

**Wind:** 56 D2Q9 2D cases ran sequentially on IIS, with a 5 m grid, periodic boundaries and constant forcing. Each ran 4,500 steps and averaged the last 500. Crown drag 0.006 is fixed. Each pair uses the baseline all-fluid 90th-percentile speed for that direction as its reference. Numerical checks passed for this teaching batch; core mean relative-speed change was 0 to −0.7653%. Difference contrast can change, while values/units retain the computed difference.

Relative speed is not field-calibrated. The 2D projection omits vertical flow and real urban turbulence. Streamlines follow computed direction, but a minimum visual speed and multiplier mean animation time is not physical time or measured m/s.

**Shade:** 96 building fields = three dates × eight hours × four height factors. Cellwise ray intersections on a 5 m height raster model building obstruction; the frontend adds elliptical crown projections. The denominator is 2,830 fixed core open-ground samples. Baseline shade includes buildings only because trees lack a complete survey. Rays stop at model edges; low sun angles are more sensitive to context extent.

The v2 July 15 noon baseline is 18.763%, compared with v1 polygon projection at 19.929%: −1.166 percentage points, with 219/2,830 sample classifications differing. Matching solar position did not remove the difference, which comes from geometry methods. Do not combine versions as planning benefits or convert shade share directly to air cooling.

**Carbon:** projected area × storeys × assumed electricity intensity × grid factor. Defaults: 120 kWh/m²/year, 20% saving, 0% self-used PV, 0.421 kg CO₂/kWh. Actual energy, direct emissions and air-conditioning waste heat await records. Indirect electricity emissions are not a street CO₂-plume input.

## Reproduce and attribution

`dist/data/wind-v2.json` indexes 56 Float32 flow fields. `shade-v2.json` indexes 96 Uint8 fields in `shade-v2.bin`; `core-mask.bin` defines the common denominator. See `provenance.json` for sources/processing.

Authoritative scripts live in root `08_Scripts`. Rebuilding inputs needs external originals and the corresponding Python/QGIS environment; independent web viewing needs only `dist` and the server script. Originals, logs and sources are listed in root `DATA_ACCESS.md`.

Historical v2 resource allocation: two IIS tasks, each one CPU and a 1 GiB address-space limit, with 120 CPU seconds per calculation process. Other remote modelling environments were not changed.

PLATEAU / MLIT and local governments: CC BY 4.0. OpenStreetMap contributors: ODbL, roads snapshot 2026-10-13. Census boundary: 2020. Software licences: `dist/vendor/*LICENSE.txt`.
