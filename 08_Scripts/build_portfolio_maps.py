#!/usr/bin/env python3
"""Export PNG-only source-bound Kajicho map plates. Does not change sources or run CFD.

Run: python3 build_portfolio_maps.py --input inputs --output . --workers 4
Input contains consistent read-only SQLite backups baseline.gpkg/common.gpkg and sources.json.
"""
import argparse, collections, concurrent.futures, hashlib, json, math, os, platform, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path
import shapely
from shapely import wkb
from shapely.geometry import box, mapping
from shapely.ops import transform, unary_union
from shapely.geometry.polygon import orient
import pyproj

EXTENT=(-6125.,-34630.,-5025.,-33730.)
W,H=1100,900
PAPER='#f7f5ef';INK='#36353a';PURPLE='#59457f';TEAL='#719a94';BRICK='#b97667';OCHRE='#cfb56d';GREY='#cfceca';WATER='#a8c8d1'
USE={
 'office':('#BE1E32',{'en':'Office','zh':'办公','ja':'業務施設'}),
 'retail':('#785028',{'en':'Retail','zh':'商业设施','ja':'商業施設'}),
 'hotel':('#F08CBE',{'en':'Hotel','zh':'住宿设施','ja':'宿泊施設'}),
 'housing':('#F0F0A0',{'en':'House','zh':'住宅','ja':'住宅'}),
 'apartments':('#FAAAA0',{'en':'Apartments','zh':'集合住宅','ja':'共同住宅'}),
 'mixed':('#F5F05A',{'en':'Housing + shop','zh':'住商混合','ja':'店舗等併用住宅'}),
 'workhome':('#B48CBE',{'en':'Housing + workshop','zh':'住工混合','ja':'作業所併用住宅'}),
 'government':('#0A78BE',{'en':'Government','zh':'行政设施','ja':'官公庁施設'}),
 'education':('#FAA032',{'en':'Education / care','zh':'文教与医疗','ja':'文教厚生施設'}),
 'logistics':('#283C8C',{'en':'Transport / storage','zh':'运输与仓储','ja':'運輸倉庫施設'}),
 'industry':('#00643C',{'en':'Factory','zh':'工厂','ja':'工場'}),
 'utilities':('#505050',{'en':'Utilities','zh':'供给处理设施','ja':'供給処理施設'}),
 'other':('#828282',{'en':'Other','zh':'其他','ja':'その他'}),
 'unknown':('#BEBEBE',{'en':'Unknown','zh':'未知','ja':'不明'})}
LAND={
 '211':('#FFFF00',{'en':'Housing / mixed','zh':'居住与住商混合','ja':'住宅用地'}),
 '212':('#E65050',{'en':'Commercial land','zh':'商业用地','ja':'商業用地'}),
 '213':('#1E46FF',{'en':'Industrial land','zh':'工业用地','ja':'工業用地'}),
 '214':('#C800DC',{'en':'Public facilities','zh':'公共设施用地','ja':'公益施設用地'}),
 '215':('#FFFFFF',{'en':'Road land','zh':'道路用地','ja':'道路用地'}),
 '216':('#8C8C8C',{'en':'Rail / logistics','zh':'交通与仓储','ja':'交通施設用地'}),
 '217':('#C8FFC8',{'en':'Parks / open space','zh':'公园与运动场','ja':'公共空地'}),
 '204':('#78DCFF',{'en':'Water','zh':'水域','ja':'水面'}),
 '222':('#FFFFFF',{'en':'Outdoor parking','zh':'露天停车场（斜线）','ja':'屋外駐車場'}),
 '223':('#FFFFFF',{'en':'Other outdoor use','zh':'其他室外用地（斜线）','ja':'その他屋外利用地'}),
 '224':('#FFFFFF',{'en':'Unused land','zh':'未利用地（竖线）','ja':'未利用地'})}

