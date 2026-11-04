#!/usr/bin/env python3
"""Check newly generated native mesh; no case-specific repairs are inherited."""
import json,re,sys,subprocess
from pathlib import Path
b=Path(sys.argv[1]);s=(b/'logs/checkMesh.log').read_text()
def value(pattern):
 m=re.search(pattern,s);assert m,pattern
 return float(m.group(1).rstrip('.'))
fail=re.search(r'Failed (\d+) mesh checks',s)
nfail=int(fail.group(1)) if fail else 0
assert nfail<=1, 'Inspect this new mesh before solving: multiple failed categories'
assert not fail or 'Concave cells (using face planes)' in s
assert 'Cells with small determinant' not in s, 'New weak cells need their own diagnosis'
q={'cells':int(value(r'\bcells:\s+(\d+)')),
 'minimum_volume_m3':value(r'Min volume = ([\deE.+-]+)'),
 'maximum_nonorthogonality_deg':value(r'non-orthogonality Max: ([\deE.+-]+)'),
 'maximum_skewness':value(r'Max skewness = ([\deE.+-]+)'),
 'minimum_face_weight':value(r'Face interpolation weight : minimum: ([\deE.+-]+)'),
 'minimum_internal_face_connectivity_determinant':value(r'Cell determinant.*?minimum: ([\deE.+-]+)'),
 'all_geometry_failed_categories':nfail,
 'concave_cells':int(value(r'Concave cells.*?number of cells: (\d+)')) if fail else 0,
 'remaining_weak_connectivity_cells':0,'local_repair':'none',
 'mesh_type':'native castellated Cartesian/octree; snap false',
 'geometry_error':'Staircase boundaries; narrow gaps and the small-object patch require explicit checks.',
 'scientific_validation':'convergence, heat balance, mesh and domain sensitivity pending',
 'accepted_for_exploratory_pair':True,'source_log':'logs/checkMesh.log'}
assert q['minimum_volume_m3']>0
assert q['maximum_nonorthogonality_deg']<65 and q['maximum_skewness']<4
assert q['minimum_face_weight']>=.05 and q['minimum_internal_face_connectivity_determinant']>=.001
# Check the generated boundary, not just the input STL or refinement request.
# The official surfaceMeshExtract utility is provided by the pinned image.
subprocess.run(['docker','run','--rm','--entrypoint','/bin/bash',
 '--user',f'{__import__("os").getuid()}:{__import__("os").getgid()}',
 '-v',f'{b.resolve()}:/work','opencfd/openfoam-default:2412','-lc',
 'source /usr/lib/openfoam/openfoam2412/etc/bashrc; set -e; cd /work/cases/mesh_cartesian; '
 'surfaceMeshExtract -constant -patches "(buildings_context)" /work/inputs/meshed_context.stl > /work/logs/extract_context_surface.log 2>&1'],check=True)
import numpy as np
import trimesh
from shapely.geometry import shape
from shapely import contains_xy
paths=list((b/'inputs').glob('meshed_context*.stl'))
assert len(paths)==1, paths
surface=trimesh.load_mesh(paths[0],process=False)
centres=surface.triangles_center;normals=surface.face_normals
lookup={f['properties']['id']:f for f in json.loads((b/'inputs/cfd_buildings_local.geojson').read_text())['features']}
q['small_object_boundary_checks']=[]
for item in json.loads((b/'inputs/small_object_refinement.json').read_text()):
 f=lookup[item['id']];g=shape(f['geometry']);h=f['properties']['height_m']
 near=contains_xy(g.buffer(.4),centres[:,0],centres[:,1])
 # This is the fluid-domain boundary: the air's outward normal at a roof
 # points down into the solid, opposite to the original solid STL normal.
 roof=near&(abs(centres[:,2]-h)<=.4)&(normals[:,2]<-.8)
 wall=near&(centres[:,2]>.5)&(centres[:,2]<h-.5)&(abs(normals[:,2])<.2)
 result={'id':item['id'],'nearby_roof_triangles':int(roof.sum()),'nearby_wall_triangles':int(wall.sum()),
  'nearby_roof_area_m2':float(surface.area_faces[roof].sum()),'horizontal_check_buffer_m':.4,
  'resolved_boundary_present':bool(roof.any() and wall.any()),
  'scope':'Local roof and wall presence on the generated patch; this does not establish mesh-independent flow.'}
 q['small_object_boundary_checks'].append(result)
 assert result['resolved_boundary_present'], 'The newly included small object was not resolved by this mesh'
(b/'inputs/mesh_quality.json').write_text(json.dumps(q,indent=2))
print(json.dumps(q,indent=2))
