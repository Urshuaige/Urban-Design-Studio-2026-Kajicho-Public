#!/usr/bin/env python3
"""Screen seven adjacent wards using official LOD1 tile metadata (no CFD work)."""
import json, math, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime,timezone
from pyproj import Transformer
from shapely.geometry import Polygon,shape

R=Path(__file__).resolve().parents[1];RAW=R/'04_Data/Raw/CFD_Domain_Audit_2026-10-14';RAW.mkdir(parents=True,exist_ok=True)
core=shape(json.loads((R/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data/cfd-context.json').read_text())['boundary'])
tr=Transformer.from_crs(4326,6677,always_xy=True);origin=(-5600,-34320)
def polygon(region):
 w,s,e,n=map(math.degrees,region[:4]);points=[]
 for lon,lat in [(w,s),(e,s),(e,n),(w,n)]:
  x,y=tr.transform(lon,lat);points.append((x-origin[0],y-origin[1]))
 return Polygon(points)
def fetch(url,path):
 if path.exists():return json.loads(path.read_text())
 with urllib.request.urlopen(url,timeout=30) as r:d=json.load(r)
 path.write_text(json.dumps(d,ensure_ascii=False));return d
wards=[];leaves=[]
for ward in ['13101','13102','13103','13105','13106','13107','13108']:
 url=f'https://api.plateauview.mlit.go.jp/datacatalog/3dtiles/{ward}-bldg-lod1-latest/tileset.json'
 try:
  wrapper=fetch(url,RAW/f'{ward}_lod1_wrapper.json')
  for ci,ch in enumerate(wrapper['root'].get('children',[])):
   asset=ch.get('content',{}).get('uri')
   if not asset:continue
   d=fetch(asset,RAW/f'{ward}_lod1_{ci}.json')
   h=d.get('properties',{}).get('bldg:measuredHeight',{}).get('maximum')
   region=d['root']['boundingVolume']['region'];geom=polygon(region)
   upper=max(float(h or 0),float(region[5]-region[4]));dist=geom.distance(core)
   wards.append({'ward':ward,'url':asset,'H_upper_m':upper,'measured_height_max_m':h,'ward_bbox_distance_m':dist,'possible6H':dist<=6*upper,'possible10H':dist<=10*upper})
   def walk(node):
    if node.get('children'):
     for c in node['children']:walk(c)
    else:
     content=node.get('content',{});reg=content.get('boundingVolume',node.get('boundingVolume',{})).get('region')
     if reg and content.get('uri'):
      dist=polygon(reg).distance(core)
      leaves.append({'ward':ward,'url':urllib.parse.urljoin(asset,content['uri']),'distance_lower_bound_m':dist,'H_upper_m':upper,'possible6H':dist<=max(500,6*upper),'possible10H':dist<=max(500,10*upper),'region':reg})
   walk(d['root'])
  print(ward,wards[-1] if wards else 'no ward',flush=True)
 except Exception as e:
  wards.append({'ward':ward,'error':str(e)});print(ward,str(e),flush=True)
output={'snapshot_utc':datetime.now(timezone.utc).isoformat(),'method':'Whole-ward measuredHeight maximum or root vertical range, whichever is larger; leaf envelope distance lower bound. Conservative candidate screening only, not per-building inclusion.',
 'search_scope':'Chiyoda, Chuo, Minato, Bunkyo, Taito, Sumida, Koto; seven adjacent wards around current6.18x7.30km domain','wards':wards,'leaves':leaves,
 'license':'PLATEAU CC BY4.0; retain original source metadata','crs':'EPSG:6677 with local origin[-5600,-34320]','sources':'Official PLATEAU catalog wrappers and their referenced LOD1 assets; latest dataset year preserved in asset URL'}
(RAW/'Wider_Tile_Screen.json').write_text(json.dumps(output,indent=2,ensure_ascii=False))
print('possible leaves',sum(x['possible6H'] for x in leaves),sum(x['possible10H'] for x in leaves),flush=True)
