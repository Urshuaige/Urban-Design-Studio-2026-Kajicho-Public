#!/usr/bin/env python3
"""Check the prepared data package, including a relocated QGIS project copy.

Use the same PyQGIS environment as build_common_qgis.py. The captured source
snapshot and official census totals define the checks for this delivery.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import json, shutil, os, csv, re, math
from qgis.core import *

root=Path(__file__).resolve().parents[1]
app=QgsApplication([],False);app.initQgis()
project=root/'05_QGIS/Projects/Kanda_Nihonbashi_Common_Foundation_2026-10-13.qgz'
gpkg=root/'04_Data/Ready/Kanda_Nihonbashi_Common_Foundation.gpkg'
q=QgsProject();assert q.read(str(project));assert len(q.mapLayers())==12
assert all(l.isValid() and l.crs().authid()=='EPSG:6677' for l in q.mapLayers().values())
b=next(l for l in q.mapLayers().values() if l.name().startswith('Buildings'))
assert b.featureCount()==9012
assert all(QgsVariantUtils.isNull(f['electricity_kwh']) and QgsVariantUtils.isNull(f['annual_electricity_co2_t']) for f in b.getFeatures())
c=next(l for l in q.mapLayers().values() if l.name().startswith('Census'))
towns={};wards={}
for f in c.getFeatures():
    d=towns.setdefault(f['town_code'],{'pop':0,'area':0,'density':[]})
    d['pop']+=f['population_2020'];d['area']+=f['area_m2'];d['density'].append(f['population_per_ha'])
    wards[f['ward_code']]=wards.get(f['ward_code'],0)+f['population_2020']
assert wards=={'13101':66680,'13102':169179}
assert all(all(abs(d-v['pop']*10000/v['area'])<1e-8 for d in v['density']) for v in towns.values())
layout_checks=[]
for lay in q.layoutManager().layouts():
    m=next(i for i in lay.items() if isinstance(i,QgsLayoutItemMap))
    assert math.isfinite(m.scale()) and m.scale()>0
    layout_checks.append({'name':lay.name(),'map_width_mm':m.sizeWithUnits().width(),'map_height_mm':m.sizeWithUnits().height(),'scale':m.scale()})
with ZipFile(project) as z:
    xml=z.read(next(n for n in z.namelist() if n.endswith('.qgs'))).decode()
    assert '/Volumes/' not in xml
for p in (root/'05_QGIS/Layouts/Common_Foundation').glob('*.qpt'):
    if not p.name.startswith('._'):assert '/Volumes/' not in p.read_text()
with TemporaryDirectory(prefix='uds2026_portable_') as td:
    relocated=Path(td)
    for src in [project,gpkg]:
        dst=relocated/src.relative_to(root);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    check=QgsProject();assert check.read(str(relocated/project.relative_to(root)))
    assert len(check.mapLayers())==12 and all(l.isValid() for l in check.mapLayers().values())
    assert all(str(relocated) in l.source() for l in check.mapLayers().values())
    for lay in check.layoutManager().layouts():
        for m in [i for i in lay.items() if isinstance(i,QgsLayoutItemMap)]:
            assert all(l.isValid() and str(relocated) in l.source() for l in m.layers())
    check.clear()
missing=[];checked=0
for p in (root/'03_Theme_B/Common_Foundation').glob('*'):
    if p.suffix not in ['.md','.html'] or p.name.startswith('._'):continue
    text=p.read_text()
    links=re.findall(r'(?:href|src)="([^"]+)"',text) if p.suffix=='.html' else re.findall(r'\]\(([^)]+)\)',text)
    for ref in links:
        if ref.startswith(('https://','http://','#','mailto:')):continue
        checked+=1
        if not (p.parent/ref.split('#')[0]).exists():missing.append([str(p),ref])
assert not missing,missing
rows=list(csv.DictReader((root/'04_Data/Metadata/Data_Register.csv').open(encoding='utf-8-sig')))
assert len(rows)==19 and all((root/r['local_path'].split('|')[0]).exists() for r in rows)
report={'date':'2026-10-13','project_layers_valid':12,'crs':'EPSG:6677','relocated_project_and_layout_readback':'pass','project_absolute_volume_paths':0,'actual_building_energy_and_co2':'all null','census_ward_population_totals':wards,'census_town_density_grouping':'pass','relative_document_links_checked':checked,'missing_relative_document_links':missing,'data_register_files_exist':19,'layouts':layout_checks,'png_visual_review':'three A4 maps inspected; map extent and scale bar repaired','portal_browser_review':'desktop layout and all map thumbnails inspected','demo_browser_checks':['base=100000, efficiency=0, pv=0 -> 42.10/42.10/42.10 t','base=100000, efficiency=20, pv=90000 -> 42.10/33.68/0 t','restored default -> 42.10/33.68/25.26 t']}
(root/'03_Theme_B/Common_Foundation/Sources/Quality_Checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
q.clear();os._exit(0)
