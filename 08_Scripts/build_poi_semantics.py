#!/usr/bin/env python3
"""Classify open POI source objects and describe their functional mix and spatial tendency."""
import json,csv,math,unicodedata,collections,hashlib
from pathlib import Path
from shapely.geometry import Point,Polygon,shape,mapping,box
from shapely.ops import transform
from pyproj import Transformer
CATEGORIES={
 'food':('Food & drink','餐饮','#c66b43'),
 'retail':('Shops & daily needs','零售与日常采购','#bc9a34'),
 'work':('Work & services','办公与服务','#6965a7'),
 'health':('Health','健康医疗','#b86485'),
 'stay':('Hotels & stays','旅宿','#8c6a50'),
 'civic':('Civic & learning','公共服务与教育','#4c8c91'),
 'culture':('Culture & leisure','文化与休闲','#638c60'),
 'transit':('Mobility services','交通与出行服务','#4c7195'),
 'other':('Other named places','其他有名场所','#858078')}
SUPPORT={'bench','waste_basket','waste_disposal','recycling','bicycle_parking','motorcycle_parking','parking','parking_entrance','charging_station','vending_machine','atm','toilets','drinking_water','post_box','telephone','clock','taxi','shelter','grit_bin','hunting_stand','loading_dock'}
def classify(t):
 a=t.get('amenity','');s=t.get('shop','');tour=t.get('tourism','')
 if a in SUPPORT or tour=='information':return None,'support'
 if a in {'restaurant','cafe','fast_food','bar','pub','biergarten','food_court','ice_cream'}:return 'food','amenity='+a
 if t.get('healthcare') or a in {'pharmacy','hospital','clinic','doctors','dentist','nursing_home','veterinary'} or s in {'chemist','medical_supply','hearing_aids'}:return 'health','healthcare='+t.get('healthcare',a or s)
 if tour in {'hotel','hostel','guest_house','motel','apartment'}:return 'stay','tourism='+tour
 if a in {'bank','bureau_de_change','insurance','coworking_space'} or t.get('office') or t.get('craft') or s in {'hairdresser','beauty','laundry','dry_cleaning','travel_agency','copyshop','tattoo'}:return 'work','office='+t.get('office',t.get('craft',a or s))
 if s and s not in {'no','vacant','closed'}:return 'retail','shop='+s
 if a in {'school','college','university','kindergarten','childcare','library','townhall','police','fire_station','post_office','community_centre','social_facility','public_building'}:return 'civic','amenity='+a
 if t.get('railway')=='station' or a in {'bus_station','ferry_terminal','bicycle_rental','car_rental','car_sharing'}:return 'transit','railway='+t.get('railway',a)
 if t.get('leisure') in {'fitness_centre','sports_centre','park','garden','amusement_arcade','dance','escape_game','mahjong','pitch','track','playground','swimming_pool'} or tour in {'museum','gallery','attraction','artwork','viewpoint'} or a in {'cinema','theatre','nightclub','place_of_worship','arts_centre','casino','events_venue','gambling','karaoke_box','internet_cafe','public_bath'}:return 'culture','leisure='+t.get('leisure',tour or a)
 if t.get('name') and a not in {'no','vacant'} and s not in {'vacant','closed'}:return 'other','other'
 return None,'unclassified'
