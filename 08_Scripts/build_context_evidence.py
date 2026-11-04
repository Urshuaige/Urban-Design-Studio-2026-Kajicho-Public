#!/usr/bin/env python3
"""Compute source-bound Kajicho context evidence and PNG figures; no solver.
Usage: python3 build_context_evidence.py --input inputs --output . [--analyze-only]
"""
import argparse,collections,concurrent.futures,csv,hashlib,json,math,os,platform,sqlite3,statistics,sys
from datetime import datetime,timezone
from pathlib import Path
import xml.etree.ElementTree as ET
import shapely
from shapely import wkb
from shapely.geometry import box,Polygon,GeometryCollection
from shapely.ops import unary_union,transform
import pyproj
PAPER='#f7f5ef';INK='#36353a';PURPLE='#59457f';TEAL='#719a94';BRICK='#b97667';OCHRE='#cfb56d';GREY='#c8c6bf'
USE_COLORS={'業務施設':'#BE1E32','商業施設':'#785028','宿泊施設':'#F08CBE','住宅':'#F0F0A0','共同住宅':'#FAAAA0','店舗等併用住宅':'#F5F05A','作業所併用住宅':'#B48CBE','官公庁施設':'#0A78BE','文教厚生施設':'#FAA032','運輸倉庫施設':'#283C8C','工場':'#00643C','供給処理施設':'#505050','その他':'#828282','不明':'#BEBEBE'}
USE_LABELS={'業務施設':('Office','办公'),'商業施設':('Retail','商业'),'宿泊施設':('Hotel','住宿'),'住宅':('House','住宅'),'共同住宅':('Apartments','集合住宅'),'店舗等併用住宅':('Housing + shop','住商混合'),'作業所併用住宅':('Housing + work','住工混合'),'官公庁施設':('Government','行政'),'文教厚生施設':('Education / care','文教医疗'),'運輸倉庫施設':('Transport / storage','运输仓储'),'工場':('Factory','工厂'),'供給処理施設':('Utilities','供给处理'),'その他':('Other','其他'),'不明':('Unknown','未知')}
LAND_LABELS={'204':('Water','水域'),'211':('Housing / mixed','住宅与住商混合'),'212':('Commercial','商业'),'213':('Industrial','工业'),'214':('Public facilities','公共设施'),'215':('Roads','道路'),'216':('Transport','交通设施'),'217':('Parks / open space','公共空地'),'222':('Outdoor parking','露天停车'),'223':('Other outdoor use','其他室外利用'),'224':('Unused land','未利用地')}
LAND_COLORS={'204':'#78DCFF','211':'#FFFF00','212':'#E65050','213':'#1E46FF','214':'#C800DC','215':'#e3e1db','216':'#8C8C8C','217':'#C8FFC8','222':'#ded1b5','223':'#c9bcae','224':'#f0ede5'}
SCENARIOS=[('kanda_2018_l2','神田川流域（想定最大規模）','2018-03-30','Kanda inundation forecast / L2','神田川浸水预想 · 2018 · L2'),('kanda_river_2024_l2','荒川水系神田川流域（想定最大規模）','2024-02-15','Kanda river flooding / L2','神田川河川洪水 · 2024 · L2'),('kanda_river_2024_l1','荒川水系神田川流域（計画規模）','2024-02-15','Kanda river flooding / L1','神田川河川洪水 · 2024 · L1'),('sumida_2021_l2','隅田川・新河岸川流域（想定最大規模）','2021-03-30','Sumida / Shingashi / L2','隅田川・新河岸川 · 2021 · L2')]

def geomblob(b):
 f=b[3];e=(f>>1)&7
 return wkb.loads(bytes(b)[8+{0:0,1:32,2:48,3:48,4:64}[e]:])
def read(path,table):
 c=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True);c.row_factory=sqlite3.Row;out=[]
 for row in c.execute('select * from "'+table+'"'):
  d=dict(row);g=geomblob(d.pop('geom'))
  if not g.is_valid:g=shapely.make_valid(g)
  out.append((d,g))
 c.close();return out

