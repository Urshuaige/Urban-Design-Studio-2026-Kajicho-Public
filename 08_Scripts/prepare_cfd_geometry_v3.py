#!/usr/bin/env python3
"""Stream LOD1 CityGML to flat-ground CFD geometry, preserving all core IDs.
Context includes buildings within 500 m and every source building within 6H of ROI.
All source triangles/coordinates stay in archived CityGML; this is a derived extrusion.
"""
import json,sys,xml.etree.ElementTree as ET,struct,math
from pathlib import Path
from collections import Counter
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon,shape,mapping,MultiPolygon
from shapely.affinity import translate
from shapely.ops import unary_union,triangulate
BASE=Path(sys.argv[1]);data=json.loads((BASE/'inputs/city.json').read_text());origin=data['meta']['origin_epsg6677'];core=shape(data['boundary']);coreids={b['id'] for b in data['buildings'] if b['core']};old={b['id']:b for b in data['buildings']}
tr=Transformer.from_crs(6668,6677,always_xy=True);G='{http://www.opengis.net/gml}';B='{http://www.opengis.net/citygml/building/2.0}';C='{http://www.opengis.net/citygml/2.0}'
bs={};omitted=[];bad=[];sources=[]
cached=BASE/'inputs/cfd_buildings_local.geojson'
paths=sorted((BASE/'inputs/gml').glob('*.gml'))
if '--cached' in sys.argv:
 for f in json.loads(cached.read_text())['features']:
  b=f['properties'];b['geometry']=shape(f['geometry']);bs[b['id']]=b
 sources=[p.name for p in paths if not p.name.startswith('._')]
 omissions_path=BASE/'inputs/context_omissions.json'
 if omissions_path.exists():omitted=json.loads(omissions_path.read_text())
for p in ([] if '--cached' in sys.argv else paths):
 if p.name.startswith('._'):continue
 it=ET.iterparse(p,events=('start','end'));_,root=next(it);n=0
 for ev,node in it:
  if ev!='end' or node.tag!=C+'cityObjectMember':continue
  b=node[0];id=b.get(G+'id');lod=b.find(B+'lod1Solid')
  if lod is not None and id not in bs:
   polys=[];zs=[]
   for poly in lod.iter(G+'Polygon'):
    ring=poly.find('.//'+G+'exterior//'+G+'posList')
    if ring is None:continue
    a=np.fromstring(ring.text,sep=' ').reshape(-1,3);zs.extend(a[:,2]);x,y=tr.transform(a[:,1],a[:,0]);g=Polygon(np.column_stack((x-origin[0],y-origin[1])))
    if g.area>.05:polys.append(g)
   if polys:
    geom=unary_union(polys)
    if not geom.is_valid:geom=geom.buffer(0)
    h=b.findtext(B+'measuredHeight');h=float(h) if h and 0<float(h)<1000 else float(max(zs)-min(zs));h=old.get(id,{}).get('h',h)
    dist=geom.distance(core)
    if (id in coreids or dist<=max(500,6*h)) and h>1 and geom.area>1:
     bs[id]={'id':id,'height_m':h,'core':id in coreids,'distance_to_core_m':dist,'source_mesh':p.name,'ground_source_m':float(min(zs)),'geometry':geom};n+=1
    else:omitted.append({'id':id,'height_m':h,'distance_to_core_m':dist,'source_mesh':p.name})
  node.clear();root.clear()
 sources.append(p.name);print(p.name,n,flush=True)
