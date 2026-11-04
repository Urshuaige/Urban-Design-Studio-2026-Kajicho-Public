#!/usr/bin/env python3
"""Independently verify full-footprint membership, rendering and saved GIS layers."""
import argparse,collections,csv,json,sqlite3,tempfile,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from shapely import wkb
from shapely.geometry import box,shape
import build_boundary_atlas as b
import build_study_atlas as atlas

def source_rows(path,name):
 c=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 col=c.execute('select column_name from gpkg_geometry_columns where table_name=?',(name,)).fetchone()[0]
 rows=[]
 for row in c.execute('select * from "'+name+'"'):
  r=dict(row);blob=bytes(r.pop(col));size={0:0,1:32,2:48,3:48,4:64}[(blob[3]>>1)&7]
  g=wkb.loads(blob[8+size:]);assert g.is_valid,(name,r.get('asset_id') or r.get('osm_id'),'source geometry invalid; must not silently repair')
  rows.append((r,g,blob))
 c.close();return rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--task-root',type=Path,required=True);p.add_argument('--artifacts',action='store_true');p.add_argument('--skip-render',action='store_true');a=p.parse_args()
 root=a.task_root;out=root/'team/06_Outputs/Study_Area_2026-10-18';source=root/'assets/assets.gpkg'
 data=json.loads((out/'study_boundary_6677.geojson').read_text());bounds={f['properties']['id']:(f['properties'],shape(f['geometry'])) for f in data['features']}
 rows={name:source_rows(source,name) for name in ('buildings','osm_buildings')}
 expected={sid:{name:{str(r.get('asset_id') or r.get('osm_id')) for r,g,blob in rs if scope.covers(g)} for name,rs in rows.items()} for sid,(props,scope) in bounds.items()}
 assert {sid:len(v['buildings']) for sid,v in expected.items()}=={'study_area':1074,'primary_brief':277}
 assert {sid:len(v['osm_buildings']) for sid,v in expected.items()}=={'study_area':1029,'primary_brief':232}
 assert atlas.NORTHERN_ID not in expected['study_area']['buildings']
 assert '190375727' not in expected['study_area']['osm_buildings']
 # Regression: a centroid/representative point inside does not admit a crossing object.
 area=box(0,0,10,10);synthetic=[({'asset_id':'inside'},box(1,1,2,2)),({'asset_id':'touching'},box(0,0,2,2)),({'asset_id':'crossing'},box(8,1,11,3)),({'asset_id':'outside'},box(11,1,12,2))]
 assert area.covers(synthetic[2][1].representative_point()) and not area.covers(synthetic[2][1])
 assert {r['asset_id'] for r,g in b.select_full_buildings(synthetic,area)}=={'inside','touching'}
 for sid,(props,scope) in bounds.items():
  actual={r['asset_id'] for r,g in b.select_full_buildings([(r,g) for r,g,z in rows['buildings']],scope)}
  assert actual==expected[sid]['buildings']
 if not a.skip_render:
  north=next((r,g) for r,g,z in rows['buildings'] if r['asset_id']==atlas.NORTHERN_ID)
  inside=next((r,g) for r,g,z in rows['buildings'] if r['asset_id'] in expected['study_area']['buildings'])
  raw={k:[] for k in ('water','osm_buildings','roads','land_use','zones','parks','tree_routes','trees','flood','rail','stations')};raw['buildings']=[north,inside];raw['osm_buildings']=[({'osm_id':'190375727'},next(g for r,g,z in rows['osm_buildings'] if str(r['osm_id'])=='190375727'))]
  for theme in (-1,0,1,2,3,4,5,6,7,8):
   # Inspect the real renderer's drawing calls while still drawing a real PNG.
   calls=[];original=b.draw_geom
   def track(ax,g,face='none',edge='none',lw=.3,z=1,*args,**kwargs):
    if g.equals(north[1]):calls.append((face,z))
    return original(ax,g,face,edge,lw,z,*args,**kwargs)
   with tempfile.TemporaryDirectory(prefix='strict-render-',dir=str(out)) as tmp:
    temp=Path(tmp);(temp/'study_boundary_6677.geojson').write_text(json.dumps(data));atlas._DATA=(raw,bounds['study_area'][1],{'area_ha':bounds['study_area'][1].area/10000,'selected_models':1},temp,bounds['study_area'][0],bounds['primary_brief'][1],[])
    b.draw_geom=track
    try:plate=atlas.render(theme)
    finally:b.draw_geom=original
    assert calls and all(face=='#dcdad3' and z==5 for face,z in calls),(theme,calls)
    assert all(not ('representative point' in p['reading_note']['en']) for p in [plate])
 if a.artifacts:
  actual=collections.defaultdict(set)
  with (out/'tables/buildings.csv').open(encoding='utf-8-sig') as f:
   for r in csv.DictReader(f):actual[r['scope']].add(r['asset_id']);assert r['boundary_crossing']=='False';assert abs(float(r['intersection_fraction'])-1)<1e-10
  assert dict(actual)=={sid:v['buildings'] for sid,v in expected.items()}
  for name,key in [('height_models','building_id'),('flood_buildings','building_id')]:
   with (out/'tables'/f'{name}.csv').open(encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):assert r[key] in expected[r['scope']]['buildings'],(name,r)
  db=root/'team/04_Data/Ready/Study_Area_2026-10-18/Kanda_Nihonbashi_Study.gpkg'
  for name in ('buildings','osm_buildings'):
   saved=source_rows(db,name);original={str(r.get('asset_id') or r.get('osm_id')):(g,blob) for r,g,blob in rows[name]}
   assert len(saved)==len(original)
   for r,g,blob in saved:
    uid=str(r.get('asset_id') or r.get('osm_id'));assert blob==original[uid][1],(name,uid,'raw source bytes changed')
    for col,sid in [('in_study_area','study_area'),('in_primary_area','primary_brief')]:assert int(r[col])==int(uid in expected[sid][name]),(name,uid,col)
  for name,sid in [('analysis_buildings_wider','study_area'),('analysis_buildings_primary','primary_brief')]:
   saved=source_rows(db,name);assert {r['asset_id'] for r,g,z in saved}==expected[sid]['buildings']
   original={r['asset_id']:g for r,g,z in rows['buildings']}
   for r,g,z in saved:assert bounds[sid][1].covers(g) and g.equals_exact(original[r['asset_id']],0),(name,r['asset_id'])
  c=sqlite3.connect(db)
  for sid in bounds:assert {r[0] for r in c.execute('select asset_id from study_membership where scope=?',(sid,))}==expected[sid]['buildings']
  assert c.execute('select count(*) from gpkg_geometry_columns').fetchone()[0]==20;c.close()
  wal=Path(str(db)+'-wal');assert not wal.exists() or wal.stat().st_size==0,'Delivery GeoPackage depends on an unshipped WAL'
  project=root/'team/05_QGIS/Projects/Kanda_Nihonbashi_Study_2026-10-18.qgz'
  with zipfile.ZipFile(project) as z:xml=ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith('.qgs'))))
  layers=xml.findall('.//projectlayers/maplayer');assert len(layers)==21,len(layers)
  for layer in layers:
   source_text=layer.findtext('datasource');assert not source_text.startswith('/'),source_text
  names=[node.get('name') for node in xml.findall('./layer-tree-group/layer-tree-layer')]
  assert names.index('analysis_buildings_wider')<names.index('Context · PLATEAU source buildings'),names
  assert 'study_membership' in names
  quality=json.loads((out/'quality_checks.json').read_text());assert quality['gis_export_status']=='passed'
  exclusions=list(csv.DictReader((out/'tables/excluded_buildings.csv').open(encoding='utf-8-sig')))
  assert any(r['source_id']==atlas.NORTHERN_ID and r['scope']=='study_area' and r['northern_reported_building']=='1' and float(r['outside_m2'])>229 for r in exclusions)
 print(json.dumps({'status':'passed','counts':{sid:{name:len(ids) for name,ids in v.items()} for sid,v in expected.items()},'source_geometry_valid':True,'northern_excluded':True,'all_theme_render_regression':not a.skip_render,'saved_gis_artifacts_checked':a.artifacts}),flush=True)
if __name__=='__main__':main()