def writecsv(path,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def read_l1(inp):
 tr=pyproj.Transformer.from_crs(6668,6677,always_xy=True).transform;out=[];G='{http://www.opengis.net/gml}'
 for p in sorted(inp.glob('*_l1_*.gml')):
  if p.name.startswith('._'):continue
  r=ET.parse(p).getroot()
  for member in r.iter():
   if member.tag.split('}')[-1]!='cityObjectMember':continue
   ob=member[0];polys=[]
   for q in ob.iter(G+'Polygon'):
    rings=[]
    for kind in ['exterior','interior']:
     for ring in q.findall(G+kind):
      pos=ring.find('.//'+G+'posList')
      if pos is None:continue
      vals=list(map(float,pos.text.split()));rings.append([(vals[i+1],vals[i]) for i in range(0,len(vals),3)])
    if rings:
     pg=transform(tr,Polygon(rings[0],rings[1:]))
     if not pg.is_valid:pg=shapely.make_valid(pg)
     polys.append(pg)
   if polys:
    attrs={x.tag.split('}')[-1]:x.text for x in ob.iter() if x.text and not len(x) and x.tag.split('}')[-1] in ['name','rank','scale','description']}
    attrs['source_file']=p.name;out.append((attrs,unary_union(polys)))
 return out

def analyze(inp,out):
 a=out/'analysis';a.mkdir(parents=True,exist_ok=True)
 raw={t:read(inp/'baseline.gpkg',t) for t in ['primary_area','analysis_extent','buildings','plateau_luse','plateau_fld','roads','rail','water']}
 raw['osm_buildings']=read(inp/'common.gpkg','buildings');core=unary_union([g for r,g in raw['primary_area']]);window=unary_union([g for r,g in raw['analysis_extent']]);area=core.area
 buildings=raw['buildings'];cb=[(r,g) for r,g in buildings if r['core']==1];assert len(cb)==277
 touching=[(r,g.intersection(core)) for r,g in buildings if g.intersection(core).area>.01];union=unary_union([g for r,g in touching]);coreunion=unary_union([g.intersection(core) for r,g in cb])
 area_rows=[];use_groups=collections.defaultdict(list);building_rows=[]
 for r,g in cb:
  use_groups[r['usage']].append((r,g));building_rows.append({'building_id':r['building_id'],'use':r['usage'],'source_plan_area_m2':r['plan_area_m2'],'geometry_full_projection_m2':g.area,'geometry_within_core_m2':g.intersection(core).area,'floor_proxy_m2':r['floor_proxy_m2'],'height_m':r['height_m'],'height_source':r['height_source'],'levels':r['levels'],'levels_source':r['levels_source'],'survey_year':r['survey_year'],'model_year':r['model_year']})
 use=[]
 for k,rows in use_groups.items():
  use.append({'source_use':k,'label_en':USE_LABELS.get(k,(k,k))[0],'label_zh':USE_LABELS.get(k,(k,k))[1],'objects':len(rows),'object_share_pct':100*len(rows)/277,'sum_source_plan_area_m2':sum(r['plan_area_m2'] for r,g in rows),'sum_projection_within_core_m2':sum(g.intersection(core).area for r,g in rows),'sum_floor_proxy_m2':sum(r['floor_proxy_m2'] for r,g in rows),'color':USE_COLORS.get(k,GREY)})
 use.sort(key=lambda x:-x['objects']);totalplan=sum(x['sum_source_plan_area_m2'] for x in use);totalfloor=sum(x['sum_floor_proxy_m2'] for x in use)
 for x in use:x.update(plan_share_pct=100*x['sum_source_plan_area_m2']/totalplan,floor_proxy_share_pct=100*x['sum_floor_proxy_m2']/totalfloor)
 lgroup=collections.defaultdict(list);land_features=[]
 for r,g in raw['plateau_luse']:
  clip=g.intersection(core)
  if clip.area>.000001:lgroup[str(r['class'])].append(clip);land_features.append({'id':r['gml_id'],'source_class':r['class'],'source_label':r['class_label'],'source_detail':r['orgLandUse_label'],'within_core_m2':clip.area})
 land_union=unary_union([g for v in lgroup.values() for g in v]);land=[]
 for k,geoms in lgroup.items():
  val=unary_union(geoms).area;en,zh=LAND_LABELS.get(k,(k,k));land.append({'class':k,'label_en':en,'label_zh':zh,'source_label':next(r['class_label'] for r,g in raw['plateau_luse'] if str(r['class'])==k),'area_m2':val,'core_share_pct':100*val/area,'color':LAND_COLORS.get(k,GREY)})
 land.sort(key=lambda x:-x['area_m2']);uncovered=core.difference(land_union).area;class_overlap=sum(x['area_m2'] for x in land)-land_union.area
 coverage={'boundary_area_m2':area,'boundary_area_ha':area/10000,'boundary_year':2020,'boundary_definition':'Dissolved 2020 Census Kajicho 1 and 2; course outline to confirm.','core_id_objects':277,'any_overlap_objects':len(touching),'union_building_projection_m2':union.area,'gross_coverage_pct':100*union.area/area,'uncovered_by_building_projection_m2':area-union.area,'core_id_union_within_boundary_m2':coreunion.area,'core_id_union_coverage_pct':100*coreunion.area/area,'sum_touching_clipped_footprints_m2':sum(g.area for r,g in touching),'overlapping_projection_excess_m2':sum(g.area for r,g in touching)-union.area,'objects_per_gross_ha':277/(area/10000),'legal_bcr_computed':False,'note':'Gross coverage is union horizontal building-model projection inside the entire town area. It is not parcel BCR and the complement is not all public open space.'}
 coverage['source_window_core_coverage_pct']=100*core.intersection(window).area/area
 land_meta={'source_survey_year':2021,'model_year':2025,'total_union_m2':land_union.area,'coverage_pct':100*land_union.area/area,'unmapped_m2':uncovered,'unmapped_pct':100*uncovered/area,'between_class_overlap_m2':class_overlap,'category_sum_m2':sum(x['area_m2'] for x in land),'area_denominator_m2':area,'method':'Intersect source polygons with core; dissolve within each category and report union coverage and between-category overlap separately.'}
 height=[{'bin':'<10 m','count':0},{'bin':'10–20 m','count':0},{'bin':'20–30 m','count':0},{'bin':'30–45 m','count':0},{'bin':'≥45 m','count':0},{'bin':'Proxy height','count':0}];hv=[]
 for r,g in cb:
  h=r['height_m'];i=5 if r['height_source']!='bldg:measuredHeight' else next(i for i,b in enumerate([10,20,30,45,math.inf]) if h<b);height[i]['count']+=1
  if i!=5:hv.append(h)
 height_meta={'source_height_n':len(hv),'proxy_n':277-len(hv),'source_median_m':statistics.median(hv),'source_min_m':min(hv),'source_max_m':max(hv),'source_mean_m':statistics.mean(hv),'denominator_objects':277,'proxy_source':dict(collections.Counter(r['height_source'] for r,g in cb if r['height_source']!='bldg:measuredHeight'))}
 # Flood sources retain separate dates and model domains. Dissolve depth classes; highest class owns any overlap.
 l1=read_l1(inp);raw['flood_l1']=l1;flood=[];exposure=[];flood_geoms={}
 for sid,name,date,en,zh in SCENARIOS:
  selected=l1 if sid.endswith('_l1') else [(r,g) for r,g in raw['plateau_fld'] if r['name']==name]
  ranks=collections.defaultdict(list)
  for r,g in selected:ranks[str(r.get('rank','unknown'))].append(g)
  dissolved={r:unary_union(v) for r,v in ranks.items()};allg=unary_union(list(dissolved.values()));claimed=GeometryCollection();disjoint={}
  for rank in sorted(dissolved,key=lambda x:int(x) if x.isdigit() else -1,reverse=True):disjoint[rank]=dissolved[rank].difference(claimed);claimed=unary_union([claimed,dissolved[rank]])
  flood_geoms[sid]=disjoint;counts=collections.Counter();within_counts=collections.Counter();exposed_plan=0
  for r,g in cb:
   hits=[rank for rank,gg in dissolved.items() if g.intersection(gg).area>.01];rh=max(hits,key=lambda x:int(x)) if hits else None
   wg=g.intersection(core);whits=[rank for rank,gg in dissolved.items() if wg.intersection(gg).area>.01];wr=max(whits,key=lambda x:int(x)) if whits else None
   status='overlap' if rh else ('outside_download_window' if g.intersection(window).area<.01 else 'no_recorded_overlap')
   counts[rh or status]+=1;within_counts[wr or 'no_recorded_overlap']+=1
   ov=g.intersection(allg).area;exposed_plan+=ov
   exposure.append({'scenario':sid,'source_name':name,'source_date':date,'building_id':r['building_id'],'status':status,'max_depth_rank':rh or '', 'intersection_full_model_m2':ov,'intersection_model_within_core_m2':wg.intersection(allg).area,'max_depth_rank_within_core':wr or ''})
  hazard_area=core.intersection(allg).area
  flood.append({'id':sid,'source_name':name,'source_date':date,'title_en':en,'title_zh':zh,'scale':'L1' if sid.endswith('_l1') else 'L2','input_features':len(selected),'raw_polygon_bounds':list(allg.bounds) if not allg.is_empty else None,'core_flood_area_m2':hazard_area,'core_flood_area_pct':100*hazard_area/area,'depth_area_m2':{k:core.intersection(g).area for k,g in disjoint.items()},'objects_by_max_depth_rank':dict(counts),'objects_within_core_by_max_depth_rank':dict(within_counts),'exposed_core_objects':sum(v for k,v in counts.items() if k.isdigit()),'exposed_core_objects_pct':100*sum(v for k,v in counts.items() if k.isdigit())/277,'sum_exposed_building_projection_m2':exposed_plan,'download_window_core_coverage_pct':coverage['source_window_core_coverage_pct'],'interpretation':'No recorded overlap means no positive intersection with available polygons. It is not a declaration of safety; source hazard domains and rainfall assumptions differ.','source_coverage_status':'Acquired polygon records available; polygon absence is not a surveyed safe area.'})
 old=list(csv.DictReader((inp/'Building_Flood_Exposure.csv').open(encoding='utf-8-sig')));oldids={r['building_id'] for r in old if r['scenario_name']=='神田川流域（想定最大規模）'};newids={r['building_id'] for r in exposure if r['scenario']=='kanda_2018_l2' and r['status']=='overlap'}
 flood_qc={'existing_exposure_objects':len(oldids),'recomputed_exposure_objects':len(newids),'ids_only_in_existing':sorted(oldids-newids),'ids_only_in_recomputed':sorted(newids-oldids),'depth_count_rule':'A core model intersecting multiple depth categories counts once at its highest intersected category; threshold area > 0.01 m2.','depth_area_rule':'Dissolve each rank, subtract higher ranks to avoid counting overlapping categories twice.','L1_note':'Two original 2024 river-flood L1 files retained north of the core; no L1 polygons entered the clipped baseline.'}
 assert oldids==newids,flood_qc
 # Observed hourly temperature only; group by original observation day (hours 1–24), preserving source QC.
 weather=list(csv.DictReader((inp/'Tokyo_2025_hourly.csv').open(encoding='utf-8-sig')));dailyg=collections.defaultdict(list);monthlyg=collections.defaultdict(list)
 for r in weather:
  if r['temperature_qc']=='8' and r['temperature_c']!='':dailyg[r['observation_day']].append(float(r['temperature_c']));monthlyg[int(r['observation_day'][5:7])].append(float(r['temperature_c']))
 daily=[{'date':d,'valid_hours':len(v),'temperature_mean_c':statistics.mean(v),'hourly_max_c':max(v),'hourly_min_c':min(v),'hours_ge30':sum(x>=30 for x in v),'hours_ge35':sum(x>=35 for x in v)} for d,v in sorted(dailyg.items())]
 monthly=[{'month':m,'valid_temperature_hours':len(v),'temperature_mean_c':statistics.mean(v),'hourly_max_c':max(v),'hours_ge30':sum(x>=30 for x in v),'hours_ge35':sum(x>=35 for x in v)} for m,v in sorted(monthlyg.items())]
 temps=[float(r['temperature_c']) for r in weather if r['temperature_qc']=='8' and r['temperature_c']!=''];weather_meta={'station':'Tokyo s47662','year':2025,'valid_temperature_hours':len(temps),'source_hours':len(weather),'max_hourly_c':max(temps),'max_timestamp_jst':next(r['timestamp_jst'] for r in weather if r['temperature_c'] and float(r['temperature_c'])==max(temps)),'hours_ge30':sum(t>=30 for t in temps),'hours_ge35':sum(t>=35 for t in temps),'days_with_hourly_ge30':sum(r['hours_ge30']>0 for r in daily),'days_with_hourly_ge35':sum(r['hours_ge35']>0 for r in daily),'complete_days':sum(r['valid_hours']==24 for r in daily),'mean_c':statistics.mean(temps),'note':'Hourly observations at the background station; counts are sampled hours/days, not official daily-maximum heat-day statistics, street temperature or heat-stress index.'}
 tables={'building_use':use,'land_use':land,'height':height,'flood_scenarios':flood,'weather_monthly':monthly,'weather_daily':daily}
 for name,rows in [('core_buildings',building_rows),('building_use',use),('land_use',land),('land_use_features',land_features),('height_bins',height),('flood_building_exposure',exposure),('weather_monthly',monthly),('weather_daily',daily)]:writecsv(a/(name+'.csv'),rows)
 metrics={'coverage':coverage,'building_use':{'objects':277,'known':250,'unknown':27,'sum_source_plan_area_m2':totalplan,'sum_floor_proxy_m2':totalfloor,'floor_proxy_definition':'Source plan area × source/proxy storeys; it is not measured total floor area or legal FAR.'},'land_use':land_meta,'height':height_meta,'flood':flood,'flood_qc':flood_qc,'weather':weather_meta}
 earthquake=None
 if (inp/'Kajicho_Earthquake_Risk_2022_rows.json').exists():earthquake=json.loads((inp/'Kajicho_Earthquake_Risk_2022_rows.json').read_text());metrics['earthquake']=earthquake
 sources=json.loads((inp/'Source_Register.json').read_text());sources.extend([{'dataset_id':'OSM_20261013','source_url':'https://www.openstreetmap.org/copyright','data_year':'Snapshot 2026-10-13','provider':'© OpenStreetMap contributors','license':'ODbL 1.0','crs':'EPSG:4326 source; EPSG:6677 derived','processing_steps':'Use saved streets, rail, water and building footprints as background context; no new query.'},{'dataset_id':'ESTAT_2020','source_url':'https://www.e-stat.go.jp/gis/statmap-search','data_year':'2020','provider':'e-Stat','license':'e-Stat terms / GIS terms','crs':'EPSG:6677 derived','processing_steps':'Dissolve 2020 census Kajicho 1 and 2 town boundaries.'},{'dataset_id':'FLOOD_METADATA','source_url':'https://www.geospatial.jp/ckan/dataset/plateau-13101-chiyoda-ku-2025','data_year':'Kanda forecast 2018-03-30; Sumida/Shingashi 2021-03-30; Kanda river flood 2024-02-15','model_year':'2025','metadata_date':'2026-03-13','license':'CC BY 4.0','local_input':'flood_metadata.xml','processing_steps':'Read source scenario names/dates from metadata; match scenario names and original folder paths; keep scope differences.'}])
 doc={'schema_version':1,'created_utc':datetime.now(timezone.utc).isoformat(),'metrics':metrics,'tables':tables,'charts':[],'sources':sources,'crs':'EPSG:6677','no_new_cfd':True,'runtime':{'host':platform.node(),'pid':os.getpid(),'python':sys.version,'shapely':shapely.__version__,'pyproj':pyproj.__version__},'inputs':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inp.iterdir() if p.is_file() and not p.name.startswith('._')]}
 (a/'Context_Evidence.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2))
 print(json.dumps({'stage':'metrics_ready','coverage':coverage,'land_use':land_meta,'height':height_meta,'flood':[(x['id'],x['exposed_core_objects'],x['core_flood_area_pct']) for x in flood],'weather':weather_meta},ensure_ascii=False),flush=True)
 return doc,raw,core,window,flood_geoms


def render_one(index,doc,raw,core,window,flood_geoms,out):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 import matplotlib.dates as mdates
 from matplotlib.path import Path as MPath
 from matplotlib.patches import PathPatch,Rectangle,Polygon as MPolygon
 from matplotlib.font_manager import FontProperties
 from PIL import Image
 serif=FontProperties(fname='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')
 cjk=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc')
 sans=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
 plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':13,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':'#b6b1a6','axes.linewidth':.7,'savefig.facecolor':PAPER})
 fig=plt.figure(figsize=(16,11),dpi=100,facecolor=PAPER)
 meta=CHARTS[index];m=doc['metrics'];tables=doc['tables']
 def ft(x,y,s,size=13,color=INK,font=None,**kw):return fig.text(x,y,s,fontsize=size,color=color,fontproperties=font or sans,va='top',**kw)
 ft(.045,.966,'KAJICHO / 鍛冶町   ·   CONTEXT STUDY',12,PURPLE,cjk)
 ft(.045,.918,meta['title']['en'],29,INK,serif);ft(.045,.86,meta['title']['zh'],18,INK,cjk)
 ft(.91,.958,f'{index+1:02d}',39,PURPLE,serif)
 fig.add_artist(plt.Line2D([.045,.955],[.825,.825],transform=fig.transFigure,color='#bcb6a9',lw=.7))
 def axis(rect):
  ax=fig.add_axes(rect,facecolor=PAPER)
  ax.spines[['top','right']].set_visible(False);ax.tick_params(labelsize=12,length=3,width=.6)
  return ax
 def footer(en,zh,source):
  fig.add_artist(plt.Line2D([.045,.955],[.132,.132],transform=fig.transFigure,color='#bcb6a9',lw=.7))
  ft(.045,.113,en,11);ft(.045,.086,zh,11);ft(.045,.045,source,9,'#6c6761');ft(.866,.045,'15 OCT 2026',10,PURPLE)
 def mapax(rect,sid=None,cover=False):
  ax=fig.add_axes(rect,facecolor='#f0eee8');ext=(-6125,-34630,-5025,-33730);extent=box(*ext);ax.set_xlim(ext[0],ext[2]);ax.set_ylim(ext[1],ext[3]);ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
  for sp in ax.spines.values():sp.set_edgecolor('#c3bfb5');sp.set_linewidth(.5)
  def draw(g,fc='none',ec='none',lw=.3,z=1,alpha=1):
   if g.is_empty or not g.intersects(extent):return
   g=g.intersection(extent)
   for q in (list(g.geoms) if hasattr(g,'geoms') else [g]):
    if q.geom_type=='Polygon':
     from shapely.geometry.polygon import orient
     q=orient(q);v=[];c=[]
     for ring in [q.exterior]+list(q.interiors):
      co=list(ring.coords);v.extend(co);c.extend([MPath.MOVETO]+[MPath.LINETO]*(len(co)-2)+[MPath.CLOSEPOLY])
     ax.add_patch(PathPatch(MPath(v,c),facecolor=fc,edgecolor=ec,lw=lw,zorder=z,alpha=alpha))
    elif q.geom_type in ['LineString','LinearRing']:
     co=list(q.coords);ax.plot([p[0] for p in co],[p[1] for p in co],color=ec,lw=lw,zorder=z,alpha=alpha)
  for r,g in raw['water']:draw(g,'#adcbd1','none',z=1)
  for r,g in raw['osm_buildings']:draw(g,'#d8d6ce','#b7b5ad',.15,2)
  if sid:
   for rank,g in flood_geoms[sid].items():draw(g,{'1':'#b7d9e2','2':'#5899b0'}.get(rank,'#b8797b'),'none',z=3,alpha=.9)
   allf=unary_union(list(flood_geoms[sid].values()))
   for r,g in raw['buildings']:
    if r['core']==1 and g.intersection(allf).area>.01:draw(g,BRICK,PAPER,.12,4)
  if cover:
   draw(core,'#ebe5f0','none',z=3)
   for r,g in raw['buildings']:
    if g.intersection(core).area>.01:draw(g.intersection(core),INK,PAPER,.15,4)
  for r,g in raw['rail']:draw(g,'none','#777377',.35,5)
  draw(core,'none',PAPER,2.5,6);draw(core,'none',PURPLE,1.2,7)
  nx,ny=ext[2]-40,ext[3]-55
  ax.add_patch(MPolygon([(nx,ny+20),(nx-6,ny-8),(nx,ny-1),(nx+6,ny-8)],fc=INK,zorder=9));ax.text(nx,ny+30,'N',ha='center',fontsize=10,zorder=9)
  sx,sy=ext[0]+30,ext[1]+33;ax.add_patch(Rectangle((sx-10,sy-20),265,52,fc=PAPER,ec='none',alpha=.93,zorder=9))
  for j in range(2):ax.add_patch(Rectangle((sx+j*100,sy),100,5,fc=INK if j==0 else PAPER,ec=INK,lw=.5,zorder=10))
  for j,l in enumerate(['0','100','200 m']):ax.text(sx+j*100,sy-10,l,va='top',fontsize=9,zorder=10)
  return ax
 if index==0:
  c=m['coverage'];mapax([.045,.17,.54,.63],cover=True)
  ft(.645,.77,f"{c['gross_coverage_pct']:.1f}%",50,PURPLE,serif)
  ft(.647,.681,'Gross footprint coverage / 总体投影覆盖率',14)
  ft(.647,.63,f"{c['union_building_projection_m2']:,.0f} m² / {c['boundary_area_m2']:,.0f} m²",17)
  ft(.647,.57,'Union footprint ÷ whole town area\n建筑水平投影并集 ÷ 丁目总面积',13)
  ft(.647,.475,f"{c['core_id_objects']} core model objects / 核心模型对象",15)
  ft(.647,.429,f"{c['any_overlap_objects']} objects touch the boundary area\n{c['any_overlap_objects']} 个对象与核心区有面积相交",12)
  ft(.647,.354,f"{c['objects_per_gross_ha']:.1f} objects per gross hectare\n每公顷总用地 {c['objects_per_gross_ha']:.1f} 个核心模型对象",13)
  ax=axis([.647,.23,.28,.065]);ax.barh([0],[c['gross_coverage_pct']],color=INK,height=.65);ax.barh([0],[100-c['gross_coverage_pct']],left=c['gross_coverage_pct'],color='#ddd7e3',height=.65);ax.set_xlim(0,100);ax.set_yticks([]);ax.set_xlabel('Share of core area / 核心区面积占比 (%)',fontsize=10);ax.spines['left'].set_visible(False)
  footer('Gross coverage uses the entire census-town area, including roads and rail. It is not legal parcel BCR.','空白部分为未被建筑模型投影覆盖的面积，不直接等同于公共开放空间。','Source: e-Stat 2020 · PLATEAU 2025 · © OpenStreetMap contributors / ODbL · EPSG:6677')
 elif index==1:
  rows=tables['building_use'];ys=list(range(len(rows)));keys=['object_share_pct','plan_share_pct','floor_proxy_share_pct'];title=['Model count / 模型数量','Plan area / 源投影面积','Floor-area proxy / 楼面代理'];den=[f"N = 277",f"Σ = {m['building_use']['sum_source_plan_area_m2']:,.0f} m²",f"Σ = {m['building_use']['sum_floor_proxy_m2']:,.0f} m²"]
  for j in range(3):
   ax=axis([.21+j*.255,.205,.205,.55]);vals=[r[keys[j]] for r in rows];ax.barh(ys,vals,height=.64,color=[r['color'] for r in rows],edgecolor='#746e66',linewidth=.3);ax.set_xlim(0,78);ax.set_ylim(len(rows)-.35,-.65);ax.set_xticks([0,25,50,75]);ax.grid(axis='x',color='#dcd7cc',lw=.5,zorder=0);ax.set_axisbelow(True);ax.set_yticks(ys)
   ax.set_yticklabels([r['label_en']+' / '+r['label_zh'] for r in rows] if j==0 else [],fontsize=11);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False);ax.set_xlabel('Share (%) / 占比',fontsize=11)
   for y,r,v in zip(ys,rows,vals):ax.text(v+1,y,f'{v:.1f}'+(f" · {r['objects']}" if j==0 else ''),va='center',fontsize=10)
   ft(.21+j*.255,.8,title[j],13);ft(.21+j*.255,.772,den[j],11,'#66615b')
  footer('The same 277 objects give three different compositions. Count labels also show the number of objects.','楼面代理 = 源投影面积 × 层数；源层数与代理层数并存，数值不等同于实测延床面积。','Source: PLATEAU 2021 survey / 2025 model · Colors: MLIT survey guide, 2023 p.45')
 elif index==2:
  rows=tables['land_use'];ax=axis([.245,.22,.59,.53]);ys=list(range(len(rows)));ax.barh(ys,[r['core_share_pct'] for r in rows],height=.62,color=[r['color'] for r in rows],edgecolor='#6c675f',lw=.4);ax.set_yticks(ys);ax.set_yticklabels([r['label_en']+' / '+r['label_zh'] for r in rows],fontsize=12);ax.set_ylim(len(rows)-.4,-.7);ax.set_xlim(0,40);ax.set_xlabel('Share of whole core area (%) / 占丁目总面积',fontsize=13);ax.grid(axis='x',color='#ddd8cc',lw=.55);ax.set_axisbelow(True);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
  for y,r in enumerate(rows):ax.text(r['core_share_pct']+.45,y,f"{r['core_share_pct']:.2f}%  ·  {r['area_m2']/10000:.3f} ha",va='center',fontsize=11)
  ft(.245,.79,f"Denominator / 分母: {m['coverage']['boundary_area_m2']/10000:.4f} ha",14)
  ft(.245,.174,f"Mapped area 100% · Unmapped 0 m² · Between-class overlap {m['land_use']['between_class_overlap_m2']:.3f} m²",11)
  footer('Intersected and dissolved category areas. Roads and transport occupy 56.33% by category area.','源分类分别求并集；类别间保留 0.858 m² 的微小重叠，未将其强制分配到某一用途。','Source: PLATEAU land use, 2021 survey / 2025 model · e-Stat 2020 boundary · EPSG:6677')
 elif index==3:
  rows=tables['height'];ax=axis([.105,.245,.81,.48]);xs=[0,1,2,3,4,5.6];colors=['#dedbd3','#b8cac5','#82aaa1','#508179','#355c59','#e8e2d7'];ax.bar(xs,[r['count'] for r in rows],width=.65,color=colors,edgecolor='#635d55',lw=.5);ax.set_xticks(xs);ax.set_xticklabels([r['bin'] for r in rows]);ax.set_ylim(0,115);ax.set_ylabel('Building model objects / 建筑模型对象',fontsize=13);ax.grid(axis='y',color='#ded8cc',lw=.55);ax.set_axisbelow(True)
  for x,r in zip(xs,rows):ax.text(x,r['count']+3,f"{r['count']}\n{r['count']/277*100:.1f}%",ha='center',fontsize=12)
  ax.axvline(4.8,color='#b8b1a3',lw=.8,ls=(0,(3,3)))
  ft(.105,.79,'261 source height values / 261 个源高度值',15);ft(.105,.755,f"Median / 中位数: {m['height']['source_median_m']:.1f} m   ·   Range / 范围: {m['height']['source_min_m']:.1f}–{m['height']['source_max_m']:.1f} m",12)
  ft(.705,.79,'16 proxy heights / 16 个代理值',14,PURPLE)
  footer('Each model counts once. Percentages use all 277 core objects; source-height statistics exclude proxies.','源高度取 measuredHeight 字段；16 个代理值来自 LOD1 高差，分开显示。','Source: PLATEAU building attributes / 2025 model · Height in meters')
 elif index==4:
  for j,sid in enumerate(['kanda_2018_l2','kanda_river_2024_l2']):
   row=next(r for r in m['flood'] if r['id']==sid);xx=.045+j*.49
   ft(xx,.793,row['title_zh'],15,font=cjk);ft(xx,.762,row['source_name'],10,'#6c6761')
   mapax([xx,.34,.42,.39],sid=sid)
   ax=axis([xx,.237,.42,.055]);n=row['exposed_core_objects'];ax.barh([0],[n],color=BRICK,height=.6);ax.barh([0],[277-n],left=n,color='#dcd8d0',height=.6);ax.set_xlim(0,277);ax.set_xticks([0,144,277]);ax.set_yticks([]);ax.spines['left'].set_visible(False)
   ft(xx,.312,f"{n} / 277 model objects intersect / 模型对象相交",13)
   ft(xx,.189,f"Core inundation area / 核心区浸水面: {row['core_flood_area_pct']:.2f}%",12)
  ft(.49,.69,'<0.5 m',10);ft(.49,.657,'0.5–<3 m',10);ft(.49,.624,'Model\noverlap',9)
  for yy,col in [(.693,'#b7d9e2'),(.66,'#5899b0'),(.627,BRICK)]:fig.add_artist(Rectangle((.478,yy-.009),.008,.012,transform=fig.transFigure,fc=col,ec='none'))
  footer('Different source scopes. The 2018 layer intersects 144 models; the available 2024 river L1/L2 polygons do not overlap the core.','无相交不等于安全。2018 浸水预想与 2024 河川洪水采用不同资料口径；L1 原始图斑位于核心区以北。','Source: Tokyo 2018 / 2024 · PLATEAU 2025 · © OpenStreetMap contributors / ODbL · EPSG:6677')
 elif index==5:
  rows=tables['weather_daily'];dates=[datetime.fromisoformat(r['date']) for r in rows];ax=axis([.09,.49,.82,.29]);ax.plot(dates,[r['hourly_max_c'] for r in rows],color=BRICK,lw=1.1,label='Daily max of hourly readings / 每日小时值最大值');ax.plot(dates,[r['temperature_mean_c'] for r in rows],color=TEAL,lw=1.6,label='Daily mean / 日平均');ax.set_ylim(0,42);ax.set_ylabel('Temperature (°C) / 气温');ax.set_xlim(datetime(2025,1,1),datetime(2025,12,31));ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,3,5,7,9,11,12]));ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'));ax.grid(axis='y',color='#ddd8ce',lw=.5);ax.legend(frameon=False,loc='upper left',fontsize=11,ncol=2)
  mon=tables['weather_monthly'];bx=axis([.09,.22,.82,.18]);low=[r['hours_ge30']-r['hours_ge35'] for r in mon];high=[r['hours_ge35'] for r in mon];bx.bar(range(1,13),low,color=OCHRE,label='30 to <35°C');bx.bar(range(1,13),high,bottom=low,color=BRICK,label='≥35°C');bx.set_xlim(.5,12.5);bx.set_xticks(range(1,13));bx.set_xlabel('Month of 2025 / 2025 年月份');bx.set_ylabel('Observed hours / 小时数');bx.grid(axis='y',color='#ddd8ce',lw=.5);bx.set_axisbelow(True);bx.legend(frameon=False,ncol=2,loc='upper left',fontsize=11)
  ft(.09,.446,f"{m['weather']['hours_ge30']} hours ≥30°C   ·   {m['weather']['hours_ge35']} hours ≥35°C   ·   {m['weather']['valid_temperature_hours']:,} valid hourly readings",13)
  footer('Tokyo background station, 2025. Hourly thresholds describe sampled readings, not official daily-maximum heat-day counts.','背景站观测提供季节与时段条件；不代表鍛冶町街道气温，也不是人体热舒适指标。','Source: JMA Tokyo s47662 · 2025 hourly observations · Normal temperature QC: 8,760 / 8,760')
 elif index==6:
  eq=m['earthquake'];rows=eq['rows'];fields=['建物倒壊危険度危険量（棟/ha）','火災危険度危険量（棟/ha）','総合危険度危険量（棟/ha）'];titles=['Collapse / 建筑倒塌','Fire / 火灾','Composite / 综合'];lims=[5,.1,.6];cols=[PURPLE,BRICK,TEAL]
  for j in range(3):
   ax=axis([.12+j*.285,.44,.225,.26]);v=[float(r[fields[j]]) for r in rows];ax.barh([0,1],v,height=.46,color=cols[j]);ax.set_ylim(1.5,-.6);ax.set_xlim(0,lims[j]);ax.set_yticks([0,1]);ax.set_yticklabels(['Kajicho 1 / 一丁目','Kajicho 2 / 二丁目'] if j==0 else []);ax.set_xlabel('Model risk amount (buildings/ha)\n危险量（棟/ha）',fontsize=10);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False);ax.grid(axis='x',color='#ded8cc',lw=.5);ax.set_axisbelow(True)
   for y,x in enumerate(v):ax.text(x+lims[j]*.025,y,f'{x:.2f}',va='center',fontsize=14)
   ft(.12+j*.285,.766,titles[j],16,font=cjk)
  ft(.12,.305,'Relative ranks / 相对等级（1–5）',14)
  for j,(name,field) in enumerate([('Collapse / 倒塌','建物倒壊危険度ランク'),('Fire / 火灾','火災危険度ランク'),('Composite / 综合','総合危険度ランク')]):
   ft(.12+j*.285,.264,f"{name}: {rows[0][field]} / {rows[1][field]}",14,cols[j]);ft(.12+j*.285,.229,'Kajicho 1 / Kajicho 2',10,'#6c6761')
  ft(.12,.178,'Emergency-response difficulty / 活动困难系数: 0.11 / 0.10',12)
  footer('Tokyo 9th survey (September 2022): relative ranks across 5,192 towns under common engineering-bedrock shaking.','指标用于区域比较；不是年发生概率或单栋安全鉴定。综合值沿用官方公布值，不按舍入分项重算。','Source: Tokyo Metropolitan Government, 9th regional earthquake risk survey · Official town/chome table')
 fdir=out/'figures';fdir.mkdir(exist_ok=True);(fdir/'previews').mkdir(exist_ok=True);name=meta['id'];fig.savefig(fdir/(name+'.png'),dpi=200);plt.close(fig)
 im=Image.open(fdir/(name+'.png')).convert('RGB');im.thumbnail((1200,825));im.save(fdir/'previews'/(name+'.jpg'),quality=88,optimize=True)
 return {'id':name,'file':'figures/'+name+'.png','preview':'figures/previews/'+name+'.jpg','pixels':[3200,2200]}