assert coreids.issubset(bs),(len(coreids-set(bs)),list(coreids-set(bs))[:5])
features=[]
for b in bs.values():features.append({'type':'Feature','properties':{k:v for k,v in b.items() if k!='geometry'},'geometry':mapping(b['geometry'])})
(BASE/'inputs/cfd_buildings_local.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':')))
bounds=unary_union([b['geometry'] for b in bs.values()]).bounds;H=max(b['height_m'] for b in bs.values());pad=5*H
# South wind travels +north (model y). COST conservative 5H upwind,15H downwind.
domain=[bounds[0]-pad,bounds[1]-pad,bounds[2]+pad,bounds[3]+15*H,6*H]
from shapely.geometry import box
front=unary_union([box(b['geometry'].bounds[0],0,b['geometry'].bounds[2],b['height_m']) for b in bs.values()]).area
initial_blockage=front/((domain[2]-domain[0])*domain[4])
# Expand symmetrically to 2.8%, below the common 3% frontal-blockage criterion.
required_width=front/(.028*domain[4])
extra=max(0,(required_width-(domain[2]-domain[0]))/2)
domain[0]-=extra;domain[2]+=extra
blockage=front/((domain[2]-domain[0])*domain[4]);assert blockage<.03,blockage
stats={'core_buildings':len(coreids),'context_buildings':len(bs)-len(coreids),'total_buildings':len(bs),'Hmax_m':H,'source_meshes':sources,'built_bounds_m':bounds,'domain_m':domain,'upstream_clearance_m':5*H,'downstream_clearance_m':15*H,'side_clearance_m':5*H+extra,'top_clearance_above_tallest_m':5*H,'projected_frontal_area_m2':front,'initial_projected_frontal_blockage_fraction':initial_blockage,'projected_frontal_blockage_fraction':blockage,'context_selection':'all source buildings within max(500 m, 6*individual_height) of ROI; limited to listed official source meshes','terrain':'flat ground z=0; source base elevations retained for sensitivity; LOD1 extrusion','origin_epsg6677':origin,'omitted_buildings':len(omitted) if omitted else None,'omitted_relevant_6H':sum(b['distance_to_core_m']<6*b['height_m'] for b in omitted) if omitted else None,'core_bounds_m':core.bounds}
(BASE/'inputs/domain.json').write_text(json.dumps(stats,indent=2));(BASE/'inputs/context_omissions.json').write_text(json.dumps(omitted,separators=(',',':')))
# ASCII multi-region STL. Each core object's roof/walls together form a closed prism.
regions={'context':[],'coreRoofs':[],'coreWalls':[]}
def triangle(reg,pts):
 a=np.array(pts);normal=np.cross(a[1]-a[0],a[2]-a[0]);norm=np.linalg.norm(normal)
 if norm<1e-10:return
 normal/=norm;regions[reg].append((normal,a))
for b in bs.values():
 geom=b['geometry'];h=b['height_m'];rroof='coreRoofs' if b['core'] else 'context';rwall='coreWalls' if b['core'] else 'context'
 for poly in ([geom] if geom.geom_type=='Polygon' else geom.geoms):
  poly=poly.simplify(.05 if b['core'] else .3,preserve_topology=True)
  from shapely.geometry.polygon import orient
  poly=orient(poly,sign=1)
  for tri in triangulate(poly):
   if not poly.covers(tri.representative_point()):continue
   a=list(tri.exterior.coords)[:3]
   triangle(rroof,[(x,y,h) for x,y in a]);triangle(rwall,[(x,y,0) for x,y in a[::-1]])
  for ring in [poly.exterior,*poly.interiors]:
   coords=list(ring.coords)
   for (x1,y1),(x2,y2) in zip(coords,coords[1:]):
    triangle(rwall,[(x1,y1,0),(x2,y2,0),(x2,y2,h)]);triangle(rwall,[(x1,y1,0),(x2,y2,h),(x1,y1,h)])
with (BASE/'inputs/buildings.stl').open('w') as f:
 for reg,tris in regions.items():
  f.write('solid '+reg+'\n')
  for n,a in tris:
   f.write('facet normal '+' '.join(f'{v:.7g}' for v in n)+'\nouter loop\n')
   for xyz in a:f.write('vertex '+' '.join(f'{v:.7g}' for v in xyz)+'\n')
   f.write('endloop\nendfacet\n')
  f.write('endsolid '+reg+'\n')
print(json.dumps(stats),flush=True)
