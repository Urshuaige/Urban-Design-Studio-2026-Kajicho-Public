#!/usr/bin/env python3
"""Build field-visit GIS from recorded geocodes and the current Figure 5 atlas."""
import argparse,copy,json
from pathlib import Path
from urllib.parse import urlencode

def build(task_root):
 root=Path(task_root);team=root/'team';source=team/'docs/Sunday_Fieldwork_2026-10-25'
 guide=json.loads((source/'Guide_Source.json').read_text())
 geocodes=json.loads((source/'Geocoding_Record.json').read_text())
 atlas=json.loads((root/'site/dist/study-atlas/atlas.geojson').read_text())
 boundaries=json.loads((root/'site/dist/study-atlas/study_boundary.geojson').read_text())
 boundary=next(f for f in boundaries['features'] if f['properties']['id']=='study_area')
 rings=boundary['geometry']['coordinates']
 if boundary['geometry']['type']=='MultiPolygon':rings=rings[0]
 def in_ring(x,y,ring):
  inside=False
  for (x1,y1),(x2,y2) in zip(ring,ring[1:]):
   if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:inside=not inside
  return inside
 def within(c):return in_ring(*c,rings[0]) and not any(in_ring(*c,r) for r in rings[1:])
 points=[]
 for p in guide['places']:
  if p.get('geocode_query'):
   result=geocodes['responses'][p['geocode_query']]
   p['coordinates']=result[0]['geometry']['coordinates']
   p['geocode_result']=result
   p['location_source']='https://msearch.gsi.go.jp/address-search/AddressSearch?'+urlencode({'q':p['geocode_query']})
   p['location_method']='Official address -> GSI Address Search; returned '+result[0]['properties']['title']+'. Address/block reference, not a surveyed entrance.'
   p['geocode_checked_on']='2026-10-21'
  p['in_wider_area']=within(p['coordinates'])
  props={k:v for k,v in p.items() if k not in ('coordinates','name','task','geocode_result')}
  props.update({'name_'+l:v for l,v in p['name'].items()})
  props['source_urls']=[next(s['url'] for s in guide['sources'] if s['id']==sid) for sid in p['sources']]
  props['contact_ids']=[c['id'] for c in guide['contacts'] if c['place']==p['id']]
  props['activity_indices']=[i for i,a in enumerate(guide['activities']) if a['place']==p['id']]
  points.append({'type':'Feature','properties':props,'geometry':{'type':'Point','coordinates':p['coordinates']}})
 def vertices(c):
  if c and isinstance(c[0],(int,float)):yield c
  else:
   for v in c:yield from vertices(v)
 def intersects(f):
  cs=list(vertices(f['geometry']['coordinates']))
  return cs and max(c[0] for c in cs)>=139.757 and min(c[0] for c in cs)<=139.779 and max(c[1] for c in cs)>=35.688 and min(c[1] for c in cs)<=35.699
 context=[];streets=[];past_event=[]
 for f in atlas['features']:
  p=f['properties']
  if p.get('layer') not in ('roads','rail','water','osm_buildings') or not intersects(f):continue
  feature={'type':'Feature','properties':{k:v for k,v in p.items() if k in ('osm_id','name','layer','tag','source_date')},'geometry':f['geometry']}
  context.append(feature)
  if p.get('osm_id') in ('232805829','264115339','264114582','264114583'):past_event.append(copy.deepcopy(feature))
  if p.get('layer')=='roads' and p.get('name') in ('神田ふれあい通り','神田金物通り'):
   streets.append(copy.deepcopy(feature))
 out=team/'06_Outputs/Community_Fieldwork_2026-10-25';out.mkdir(parents=True,exist_ok=True)
 def write(name,d): (out/name).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
 meta={'crs':'OGC:CRS84','coordinate_order':'longitude, latitude','checked_on':guide['checked_on'],'license':'Point descriptions: original short notes with source links. OSM-derived anchors and linework: ODbL 1.0. GSI coordinates: GSI terms linked in guide.','processing':guide['spatial_metadata']}
 write('guide.json',guide)
 for name,features in [('places.geojson',points),('boundary.geojson',[boundary]),('streets.geojson',streets),('past-event-street.geojson',past_event),('context.geojson',context)]:
  write(name,{'type':'FeatureCollection','metadata':meta,'features':features})
 assert len(points)==9 and len(streets)>0
 assert not next(p for p in guide['places'] if p['id']=='books')['in_wider_area']
 assert not next(p for p in guide['places'] if p['id']=='sports')['in_wider_area']
 assert all(next(p for p in guide['places'] if p['id']==id)['in_wider_area'] for id in ('watage','cwl'))
 print(json.dumps({'points':len(points),'context_features':len(context),'street_segments':len(streets),'boundary_features':1,'geometry_or_model_changes':False},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--task-root',required=True);a=p.parse_args();build(a.task_root)
