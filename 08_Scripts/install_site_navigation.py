#!/usr/bin/env python3
"""Install one global menu, explicit parent/siblings and a separate local outline."""
import argparse,re,shutil,json
from pathlib import Path
REV="20261021-fieldwork"
PAGES={
 "index.html":("atlas",None),
 "research.html":("research",None),
 "plan.html":("studies","plan"),
 "studies.html":("studies","parameters"),
 "cfd.html":("studies","cfd"),
 "team.html":("team",None),
 "style-guide.html":("team","style"),
 "fieldwork.html":("team","visit"),
}
LABELS={"atlas":"Atlas","research":"Research review","studies":"Studies","team":"Team desk","parameters":"Current 3D model","plan":"Work plan","cfd":"CFD diagnostics","style":"Type & maps","visit":"Sunday visit"}
URLS={"atlas":"index.html","research":"research.html","studies":"studies.html","team":"team.html","parameters":"studies.html","plan":"plan.html","cfd":"cfd.html","style":"style-guide.html","visit":"fieldwork.html"}
def a(key,current=False):
 return '<a href="'+URLS[key]+'" data-site-label="'+key+'"'+(' aria-current="page"' if current else '')+'>'+LABELS[key]+'</a>'
def header(page):
 parent,child=PAGES[page]
 nav=''.join(a(k,k==parent).replace('aria-current="page"','aria-current="true"') if child and k==parent else a(k,k==parent) for k in ("atlas","research","studies","team"))
 bread='<a href="index.html" data-site-label="home">Kajicho</a><span class="site-separator" aria-hidden="true">/</span>'
 bread+=a(parent,not child)
 if child:bread+='<span class="site-separator" aria-hidden="true">/</span>'+a(child,True)
 siblings=("parameters","plan","cfd") if parent=="studies" else ("team","visit","style") if parent=="team" else ()
 below='<nav class="site-siblings" aria-label="Pages in this section"><span data-site-label="siblingsLabel">Pages in this section</span>'+''.join(a(k,k==(child or parent)) for k in siblings)+'</nav>' if siblings else '<span class="site-local-hint" data-site-label="local">Sections on this page: use the left outline</span>'
 return '<header class="site-header" data-page-header><div class="site-main-row"><a class="site-brand" href="index.html"><b lang="ja">鍛冶町</b><span>KAJICHO<br>URBAN DESIGN STUDIO · 2026</span></a><nav class="site-global-nav" aria-label="Main pages">'+nav+'</nav><div class="site-languages languages folio-languages" aria-label="Language"><button data-lang="en" aria-pressed="true">EN</button><button data-lang="zh" aria-pressed="false">中</button><button data-lang="ja" aria-pressed="false">日</button></div></div><div class="site-location-row"><nav class="site-breadcrumb" aria-label="You are here">'+bread+'</nav>'+below+'</div></header>'
def apply(task_root):
 root=Path(task_root);dist=root/"site/dist";modules=root/"team/08_Scripts/site_modules"
 for name in ("site-navigation.css","site-navigation.js"):shutil.copy2(modules/name,dist/name)
 for page in PAGES:
  p=dist/page;s=p.read_text()
  # The large dated scope notice previously appeared ahead of the global menu.
  # Current spatial scope remains in the atlas and archived model notes.
  s=re.sub(r'<aside class="course-scope-note".*?</aside>','',s,flags=re.S)
  s=re.sub(r'<header\b[^>]*>.*?</header>',lambda m:header(page),s,count=1,flags=re.S)
  s=re.sub(r'<link\b[^>]*href="site-navigation\.css[^"]*"[^>]*>','',s)
  s=re.sub(r'<script\b[^>]*src="site-navigation\.js[^"]*"[^>]*>\s*</script>','',s)
  s=s.replace("</head>",'<link rel="stylesheet" href="site-navigation.css?v='+REV+'"></head>')
  s=s.replace("</body>",'<script type="module" src="site-navigation.js?v='+REV+'"></script></body>')
  if '<body class="' in s:s=s.replace('<body class="','<body class="site-reading ',1) if 'site-reading' not in s else s
  else:s=s.replace("<body>",'<body class="site-reading">',1)
  p.write_text(s)
 app=dist/"app.js";text=app.read_text();text=text.replace("for(const id of [\'sourcesBtn\',\'methodsLink\'])$(id).addEventListener","for(const id of [\'sourcesBtn\',\'methodsLink\'])$(id)?.addEventListener");app.write_text(text)
 return {"global_pages":list(PAGES),"top_level":["Atlas","Research review","Studies","Team desk"],"nested":{"Studies":["Current 3D model","Work plan","CFD diagnostics"],"Team desk":["Team desk","Sunday visit","Type & maps"]}}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--task-root",required=True);args=p.parse_args();print(json.dumps(apply(args.task_root),indent=2))