def csvout(path,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def build(root,boundaries):
 team=root/'team';rawdir=team/'04_Data/Raw/POI_OSM_2026-10-18';out=team/'06_Outputs/Study_Area_2026-10-18';ready=team/'04_Data/Ready/POI_OSM_2026-10-18';ready.mkdir(parents=True,exist_ok=True)
 data=json.loads((rawdir/'osm_poi_raw.json').read_text());source=json.loads((rawdir/'source_manifest.json').read_text())
 to6677=Transformer.from_crs(4326,6677,always_xy=True).transform;to4326=Transformer.from_crs(6677,4326,always_xy=True).transform
 rows=[];excluded=[];by_id={}
 for e in data['elements']:
  uid=f"osm:{e['type']}:{e['id']}"
  if uid in by_id:continue
  by_id[uid]=e;t=e.get('tags',{});cat,sub=classify(t)
  if not cat:excluded.append({'source_id':uid,'reason':sub,'name':t.get('name','')});continue
  if any(k in t for k in ['disused:amenity','abandoned:amenity']) and not any(t.get(k) for k in ['amenity','shop','office','healthcare']):continue
  geom=None;method=None
  if e['type']=='node' and 'lon' in e:geom=Point(e['lon'],e['lat']);method='OSM node coordinate'
  elif e.get('geometry'):
   pts=[(p['lon'],p['lat']) for p in e['geometry'] if 'lon' in p]
   if len(pts)>3 and pts[0]==pts[-1]:
    poly=Polygon(pts)
    if poly.is_valid and poly.area>0:geom=poly;method='Representative point of source polygon'
  if geom is None and e.get('center'):geom=Point(e['center']['lon'],e['center']['lat']);method='OSM bounding-box center fallback'
  if geom is None:excluded.append({'source_id':uid,'reason':'no supported location','name':t.get('name','')});continue
  projected=transform(to6677,geom);pt=projected.representative_point()
  r={'source_id':uid,'osm_type':e['type'],'osm_id':e['id'],'name':t.get('name:en') or t.get('name') or t.get('brand') or sub,'original_name':t.get('name',''),'category':cat,'category_label':CATEGORIES[cat][0],'subtype':sub,'level':t.get('level',''),'branch':t.get('branch',''),'brand':t.get('brand',''),'operator':t.get('operator',''),'source_url':f"https://www.openstreetmap.org/{e['type']}/{e['id']}",'location_method':method,'easting':pt.x,'northing':pt.y,'in_study_area':int(boundaries['study_area'][1].covers(pt)),'in_primary_area':int(boundaries['primary_brief'][1].covers(pt)),'raw_tags':json.dumps(t,ensure_ascii=False,sort_keys=True)}
  rows.append((r,pt,projected))
 # Merge a node/area pair only when identical name, function and level agree AND
 # the precise node lies inside that same source area. Keep every source ID in audit.
 norm=lambda s:''.join(unicodedata.normalize('NFKC',s).lower().split())
 removed=set();duplicates=[];nodes=[x for x in rows if x[0]['osm_type']=='node']
 for r,pt,g in rows:
  if r['osm_type']=='node' or g.geom_type=='Point' or not r['original_name']:continue
  matches=[rr for rr,pp,gg in nodes if norm(rr['original_name'])==norm(r['original_name']) and rr['category']==r['category'] and rr['subtype']==r['subtype'] and rr['level']==r['level'] and rr['branch']==r['branch'] and g.covers(pp)]
  if len(matches)==1:
   removed.add(r['source_id']);duplicates.append({'removed_area_id':r['source_id'],'kept_node_id':matches[0]['source_id'],'reason':'Same name/function/level/branch; node contained by source area','name':r['original_name']})
 kept=[(r,pt) for r,pt,g in rows if r['source_id'] not in removed]
 csvout(ready/'poi_inventory.csv',[r for r,p in kept]);csvout(ready/'duplicate_audit.csv',duplicates or [{'removed_area_id':'','kept_node_id':'','reason':'No node/area pairs merged','name':''}]);csvout(ready/'excluded_support.csv',excluded)
 def features(transformer=None):
  return [{'type':'Feature','properties':r,'geometry':mapping(transform(transformer,p) if transformer else p)} for r,p in kept]
 (ready/'poi_6677.geojson').write_text(json.dumps({'type':'FeatureCollection','crs':{'type':'name','properties':{'name':'EPSG:6677'}},'features':features()},ensure_ascii=False,indent=2)+'\n')
 (out/'poi.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features(to4326)},ensure_ascii=False,separators=(',',':'))+'\n')
 scope_results={};category_rows=[];sector_rows=[];cells=[]
 for sid,(props,area) in boundaries.items():
  selected=[(r,p) for r,p in kept if area.covers(p)];counts=collections.Counter(r['category'] for r,p in selected);N=len(selected)
  shares={k:v/N for k,v in counts.items()};entropy=-sum(v*math.log(v) for v in shares.values())/math.log(len(CATEGORIES)) if N else 0.
  minx,miny,maxx,maxy=area.bounds;dy=(maxy-miny)/3
  sectors=[]
  for i,label in enumerate(['South / Shin-Nihonbashi side','Middle / Kajicho–Kanda side','North / Iwamotocho side']):
   band=area.intersection(box(minx-1,miny+i*dy,maxx+1,miny+(i+1)*dy));sel=[r for r,p in selected if miny+i*dy<=p.y and (p.y<miny+(i+1)*dy or i==2)];cc=collections.Counter(r['category'] for r in sel)
   sectors.append({'sector':label,'area_ha':band.area/10000,'poi_count':len(sel),'poi_per_ha':len(sel)/(band.area/10000) if band.area else None,'northing_range':[miny+i*dy,miny+(i+1)*dy],'categories':dict(cc),'mix':[{ 'category':k,'count':cc[k],'share_pct':100*cc[k]/len(sel) if sel else 0.,'location_quotient':(cc[k]/len(sel))/shares[k] if sel and shares.get(k) else None} for k in CATEGORIES]})
   for k in CATEGORIES:sector_rows.append({'scope':sid,'sector':label,'category':k,'count':cc[k],'area_ha':band.area/10000,'sector_poi_count':len(sel),'location_quotient':(cc[k]/len(sel))/shares[k] if sel and shares.get(k) else None})
  grid=collections.defaultdict(list)
  for r,p in selected:grid[(int(p.x//100),int(p.y//100))].append(r)
  for (x,y),rs in grid.items():
   cell=area.intersection(box(x*100,y*100,(x+1)*100,(y+1)*100));cc=collections.Counter(r['category'] for r in rs)
   for k,n in cc.items():
    lq=(n/len(rs))/shares[k]
    if len(rs)>=5 and n>=3 and lq>=1.5:
     cells.append({'scope':sid,'grid_easting':x*100,'grid_northing':y*100,'cell_area_ha':cell.area/10000,'total_pois':len(rs),'category':k,'category_count':n,'location_quotient':lq,'name_examples':[r['name'] for r in rs if r['category']==k][:3]})
  cats=[{'id':k,'label':{'en':CATEGORIES[k][0],'zh':CATEGORIES[k][1],'ja':CATEGORIES[k][0]},'color':CATEGORIES[k][2],'count':counts[k],'share_pct':100*counts[k]/N if N else 0.} for k in CATEGORIES]
  category_rows += [dict(scope=sid,category=x['id'],count=x['count'],share_pct=x['share_pct']) for x in cats]
  scope_results[sid]={'poi_count':N,'poi_per_ha':N/(area.area/10000),'mix_entropy_0_1':entropy,'categories':cats,'sectors':sectors,'boundary_sensitive_pois':sum(area.boundary.distance(p)<=25 for r,p in selected),'whole_source_object_ids':[r['source_id'] for r,p in selected]}
 cells.sort(key=lambda r:(r['scope'],-r['category_count'],-r['location_quotient'],r['grid_northing'],r['grid_easting']))
 result={'schema_version':1,'boundary_revision':'2026-10-18-brief-figure5','source':source,'raw_source_elements':len(data['elements']),'classified_source_objects':len(rows),'merged_node_area_pairs':len(duplicates),'excluded_support_or_unclassified':len(excluded),'kept_source_objects':len(kept),'scopes':scope_results,'local_concentrations':cells,'methods':{'membership':'OSM nodes, or representative points of closed source polygons; explicit source-center fallback for unresolved ways/relations. Full geometry and original tags retained.','duplicates':'Source type+ID is the base key. Merge node/area only with identical name, category, subtype, level and branch, and containment by the source area. No name-only station merge.','categories':'One primary function per object using explicit OSM amenity/shop/office/craft/healthcare/tourism/leisure/railway tags; the full rule is versioned in build_poi_semantics.py.','spatial_tendency':'Three equal-northing bands within each trace; per-hectare density uses clipped band area. LQ = local category share / whole-scope category share.','local_concentration':'100 m EPSG:6677 grid; report cells with >=5 POIs, >=3 of a category and LQ>=1.5. Descriptive specialization, not a significance test.','coverage':'OSM is a volunteered inventory, not a business census or floor-use survey. Support features are retained separately, excluded from destination mix. Counts represent tagged source objects after the stated merge.'}}
 (out/'poi_semantics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 for name,rs in [('poi_categories',category_rows),('poi_sectors',sector_rows),('poi_concentrations',cells)]:csvout(out/'tables'/(name+'.csv'),rs or [{'scope':'','note':'No cells meet the stated descriptive threshold'}])
 csvout(out/'tables/poi_inventory.csv',[r for r,p in kept if r['in_study_area']])
 return kept,result
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--task-root',type=Path,required=True);a=p.parse_args()
 fs=json.loads((a.task_root/'team/06_Outputs/Study_Area_2026-10-18/study_boundary_6677.geojson').read_text())['features'];bs={f['properties']['id']:(f['properties'],shape(f['geometry'])) for f in fs}
 rows,d=build(a.task_root,bs);print(json.dumps({k:v['poi_count'] for k,v in d['scopes'].items()}))

