#!/usr/bin/env python3
"""Install the current LOD2 scene and the planning-only environmental work unit."""
import argparse,json,re,shutil
from pathlib import Path
def apply(task_root):
 root=Path(task_root);team=root/"team";dist=root/"site/dist";modules=team/"08_Scripts/site_modules";docs=team/"docs/Environmental_Work_Plan_2026-10-20"
 for n in ("plan.html","studies.html","work-plan.css","work-plan.js","current-model.js"):shutil.copy2(modules/n,dist/n)
 shutil.copy2(docs/"Plan.json",dist/"work-plan.json")
 evidence=json.loads((docs/"Methods_Evidence.json").read_text())
 sources=[{"id":r["id"],"title":r["title"],"year":r.get("publication_year"),"url":r.get("read_url") or r.get("url") or r.get("official_index"),"read_scope":r.get("read_scope",""),"locators":r.get("locators",[])} for r in evidence["source_records"]]
 for source in sources:
  source["read_scope"]=source["read_scope"].replace("abstract_only","Abstract only").replace("CFDrequirements","CFD requirements")
  source["locators"]=[v.replace("CFDrequirements","CFD requirements").replace("printedpp.","printed pp.").replace("UsingwindtunnelandCFDincombination","Wind tunnel and CFD in combination").replace("Volume269","Volume 269").replace("article106321","article 106321").replace("v in10m","v at 10 m").replace("Necessaryrequirements","Necessary requirements").replace("Connected/semi-connected/disconnectedstates","Connection states") for v in source["locators"]]
 assert all(str(s["url"]).startswith("https://") for s in sources)
 (dist/"work-plan-sources.json").write_text(json.dumps(sources,ensure_ascii=False,indent=2)+"\n")
 target=dist/"current-model";target.mkdir(exist_ok=True)
 src=team/"04_Data/Ready/PLATEAU_Highest_2026-10-20"
 for n in ("kajicho-current-untextured.glb","geometry-summary.json","geometry-index.json","detail_examples.json","geometry_quality.json","projection_boundary_quality.json"):
  assert (src/n).is_file(), "Missing model source/check: "+n
  shutil.copy2(src/n,target/n)
 data=json.loads((team/"06_Outputs/Study_Area_2026-10-18/study_boundary_6677.geojson").read_text())
 boundary={"crs":"Local metres from EPSG6677 origin[-5600,-34320]; z=-northing_delta","features":[{"id":f["properties"]["id"],"geometry_sha256":f["properties"]["geometry_sha256"],"coordinates":[[e+5600,-(n+34320)] for e,n in f["geometry"]["coordinates"][0]]} for f in data["features"]]}
 (target/"boundaries.json").write_text(json.dumps(boundary,separators=(",",":"))+"\n")
 # Root uses the same pinned Three.js release as the retained Site source.
 assert (dist/"vendor/GLTFLoader.js").is_file(), "Pinned Three.js r180 GLTFLoader is required"
 teaser='<aside class="work-status" data-environment-teaser><b data-next-label="title">Next studio work</b> · <a href="plan.html" data-next-label="plan">Fieldwork, heat and CFD work plan →</a> · <a href="studies.html" data-next-label="model">Current LOD2 model →</a></aside>'
 for n in ("index.html","research.html","team.html","cfd.html"):
  p=dist/n;s=p.read_text();s=re.sub(r'<aside\b[^>]*data-environment-teaser[^>]*>.*?</aside>','',s,flags=re.S)
  s=re.sub(r'(<main\b[^>]*>)',lambda m:m.group(1)+teaser,s,count=1)
  s=re.sub(r'<link\b[^>]*href="work-plan\.css[^"]*"[^>]*>','',s)
  s=re.sub(r'<script\b[^>]*src="work-plan\.js[^"]*"[^>]*>\s*</script>','',s)
  s=s.replace("</head>",'<link rel="stylesheet" href="work-plan.css?v=20261020"></head>')
  s=s.replace("</body>",'<script type="module" src="work-plan.js?v=20261020"></script></body>')
  if n=="cfd.html":
   cleanup='<p class="work-status" data-cfd-cleanup><span data-next-label="cleanup">20 October: obsolete native CFD fields and meshes removed. The retained teaching snapshots remain unconverged.</span> <a href="https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho/blob/main/docs/Environmental_Work_Plan_2026-10-20/CLEANUP.md" data-next-label="cleanupLink">Cleanup record ↗</a></p>'
   s=re.sub(r'<p\b[^>]*data-cfd-cleanup[^>]*>.*?</p>','',s,flags=re.S)
   s=s.replace(teaser,teaser+cleanup)
  p.write_text(s)
 # Current team membership is confirmed; pilot, roles and intervention remain team decisions.
 p=dist/"team.js";s=p.read_text().replace("TEAM START / 2026-10-18","TEAM START / 2026-10-20");p.write_text(s)
 summary=json.loads((target/"geometry-summary.json").read_text())
 return {"model_objects":summary["buildings"],"actual_lod":summary["actual_lod_counts"],"new_environmental_simulation":False,"plan":"plan.html","model":"studies.html"}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--task-root",required=True);a=p.parse_args();print(json.dumps(apply(a.task_root),indent=2))
