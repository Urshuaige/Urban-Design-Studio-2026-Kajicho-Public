#!/usr/bin/env python3
"""Update the shared entrypoints and catalogs for the registered boundary release."""
import csv,json,sqlite3,shutil,subprocess,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'06_Outputs/Boundary_Atlas_2026-10-16';SITE=ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist'
atlas=json.loads((OUT/'atlas.json').read_text());map_count=len(atlas['plates']);theme_count=sum(p.get('kind')=='theme' for p in atlas['plates']);release_date=atlas.get('presentation_date','2026-10-16')
data=json.loads((OUT/'statistics.json').read_text());s=data['scopes'];primary=s['primary_brief'];wider=s['secondary_brief'];poster=s['poster_blue']
doc=f'''# Course areas and current data

{release_date}. The current course atlas covers the Kajicho primary area and the Kanda–Nihonbashi wider area. The official poster blue outline is registered independently.

| Source area | Area / ha | Selected model objects | Land-use record coverage |
| --- | ---: | ---: | ---: |
| Brief solid primary | {primary['area_ha']:.4f} | {primary['selected_models']} | {primary['land_use_coverage_pct']:.2f}% |
| Brief dashed wider | {wider['area_ha']:.4f} | {wider['selected_models']} | {wider['land_use_coverage_pct']:.2f}% |
| Poster blue | {poster['area_ha']:.4f} | {poster['selected_models']} | {poster['land_use_coverage_pct']:.2f}% |

Open [the current portable QGIS project](../05_QGIS/Projects/Kanda_Nihonbashi_Course_2026-10-16.qgz). Its data is [Kanda_Nihonbashi_Course.gpkg](../04_Data/Ready/Course_Boundaries_2026-10-16/Kanda_Nihonbashi_Course.gpkg). Read the [{theme_count} thematic PNG maps + overview](../06_Outputs/Boundary_Atlas_2026-10-16/atlas.json), [statistics](../06_Outputs/Boundary_Atlas_2026-10-16/statistics.json), [CSV tables](../06_Outputs/Boundary_Atlas_2026-10-16/tables), [source register](../06_Outputs/Boundary_Atlas_2026-10-16/source_manifest.json), and [source registration](../06_Outputs/Boundary_Atlas_2026-10-16/registration.json).

The brief supplies a raster map on page 4, Figure 5. Six identifiable road junctions fit an affine transform (pixel coordinates to projected map coordinates). The primary solid and wider dashed strokes are traced separately. The poster blue line uses its own transform. Original sources remain unchanged. The source overlays are [brief registration](../06_Outputs/Boundary_Atlas_2026-10-16/registration/brief_registration.png) and [poster registration](../06_Outputs/Boundary_Atlas_2026-10-16/registration/poster_registration.png).

The brief fit has 7.43 m root mean square residual and 20.17 m maximum leave-one-control-out error. The poster values are 11.49 m and 33.32 m. The 25 m and 45 m bands include those predictive checks and source line width. They support membership sensitivity checks and are not confidence intervals. The brief labels its wider area approximate. The raster sources do not supply parcel survey coordinates.

The primary trace preserves all visible northern and western bends. [Eleven edge checks](../06_Outputs/Boundary_Atlas_2026-10-16/tables/primary_edge_checks.csv) compare sampled points along every source edge against the 2020 census outline. The maximum sampled separation is 11.49 m; the full-boundary Hausdorff distance is 11.65 m. The two polygons have a 5,068.40 m² symmetric difference and select the same 277 model IDs. The 10.79 ha census area remains the denominator for historical model runs; the current primary trace is 10.70 ha.

## Calculation rules

Model counts use a representative point inside each source outline. Footprint coverage uses the union of all positive area intersections, including crossing models. Building use and height summaries use each area's own selected IDs. Source measured heights and proxy heights stay separate. Full selected-model floor proxies and within-outline allocated proxies have separate fields. Actual energy and carbon remain missing.

Observed land use is clipped from complete source members, dissolved within each class, and reported with class overlap and unmapped area. Both ward source packages were inspected; shared land-use records are deduplicated by original ID. Planning reference zones remain separate from observed land use. Road length, trees, route inventory intersections and park area are recomputed for every outline. Individual tree record absence does not establish that no trees exist.

Four flood sources retain separate dates and scales: Kanda basin 2018 L2, Sumida–Shingashi 2021 L2, and Kanda river 2024 L1/L2. Exposed models require positive overlap inside the named course area. Missing hazard polygons do not establish safety. Population rows retain full 2020 census town totals; intersected fractions are not assigned full town populations. Tokyo station weather and the official town-level earthquake ranks retain their original units.

JR Kanda and Ginza Line Kanda keep distinct source points. Multiple JR line records can share a display label only at the same location. Station source points do not identify individual entrances.

## Reproduction and scope

Use `08_Scripts/register_course_boundaries.py`, `extract_boundary_assets.py`, `build_boundary_atlas.py`, and `assemble_boundary_site.py`. Inspect live compute hosts before new processing. Use one writer for a GeoPackage and keep its QGIS project and data paths together. Source CRS, licenses, original member paths, years and processing rules are in the source manifest.

The current delivery uses PNG maps and JPEG previews. All processing and delivery outputs were produced on the selected remote host; no generated data, map or package was copied to the local computer. Historical simulation fields retain their geometry and acceptance state. Their pages label the historical census ROI and show the corrected course overlays. No new CFD was run.
'''
(ROOT/'docs/COURSE_BOUNDARIES.md').write_text(doc)
(OUT/'README.md').write_text(doc.replace('../06_Outputs/Boundary_Atlas_2026-10-16/','').replace('../05_QGIS/','../../05_QGIS/').replace('../04_Data/','../../04_Data/'))
for filename,lang in [('README.md','en'),('README.zh-CN.md','zh'),('README.ja.md','ja')]:
    p=ROOT/filename;t=p.read_text();title=t.index('\n')+1
    text={'en':f'\n{release_date}: [Course boundaries and data](docs/COURSE_BOUNDARIES.md) are updated. Primary {primary["area_ha"]:.2f} ha / {primary["selected_models"]} models; wider {wider["area_ha"]:.2f} ha / {wider["selected_models"]} models; poster {poster["area_ha"]:.2f} ha / {poster["selected_models"]} models. Start with the [current QGIS project](05_QGIS/Projects/Kanda_Nihonbashi_Course_2026-10-16.qgz) and {theme_count} thematic PNG maps + overview. Earlier dated GIS and simulations retain their historical scope.\n',
      'zh':f'\n{release_date}：[课程边界与数据](docs/COURSE_BOUNDARIES.md)已更新。重点区 {primary["area_ha"]:.2f} ha／{primary["selected_models"]} 个模型；外围区 {wider["area_ha"]:.2f} ha／{wider["selected_models"]} 个模型；海报区 {poster["area_ha"]:.2f} ha／{poster["selected_models"]} 个模型。使用[当前 QGIS 工程](05_QGIS/Projects/Kanda_Nihonbashi_Course_2026-10-16.qgz)与 {theme_count} 张专题 PNG＋总图。此前日期版 GIS 和模拟保留其历史口径。\n',
      'ja':f'\n{release_date}：[授業対象区域とデータ](docs/COURSE_BOUNDARIES.md)を更新。重点区域 {primary["area_ha"]:.2f} ha／{primary["selected_models"]} モデル、周辺区域 {wider["area_ha"]:.2f} ha／{wider["selected_models"]} モデル、ポスター区域 {poster["area_ha"]:.2f} ha／{poster["selected_models"]} モデル。[現在の QGIS プロジェクト](05_QGIS/Projects/Kanda_Nihonbashi_Course_2026-10-16.qgz)と 主題図{theme_count}枚＋全体図（PNG）を使う。以前の日付版 GIS と計算は旧対象区域を保持する。\n'}[lang]
    t=re.sub(r'\n2026-\d{2}-\d{2}[:：].*?\n','\n',t,count=1);t=t[:title]+text+t[title:]
    if lang=='en':t=t.replace('for **Kajicho 1 & 2, Tokyo**','for **Kanda–Nihonbashi and Kajicho 1 & 2, Tokyo**').replace('The core contains 277 building model objects.','The historical census ROI contains 277 building model objects.').replace('1. Clone the complete repository or download and extract its ZIP. Open `05_QGIS/Projects/Kajicho_Public_Baseline_2026-10-14.qgz` in QGIS, keeping the folder structure intact.','1. Clone the complete repository or download and extract its ZIP. Open `05_QGIS/Projects/Kanda_Nihonbashi_Course_2026-10-16.qgz` in QGIS, keeping the folder structure intact. The earlier `Kajicho_Public_Baseline_2026-10-14.qgz` is a historical baseline.')
    p.write_text(t)
