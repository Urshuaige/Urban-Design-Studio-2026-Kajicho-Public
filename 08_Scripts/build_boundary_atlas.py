#!/usr/bin/env python3
"""Rebuild course maps and statistics from registered source outlines.

Run on the selected compute host. Outputs stay on that host and in its shared
repository checkout. Source GeoPackages and historical simulation fields are read
only. Formal map exports are PNG; web previews are JPEG.
"""
import argparse, collections, concurrent.futures, csv, json, math, os, shutil
import sqlite3, statistics, sys
from datetime import datetime, timezone
from pathlib import Path
from shapely import wkb
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union, transform
from pyproj import Transformer

PAPER='#f7f5ef'; INK='#36353a'; PRIMARY='#59457f'; SECONDARY='#a46d32'; POSTER='#27abd1'
COLORS={'office':'#be1e32','retail':'#785028','hotel':'#f08cbe','housing':'#f0f0a0','apartments':'#faaaa0','mixed':'#f5f05a','workhome':'#b48cbe','government':'#0a78be','education':'#faa032','logistics':'#283c8c','industry':'#00643c','utilities':'#505050','other':'#828282','unknown':'#bebebe'}
USES={'業務施設':'office','商業施設':'retail','宿泊施設':'hotel','住宅':'housing','共同住宅':'apartments','店舗等併用住宅':'mixed','作業所併用住宅':'workhome','官公庁施設':'government','文教厚生施設':'education','運輸倉庫施設':'logistics','工場':'industry','供給処理施設':'utilities','その他':'other'}
LAND={'211':('Housing / mixed','#ffff00'),'212':('Commercial','#e65050'),'213':('Industry','#1e46ff'),'214':('Public facilities','#c800dc'),'215':('Road','#ffffff'),'216':('Rail / logistics','#8c8c8c'),'217':('Park / open space','#c8ffc8'),'204':('Water','#78dcff'),'222':('Outdoor parking','#e1d7c6'),'223':('Other outdoor use','#ddd7c9'),'224':('Unused land','#eee6d3')}
SCOPE_NAMES={'primary_brief':{'en':'Kajicho primary area','zh':'鍛冶町重点区','ja':'鍛冶町重点区域'},'secondary_brief':{'en':'Kanda–Nihonbashi wider area','zh':'神田—日本桥外围区','ja':'神田・日本橋の周辺区域'},'poster_blue':{'en':'2026 poster study area','zh':'2026 海报研究区','ja':'2026年ポスターの対象区域'}}
THEMES=[('01_figure_ground','Building footprints','建筑与开放空间'),('02_connections','Streets and rail','道路与铁路'),('03_building_use','Building use','建筑用途'),('04_building_height','Building height','建筑高度'),('05_land_use','Observed land use','现状土地利用'),('06_planning_zones','Planning zones','规划用途地域'),('07_green_water','Green and water','绿化与水系'),('08_flood','Flood source overlap','洪水源图层叠加')]

