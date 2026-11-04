#!/usr/bin/env python3
"""Recalculate the fixed Figure 5 areas using complete contained building objects."""
import argparse,json,csv,sqlite3,shutil,collections,concurrent.futures,os,resource,hashlib
from pathlib import Path
from shapely.geometry import shape,mapping,box
from shapely.ops import unary_union,transform
from pyproj import Transformer
import build_boundary_atlas as b
import build_poi_semantics as poi

NAMES={'en':'Kanda–Nihonbashi study area','zh':'神田—日本桥研究区','ja':'神田・日本橋研究区域'}
USE_LABEL={'office':'Office','retail':'Retail','hotel':'Hotel','housing':'House','apartments':'Apartments','mixed':'Shop + house','workhome':'Workshop + house','government':'Government','education':'Education / welfare','logistics':'Transport / storage','industry':'Industry','utilities':'Utilities','other':'Other','unknown':'Unknown'}
THEMES=b.THEMES+[('09_poi','POI functions','POI 功能')]
_DATA=None

def write(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def tr(en,zh=None,ja=None):return {'en':en,'zh':zh or en,'ja':ja or en}
def item(label,color,kind='fill',dash=False):return {'label':label if isinstance(label,dict) else tr(label),'color':color,'kind':kind,'dash':dash}

def legend_for(idx,raw,scope):
 out=[item(tr('Primary area · brief solid','重点区 · 任务书实线','重点区域・課題書の実線'),b.INK,'line'),item(tr('Wider area · brief dashed (approx.)','外围区 · 任务书虚线（概略）','周辺区域・課題書の破線（概略）'),b.INK,'line',True)]
 if idx==0:out += [item(tr('Building model','建筑模型','建物モデル'),b.INK),item(tr('Surrounding building','周边建筑','周辺建物'),'#dcdad3')]
 elif idx==1:out += [item(tr(t,z,j),c,'line') for t,z,j,c in [('Main road','主要道路','主要道路','#ad6659'),('Local road','地区道路','地区道路','#c39f4e'),('Pedestrian path','步行通道','歩行者通路','#54877d')]]
 elif idx==2:
  present={b.USES.get(r.get('usage'),'unknown') for r,g in raw['buildings'] if scope.covers(g)}
  out += [item(USE_LABEL[k],c) for k,c in b.COLORS.items() if k in present]
 elif idx==3:out += [item(t,c) for t,c in zip(['<10 m','10–20 m','20–30 m','30–45 m','≥45 m','Proxy / unavailable'],['#dedbd3','#b8cac5','#82aaa1','#508179','#355c59','#e3ded3'])]
 elif idx==4:
  present=set(str(r.get('class')) for r,g in raw['land_use'] if g.intersection(scope).area>.01)
  out += [item(b.LAND[k][0],b.LAND[k][1]) for k in b.LAND if k in present]
 elif idx==5:
  fars=sorted({float(r['FAR']) for r,g in raw['zones'] if r.get('FAR') and g.intersection(scope).area>.01})
  import matplotlib.pyplot as plt
  from matplotlib.colors import to_hex
  out += [item(f'FAR reference {far:g}%',to_hex(plt.get_cmap('PuRd')(.15+.7*i/max(1,len(fars)-1)))) for i,far in enumerate(fars)]
 elif idx==6:out += [item(tr('Park inventory','公园记录','公園記録'),'#8eac8e'),item(tr('Tree-route record','行道树路线记录','街路樹路線の記録'),'#568f73','line',True),item(tr('Tree point record','单株树记录','単木の記録'),'#446a55','point'),item(tr('Water','水系','水域'),'#a8c8d1')]
 elif idx==7:out += [item(tr('Kanda 2018 L2 overlap','神田川 2018 L2 相交范围','神田川2018 L2の重なり'),'#73a7bf'),item(tr('No recorded overlap','无相交记录','記録上の重なりなし'),'#eeece5')]
 if idx==8:out += [item(tr(en,zh,en),color,'point') for en,zh,color in poi.CATEGORIES.values()]
 if idx!=0:out += [item(tr('Context buildings','背景建筑','背景建物'),'#dcdad3')]
 return out


def render(idx):
 resource.setrlimit(resource.RLIMIT_AS,(int(3.5*1024**3),int(3.5*1024**3)))
 raw,scope,sm,out,contract,primary,poi_rows=_DATA
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.patches import Patch
 from matplotlib.lines import Line2D
 from matplotlib import patheffects
 plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':16,'text.color':b.INK,'axes.facecolor':'#eeece5','savefig.facecolor':b.PAPER})
 overview=idx<0;theme=0 if overview else idx
 window=box(*scope.buffer(90).bounds)
 fig=plt.figure(figsize=(14,12.6),facecolor=b.PAPER);ax=fig.add_axes([.04,.155,.68,.70]);ax.set_aspect('equal');ax.set_xlim(window.bounds[0],window.bounds[2]);ax.set_ylim(window.bounds[1],window.bounds[3]);ax.set_xticks([]);ax.set_yticks([])
 for sp in ax.spines.values():sp.set_color('#bcb7ac');sp.set_linewidth(.7)
 def layer(name,face='none',edge='none',lw=.3,z=1,clip=False,ls='-'):
  for r,g in raw.get(name,[]):
   if not g.intersects(window):continue
   gg=g.intersection(scope) if clip else g
   b.draw_geom(ax,gg,face,edge,lw,z,ls=ls)
 layer('water','#a8c8d1','#90b4c0',.3,1);layer('osm_buildings','#dcdad3','#bdbcb7',.12,5);layer('buildings','#dcdad3','#bdbcb7',.12,5);layer('roads',edge='#fffefa',lw=1.6,z=3)
 if theme in (0,2,3):
  for r,g in raw['buildings']:
   if not scope.covers(g):continue
   color=b.INK
   if theme==2:color=b.COLORS[b.USES.get(r.get('usage'),'unknown')]
   if theme==3:
    h=b.number(r.get('height_m'));color='#e3ded3' if 'measured' not in str(r.get('height_source','')).lower() else ['#dedbd3','#b8cac5','#82aaa1','#508179','#355c59'][0 if h is None or h<10 else 1 if h<20 else 2 if h<30 else 3 if h<45 else 4]
   b.draw_geom(ax,g,color,b.PAPER,.12,6)
 if theme==1:
  for r,g in raw['roads']:
   if not g.intersects(scope):continue
   t=r.get('tag');c='#ad6659' if t in ('motorway','trunk','primary') else '#c39f4e' if t in ('secondary','tertiary') else '#54877d' if t in ('footway','pedestrian','path') else '#aaa59b'
   b.draw_geom(ax,g.intersection(scope),edge=c,lw=2.0 if t in ('trunk','primary') else 1.3 if t in ('secondary','tertiary') else .8,z=4)
 if theme==4:
  for r,g in raw['land_use']:
   if g.intersects(scope):b.draw_geom(ax,g.intersection(scope),b.LAND.get(str(r.get('class')),('','#bfbdb7'))[1],b.PAPER,.15,4)
 if theme==5:
  fars=sorted({float(r['FAR']) for r,g in raw['zones'] if r.get('FAR') and g.intersection(scope).area>.01})
  for r,g in raw['zones']:
   if g.intersects(scope):b.draw_geom(ax,g.intersection(scope),plt.get_cmap('PuRd')(.15+.7*fars.index(float(r['FAR']))/max(1,len(fars)-1)) if r.get('FAR') else '#bbb',b.PAPER,.4,4)
 if theme==6:layer('parks','#8eac8e','#577d62',.6,4,True);layer('tree_routes',edge='#568f73',lw=1.6,z=5,clip=True,ls='--');layer('trees','#446a55','#446a55',z=6,clip=True)
 if theme==7:
  for r,g in raw['flood']:
   if r.get('source_date')=='2018-03-30' and '神田' in str(r.get('scenario','')) and g.intersects(scope):b.draw_geom(ax,g.intersection(scope),'#73a7bf',b.PAPER,.15,4,alpha=.8)
 layer('rail',edge='#79787b',lw=.9,z=6)
 if theme==8:
  for rr,pt in poi_rows:
   if scope.covers(pt):ax.scatter([pt.x],[pt.y],s=22,c=poi.CATEGORIES[rr['category']][2],edgecolors=b.PAPER,linewidths=.25,zorder=8)
 for g,dash in [(scope,'--'),(primary,'-')]:
  b.draw_geom(ax,g,edge=b.PAPER,lw=5,z=9)
  b.draw_geom(ax,g,edge=b.INK,lw=2.3,z=10,ls=dash)
 station_names={'神田駅':'Kanda','新日本橋駅':'Shin-Nihonbashi','三越前駅':'Mitsukoshimae','小伝馬町駅':'Kodemmacho','淡路町駅':'Awajicho','岩本町駅':'Iwamotocho'};seen=set()
 for r,g in raw['stations']:
  name=r.get('name');line=r.get('line','');pt=g.representative_point()
  if name not in station_names or not window.buffer(-30).covers(pt):continue
  category='Ginza' if '銀座' in line else 'JR' if any(t in line for t in ('中央','東北','総武','山手')) else ''
  key=(name,category,round(pt.x/5),round(pt.y/5))
  if key in seen:continue
  seen.add(key);label=station_names[name]+(' · '+category if category else '')
  ax.plot(pt.x,pt.y,'s',ms=6,mfc=b.PAPER,mec=b.INK,mew=.8,zorder=12)
  offset=(-18,18) if name=='神田駅' and category=='Ginza' else (8,-25) if name=='神田駅' else (-20,16) if name=='新日本橋駅' else (8,15)
  txt=ax.annotate(label,(pt.x,pt.y),xytext=offset,textcoords='offset points',fontsize=18,zorder=13);txt.set_path_effects([patheffects.withStroke(linewidth=3.7,foreground=b.PAPER)])
 focus_geoms=[primary]
 if focus_geoms:
  pt=unary_union(focus_geoms).representative_point();label=ax.annotate('Kajicho 1 & 2',(pt.x,pt.y),xytext=(18,24),textcoords='offset points',fontsize=17,weight='bold',color=b.PRIMARY,zorder=15);label.set_path_effects([patheffects.withStroke(linewidth=4,foreground=b.PAPER)])
 width=window.bounds[2]-window.bounds[0];sx=window.bounds[0]+width*.06;sy=window.bounds[1]+(window.bounds[3]-window.bounds[1])*.04
 ax.plot([sx,sx+100],[sy,sy],color=b.INK,lw=3,zorder=20);ax.text(sx,sy+15,'0     100 m',fontsize=14,zorder=20,bbox={'facecolor':b.PAPER,'edgecolor':'none','alpha':.9,'pad':3})
 ax.annotate('N',xy=(.95,.96),xytext=(.95,.85),xycoords='axes fraction',ha='center',arrowprops={'arrowstyle':'-|>','color':b.INK},fontsize=17,zorder=22)
 title='Study area' if overview else THEMES[theme][1];subtitle='研究区总图' if overview else THEMES[theme][2]
 fig.text(.045,.952,'KANDA–NIHONBASHI',fontsize=16,color=b.PRIMARY);fig.text(.045,.901,title,fontsize=31);fig.text(.045,.865,subtitle,fontsize=18)
 fig.text(.755,.82,'BRIEF FIGURE 5',fontsize=16,weight='bold');fig.text(.755,.778,f"{sm['area_ha']:.2f} ha",fontsize=23);fig.text(.755,.736,f"{sm['selected_models']:,} wider-area models",fontsize=18)
 legend=legend_for(theme,raw,scope)
 handles=[]
 for entry in legend:
  label=__import__('textwrap').fill(entry['label']['en'],width=22)
  if entry['kind']=='line':h=Line2D([0],[0],color=entry['color'],lw=2.5,ls='--' if entry['dash'] else '-',label=label)
  elif entry['kind']=='point':h=Line2D([0],[0],marker='o',ls='',color=entry['color'],ms=6,label=label)
  else:h=Patch(facecolor=entry['color'],edgecolor='#bab6ad',lw=.3,label=label)
  handles.append(h)
 fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.745,.69),frameon=False,fontsize=17,labelspacing=.65,handlelength=1.9)
 fig.text(.045,.115,'Official brief: solid primary + dashed approximate wider area. Registration screening band: 25 m.',fontsize=15)
 note='Buildings: PLATEAU LOD1 / OSM context. Source dates and methods: source_manifest.json.'
 if theme==6:note='Green records: park, tree point and route inventories. Missing point records remain a source gap.'
 if theme==8:note='POIs: © OpenStreetMap contributors (ODbL), 18 OCT 2026. Tagged destinations; support records kept separately.'
 if theme==7:note='Map: Kanda basin 2018 L2 source overlap. All four scenarios remain separate in the data tables.'
 fig.text(.045,.058,note+'\nEPSG:6677 · North up · © OpenStreetMap contributors · 18 OCT 2026',fontsize=12.5,linespacing=1.7,color='#625e58')
 name='00_study_area' if overview else THEMES[theme][0];png=out/'maps'/(name+'.png');png.parent.mkdir(exist_ok=True);fig.savefig(png,dpi=200)
 fig.canvas.draw();bbox=ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted());preview=out/'maps/previews'/(name+'.jpg');preview.parent.mkdir(exist_ok=True)
 fig.savefig(preview,dpi=160,bbox_inches=bbox,pad_inches=.02,format='jpeg',pil_kwargs={'quality':94})
 plt.close(fig)
 notes={0:tr('Only complete footprints covered by the fixed outline enter building analysis. Exterior and crossing models stay grey.','建筑分析仅纳入边界完整覆盖的原始轮廓；外部和跨界模型统一显示为浅灰。'),1:tr('Road lengths describe mapped source lines, including separate carriageways.','道路长度统计源线，分隔车道分别保留。'),2:tr('Use classes come from source building attributes. Unknown uses remain visible.','用途来自模型源属性，未知用途单列。'),3:tr('Measured-height source values and proxy heights remain separate.','源高度与代理高度分列。'),4:tr('Observed land use uses the survey classification, separate from legal planning zones.','现状土地利用与法定用途地域分别读取。'),5:tr('Reference FAR is a planning layer; parcel controls require site-specific checks.','图层为规划参考容积率，地块条件须逐宗核查。'),6:tr('Point, route and park records have different units and coverage.','单株、路线和公园记录采用不同单位与覆盖范围。'),7:tr('No recorded flood-polygon overlap does not establish safety.','无洪水源面相交记录不代表安全。')}
 notes[8]=tr('OSM function tags describe mapped destinations. Counts and local mixes reflect source coverage.','OSM 功能标签描述已记录目的地；数量与局部功能构成受来源覆盖影响。')
 return {'id':name,'kind':'overview' if overview else 'theme','theme':None if overview else THEMES[theme][0],'scope':'study_area','overlaid_scopes':['study_area','primary_brief'],'primary_boundary_geometry_sha256':json.loads((out/'study_boundary_6677.geojson').read_text())['features'][1]['properties']['geometry_sha256'],'title':tr(title,subtitle,title),'file':'study-atlas/maps/'+png.name,'preview':'study-atlas/maps/previews/'+preview.name,'pixels':[2800,2520],'preview_kind':'map_only','preview_pixels':list(__import__('PIL.Image',fromlist=['Image']).open(preview).size),'extent_6677':list(window.bounds),'boundary_geometry_sha256':contract['geometry_sha256'],'legend':legend,'reading_note':notes[theme],'text_sizes':{'export_legend_pt':17,'export_map_labels_pt':18,'web_legend_css_px':17},'metrics':{'area_ha':sm['area_ha'],'building_models':sm['selected_models']}}