for rel in ['docs/TEAM_START.md','docs/DATA_GUIDE.md','docs/PROJECT_PLAN.md','docs/PORTFOLIO_GUIDE.md']:
    p=ROOT/rel;t=p.read_text();idx=t.index('\n')+1
    if 'COURSE_BOUNDARIES.md' not in t:t=t[:idx]+'\nCurrent course scope and GIS: [2026-10-16 boundary release](COURSE_BOUNDARIES.md). Use the new portable project for current course maps. Earlier dated tables and simulations keep their recorded census/model scope.\n'+t[idx:]
    p.write_text(t)
for rel in ['03_Theme_B/Public_Baseline/README.md','03_Theme_B/Simulation_V3/README.md','06_Outputs/Portfolio_2026-10-15/README.md','06_Outputs/Context_Study_2026-10-15/README.md']:
    p=ROOT/rel
    if not p.exists():continue
    t=p.read_text();link='../../docs/COURSE_BOUNDARIES.md'
    if 'registered boundary release' not in t:t=t[:t.index('\n')+1]+'\nCurrent course geography: [registered boundary release]('+link+'). This dated package records the earlier census ROI; use the current course atlas for source-area totals.\n'+t[t.index('\n')+1:];p.write_text(t)
# Refresh the machine-readable layer/field indexes with the current GeoPackage.
gp='04_Data/Ready/Course_Boundaries_2026-10-16/Kanda_Nihonbashi_Course.gpkg';con=sqlite3.connect(ROOT/gp)
for filename,kind in [('Layer_Catalog.csv','layers'),('Layer_Fields.csv','fields')]:
    p=ROOT/'04_Data/Metadata'/filename;existing=list(csv.DictReader(p.open(encoding='utf-8-sig')));keys=list(existing[0]);existing=[r for r in existing if r['dataset_path']!=gp]
    for table,dtype in con.execute('select table_name,data_type from gpkg_contents').fetchall():
        geom=con.execute('select column_name,geometry_type_name,srs_id from gpkg_geometry_columns where table_name=?',(table,)).fetchone();cols=con.execute('pragma table_info("'+table+'")').fetchall()
        if kind=='layers':existing.append(dict(dataset_path=gp,layer=table,data_type=dtype,geometry_column=geom[0] if geom else '',geometry_type=geom[1] if geom else '',crs='EPSG:'+str(geom[2]) if geom else '',records=con.execute('select count(*) from "'+table+'"').fetchone()[0],id_fields=','.join(r[1] for r in cols if r[1] in ('asset_id','gml_id','building_id','scope','town_code'))))
        else:
            for _,name,typ,nn,default,pk in cols:existing.append(dict(dataset_path=gp,layer=table,field=name,sqlite_type=typ,not_null=nn,primary_key=pk,is_geometry=int(bool(geom and name==geom[0])),default_value=default or ''))
    with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(existing)
