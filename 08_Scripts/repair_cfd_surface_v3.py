#!/usr/bin/env python3
"""Union derived LOD1 prisms into a closed solid for snappyHexMesh.
Original CityGML and building IDs are never changed. Internal party walls disappear.
"""
import sys,json,time
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as mf
from shapely.geometry import shape,Point
from shapely.strtree import STRtree
B=Path(sys.argv[1]);features=json.loads((B/'inputs/cfd_buildings_local.geojson').read_text())['features']
solids=[];corepolys=[];coreheights=[];t=time.time()
for f in features:
 g=shape(f['geometry']);p=f['properties'];h=p['height_m']
 for poly in ([g] if g.geom_type=='Polygon' else g.geoms):
  poly=poly.simplify(.05 if p['core'] else .3,preserve_topology=True)
  mesh=trimesh.creation.extrude_polygon(poly,h,engine='earcut')
  assert mesh.is_watertight and mesh.is_volume,p['id']
  solid=mf.Manifold(mf.Mesh(vert_properties=np.asarray(mesh.vertices,dtype=np.float32),tri_verts=np.asarray(mesh.faces,dtype=np.uint32)))
  assert solid.status()==mf.Error.NoError,(p['id'],solid.status())
  solids.append(solid)
  if p['core']:corepolys.append(poly);coreheights.append(h)
print('Union',len(solids),'closed prisms',flush=True)
union=mf.Manifold.batch_boolean(solids,mf.OpType.Add)
assert union.status()==mf.Error.NoError,union.status()
m=union.to_mesh();vertices=np.asarray(m.vert_properties)[:,:3].astype(float);faces=np.asarray(m.tri_verts)
result=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
assert result.is_watertight and result.is_volume
tree=STRtree(corepolys);groups={'context':[],'coreRoofs':[],'coreWalls':[]}
for face,normal,center in zip(faces,result.face_normals,result.triangles_center):
 pt=Point(center[:2]);candidates=tree.query(pt.buffer(.02));is_core=any(corepolys[i].distance(pt)<.02 for i in candidates)
 roof=is_core and normal[2]>.9 and any(abs(center[2]-coreheights[i])<.03 and corepolys[i].distance(pt)<.02 for i in candidates)
 group='coreRoofs' if roof else ('coreWalls' if is_core else 'context')
 groups[group].append((face,normal))
with (B/'inputs/buildings.stl').open('w') as out:
 for group,tris in groups.items():
  out.write('solid '+group+'\n')
  for face,n in tris:
   out.write('facet normal '+' '.join(f'{v:.9g}' for v in n)+'\nouter loop\n')
   for point in vertices[face]:out.write('vertex '+' '.join(f'{v:.9g}' for v in point)+'\n')
   out.write('endloop\nendfacet\n')
  out.write('endsolid '+group+'\n')
stats={'method':'Manifold boolean union of earcut-triangulated LOD1 prisms; internal party walls removed','input_prisms':len(solids),'vertices':len(vertices),'faces':len(faces),'watertight':bool(result.is_watertight),'positive_volume':bool(result.is_volume),'volume_m3':float(result.volume),'core_roof_area_m2':float(sum(result.area_faces[i] for i,(n,c) in enumerate(zip(result.face_normals,result.triangles_center)) if n[2]>.9 and any(abs(c[2]-coreheights[j])<.03 and corepolys[j].distance(Point(c[:2]))<.02 for j in tree.query(Point(c[:2]).buffer(.02))))),'regions':{k:len(v) for k,v in groups.items()},'wall_seconds':time.time()-t}
(B/'inputs/geometry_quality.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats),flush=True)