def refresh_manifest(manifest,contract,sm):
 manifest.update(scope_ids=['study_area','primary_brief'],course_boundary=contract['basis'],boundary_geometry_sha256=contract['geometry_sha256'],building_clipping=False,map_presentation='Map-only web previews with native HTML legends; full PNG exports use large legends.',processing_date='2026-10-18',new_cfd=False,model_membership_rule=sm['selection_rule'])
 manifest['source_pool_building_wards']=manifest.pop('building_wards',manifest.get('source_pool_building_wards',{}))
 manifest['selected_building_wards']=sm['selected_ward_models']
 manifest['study_inventory']={'area_ha':sm['area_ha'],'selected_models':sm['selected_models'],'source_pool_models':9244,'selected_ward_labels':{'13101':'Chiyoda','13102':'Chuo'},'model_year':2025,'known_survey_year':2021,'known_use_models':sm['known_use_models'],'unknown_use_models':sm['unknown_use_models'],'record_unit':'Complete LOD1 model object; not a surveyed individual-building count'}
 for layer,info in manifest['layers'].items():info['inventory_role']='Retained source-pool records; study selection is recorded separately.'
 keep={'OSM_Raw','P0_MLIT_PLANNING_FY2025','P0_TOKYO_TREE_POINTS','P0_TOKYO_TREE_ROUTES','P0_TOKYO_PARKS','P1_PLATEAU_RELATED'}
 manifest['source_register']=[x for x in manifest['source_register'] if x['dataset_id'] in keep]
 common={'provider':'MLIT PLATEAU','document_year':'2025 release','website_file_version':'2025 CityGML','download_date':'2026-10-16','crs':'EPSG:6697 source; EPSG:6677 analysis','license':'CC BY 4.0','units':'m; m2'}
 for dataset,name,url,year,unit in [
  ('Study_PLATEAU_Chiyoda','PLATEAU Chiyoda buildings','https://www.geospatial.jp/ckan/dataset/plateau-13101-chiyoda-ku-2025','2025 model; 2021 survey where known; geometry 2024-03-15',f"Complete LOD1 model object; {sm['selected_ward_models'].get('13101',0)} study-selected"),
  ('Study_PLATEAU_Chuo','PLATEAU Chuo buildings','https://assets.cms.plateau.reearth.io/assets/93/1f058b-e06b-445c-ae62-2e02cdf72849/13102_chuo-ku_pref_2025_citygml_1_op.zip','2025 model; 2021 survey where known; geometry 2024-03-15',f"Complete LOD1 model object; {sm['selected_ward_models'].get('13102',0)} study-selected"),
  ('Study_Land_Use','PLATEAU observed land use: Tokyo','https://assets.cms.plateau.reearth.io/assets/93/1f058b-e06b-445c-ae62-2e02cdf72849/13102_chuo-ku_pref_2025_citygml_1_op/udx/luse/533946_luse_6697_op.gml','2021 survey; 2025 model','Survey-class union intersected with study area; duplicate Chiyoda records omitted'),
  ('Study_Flood','PLATEAU river-flood scenario polygons','https://www.geospatial.jp/ckan/dataset/plateau-13101-chiyoda-ku-2025','2018-03-30; 2024-02-15; 2021-03-30 scenarios; 2025 model','Each scenario intersected separately; four scenarios; no recorded overlap is not safety')]:
  manifest['source_register'].append(dict(common,dataset_id=dataset,name=name,source_url=url,data_year=year,record_unit=unit))
 manifest['source_register'].append({'dataset_id':'Study_Boundary','name':'Official brief Figure 5 solid primary and dashed approximate secondary traces','source_url':'https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view','data_year':'2026 brief; railway land-use survey 2021 / model 2025; OSM 2026-10-13','document_year':'2026','download_date':'2026-10-16','record_unit':'Two unchanged registered Figure 5 source traces; solid primary and approximate dashed wider area','crs':'EPSG:6677','license':'Brief copyright retained; OSM-derived geometry ODbL'})
 return manifest

