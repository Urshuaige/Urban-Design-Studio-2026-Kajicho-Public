#!/usr/bin/env python3
"""Synchronize current delivery labels, member totals and team instructions."""
import argparse,json,re,sqlite3
from pathlib import Path
DRIVE="https://drive.google.com/file/d/1zSJaSWM6WXMdMsgJQJG5Nd6M9kechosz/view"
REPO="https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho"
def apply(task_root):
 root=Path(task_root);team=root/"team";dist=root/"site/dist";out=team/"06_Outputs/Study_Area_2026-10-18"
 atlas=json.loads((out/"atlas.json").read_text());w=atlas["scopes"]["study_area"];p=atlas["scopes"]["primary_brief"]
 c=sqlite3.connect(team/"04_Data/Ready/Study_Area_2026-10-18/Kanda_Nihonbashi_Study.gpkg");layers=c.execute("select count(*) from gpkg_geometry_columns").fetchone()[0];c.close()
 js=dist/"team.js";s=js.read_text()
 s=re.sub(r"const packageUrl=.*?;",lambda m:"const packageUrl="+json.dumps(DRIVE)+";",s,count=1)
 dc={"en":["Get current maps & GIS · Drive","ZIP · 18 Oct 2026 · Current Figure 5 maps, GIS, tables and source code.","Current source · GitHub","Back to the site atlas"],"zh":["领取当前地图与 GIS · Drive","ZIP · 2026-10-18 · 当前 Figure 5 地图、GIS、表格和源码。","当前源码 · GitHub","返回场地图集"],"ja":["現在の地図とGIS · Drive","ZIP · 2026-10-18 · 現在の図5地図・GIS・集計・ソース。","現在のソース · GitHub","敷地アトラスへ戻る"]}
 start=s.index("const downloadCopy=");end=s.index(";\nconst copy=",start)
 s=s[:start]+"const downloadCopy="+json.dumps(dc,ensure_ascii=False)+s[end:]
 start=s.index("const currentScopeCopy=")+len("const currentScopeCopy=");data,used=json.JSONDecoder().raw_decode(s[start:])
 strict={"en":"Only complete footprints fully covered by the official trace; boundary-crossing models excluded. Actual energy remains missing.","zh":"仅纳入投影完整位于任务书边线内的模型，跨界模型排除。真实用能仍缺失。","ja":"課題書境界に完全に含まれる投影のみを採用。境界を跨ぐモデルは除外。実エネルギーは未取得。"}
 for lang,v in data.items():
  v["rows"][0][1]={"en":f"{layers} spatial layers + membership table","zh":f"{layers} 个空间图层＋成员表","ja":f"{layers} 空間レイヤー＋対応表"}[lang]
  v["rows"][1][1]={"en":f"{w['selected_models']:,} wider / {p['selected_models']} primary model objects","zh":f"外围 {w['selected_models']:,}／重点 {p['selected_models']} 个模型","ja":f"周辺{w['selected_models']:,}／重点{p['selected_models']}モデル"}[lang]
  v["rows"][1][2]=strict[lang]
  v["steps"][2]={"en":["Use the analysis layers","Select analysis_buildings_wider or analysis_buildings_primary. Raw surroundings are context; do not add them to building totals."],"zh":["使用分析建筑图层","选用 analysis_buildings_wider 或 analysis_buildings_primary。原始周边建筑仅作背景，不计入建筑统计。"],"ja":["解析用の建物レイヤーを使う","analysis_buildings_wider又はanalysis_buildings_primaryを選ぶ。周辺原データは背景であり集計対象外。"]}[lang]
  v["footer"]={"en":"Updated 18 Oct 2026 · Current maps and GIS · Pilot and team roles remain open","zh":"更新于 2026-10-18 · 当前地图与 GIS · 试点和分工待团队确定","ja":"2026-10-18更新・現在の地図とGIS・試行地点と役割はチームで検討"}[lang]
 s=s[:start]+json.dumps(data,ensure_ascii=False)+s[start+used:]
 s=s.replace("TEAM START / 2026-10-16","TEAM START / 2026-10-18")
 s=s.replace("{zh:'场地研究与数据图表',en:'Context study and charts',ja:'地域研究とデータ図表'}[lang],\""+REPO+"/archive/refs/heads/main.zip\"","{zh:'查看当前场地图集',en:'Explore current site maps',ja:'現在の地図を見る'}[lang],\"index.html#mapping\"")
 js.write_text(s)
 ctx=json.loads((dist/"context-study/context.json").read_text())
 for metric in ctx["metrics"]:
  if metric["label"]["en"]=="Wider-area models":metric["note"]=strict
 for chart in ctx["charts"][:5]:
  chart["method"]={"en":"Building totals use full-footprint containment within each Figure 5 trace. Land and planning polygons use boundary intersections.","zh":"建筑总数按完整投影是否位于 Figure 5 边线内筛选。用地与规划面采用边界相交。","ja":"建物は図5境界への投影全体の包含で抽出。土地・計画ポリゴンは境界との重なりを用いる。"}
 (dist/"context-study/context.json").write_text(json.dumps(ctx,ensure_ascii=False,indent=2)+"\n")
 (dist/"context-study/README.md").write_text(f"# Current Figure 5 mapping\n\nUpdated 18 October 2026. Wider: {w['selected_models']} fully contained models. Primary: {p['selected_models']}.\nThe official solid and dashed source traces remain unchanged. Analysis requires exact containment of the whole source projection. Crossing/exterior buildings are grey context and excluded from totals.\n\nCurrent maps/GIS: {DRIVE}\nCurrent source: {REPO}\n")
 registry_path=team/"docs/Current_Delivery.json";previous=json.loads(registry_path.read_text()) if registry_path.exists() else {}
 previous_doc=(team/"docs/CURRENT_DELIVERY.md").read_text()
 receipt_footer=previous_doc[previous_doc.index("\n[Cloud delivery receipt]"):] if "\n[Cloud delivery receipt]" in previous_doc else ""
 registry={"date":"2026-10-18","package_url":DRIVE,"source_url":REPO,"qgis":"05_QGIS/Projects/Kanda_Nihonbashi_Study_2026-10-18.qgz","gis":"04_Data/Ready/Study_Area_2026-10-18/Kanda_Nihonbashi_Study.gpkg","maps":"06_Outputs/Study_Area_2026-10-18/maps","building_rule":"Exact covers(full footprint); original geometry unchanged","wider_models":w["selected_models"],"primary_models":p["selected_models"],"spatial_layers":layers,"analysis_layers":["analysis_buildings_wider","analysis_buildings_primary"],"context_role":"Raw surroundings are retained separately; excluded from current building statistics.","archive_policy":"One current Drive ZIP. Superseded generated packages and map exports removed from active delivery."}
 if previous.get("package_url")==DRIVE:
  for key in ("delivery_receipt","package_source_commit","drive_write_status"):
   if key in previous:registry[key]=previous[key]
 (team/"docs/Current_Delivery.json").write_text(json.dumps(registry,indent=2)+"\n")
 (team/"docs/CURRENT_DELIVERY.md").write_text(f"# Current team delivery\n\nUpdated 18 October 2026. [Get the current maps and GIS]({DRIVE}). [Current source and documentation]({REPO}).\n\nExtract the ZIP once. Open {registry['qgis']} while keeping the folder tree intact. Use analysis_buildings_wider ({w['selected_models']} objects) or analysis_buildings_primary ({p['selected_models']} objects). Every analysis footprint is fully covered by its Figure 5 outline. Buildings that cross or lie outside the line are context only.\n\nThe ten PNG exports, tables and portable GIS share these members. CURRENT_RELEASE.json inside the downloaded package identifies the exact source commit. There is one current map package; dated numerical evidence in the repository retains its original experiment inputs.\n\n[Excluded-building audit](../06_Outputs/Study_Area_2026-10-18/tables/excluded_buildings.csv) · [Boundary source and method](COURSE_BOUNDARIES.md)\n")
 (team/"docs/CURRENT_DELIVERY.md").write_text((team/"docs/CURRENT_DELIVERY.md").read_text()+receipt_footer)
 return registry
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--task-root",required=True);args=p.parse_args();print(json.dumps(apply(args.task_root),indent=2))
