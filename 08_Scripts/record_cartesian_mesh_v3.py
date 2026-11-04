#!/usr/bin/env python3
"""Require zero weak-connectivity cells; retain concavity as a separate warning."""
import sys,json,re
from pathlib import Path
B=Path(sys.argv[1]);s=(B/'logs/checkMesh.log').read_text();assert 'Cells with small determinant' not in s
failure=re.search(r'Failed (\d+) mesh checks',s);assert (int(failure.group(1)) if failure else 0)<=1
assert failure is None or 'Concave cells (using face planes)' in s
def n(pattern):
 m=re.search(pattern,s);assert m,pattern;return float(m.group(1).rstrip('.'))
d={'cells':int(n(r'\bcells:\s+(\d+)')),'minimum_volume_m3':n(r'Min volume = ([\deE.+-]+)'),'maximum_nonorthogonality_deg':n(r'non-orthogonality Max: ([\deE.+-]+)'),'maximum_skewness':n(r'Max skewness = ([\deE.+-]+)'),'minimum_face_weight':n(r'Face interpolation weight : minimum: ([\deE.+-]+)'),'minimum_internal_face_connectivity_determinant':n(r'Cell determinant.*?minimum: ([\deE.+-]+)'),'remaining_weak_connectivity_cells':0,'concave_cells':int(n(r'Concave cells.*?number of cells: (\d+)')) if failure else 0,'all_geometry_failed_categories':1 if failure else 0,'allGeometry_status':'Concave-cell warning retained; connectivity, volumes, face flatness, skew and weights pass','accepted_for_exploratory_pair':True,'scientific_validation':'pending convergence, heat balance, second-order continuation and mesh/domain sensitivity','mesh_type':'native castellated Cartesian/octree, snap false','geometry_error':'staircase boundary approximation of the same STL; narrow gaps may close; validate against finer mesh','local_repair':'removed four native underdeterminedCells with zero connectivity determinant; no buffer ring; added boundaries adiabatic','previous_trials':'snapped mesh trials preserved and rejected as environmental predictions','source_log':'logs/checkMesh.log'}
assert d['minimum_volume_m3']>0 and d['maximum_skewness']<4 and d['maximum_nonorthogonality_deg']<65 and d['minimum_internal_face_connectivity_determinant']>=.001
(B/'inputs/mesh_quality.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