def make_qgis(asset,team,boundaries,members,poi_rows):
 from qgis.core import QgsApplication,QgsVectorLayer,QgsProject,QgsCoordinateReferenceSystem,QgsVectorFileWriter,QgsFeature,QgsField,QgsGeometry,Qgis,QgsFillSymbol,QgsLineSymbol,QgsMarkerSymbol,QgsCategorizedSymbolRenderer,QgsRendererCategory,QgsReferencedRectangle,QgsRectangle
 from qgis.PyQt.QtCore import QVariant
 assert Qgis.QGIS_VERSION_INT>=34400,'Use QGIS 3.44+ for the portable GeoPackage project; older mdx1 GDAL failed provider reads.'
 global _QGIS_APP
 _QGIS_APP=QgsApplication.instance() or QgsApplication([],False);_QGIS_APP.initQgis()
 project=QgsProject();project.setCrs(QgsCoordinateReferenceSystem('EPSG:6677'));project.setTitle('Kanda–Nihonbashi | Official brief Figure 5 + POI')
 project.setFilePathStorage(Qgis.FilePathType.Relative)
 path=team/'04_Data/Ready/Study_Area_2026-10-18/Kanda_Nihonbashi_Study.gpkg';path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():path.unlink()
 source=sqlite3.connect('file:'+str(asset)+'?mode=ro',uri=True);dest=sqlite3.connect(path);source.backup(dest);dest.close();source.close()
 def save(layer,name):
  opt=QgsVectorFileWriter.SaveVectorOptions();opt.driverName='GPKG';opt.layerName=name;opt.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteLayer
  result=QgsVectorFileWriter.writeAsVectorFormatV3(layer,str(path),project.transformContext(),opt);assert result[0]==QgsVectorFileWriter.NoError,result
 for sid,(props,g) in boundaries.items():
  layer=QgsVectorLayer('MultiPolygon?crs=EPSG:6677',sid,'memory');dp=layer.dataProvider()
  dp.addAttributes([QgsField('scope',QVariant.String),QgsField('area_ha',QVariant.Double),QgsField('source',QVariant.String),QgsField('geometry_sha256',QVariant.String),QgsField('screening_band_m',QVariant.Double),QgsField('line_style',QVariant.String)]);layer.updateFields()
  f=QgsFeature(layer.fields());gg=QgsGeometry.fromWkt(g.wkt);gg.convertToMultiType();f.setGeometry(gg);f.setAttributes([sid,g.area/10000,props['source'],props['geometry_sha256'],25.,props['line_style']]);dp.addFeatures([f]);save(layer,sid)
 layer=QgsVectorLayer(str(team/'04_Data/Ready/POI_OSM_2026-10-18/poi_6677.geojson'),'poi','ogr');assert layer.isValid();save(layer,'poi')
 c=sqlite3.connect(path)
 def geom(blob):
  blob=bytes(blob);size={0:0,1:32,2:48,3:48,4:64}[(blob[3]>>1)&7];return b.wkb.loads(blob[8+size:])
 c.create_function('ST_IsEmpty',1,lambda data:int(geom(data).is_empty))
 for fn,idx in [('ST_MinX',0),('ST_MinY',1),('ST_MaxX',2),('ST_MaxY',3)]:c.create_function(fn,1,lambda data,i=idx:geom(data).bounds[i])
 for col,sid in [('in_study_area','study_area'),('in_primary_area','primary_brief')]:
  c.execute('alter table buildings add column '+col+' integer not null default 0');c.executemany('update buildings set '+col+'=1 where asset_id=?',[(i,) for i in members[sid]])
 for col,sid in [('in_study_area','study_area'),('in_primary_area','primary_brief')]:
  c.execute('alter table osm_buildings add column '+col+' integer not null default 0')
  ids=[(str(r['osm_id']),) for r,g in b.read(asset)['osm_buildings'] if boundaries[sid][1].covers(g)]
  c.executemany('update osm_buildings set '+col+'=1 where osm_id=?',ids)
 c.execute('create table study_membership(scope text,asset_id text,selection_rule text,primary key(scope,asset_id))');c.executemany('insert into study_membership values(?,?,?)',[(sid,i,'Fixed Figure 5 outline covers the complete original source footprint; no clipping') for sid,ids in members.items() for i in ids]);c.execute("insert into gpkg_contents(table_name,data_type,identifier,description) values('study_membership','attributes','study_membership','Independent membership in the two Figure 5 source traces')");c.commit();c.close()
 for name,col in [('analysis_buildings_wider','in_study_area'),('analysis_buildings_primary','in_primary_area')]:
  layer=QgsVectorLayer(str(path)+'|layername=buildings',name,'ogr');assert layer.isValid();assert layer.setSubsetString('"'+col+'" = 1');save(layer,name);layer=None
 c=sqlite3.connect(path);names=[x[0] for x in c.execute('select table_name from gpkg_geometry_columns')];c.close()
 membership=QgsVectorLayer(str(path)+'|layername=study_membership','study_membership','ogr');assert membership.isValid();assert membership.featureCount()==sum(len(v) for v in members.values());project.addMapLayer(membership);project.layerTreeRoot().findLayer(membership.id()).setItemVisibilityChecked(False);membership=None
 def draw_order(name):return 5 if name in boundaries else 4 if name in ('poi','stations') else 3 if name.startswith('analysis_buildings_') else 2 if name in ('roads','rail') else 1 if name in ('buildings','osm_buildings') else 0
 for name in sorted(names,key=lambda n:(draw_order(n),n)):
  layer=QgsVectorLayer(str(path)+'|layername='+name,name,'ogr');assert layer.isValid()
  if name in boundaries:layer.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'0,0,0,0','outline_color':b.INK,'outline_width':'.9','outline_style':'dash' if name=='study_area' else 'solid'}))
  elif name in ('buildings','osm_buildings'):
   layer.setName('Context · '+('PLATEAU source buildings' if name=='buildings' else 'OSM source buildings'));layer.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'#dcdad3','outline_color':'#bdbcb7','outline_width':'.05'}))
  elif name.startswith('analysis_buildings_'):
   layer.renderer().setSymbol(QgsFillSymbol.createSimple({'color':b.INK,'outline_color':'#fff','outline_width':'.08'}))
  elif name=='poi':
   cats=[QgsRendererCategory(k,QgsMarkerSymbol.createSimple({'color':color,'size':'2.2','outline_color':'#fff','outline_width':'.1'}),en) for k,(en,zh,color) in poi.CATEGORIES.items()];layer.setRenderer(QgsCategorizedSymbolRenderer('category',cats));layer.setSubsetString('"in_study_area" = 1')
  elif layer.geometryType()==2:layer.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'#d4d0c7','outline_color':'#fff','outline_width':'.1'}))
  elif layer.geometryType()==1:layer.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':'#8a857d','line_width':'.25'}))
  else:layer.renderer().setSymbol(QgsMarkerSymbol.createSimple({'color':'#446a55','size':'1.5'}))
  verify=sqlite3.connect(path);expected=verify.execute('select count(*) from "'+name+'"'+(' where in_study_area=1' if name=='poi' else '')).fetchone()[0];verify.close()
  actual=sum(1 for f in layer.getFeatures());assert actual==expected,(name,actual,expected)
  project.addMapLayer(layer);project.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(name in ('study_area','primary_brief','buildings','osm_buildings','analysis_buildings_wider','roads','rail','water','stations','poi'))
 project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(QgsRectangle(*boundaries['study_area'][1].buffer(90).bounds),project.crs()))
 filename=team/'05_QGIS/Projects/Kanda_Nihonbashi_Study_2026-10-18.qgz';filename.parent.mkdir(parents=True,exist_ok=True);project.setFileName(str(filename));assert project.write()
 # Close all providers before transferring the GeoPackage; no unshipped WAL state.
 project.clear();layer=None;dp=None
 import gc;gc.collect()
 c=sqlite3.connect(path);checkpoint=c.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone();assert checkpoint[0]==0,checkpoint;c.close()
 wal=Path(str(path)+'-wal');assert not wal.exists() or wal.stat().st_size==0,'Export must be self-contained before transfer'
 return path,filename



