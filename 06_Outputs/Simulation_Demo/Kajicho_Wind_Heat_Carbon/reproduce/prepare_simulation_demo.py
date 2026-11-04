"""Build the bounded Kajicho demo inputs; run with the QGIS bundled Python."""
import json, math, struct, sqlite3, os
from pathlib import Path
import numpy as np
from shapely.geometry import shape, Point, box, mapping
from shapely import wkb
from shapely.ops import unary_union
from shapely.affinity import translate
from shapely.prepared import prep

ROOT=Path(__file__).resolve().parents[1]
READY=ROOT/'04_Data/Ready/Simulation_Demo'
SITE=ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon'
OUT=SITE/'dist/data'; OUT.mkdir(parents=True,exist_ok=True)
ORIGIN=(-5600.,-34320.); DX=5.; NX=184; NY=220; X0=-460.; Y0=-550.
con=sqlite3.connect(str(ROOT/'04_Data/Ready/Kanda_Nihonbashi_Common_Foundation.gpkg'))
def read_layer(name):
    geom=con.execute('select column_name from gpkg_geometry_columns where table_name=?',(name,)).fetchone()[0]
    rows=con.execute('select "'+geom+'" from "'+name+'"').fetchall()
    ans=[]
    for (blob,) in rows:
        if not blob: continue
        env=(blob[3]>>1)&7; offset=8+{0:0,1:32,2:48,3:48,4:64}[env]
        ans.append(translate(wkb.loads(blob[offset:]),-ORIGIN[0],-ORIGIN[1]))
    return ans
core=unary_union(read_layer('primary_area')); domain=box(X0,Y0,X0+NX*DX,Y0+NY*DX)
features=json.loads((READY/'plateau_buildings_6677.geojson').read_text())['features']
bs=[]; polys=[]
for f in features:
    p=f['properties']; g=translate(shape(f['geometry']),-ORIGIN[0],-ORIGIN[1]); polys.append(g)
    rings=[[[round(x,2),round(y,2)] for x,y in ring.coords] for ring in [g.exterior,*g.interiors]]
    levels=p['storeys'] if p['storeys'] and p['storeys']>0 else max(1,round(p['height_m']/3.3))
    bs.append(dict(id=p['id'],rings=rings,h=p['height_m'],height_source=p['height_source'],levels=levels,
                   levels_source='source' if p['storeys'] and p['storeys']>0 else 'height / 3.3 m',
                   area=p['area_m2'],usage=p['usage'],survey=p['survey_year_raw'],
                   core=core.covers(g.representative_point()),center=[round(g.centroid.x,2),round(g.centroid.y,2)]))
solid=unary_union(polys); solids=prep(solid); rail=read_layer('rail'); railarea=unary_union(rail).buffer(6)
roads=read_layer('roads'); trees=[]
# Candidate shade trees along mapped roads: scenario geometry only, no claim of planting feasibility.
for road in roads:
    if road.geom_type!='LineString' or not road.intersects(core): continue
    for d in np.arange(10,road.length,25):
        p=road.interpolate(float(d)); a=road.interpolate(max(0,float(d)-1)); b=road.interpolate(min(road.length,float(d)+1))
        vx,vy=b.x-a.x,b.y-a.y; norm=math.hypot(vx,vy)
        if norm<.1: continue
        for sign in [-1,1]:
            q=Point(p.x-sign*vy/norm*4,p.y+sign*vx/norm*4)
            if core.covers(q) and q.distance(solid)>2.7 and not railarea.covers(q) and all(q.distance(Point(t['x'],t['y']))>13 for t in trees):
                trees.append(dict(x=round(q.x,2),y=round(q.y,2),r=4,h=8)); break
trees=trees[:48]
def lines(gs):
    result=[]
    for g in gs:
        if not g.intersects(domain): continue
        g=g.intersection(domain)
        for q in ([g] if g.geom_type=='LineString' else getattr(g,'geoms',[])):
            if q.geom_type=='LineString': result.append([[round(x,2),round(y,2)] for x,y in q.coords])
    return result
data=dict(meta=dict(title='Kajicho 1 & 2',origin_epsg6677=ORIGIN,crs='EPSG:6677',dx=DX,nx=NX,ny=NY,x0=X0,y0=Y0,
    geometry='PLATEAU LOD1 horizontal projection extruded with source heights',release_year=2025,
    download_date='2026-10-13',shade_date='2026-07-15',carbon_factor_kg_kwh=.421),
    buildings=bs,roads=lines(roads),rail=lines(rail),boundary=mapping(core),trees=trees)
(OUT/'city.json').write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False))
(OUT/'provenance.json').write_text((READY/'plateau_metadata.json').read_text())
mask=np.zeros((NY,NX),dtype=np.uint8); heights=np.zeros((NY,NX),dtype=np.float32)
# Rasterize building outlines at cell centers. The grid deliberately retains every source polygon.
for b,g in zip(bs,polys):
    x1,y1,x2,y2=g.bounds; pg=prep(g)
    for j in range(max(0,int((y1-Y0)/DX)),min(NY,int((y2-Y0)/DX)+1)):
        for i in range(max(0,int((x1-X0)/DX)),min(NX,int((x2-X0)/DX)+1)):
            if pg.covers(Point(X0+(i+.5)*DX,Y0+(j+.5)*DX)):
                mask[j,i]=1; heights[j,i]=max(heights[j,i],b['h'])
drag=np.zeros_like(heights)
for t in trees:
    for j in range(max(0,int((t['y']-t['r']-Y0)/DX)),min(NY,int((t['y']+t['r']-Y0)/DX)+1)):
        for i in range(max(0,int((t['x']-t['r']-X0)/DX)),min(NX,int((t['x']+t['r']-X0)/DX)+1)):
            if math.hypot(X0+(i+.5)*DX-t['x'],Y0+(j+.5)*DX-t['y'])<t['r'] and not mask[j,i]: drag[j,i]=.006
with (READY/'wind_input.txt').open('w') as f:
    f.write(f'{NX} {NY}\n'); f.write(' '.join(map(str,mask.ravel()))+'\n'); f.write(' '.join(map(str,drag.ravel()))+'\n')
np.savez_compressed(str(READY/'grid.npz'),mask=mask,height=heights)
print(json.dumps(dict(buildings=len(bs),core_buildings=sum(b['core'] for b in bs),trees=len(trees),grid=[NX,NY],solid_cells=int(mask.sum())),ensure_ascii=False))
