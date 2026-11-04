#!/usr/bin/env python3
"""Audit retained vs available CityGML geometry; derive candidate extents, not CFD fields."""
import json, math, time, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon, shape, mapping, box
from shapely.ops import unary_union

R = Path(__file__).resolve().parents[1]
OUT = R/'04_Data/Ready/CFD_Domain_Audit_2026-10-14'
OUT.mkdir(parents=True, exist_ok=True)
SITE = R/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data'
old = json.loads((SITE/'cfd-context.json').read_text())
run = json.loads((SITE/'cfd-results.json').read_text())
core = shape(old['boundary']); retained = {b['id']: b for b in old['buildings']}
origin = run['domain']['origin_epsg6677']
core_max = max(b['h'] for b in retained.values() if b['core'])
base_radius = math.ceil(10*core_max/50)*50
tr = Transformer.from_crs(6668,6677,always_xy=True)
G = '{http://www.opengis.net/gml}'; B = '{http://www.opengis.net/citygml/building/2.0}'
C = '{http://www.opengis.net/citygml/2.0}'
catalog = json.loads((R/'04_Data/Raw/CFD_Context_2026-10-14/Expanded_Catalog.json').read_text())
url_lookup = {(c['cityCode'], Path(f['url']).name): f['url'] for c in catalog['cities']
              for f in c.get('files',{}).get('bldg',[])}
paths = [p for p in (R/'04_Data/Raw/CFD_Context_2026-10-14').glob('*.gml') if not p.name.startswith('._')]
paths += [p for p in (R/'04_Data/Raw/Public_Baseline_2026-10-14/PLATEAU').rglob('*.gml')
          if '/bldg/' in str(p) and not p.name.startswith('._')]
extra = R/'04_Data/Raw/CFD_Domain_Audit_2026-10-14'
if extra.exists(): paths += [p for p in extra.rglob('*.gml') if not p.name.startswith('._')]
rows = {}; sources = []; invalid = []
cache = OUT/'available_buildings_local.geojson'
cache_version = 0
if cache.exists():
    cached_data = json.loads(cache.read_text()); cache_version = cached_data.get('metadata',{}).get('parser_version',1)
    for f in cached_data['features']:
        b = f['properties']; b['geometry'] = shape(f['geometry']); rows[b['id']] = b
for path in paths:
    ward = next((p[:5] for p in path.parts if p[:5].isdigit() and '_citygml_' in p),None)
    if not ward: ward = next((p for p in path.parts if p in {'13101','13102','13103','13105','13106','13107','13108'}),None)
    if not ward: ward = '13102' if path.name == '53394612_bldg_6697_op.gml' else '13101'
    marker = f'{ward}:{path.name}'
    if cache_version >= 2 and any(b.get('source_key') == marker for b in rows.values()):
        sources.append({'file':str(path.relative_to(R)), 'source_key':marker, 'cached':True}); continue
    start = time.time(); count = 0; no_lod1 = 0
    it = ET.iterparse(path,events=('start','end')); _, root = next(it)
    for ev,node in it:
        if ev != 'end' or node.tag != C+'cityObjectMember': continue
        b = node[0]; ident = b.get(G+'id'); lod = b.find(B+'lod1Solid')
        if lod is None: no_lod1 += 1
        if lod is not None and ident not in rows:
            polygons = []; zs = []
            for poly in lod.iter(G+'Polygon'):
                ring = poly.find('.//'+G+'exterior//'+G+'posList')
                if ring is None or not ring.text: continue
                a = np.fromstring(ring.text,sep=' ').reshape(-1,3); zs.extend(a[:,2])
                x,y = tr.transform(a[:,1],a[:,0]); g = Polygon(np.column_stack((x-origin[0],y-origin[1])))
                if not g.is_valid: g = g.buffer(0)
                if g.area > 1e-6: polygons.append(g)
            if polygons:
                geom = unary_union(polygons)
                h = b.findtext(B+'measuredHeight')
                h = float(h) if h and 0<float(h)<1000 else float(max(zs)-min(zs))
                h = retained.get(ident,{}).get('h',h)
                if h > 0 and geom.area > 1e-6:
                    # Retained geometries remain exact to the current comparison.
                    if ident in retained: geom = shape(retained[ident]['geometry'])
                    d = geom.distance(core)
                    rows[ident] = {'id':ident,'height_m':h,'distance_to_core_m':d,
                        'core':retained.get(ident,{}).get('core',False),'retained':ident in retained,
                        'source_key':marker,'source_url':url_lookup.get((ward,path.name)),
                        'source_data_year':2025,'ground_source_m':float(min(zs)),
                        'tiny_footprint':geom.area<=1,'geometry':geom}
                    count += 1
        node.clear(); root.clear()
    sources.append({'file':str(path.relative_to(R)),'source_key':marker,'eligible_objects':count,
                    'no_lod1':no_lod1,'seconds':round(time.time()-start,2)})
    print(marker,count,round(time.time()-start,1),flush=True)