def seal_gis(path):
 # End the QGIS provider pool, then freeze a complete SQLite snapshot for sharing.
 global _QGIS_APP
 _QGIS_APP.exitQgis();_QGIS_APP=None
 import gc;gc.collect()
 snapshot=path.with_name(path.stem+'.sealed.gpkg')
 if snapshot.exists():snapshot.unlink()
 source=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True);dest=sqlite3.connect(snapshot)
 source.backup(dest);dest.close();source.close()
 for suffix in ('-wal','-shm'):
  side=Path(str(path)+suffix)
  if side.exists():
   if suffix=='-wal':assert side.stat().st_size==0,'Unclosed GIS writer'
   side.unlink()
 snapshot.replace(path)
 check=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True);assert check.execute('PRAGMA quick_check').fetchone()[0]=='ok';assert check.execute('select count(*) from gpkg_geometry_columns').fetchone()[0]==20;check.close()

MEMBERSHIP_RULE='The fixed registered Figure 5 outline covers the complete original source footprint; exterior and crossing objects are context only, with no clipping.'
NORTHERN_ID='13101:bldg_8b5f6318-5eeb-4219-87fa-1c09506ef58a'

def audit_membership(raw,boundaries,out):
 rows=[];crossings=[];summary={}
 for sid,(props,scope) in boundaries.items():
  summary[sid]={}
  for layer in ('buildings','osm_buildings'):
   counts=collections.Counter()
   for r,g in raw[layer]:
    included=scope.covers(g);inside=g.intersection(scope).area;outside=g.difference(scope).area
    reason='fully_covered' if included else 'crossing_outline' if inside>0 else 'outside_or_touch_only'
    uid=str(r.get('asset_id') or r.get('osm_id'));counts[reason]+=1
    row={'scope':sid,'source_layer':layer,'source_id':uid,'in_analysis':int(included),'reason':reason,'source_footprint_m2':g.area,'inside_m2':inside,'outside_m2':outside,'previous_representative_point_inside':int(scope.covers(g.representative_point())),'northern_reported_building':int(uid in (NORTHERN_ID,'190375727'))}
    rows.append(row)
    if not included:crossings.append(row)
   summary[sid][layer]=dict(counts)
 b.csvout(out/'building_membership_audit.csv',rows)
 b.csvout(out/'tables/excluded_buildings.csv',crossings)
 return summary