HEIGHTS=[('#dedbd3',{'en':'< 10 m','zh':'低于 10 米','ja':'10 m 未満'}),('#b8cac5',{'en':'10–20 m','zh':'10–20 米','ja':'10–20 m'}),('#82aaa1',{'en':'20–30 m','zh':'20–30 米','ja':'20–30 m'}),('#508179',{'en':'30–45 m','zh':'30–45 米','ja':'30–45 m'}),('#355c59',{'en':'≥ 45 m','zh':'45 米及以上','ja':'45 m 以上'}),('#ece8df',{'en':'Height proxy','zh':'代理高度','ja':'推定高さ'})]

def geometry(b):
 if b is None:return None
 flag=b[3];envelope=(flag>>1)&7
 return wkb.loads(bytes(b)[8+{0:0,1:32,2:48,3:48,4:64}[envelope]:])

def read(path,table):
 c=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 result=[]
 for row in c.execute('select * from "'+table+'"'):
  r=dict(row);g=geometry(r.pop('geom'))
  if g is not None and not g.is_empty and g.intersects(box(*EXTENT)):
   if not g.is_valid:g=g.buffer(0)
   g=g.intersection(box(*EXTENT))
   if not g.is_empty:result.append((r,g))
 c.close();return result

def xy(g):return transform(lambda x,y,z=None:(x-EXTENT[0],EXTENT[3]-y),g)
def path_string(g):
 g=xy(g).simplify(.12,preserve_topology=True)
 def line(coords,closed=False):
  pts=list(coords)
  if not pts:return ''
  return 'M'+' L'.join(f'{p[0]:.1f},{p[1]:.1f}' for p in pts)+(' Z' if closed else '')
 def rec(q):
  if q.geom_type=='Polygon':return line(q.exterior.coords,True)+' '+ ' '.join(line(r.coords,True) for r in q.interiors)
  if q.geom_type in ['LineString','LinearRing']:return line(q.coords)
  if hasattr(q,'geoms'):return ' '.join(rec(p) for p in q.geoms)
  return ''
 return rec(g)

def group_use(v):
 return {'業務施設':'office','商業施設':'retail','宿泊施設':'hotel','住宅':'housing','共同住宅':'apartments','店舗等併用住宅':'mixed','作業所併用住宅':'workhome','官公庁施設':'government','文教厚生施設':'education','運輸倉庫施設':'logistics','工場':'industry','供給処理施設':'utilities','その他':'other'}.get(v,'unknown')