features = [{'type':'Feature','properties':{k:v for k,v in b.items() if k!='geometry'},'geometry':mapping(b['geometry'])} for b in rows.values()]
cache.write_text(json.dumps({'type':'FeatureCollection','metadata':{'parser_version':2,'crs':'EPSG:6677 local, add origin','origin':origin,'sources':sources,'geometry_floor_m2':1e-6},'features':features},ensure_ascii=False,separators=(',',':')))
assert set(retained).issubset(rows),len(set(retained)-set(rows))

def extent(name, selected):
    bounds = [min(b['geometry'].bounds[i] for b in selected) for i in [0,1]]
    bounds += [max(b['geometry'].bounds[i] for b in selected) for i in [2,3]]
    H = max(b['height_m'] for b in selected); top = 6*H
    silhouette = unary_union([box(b['geometry'].bounds[0],0,b['geometry'].bounds[2],b['height_m']) for b in selected]).area
    minimum_width = bounds[2]-bounds[0]+10*H
    width = max(minimum_width,silhouette/(.028*top)); side = (width-(bounds[2]-bounds[0]))/2
    domain = [bounds[0]-side,bounds[1]-5*H,bounds[2]+side,bounds[3]+15*H,top]
    return {'name':name,'building_objects':len(selected),'added_objects':sum(not b['retained'] for b in selected),
        'Hmax_m':H,'built_bounds_m':bounds,'domain_m':domain,'size_m':[width,domain[3]-domain[1],top],
        'upstream_m':5*H,'downstream_m':15*H,'side_m':side,'top_above_roofs_m':5*H,
        'projected_silhouette_proxy_m2':silhouette,'blockage_proxy':silhouette/(width*top),
        'interpretation':'Conservative candidate start; not a boundary-independence or geometry-convergence result.'}

existing = [b for b in rows.values() if b['retained']]
six = [b for b in rows.values() if b['core'] or b['distance_to_core_m'] <= max(base_radius,6*b['height_m'])]
ten = [b for b in rows.values() if b['core'] or b['distance_to_core_m'] <= max(base_radius,10*b['height_m'])]
missed6 = [b for b in six if not b['retained']]
six_ids = {b['id'] for b in six}
between6_10 = [b for b in ten if b['id'] not in six_ids]
summary = {'calculated_jst':datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(timespec='seconds'),
    'kind':'Geometry and domain arithmetic; no flow sensitivity computed',
    'core_height_max_m':core_max,'core_height_10H_m':10*core_max,'candidate_base_radius_m':base_radius,
    'original_500m':'Fixed project setting. Recalculation gives ceil(10*48.5/50)*50=500m; source does not prescribe a universal500m.',
    'available_source_files':sources,'available_objects':len(rows),'source_coverage':'Only listed files; broader catalog must be screened for high-rise candidates.',
    'tiny_footprint_objects':sum(b['geometry'].area<=1 for b in rows.values()),
    'retained_rule_violations_within_available_data':[ {k:v for k,v in b.items() if k!='geometry'} for b in missed6],
    'additional_6to10H_objects':len(between6_10),'candidates':[extent('current_geometry',existing),extent('complete6H_within_available_data',six),extent('expanded10H_within_available_data',ten)],
    'outer_domain_original':run['domain'],'crs':'EPSG:6677 local','origin':origin,
    'sources':[{'title':'COST732 Best Practice Guideline2007','sections':'5.4–5.5, printed pp16–18','url':'https://www.airshed.co.uk/wp-content/uploads/2018/03/COST-732-Best-Practice-Guideline-May-2007.pdf'}]}
(OUT/'Domain_Audit.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
for name, selection in [('geometry6H',six),('geometry10H',ten)]:
    selected_ids = {b['id'] for b in selection}
    (OUT/(name+'.geojson')).write_text(json.dumps({'type':'FeatureCollection','metadata':{'crs':'EPSG:6677 local','origin':origin,'scope':'Candidate geometry; not active CFD inputs'},'features':[f for f in features if f['properties']['id'] in selected_ids]},ensure_ascii=False,separators=(',',':')))
print(json.dumps({'objects':len(rows),'missed6H':len(missed6),'extra10H':len(between6_10),'candidates':summary['candidates']},ensure_ascii=False),flush=True)
