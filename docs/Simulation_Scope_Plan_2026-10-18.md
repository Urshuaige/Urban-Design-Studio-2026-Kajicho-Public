# Simulation scope after Figure 5

Current execution planning is in [20 October work plan](Environmental_Work_Plan_2026-10-20/README.md). This dated scope record remains evidence for the Figure 5 mapping update.

The official brief sets two study levels in one view: the solid Kajicho primary area (10.70 ha, 277 model objects) and dashed approximate wider district (41.99 ha, 1074 objects).
The source-pixel traces are retained. Registration RMSE is 7.43 m, with a 25 m cartographic screening band; model membership sensitivity is in statistics.json.

1. Keep the primary area as the design focus and the wider area as the context/reporting scope. These are reporting areas; neither automatically defines the air-domain box.
2. Use the POI function mix and local concentrations to choose field-survey routes and candidate streets near Kanda station. Confirm building/roof geometry, vegetation, street use and intervention on site.
3. Rebuild membership, surface masks and samples for both source scopes. Keep complete source model geometry; no outline expansion to preserve old inventories.
4. For a selected pilot, rebuild surrounding shade context and the wind-aligned air domain after the relevant weather cases and heights are known. Apply the recorded context and domain criteria, then check sensitivity. No new numeric domain dimensions are fixed.
5. Rebuild mesh, inlet profiles and probes where geometry or physical inputs change. Check convergence, thermal balance and mesh/domain sensitivity under the existing acceptance protocol.
6. Report paired design changes on common samples. POI counts are activities, not heat loads; building floor proxies are separate from measured energy. Collect energy/material inputs before energy/carbon claims.

The previous 6000-iteration reference and 2000-iteration light cases retain their unaccepted numerical status. No new CFD, radiation, building-energy run or queued case is authorized by this plan.

Sources: [Official brief Figure 5](https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view), saved COST 732 source and [UMEP SOLWEIG manual](https://umep-docs.readthedocs.io/en/latest/processor/Outdoor%20Thermal%20Comfort%20SOLWEIG.html).
Exact recorded criteria, weather and historical input values remain in Simulation_Scope_Plan_2026-10-18.json.
