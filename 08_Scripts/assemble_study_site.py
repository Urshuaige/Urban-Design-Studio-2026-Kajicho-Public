#!/usr/bin/env python3
"""Rebuild current Figure 5 maps, statistics, source readings and shared Site navigation."""
import argparse,json,csv,shutil,re,subprocess
from pathlib import Path
REPO='https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho'
def tr(en,zh=None,ja=None):return {'en':en,'zh':zh or en,'ja':ja or en}
def read(p):return json.loads(p.read_text())
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def csvrows(p):return [r for r in csv.DictReader(p.open(encoding='utf-8-sig')) if r.get('scope','study_area')=='study_area']
def main():
 p=argparse.ArgumentParser();p.add_argument('--task-root',type=Path,required=True);a=p.parse_args();root=a.task_root;team=root/'team';dist=root/'site/dist';out=team/'06_Outputs/Study_Area_2026-10-18'
 for module in ['poi-semantics.js','poi-semantics.css']:shutil.copy2(team/'08_Scripts/site_modules'/module,dist/module)
 atlas=read(out/'atlas.json');sm=atlas['scopes']['study_area'];ctxp=dist/'context-study/context.json';ctx=read(ctxp)
 target=dist/'study-atlas'
 if target.exists():shutil.rmtree(target)
 target.mkdir()
 for name in ['atlas.json','atlas.geojson','statistics.json','source_manifest.json','quality_checks.json','study_boundary.geojson','boundary_edges.csv','earthquake_risk_by_town.json']:shutil.copy2(out/name,target/name)
 for name in ['maps','tables']:shutil.copytree(out/name,target/name)
 old=dist/'boundary-atlas'
 if old.exists():shutil.rmtree(old)
 for folder in [dist/'portfolio/maps',dist/'portfolio/mapping_data']:
  if folder.exists():shutil.rmtree(folder)
 ctx['metrics']=[
 {'label':tr('Study area','研究区面积','研究区域の面積'),'value':round(sm['area_ha'],2),'unit':'ha','note':tr('One street-block boundary from the brief.','任务书落实为一条街区边界。','課題書に基づく一つの街区境界。')},
 {'label':tr('Building models','建筑模型','建物モデル'),'value':sm['selected_models'],'unit':'','note':tr('Complete PLATEAU LOD1 objects.','完整的 PLATEAU LOD1 对象。','完全なPLATEAU LOD1オブジェクト。')},
 {'label':tr('Footprint coverage','建筑投影覆盖','建物投影の被覆'),'value':round(sm['gross_footprint_coverage_pct'],2),'unit':'%','note':tr('Union of full model projections.','完整模型投影的并集。','完全なモデル投影の和集合。')},
 {'label':tr('Land-use coverage','土地利用覆盖','土地利用の被覆'),'value':round(sm['land_use_coverage_pct'],2),'unit':'%','note':tr('Survey polygons within the study area.','研究区内的土地调查面。','研究区域内の土地利用調査面。')},
 {'label':tr('Cut building models','被边线切开的模型','境界で切断されるモデル'),'value':0,'unit':'','note':tr('PLATEAU and OSM checked.','已检查 PLATEAU 与 OSM。','PLATEAUとOSMを確認。')}]
 src=[{'document_title':tr('Official Theme B brief','Theme B 官方任务书','Theme B公式課題書'),'url':'https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view','year':'2026','page':'p.4 / Figure 5'}]
 def chart(i,title,finding,method,limits,headers,rows,plate):
  return {'id':i,'title':title,'finding':finding,'method':method,'limits':limits,'headers':headers,'rows':rows,'file':'study-atlas/maps/'+plate+'.png','preview':'study-atlas/maps/previews/'+plate+'.jpg','map_target':'map-'+plate,'sources':src,'design_meaning':tr('Use the same study area for field checks and comparison.','现场核查与方案对比统一使用此研究区。','現地確認と比較に同じ研究区域を使う。')}
 common=tr('Select complete model projections inside the street-block boundary.','按街区边界选取完整建筑模型投影。','街区境界内の完全な建物投影を抽出。')
 precise=tr('The brief guides the district; the edge register defines the working line.','任务书确定研究地区，边线记录明确工作边界。','課題書が対象地区を示し、境界記録が作業線を定義。')
 charts=[chart('01_building_coverage',tr('One area, one denominator','一个研究区，一个分母','一つの区域と分母'),tr(f"{sm['area_ha']:.2f} ha contains {sm['selected_models']:,} complete building models.",f"{sm['area_ha']:.2f} ha 内有 {sm['selected_models']:,} 个完整建筑模型。"),common,precise,[tr('Measure','项目'),tr('Value','数值')],[[tr('Area / ha','面积 / ha'),f"{sm['area_ha']:.2f}"],[tr('Building models','建筑模型'),sm['selected_models']],[tr('Footprint coverage','建筑投影覆盖'),f"{sm['gross_footprint_coverage_pct']:.2f}%"],[tr('Cut models','被切开模型'),0]],'00_study_area')]
 data=csvrows(out/'tables/building_use.csv')
 charts.append(chart('02_building_use',tr('Building use','建筑用途','建物用途'),tr('Each use class has the same building-model denominator.','各用途类别使用同一建筑模型总数作为分母。'),common,tr('Floor proxy uses projection area × source or proxy floors; actual energy remains to be measured.','楼面代理为投影面积乘源层数或代理层数；真实用能仍需采集。'),[tr('Use','用途'),tr('Models','模型数'),tr('Count share','数量占比'),tr('Floor proxy share','楼面代理占比')],[[r['use'],int(r['models']),f"{float(r['count_share_pct']):.2f}%",f"{float(r['floor_proxy_share_pct']):.2f}%"] for r in data],'03_building_use'))
 data=csvrows(out/'tables/land_use.csv')
 charts.append(chart('03_land_use_area',tr('Observed land use','现状土地利用','現況土地利用'),tr('All class areas use the same study boundary.','各类面积统一按研究区边界计算。'),tr('Dissolve each survey class, then intersect the study area.','同类调查面先求并集，再与研究区相交。'),tr('Observed use and legal planning zones answer different questions.','现状利用和法定用途地域分别回答不同问题。'),[tr('Class','分类'),tr('Area / m²','面积 / m²'),tr('Share','占比')],[[r['label'],f"{float(r['area_m2']):,.0f}",f"{float(r['scope_share_pct']):.2f}%"] for r in data],'05_land_use'))
 counts={}
 for r in csvrows(out/'tables/height_models.csv'):counts[r['class']]=counts.get(r['class'],0)+1
 charts.append(chart('04_building_height',tr('Height data','建筑高度资料','建物高さの資料'),tr('Source heights and proxy values remain separate.','源高度与代理高度分列。'),tr('Count the same complete models; medians use valid source heights.','使用同一组完整模型，中位数仅采用有效源高度。'),tr('A model height is not a surveyed roof condition.','模型高度不等同于实测屋顶状况。'),[tr('Height class','高度组'),tr('Models','模型数')],[[k,v] for k,v in counts.items()],'04_building_height'))
 data=csvrows(out/'tables/flood_scenarios.csv')
 charts.append(chart('05_flood_sources',tr('Flood source overlap','洪水源面相交','洪水出典面の重なり'),tr('Four source scenarios keep their own dates and scales.','四个来源情景分别保留日期与规模。'),tr('Intersect each scenario with the study area and its complete models.','各情景分别与研究区及完整模型相交。'),tr('No recorded overlap does not establish safety. Map: Kanda 2018 L2.','无相交记录不代表安全。地图采用神田川 2018 L2。'),[tr('Source scenario','源情景'),tr('Date','日期'),tr('Area / m²','面积 / m²'),tr('Models','模型数')],[[r['scenario'],r['source_date'],f"{float(r['recorded_overlap_m2']):,.0f}",int(r['exposed_selected_models'])] for r in data],'08_flood'))
 bldg_sources=[
 {'document_title':tr('PLATEAU CityGML: Chiyoda buildings','PLATEAU 千代田区建筑','PLATEAU 千代田区建物'),'url':'https://www.geospatial.jp/ckan/dataset/plateau-13101-chiyoda-ku-2025','year':'2025 model','page':'2021 survey where known; geometry 2024-03-15; CC BY 4.0'},
 {'document_title':tr('PLATEAU CityGML: Chuo buildings','PLATEAU 中央区建筑','PLATEAU 中央区建物'),'url':'https://assets.cms.plateau.reearth.io/assets/93/1f058b-e06b-445c-ae62-2e02cdf72849/13102_chuo-ku_pref_2025_citygml_1_op.zip','year':'2025 model','page':'2021 survey where known; geometry 2024-03-15; CC BY 4.0'}]
 charts[0]['sources']=src+bldg_sources
 charts[1]['sources']=bldg_sources
 charts[2]['sources']=[{'document_title':tr('PLATEAU observed land use: Tokyo','PLATEAU 东京现状土地利用','PLATEAU 東京現況土地利用'),'url':'https://assets.cms.plateau.reearth.io/assets/93/1f058b-e06b-445c-ae62-2e02cdf72849/13102_chuo-ku_pref_2025_citygml_1_op/udx/luse/533946_luse_6697_op.gml','year':'2021 survey / 2025 model','page':'luse; duplicate Chiyoda records omitted; CC BY 4.0'}]
 charts[3]['sources']=bldg_sources
 charts[4]['sources']=[{'document_title':tr('PLATEAU river-flood scenario polygons','PLATEAU 河流洪水情景','PLATEAU 河川洪水シナリオ'),'url':'https://www.geospatial.jp/ckan/dataset/plateau-13101-chiyoda-ku-2025','year':'2018 / 2021 / 2024 scenarios; 2025 model','page':'fld; Kanda 2018 L2 map; four scenarios tabulated; CC BY 4.0'}]
 use_names={'office':'Office','retail':'Retail','hotel':'Hotel','housing':'House','apartments':'Apartments','mixed':'Shop + house','workhome':'Workshop + house','government':'Government','education':'Education / welfare','logistics':'Transport / storage','industry':'Industry','utilities':'Utilities','other':'Other','unknown':'Unknown'}
 for row in charts[1]['rows']:row[0]=use_names.get(row[0],row[0])
 for c in charts:c.pop('design_meaning',None)
 charts.extend(ctx['charts'][5:])
 risk=read(out/'earthquake_risk_by_town.json')
 names=['Uchi-Kanda 3','Kanda-Sudacho 2','Kajicho 1','Kajicho 2','Kanda-Kajicho 3','Kanda-Konyacho','Kanda-Kitanorimonocho','Kanda-Tomiyamacho','Kanda-Mikuracho','Iwamotocho 1','Iwamotocho 2','Iwamotocho 3','Kanda-Nishifukudacho','Kanda-Higashimatsushitacho','Kanda-Higashikonyacho','Kanda-Iwamotocho','Nihonbashi-Hongokucho 3','Nihonbashi-Hongokucho 4','Nihonbashi-Muromachi 3','Nihonbashi-Muromachi 4','Nihonbashi-Honcho 3','Nihonbashi-Honcho 4','Nihonbashi-Kodemmacho']
 names=dict(zip(['13101029003', '13101033002', '13101035001', '13101035002', '131010360', '131010370', '131010380', '131010390', '131010400', '13101041001', '13101041002', '13101041003', '131010420', '131010430', '131010440', '131010450', '13102012003', '13102012004', '13102013003', '13102013004', '13102014003', '13102014004', '131020160'],names))
 for row in risk['rows']:row['name']=tr(names.get(row['town_code'],row['official_town_name']),row['official_town_name'],row['official_town_name'])
 risk['sources']=[{'document_title':tr('Tokyo 9th Regional Earthquake Risk Survey','东京都第9回地域危险度测定','東京都第9回地域危険度測定'),'url':risk['source']['source_url'],'year':'2022','page':'5,192 official town units; original CSV'},{'document_title':tr('Study-area town join and source record','研究区町丁目连接与来源记录','研究区域の町丁目結合と出典記録'),'url':'study-atlas/earthquake_risk_by_town.json','year':'2026-10-18','page':'23 matched town units; 24 census geometry parts'}]
 ctx['seismic']=risk
 c=charts[6];c.pop('file',None);c.pop('preview',None);c['presentation']='native_table';c['sources']=risk['sources'];c.pop('design_meaning',None)
 c['finding']=tr('23 intersecting town units retain their full official 2022 risk values.','相交的 23 个町丁目保留各自 2022 年官方风险原值。','重なる23町丁目の2022年公式危険度をそのまま示す。')
 c['method']=tr('Join every positive 2020 census intersection to the official town. Merge duplicate geometry parts; retain partial towns.','全部 2020 年国势调查相交单元与官方町丁目连接，合并同町重复几何，保留部分相交单元。')
 c['limits']=tr('Values describe whole official towns. Overlap selects rows; it does not scale risk.','风险数值对应完整官方町丁目。相交仅用于选取记录，不按面积缩放风险。')
 c['headers']=[tr('Town unit','町丁目'),tr('Collapse / buildings·ha⁻¹','倒塌 / 棟·ha⁻¹'),tr('Collapse rank','倒塌等级'),tr('Fire / buildings·ha⁻¹','火灾 / 棟·ha⁻¹'),tr('Fire rank','火灾等级'),tr('Overall rank','综合等级'),tr('Study overlap','研究区相交比例')]
 c['rows']=[[row['name'],row['collapse'],row['collapse_rank'],row['fire'],row['fire_rank'],row['overall_rank'],f"{row['town_overlap_fraction']*100:.1f}%"] for row in risk['rows']]
 for old in [dist/'context-study/figures/07_earthquake_risk.png',dist/'context-study/figures/previews/07_earthquake_risk.jpg']:
  if old.exists():old.unlink()
 ctx.update(charts=charts,date='2026-10-18',boundary_release='2026-10-18',source_scopes=['study_area'],mapping_view='one study boundary; whole buildings',presentation_updated='2026-10-18',no_new_cfd=True,map_export_formats=['PNG'])
 write(ctxp,ctx)
 analysis=dist/'context-study/analysis'
 if analysis.exists():shutil.rmtree(analysis)
 shutil.copytree(out/'tables',analysis)
 (dist/'context-study/README.md').write_text(f'''# Current study area and source readings

2026-10-18. One operational street-block boundary implements the wider district in Theme B Figure 5. Kajicho 1 & 2 remains the named detailed focus.

Area: {sm['area_ha']:.4f} ha. Complete PLATEAU LOD1 model objects: {sm['selected_models']:,}. Positive-area building cuts: zero in PLATEAU and OSM.

Eight thematic maps share this boundary. Web legends use native readable text; full PNG exports keep large legends. The source readings use linked boxes and prominent document citations. Full readings and original source quotations remain in context.json.

Current tables: ../study-atlas/tables/. Map sources: ../study-atlas/source_manifest.json. Simulation change plan: ../data/simulation-scope-plan.json. Weather and earthquake records retain their station and town units. No new solver was started.
''')
 plan=team/'docs/Simulation_Scope_Plan_2026-10-18.json';shutil.copy2(plan,dist/'data/simulation-scope-plan.json')
 js=re.sub(r'^import .*;\n','',(dist/'portfolio.js').read_text(),flags=re.M)
 js=js.replace('let study=null,loadFailed=false,boundaryData=null;','let study=null,loadFailed=false,boundaryData=null,plates=[];')
 # Normalize the language dictionary instead of accumulating outdated override blocks.
 prefix=js[:js.index("let lang='en';")]
 node=root/'node-v22.16.0-linux-x64/bin/node'
 bundle=json.loads(subprocess.check_output([str(node),'-e',"const fs=require('fs'),vm=require('vm');const p=fs.readFileSync(process.argv[1],'utf8').split('\\n').filter(l=>!l.startsWith('import ')).join('\\n');const h=p.slice(0,p.indexOf(\"let lang='en';\"));process.stdout.write(vm.runInNewContext(h+';JSON.stringify({lex,work})'));",str(dist/'portfolio.js')],text=True))
 copy={
 'en':{'heroIntro':'One Kanda–Nihonbashi study area, with detailed design focused on Kajicho 1 & 2, towards 2050.','heroCaption':'Street blocks define one working boundary; building models remain whole.','scopeLabel':'STUDY AREA','scopeValue':'Kanda–Nihonbashi','contextTitle':'Documents into design decisions','contextIntro':'Read each document as a short chain: source requirement, local check and design action.','mappingTitle':'One boundary, eight themes','mappingIntro':'Every map uses the same study area. Legends are readable on the page; buildings remain whole.','mapFoot':'Purple: the single study boundary, aligned to street blocks. Kajicho 1 & 2 is the named detailed focus.','mapExtent':'One street-block boundary · EPSG:6677 · North up','boundaryTitle':'A clear working boundary','boundaryIntro':'Figure 5 guides the district. Connected street blocks define the working line; Kajicho remains the detailed focus.','edition':'Urban Design Studio 2026 · Theme B · 2026.10.18','footer':'One study area · 2026.10.18','contextPackageNote':'One area · current CSV tables · document sources','atlasPackageNote':'8 thematic PNG maps + overview · portable QGIS','cfdStatus':'Simulation update: fix the geometry, choose a pilot and screen the computational domain before new cases.','cfdLink':'Simulation update plan','parameterLink':'Select the next study','navStudies':'Next studies','simulationTitle':'Prepare the next simulations','simulationIntro':'Keep the project boundary fixed, then choose the question, pilot and model inputs.','evidenceIntro':'Each measure uses the study area or names its independent source unit.'},
 'zh':{'heroIntro':'以统一的神田—日本桥研究区为基础，围绕鍛冶町一、二丁目开展详细设计，面向 2050 年。','heroCaption':'沿街区确定一条工作边界，建筑模型保持完整。','scopeLabel':'STUDY AREA / 研究区','scopeValue':'神田—日本桥','contextTitle':'从文件要求到设计行动','contextIntro':'用“来源要求 → 场地核查 → 设计行动”简要阅读每份文件。','mappingTitle':'一条边界，八类专题','mappingIntro':'所有地图使用同一研究区。图例可直接在网页阅读，建筑保持完整。','mapFoot':'紫色为沿街区确定的唯一研究区边界；鍛冶町一、二丁目是详细设计重点。','mapExtent':'一条街区边界 · EPSG:6677 · 北向上','boundaryTitle':'明确一条工作边界','boundaryIntro':'任务书第 5 图确定研究地区，连续街区落实具体边线；鍛冶町保留为详细设计重点。','edition':'Urban Design Studio 2026 · Theme B · 2026.10.18','footer':'统一研究区 · 2026.10.18','contextPackageNote':'一个研究区 · 当前 CSV · 文件来源','atlasPackageNote':'8 张专题 PNG＋总图 · 便携 QGIS','cfdStatus':'仿真调整：先固定几何、选择试点并检查计算域，再建立新情景。','cfdLink':'仿真调整计划','parameterLink':'确定下一步研究','navStudies':'后续研究','simulationTitle':'准备下一轮仿真','simulationIntro':'固定项目边界，再选择问题、试点与模型输入。','evidenceIntro':'各项数据采用研究区范围，或明确其独立的来源单位。'},
 'ja':{'heroIntro':'神田・日本橋の一つの研究区域を基に、鍛冶町一・二丁目で2050年へ向けた詳細設計を進める。','heroCaption':'街区に沿う一つの作業境界。建物モデルを切断しない。','scopeLabel':'STUDY AREA / 研究区域','scopeValue':'神田・日本橋','contextTitle':'資料の要求から設計の行動へ','contextIntro':'出典の要求、現地確認、設計の行動を短い流れで読む。','mappingTitle':'一つの境界、八つの主題','mappingIntro':'全図に同じ研究区域を使う。凡例はページ上で読み、建物を完全な形で示す。','mapFoot':'紫は街区に沿う一つの研究境界。鍛冶町一・二丁目が詳細設計の重点。','mapExtent':'一つの街区境界 · EPSG:6677 · 北向き','boundaryTitle':'明確な作業境界','boundaryIntro':'課題書図5の地区を、連続した街区で具体化。鍛冶町を詳細設計の重点とする。','edition':'Urban Design Studio 2026 · Theme B · 2026.10.18','footer':'一つの研究区域 · 2026.10.18','contextPackageNote':'一つの区域 · 現在のCSV · 文献出典','atlasPackageNote':'主題PNG8枚＋全体図 · 可搬QGIS','cfdStatus':'計算の更新：幾何を固定し、試行場所と計算領域を確認してから新ケースを作る。','cfdLink':'計算更新の計画','parameterLink':'次の研究を決める','navStudies':'次の研究','simulationTitle':'次の計算を準備する','simulationIntro':'対象境界を固定し、問い、試行場所、モデル入力を選ぶ。','evidenceIntro':'各値は研究区域又は明記した出典単位を使う。'}}
 for lang,values in copy.items():bundle['lex'][lang].update(values)
 js="import {renderPolicyDiagrams} from './policy-diagrams.js?v=20261018';\nimport {renderSimulationPlan} from './simulation-plan.js?v=20261018';\n"+js[:js.index('const lex=')]+"const lex="+json.dumps(bundle['lex'],ensure_ascii=False)+";\nconst work="+json.dumps(bundle['work'],ensure_ascii=False)+";\n"+js[js.index("let lang='en';"):]
 start=js.index('function renderContext(){');end=js.index('function dataTable',start)
 js=js[:start]+"function renderContext(){const list=$('#context-list'),brief=$('#brief-checklist');if(!study){list.replaceChildren(el('p',lex[lang][loadFailed?'loadError':'loading']));return;}renderPolicyDiagrams(study,lang,{briefHost:brief,topicHost:list});}\n"+js[end:]
 js=js.replace("if(url.startsWith('boundary-atlas/maps/')){img.width=3200;img.height=2400;}","")
 js=js.replace("article.append(plateFigure(localized(c.title),c.file,c.preview),text);charts.append(article);", "if(chartIndex>=5)article.append(plateFigure(localized(c.title),c.file,c.preview));else{article.classList.add('evidence-data-only');text.prepend(link(localized({en:'See the map and legend',zh:'查看地图与图例',ja:'地図と凡例を見る'}),(c.map_target==='map-00_study_area'?'#study-area':'#'+c.map_target)));}article.append(text);charts.append(article);")
 seismic_start=js.index(' if(study.seismic?.rows?.length)')
 seismic_end=js.index('\n}\nfunction mapSheet',seismic_start) if '\n}\nfunction mapSheet' in js else js.index('\n}\nfunction renderMaps',seismic_start)
 js=js[:seismic_start]+''' if(study.seismic?.rows?.length){const section=$('#seismic-risk');section.append(el('p','EARTHQUAKE + FIRE / 2022','kicker'),el('h3',t.seismicTitle),el('p',localized({en:'23 intersecting town units, including 15 partial census units. Published values describe the complete official towns.',zh:'相交的23个町丁目中，有15个国势调查单元仅部分位于研究区。官方风险数值对应完整町丁目。',ja:'重なる23町丁目のうち15国勢調査単位は一部のみ対象区域内。公式危険度は町丁目全体の値。'})),el('p',localized({en:'Rank 1 → 5: lower → higher relative risk. Overlap is the fraction of full 2020 census geometry; it never weights risk.',zh:'等级1→5：相对风险由低到高。相交比例按完整2020年调查几何计算，不用于加权风险。',ja:'ランク1→5：相対危険度の低→高。重なり率は2020年調査図形全体に対する比率で、危険度の重みには使わない。'}),'chart-method'));const c=study.charts.find(c=>c.presentation==='native_table'),matrix=dataTable(c.headers,c.rows);matrix.classList.add('risk-matrix');matrix.querySelectorAll('tbody tr').forEach((tr,i)=>{const row=study.seismic.rows[i];if(row.focus){tr.classList.add('risk-focus');tr.cells[0].append(el('span',localized({en:'Focus',zh:'重点',ja:'重点'}),'risk-focus-label'));}for(const index of [2,4,5]){const cell=tr.cells[index];cell.classList.add('risk-rank','rank-'+cell.textContent);}});section.append(matrix,el('p',t.seismicNote),sources(study.seismic.sources));}
''' +js[seismic_end:]
 start=js.index('function mapSheet(') if 'function mapSheet(' in js else js.index('function renderMaps(){');end=js.index('\nfunction render(){',start)
 js=js[:start]+'''function mapSheet(p){const layout=el('div',undefined,'map-sheet');const fig=plateFigure(localized(p.title),p.file,p.preview);const image=fig.querySelector('img');if(p.preview_pixels){image.width=p.preview_pixels[0];image.height=p.preview_pixels[1];}const aside=el('aside',undefined,'map-legend');aside.setAttribute('aria-label','Legend');aside.append(el('h4',localized({en:'Legend',zh:'图例',ja:'凡例'})));const ul=el('ul');for(const entry of p.legend){const row=el('li'),swatch=el('span',undefined,'map-key '+entry.kind);swatch.style.setProperty('--key-color',entry.color);if(entry.dash)swatch.classList.add('dash');row.append(swatch,el('span',localized(entry.label)));ul.append(row);}aside.append(ul,el('p',localized(p.reading_note),'map-note'),link(localized({en:'Sources and methods',zh:'来源与方法',ja:'出典と方法'}),'study-atlas/source_manifest.json','map-source'));layout.append(fig,aside);return layout;}
function renderMaps(){const box=$('#all-maps');box.replaceChildren();plates.filter(p=>p.kind==='theme').forEach((p,i)=>{const article=el('article',undefined,'map-reading');article.id='map-'+p.id;article.append(el('p','MAP '+String(i+1).padStart(2,'0'),'kicker'),el('h3',localized(p.title)),mapSheet(p));box.append(article);});}
function renderBoundaries(data){const box=$('#boundary-content');box.replaceChildren();box.append(mapSheet(data.plates.find(p=>p.kind==='overview')));const note=el('p',localized({en:'The brief marks an approximate wider district. The edge register defines one street-block working boundary, with no split building models.',zh:'任务书给出约略外围地区，边线记录将其落实为一条街区工作边界，建筑模型不被切开。',ja:'課題書の概略周辺地区を、一つの街区作業境界として記録。建物モデルを切断しない。'}),'study-boundary-note');box.append(note,sources([{document_title:{en:'Official Theme B brief',zh:'Theme B 官方任务书',ja:'Theme B公式課題書'},url:'https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view',year:'2026',page:'p.4 / Figure 5'}]),link(localized({en:'Boundary street register',zh:'边线与街道记录',ja:'境界と街路の記録'}),'study-atlas/boundary_edges.csv','map-source'));}
''' +js[end:]
 js=js.replace('renderSimulationPlan(lang,$("#simulation-content"));','')
 js=js.replace('renderContext();renderEvidence();renderMaps();','renderContext();renderEvidence();renderMaps();renderSimulationPlan(lang,$("#simulation-content"));')
 js=js.replace('boundary-atlas/atlas.json','study-atlas/atlas.json')
 (dist/'portfolio.js').write_text(js)
 html=(dist/'index.html').read_text();html=html.replace('id="course-boundaries"','id="study-area"').replace('COURSE AREAS / 2026','ONE STUDY AREA / 2026').replace('>COURSE AREAS<','>STUDY AREA<').replace('Registered primary, wider brief and poster study outlines','One street-block study boundary and complete building models').replace('boundary-atlas/maps/previews/course_00_overview.jpg','study-atlas/maps/previews/00_study_area.jpg')
 html=html.replace('boundary-atlas/source_manifest.json','study-atlas/source_manifest.json').replace('boundary-atlas/atlas.geojson','study-atlas/atlas.geojson').replace('href="studies.html"','href="#simulation-plan"').replace('href="cfd.html"','href="#simulation-plan"')
 section='<section class="folio-section" id="simulation-plan"><div class="section-head"><span class="number">04</span><div><p class="kicker">NEXT STUDIES</p><h2 data-t="simulationTitle">Prepare the next simulations</h2></div><p data-t="simulationIntro">Keep the project boundary fixed, then choose the question, pilot and model inputs.</p></div><div id="simulation-content"></div></section>'
 if 'id="simulation-plan"' not in html:html=html.replace('<section class="folio-section" id="questions">',section+'\n<section class="folio-section" id="questions">')
 for key,value in bundle['lex']['en'].items():
  if isinstance(value,str):html=re.sub(r'(<([a-z0-9]+)\b[^>]*data-t="'+re.escape(key)+r'"[^>]*>)[^<]*(</\2>)',lambda m:m.group(1)+value+m.group(3),html)
 for css in ['policy-diagrams.css','simulation-plan.css','study-mapping.css']:
  if css not in html:html=html.replace('</head>','<link rel="stylesheet" href="'+css+'?v=20261018"></head>')
 html=html.replace('id="questions"><div class="section-head"><span class="number">04</span>','id="questions"><div class="section-head"><span class="number">05</span>')
 (dist/'index.html').write_text(html)
 # Every served map reference now resolves to the single-area atlas, including the drawing guide.
 for p in dist.rglob('*'):
  if p.suffix not in ('.html','.js'):continue
  text=p.read_text();text=text.replace('boundary-atlas/maps/course_03_building_use.png','study-atlas/maps/03_building_use.png').replace('boundary-atlas/maps/previews/course_03_building_use.jpg','study-atlas/maps/previews/03_building_use.jpg').replace('boundary-atlas/source_manifest.json','study-atlas/source_manifest.json').replace('index.html#course-boundaries','index.html#study-area')
  if p.suffix=='.html':text=re.sub(r'((?:src|href)="(?:portfolio|team|app|cfd|domain-map|styles)[^"/?]*\.(?:js|css))(?:\?[^\"]*)?"',r'\1?v=20261018-study"',text)
  p.write_text(text)
 # The current locator contains one study line; historical solver boxes remain technical views.
 dm=read(dist/'data/domain-map.geojson');dm['features']=[f for f in dm['features'] if f['properties'].get('role') not in ('primary_brief','secondary_brief','poster_blue','design_area','study_area')]
 boundary=read(target/'study_boundary.geojson')['features'][0];dm['features'].append({'type':'Feature','properties':{'role':'study_area','name':'Kanda–Nihonbashi study area'},'geometry':boundary['geometry']});write(dist/'data/domain-map.geojson',dm)
 dj=(dist/'domain-map.js').read_text();dj=dj.replace("['design_area', colors.design, '2 3', 2, .03],\n    ['primary_brief','#59457f',null,3,.06],\n    ['secondary_brief','#a46d32','6 4',2,0],\n    ['poster_blue','#27abd1',null,2,0]", "['study_area','#59457f',null,3,.04]")
 dj=dj.replace("['primary_brief','secondary_brief','poster_blue']","['study_area']").replace("feature(data,'design_area')","feature(data,'study_area')").replace("feature(data, 'design_area')","feature(data, 'study_area')")
 dj=re.sub(r'const courseCopy=.*?;for\(const l of Object.keys\(courseCopy\)\)Object.assign\(copy\[l\],courseCopy\[l\]\);',"const courseCopy="+json.dumps({l:{'designLegend':label,'coreLabel':label,'note':note} for l,label,note in [('en','Current study area','Purple: current single study boundary. Model envelope and domain views describe the archived experiment; the new simulation plan is on the main page.'),('zh','当前研究区','紫色为当前唯一研究区边界。模型与计算域视图记录历史试验，新仿真调整计划见主页。'),('ja','現在の研究区域','紫は現在の一つの研究境界。モデルと計算領域は旧試行で、新計算計画はメインページに示す。')]},ensure_ascii=False)+";for(const l of Object.keys(courseCopy))Object.assign(copy[l],courseCopy[l]);",dj,flags=re.S)
 archive_copy={'en':{'title':'Archived computational coverage','detail':'Current study area and archived model','model':'Archived model extent','full':'Archived air domain','sourceText':'OSM map; PLATEAU 2025 buildings; air domain from the archived solver mesh.','detailAria':'Current study area with archived model coverage','overviewAria':'Archived computational domain and boundary conditions'},'zh':{'title':'历史计算范围','detail':'当前研究区与历史模型','model':'历史模型范围','full':'历史空气计算域','sourceText':'OSM 底图；PLATEAU 2025 建筑；空气计算域来自历史求解网格。','detailAria':'当前研究区与历史模型覆盖','overviewAria':'历史计算域与边界条件'},'ja':{'title':'旧計算の範囲','detail':'現在の研究区域と旧モデル','model':'旧モデルの範囲','full':'旧空気計算領域','sourceText':'OSM地図、PLATEAU 2025建物、旧ソルバーメッシュの計算領域。','detailAria':'現在の研究区域と旧モデル範囲','overviewAria':'旧計算領域と境界条件'}}
 if 'const archiveCopy=' not in dj:dj=dj.replace('let language =', 'const archiveCopy='+json.dumps(archive_copy,ensure_ascii=False)+';for(const l of Object.keys(archiveCopy))Object.assign(copy[l],archiveCopy[l]);\nlet language =')
 (dist/'domain-map.js').write_text(dj)
 banner='<aside class="course-scope-note" style="padding:18px 24px;background:#f7f5ef;color:#36353a;border-bottom:2px solid #59457f;font:17px/1.6 sans-serif"><b>Study area update · 2026-10-18</b><p><a href="index.html#study-area">One street-block boundary and current data</a> · <a href="index.html#simulation-plan">Simulation update plan</a>. Existing numerical trials retain their archived input geometry and acceptance state.</p></aside>'
 for name in ['team.html','studies.html','cfd.html','style-guide.html']:
  p=dist/name;text=p.read_text();text=re.sub(r'<aside class="course-scope-note".*?</aside>',banner,text,flags=re.S);p.write_text(text)
 # Keep current team handover roles synchronized; source history stays in dated repository folders.
 tj=(dist/'team.js').read_text();tj=tj.replace('Kanda_Nihonbashi_Course_2026-10-16.qgz','Kanda_Nihonbashi_Study_2026-10-18.qgz').replace('primary_brief, secondary_brief and poster_blue; census_legacy is the historical comparison.','study_area, the single current boundary.').replace('primary_brief、secondary_brief、poster_blue 是三条来源边线；census_legacy 是历史统计边界对照。','study_area 是唯一当前研究区边界。').replace('primary_brief、secondary_brief、poster_blue は出典境界、census_legacy は旧統計区域。','study_area は現在の一つの研究境界。')
 tj=tj.replace('277 primary / 1,087 wider / 1,070 poster models',f"{sm['selected_models']:,} complete study-area models").replace('重点 277／外围 1,087／海报 1,070 个模型',f"研究区 {sm['selected_models']:,} 个完整模型").replace('重点277／周辺1,087／ポスター1,070モデル',f"研究区域の完全な{sm['selected_models']:,}モデル").replace('Three registered course outlines and the historical census reference','One street-block study boundary').replace('三条课程来源边线与历史统计边界','一条街区研究边界').replace('三つの出典境界と旧統計区域','一つの街区研究境界').replace('19 spatial layers + membership table','16 spatial layers + membership table').replace('19 个空间图层＋成员表','16 个空间图层＋成员表').replace('19 空間レイヤー＋対応表','16 空間レイヤー＋対応表').replace('2026-10-16 registered outlines','2026-10-18 street-block boundary').replace('2026-10-16 配准边线','2026-10-18 街区边界').replace('2026-10-16の位置合わせ境界','2026-10-18の街区境界').replace('course_membership','study_membership')
 tj=tj.replace('Representative-point selection; actual energy remains missing','Complete source projections; actual energy remains missing').replace('代表点选取；真实用能仍缺失','完整源投影选取；真实用能仍缺失').replace('代表点で選択。実使用量は未取得','元の投影全体を選択。実使用量は未取得').replace('代表点抽出。実エネルギーは未取得','元の投影全体を選択。実エネルギーは未取得')
 tj=tj.replace('Choose the matching area','Read study membership').replace('选取相应范围','读取研究区成员').replace('対応する区域を選ぶ','研究区域の対応表を読む').replace('Both-source land use and MLIT zones','Tokyo 2021 land use and MLIT zones').replace('两份源用地面与 MLIT 用途地域','东京2021用地与 MLIT 用途地域').replace('両出典の土地利用と MLIT 用途地域','東京2021土地利用とMLIT用途地域')
 tj=tj.replace('Four source scenarios / three areas','Four source scenarios / one study area').replace('四个源情景／三个范围','四个源情景／一个研究区').replace('四シナリオ／三区域','四シナリオ／一研究区域')
 (dist/'team.js').write_text(tj)
 from assemble_figure5_view import apply
 apply(root)
 from install_research_review import apply as install_review
 install_review(root)
 from refresh_current_delivery import apply as refresh_delivery
 refresh_delivery(root)
 from install_environment_plan import apply as install_environment
 install_environment(root)
 from install_sunday_fieldwork import apply as install_fieldwork
 install_fieldwork(root)
 from install_site_navigation import apply as install_navigation
 install_navigation(root)
 from install_page_outline import apply as install_outline
 install_outline(root)
 # Match the remote shared repository snapshot to the opened Site source.
 mirror=team/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist'
 if mirror.exists():shutil.rmtree(mirror)
 shutil.copytree(dist,mirror)
 print(json.dumps({'status':'assembled','source_outlines':2,'area_ha':sm['area_ha'],'models':sm['selected_models'],'themes':9,'policy_topics':len(ctx['topics']),'new_cfd':False}),flush=True)

if __name__=='__main__':main()
