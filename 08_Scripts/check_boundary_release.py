#!/usr/bin/env python3
"""Check released course geometry, denominators, files and QGIS paths."""
import csv,json,math,sqlite3,struct,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist'
BASE=DIST/'boundary-atlas';atlas=json.loads((BASE/'atlas.json').read_text());stats=json.loads((BASE/'statistics.json').read_text())['scopes']
assert set(stats)=={'primary_brief','secondary_brief','poster_blue'}
reg=json.loads((BASE/'registration.json').read_text())
for f in reg['features']:
    p=f['properties'];m=p['registration']['affine_matrix'];vertices=p['source_pixel_vertices'];coords=f['geometry']['coordinates'][0]
    assert len(vertices)==len(coords)
    for (u,v),(east,north) in zip(vertices,coords):
        assert abs(u*m[0][0]+v*m[1][0]+m[2][0]-east)<1e-7
        assert abs(u*m[0][1]+v*m[1][1]+m[2][1]-north)<1e-7
    area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(coords,coords[1:])))/2
    assert abs(area-stats[p['id']]['area_m2'])<.001
    assert p['registration']['uncertainty_m']>=max(p['registration']['leave_one_out_errors_m'])
assert len(atlas['plates'])==9
assert atlas['map_export_formats']==['PNG'] and atlas['no_new_cfd']
for plate in atlas['plates']:
    p=DIST/plate['file'];assert p.is_file() and p.stat().st_size>1000
    b=p.open('rb').read(24);assert b[:8]==b'\x89PNG\r\n\x1a\n';assert struct.unpack('>II',b[16:24])==(3200,2400)
    assert (DIST/plate['preview']).is_file()
assert not list(BASE.rglob('*.svg'))
for p in BASE.rglob('*.json'):
    text=p.read_text();assert '/home/' not in text and '/Users/' not in text and '/Volumes/' not in text,p
for p in DIST.rglob('*'):
    if p.is_file():assert p.stat().st_size<25*1024*1024,(p,p.stat().st_size)
def readcsv(name):return list(csv.DictReader((BASE/'tables'/(name+'.csv')).open(encoding='utf-8-sig')))
models=readcsv('buildings');uses=readcsv('building_use');land=readcsv('land_use');heights=readcsv('height_models');flood=readcsv('flood_scenarios')
for sid,m in stats.items():
    selected=[r for r in models if r['scope']==sid];assert len(selected)==m['selected_models'];assert len({r['asset_id'] for r in selected})==len(selected)
    for row in selected:
        assert 0<float(row['levels'])<9999,row['asset_id']
        assert abs(float(row['plan_area_m2'])*float(row['levels'])-float(row['floor_proxy_m2']))<.001,row['asset_id']
    assert sum(int(r['models']) for r in uses if r['scope']==sid)==len(selected)
    assert sum(r['scope']==sid for r in heights)==len(selected)
    assert abs(m['area_m2']/10000-m['area_ha'])<1e-9
    assert 0<m['gross_footprint_union_m2']<=m['area_m2']
    assert 99.99<=m['land_use_coverage_pct']<=100.00001
    assert len([r for r in flood if r['scope']==sid])==4
    assert m['model_membership_sensitivity']['eroded_count']<=len(selected)<=m['model_membership_sensitivity']['buffered_count']
    assert m['boundary_uncertainty_m']==m['source_outline']['registration']['uncertainty_m']
    lu=sum(float(r['area_m2']) for r in land if r['scope']==sid)
    assert abs(lu-m['land_use_covered_m2']-m['land_use_between_class_overlap_m2'])<.1
project=ROOT/'05_QGIS/Projects/Kanda_Nihonbashi_Course_2026-10-16.qgz'
with zipfile.ZipFile(project) as z:
    doc=ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith('.qgs'))))
    for source in doc.findall('.//projectlayers/maplayer/datasource'):
        file=source.text.split('|')[0];assert not Path(file).is_absolute(),file;assert (project.parent/file).exists(),file