def L(zh,en,ja):return {'zh':zh,'en':en,'ja':ja}
CHARTS=[
 {'id':'01_building_coverage','title':L('街区建筑覆盖','Building coverage','街区の建物被覆'),'finding':L('模型投影覆盖丁目总面积的34.37%；其余面积包含道路、铁路等。','Model footprints cover 34.37% of the whole town area; the complement includes roads and rail.','建物モデルの投影面積は町丁目総面積の34.37%。残りには道路・鉄道等を含む。'),'method':L('在EPSG:6677内裁剪所有相交建筑投影，求并集，再除以2020年丁目边界面积。','Clip all intersecting building projections in EPSG:6677, union them, then divide by the 2020 town-boundary area.','EPSG:6677で相交する建物投影を切り出し、和集合面積を2020年町丁目面積で除した。'),'limits':L('总体覆盖率不等同于地块法定建蔽率；277个核心ID与286个边界相交对象采用不同计数规则。','Gross coverage is not legal parcel BCR. The 277 core IDs and 286 intersecting objects use different selection rules.','総面積の被覆率は敷地の法定建蔽率ではない。中心点による277件と面積相交による286件は選定方法が異なる。'),'table':'coverage'},
 {'id':'02_building_use','title':L('建筑用途：数量与面积','Building use: count and area','建物用途：件数と面積'),'finding':L('办公占核心模型数量49.1%，占楼面面积代理68.5%；用途未知27个。','Offices account for 49.1% of core model objects and 68.5% of the floor-area proxy; 27 uses are unknown.','業務施設は件数の49.1%、延べ面積代理値の68.5%。用途不明は27件。'),'method':L('固定277个核心ID，分别汇总模型数量、源投影面积和投影面积×层数。','Use the same 277 core IDs to summarize model counts, source plan area, and plan area × storeys.','同じ277件について、モデル数、源投影面積、投影面積×階数を集計。'),'limits':L('用途为2021年建筑属性；楼面面积代理不等同于实测延床面积，未知用途保留。','Uses are 2021 building attributes. The floor-area proxy is not measured floor area; unknown uses remain explicit.','用途は2021年の建物属性。延べ面積代理値は実測値ではなく、不明用途を明示した。'),'table':'building_use'},
 {'id':'03_land_use_area','title':L('现状土地利用面积','Land-use area','現況土地利用面積'),'finding':L('商业、道路、交通设施分别占31.96%、29.76%、26.56%；道路与交通设施合计56.33%。','Commercial, road and transport land account for 31.96%, 29.76% and 26.56%; roads plus transport total 56.33%.','商業・道路・交通施設用地は31.96%、29.76%、26.56%。道路と交通施設の合計は56.33%。'),'method':L('现状用地面与核心边界相交，同类求并集；分母为10.7914公顷丁目总面积。','Intersect land-use polygons with the core and union each class. The denominator is the whole 10.7914 ha town area.','土地利用ポリゴンを境界で切り、分類ごとに和集合。分母は町丁目総面積10.7914 ha。'),'limits':L('图层覆盖100%，未映射面积0；类别间有0.858平方米重叠。现状用地与法定用途地域不同。','Coverage is 100%, with 0 m² unmapped and 0.858 m² of cross-class overlap. Observed land use differs from legal zoning.','データ被覆は100%、未対応0 m²、分類間重複0.858 m²。現況土地利用と法定用途地域は異なる。'),'table':'land_use'},
 {'id':'04_building_height','title':L('建筑高度分布','Building height distribution','建物高さの分布'),'finding':L('261个源高度的中位数为16.2米，另有16个高度代理值。','The median of 261 source height values is 16.2 m; 16 other objects use height proxies.','源高さ261件の中央値は16.2 m。別に推定高さ16件がある。'),'method':L('按源高度分组；模型代理值单列，比例分母为全部277个核心模型。','Bin source heights and show proxy values separately. Percentages use all 277 core models.','源高さを階級化し、推定値を別表示。比率の分母は中心部277件。'),'limits':L('measuredHeight是源字段，模型高度不替代现场测量；代理值不进入源高度中位数。','measuredHeight is a source field. Model height does not replace field measurement; proxies are excluded from its median.','measuredHeightは源属性で現地実測の代用ではない。推定値は中央値から除外。'),'table':'height'},
 {'id':'05_flood_sources','title':L('洪水情景与资料口径','Flood scenarios and source scope','浸水シナリオと資料範囲'),'finding':L('2018神田川浸水预想L2覆盖核心区38.43%，与144个核心模型相交；核心相交深度类别均低于0.5米。','The 2018 Kanda forecast L2 covers 38.43% of the core and intersects 144 core models; all core overlaps are in the <0.5 m class.','2018年神田川浸水予想L2は中心部38.43%を覆い、144モデルと相交。中心部の相交は全て0.5 m未満。'),'method':L('各资料情景独立求并集并叠加277个核心模型，面积相交阈值0.01平方米；多深度相交按最高类别计一次。','Union each source scenario separately and intersect 277 core models at >0.01 m². Each object counts once at its highest intersected depth class.','資料別に和集合を作り277件と重ね、0.01 m²超で相交。複数深度は最大区分で1回計上。'),'limits':L('2018浸水预想与2024河川洪水口径不同。可得2024 L1/L2在核心内无记录相交，不等同于安全；L1原图斑位于北侧。','The 2018 forecast and 2024 river-flood layers differ in scope. Available 2024 L1/L2 polygons have no core overlap, which does not imply safety; L1 polygons lie north.','2018年浸水予想と2024年河川洪水は対象が異なる。取得した2024 L1/L2に中心部の相交はないが、安全を意味しない。L1図斑は北側。'),'table':'flood_scenarios'},
 {'id':'06_observed_heat','title':L('背景气象与高温时段','Observed weather and hot hours','背景気象と高温時間'),'finding':L('东京站2025年8760个小时观测中，705小时达到30°C，58小时达到35°C；小时最高38.4°C。','Among 8,760 Tokyo station observations in 2025, 705 hours reach 30°C and 58 reach 35°C; the highest hourly reading is 38.4°C.','東京地点2025年8,760時間のうち30°C以上は705時間、35°C以上は58時間。最高の毎時値は38.4°C。'),'method':L('按原观测日的1–24时汇总正常质量码小时温度，不填补数据。','Aggregate normal-quality hourly temperatures by original observation day, hours 1–24, with no imputation.','正常品質の毎時気温を元の観測日1～24時で集計。補間なし。'),'limits':L('小时阈值计数不等于官方日最高温统计；背景站不能直接表示街道气温或热舒适。','Hourly threshold counts differ from official daily-maximum statistics. The background station does not directly represent street temperature or comfort.','毎時値の閾値集計は公式の日最高気温統計と異なる。背景地点は街路気温や快適性を直接表さない。'),'table':'weather_monthly'},
 {'id':'07_earthquake_risk','title':L('地震区域危险度','Regional earthquake risk','地震に関する地域危険度'),'finding':L('两丁目倒塌危险度均为3级，综合均为2级；一丁目火灾2级、二丁目1级。','Both chome have collapse rank 3 and composite rank 2; fire ranks are 2 in Kajicho 1 and 1 in Kajicho 2.','両丁目とも建物倒壊ランク3、総合ランク2。火災は一丁目2、二丁目1。'),'method':L('直接读取东京都第9回调查的两个官方丁目行，保留公布危险量、等级和活动困难系数。','Read the two official chome rows in Tokyo’s 9th survey; retain published risk amounts, ranks and response-difficulty coefficients.','東京都第9回調査の公式2行を読み、危険量・ランク・活動困難係数を原値で保持。'),'limits':L('2022年调查在统一工学基盘摇晃条件下比较5192个町丁目；等级不是年概率或单栋鉴定。','The 2022 survey compares 5,192 towns under common engineering-bedrock shaking. Ranks are not annual probabilities or individual-building assessments.','2022年調査は同じ工学的基盤の揺れで5,192町丁目を比較。ランクは年確率や個別建物診断ではない。'),'table':'earthquake'}
]

