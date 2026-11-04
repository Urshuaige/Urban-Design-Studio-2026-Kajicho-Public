# Archived case settings

Read-only snapshot from the original trial after the common iteration50 restart, 2026-10-14. The pair uses the same 8,187,492-cell Cartesian/octree mesh and the same weather; core-roof heat differs by scenario.

These folders contain actual system dictionaries, transport/turbulence settings and initial temperature boundaries. Full meshes, processor fields and compiled libraries remain on the compute host. Use the original builder to create initial fields, then native setExprFields to reproduce the saved neutral U/k/epsilon profile.

The saved topoSetDict records the four-cell connectivity repair; inspect current cell sets before using a repair on a newly generated mesh. Original PLATEAU files remain unchanged. Numerical checks, thermal balance and sensitivity are recorded separately from this settings snapshot.

This is a configuration record, not a running-job instruction. Current numerical meaning is in `docs/CFD_STATUS.md` at the repository root. Execution directories and resources are configured by each runner.
