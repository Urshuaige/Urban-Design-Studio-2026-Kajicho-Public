#!/usr/bin/env python3
"""Apply the Figure 5 two-outline view and POI reading to the opened Site source."""
import json,re,csv,hashlib,shutil
from pathlib import Path
REV='20261018-strict-nav'
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def tr(en,zh,ja=None):return {'en':en,'zh':zh,'ja':ja or en}
def apply(root):
 team=root/'team';dist=root/'site/dist';out=team/'06_Outputs/Study_Area_2026-10-18';atlas=read(out/'atlas.json');w=atlas['scopes']['study_area'];p=atlas['scopes']['primary_brief'];pd=read(out/'poi_semantics.json')
 uses=list(csv.DictReader((out/'tables/building_use.csv').open(encoding='utf-8-sig')))
 office=next(x for x in uses if x['scope']=='study_area' and x['use']=='office')
 pd['building_use_context']={'office_floor_proxy_share_pct':float(office['floor_proxy_share_pct']),'source':'PLATEAU 2025 model attributes; survey 2021 where known','record_unit':'Projection × source/proxy floors; not measured occupied floor area','source_table':'study-atlas/tables/building_use.csv'}
 write(out/'poi_semantics.json',pd)
 for name in ['poi_semantics.json','poi.geojson','earthquake_risk_primary.json','earthquake_risk_by_town.csv','earthquake_risk_primary.csv']:shutil.copy2(out/name,dist/'study-atlas'/name)
 ctx=read(dist/'context-study/context.json')
 ctx.update(source_scopes=['study_area','primary_brief'],mapping_view='Figure 5 solid primary and dashed approximate secondary in one shared view',boundary_release='2026-10-18-brief-figure5')
 ctx['metrics']=[
 {'label':tr('Wider area','外围区面积'),'value':round(w['area_ha'],2),'unit':'ha','note':tr('Brief dashed outline; approximate.','任务书虚线，概略范围。')},
 {'label':tr('Wider-area models','外围区模型'),'value':w['selected_models'],'unit':'','note':tr('Only full-footprint models contained by the outline.','仅纳入完整投影位于边线内的模型。')},
 {'label':tr('Primary area','重点区面积'),'value':round(p['area_ha'],2),'unit':'ha','note':tr('Brief solid outline.','任务书实线范围。')},
 {'label':tr('Primary-area models','重点区模型'),'value':p['selected_models'],'unit':'','note':tr('Full source objects; separate denominator.','完整源对象，分母单列。')},
 {'label':tr('POI destinations','POI 目的地'),'value':pd['scopes']['study_area']['poi_count'],'unit':'','note':tr('OSM wider-area records; primary area '+str(pd['scopes']['primary_brief']['poi_count'])+'.','OSM 外围记录；重点区 '+str(pd['scopes']['primary_brief']['poi_count'])+' 条。')}]
 c=ctx['charts'][0];c['title']=tr('Two source outlines, clear denominators','两条任务书边线，分别统计')
 c['finding']=tr(f"The wider trace is {w['area_ha']:.2f} ha / {w['selected_models']:,} models; the primary trace is {p['area_ha']:.2f} ha / {p['selected_models']} models.",f"外围描线 {w['area_ha']:.2f} ha／{w['selected_models']:,} 个模型；重点区 {p['area_ha']:.2f} ha／{p['selected_models']} 个模型。")
 c['method']=tr('Source-stroke traces from Figure 5. Analysis requires the full original footprint to be contained by its outline.','按 Figure 5 源线描绘；分析仅纳入投影完整位于边线内的模型。')
 c['limits']=tr('Registration RMSE 7.43 m; a 25 m cartographic screening band describes boundary sensitivity. The wider area is explicitly approximate.','配准 RMSE 7.43 m；采用 25 m 制图筛查带报告边界敏感性。外围区原文明确为概略范围。')
 c['rows']=[[tr('Wider area / ha','外围区 / ha'),f"{w['area_ha']:.2f}"],[tr('Wider-area models','外围区模型'),w['selected_models']],[tr('Primary area / ha','重点区 / ha'),f"{p['area_ha']:.2f}"],[tr('Primary-area models','重点区模型'),p['selected_models']],[tr('Wider footprint coverage','外围投影覆盖'),f"{w['gross_footprint_coverage_pct']:.2f}%"],[tr('Primary footprint coverage','重点区投影覆盖'),f"{p['gross_footprint_coverage_pct']:.2f}%"]]
 for c in ctx['charts'][1:5]:
  c['method']=tr('Building membership requires the full footprint inside the wider Figure 5 trace. Area layers use intersections.','建筑投影完整位于 Figure 5 外围描线内才纳入统计，面图层采用相交。')
  c['scope']='study_area'
 write(dist/'context-study/context.json',ctx)
 js=(dist/'portfolio.js').read_text()
 # Readable labels remain in one dictionary and the user’s language preference persists.
 a=js.index('const lex=')+len('const lex=');z=js.index(';\nconst work=',a);lex=json.loads(js[a:z])
 updates={
 'en':{'heroIntro':'Study Kanda–Nihonbashi towards 2050, with Kajicho 1 & 2 as the detailed primary area in the official brief.','heroCaption':'Figure 5: solid primary area and dashed approximate wider area.','mappingTitle':'One view, nine themes','mappingIntro':'Each theme shows both Figure 5 outlines in the same view. POI functions, building data and source dates are linked below.','mapFoot':'Solid: Kajicho primary area. Dashed: approximate Kanda–Nihonbashi wider area. Both follow the official brief Figure 5.','mapExtent':'Figure 5 source outlines · EPSG:6677 · North up','boundaryTitle':'The official brief’s study areas','boundaryIntro':'Retain Figure 5’s solid primary and dashed approximate secondary outlines. No inferred block or poster boundary is used.','atlasPackageNote':'9 thematic PNG maps + overview · portable QGIS + POIs','contextPackageNote':'Two source scopes · current CSV tables · document sources','footer':'Official brief Figure 5 · 2026.10.18'},
 'zh':{'heroIntro':'依据官方任务书，面向 2050 年研究神田—日本桥，并以鍛冶町一、二丁目作为详细设计重点区。','heroCaption':'Figure 5：实线重点区与虚线概略外围区。','mappingTitle':'同一视角，九类专题','mappingIntro':'每张专题图在同一视角叠加任务书的两条边线，下方连接 POI 功能、建筑数据与来源日期。','mapFoot':'实线：鍛冶町重点区；虚线：神田—日本桥概略外围区。均依官方任务书 Figure 5。','mapExtent':'Figure 5 来源描线 · EPSG:6677 · 北向上','boundaryTitle':'官方任务书中的研究范围','boundaryIntro':'保留 Figure 5 的实线重点区与虚线概略外围区，不采用自行扩出的街区边界或海报边界。','atlasPackageNote':'9 张专题 PNG＋总图 · 便携 QGIS＋POI','contextPackageNote':'两个来源范围 · 当前 CSV · 文件来源','footer':'官方任务书 Figure 5 · 2026.10.18'},
 'ja':{'heroIntro':'公式課題書に基づき神田・日本橋を2050年へ向けて研究し、鍛冶町一・二丁目を詳細設計の重点区域とする。','heroCaption':'図5：実線の重点区域と破線の概略周辺区域。','mappingTitle':'同じ視点、九つの主題','mappingIntro':'各主題図は図5の二つの境界を同じ視点で重ねる。POI機能、建物データと出典日付を併記。','mapFoot':'実線：鍛冶町重点区域。破線：神田・日本橋概略周辺区域。いずれも公式課題書の図5。','mapExtent':'図5の出典境界 · EPSG:6677 · 北向き','boundaryTitle':'公式課題書の研究区域','boundaryIntro':'図5の実線重点区域と破線概略周辺区域を保持。独自の街区・ポスター境界は使用しない。','atlasPackageNote':'主題PNG9枚＋全体図 · 可搬QGIS＋POI','contextPackageNote':'二つの出典区域 · 現在のCSV · 文献出典','footer':'公式課題書図5 · 2026.10.18'}}
 for lang,vals in updates.items():lex[lang].update(vals)
 js=js[:a]+json.dumps(lex,ensure_ascii=False)+js[z:]
 js="import {renderPOI} from './poi-semantics.js?v="+REV+"';\n"+js
 js=js.replace("article.append(el('p','MAP '+String(i+1).padStart(2,'0'),'kicker'),el('h3',localized(p.title)),mapSheet(p));box.append(article);","article.append(el('p','MAP '+String(i+1).padStart(2,'0'),'kicker'),el('h3',localized(p.title)),mapSheet(p));if(p.id==='09_poi'){const insight=el('section',undefined,'poi-insights');insight.id='poi-insights';article.append(insight);box.append(article);renderPOI(insight,lang);}else box.append(article);")
 a=js.index('function renderBoundaries(');z=js.index('\nfunction render(){',a)
 js=js[:a]+"""function renderBoundaries(data){const host=$('#boundary-content');host.replaceChildren(mapSheet(data.plates.find(p=>p.kind==='overview')));const primary=data.scopes.primary_brief,wider=data.scopes.study_area;host.append(dataTable([{en:'Figure 5 outline',zh:'Figure 5 边线',ja:'図5境界'},{en:'Area / ha',zh:'面积 / ha',ja:'面積 / ha'},{en:'Model objects',zh:'模型对象',ja:'モデル'}],[[{en:'Solid · primary',zh:'实线 · 重点区',ja:'実線・重点区域'},primary.area_ha.toFixed(2),primary.selected_models],[{en:'Dashed · wider (approx.)',zh:'虚线 · 外围区（概略）',ja:'破線・周辺区域（概略）'},wider.area_ha.toFixed(2),wider.selected_models]]),el('p',localized({en:'These are registered traces of the official brief. Registration RMSE: 7.43 m; screening band: 25 m. Source models stay whole; edge-sensitive membership is reported in the data.',zh:'以上为官方任务书的配准描线。配准 RMSE 7.43 m，筛查带 25 m。源模型保持完整，边缘成员敏感性在数据中报告。',ja:'公式課題書の位置合わせ済み描線。RMSE7.43m、スクリーニング帯25m。元モデルを保持し、境界付近の対応感度をデータに示す。'}),'study-boundary-note'),sources([{document_title:{en:'Official Theme B brief · Figure 5',zh:'Theme B 官方任务书 · Figure 5',ja:'Theme B公式課題書・図5'},url:'https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view',year:'2026',page:'p.4'}]),link(localized({en:'Source trace and registration record',zh:'来源描线与配准记录',ja:'出典描線と位置合わせ記録'}),'study-atlas/study_boundary.geojson','map-source'));}
""" +js[z:]
 js=js.replace("const image=fig.querySelector('img');","const image=fig.querySelector('img');image.src=p.preview+'?v="+REV+"';")
 js=js.replace("fetch('context-study/context.json')","fetch('context-study/context.json?v="+REV+"',{cache:'no-store'})").replace('fetch("study-atlas/atlas.json")','fetch("study-atlas/atlas.json?v='+REV+'",{cache:"no-store"})')
 js=re.sub(r'\?v=20261018(?=[\'"])','?v='+REV,js)
 (dist/'portfolio.js').write_text(js)
 html=(dist/'index.html').read_text().replace('ONE STUDY AREA / 2026','BRIEF FIGURE 5 / 2026').replace('One street-block study boundary and complete building models','Official Figure 5 primary and approximate wider outlines')
 for key,val in lex['en'].items():
  if isinstance(val,str):html=re.sub(r'(<([a-z0-9]+)\b[^>]*data-t="'+re.escape(key)+r'"[^>]*>)[^<]*(</\2>)',lambda m:m.group(1)+val+m.group(3),html)
 if 'poi-semantics.css' not in html:html=html.replace('</head>','<link rel="stylesheet" href="poi-semantics.css?v='+REV+'"></head>')
 html=re.sub(r'\?v=20261018(?:-study)?(?=["\'])','?v='+REV,html)
 (dist/'index.html').write_text(html)
 # The locator retains archived model/domain metadata, with the two current course outlines.
 dm=read(dist/'data/domain-map.geojson');dm['features']=[f for f in dm['features'] if f['properties'].get('role') not in ('study_area','primary_brief','secondary_brief','poster_blue','design_area')]
 for f in read(out/'study_boundary.geojson')['features']:dm['features'].append({'type':'Feature','properties':{'role':f['properties']['id'],'name':f['properties']['name']['en']},'geometry':f['geometry']})
 write(dist/'data/domain-map.geojson',dm)
 dj=(dist/'domain-map.js').read_text().replace("['study_area','#59457f',null,3,.04]","['study_area','#36353a','6 4',2,0],['primary_brief','#36353a',null,3,0]")
 dj=dj.replace('Purple: current single study boundary.','Solid primary and dashed approximate wider outlines from Figure 5.').replace('紫色为当前唯一研究区边界。','实线重点区与虚线概略外围区均依 Figure 5。').replace('紫は現在の一つの研究境界。','実線重点区域と破線概略周辺区域は図5に基づく。')
 (dist/'domain-map.js').write_text(dj)
 # Replace dated active handover copy. Numerical history stays in the CFD archive.
 tj=(dist/'team.js').read_text()
 tj=tj.replace('1,134 complete study-area models',f"{w['selected_models']:,} wider / {p['selected_models']} primary model objects").replace('研究区 1,134 个完整模型',f"外围 {w['selected_models']:,}／重点 {p['selected_models']} 个模型").replace('研究区域の完全な1,134モデル',f"周辺{w['selected_models']:,}／重点{p['selected_models']}モデル")
 for old,new in [('One street-block study boundary','Official Figure 5 solid + dashed source outlines'),('一条街区研究边界','Figure 5 实线重点区＋虚线外围区'),('一つの街区研究境界','図5の実線重点区域＋破線周辺区域'),('study_area, the single current boundary.','study_area + primary_brief, the two Figure 5 source traces.'),('study_area 是唯一当前研究区边界。','study_area 与 primary_brief 分别为 Figure 5 虚线和实线。'),('study_area は現在の一つの研究境界。','study_areaとprimary_briefが図5の破線と実線。'),('Complete source projections; actual energy remains missing','Full-footprint containment; crossing models excluded; actual energy remains missing'),('完整源投影选取；真实用能仍缺失','完整投影包含筛选，跨界模型排除；真实用能仍缺失'),('16 spatial layers + membership table','18 spatial layers + membership table'),('16 个空间图层＋成员表','18 个空间图层＋成员表'),('16 空間レイヤー＋対応表','18 空間レイヤー＋対応表'),('2026-10-18 street-block boundary','2026-10-18 official brief traces + POIs'),('2026-10-18 街区边界','2026-10-18 任务书描线＋POI'),('2026-10-18の街区境界','2026-10-18の課題書描線＋POI'),('Four source scenarios / one study area','Four scenarios / two Figure 5 scopes'),('四个源情景／一个研究区','四个源情景／Figure 5 两个范围'),('四シナリオ／一研究区域','四シナリオ／図5の二区域')]:tj=tj.replace(old,new)
 (dist/'team.js').write_text(tj)
 banner='<aside class="course-scope-note" style="padding:18px 24px;background:#f7f5ef;color:#36353a;border-bottom:2px solid #36353a;font:17px/1.6 sans-serif"><b>Official brief Figure 5 · 2026-10-18</b><p><a href="index.html#study-area">Solid primary + dashed approximate wider area</a> · <a href="index.html#map-09_poi">POI functions</a> · <a href="index.html#simulation-plan">Simulation update plan</a>. Numerical trials retain their archived input geometry and acceptance state.</p></aside>'
 for name in ['team.html','studies.html','cfd.html','style-guide.html']:
  pp=dist/name;text=pp.read_text();text=re.sub(r'<aside class="course-scope-note".*?</aside>',banner,text,flags=re.S);text=re.sub(r'\?v=20261018(?:-study)?(?=["\'])','?v='+REV,text);pp.write_text(text)
 (dist/'context-study/README.md').write_text(f"""# Official brief Figure 5 + source readings

Solid primary: {p['area_ha']:.4f} ha / {p['selected_models']} model objects.
Dashed approximate wider area: {w['area_ha']:.4f} ha / {w['selected_models']} objects.
Both outlines retain source pixels and the affine registration. RMSE 7.43 m; screening band 25 m.
Models require exact full-footprint containment and retain full source geometry. Crossing/exterior models are context only. The exclusion audit records IDs and reasons.

Nine thematic PNG maps and one overview use the same view. The ninth theme contains POI classes and a native functional mix / concentration reading.
POI: OSM 2026-10-18, {pd['scopes']['study_area']['poi_count']} wider-area records / {pd['scopes']['primary_brief']['poi_count']} primary-area records.
Weather retains its station unit; earthquake values retain full official-town units. No new CFD.
""")
 for filename in ['README.md','Simulation_Scope_Plan_2026-10-18.md']:
  pass
 print(json.dumps({'stage':'figure5_site_applied','wider_models':w['selected_models'],'primary_models':p['selected_models'],'poi_wider':pd['scopes']['study_area']['poi_count'],'poi_primary':pd['scopes']['primary_brief']['poi_count']}))

