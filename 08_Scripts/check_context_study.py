#!/usr/bin/env python3
"""Check context coverage, visible content inputs and map publication boundaries."""
import csv, json, re, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / '06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist'
STUDY = DIST / 'context-study'
data = json.loads((STUDY / 'context.json').read_text())
study_release = (DIST / 'study-atlas/atlas.json').is_file()
languages = ('zh', 'en', 'ja')
assert len(data['topics']) == 18
assert len(data['brief_checklist']) == 7
assert len({t['id'] for t in data['topics']}) == len(data['topics'])
for topic in data['topics']:
    for key in ('title', 'source_fact', 'local_meaning', 'design_response', 'scope', 'missing'):
        assert all(topic[key].get(l) for l in languages), (topic['id'], key)
    assert topic['evidence']
    assert all(e['url'].startswith('https://') and e.get('page') for e in topic['evidence'])
for item in data['brief_checklist']:
    assert all(item[k].get(l) for k in ('requirement', 'response') for l in languages)
assert len(data['metrics']) >= 5
assert len(data['charts']) == 7
for chart in data['charts']:
    for key in ('title', 'finding', 'method', 'limits'):
        assert all(chart[key].get(l) for l in languages), (chart['id'], key)
    if study_release and chart.get('presentation') == 'native_table':
        assert chart['id'] == '07_earthquake_risk', 'Only earthquake risk uses the native source-town matrix'
        assert not chart.get('file') and not chart.get('preview')
    else:
        assert chart['file'].endswith('.png')
        for key in ('file', 'preview'):
            assert (DIST / chart[key]).stat().st_size > 1000, chart[key]
    assert chart['rows'] and all(isinstance(row, list) for row in chart['rows'])
    assert all(len(row) == len(chart['headers']) for row in chart['rows'])
if study_release:
    from check_study_area_release import validate_seismic
    with (DIST / 'study-atlas/tables/census_intersections.csv').open(newline='',encoding='utf-8-sig') as source:
        seismic_units = validate_seismic(data['seismic'], list(csv.DictReader(source)))
    risk_chart = next(c for c in data['charts'] if c['id'] == '07_earthquake_risk')
    assert risk_chart.get('presentation') == 'native_table'
    assert len(risk_chart['rows']) == seismic_units
else:
    assert len(data['seismic']['rows']) == 2
    assert [r['collapse'] for r in data['seismic']['rows']] == ['4.15', '3.81']
    seismic_units = 2
assert data['no_new_cfd'] is True and data['map_export_formats'] == ['PNG']
assert not list(STUDY.rglob('*.svg'))
html = (DIST / 'index.html').read_text()
js = (DIST / 'portfolio.js').read_text()
assert 'context-filters' not in html and 'atlas-tabs' not in html
assert '<details' not in html and "el('details'" not in js
assert 'context-study/context.json' in js
assert 'renderContext()' in js and 'renderEvidence()' in js and 'renderMaps()' in js
public_text = '\n'.join(p.read_text() for p in STUDY.rglob('*.json') if not p.name.startswith('._'))
assert '/Users/' not in public_text and '/Volumes/' not in public_text
assert not re.search(r'"(?:host|pid|runtime)"\s*:', public_text)
if not data.get('boundary_release'):
    with zipfile.ZipFile(STUDY / 'Kajicho_Context_Study_2026-10-15_EN.zip') as archive:
        names = archive.namelist()
        assert not any('/._' in n or n.lower().endswith(('.svg', '.pdf', '.gpkg')) for n in names)
        assert archive.testzip() is None
assert max(p.stat().st_size for p in STUDY.rglob('*') if p.is_file() and not p.name.startswith('._')) < 25*1024*1024
print(json.dumps({'topics':18, 'brief_requirements':7, 'charts':7,
                  'languages':list(languages), 'earthquake_source_units':seismic_units, 'content_gates':0,
                  'private_execution_metadata':0, 'svg_maps':0, 'new_cfd':False}))
