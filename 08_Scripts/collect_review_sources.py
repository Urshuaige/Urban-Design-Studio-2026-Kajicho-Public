#!/usr/bin/env python3
"""Collect the source records for the course-grounded integrative review."""
import argparse,json,re
from pathlib import Path
def main(root):
 d=Path(root)/"docs/Research_Review_2026-10-18";p=d/"phase2_sources"
 seeds=json.loads((p/"seed_sources.json").read_text())
 methods=json.loads((p/"methods_sources.json").read_text())["sources"]
 cases=json.loads((p/"global_cases.json").read_text())["cases"]
 sources=[]
 for s in seeds+methods:
  x=dict(s);x.setdefault("role","methods");x.setdefault("citation_apa",x["title"]);sources.append(x)
 for case in cases:
  for s in case["sources"]:
   citation=s.get("apa7",s["title"])
   year=re.search(r"\((\d{4}|n\.d\.)",citation)
   scope=s.get("read_scope","unknown")
   kind="limited_extract" if re.search(r"LIMITED|[Ss]earch.delivered|[Ss]earch.extracted|[Ss]earchable bilingual",scope) else "abstract_only" if re.search(r"[Aa]bstract.*only",scope) else "sections"
   sources.append({"slug":case["slug"]+"-"+s["id"].lower(),"case_id":case["slug"],"title":s["title"],"authors":[s.get("author","")],"year":int(year.group(1)) if year and year.group(1).isdigit() else None,"date_note":s.get("date"),"doi":s.get("doi"),"official_url":s["url"],"citation_apa":citation,"source_type":"Case evaluation or official implementation record","role":"cases","read_scope":kind,"read_scope_detail":scope,"locators":[scope],"verification":s.get("verification"),"metadata_note":s.get("metadata_note"),"source_id":s["id"]})
 assert len({s["slug"] for s in sources})==len(sources)
 for s in sources:
  assert s["official_url"].startswith(("https://","http://"))
  s["human_read_status"]="unknown"
  if s["read_scope"]=="sections" and not s.get("pdf_integrity") and (".pdf" in s.get("read_url","") or ".pdf" in s["official_url"] or "PDF" in s.get("read_scope_detail","")):
   s["locator_note"]="Use section/abstract locators; a retained structural PDF preflight was not provided for this record."
 (d/"Sources.json").write_text(json.dumps(sources,ensure_ascii=False,indent=2)+"\n")
 lines=["# Source reading matrix","","This table records the material actually inspected. It does not certify human reading, exhaustive coverage or source correctness. Full source annotations and search strings are in phase2_sources/.","","| Source | Role | Reading | Locator / scope |","| --- | --- | --- | --- |"]
 for s in sources:
  cell=lambda x:str(x).replace("|","/").replace("\n"," ")
  lines.append("| ["+cell(s["title"])+"]("+s["official_url"]+") | "+s["role"]+" | "+cell(s["read_scope"])+" | "+cell("; ".join(s.get("locators",[])))+" |")
 (d/"Read_Matrix.md").write_text("\n".join(lines)+"\n")
 print(json.dumps({"sources":len(sources),"case_studies":len(cases),"course_references":6,"source_types":"papers, methods and programme records; read scopes retained"}))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--team",required=True,type=Path);main(p.parse_args().team)
