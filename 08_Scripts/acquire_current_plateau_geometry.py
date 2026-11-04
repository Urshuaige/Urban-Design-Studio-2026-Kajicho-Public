#!/usr/bin/env python3
"""Acquire highest available outdoor building geometry without textures; remote only."""
import argparse,concurrent.futures,datetime,hashlib,json,math,urllib.parse,urllib.request
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument("--task-root",type=Path,required=True);p.add_argument("--workers",type=int,required=True);a=p.parse_args()
 D=a.task_root/"raw/plateau/Highest_Geometry_2026-10-20";D.mkdir(exist_ok=True,parents=True);jobs=[];catalogs=[]
 B=[math.radians(x) for x in [139.7685,35.6868,139.777,35.6965]]
 for ward in ["13101","13102"]:
  for spec in ["lod2-notexture-latest","lod3-notexture-latest","maxlod4-notexture-latest","maxlod4-latest","lod3-latest","lod4-latest"]:
   u=f"https://api.plateauview.mlit.go.jp/datacatalog/3dtiles/{ward}-bldg-{spec}/tileset.json";name=f"{ward}_{spec}_catalog.json";dest=D/name
   if not dest.exists():dest.write_bytes(urllib.request.urlopen(u).read())
   j=json.loads(dest.read_text());catalogs.append({"query":u,"file":name,"resolved_uris":[x["content"]["uri"] for x in j["root"].get("children",[])],"sha256":hashlib.sha256(dest.read_bytes()).hexdigest()})
  selected=json.loads((D/f"{ward}_lod2-notexture-latest_catalog.json").read_text());u=selected["root"]["children"][0]["content"]["uri"];dest=D/f"{ward}_lod2_tileset.json"
  if not dest.exists():dest.write_bytes(urllib.request.urlopen(u).read())
  t=json.loads(dest.read_text())
  def walk(n):
   r=n.get("boundingVolume",{}).get("region",[])
   if r and (r[2]<B[0] or r[0]>B[2] or r[3]<B[1] or r[1]>B[3]):return
   if n.get("children"):
    for c in n["children"]:walk(c)
   elif "content" in n:jobs.append((ward,urllib.parse.urljoin(u,n["content"]["uri"])))
  walk(t["root"])
 def get(job):
  ward,u=job;dest=D/(ward+"_"+u.rsplit("/",1)[-1])
  if not dest.exists():dest.write_bytes(urllib.request.urlopen(u).read())
  return {"ward":ward,"url":u,"file":dest.name,"bytes":dest.stat().st_size,"sha256":hashlib.sha256(dest.read_bytes()).hexdigest()}
 with concurrent.futures.ThreadPoolExecutor(max_workers=min(a.workers,len(jobs))) as ex:results=list(ex.map(get,jobs))
 receipt={"date":"2026-10-20","bbox_lonlat":[139.7685,35.6868,139.777,35.6965],"fetch_policy":"Existing original files are reused; each downloaded tile is a checkpoint. No automatic substitution for a failed source.","catalogs":catalogs,"tiles":results,"total_bytes":sum(x["bytes"] for x in results)}
 (D/"acquisition_receipt.json").write_text(json.dumps(receipt,indent=2));print(json.dumps({"tiles":len(results),"bytes":receipt["total_bytes"],"receipt":str(D/"acquisition_receipt.json")}))
if __name__=="__main__":main()