def build(inp):
 base=inp/'baseline.gpkg';common=inp/'common.gpkg'
 tables={'core':(base,'primary_area'),'coverage':(base,'analysis_extent'),'buildings':(base,'buildings'),'osm_buildings':(common,'buildings'),'roads':(base,'roads'),'rail':(base,'rail'),'water':(base,'water'),'water_lines':(base,'water_lines'),'land_use':(base,'plateau_luse'),'zones_chiyoda':(base,'mlit_13101_youto'),'zones_chuo':(base,'mlit_13102_youto'),'parks_city':(base,'parks_city'),'parks_other':(base,'parks_other'),'trees':(base,'street_tree_points'),'tree_routes':(base,'street_tree_routes'),'stations_chiyoda':(base,'related_13101_station'),'stations_chuo':(base,'related_13102_station')}
 raw={k:read(*v) for k,v in tables.items()};raw['zones']=raw.pop('zones_chiyoda')+raw.pop('zones_chuo');raw['parks']=raw.pop('parks_city')+raw.pop('parks_other');raw['stations']=raw.pop('stations_chiyoda')+raw.pop('stations_chuo')
 layers={};features=[];to_wgs=pyproj.Transformer.from_crs(6677,4326,always_xy=True).transform
 for k,rows in raw.items():
  entries=[]
  for i,(r,g) in enumerate(rows):
   out={'id':str(r.get('building_id') or r.get('osm_id') or r.get('gml_id') or f'{k}-{i+1}'),'path':path_string(g)}
   if k=='buildings':
    use=group_use(r.get('usage'));height=r.get('height_m');hb=5 if r.get('height_source')!='bldg:measuredHeight' else next((j for j,b in enumerate([10,20,30,45,math.inf]) if height<b),4)
    out.update(core=bool(r['core']),use=use,useLabel=USE[use][1],color=USE[use][0],sourceUse=r.get('usage'),detail=r.get('detailed_use'),height=height,heightSource=r.get('height_source'),heightBand=hb,surveyYear=r.get('survey_year'),modelYear=r.get('model_year'))
   elif k=='land_use':out.update(color=LAND.get(str(r['class']),('#BEBEBE',{}))[0],pattern={'222':'parking','223':'outdoor','224':'unused'}.get(str(r['class'])),category=str(r['class']),label=r['class_label'],detail=r.get('orgLandUse_label'),surveyYear=r.get('surveyYear'))
   elif k=='zones':out.update(label=r['YoutoName'],far=float(r['FAR']),bcr=float(r['BCR']),city=r.get('Cityname'))
   elif k in ['roads','rail','water','water_lines','osm_buildings']:out.update(name=r.get('name',''),kind=r.get('tag',''))
   elif k=='parks':out.update(name=r.get('公園名',''),kind=r.get('区分',''))
   elif k=='tree_routes':out.update(name=r.get('路線名',''),species=r.get('樹種',''),originalRouteCount=r.get('本数'))
   elif k=='stations':out.update(name=r['駅名'],line=r['路線名'])
   if g.geom_type=='Point':out.update(x=round(g.x-EXTENT[0],1),y=round(EXTENT[3]-g.y,1));out.pop('path',None)
   elif k in ['stations','parks']:
    pt=g.representative_point();out.update(x=round(pt.x-EXTENT[0],1),y=round(EXTENT[3]-pt.y,1))
   entries.append(out)
   prop={a:b for a,b in out.items() if a not in ['path','x','y']};prop['layer']=k
   features.append({'type':'Feature','geometry':mapping(transform(to_wgs,g.simplify(.12,preserve_topology=True))),'properties':prop})
  layers[k]=entries
 core=[x for x in layers['buildings'] if x['core']]
 assert len(core)==277,len(core)
 counts={k:len(v) for k,v in layers.items()};counts.update(core_buildings=len(core),core_known_use=sum(x['sourceUse']!='不明' for x in core),core_use=dict(collections.Counter(x['use'] for x in core)),core_height_proxy=sum(x['heightBand']==5 for x in core))
 sources=json.loads((inp/'sources.json').read_text());sources=[x for x in sources if not any(q in x['dataset_id'] for q in ['DECC','FLOOD','HOURLY'])]
 sources.extend([{'dataset_id':'OSM_20261013','name':'Streets, rail, water and context buildings','provider':'© OpenStreetMap contributors','source_url':'https://www.openstreetmap.org/copyright','data_year':'Snapshot 2026-10-13','download_date':'2026-10-13','crs':'EPSG:4326 source; EPSG:6677 display','license':'ODbL 1.0','processing_steps':'Clip existing source snapshot to map extent; no inferred roads or connections.'},{'dataset_id':'ESTAT_2020','name':'Kajicho 1 and 2 boundary','provider':'e-Stat / Statistics Bureau','source_url':'https://www.e-stat.go.jp/gis/statmap-search','data_year':'2020 Census','download_date':'2026-10-13','crs':'EPSG:6668 source; EPSG:6677 display','license':'e-Stat terms and GIS terms; attribution required','processing_steps':'Dissolve census town codes 13101035001 and 13101035002; course boundary remains to confirm.'}])
 return layers,raw,counts,sources,{'type':'FeatureCollection','features':features}

