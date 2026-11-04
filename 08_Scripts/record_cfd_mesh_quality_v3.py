#!/usr/bin/env python3
"""Record configured checks and remaining warnings separately before exploratory solving."""
import sys,json,re
from pathlib import Path
B=Path(sys.argv[1]);s=(B/'logs/checkMesh_repaired.log').read_text(errors='replace')
def number(pattern):
 m=re.search(pattern,s);assert m,pattern;return float(m.group(1).rstrip('.'))
for token in ['Cell volumes OK.','Face pyramids OK.','Face tets OK.','Non-orthogonality check OK.','Face interpolation weight check OK.','Coupled point location match']:
 assert token in s,token
quality={'cells':int(number(r'\bcells:\s+(\d+)')),'minimum_volume_m3':number(r'Min volume = ([\deE.+-]+)'),'maximum_nonorthogonality_deg':number(r'non-orthogonality Max: ([\deE.+-]+)'),'maximum_skewness':number(r'Max skewness = ([\deE.+-]+)'),'minimum_face_weight':number(r'Face interpolation weight : minimum: ([\deE.+-]+)'),'minimum_internal_face_connectivity_determinant':number(r'Cell determinant.*?minimum: ([\deE.+-]+)'),'remaining_weak_connectivity_cells':int(number(r'Cells with small determinant.*?number of cells: (\d+)')),'concave_cells':int(number(r'Concave cells.*?number of cells: (\d+)')),'all_geometry_failed_categories':int(number(r'Failed (\d+) mesh checks'))}
assert quality['minimum_volume_m3']>0 and quality['maximum_nonorthogonality_deg']<65 and quality['maximum_skewness']<4 and quality['minimum_face_weight']>=.05
assert quality['remaining_weak_connectivity_cells']<=2 and quality['minimum_internal_face_connectivity_determinant']>0
assert quality['all_geometry_failed_categories']==2
quality.update({'accepted_for_exploratory_pair':True,'scientific_validation':'pending convergence, conservation, inlet and mesh/domain sensitivity','configured_snappy_checks':'passed','allGeometry_status':'2 warning categories remain; not a clean allGeometry pass','remaining_warning_interpretation':'Two nonzero weak-connectivity cells outside the core are retained after bounded local repair; concave-cell classification differs from snappy face-angle quality. Preserve exact locations and review paired sensitivity before scientific use.','local_repairs':'7 isolated weak cells, then2adjacent cells, then8cells in a one-ring pocket repair; added surfaces are adiabatic context wall','official_originals':'unchanged; only derived fluid mesh modified','source_log':'logs/checkMesh_repaired.log'})
(B/'inputs/mesh_quality.json').write_text(json.dumps(quality,indent=2));print(json.dumps(quality),flush=True)