def read(path):
    c=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    out={}
    for tab,col in c.execute('select table_name,column_name from gpkg_geometry_columns').fetchall():
        rows=[]
        for row in c.execute('select * from "'+tab+'"'):
            r=dict(row);b=r.pop(col,None)
            if not b:continue
            b=bytes(b);size={0:0,1:32,2:48,3:48,4:64}[(b[3]>>1)&7]
            g=wkb.loads(b[8+size:])
            if not g.is_valid:g=g.buffer(0)
            if not g.is_empty:rows.append((r,g))
        out[tab]=rows
    c.close();return out

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def csvout(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def number(x):
    try:
        y=float(x);return y if math.isfinite(y) and y>=0 else None
    except (ValueError,TypeError):return None

def source_boundaries(path):
    d=json.loads(path.read_text());features=d.get('features',[])
    rows={}
    for f in features:
        p=f.get('properties',{});sid=p.get('id') or p.get('scope') or f.get('id')
        g=shape(f['geometry']);rows[sid]=(p,g)
    assert set(SCOPE_NAMES).issubset(rows),list(rows)
    assert all(g.is_valid and g.area>0 for p,g in rows.values())
    return d,rows

def select_full_buildings(rows, scope):
    """Select unchanged source footprints completely covered by the fixed outline."""
    return [(record, geometry) for record, geometry in rows if scope.covers(geometry)]

def analyze(raw,boundaries,registration,out):
    summaries={};tables=collections.defaultdict(list);members={}
    for sid in SCOPE_NAMES:
        props,scope=boundaries[sid];area=scope.area
        delta=float(props.get('registration',{}).get('uncertainty_m',15))
        selected=select_full_buildings(raw['buildings'],scope)
        assert all(scope.covers(g) for r,g in selected)
        overlap=[(r,g,g) for r,g in selected]
        footprint=unary_union([gg for r,g,gg in overlap]);groups=collections.defaultdict(list)
        for r,g in selected:groups[USES.get(r.get('usage'),'unknown')].append((r,g))
        height=[number(r.get('height_m')) for r,g in selected if 'measured' in str(r.get('height_source','')).lower()]
        height=[h for h in height if h is not None and h>0]
        for r,g in selected:
            rr={k:v for k,v in r.items() if k!='source_attrs_json'};rr.update(scope=sid,intersection_m2=g.area,intersection_fraction=1.0,boundary_crossing=not scope.covers(g),use_group=USES.get(r.get('usage'),'unknown'))
            rr['floor_proxy_allocated_m2']=(number(r.get('floor_proxy_m2')) or 0)*rr['intersection_fraction'];tables['buildings'].append(rr)
        totalfloor=sum(number(r.get('floor_proxy_m2')) or 0 for r,g in selected)
        for key,rows in groups.items():
            f=sum(number(r.get('floor_proxy_m2')) or 0 for r,g in rows)
            tables['building_use'].append({'scope':sid,'use':key,'models':len(rows),'count_share_pct':100*len(rows)/len(selected) if selected else None,'full_selected_model_floor_proxy_m2':f,'floor_proxy_share_pct':100*f/totalfloor if totalfloor else None})
        lu=collections.defaultdict(list)
        for r,g in raw.get('land_use',[]):
            if not g.intersects(scope):continue
            clip=g.intersection(scope)
            if clip.area>.01:lu[str(r.get('class'))].append(clip)
        lug={k:unary_union(gs) for k,gs in lu.items()};luunion=unary_union(list(lug.values()))
        for k,g in lug.items():tables['land_use'].append({'scope':sid,'class':k,'label':LAND.get(k,(k,''))[0],'area_m2':g.area,'scope_share_pct':100*g.area/area})
        zones=collections.defaultdict(list)
        for r,g in raw.get('zones',[]):
            if g.intersects(scope):zones[(r.get('zone_name'),r.get('FAR'),r.get('BCR'))].append(g.intersection(scope))
        for (name,far,bcr),gs in zones.items():tables['planning_zones'].append({'scope':sid,'zone':name,'FAR_pct':far,'BCR_pct':bcr,'intersection_area_m2':unary_union(gs).area})
        for r,g in raw.get('census',[]):
            ov=g.intersection(scope).area
            if ov>.01:
                rr=dict(r);rr.update(scope=sid,scope_overlap_m2=ov,town_overlap_fraction=ov/g.area,allocation='Full source town total; population is not assigned to the intersected fraction.');tables['census_intersections'].append(rr)
        floodgroups=collections.defaultdict(list)
        for r,g in raw.get('flood',[]):
            name=str(r.get('scenario') or r.get('name') or r.get('scenario_name') or r.get('source_member'))
            floodgroups[name].append((r,g))
        floods=[]
        for name,rows in floodgroups.items():
            allg=unary_union([g for r,g in rows]);clipped=scope.intersection(allg);exposed=0
            for r,g in selected:
                ov=g.intersection(allg).area
                if ov>.01:exposed+=1
                tables['flood_buildings'].append({'scope':sid,'scenario':name,'building_id':r.get('asset_id') or r.get('building_id') or r.get('gml_id'),'within_scope_overlap_m2':ov,'status':'recorded_overlap' if ov>.01 else 'no_recorded_overlap','meaning':'Overlap with available source polygons; missing polygon is not a surveyed safe area.'})
            rankgroups=collections.defaultdict(list)
            for r,g in rows:rankgroups[str(r.get('rank','unknown'))].append(g)
            claimed=box(0,0,0,0)
            for rank in sorted(rankgroups,key=lambda x:int(x) if x.isdigit() else -1,reverse=True):
                gg=unary_union(rankgroups[rank]);disjoint=gg.difference(claimed);claimed=unary_union([claimed,gg]);tables['flood_depth_area'].append({'scope':sid,'scenario':name,'rank':rank,'area_m2':scope.intersection(disjoint).area})
            f={'scope':sid,'scenario':name,'source_date':rows[0][0].get('source_date'),'recorded_overlap_m2':clipped.area,'scope_overlap_pct':100*clipped.area/area,'exposed_selected_models':exposed,'source_domain_note':'Available source polygons; no recorded overlap is not zero risk.'};floods.append(f);tables['flood_scenarios'].append(f)
        roadlength=sum(g.intersection(scope).length for r,g in raw.get('roads',[]))
        trees=sum(scope.covers(g) for r,g in raw.get('trees',[]));routes=sum(g.intersection(scope).length>.01 for r,g in raw.get('tree_routes',[]));parks=unary_union([g.intersection(scope) for r,g in raw.get('parks',[]) if g.intersects(scope)])
        inside=scope.buffer(-delta);outside=scope.buffer(delta)
        nlo=len(select_full_buildings(raw['buildings'],inside));nhi=len(select_full_buildings(raw['buildings'],outside))
        summaries[sid]={'name':SCOPE_NAMES[sid],'area_m2':area,'area_ha':area/10000,'selected_models':len(selected),'positive_overlap_models':len(overlap),'boundary_crossing_selected_models':sum(not scope.covers(g) for r,g in selected),'gross_footprint_union_m2':footprint.area,'gross_footprint_coverage_pct':100*footprint.area/area,'models_per_ha':len(selected)/(area/10000),'known_use_models':sum(len(rows) for key,rows in groups.items() if key!='unknown'),'unknown_use_models':len(groups['unknown']),'source_height_models':len(height),'height_proxy_models':len(selected)-len(height),'source_height_median_m':statistics.median(height) if height else None,'full_selected_model_floor_proxy_m2':totalfloor,'land_use_covered_m2':luunion.area,'land_use_coverage_pct':100*luunion.area/area,'land_use_unmapped_m2':scope.difference(luunion).area,'land_use_between_class_overlap_m2':sum(g.area for g in lug.values())-luunion.area,'road_mapped_length_m':roadlength,'tree_point_records':trees,'tree_route_intersections':routes,'park_inventory_union_m2':parks.area,'flood':floods,'boundary_uncertainty_m':delta,'model_membership_sensitivity':{'eroded_count':nlo,'traced_count':len(selected),'buffered_count':nhi,'rule':'Complete footprint covered by boundary eroded/buffered by registration and stroke uncertainty; sensitivity, not a confidence interval.'},'selection_rule':'Complete original source building footprint covered by the fixed outline; exterior and crossing objects are excluded from all building analysis.','source_outline':props}
        members[sid]={r.get('asset_id') or r.get('gml_id') for r,g in selected}
        tables['summary'].append(dict({k:v for k,v in summaries[sid].items() if isinstance(v,(str,int,float)) or v is None},scope=sid))
        for r,g in selected:
            h=number(r.get('height_m'));hb='Proxy / unavailable' if 'measured' not in str(r.get('height_source','')).lower() else '<10 m' if h is not None and h<10 else '10–20 m' if h is not None and h<20 else '20–30 m' if h is not None and h<30 else '30–45 m' if h is not None and h<45 else '≥45 m'
            tables['height_models'].append({'scope':sid,'building_id':r.get('asset_id') or r.get('gml_id'),'height_m':h,'source':r.get('height_source'),'class':hb})
    for name,rows in tables.items():csvout(out/'tables'/(name+'.csv'),rows)
    dump(out/'statistics.json',{'updated_utc':datetime.now(timezone.utc).isoformat(),'crs':'EPSG:6677','scopes':summaries,'rules':{'model_selection':'Complete original source building footprint covered by each fixed registered outline.','building_coverage':'Union of complete selected source footprints; exterior and crossing models contribute no footprint fragments.','floor_proxy':'Complete selected model footprint × source/proxy levels; no clipping or exterior-model allocation.','census_population':'Original full-town totals retained; intersecting fractions are not assigned the full population.','uncertainty':'Area and counts describe a traced reference line; buffered membership is a sensitivity check.','energy':'Actual energy and carbon remain missing. No metered totals are inferred.'}})
    return summaries,tables,members

def draw_geom(ax,g,face='none',edge='none',lw=.3,z=1,alpha=1,ls='-',hatch=None):
    from matplotlib.path import Path as MP
    from matplotlib.patches import PathPatch
    from shapely.geometry.polygon import orient
    if g.is_empty:return
    if hasattr(g,'geoms'):
        for p in g.geoms:draw_geom(ax,p,face,edge,lw,z,alpha,ls,hatch)
    elif g.geom_type=='Polygon':
        g=orient(g,sign=1);vertices=[];codes=[]
        for ring in [g.exterior,*g.interiors]:
            cc=list(ring.coords);vertices.extend(cc);codes.extend([MP.MOVETO]+[MP.LINETO]*(len(cc)-2)+[MP.CLOSEPOLY])
        ax.add_patch(PathPatch(MP(vertices,codes),facecolor=face,edgecolor=edge,linewidth=lw,zorder=z,alpha=alpha,linestyle=ls,hatch=hatch))
    elif g.geom_type in ('LineString','LinearRing'):
        x,y=g.xy;ax.plot(x,y,color=edge,lw=lw,zorder=z,alpha=alpha,linestyle=ls)
    elif g.geom_type=='Point':ax.plot(g.x,g.y,'o',ms=2,color=face if face!='none' else edge,zorder=z,alpha=alpha)

def render(task,raw,boundaries,summaries,out):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    from matplotlib import patheffects
    from PIL import Image
    plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':10,'text.color':INK,'savefig.facecolor':PAPER,'axes.facecolor':'#eeece5'})
    sid,theme=task;overview=sid=='overview';scope=unary_union([boundaries[k][1] for k in SCOPE_NAMES]);pad=100
    x0,y0,x1,y1=scope.bounds;extent=box(x0-pad,y0-pad,x1+pad,y1+pad)
    fig=plt.figure(figsize=(16,12),facecolor=PAPER);ax=fig.add_axes([.045,.17,.72,.68]);ax.set_aspect('equal');ax.set_xlim(extent.bounds[0],extent.bounds[2]);ax.set_ylim(extent.bounds[1],extent.bounds[3]);ax.set_xticks([]);ax.set_yticks([])
    for sp in ax.spines.values():sp.set_color('#c3bfb5');sp.set_linewidth(.5)
    def layer(name,face='none',edge='none',lw=.25,z=1,ls='-',clip=False):
        for r,g in raw.get(name,[]):
            if g.intersects(extent):draw_geom(ax,g.intersection(scope) if clip else g,face,edge,lw,z,ls=ls)
    layer('water','#a8c8d1','#90b4c0',.25,1);layer('osm_buildings','#dcdad3','#bdbcb7',.12,5);layer('buildings','#dcdad3','#bdbcb7',.12,5)
    layer('roads',edge='#faf9f4',lw=1.1,z=3)
    legends=[]
    idx=0 if overview else theme
    if idx in (0,2,3):
        for r,g in raw['buildings']:
            if not scope.covers(g):continue
            gg=g
            color=INK
            if idx==2:color=COLORS[USES.get(r.get('usage'),'unknown')]
            if idx==3:
                h=number(r.get('height_m'));color='#e3ded3' if 'measured' not in str(r.get('height_source','')).lower() else ['#dedbd3','#b8cac5','#82aaa1','#508179','#355c59'][0 if h is None or h<10 else 1 if h<20 else 2 if h<30 else 3 if h<45 else 4]
            draw_geom(ax,gg,color,PAPER,.1,6)
        if idx==0:legends=[Patch(facecolor=INK,label='PLATEAU model projection'),Patch(facecolor='#dcdad3',label='OSM context footprint')]
        elif idx==2:legends=[Patch(facecolor=c,label=k.replace('workhome','House / workshop')) for k,c in COLORS.items() if any(USES.get(r.get('usage'),'unknown')==k and scope.covers(g) for r,g in raw['buildings'])]
        else:legends=[Patch(facecolor=c,label=t) for c,t in zip(['#dedbd3','#b8cac5','#82aaa1','#508179','#355c59','#e3ded3'],['<10 m','10–20 m','20–30 m','30–45 m','≥45 m','Proxy / unavailable'])]
    if idx==1:
        for r,g in raw.get('roads',[]):
            if not g.intersects(scope):continue
            kind=r.get('tag');major=kind in ('motorway','trunk','primary');middle=kind in ('secondary','tertiary')
            draw_geom(ax,g.intersection(scope),edge='#b97667' if major else '#cfb56d' if middle else '#719a94' if kind in ('footway','pedestrian','path') else '#aaa59b',lw=1.3 if major else .8 if middle else .4,z=4)
        legends=[Line2D([0],[0],color=c,lw=2,label=t) for c,t in [('#b97667','Major mapped road'),('#cfb56d','Secondary / local road'),('#719a94','Mapped pedestrian path')]]
    if idx==4:
        for r,g in raw.get('land_use',[]):
            if g.intersects(scope):
                k=str(r.get('class'));draw_geom(ax,g.intersection(scope),LAND.get(k,(k,'#bfbdb7'))[1],PAPER,.1,4,hatch='///' if k in ('222','223','224') else None)
        legends=[Patch(facecolor=LAND.get(k,(k,'#bfbdb7'))[1],label=LAND.get(k,(k,''))[0]) for k in dict.fromkeys(str(r.get('class')) for r,g in raw.get('land_use',[]) if g.intersects(scope))]
    if idx==5:
        fars=sorted({float(r['FAR']) for r,g in raw.get('zones',[]) if r.get('FAR') and g.intersects(scope)});palette=plt.get_cmap('PuRd')
        for r,g in raw.get('zones',[]):
            if g.intersects(scope):draw_geom(ax,g.intersection(scope),palette(.15+.7*fars.index(float(r['FAR']))/max(1,len(fars)-1)) if r.get('FAR') else '#bbb',PAPER,.4,4)
        legends=[Patch(facecolor=palette(.15+.7*i/max(1,len(fars)-1)),label=f'FAR {far:g}%') for i,far in enumerate(fars)]
    if idx==6:
        layer('parks','#8eac8e','#577d62',.5,4,clip=True);layer('tree_routes',edge='#568f73',lw=1.2,z=5,ls='--',clip=True);layer('trees','#446a55','#446a55',z=6,clip=True)
        legends=[Patch(facecolor='#8eac8e',label='Park inventory'),Line2D([0],[0],color='#568f73',ls='--',label='Tree-route record'),Line2D([0],[0],marker='o',color='#446a55',ls='',label='Individual tree record'),Patch(facecolor='#a8c8d1',label='Water')]
    if idx==7:
        rows=[(r,g) for r,g in raw.get('flood',[]) if r.get('source_date')=='2018-03-30' and '神田' in str(r.get('scenario') or r.get('name') or '')]
        for r,g in rows:
            if g.intersects(scope):draw_geom(ax,g.intersection(scope),'#73a7bf','#f7f5ef',.1,4,alpha=.75)
        legends=[Patch(facecolor='#73a7bf',label='Kanda basin 2018 / L2'),Patch(facecolor='#eeece5',label='No positive polygon overlap')]
    layer('rail',edge='#77767a',lw=.65,z=6)
    for key,(p,g) in boundaries.items():
        if key not in SCOPE_NAMES:continue
        col={'primary_brief':PRIMARY,'secondary_brief':SECONDARY,'poster_blue':POSTER}[key];ls='--' if key=='secondary_brief' else '-'
        draw_geom(ax,g,edge=PAPER,lw=3,z=9,ls=ls);draw_geom(ax,g,edge=col,lw=1.6,z=10,ls=ls)
    if overview and theme==1 and 'census_legacy' in boundaries:draw_geom(ax,boundaries['census_legacy'][1],edge='#b13a48',lw=1.2,z=11,ls=':')
    seen=set()
    for r,g in raw.get('stations',[]):
        pt=g.representative_point();name=r.get('name','');line=r.get('line','');key=(name,'Ginza' if '銀座' in line else 'JR' if any(t in line for t in ('中央','東北','総武','山手')) else line,round(pt.x/5),round(pt.y/5))
        if key in seen or not extent.buffer(-20).covers(pt):continue
        seen.add(key)
        if name not in ('神田駅','新日本橋駅','三越前駅','小伝馬町駅','淡路町駅','岩本町駅') and not overview:continue
        label={'神田駅':'Kanda','新日本橋駅':'Shin-Nihonbashi','三越前駅':'Mitsukoshimae','小伝馬町駅':'Kodemmacho','淡路町駅':'Awajicho','岩本町駅':'Iwamotocho'}.get(name,name.replace('駅',''))+(' · Ginza' if '銀座' in line else ' · JR' if key[1]=='JR' else '')
        ax.plot(pt.x,pt.y,'s',ms=4,mfc=PAPER,mec=INK,mew=.7,zorder=12)
        yshift=14 if '銀座' in line else -17 if name=='神田駅' else 10
        tx=ax.annotate(label,(pt.x,pt.y),xytext=(7,yshift),textcoords='offset points',fontsize=8,zorder=13);tx.set_path_effects([patheffects.withStroke(linewidth=2.8,foreground=PAPER)])
    width=extent.bounds[2]-extent.bounds[0];scale=100 if width<1000 else 250 if width<2200 else 500
    sx=extent.bounds[0]+width*.055;sy=extent.bounds[1]+(extent.bounds[3]-extent.bounds[1])*.055
    ax.plot([sx,sx+scale],[sy,sy],color=INK,lw=3,zorder=20);ax.text(sx,sy+width*.015,f'0      {scale} m',fontsize=9,zorder=20,bbox=dict(facecolor=PAPER,edgecolor='none',alpha=.9,pad=2))
    ax.annotate('N',xy=(.95,.95),xytext=(.95,.85),xycoords='axes fraction',ha='center',arrowprops={'arrowstyle':'-|>','color':INK},fontsize=11,zorder=22)
    title='Course areas together' if overview and theme==0 else 'Primary edge comparison' if overview else THEMES[theme][1]
    subtitle='课程范围总图' if overview and theme==0 else '重点区边线对照' if overview else THEMES[theme][2]
    fig.text(.045,.956,'KANDA–NIHONBASHI / 神田—日本橋',fontsize=12,color=PRIMARY)
    fig.text(.045,.907,title,fontsize=27);fig.text(.045,.866,subtitle,fontsize=15)
    y=.82
    fig.text(.79,y,'AREA / MODELS',fontsize=11,weight='bold');y-=.035
    scope_metrics=[]
    for key,label in [('primary_brief','Kajicho primary'),('secondary_brief','Brief wider (approx.)'),('poster_blue','Poster blue')]:
        sm=summaries[key]
        text=f"{label}  {sm['area_ha']:.2f} ha / {sm['selected_models']:,}"
        fig.text(.79,y,text,fontsize=9.5);y-=.027
        if idx==0:metric_label='Footprint union';value=sm['gross_footprint_coverage_pct'];unit='%';detail=f'{value:.2f}% footprint union'
        elif idx==1:metric_label='Mapped road length';value=sm['road_mapped_length_m']/1000;unit='km';detail=f'{value:.2f} km mapped roads'
        elif idx==2:metric_label='Known building use';value=sm['known_use_models'];unit='models';detail=f"{value:,} known use / {sm['unknown_use_models']:,} unknown"
        elif idx==3:metric_label='Source height median';value=sm['source_height_median_m'];unit='m';detail=f"{value:.1f} m source median / {sm['height_proxy_models']:,} proxies" if value is not None else f"No source height / {sm['height_proxy_models']:,} proxies"
        elif idx==4:metric_label='Land-use coverage';value=sm['land_use_coverage_pct'];unit='%';detail=f'{value:.2f}% land-use coverage'
        elif idx==5:
            value=unary_union([g.intersection(boundaries[key][1]) for r,g in raw.get('zones',[]) if g.intersects(boundaries[key][1])]).area/sm['area_m2']*100
            metric_label='Zone source coverage';unit='%';detail=f'{value:.2f}% zone source coverage'
        elif idx==6:metric_label='Tree point records';value=sm['tree_point_records'];unit='records';detail=f"{value:,} tree points / {sm['park_inventory_union_m2']/10000:.2f} ha parks"
        else:
            f=next(f for f in sm['flood'] if f['source_date']=='2018-03-30' and '神田' in f['scenario'])
            metric_label='Kanda 2018 L2 overlap';value=f['scope_overlap_pct'];unit='%';detail=f"{value:.2f}% overlap / {f['exposed_selected_models']:,} models"
        fig.text(.79,y,detail,fontsize=8.5,color='#6c6761');y-=.046
        scope_metrics.append({'scope':key,'area_ha':sm['area_ha'],'selected_models':sm['selected_models'],'metric':metric_label,'value':value,'unit':unit,'printed_text':text+'; '+detail})
    y-=.01
    boundary_handles=[Line2D([0],[0],color=col,ls=ls,lw=1.6,label=label) for col,ls,label in [(PRIMARY,'-','Brief: primary'),(SECONDARY,'--','Brief: wider (approx.)'),(POSTER,'-','2026 poster: blue')]]
    if overview and theme==1:boundary_handles.append(Line2D([0],[0],color='#b13a48',ls=':',label='2020 Census: legacy'))
    fig.legend(handles=boundary_handles+legends,loc='upper left',bbox_to_anchor=(.78,y),frameon=False,fontsize=9,labelspacing=.9,handlelength=2.5)
    notes=['Official source outlines registered to street junctions.','图线按官方图像配准；原图虚线保留约略范围含义。','JR Kanda and Ginza Line Kanda keep separate source points.','Buildings: PLATEAU LOD1 · roads: © OpenStreetMap contributors.','Observed land use and legal planning zones keep separate source roles.']
    if idx==7:notes[4]='Flood: available source overlap; no polygon overlap does not establish safety.'
    if idx==6:notes[4]='Tree-route counts cover original routes; point absence is a source gap.'
    fig.text(.045,.115,'\n'.join(notes[:3]),fontsize=10,linespacing=1.6)
    fig.text(.045,.043,'\n'.join(notes[3:])+ '\nEPSG:6677 · North up · Source and survey years: source_manifest.json · 17 OCT 2026',fontsize=8.5,linespacing=1.5,color='#6c6761')
    filename='course_00_overview' if overview else 'course_'+THEMES[theme][0]
    file=out/'maps'/(filename+'.png');file.parent.mkdir(parents=True,exist_ok=True);fig.savefig(file,dpi=200);plt.close(fig)
    preview=out/'maps/previews'/(filename+'.jpg');preview.parent.mkdir(parents=True,exist_ok=True)
    im=Image.open(file).convert('RGB');im.thumbnail((1400,1050));im.save(preview,quality=90)
    return {'id':filename,'scope':'common_view','kind':'overview' if overview else 'theme','theme':None if overview else THEMES[theme][0],'title':{'en':title,'zh':subtitle,'ja':title},'file':'boundary-atlas/maps/'+file.name,'preview':'boundary-atlas/maps/previews/'+preview.name,'pixels':[3200,2400],'extent_6677':list(extent.bounds),'scope_metrics':scope_metrics}


def build_qgis(asset_path,root,boundaries,members):
    from qgis.core import QgsApplication,QgsVectorLayer,QgsProject,QgsCoordinateReferenceSystem,QgsVectorFileWriter,QgsFeature,QgsField,QgsGeometry,Qgis,QgsFillSymbol,QgsLineSymbol,QgsMarkerSymbol
    from qgis.PyQt.QtCore import QVariant
    app=QgsApplication.instance() or QgsApplication([],False);app.initQgis()
    dest=root/'04_Data/Ready/Course_Boundaries_2026-10-16/Kanda_Nihonbashi_Course.gpkg';dest.parent.mkdir(parents=True,exist_ok=True)
    source_db=sqlite3.connect('file:'+str(asset_path)+'?mode=ro',uri=True)
    target_db=sqlite3.connect(dest)
    source_db.backup(target_db)
    target_db.close();source_db.close()
    project=QgsProject();project.setCrs(QgsCoordinateReferenceSystem('EPSG:6677'));project.setTitle('Kanda–Nihonbashi | Registered course areas 2026-10-16');project.setFilePathStorage(Qgis.FilePathType.Relative)
    for sid,(props,g) in boundaries.items():
        layer=QgsVectorLayer('MultiPolygon?crs=EPSG:6677',sid,'memory');dp=layer.dataProvider();dp.addAttributes([QgsField('scope',QVariant.String),QgsField('source',QVariant.String),QgsField('area_ha',QVariant.Double),QgsField('status',QVariant.String)]);layer.updateFields();f=QgsFeature(layer.fields());qg=QgsGeometry.fromWkt(g.wkt);qg.convertToMultiType();f.setGeometry(qg);f.setAttributes([sid,str(props.get('source','')),g.area/10000,str(props.get('status','Registered raster reference'))]);dp.addFeatures([f])
        opt=QgsVectorFileWriter.SaveVectorOptions();opt.driverName='GPKG';opt.layerName=sid;opt.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteLayer
        result=QgsVectorFileWriter.writeAsVectorFormatV3(layer,str(dest),project.transformContext(),opt);assert result[0]==QgsVectorFileWriter.NoError,result
    con=sqlite3.connect(dest);names=[r[0] for r in con.execute('select table_name from gpkg_geometry_columns')];con.close()
    for name in names:
        layer=QgsVectorLayer(str(dest)+'|layername='+name,name,'ogr');assert layer.isValid(),name
        if name in boundaries:
            color={'primary_brief':PRIMARY,'secondary_brief':SECONDARY,'poster_blue':POSTER,'census_legacy':'#b13a48'}.get(name,'#333');layer.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'0,0,0,0','outline_color':color,'outline_width':'0.6','outline_style':'dash' if name=='secondary_brief' else 'dot' if name=='census_legacy' else 'solid'}))
        elif layer.geometryType()==2:layer.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'#d4d0c7','outline_color':'#ffffff','outline_width':'0.1'}))
        elif layer.geometryType()==1:layer.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':'#8a857d','line_width':'0.25'}))
        else:layer.renderer().setSymbol(QgsMarkerSymbol.createSimple({'color':'#446a55','size':'1.5'}))
        project.addMapLayer(layer)
    # Add explicit membership table; source assets and historical core flags stay unchanged.
    con=sqlite3.connect(dest);con.execute('create table course_membership (scope text,asset_id text,selection_rule text,primary key(scope,asset_id))')
    con.executemany('insert into course_membership values (?,?,?)',[(s,str(i),'representative point within registered outline') for s,ids in members.items() for i in ids]);con.execute("insert into gpkg_contents(table_name,data_type,identifier,description) values ('course_membership','attributes','course_membership','Independent membership for each registered course outline')");con.commit();con.close()
    p=root/'05_QGIS/Projects/Kanda_Nihonbashi_Course_2026-10-16.qgz';p.parent.mkdir(parents=True,exist_ok=True);project.setFileName(str(p));assert project.write(),p
    return dest,p