con.close()
subprocess.run([sys.executable,str(ROOT/'08_Scripts/build_layer_catalog.py')],check=True)
# Existing check entrypoints dispatch to current boundary checks when present.
p=ROOT/'08_Scripts/check_portfolio.py';t=p.read_text();anchor="ROOT=Path(__file__).resolve().parents[1]";extra="\nif (ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/boundary-atlas/atlas.json').exists():\n import runpy\n runpy.run_path(str(ROOT/'08_Scripts/check_boundary_release.py'))\n raise SystemExit(0)\n"
if 'check_boundary_release.py' not in t:t=t.replace(anchor,anchor+extra);p.write_text(t)
p=ROOT/'08_Scripts/check_context_study.py';t=p.read_text()
if "if not data.get('boundary_release'):" not in t:
    start=t.index('with zipfile.ZipFile(STUDY');end=t.index('\nassert max(',start)
    t=t[:start]+"if not data.get('boundary_release'):\n"+'\n'.join('    '+line for line in t[start:end].splitlines())+t[end:];p.write_text(t)
# The active registry contains release state, not execution-host details.
state={'updated_on':release_date,'status':'boundary atlas and data rebuilt; publication pending','course_boundary_guide':'docs/COURSE_BOUNDARIES.md','qgis_project':'05_QGIS/Projects/Kanda_Nihonbashi_Course_2026-10-16.qgz','scopes':{k:{kk:v[kk] for kk in ('area_ha','selected_models','boundary_uncertainty_m')} for k,v in s.items()},'maps_png':map_count,'mapping_themes':theme_count,'no_new_cfd':True,'local_result_copy':False}
(ROOT/'docs/BOUNDARY_RELEASE.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps({'entrypoints':'updated','current_qgis':gp,'catalogs':'updated','scopes':list(s)}))