PLATES=[
 {'id':'01_figure_ground','title':{'en':'A compact urban fabric','zh':'紧凑的街区肌理','ja':'密度のある街区'},'subtitle':'FIGURE GROUND  /  建筑与开放空间','body':['Kajicho 1 & 2','鍛冶町一・二丁目','277 core building model objects','核心区 277 个建筑模型对象','','Street blocks meet the rail corridor.','街巷与铁路共同组织街区。'],'note':['Core: PLATEAU model objects. Context: OSM footprints.','核心为 PLATEAU；背景为 OSM 建筑轮廓。'],'sources':['P0_PLATEAU_BUILDINGS_2025','OSM_20261013','ESTAT_2020']},
 {'id':'02_connections','title':{'en':'Streets and rail','zh':'街道与铁路','ja':'街路と鉄道'},'subtitle':'CONNECTIONS  /  连接关系','body':['Kanda Station','神田駅','','Major roads / local streets / rail','主要道路、街巷与铁路','','Recorded route geometry','地图记录的线路几何'],'note':['OSM road classes describe mapped routes.','道路等级按 OSM 标签；未计算步行可达时间。'],'sources':['OSM_20261013','P1_PLATEAU_RELATED','ESTAT_2020']},
 {'id':'03_building_use','title':{'en':'Uses within the blocks','zh':'街区中的建筑用途','ja':'街区の建物用途'},'subtitle':'BUILDING USE  /  建筑用途','body':['2021 survey · 2025 model','2021 年调查 · 2025 年模型','','250 known uses in the core','核心区 250 个对象用途已知','27 unknown uses to check','27 个对象待核查'],'note':['Building-level use. Colors: MLIT survey guide, 2023, p.45.','用途来自建筑属性；不是首层店铺调查。'],'sources':['P0_PLATEAU_BUILDINGS_2025','OSM_20261013','ESTAT_2020']},
 {'id':'04_building_height','title':{'en':'The height of the city','zh':'街区的建筑高度','ja':'街区の建物高さ'},'subtitle':'BUILDING HEIGHT  /  建筑高度','body':['Height in meters','建筑高度 · 米','','Source measured height','PLATEAU measuredHeight 字段','Pale outlines: proxy height','浅色轮廓：代理高度'],'note':['Core: 261 source heights and 16 proxy heights. Pale background: OSM.','核心区 261 个源高度、16 个代理高度；浅灰背景为 OSM。'],'sources':['P0_PLATEAU_BUILDINGS_2025','OSM_20261013','ESTAT_2020']},
 {'id':'05_land_use','title':{'en':'Land use on the ground','zh':'现状土地利用','ja':'現況の土地利用'},'subtitle':'LAND USE  /  2021 年调查','body':['2021 land-use survey','2021 年土地利用调查','','Official source classes','保留官方源分类','Colors: MLIT survey guide','配色参考国交省基础调查要领'],'note':['Survey land use. MLIT colors, 2023, p.26; categories matched by meaning.','现状用地类别与法定用途地域分开编排。'],'sources':['P0_PLATEAU_LANDUSE','OSM_20261013','ESTAT_2020']},
 {'id':'06_planning_zones','title':{'en':'The planning framework','zh':'规划条件','ja':'都市計画の条件'},'subtitle':'PLANNING ZONES  /  用途地域','body':['Commercial zone','商業地域','','Floor-area ratio (FAR)','容积率：楼面面积与用地面积之比','','FY2025 reference GIS','2025 年度参考 GIS'],'note':['Reference polygons; parcel conditions need ward-map review.','参考图层；地块条件需结合区正式图则核对。'],'sources':['P0_MLIT_PLANNING_FY2025','OSM_20261013','ESTAT_2020']},
 {'id':'07_green_water','title':{'en':'Green, water and fieldwork','zh':'绿化、水系与现场补查','ja':'緑・水と現地確認'},'subtitle':'GREEN & WATER  /  绿化与水系','body':['Tree inventory: 2020 / 2024','单株调查 2020 · 路线记录 2024','','Core: 7 tree-route records','核心区相交 7 条树木路线','Core tree points: no coverage','核心区缺单株点位资料'],'note':['Route records do not locate individual trees.','路线树数不等于裁剪范围内树数；树位需现场补查。'],'sources':['P0_TOKYO_TREE_POINTS','P0_TOKYO_TREE_ROUTES','P0_TOKYO_PARKS','OSM_20261013','ESTAT_2020']}
]


