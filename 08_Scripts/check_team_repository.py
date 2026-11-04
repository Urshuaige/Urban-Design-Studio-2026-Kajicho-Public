#!/usr/bin/env python3
"""Check portable shared files and source joins; this is not CFD validation."""
import csv,json,sqlite3,subprocess,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];checks={}
from build_layer_catalog import catalog
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
personal=[]
for name in tracked:
 # The root AGENTS.md is the portable shared policy; personal/nested variants remain excluded.
 if name == 'AGENTS.md':continue
 parts=Path(name).parts
 if (any(p in {'AGENTS.md','AGENTS.local.md','CLAUDE.md','GEMINI.md','.codex','.claude','.cursor','.openai','local','.local'} for p in parts)
     or name.startswith(('00_Start/','07_Team/Compute/','07_Team/Review/'))):personal.append(name)
assert not personal,personal
layers,fields=catalog(ROOT)
for filename,expected in [('Layer_Catalog.csv',layers),('Layer_Fields.csv',fields)]:
 with (ROOT/'04_Data/Metadata'/filename).open(encoding='utf-8',newline='') as stream:actual=list(csv.DictReader(stream))
 assert actual==[{k:str(v) for k,v in row.items()} for row in expected],filename+' is stale; run build_layer_catalog.py'
checks['shared_catalog']={'layers':len(layers),'fields':len(fields),'personal_files_tracked':0}
for name in ['Kajicho_CFD_Baseline_2026-10-14.qgz','Kajicho_Public_Baseline_2026-10-14.qgz']:
 p=ROOT/'05_QGIS/Projects'/name
 with zipfile.ZipFile(p) as archive:
  xml=ET.fromstring(archive.read(next(n for n in archive.namelist() if n.endswith('.qgs'))))
  sources=[node.text for node in xml.findall('.//projectlayers/maplayer/datasource')]
  for uri in sources:
   file=uri.split('|',1)[0];assert not Path(file).is_absolute(),(name,file);assert (p.parent/file).exists(),(name,file)
 checks[name]={'relative_data_sources':len(sources)}
folder=ROOT/'04_Data/Ready/CFD_Baseline_2026-10-14';db=sqlite3.connect((folder/'Kajicho_CFD_Baseline.gpkg').resolve().as_uri()+'?mode=ro',uri=True)
assert db.execute('pragma integrity_check').fetchone()[0]=='ok';tables={r[0] for r in db.execute('select table_name from gpkg_contents')};assert len(tables)==45,len(tables)
for table,count in [('cfd_context_buildings',3805),('cfd_roof_scenarios',277),('far26_review',26),('street_trees_extended',901)]:assert db.execute(f'select count(*) from {table}').fetchone()[0]==count
rows=json.loads((folder/'FAR26_Official_Review.json').read_text());assert len({r['building_id'] for r in rows})==26;assert sum(r['review_class']=='crosses official FAR boundary' for r in rows)==25
city=json.loads((ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data/cfd-context.json').read_text());ids={b['id'] for b in city['buildings']};assert len(ids)==3805;assert sum(b['core'] for b in city['buildings'])==277;assert all(b['actual_electricity_kwh'] is None for b in city['buildings'])
assert {r['building_id'] for r in rows}.issubset(ids)
checks['source_joins']={'objects':3805,'core':277,'far_review':26,'actual_energy':'missing, preserved as null'}
print(json.dumps(checks,ensure_ascii=False,indent=2))
