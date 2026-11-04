#!/usr/bin/env python3
"""Prepare a native castellated-only alternative; preserve the snapped trial.

The same STL and domain are used. Boundary location has a cell-size approximation.
"""
import sys,json,shutil
from pathlib import Path
B=Path(sys.argv[1]);src=B/'trials/02_upwind_snapped_mesh/baseline';dst=B/'cases/mesh_cartesian';assert not dst.exists()
shutil.copytree(src/'system',dst/'system');shutil.copytree(src/'0',dst/'0');shutil.copytree(src/'constant',dst/'constant',ignore=shutil.ignore_patterns('polyMesh'))
p=dst/'system/snappyHexMeshDict';s=p.read_text().replace('snap true','snap false');p.write_text(s)
p=dst/'system/decomposeParDict';s=p.read_text().replace('numberOfSubdomains 32','numberOfSubdomains 64');p.write_text(s)
# Restore final target schemes in the mesh's template; startup is staged separately.
p=dst/'system/fvSchemes';s=p.read_text().replace('div(phi,U) bounded Gauss upwind','div(phi,U) bounded Gauss linearUpwind grad(U)').replace('div(phi,T) bounded Gauss upwind','div(phi,T) bounded Gauss linearUpwind grad(T)');p.write_text(s)
(B/'inputs/mesh_selection.json').write_text(json.dumps({'case':dst.name,'type':'castellated Cartesian/octree; snap false','geometry_reference':'same original-derived STL; no source geometry edit','boundary_location_error':'cell-size approximation; core walls ~1m and near-ground ~0.5m; verify against STL and mesh sensitivity','reason':'snapped boundary pockets produced nonphysical local velocity despite bounded startup and pressure solve checks'},indent=2))
print(dst,flush=True)