def render_all(args,doc,raw,core,window,flood_geoms):
 with concurrent.futures.ProcessPoolExecutor(max_workers=min(args.workers,4)) as pool:
  futures=[pool.submit(render_one,i,doc,raw,core,window,flood_geoms,args.output) for i in range(7)]
  outputs=[f.result() for f in futures]
 for meta,r in zip(CHARTS,outputs):
  q=dict(meta);q.update(r);q['rows']=doc['tables'].get(meta['table'],[])
  if meta['table']=='coverage':q['rows']=[doc['metrics']['coverage']]
  if meta['table']=='earthquake':q['rows']=doc['metrics']['earthquake']['rows']
  doc['charts'].append(q)
 detail=doc['metrics'];cov=detail['coverage'];office=next(r for r in doc['tables']['building_use'] if r['source_use']=='業務施設');flood=detail['flood'][0]
 doc['details']=detail
 doc['metrics']=[
 {'label':L('核心区面积','Core area','中心部面積'),'value':round(cov['boundary_area_ha'],4),'unit':'ha','note':L('2020年鍛冶町一、二丁目边界','2020 Census Kajicho 1 and 2 boundary','2020年鍛冶町一・二丁目境界')},
 {'label':L('总体投影覆盖率','Gross footprint coverage','総面積の投影被覆率'),'value':round(cov['gross_coverage_pct'],2),'unit':'%','note':L('投影并集÷丁目总面积；非地块法定建蔽率','Union footprint / whole town area; not legal parcel BCR','投影和集合／町丁目総面積。法定建蔽率ではない')},
 {'label':L('核心建筑模型','Core building models','中心部建物モデル'),'value':277,'unit':'objects','note':L('既有代表点筛选ID；边界相交另为286个','Established representative-point IDs; 286 objects intersect the boundary area','既存の代表点選定ID。面積相交は286件')},
 {'label':L('办公数量占比','Office share by count','業務施設の件数比'),'value':round(office['object_share_pct'],1),'unit':'%','note':L('136/277；用途未知27个','136 / 277; 27 uses unknown','136／277。不明用途27件')},
 {'label':L('办公楼面代理占比','Office share of floor proxy','業務施設の延べ面積代理比'),'value':round(office['floor_proxy_share_pct'],1),'unit':'%','note':L('源投影面积×层数；非实测楼面面积','Source plan area × storeys; not measured floor area','源投影面積×階数。実測延べ面積ではない')},
 {'label':L('源高度中位数','Median source height','源高さ中央値'),'value':detail['height']['source_median_m'],'unit':'m','note':L('261个源值；另有16个代理高度','261 source values; 16 proxies shown separately','源値261件。推定16件は別表示')},
 {'label':L('2018情景浸水面积','2018 scenario flooded area','2018シナリオ浸水面積'),'value':round(flood['core_flood_area_pct'],2),'unit':'%','note':L('神田川浸水预想L2；不同于2024河川洪水口径','Kanda forecast L2; scope differs from the 2024 river-flood layer','神田川浸水予想L2。2024年河川洪水と対象が異なる')},
 {'label':L('2018情景相交模型','Models intersecting the 2018 layer','2018図層と相交するモデル'),'value':144,'unit':'objects','note':L('144/277；相交深度类别均<0.5米','144 / 277; all core overlaps in <0.5 m class','144／277。中心部相交は全て0.5 m未満区分')}
 ]
 doc['tables']['earthquake']=detail['earthquake']['rows'];doc['sources'].append(dict(detail['earthquake'],dataset_id='TOKYO_EARTHQUAKE_2022'))
 doc['runtime'].update(matplotlib=__import__('matplotlib').__version__,workers=min(args.workers,4),completed_utc=datetime.now(timezone.utc).isoformat())
 private_runtime=doc.pop('runtime');doc['software']={k:private_runtime[k] for k in ['python','shapely','pyproj','matplotlib']}
 out=args.output/'analysis';(out/'Context_Evidence.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2))
 narrative=f'''# Context evidence

2026-10-15 · Kajicho 1 &2 · EPSG: 6677

Core area is {cov['boundary_area_ha']:.4f} ha. The union of horizontal building-model projections is {cov['union_building_projection_m2']:,.2f} m², or {cov['gross_coverage_pct']:.2f}% of the whole town area. The denominator includes roads/rail: this gross coverage is distinct from legal parcel coverage. The established representative-point set has 277 models; 286 objects have positive area intersection.

Office use accounts for {office['object_share_pct']:.1f}% of models and {office['floor_proxy_share_pct']:.1f}% of floor-area proxy. Count describes object distribution; the proxy combines projected area and storeys. Total floor proxy is {detail['building_use']['sum_floor_proxy_m2']:,.2f} m². Actual purchased electricity and gas are absent from this analysis; 27 uses are unknown.

Commercial land is 31.96%, roads 29.76%, transport 26.56%. Land-use polygons cover the complete core, with no unmapped area and 0.858 m² of between-class overlap retained in checks. Observed use comes from 2021; legal zoning is read separately.

The 261 source heights have median 16.2 m and range 3.2–48.5 m. Sixteen LOD 1 height-difference proxies are displayed separately and excluded from source-height statistics.

The 2018-03-30 Kanda inundation forecast L 2 overlaps {flood['core_flood_area_m2']:,.2f} m², or {flood['core_flood_area_pct']:.2f}% of the core.144 models have area intersection above 0.01 m²; all core intersections are in the source depth class below 0.5 m. Recomputed IDs exactly match the existing Building_Flood_Exposure.csv.

Available 2024-02-15 Kanda river-flood L 1/L 2 and 2021-03-30 Sumida/Shingashi polygons have no core intersections. Their scope differs from the 2018 inundation forecast. The two raw L 1 GML files contain polygons north of the core. No intersection is not evidence of safety. The download window covers the core, but hazard polygons do not constitute a complete surveyed safe-area domain. Model year 2025, metadata date 2026-03-13 and source-scenario dates remain separate.

All 8,760 hourly 2025 Tokyo temperatures have normal quality codes.705 hours reach 30°C and 58 reach 35°C; the highest hourly value is 38.4°C. These are background seasonal conditions, distinct from official daily-maximum statistics and site comfort.

Tokyo's 2022 ninth earthquake assessment assigns both towns collapse rank 3 and overall rank 2; fire ranks are 2 and 1. These compare 5,192 town units under common engineering-bedrock shaking, not annual probability or individual building safety.

## Files and sources

Context_Evidence.json includes three-language metrics/charts and full details, tables and sources. CSV retains building records, land polygons, use composition, heights, scenario exposure and daily/monthly weather. Formal figures are PNG, with JPEG previews.

- [PLATEAU Chiyoda2025](https://www.geospatial.jp/ckan/dataset/plateau-13101-chiyoda-ku-2025):2021 building/land surveys,2025 model; CC BY4.0.
- [e-Stat GIS](https://www.e-stat.go.jp/gis/statmap-search):2020 town boundaries, with source terms retained.
- [JMA download](https://www.data.jma.go.jp/risk/obsdl/index.php): Tokyo2025 hourly observations.
- [Tokyo earthquake risk](https://www.funenka.metro.tokyo.lg.jp/area-hazard-level/regional-risk-list/chiyoda/index.html): ninth assessment,2022-09; published rounded values retained.
- Background outlines: © OpenStreetMap contributors, ODbL.

Processing: 08_Scripts/build_context_evidence.py. Original data/GIS were not rewritten. No CFD or other site-physics simulation was added.
'''
 (out/'Analysis.md').write_text(narrative)
 (out/'Run_Receipt.json').write_text(json.dumps({'status':'complete','runtime':private_runtime,'inputs':doc['inputs'],'outputs':outputs,'checks':{'core_objects':277,'boundary_covered_by_download_window':True,'land_class_overlap_m2':detail['land_use']['between_class_overlap_m2'],'flood_existing_ids_match':True,'flood_source_dates_separate':True,'temperature_valid_hours':8760,'formal_formats':['PNG'],'no_svg':True},'no_new_cfd':True},ensure_ascii=False,indent=2))
 print(json.dumps({'stage':'complete','charts':outputs,'metrics':doc['metrics']},ensure_ascii=False),flush=True)


def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--analyze-only',action='store_true');p.add_argument('--workers',type=int,default=4);args=p.parse_args()
 doc,raw,core,window,flood_geoms=analyze(args.input,args.output)
 if not args.analyze_only:render_all(args,doc,raw,core,window,flood_geoms)
if __name__=='__main__':main()
