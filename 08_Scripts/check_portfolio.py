#!/usr/bin/env python3
"""Verify deployable portfolio resources and map evidence joins without running models."""
import ast,json,re,zipfile
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/study-atlas/atlas.json').exists():
 import runpy
 runpy.run_path(str(ROOT/'08_Scripts/check_study_area_release.py'), run_name='__main__')
 raise SystemExit(0)

if (ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/boundary-atlas/atlas.json').exists():
 import runpy
 runpy.run_path(str(ROOT/'08_Scripts/check_boundary_release.py'))
 raise SystemExit(0)

SITE=ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.paths=[]
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ['src','href'] and value:self.paths.append(value)
missing=[]
for page in ['index.html','team.html','studies.html','cfd.html','style-guide.html']:
 parser=Links();parser.feed((SITE/page).read_text())
 for value in parser.paths:
  p=urlsplit(value)
  if p.scheme or not p.path:continue
  if not (SITE/unquote(p.path)).is_file():missing.append((page,value))
assert not missing,missing
context=json.loads((SITE/'portfolio/research/context.json').read_text())['records']
assert len(context)==12
for r in context:
 assert r['source_url'].startswith('https://')
 for k in ['title','summary','scope','gap']:assert all(r[k].get(l) for l in ['zh','en','ja']),(r['id'],k)
atlas=json.loads((SITE/'portfolio/mapping_data/atlas.json').read_text())
manifest=json.loads((SITE/'portfolio/mapping_data/map_manifest.json').read_text())
assert atlas['counts']['core_buildings']==manifest['counts']['core_buildings']==277
assert atlas['counts']['core_known_use']==250
assert atlas['counts']['core_height_proxy']==16
assert len(atlas['plates'])==7
for plate in atlas['plates']:
 for ext in ['png']:
  assert (SITE/'portfolio/maps'/f"{plate['id']}.{ext}").stat().st_size>1000
 assert (SITE/'portfolio/maps/previews'/f"{plate['id']}.jpg").stat().st_size>1000
assert not list((SITE/'portfolio/maps').rglob('*.svg')), 'SVG map output is prohibited'
producer=ast.parse((ROOT/'08_Scripts/build_portfolio_maps.py').read_text())
assert not any(isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.endswith('.svg') for n in ast.walk(producer)), 'Map producer must not export SVG'
assert all('svg' not in plate for plate in atlas['plates'])
assert manifest['map_export_formats']==['PNG']
assert manifest['no_new_cfd'] is True
assert 'host' not in manifest and 'pid' not in manifest
for url in re.findall(r'url\([\'\"]?(\./fonts/[^)\'\"]+)',(SITE/'typography.css').read_text()):
 assert (SITE/url).is_file(),url
assert 'unicode-range' in (SITE/'typography.css').read_text()
assert 'size-adjust' in (SITE/'typography.css').read_text()
with zipfile.ZipFile(SITE/'portfolio/Kajicho_Field_Atlas_2026-10-15.zip') as z:
 assert len(z.namelist())==15
 assert not any('/._' in n or '__MACOSX' in n for n in z.namelist())
 assert not any(n.lower().endswith('.svg') for n in z.namelist()), 'SVG map found in download ZIP'
 assert len([n for n in z.namelist() if '/maps/' in n and n.endswith('.png')])==7
 assert z.testzip() is None
assert max(p.stat().st_size for p in SITE.rglob('*') if p.is_file() and not p.name.startswith('.'))<25*1024*1024
print(json.dumps({'html_links':'passed','context_records':12,'languages':['zh','en','ja'],'plates':7,'core_buildings':277,'known_use':250,'height_proxy':16,'font_assets':'present','zip_members':15,'asset_size_limit':'passed','new_cfd':False},indent=2))
