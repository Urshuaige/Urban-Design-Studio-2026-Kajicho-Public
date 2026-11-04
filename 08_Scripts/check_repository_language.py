#!/usr/bin/env python3
"""Check English entry points, language links and portable documentation paths."""
import csv,json,re,subprocess
from pathlib import Path
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]
files=[n for n in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0') if n]
assert all(n.isascii() for n in files),'Use ASCII filenames; keep original names in source metadata.'
for name in ('README.md','README.zh-CN.md','README.ja.md'):
    text=(ROOT/name).read_text()
    for other in ('README.md','README.zh-CN.md','README.ja.md'):
        if name!=other:assert f']({other})' in text,(name,other)
assert 'Shared data, QGIS projects' in (ROOT/'README.md').read_text()
missing=[]
for name in files:
    p=ROOT/name
    if p.suffix!='.md' or not p.is_file():continue
    text=p.read_text()
    for target in re.findall(r'\]\(([^)]+)\)',text):
        target=target.strip('<>')
        u=urlsplit(target)
        if u.scheme or not u.path or '<' in target:continue
        if not (p.parent/unquote(u.path)).exists():missing.append([name,target])
assert not missing,missing
dist=ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist'
for name in ('portfolio.js','team.js','app.js','cfd.js','style-guide.html'):
    text=(dist/name).read_text()
    assert re.search(r"getItem\(['\"]kajicho-language-20261017['\"]\)\s*\|\|\s*['\"]en['\"]",text),name
    assert 'setItem' in text,name
for name,columns in [('07_Team/Task_Queue.csv',['task_en','first_output_en','done_when_en']),('docs/HANDOVER_MANIFEST.csv',['use_en','interpretation_en']),('07_Team/Demo_Workstreams.csv',['description_en','scope','first_output'])]:
    with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    assert rows and all(r.get(c) for r in rows for c in columns),name
print(json.dumps({'readme_languages':['en','zh-CN','ja'],'ascii_filenames':True,'local_markdown_links':'passed','web_default':'en','saved_language_preserved':True,'english_task_tables':3}))
