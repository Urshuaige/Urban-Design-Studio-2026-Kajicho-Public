#!/usr/bin/env python3
"""Validate the current single-area release without GIS dependencies or model runs.

Historical releases retain check_boundary_release.py. This check reads saved inputs,
native GIS data and the deployable mirror; it never edits files or starts simulations.
"""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import sqlite3
import struct
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / '06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist'
OUT = ROOT / '06_Outputs/Study_Area_2026-10-18'
ATLAS = DIST / 'study-atlas'
LANGS = ('en', 'zh', 'ja')
GEOMETRY_SHA = '39c6bb212b52a2709d3a3fed20a2cd23bd29575b8e175d21496e1d0f06b393c1'
AREA_HA = 41.98967122381172
MODELS = 1074
OSM_MODELS = 1029


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read_json(path):
    return json.loads(path.read_text())


def close(actual, expected, label, tolerance=1e-7):
    require(math.isclose(float(actual), float(expected), rel_tol=1e-10, abs_tol=tolerance),
            f'{label}: {actual!r} != {expected!r}')


def translated(value, label):
    require(isinstance(value, dict) and all(value.get(lang) for lang in LANGS),
            f'{label}: missing English, Chinese or Japanese')


def table(name):
    with (ATLAS / 'tables' / (name + '.csv')).open(newline='',encoding='utf-8-sig') as source:
        return list(csv.DictReader(source))