def make_plate(index, raw, layers, output):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.path import Path as MPath
 from matplotlib.patches import PathPatch,Rectangle,Polygon
 from matplotlib.font_manager import FontProperties
 from matplotlib import patheffects
 plt.rcParams.update({'savefig.facecolor':PAPER})
 serif=FontProperties(fname='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')
 cjk=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc')
 sans=FontProperties(fname='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
 fig=plt.figure(figsize=(16,12),dpi=100,facecolor=PAPER)
 ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1600);ax.set_ylim(1200,0);ax.axis('off')
 plate=PLATES[index];MX,MY=62,180;S=.94
 def text(x,y,s,size=14,color=INK,font=None,**kw):
  return ax.text(x,y,s,fontsize=size*.72,color=color,fontproperties=font or (cjk if any(ord(z)>255 for z in s) else sans),va='top',**kw)
 def draw(g,face='none',edge='none',lw=.5,alpha=1,z=1,dash=None,hatch=None):
  g=xy(g);parts=list(g.geoms) if hasattr(g,'geoms') else [g]
  for q in parts:
   if q.geom_type=='Polygon':
    q=orient(q,sign=-1);verts=[];codes=[]
    for ring in [q.exterior]+list(q.interiors):
     coords=list(ring.coords);verts.extend([(MX+x*S,MY+y*S) for x,y in coords]);codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(coords)-2)+[MPath.CLOSEPOLY])
    patch=PathPatch(MPath(verts,codes),facecolor=face,edgecolor=edge,linewidth=lw,alpha=alpha,zorder=z,hatch=hatch)
    if dash:patch.set_linestyle((0,dash))
    ax.add_patch(patch)
   elif q.geom_type in ['LineString','LinearRing']:
    coords=list(q.coords);line,=ax.plot([MX+x[0]*S for x in coords],[MY+x[1]*S for x in coords],color=edge,lw=lw,alpha=alpha,zorder=z,solid_capstyle='round')
    if dash:line.set_dashes(dash)
   elif q.geom_type=='Point':ax.plot(MX+q.x*S,MY+q.y*S,'o',ms=2.5,color=edge if edge!='none' else face,zorder=z)
 def layer(k,**style):
  for _,g in raw[k]:draw(g,**style)
 # Map ground and geometries, all from projected source coordinates.
 ax.add_patch(Rectangle((MX,MY),W*S,H*S,facecolor='#f0eee8',edgecolor='none'))
 layer('water',face=WATER,edge='#9fbfc7',lw=.3)
 layer('osm_buildings',face='#dcdad3',edge='#bdbcb7',lw=.18)
 layer('roads',edge='#f7f5ef',lw=1.3)
 if index in [4,5,6]:
  layer('coverage',face='#fbfaf5',edge='none',alpha=.36)
 if index==0:
  for r,g in raw['buildings']:
   if r['core']:draw(g,face=INK,edge=PAPER,lw=.18,z=4)
 elif index==1:
  layer('roads',edge='#bdb8ad',lw=.55)
  for r,g in raw['roads']:
   kind=r['tag']
   if kind in ['motorway','trunk','primary']:draw(g,edge=BRICK,lw=2.4,z=3)
   elif kind in ['secondary','tertiary']:draw(g,edge=OCHRE,lw=1.4,z=3)
   elif kind in ['pedestrian','footway','path']:draw(g,edge=TEAL,lw=.65,z=3)
 elif index==2:
  for (r,g),a in zip(raw['buildings'],layers['buildings']):draw(g,face=USE[a['use']][0],edge=PAPER,lw=.18,z=4)
 elif index==3:
  for (r,g),a in zip(raw['buildings'],layers['buildings']):draw(g,face=HEIGHTS[a['heightBand']][0],edge='#8d8981' if a['heightBand']==5 else PAPER,lw=.2,z=4)
 elif index==4:
  for (r,g),a in zip(raw['land_use'],layers['land_use']):draw(g,face=LAND.get(a['category'],('#ccc',{}))[0],edge=('#FF0000' if a['category'] in ['222','223'] else '#555555') if a['pattern'] else PAPER,lw=.2,z=3,hatch={'parking':'///','outdoor':'\\\\','unused':'||'}.get(a['pattern']))
  layer('osm_buildings',face='none',edge='#706d66',lw=.13,alpha=.4,z=4)
 elif index==5:
  fars=sorted(set(a['far'] for a in layers['zones']))
  far_colors={600:'#ead7de',700:'#dcbdce',800:'#cea3be',900:'#b77fa4',1000:'#995b8c',1200:'#7c4378',1300:'#63305e'}
  for (r,g),a in zip(raw['zones'],layers['zones']):draw(g,face=far_colors.get(a['far'],'#c6a4ba'),edge='#9a728e',lw=.7,z=3)
  layer('osm_buildings',face='none',edge='#5c5659',lw=.15,alpha=.4,z=4)
 elif index==6:
  layer('parks',face='#8eac8e',edge='#577d62',lw=.7,z=4)
  layer('tree_routes',edge='#568f73',lw=1.4,z=5,dash=[3,2])
  layer('trees',face='#446a55',edge='#446a55',z=6)
 layer('rail',edge='#66666a',lw=.75,alpha=.72,z=5)
 layer('rail',edge=PAPER,lw=.25,alpha=.8,z=6,dash=[2.5,3])
 if index in [4,5,6]:layer('coverage',face='none',edge='#9c9990',lw=.6,z=8,dash=[2,3])
 layer('core',face='none',edge=PAPER,lw=3.5,z=9)
 layer('core',face='none',edge=PURPLE,lw=1.6,z=10)
 # Station labels are positioned at official source points; route duplicate records consolidate for display.
 seen=set()
 for (r,g),a in zip(raw['stations'],layers['stations']):
  name=a['name'];pt=g.representative_point();p=(pt.x-EXTENT[0],EXTENT[3]-pt.y)
  if name in seen or name not in ['神田駅','淡路町駅','新日本橋駅']:continue
  if p[0]<30 or p[0]>W-120 or p[1]<25 or p[1]>H-20:continue
  seen.add(name);x,y=MX+p[0]*S,MY+p[1]*S
  ax.plot(x,y,'s',ms=4.8,mfc=PAPER,mec=INK,mew=.9,zorder=12)
  en={'神田駅':'Kanda','淡路町駅':'Awajicho','新日本橋駅':'Shin-Nihombashi'}[name]
  t=text(x+10,y-5,en+' / '+name,13,zorder=13);t.set_path_effects([patheffects.withStroke(linewidth=3,foreground=PAPER)])
 # Title, editorial rail, map frame, north arrow and scale.
 text(62,37,'KAJICHO  /  鍛冶町',16,color=PURPLE)
 text(62,70,plate['title']['en'],44,font=serif)
 text(64,128,plate['subtitle'],15,color='#6c6761')
 text(1445,40,f'{index+1:02d}',54,font=serif,color=PURPLE)
 ax.plot([62,1538],[160,160],color='#bcb6a9',lw=.65)
 ax.add_patch(Rectangle((MX,MY),W*S,H*S,fill=False,edgecolor='#c3bfb5',lw=.5,zorder=20))
 nx,ny=MX+W*S-32,MY+35
 ax.add_patch(Polygon([(nx,ny-13),(nx-5,ny+8),(nx,ny+3),(nx+5,ny+8)],closed=True,facecolor=INK,zorder=21));text(nx-4,ny-31,'N',12)
 sx,sy=MX+22,MY+H*S-28
 ax.add_patch(Rectangle((sx-10,sy-23),(270*S),42,facecolor=PAPER,edgecolor='none',alpha=.9,zorder=20))
 for j in range(2):ax.add_patch(Rectangle((sx+j*100*S,sy),100*S,4,facecolor=INK if j==0 else PAPER,edgecolor=INK,lw=.5,zorder=21))
 for j,label in enumerate(['0','100','200 m']):text(sx+j*100*S,sy+8,label,10,zorder=21)
 # Right margin is reserved for captions and the legend.
 X=1142;text(X,188,plate['title']['zh'],25,font=cjk)
 y=236
 for s in plate['body']:
  text(X,y,s,14 if s else 5,color='#615d57');y+=24 if s else 13
 legends=[]
 if index==0:legends=[(INK,{'en':'Core model buildings','zh':'核心区建筑模型'}),(GREY,{'en':'Context footprints','zh':'背景建筑轮廓'})]
 if index==1:legends=[(BRICK,{'en':'Major roads','zh':'主要道路'}),(OCHRE,{'en':'Secondary / local routes','zh':'次干路与地方道路'}),(TEAL,{'en':'Mapped pedestrian paths','zh':'步行路径记录'}),('#66666a',{'en':'Rail','zh':'铁路'})]
 if index==2:legends=list(USE.values())
 if index==3:legends=HEIGHTS
 if index==4:legends=[v for k,v in LAND.items() if k in set(x['category'] for x in layers['land_use'])]
 if index==5:legends=[(far_colors.get(v,'#c6a4ba'),{'en':f'FAR {v:g}%','zh':f'容积率 {v:g}%'}) for v in fars]
 if index==6:legends=[('#8eac8e',{'en':'Park inventory','zh':'公园范围记录'}),('#568f73',{'en':'Tree-route records','zh':'树木路线记录'}),('#446a55',{'en':'Tree point records','zh':'单株树木记录'}),(WATER,{'en':'Water','zh':'水域'})]
 y=max(y+22,460)
 for color,label in legends:
  legend_hatch={'Outdoor parking':'///','Other outdoor use':'\\\\','Unused land':'||'}.get(label['en']) if index==4 else None
  legend_edge=('#555555' if label['en']=='Unused land' else '#FF0000') if legend_hatch else '#aaa59b'
  ax.add_patch(Rectangle((X,y+3),15,12,facecolor=color,edgecolor=legend_edge,lw=.25,hatch=legend_hatch));text(X+28,y,label['en'],13);text(X+28,y+(15 if index==2 else 19),label.get('zh',''),11 if index==2 else 12,color='#6c6761');y+=(32 if index==2 else 42 if index==4 else 45)
 y=max(y+10,925)
 ax.plot([X,X+18],[y+7,y+7],color=PURPLE,lw=1.7);text(X+28,y,'Kajicho 1 & 2 / 重点区',12);y+=26
 if index in [4,5,6]:
  ax.plot([X,X+18],[y+7,y+7],color='#8d887f',lw=.7,ls=':');text(X+28,y,'Source data window / 数据范围',12)
 # Footer, at normal reading size in the high-resolution PNG.
 ax.plot([62,1538],[1065,1065],color='#bcb6a9',lw=.65)
 text(62,1081,plate['note'][0],13)
 text(62,1104,plate['note'][1],13)
 text(62,1140,'Sources: PLATEAU / Tokyo / MLIT · e-Stat · © OpenStreetMap contributors',10,color='#716c64')
 text(62,1159,'EPSG:6677 · 1,100 × 900 m view · North up · Data / source years vary; see map_manifest.json',10,color='#716c64')
 text(1375,1140,'URBAN DESIGN',11,color=PURPLE);text(1375,1162,'15 OCT 2026',11)
 # Test plate layout dimensions, save a high-resolution PNG.
 stem=output/'maps'/plate['id'];fig.savefig(str(stem)+'.png',dpi=200)
 from PIL import Image
 preview=output/'maps'/'previews';preview.mkdir(exist_ok=True)
 im=Image.open(str(stem)+'.png').convert('RGB');im.thumbnail((1200,900));im.save(preview/(plate['id']+'.jpg'),quality=87,optimize=True)
 if index==0:
  from matplotlib.transforms import Bbox
  crop=Bbox.from_extents(MX/100,(1200-MY-H*S)/100,(MX+W*S)/100,(1200-MY)/100)
  fig.savefig(output/'maps'/'01_figure_ground_map.png',bbox_inches=crop,pad_inches=0,dpi=200)
  im=Image.open(output/'maps'/'01_figure_ground_map.png').convert('RGB');im.thumbnail((1600,1400));im.save(preview/'01_figure_ground_map.jpg',quality=88,optimize=True)
 plt.close(fig)
 return {'id':plate['id'],'png':str(stem.name)+'.png','canvas_px':[3200,2400],'preview':'previews/'+plate['id']+'.jpg','legend':[{'color':c,'label':l} for c,l in legends]}