def main():
 p=argparse.ArgumentParser();p.add_argument('--task-root',type=Path,required=True);p.add_argument('--workers',type=int,default=10)
 mode=p.add_mutually_exclusive_group();mode.add_argument('--gis-only',action='store_true');mode.add_argument('--skip-gis',action='store_true')
 a=p.parse_args();root=a.task_root;team=root/'team';out=team/'06_Outputs/Study_Area_2026-10-18';asset=root/'assets/assets.gpkg'
 os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',QT_QPA_PLATFORM='offscreen');resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
 source_path=out/'study_boundary_6677.geojson';source_bytes=source_path.read_bytes();data=json.loads(source_bytes)
 for f in data['features']:f['properties']['selection_rule']=MEMBERSHIP_RULE
 boundaries={f['properties']['id']:(f['properties'],shape(f['geometry'])) for f in data['features']};contract,scope=boundaries['study_area'];primary=boundaries['primary_brief'][1]
 if a.gis_only:
  atlas=json.loads((out/'atlas.json').read_text());members={sid:set() for sid in boundaries}
  with (out/'tables/buildings.csv').open(encoding='utf-8-sig') as f:
   for r in csv.DictReader(f):members[r['scope']].add(r['asset_id'])
  assert {sid:len(ids) for sid,ids in members.items()}=={sid:sm['selected_models'] for sid,sm in atlas['scopes'].items()}
  gpkg,project=make_qgis(asset,team,boundaries,members,[]);seal_gis(gpkg)
  quality=json.loads((out/'quality_checks.json').read_text());quality.update(gis_export_status='passed',qgis_project=str(project.relative_to(team)),gpkg=str(gpkg.relative_to(team)),gis_spatial_layers=20,gis_attribute_tables=1)
  write(out/'quality_checks.json',quality);print(json.dumps(quality,ensure_ascii=False),flush=True);return
 raw=b.read(asset);b.SCOPE_NAMES={sid:props['name'] for sid,(props,g) in boundaries.items()}
 summaries,tables,members=b.analyze(raw,boundaries,data,out)
 for table in (out/'tables').glob('*.csv'):table.write_text(table.read_text())
 audit=audit_membership(raw,boundaries,out)
 for sid,(props,g) in boundaries.items():
  sm=summaries[sid];sm['boundary_geometry_sha256']=props['geometry_sha256'];sm['boundary_revision']=props['boundary_revision']
  sm['selected_ward_models']=dict(collections.Counter(str(r['ward_code']) for r,h in raw['buildings'] if r['asset_id'] in members[sid]))
  sm['raw_boundary_crossing_models']=sum(h.intersection(g).area>.01 and h.difference(g).area>.01 for r,h in raw['buildings'])
  sm['raw_boundary_crossing_osm']=sum(h.intersection(g).area>.01 and h.difference(g).area>.01 for r,h in raw['osm_buildings'])
  sm['selected_osm_context_footprints']=len(b.select_full_buildings(raw['osm_buildings'],g))
  assert all(g.covers(h) for r,h in raw['buildings'] if r['asset_id'] in members[sid])
 write(out/'statistics.json',{'updated_date':'2026-10-18','crs':'EPSG:6677','scopes':summaries,'rules':{'model_selection':'The unchanged registered Figure 5 outline must cover the complete original footprint; exterior and crossing buildings remain context only.','area':'Two unchanged source outlines; outer is explicitly approximate.','footprint':'Union of complete selected source footprints; no clipping or exterior fragments.','uncertainty':'25 m cartographic screening band; full-footprint membership sensitivity is reported, not a confidence interval.','actual_energy':'Actual energy and carbon remain missing.'}})
 poi_rows,poi_data=poi.build(root,boundaries)
 sm=summaries['study_area'];global _DATA;_DATA=(raw,scope,sm,out,contract,primary,poi_rows)
 with concurrent.futures.ProcessPoolExecutor(max_workers=max(1,min(10,a.workers))) as pool:plates=list(pool.map(render,[-1]+list(range(len(THEMES)))))
 write(out/'atlas.json',{'schema_version':6,'date':'2026-10-18','crs':'EPSG:6677','study_area':contract,'boundaries':data,'plates':plates,'scopes':summaries,'map_export_formats':['PNG'],'no_new_cfd':True})
 base=team/'04_Data/Metadata/Study_Source_Manifest_Base.json'
 manifest=refresh_manifest(json.loads(base.read_text()),contract,sm);manifest['course_boundary']='Official brief p.4 Figure 5: unchanged solid primary + dashed approximate secondary source traces.';manifest['source_register'].append(dict(poi_data['source'],dataset_id='OSM_POI_2026-10-18',name='OpenStreetMap tagged destinations',source_url='https://www.openstreetmap.org/copyright',data_year='2026-10-18 source snapshot',download_date='2026-10-18',record_unit='Classified source object after documented node/area merge'));write(out/'source_manifest.json',manifest)
 trf=Transformer.from_crs(6677,4326,always_xy=True).transform
 features=[{'type':'Feature','properties':dict(props,layer=sid),'geometry':mapping(transform(trf,g))} for sid,(props,g) in boundaries.items()]
 for layer,rows in raw.items():
  if layer in ('source_coverage','census'):continue
  for r,g in rows:
   properties={k:v for k,v in r.items() if k not in ('source_attrs_json','fid')};properties['layer']=layer
   if layer in ('buildings','osm_buildings'):
    properties['in_study_area']=scope.covers(g);properties['in_primary_area']=primary.covers(g)
   display_geometry=g if layer in ('buildings','osm_buildings') else g.simplify(.12,preserve_topology=True)
   features.append({'type':'Feature','properties':properties,'geometry':mapping(transform(trf,display_geometry))})
 for r,g in poi_rows:features.append({'type':'Feature','properties':dict(r,layer='poi'),'geometry':mapping(transform(trf,g))})
 (out/'atlas.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':'))+'\n')
 gpkg=team/'04_Data/Ready/Study_Area_2026-10-18/Kanda_Nihonbashi_Study.gpkg';project=team/'05_QGIS/Projects/Kanda_Nihonbashi_Study_2026-10-18.qgz'
 if not a.skip_gis:
  gpkg,project=make_qgis(asset,team,boundaries,members,poi_rows);seal_gis(gpkg)
 assert source_path.read_bytes()==source_bytes,'Source Figure 5 boundaries changed during atlas generation'
 quality={'status':'passed','boundary_count':2,'boundary_revision':contract['boundary_revision'],'source':'Official brief p4 Figure5','geometry_sha256':contract['geometry_sha256'],'primary_geometry_sha256':boundaries['primary_brief'][0]['geometry_sha256'],'source_boundary_file_sha256':hashlib.sha256(source_bytes).hexdigest(),'area_ha':scope.area/10000,'selected_models':sm['selected_models'],'boundary_crossing_plateau':sm['raw_boundary_crossing_models'],'boundary_crossing_osm':sm['raw_boundary_crossing_osm'],'analysis_boundary_crossings':{sid:0 for sid in boundaries},'exterior_analysis_buildings':{sid:0 for sid in boundaries},'building_membership_rule':sm['selection_rule'],'building_audit':audit,'northern_reported_model_excluded':NORTHERN_ID not in members['study_area'],'source_building_geometry_unchanged':True,'png_maps':len(plates),'thematic_maps':len(THEMES),'crs':'EPSG:6677','new_cfd':False,'gis_export_status':'pending_compatible_host' if a.skip_gis else 'passed','qgis_project':str(project.relative_to(team)),'gpkg':str(gpkg.relative_to(team)),'gis_spatial_layers':20,'gis_attribute_tables':1,'poi_counts':{sid:d['poi_count'] for sid,d in poi_data['scopes'].items()}}
 write(out/'quality_checks.json',quality);print(json.dumps(quality,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
