#!/usr/bin/env python3
"""Install the Sunday field companion and spatial source register."""
from pathlib import Path
import argparse,json,re,shutil
def apply(task_root):
 root=Path(task_root);team=root/'team';dist=root/'site/dist';modules=team/'08_Scripts/site_modules'
 from build_sunday_fieldwork import build
 build(root)
 for name in ('fieldwork.html','fieldwork.css','fieldwork.js'):shutil.copy2(modules/name,dist/name)
 target=dist/'fieldwork'
 if target.exists():shutil.rmtree(target)
 shutil.copytree(team/'06_Outputs/Community_Fieldwork_2026-10-25',target)
 for page in ('index.html','team.html','plan.html'):
  p=dist/page;s=p.read_text()
  s=re.sub(r'<aside\b[^>]*data-fieldwork-teaser[^>]*>.*?</aside>','',s,flags=re.S)
  teaser='<aside data-fieldwork-teaser><a href="fieldwork.html">Sunday 25 Oct · community map &amp; field guide / 周日走访地图与中日提问 / 日曜の調査ガイド →</a></aside>'
  s=re.sub(r'(<main\b[^>]*>)',lambda m:m.group(1)+teaser,s,count=1)
  if 'fieldwork-teaser.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="fieldwork-teaser.css?v=20261021"></head>')
  p.write_text(s)
 (dist/'fieldwork-teaser.css').write_text('[data-fieldwork-teaser]{border-left:4px solid #246d69;background:#eeebe4;padding:18px 22px;margin:24px 0;font:600 17px/1.7 var(--font-ui,sans-serif)}[data-fieldwork-teaser] a{color:#59457f}')
 guide=json.loads((target/'guide.json').read_text())
 return {'page':'fieldwork.html','visit_date':guide['visit_date'],'places':len(guide['places']),'contacts':len(guide['contacts']),'questions':len(guide['questions']),'new_simulations':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--task-root',required=True);args=p.parse_args();print(json.dumps(apply(args.task_root),indent=2))
