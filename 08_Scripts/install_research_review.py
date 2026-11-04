#!/usr/bin/env python3
"""Install the assignment-led visual review after map assembly, before the outline."""
import argparse,json,re,shutil
from pathlib import Path

REV="20261018-review"
REPORT="https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho/blob/main/docs/Research_Review_2026-10-18/REPORT.md"
TEASER='''<section class="folio-section" id="research-review"><div class="section-head"><span class="number">06</span><div><p class="kicker">SHARED KNOWLEDGE</p><h2 data-r="navReview">Research review</h2></div><p data-r="intro">A shared basis for interdisciplinary discussion.</p></div><div class="review-teaser"><div><h3 data-r="teaserTitle">A common basis for the next design decision</h3><p data-r="teaserBody">Six technical paths connect theory, data and implementation. Eight practice cases show what to borrow and what to check locally.</p></div><div><div class="review-mini-flow"><b data-r="theoryShort">Theory</b><span aria-hidden="true">→</span><b data-r="methodsShort">Methods</b><span aria-hidden="true">→</span><b data-r="practiceShort">Practice</b></div><p><a class="folio-link" href="research.html" data-r="teaserLink">Explore the visual review →</a></p><a class="folio-link" href="'''+REPORT+'''" data-r="teaserFull">Full report on GitHub ↗</a></div></div></section>'''
def apply(task_root):
 root=Path(task_root);team=root/"team";dist=root/"site/dist";modules=team/"08_Scripts/site_modules";doc=team/"docs/Research_Review_2026-10-18"
 for n in ("research.html","research.js","research.css"):shutil.copy2(modules/n,dist/n)
 data={"visual":json.loads((doc/"Visual_Review.json").read_text()),"sources":json.loads((doc/"Sources.json").read_text())}
 (dist/"research-data.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
 pages=[]
 for name in ("index.html","team.html","cfd.html","studies.html","style-guide.html"):
  p=dist/name;s=p.read_text()
  # Remove this installer’s previous tags/section before reapplying.
  s=re.sub(r'<link\b[^>]*href="research\.css[^"]*"[^>]*>','',s)
  s=re.sub(r'<script\b[^>]*src="research\.js[^"]*"[^>]*>\s*</script>','',s)
  s=re.sub(r'<a\b[^>]*data-review-link[^>]*>.*?</a>','',s,flags=re.S)
  s=re.sub(r'<section\b[^>]*id="research-review"[^>]*>.*?</section>','',s,flags=re.S)
  link='<a href="research.html" data-review-link data-r="navReview">Research review</a>'
  s=re.sub(r'</nav>',lambda m:link+m.group(),s,count=1)
  s=s.replace("</body>",'<script type="module" src="research.js?v='+REV+'"></script></body>')
  if name=="index.html":
   s=s.replace("</head>",'<link rel="stylesheet" href="research.css?v='+REV+'"></head>')
   s=s.replace('<section class="folio-download" id="downloads">',TEASER+'\n<section class="folio-download" id="downloads">')
  p.write_text(s);pages.append(name)
 return {"review":"research.html","linked_pages":pages,"sources":len(data["sources"]),"tracks":len(data["visual"]["tracks"]),"cases":len(data["visual"]["cases"])}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--task-root",required=True);a=p.parse_args();print(json.dumps(apply(a.task_root),indent=2))