def png_size(path):
    with path.open('rb') as source:
        header = source.read(24)
    require(header[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {path}')
    return list(struct.unpack('>II', header[16:24]))


def jpeg_size(path):
    with path.open('rb') as source:
        require(source.read(2) == b'\xff\xd8', f'Invalid JPEG: {path}')
        while True:
            byte = source.read(1)
            require(bool(byte), f'JPEG dimensions missing: {path}')
            if byte != b'\xff':
                continue
            while byte == b'\xff':
                byte = source.read(1)
            marker = byte[0]
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                continue
            length = struct.unpack('>H', source.read(2))[0]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                          0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                _, height, width = struct.unpack('>BHH', source.read(5))
                return [width, height]
            source.seek(length - 2, 1)


def wkb_polygons(blob):
    """Read source Polygon/MultiPolygon WKB from the standard GeoPackage header."""
    require(blob[:2] == b'GP', 'Not a GeoPackage geometry')
    envelope_code = (blob[3] >> 1) & 7
    offset = 8 + (0, 32, 48, 48, 64)[envelope_code]

    def read(offset):
        endian = '<' if blob[offset] == 1 else '>'
        kind = struct.unpack_from(endian + 'I', blob, offset + 1)[0]
        offset += 5
        has_srid = bool(kind & 0x20000000)
        z, m = bool(kind & 0x80000000), bool(kind & 0x40000000)
        kind &= 0x1FFFFFFF
        if kind >= 1000:
            dimension_code, kind = divmod(kind, 1000)
            z, m = dimension_code in (1, 3), dimension_code in (2, 3)
        if has_srid:
            offset += 4
        dimensions = 2 + int(z) + int(m)
        count = struct.unpack_from(endian + 'I', blob, offset)[0]
        offset += 4
        if kind == 3:
            rings = []
            for _ in range(count):
                points = struct.unpack_from(endian + 'I', blob, offset)[0]
                offset += 4
                ring = []
                for _ in range(points):
                    values = struct.unpack_from(endian + 'd' * dimensions, blob, offset)
                    ring.append(values[:2])
                    offset += dimensions * 8
                rings.append(ring)
            return [rings], offset
        require(kind == 6, f'Expected polygon geometry, got WKB type {kind}')
        polygons = []
        for _ in range(count):
            part, offset = read(offset)
            polygons.extend(part)
        return polygons, offset

    return read(offset)[0]


def ring_area(ring):
    # Translate before the shoelace sum to reduce cancellation at projected coordinates.
    ox, oy = ring[0]
    return abs(sum((a[0]-ox)*(b[1]-oy)-(b[0]-ox)*(a[1]-oy)
                   for a, b in zip(ring, ring[1:]))) / 2


def polygon_area(polygons):
    return sum(ring_area(p[0]) - sum(ring_area(h) for h in p[1:]) for p in polygons)


def bounds(ring):
    return min(p[0] for p in ring), min(p[1] for p in ring), max(p[0] for p in ring), max(p[1] for p in ring)


def intersects_box(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def orientation(a, b, p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def point_location(point, ring):
    """Return 1 inside, 0 on the line, -1 outside; coordinates are in metres."""
    x, y = point
    inside = False
    for a, b in zip(ring, ring[1:]):
        if min(a[0],b[0])-1e-8 <= x <= max(a[0],b[0])+1e-8 and min(a[1],b[1])-1e-8 <= y <= max(a[1],b[1])+1e-8:
            if abs(orientation(a,b,point)) <= 1e-8 * max(1,math.hypot(b[0]-a[0],b[1]-a[1])):
                return 0
        if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            inside = not inside
    return 1 if inside else -1


def geometry_membership(polygons, boundary, boundary_box, boundary_segments):
    """Independent whole-footprint coverage and crossing checks on saved source rings."""
    covered_parts, crossing = [], False
    for polygon in polygons:
        exterior = polygon[0]
        box = bounds(exterior)
        if not intersects_box(box,boundary_box):
            covered_parts.append(False)
            continue
        locations = [point_location(point,boundary) for point in exterior[:-1]]
        has_inside, has_outside = any(v == 1 for v in locations), any(v == -1 for v in locations)
        crossed = has_inside and has_outside
        # A concave study boundary can cut an edge even when all its vertices are inside.
        nearby = [(a,b,bb) for a,b,bb in boundary_segments if intersects_box(box,bb)]
        for a,b in zip(exterior,exterior[1:]):
            ab = (min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1]))
            for c,d,bb in nearby:
                if not intersects_box(ab,bb):
                    continue
                oa,ob,oc,od = orientation(a,b,c),orientation(a,b,d),orientation(c,d,a),orientation(c,d,b)
                if oa*ob < -1e-12 and oc*od < -1e-12:
                    crossed = True
                    break
            if crossed:
                break
        if not has_inside and has_outside and not crossed:
            # A very large source polygon might surround the whole study area.
            crossed = point_location(boundary[0],exterior) == 1 and not any(point_location(boundary[0],hole) >= 0 for hole in polygon[1:])
        crossing = crossing or crossed
        covered_parts.append(not has_outside and not crossed)
    if any(covered_parts) and not all(covered_parts):
        crossing = True
    return bool(covered_parts) and all(covered_parts), crossing


def validate_seismic(seismic, census_rows):
    census_rows = [row for row in census_rows if row.get('scope','study_area') == 'study_area']
    """Require the full source-town join; the two Kajicho focus rows remain a subset."""
    expected = {}
    for part in census_rows:
        if float(part['scope_overlap_m2']) <= 0:
            continue
        key = (part['ward_code'],part['town_code'])
        unit = expected.setdefault(key,{'name':part['town_name'],'overlap':0.,'area':0.})
        require(unit['name'] == part['town_name'],'Census town code has conflicting names')
        unit['overlap'] += float(part['scope_overlap_m2'])
        unit['area'] += float(part['full_town_area_m2'])
    rows = seismic['rows']
    require(len(rows) >= 2,'Earthquake source-town table needs the two Kajicho focus rows')
    keys = [(row['ward_code'],row['town_code']) for row in rows]
    require(len(set(keys)) == len(rows),'Duplicate earthquake source-town rows')
    require(set(keys) == set(expected),'Earthquake join must cover all positive-overlap census towns; missing='+
            str(sorted(set(expected)-set(keys)))+' extra='+str(sorted(set(keys)-set(expected))))
    focus_codes = {'13101035001':4.15,'13101035002':3.81}
    focus_rows = [row for row in rows if row.get('focus') is True]
    require(len(focus_rows) == 2 and {row['town_code'] for row in focus_rows} == set(focus_codes),
            'Exactly Kajicho 1 and 2 must be flagged as focus')
    for row,key in zip(rows,keys):
        unit = expected[key]
        require(row['town_name'] == unit['name'],'Earthquake row must preserve census town name')
        require(isinstance(row.get('focus'),bool),'Earthquake focus flag must be explicit')
        require(row.get('official_town_name') and row.get('join_method'),'Missing official source name/join method')
        require(row.get('source_row') and len(row['source_row']) >= 13,'Missing original earthquake source row')
        source_fields = {
            'collapse':'建物倒壊危険度危険量（棟/ha）','collapse_rank':'建物倒壊危険度ランク',
            'fire':'火災危険度危険量（棟/ha）','fire_rank':'火災危険度ランク',
            'overall':'総合危険度危険量（棟/ha）','overall_rank':'総合危険度ランク',
            'response_difficulty':'災害時活動困難度困難係数',
        }
        require(row['official_town_name'] == row['source_row']['町丁目名'],'Official earthquake town name changed')
        for field,source_field in source_fields.items():
            require(str(row[field]) == str(row['source_row'][source_field]),
                    'Published earthquake value changed or overlap weighted: '+row['town_code']+' '+field)
        require(row.get('census_part_ids'),'Missing source geometry-part membership')
        close(row['scope_overlap_m2'],unit['overlap'],'Earthquake source-town overlap',1e-4)
        close(row['full_census_town_area_m2'],unit['area'],'Earthquake source-town denominator',1e-4)
        close(row['town_overlap_fraction'],unit['overlap']/unit['area'],'Earthquake town-overlap fraction',1e-7)
        for field in ('collapse','fire','overall'):
            amount = float(row[field])
            require(math.isfinite(amount) and amount >= 0,'Invalid published earthquake amount: '+field)
        for field in ('collapse_rank','fire_rank','overall_rank'):
            require(float(row[field]) in (1,2,3,4,5),'Invalid earthquake rank: '+field)
        if row['town_code'] in focus_codes:
            close(row['collapse'],focus_codes[row['town_code']],'Kajicho source collapse amount')
    require(seismic.get('sources') and any(str(source.get('year')) == '2022' for source in seismic['sources']),
            'Earthquake publication year/source citations missing')
    for source in seismic['sources']:
        url = urlsplit(source.get('url',''))
        if url.scheme:
            require(url.scheme == 'https','Earthquake external source must use HTTPS')
        else:
            require(bool(url.path) and not Path(url.path).is_absolute() and (DIST/unquote(url.path)).is_file(),
                    'Earthquake local source link is missing: '+source.get('url',''))
    return len(rows)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []
        self.html_lang = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.html_lang = attrs.get('lang')
        self.paths.extend(attrs[k] for k in ('src','href') if attrs.get(k))


def node22():
    candidates = [os.environ.get('NODE22'), os.environ.get('NODE'),
                  str(ROOT.parent/'node-v22.16.0-linux-x64/bin/node'), shutil.which('node')]
    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        version = subprocess.check_output([candidate,'--version'],text=True).strip()
        if re.match(r'v(?:2[2-9]|[3-9][0-9])\.',version):
            return candidate, version
    raise AssertionError('Node 22 or newer is required; set NODE22 or install the CI Node 22 runtime')



def main():
    atlas,stats,quality,manifest=[read_json(ATLAS/name) for name in ('atlas.json','statistics.json','quality_checks.json','source_manifest.json')]
    projected_path=OUT/'study_boundary_6677.geojson';projected=read_json(projected_path)
    require(len(projected['features'])==2,'Figure 5 needs its two source outlines')
    frozen={f['properties']['id']:f for f in projected['features']}
    require(set(frozen)=={'study_area','primary_brief'},'Unexpected current scope')
    expected={'study_area':(GEOMETRY_SHA,AREA_HA,MODELS),'primary_brief':('07ac4282e1a54a41df1e5253c0943fb5a55ca57268a969c6bd31132321f94de8',10.703830447464894,277)}
    for sid,f in frozen.items():
        g=f['geometry'];p=f['properties'];digest=hashlib.sha256(json.dumps(g,separators=(',',':')).encode()).hexdigest()
        require(digest==expected[sid][0]==p['geometry_sha256'],sid+' source-stroke geometry changed')
        close(ring_area(g['coordinates'][0])/10000,expected[sid][1],sid+' area')
        require(p['source_scope_id']==('secondary_brief' if sid=='study_area' else sid),'Source role lost')
        require(p['line_style']==('dash' if sid=='study_area' else 'solid'),'Official line style lost')
        matrix=p['registration']['affine_matrix'];coords=g['coordinates'][0];pixels=p['source_pixel_vertices']
        require(len(coords)==len(pixels),'Source-pixel vertex count changed')
        for (x,y),(e,n) in zip(pixels,coords):
            close(e,x*matrix[0][0]+y*matrix[1][0]+matrix[2][0],sid+' affine easting')
            close(n,x*matrix[0][1]+y*matrix[1][1]+matrix[2][1],sid+' affine northing')
        close(p['registration']['rmse_m'],7.434546907555709,'RMSE')
        require(p['registration']['uncertainty_m']==25,'Cartographic screening band lost')
        for data in [atlas,read_json(OUT/'atlas.json')]:
            require(set(data['scopes'])==set(frozen),'Both source denominators required')
            require(data['scopes'][sid]['selected_models']==expected[sid][2],sid+' model count changed')
            close(data['scopes'][sid]['area_ha'],expected[sid][1],sid+' saved statistics')
        for key in ['atlas.json','statistics.json','study_boundary.geojson']:
            require((ATLAS/key).read_bytes()==(OUT/key).read_bytes(),'Site data differs from release '+key)
    primary=frozen['primary_brief']['geometry']['coordinates'][0];outer=frozen['study_area']['geometry']['coordinates'][0]
    require(all(point_location(p,outer)>=0 for p in primary),'Primary must be nested in secondary')
    require(quality['boundary_count']==2 and quality['png_maps']==10 and quality['thematic_maps']==9,'QA scope/map count')
    require(quality['source_building_geometry_unchanged'] is True and not quality['new_cfd'],'Source/solver state')
    plates=atlas['plates'];require(len(plates)==10 and len({p['id'] for p in plates})==10,'Duplicate or missing map plates')
    require(sum(p['kind']=='theme' for p in plates)==9 and sum(p['kind']=='overview' for p in plates)==1,'One common view per theme')
    extents={tuple(p['extent_6677']) for p in plates};require(len(extents)==1,'Maps must share a view')
    for p in plates:
        require(p['overlaid_scopes']==['study_area','primary_brief'],'Map source overlay mismatch')
        require(p['boundary_geometry_sha256']==GEOMETRY_SHA and p['primary_boundary_geometry_sha256']==expected['primary_brief'][0],'Map trace version mismatch')
        require(png_size(DIST/p['file'])==p['pixels']==[2800,2520],'PNG export dimensions')
        require(jpeg_size(DIST/p['preview'])==p['preview_pixels'],'JPEG preview dimensions')
        require(p['legend'][0]['kind']=='line' and not p['legend'][0]['dash'] and p['legend'][1]['dash'],'Legend must distinguish official solid/dashed')
        require(p['text_sizes']['web_legend_css_px']>=17 and p['text_sizes']['export_legend_pt']>=17,'Unreadable legend')
    require(not list(ATLAS.rglob('*.svg')),'SVG map exported')
    building_rows=table('buildings');by_scope={sid:[r for r in building_rows if r['scope']==sid] for sid in frozen}
    gpkg=ROOT/quality['gpkg'];con=sqlite3.connect('file:'+str(gpkg)+'?mode=ro',uri=True)
    require(con.execute('pragma integrity_check').fetchone()[0]=='ok','GeoPackage integrity')
    require(con.execute('select count(*) from buildings').fetchone()[0]==9244,'Source model pool changed')
    require(len(con.execute('select table_name from gpkg_geometry_columns').fetchall())==20,'GIS layers')
    for sid,f in frozen.items():
        rows=by_scope[sid];ids={r['asset_id'] for r in rows}
        require(len(rows)==len(ids)==expected[sid][2],sid+' model table duplicates/count')
        joined={r[0] for r in con.execute('select asset_id from study_membership where scope=?',(sid,))}
        col='in_study_area' if sid=='study_area' else 'in_primary_area';flagged={r[0] for r in con.execute('select asset_id from buildings where '+col+'=1')}
        subset='analysis_buildings_wider' if sid=='study_area' else 'analysis_buildings_primary'
        physical={r[0] for r in con.execute('select asset_id from '+subset)}
        require(ids==joined==flagged==physical,sid+' GIS/table membership mismatch')
        saved=wkb_polygons(con.execute('select geom from '+sid).fetchone()[0]);close(polygon_area(saved)/10000,expected[sid][1],sid+' GIS area',1e-6)
        savedring=saved[0][0][:-1];ring=f['geometry']['coordinates'][0][:-1]
        require(len(savedring)==len(ring),sid+' GIS vertex count')
        start=min(range(len(savedring)),key=lambda i:math.dist(savedring[i],ring[0]))
        require(any(all(math.dist(savedring[(start+direction*i)%len(savedring)],v)<1e-7 for i,v in enumerate(ring)) for direction in [1,-1]),sid+' GIS geometry differs')
        fullring=f['geometry']['coordinates'][0];bb=bounds(fullring);segments=[(a,b,(min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1]))) for a,b in zip(fullring,fullring[1:])]
        covered,crossing=set(),set()
        for asset_id,blob in con.execute('select asset_id,geom from buildings'):
            inside,cross=geometry_membership(wkb_polygons(blob),fullring,bb,segments)
            if inside:covered.add(asset_id)
            if cross:crossing.add(asset_id)
        require(ids==covered and not (ids&crossing),sid+' objects outside the source boundary')
        require(len(ids&crossing)==stats['scopes'][sid]['boundary_crossing_selected_models'],sid+' crossing selection audit')
        require(len(crossing)==stats['scopes'][sid]['raw_boundary_crossing_models'],sid+' raw crossing audit')
        uses=[r for r in table('building_use') if r['scope']==sid];require(sum(int(r['models']) for r in uses)==len(ids),sid+' use denominator')
        heights=[r for r in table('height_models') if r['scope']==sid];require(len(heights)==len(ids),sid+' height denominator')
        require(len([r for r in table('flood_scenarios') if r['scope']==sid])==4,sid+' flood scenario count')
    kanda=con.execute('select name,line from stations where name like ?',('%神田%',)).fetchall()
    require(any('銀座' in r[1] for r in kanda) and any(any(s in r[1] for s in ('山手','中央','京浜','JR')) for r in kanda),'Kanda JR/Ginza must remain separate')
    con.close()
    qgis=ROOT/quality['qgis_project']
    with zipfile.ZipFile(qgis) as archive:project=ET.fromstring(archive.read(next(n for n in archive.namelist() if n.endswith('.qgs'))))
    layers=project.findall('.//projectlayers/maplayer');require(len(layers)==21,'QGIS layer count')
    for layer in layers:
        source=layer.findtext('datasource') or '';path=source.split('|')[0]
        require(path and not Path(path).is_absolute() and (qgis.parent/path).resolve()==gpkg.resolve(),'Nonportable QGIS source '+source)
    public=read_json(ATLAS/'atlas.geojson');require({f['properties'].get('layer') for f in public['features']}.issuperset({'study_area','primary_brief','poi'}),'Public GIS layers')
    require(not any(f['properties'].get('layer') in {'poster_blue','census_legacy','secondary_brief'} for f in public['features']),'Obsolete public scope')
    pd=read_json(ATLAS/'poi_semantics.json');pois=read_json(ATLAS/'poi.geojson')['features'];require(len({f['properties']['source_id'] for f in pois})==len(pois),'Duplicate POI source objects')
    for sid,flag in [('study_area','in_study_area'),('primary_brief','in_primary_area')]:
        ring=next(f['geometry']['coordinates'][0] for f in read_json(ATLAS/'study_boundary.geojson')['features'] if f['properties']['id']==sid)
        selected={f['properties']['source_id'] for f in pois if point_location(f['geometry']['coordinates'],ring)>=0}
        declared={f['properties']['source_id'] for f in pois if f['properties'][flag]}
        result=pd['scopes'][sid];require(selected==declared==set(result['whole_source_object_ids']),sid+' POI spatial membership mismatch')
        require(len(selected)==result['poi_count']==(353 if sid=='study_area' else 178),sid+' POI count')
        require(sum(c['count'] for c in result['categories'])==len(selected),'POI categories do not add up')
        close(sum(c['share_pct'] for c in result['categories']),100,'POI shares',1e-7)
        require(sum(s['poi_count'] for s in result['sectors'])==len(selected),'POI band counts')
        for s in result['sectors']:close(s['poi_per_ha'],s['poi_count']/s['area_ha'],'POI band density')
    require(pd['source']['license']=='ODbL 1.0' and pd['source']['osm_base_timestamp'].startswith('2026-10-18'),'POI source version')
    require(pd['merged_node_area_pairs']==0,'Review any new node/area merge before release')
    for c in pd['local_concentrations']:
        scope=pd['scopes'][c['scope']];n=next(x['count'] for x in scope['categories'] if x['id']==c['category'])
        close(c['location_quotient'],(c['category_count']/c['total_pois'])/(n/scope['poi_count']),'POI concentration')
        require(c['total_pois']>=5 and c['category_count']>=3 and c['location_quotient']>=1.5,'Cluster threshold')
    context=read_json(DIST/'context-study/context.json')
    require(len(context['topics'])==18 and len(context['brief_checklist'])==7,'Document panel coverage')
    for t in context['topics']:
        for key in ('source','check','action'):translated(t['compact'][key],t['id']+' '+key)
        require(t['evidence'] and all(e.get('url','').startswith('https://') and e.get('page') for e in t['evidence']),'Document source missing')
    seismic_units=validate_seismic(context['seismic'],table('census_intersections'))
    require(len(read_json(ATLAS/'earthquake_risk_primary.json')['rows'])==13,'Primary risk intersections omitted')
    portfolio=(DIST/'portfolio.js').read_text()
    require('renderPOI(insight,lang)' in portfolio and "plates.filter(p=>p.kind==='theme')" in portfolio,'POI/thematic rendering missing')
    require('renderPolicyDiagrams(study,lang,' in portfolio and 'renderSimulationPlan(lang,' in portfolio,'Policy/simulation renderers')
    require('20261018-strict-nav' in portfolio,'Current data/image cache version absent')
    require('1,134' not in (DIST/'team.js').read_text(),'Old team inventory still shown')
    require(re.search(r'\.map-legend\s*\{[^}]*font:\s*(?:1[7-9]|[2-9]\d)px',(DIST/'study-mapping.css').read_text()),'Legend below17px')
    require(re.search(r'\.policy-source-title\s*\{[^}]*font-size:\s*(?:1[89]|[2-9]\d)px;[^}]*font-weight:\s*[7-9]\d\d',(DIST/'policy-diagrams.css').read_text()),'Source links need large bold text')
    for page in ('index.html','team.html','studies.html','cfd.html','style-guide.html','research.html'):
        parser=Links();parser.feed((DIST/page).read_text());require(parser.html_lang=='en',page+' initial language')
        for val in parser.paths:
            url=urlsplit(val)
            if not url.scheme and url.path:require((DIST/unquote(url.path)).is_file(),page+' missing '+val)
    for path in DIST.rglob('*'):
        if not path.is_file() or path.name.startswith('._'):continue
        require(path.stat().st_size<25*1024*1024,'Sites file limit '+str(path))
        if path.suffix in ('.html','.js','.json','.css','.md'):
            s=path.read_text();require('boundary-atlas/' not in s,'Old map reference '+str(path))
            if ATLAS in path.parents or path.name=='simulation-scope-plan.json':require(not any(x in s for x in ['/Users/','/Volumes/','/home/mdxuser/','/home/shi/']),'Private source path '+str(path))
    plan=read_json(DIST/'data/simulation-scope-plan.json');require(plan['boundary']['geometry_sha256']==GEOMETRY_SHA and plan['boundary']['mapping_outline_count']==2,'Plan scope mismatch')
    require(plan['boundary']['file_sha256']==hashlib.sha256(projected_path.read_bytes()).hexdigest(),'Plan source-file hash')
    require(plan['execution']['status']=='planning_only' and not plan['execution']['queued_cases'] and not any(plan['execution'][k] for k in ['new_mesh_started','new_solver_started','new_radiation_started','new_building_energy_started']),'Unexpected numerical execution')
    require(not plan['legacy']['full_numerical_acceptance'] and not plan['legacy']['new_scope_fields_valid'],'Historical CFD promoted')
    node,version=node22()
    for path in DIST.glob('*.js'):
        result=subprocess.run([node,'--check',str(path)],text=True,capture_output=True);require(result.returncode==0,path.name+':'+result.stderr)
    print(json.dumps({'figure5':'passed','source_outlines':2,'primary_ha':10.703830447464894,'wider_ha':AREA_HA,'primary_models':277,'wider_models':MODELS,'png_maps':10,'thematic_maps':9,'one_view_per_theme':True,'poi_wider':353,'poi_primary':178,'earthquake_towns':seismic_units,'portable_spatial_layers':20,'initial_language':'en','node':version,'new_cfd':False},indent=2))
if __name__=='__main__':main()