db=sqlite3.connect(ROOT/'04_Data/Ready/Course_Boundaries_2026-10-16/Kanda_Nihonbashi_Course.gpkg')
assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
assert db.execute('select count(*) from buildings where levels in (9999,-9999) or height_m in (9999,-9999)').fetchone()[0]==0
assert db.execute('select count(*) from course_membership').fetchone()[0]==sum(m['selected_models'] for m in stats.values())
assert db.execute("select count(*) from stations where name='神田駅' and line like '%銀座%'").fetchone()[0]>=1
assert db.execute("select count(*) from stations where name='神田駅' and (line like '%中央%' or line like '%東北%')").fetchone()[0]>=1
ctx=json.loads((DIST/'context-study/context.json').read_text());assert ctx['boundary_release']=='2026-10-16';assert [m['value'] for m in ctx['metrics'] if m['unit']=='ha']==[round(m['area_ha'],2) for m in stats.values()]
assert not list((DIST/'portfolio').glob('*.zip')) and not list((DIST/'context-study').glob('*.zip'))
html=(DIST/'index.html').read_text();assert 'boundary-atlas/maps/previews/course_00_overview.jpg' in html
print(json.dumps({'boundary_release':'passed','source_areas':len(stats),'png_maps':9,'model_totals':{s:m['selected_models'] for s,m in stats.items()},'area_ha':{s:round(m['area_ha'],4) for s,m in stats.items()},'land_use_coverage':'complete within source record union','portable_qgis':'passed','station_source_points':'JR and Ginza retained','new_cfd':False},indent=2))

themes=[p for p in atlas['plates'] if p['kind']=='theme']
assert len(themes)==8 and len({p['theme'] for p in themes})==8
assert len({tuple(p['extent_6677']) for p in atlas['plates']})==1
assert {p.name for p in (BASE/'maps').glob('*.png')}=={Path(p['file']).name for p in atlas['plates']}
assert not (DIST/'portfolio/maps').exists() and not (DIST/'portfolio/mapping_data').exists()
assert not list((BASE/'maps').glob('*_brief*'))
for plate in atlas['plates']:
    assert plate['scope']=='common_view'
    assert {m['scope'] for m in plate['scope_metrics']}==set(stats)
    for m in plate['scope_metrics']:
        source=stats[m['scope']]
        assert m['selected_models']==source['selected_models']
        assert m['area_ha']==source['area_ha']
        if m['metric']=='Footprint union':assert abs(m['value']-source['gross_footprint_coverage_pct'])<1e-8
        if m['metric']=='Mapped road length':assert abs(m['value']*1000-source['road_mapped_length_m'])<1e-8
        if m['metric']=='Land-use coverage':assert abs(m['value']-source['land_use_coverage_pct'])<1e-8
        if m['metric']=='Known building use':assert m['value']==source['known_use_models']
        if m['metric']=='Source height median':assert m['value']==source['source_height_median_m']
        if m['metric']=='Tree point records':assert m['value']==source['tree_point_records']
for chart in ctx['charts'][:5]:
    assert Path(chart['file']).name.startswith('course_')
    assert (DIST/chart['file']).is_file() and (DIST/chart['preview']).is_file()
for name in ('portfolio.js','team.js','app.js','cfd.js'):
    text=(DIST/name).read_text();assert "kajicho-language-20261017" in text and "kajicho-lang'" not in text
text=(DIST/'portfolio.js').read_text()
assert "plates.filter(p=>p.kind==='theme')" in text
assert text.count('if(boundaryData)renderBoundaries(boundaryData);')==1
for path in DIST.rglob('*.html'):
    text=path.read_text();assert 'portfolio/mapping_data/' not in text and 'portfolio/maps/' not in text and '00_primary_edge_comparison.png' not in text
assert not list((DIST/'context-study/figures').glob('0[1-5]*.png'))
print('Mapping presentation passed: eight unique themes, one frame, current area-specific metrics, legacy served maps removed, English initial language.')

from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
class Links(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key not in ('href','src') or not value:continue
            u=urlsplit(value)
            if u.scheme or u.netloc or not u.path:continue
            path=Path(unquote(u.path))
            if not path.suffix:continue
            target=(DIST/path.relative_to('/') if path.is_absolute() else self.source.parent/path).resolve()
            assert target.exists(),(self.source.name,value)
for source in DIST.glob('*.html'):
    parser=Links();parser.source=source;parser.feed(source.read_text())
print('HTML asset and download links passed.')