_RENDER_DATA=None
def render_task(task):
    return render(task,*_RENDER_DATA)

def main():
    p=argparse.ArgumentParser();p.add_argument('--assets',type=Path,required=True);p.add_argument('--boundaries',type=Path,required=True);p.add_argument('--team',type=Path,required=True);p.add_argument('--site',type=Path,required=True);p.add_argument('--workers',type=int,default=8);p.add_argument('--statistics-only',action='store_true',help='Refresh dependent tables and GIS when map geometry/style is unchanged.');a=p.parse_args()
    os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',QT_QPA_PLATFORM='offscreen')
    registration,boundaries=source_boundaries(a.boundaries);raw=read(a.assets)
    legacy=read(a.team/'04_Data/Ready/Public_Baseline_2026-10-14/Kajicho_Public_Baseline.gpkg')['primary_area'][0][1]
    boundaries['census_legacy']=({'id':'census_legacy','source':'2020 Census towns 13101035001/002','status':'Historical statistical unit; comparison only'},legacy)
    out=a.team/'06_Outputs/Boundary_Atlas_2026-10-16';out.mkdir(parents=True,exist_ok=True)
    summaries,tables,members=analyze(raw,boundaries,registration,out)
    primary=boundaries['primary_brief'][1];comparison={'legacy_census_area_ha':legacy.area/10000,'registered_primary_area_ha':primary.area/10000,'intersection_area_m2':legacy.intersection(primary).area,'symmetric_difference_m2':legacy.symmetric_difference(primary).area,'legacy_minus_primary_m2':legacy.difference(primary).area,'primary_minus_legacy_m2':primary.difference(legacy).area,'hausdorff_m':legacy.hausdorff_distance(primary),'new_only_model_ids':sorted(members['primary_brief']-{r.get('asset_id') or r.get('gml_id') for r,g in raw['buildings'] if legacy.covers(g.representative_point())}),'legacy_only_model_ids':sorted({r.get('asset_id') or r.get('gml_id') for r,g in raw['buildings'] if legacy.covers(g.representative_point())}-members['primary_brief']),'interpretation':'Census and course raster are different source definitions. Differences inside registration/stroke uncertainty remain unresolved at parcel scale.'}
    dump(out/'boundary_comparison.json',comparison);dump(out/'registration.json',registration)
    print(json.dumps({'stage':'statistics_complete','scopes':{s:{k:v for k,v in m.items() if k in ('area_ha','selected_models','positive_overlap_models','land_use_coverage_pct')} for s,m in summaries.items()},'layers':{k:len(v) for k,v in raw.items()}}),flush=True)
    tasks=[('overview',0)]+[('common_view',i) for i in range(len(THEMES))]
    if a.statistics_only:
        plates=json.loads((out/'atlas.json').read_text())['plates']
    else:
        global _RENDER_DATA
        _RENDER_DATA=(raw,boundaries,summaries,out)
        with concurrent.futures.ProcessPoolExecutor(max_workers=min(a.workers,len(tasks))) as pool:
            plates=list(pool.map(render_task,tasks))
    manifest=json.loads((a.assets.parent/'Source_Manifest.json').read_text())
    for key in ('runtime','host','pid','inputs','output_gpkg'):manifest.pop(key,None)
    manifest.update(map_export_formats=['PNG'],new_cfd=False,scope_ids=list(SCOPE_NAMES),model_membership_rule='Representative point within registered course outline',source_originals_unchanged=True)
    manifest['source_register']=[]
    register=a.team/'04_Data/Metadata/Data_Register.csv'
    if register.exists():
        for r in csv.DictReader(register.open(encoding='utf-8-sig')):
            if r.get('source_url'):manifest['source_register'].append({k:r.get(k) for k in ('dataset_id','name','source_url','provider','data_year','document_year','website_file_version','download_date','record_unit','crs','units','license')})
    manifest['course_boundary']='Three independent registered official source outlines; raster precision retained.'
    manifest['citygml_source_crs']='EPSG:6697; horizontal EPSG:6668; source axis latitude, longitude, height; derived EPSG:6677'
    dump(out/'source_manifest.json',manifest)
    tr=Transformer.from_crs(6677,4326,always_xy=True).transform
    features=[{'type':'Feature','properties':dict(props,scope=sid),'geometry':mapping(transform(tr,g))} for sid,(props,g) in boundaries.items()]
    for layer,rows in raw.items():
        if layer in ('source_coverage','census'):continue
        for r,g in rows:features.append({'type':'Feature','properties':dict({k:v for k,v in r.items() if k not in ('source_attrs_json','fid')},layer=layer),'geometry':mapping(transform(tr,g.simplify(.12,preserve_topology=True)))})
    (out/'atlas.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':'))+'\n')
    dump(out/'atlas.json',{'schema_version':3,'crs':'EPSG:6677','plates':plates,'scopes':summaries,'boundaries':{'type':'FeatureCollection','features':features[:len(boundaries)]},'map_export_formats':['PNG'],'no_new_cfd':True})
    gpkg,project=build_qgis(a.assets,a.team,boundaries,members)
    siteout=a.site/'dist/boundary-atlas';shutil.copytree(out,siteout,dirs_exist_ok=True)
    print(json.dumps({'stage':'complete','maps':len(plates),'gpkg':str(gpkg),'project':str(project),'site':str(siteout)}),flush=True)

if __name__=='__main__':main()