def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
 started=datetime.now(timezone.utc).isoformat();a.output.mkdir(parents=True,exist_ok=True)
 for d in ['maps','mapping_data']:(a.output/d).mkdir(exist_ok=True)
 layers,raw,counts,sources,geo=build(a.input)
 atlas={'schema_version':1,'crs':'EPSG:6677','extent':EXTENT,'viewBox':'0 0 1100 900','width':W,'height':H,'coordinate_note':'x=E-extent[0],y=extent[3]-N; coordinates in meters. Paths simplify at 0.12 m.','layers':layers,'plates':PLATES,'sources':sources,'counts':counts,'palette':{'paper':PAPER,'ink':INK,'accent':PURPLE,'use':{k:{'color':v[0],'label':v[1]} for k,v in USE.items()},'land':{k:{'color':v[0],'label':v[1]} for k,v in LAND.items()},'height':[{'color':c,'label':l} for c,l in HEIGHTS]},'coverage_note':{'en':'The dashed window marks land-use, planning and green data coverage. Building records have a separate acquisition extent. Pale context footprints are OSM.','zh':'虚线表示土地利用、规划与绿化图层的数据范围。建筑属性另有采集范围；浅灰背景为 OSM 建筑轮廓。','ja':'破線は土地利用・計画・緑のデータ範囲。建物属性の取得範囲は別。薄灰色の建物は OSM。'}}
 # Save early data to support independent front-end integration while PNG plates render.
 data=a.output/'mapping_data';(data/'atlas.json').write_text(json.dumps(atlas,ensure_ascii=False,separators=(',',':')))
 (data/'atlas.geojson').write_text(json.dumps(geo,ensure_ascii=False,separators=(',',':')))
 print(json.dumps({'stage':'data_ready','counts':counts,'pid':os.getpid()}),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=min(7,a.workers)) as pool:
  futures=[pool.submit(make_plate,i,raw,layers,a.output) for i in range(len(PLATES))]
  rendered=[f.result() for f in futures]
 for r in rendered:
  plate=next(x for x in atlas['plates'] if x['id']==r['id']);plate.update(r)
 (data/'atlas.json').write_text(json.dumps(atlas,ensure_ascii=False,separators=(',',':')))
 manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'started_utc':started,'host':platform.node(),'pid':os.getpid(),'python':sys.version,'libraries':{'shapely':shapely.__version__,'pyproj':pyproj.__version__,'matplotlib':__import__('matplotlib').__version__,'pillow':__import__('PIL').__version__},'environment':'Existing read-only system Python plus established user-site GIS libraries; isolated input/output run directory; OMP/BLAS threads=1' ,'workers':min(7,a.workers),'crs':'EPSG:6677','extent':EXTENT,'north_up':True,'source_window_note':atlas['coverage_note'],'counts':counts,'sources':sources,'plates':atlas['plates'],'input_files':[{'name':x.name,'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in [a.input/'baseline.gpkg',a.input/'common.gpkg',a.input/'sources.json']],'processing':['Read consistent SQLite snapshots from two existing GeoPackages.','Clip to one 1100 × 900 m north-up EPSG:6677 extent.','Keep PLATEAU building objects separate from OSM context footprints.','Keep 277 existing core model IDs.','Group source building and land-use labels for display; retain exact source labels.','Display proxy heights separately from measuredHeight fields.','Retain source data coverage boundary.','Display legal planning GIS separately from observed 2021 land use.','Create 3200 × 2400 PNG plates; GeoJSON in EPSG:4326; atlas paths in map-view meters.'],'color_note':'Paper, ink and Edo-purple HEX are studio screen approximations inspired by Chiyoda official sign manual. Building-use RGB follows MLIT 2023 p45 by source meaning. Land-use RGB follows MLIT 2023 p26 with a semantic crosswalk; outdoor and unused categories use hatch adaptations. FAR and height colors are studio palettes.','classification_color_source':'https://www.mlit.go.jp/toshi/tosiko/content/001617949.pdf','brand_source':'https://www.city.chiyoda.lg.jp/documents/4204/designmanual-3.pdf#page=5','no_new_cfd':True}
 (data/'map_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(json.dumps({'stage':'complete','plates':rendered,'counts':counts}),flush=True)
if __name__=='__main__':main()
