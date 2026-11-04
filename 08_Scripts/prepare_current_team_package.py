#!/usr/bin/env python3
"""Prepare the current shared tree on a cloud/remote host; no local delivery copy."""
import argparse,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CURRENT_PROJECT="05_QGIS/Projects/Kanda_Nihonbashi_Study_2026-10-18.qgz"
def main(output):
 out=Path(output);out.mkdir(parents=True,exist_ok=False)
 sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 tracked=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
 copied=[]
 for name in tracked:
  if not name:continue
  if name.startswith(("06_Outputs/Boundary_Atlas_2026-10-16/","04_Data/Ready/Course_Boundaries_2026-10-16/","09_Archive/","06_Outputs/Simulation_Demo/")):continue
  if name.startswith("05_QGIS/Projects/") and name!=CURRENT_PROJECT:continue
  if name.startswith("06_Outputs/Context_Study_2026-10-15/") and "/figures/" in name and "06_observed_heat" not in name:continue
  src=ROOT/name
  if not src.is_file():continue
  dst=out/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);copied.append(name)
 atlas=json.loads((out/"06_Outputs/Study_Area_2026-10-18/atlas.json").read_text())
 quality=json.loads((out/"06_Outputs/Study_Area_2026-10-18/quality_checks.json").read_text())
 release={"source_commit":sha,"date":"2026-10-18","boundary_authority":"Official brief Figure 5","building_membership":"Exact covers of full source footprint; no clipping or outline change","primary_models":atlas["scopes"]["primary_brief"]["selected_models"],"wider_models":atlas["scopes"]["study_area"]["selected_models"],"maps_png":10,"current_qgis":CURRENT_PROJECT,"quality_checks":quality,"files":len(copied),"scope_note":"Dated background/weather and archived CFD evidence remain source records; current analysis uses the named study project."}
 (out/"CURRENT_RELEASE.json").write_text(json.dumps(release,indent=2)+"\n")
 (out/"START_HERE.txt").write_text("KAJICHO CURRENT TEAM PACKAGE | 18 OCT 2026\n\nExtract this ZIP once and keep the folder tree intact.\nOpen "+CURRENT_PROJECT+"\n\nUse analysis_buildings_wider / analysis_buildings_primary for current building analysis.\nOnly complete source footprints within each Figure 5 outline are members.\nRaw/context buildings are a separate background; do not count them as members.\nCurrent maps and statistics: 06_Outputs/Study_Area_2026-10-18/\nWebsite: https://kajicho-wind-heat-carbon-demo.specialgooood.chatgpt.site\nWebsite source: GitHub main / 06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist (excluded here to avoid duplicate maps and archived field assets)\nFull research review: docs/Research_Review_2026-10-18/REPORT.md\n\nWider models: "+str(release["wider_models"])+" | Primary models: "+str(release["primary_models"])+"\nSource main commit: "+sha+"\nCurrent package entry: https://drive.google.com/file/d/1zSJaSWM6WXMdMsgJQJG5Nd6M9kechosz/view\n")
 assert len(list((out/"06_Outputs/Study_Area_2026-10-18/maps").glob("*.png")))==10
 assert list((out/"05_QGIS/Projects").glob("*.qgz"))==[out/CURRENT_PROJECT]
 assert not list((out/"06_Outputs/Study_Area_2026-10-18/maps").rglob("*.svg"))
 print(json.dumps({"source_commit":sha,"files":len(copied),"maps":10,"models":release["wider_models"],"current_project":CURRENT_PROJECT}))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);a=p.parse_args();main(a.output)
