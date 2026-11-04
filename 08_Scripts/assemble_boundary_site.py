#!/usr/bin/env python3
"""Publish corrected scope data into the existing Site source, on the remote host."""
import argparse,csv,json,re,shutil,zipfile
from pathlib import Path

REPO='https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho'
NAMES={'primary_brief':('鍛冶町重点区','Kajicho primary','鍛冶町重点区域'),'secondary_brief':('神田—日本桥外围区','Kanda–Nihonbashi wider','神田・日本橋周辺'),'poster_blue':('海报蓝线区','Poster blue','ポスター青線')}
def tr(zh,en,ja=None):return {'zh':zh,'en':en,'ja':ja or en}
def jread(p):return json.loads(p.read_text())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def nice(n,d=2):return f'{n:,.{d}f}' if isinstance(n,(int,float)) else '—'
def rows(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def public_clean(v):
    if isinstance(v,dict):return {k:public_clean(x) for k,x in v.items() if k not in ('host','pid','runtime','output_gpkg')}
    if isinstance(v,list):return [public_clean(x) for x in v]
    if isinstance(v,str):return re.sub(r'/home/mdxuser/urban_design_studio_2026/boundary_20261016/','',v)
    return v

def main():
    p=argparse.ArgumentParser();p.add_argument('--team',type=Path,required=True);p.add_argument('--site',type=Path,required=True);a=p.parse_args()
    if (a.site/'dist/study-atlas').exists():
        p.error('Current study-area release is active. Use assemble_study_site.py --task-root <task-root>; this dated assembler cannot overwrite current maps.')
    dist=a.site/'dist';atlasdir=dist/'boundary-atlas';atlas=jread(atlasdir/'atlas.json');stats=jread(atlasdir/'statistics.json')['scopes'];ctxp=dist/'context-study/context.json';ctx=jread(ctxp)
    for fn in ('source_manifest.json','registration.json','statistics.json','atlas.json'):write(atlasdir/fn,public_clean(jread(atlasdir/fn)))
    public_readme=atlasdir/'README.md'
    if public_readme.exists():public_readme.write_text(public_readme.read_text().replace('../../05_QGIS/',REPO+'/blob/main/05_QGIS/').replace('../../04_Data/',REPO+'/blob/main/04_Data/'))
    metrics=[]
    for sid,names in NAMES.items():
        m=stats[sid];label=tr(*names)
        metrics.extend([{'label':{l:label[l]+(' / 面积' if l=='zh' else ' / Area') for l in label},'value':round(m['area_ha'],2),'unit':'ha','note':tr('官方图像配准后的参考边线面积。','Area of the registered reference outline.','公式画像を位置合わせした参照線の面積。')},{'label':{l:label[l]+(' / 建筑模型' if l=='zh' else ' / Models') for l in label},'value':m['selected_models'],'unit':'','note':tr('按模型代表点入区选择；跨边线对象另列。','Models selected by representative point; crossing objects are reported separately.','代表点で抽出し、境界を横断する建物を別記。')}])
    ctx['metrics']=metrics;ctx['date']='2026-10-16'
    src=[{'document_title':tr('2026 年官方海报','Official 2026 poster','2026年公式ポスター'),'url':'https://www.due.t.u-tokyo.ac.jp/english/wp-content/uploads/sites/2/2026/09/urbandesignstudio2026_a2.png','year':'2026','page':'Theme B blue outline'},{'document_title':tr('Theme B 官方任务书','Official Theme B brief','Theme B公式課題書'),'url':'https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view','year':'2026','page':'p.4 / Figure 5'}]
    def chart(i,title,finding,method,limits,headers,data,file):
        return {'id':i,'title':title,'finding':finding,'method':method,'limits':limits,'headers':headers,'rows':data,'file':'boundary-atlas/maps/'+file+'.png','preview':'boundary-atlas/maps/previews/'+file+'.jpg','sources':src,'design_meaning':tr('以相应区域的底图选择现场核查位置。','Use the map for the named area to choose field checks.','記載区域の地図から現地確認箇所を選ぶ。')}
    names=lambda s:tr(*NAMES[s])
    commonmethod=tr('边线按官方原图配准；建筑代表点用于选对象，建筑投影并集按相交面积计算。','Register official source outlines. Select models by representative point; intersect and dissolve footprints for area coverage.','公式図を位置合わせ。建物は代表点で抽出し、面積は投影の共通部分を統合して計算。')
    limits=tr('原图线宽和控制点残差限制边线精度。外围虚线沿用任务书的约略含义；统计敏感性另表。','Source stroke width and control residuals limit edge precision. The dashed wider area remains approximate; membership sensitivity is provided.','原図の線幅と制御点残差が精度を制約。周辺の破線は概略範囲で、抽出感度を別表に示す。')
    charts=[]
    charts.append(chart('01_building_coverage',tr('三个来源范围分别统计','Three source areas, separate totals','三つの出典区域を別々に集計'),tr('总图同时展示重点区、任务书外围区和海报蓝线区。','The overview shows primary, brief wider and poster blue outlines together.','重点区域、課題書の周辺区域、ポスター青線を同時に表示。'),commonmethod,limits,[tr('区域','Area','区域'),tr('面积 / ha','Area / ha','面積 / ha'),tr('模型数','Models','モデル数'),tr('投影覆盖率','Footprint coverage','投影被覆率'),tr('跨边线模型','Crossing models','境界横断モデル')],[[names(s),nice(m['area_ha']),m['selected_models'],nice(m['gross_footprint_coverage_pct'])+'%',m['boundary_crossing_selected_models']] for s,m in stats.items()],'course_00_overview'))
    data=rows(atlasdir/'tables/building_use.csv')
    charts.append(chart('02_building_use',tr('建筑用途按范围重算','Building use by area','区域別建物用途'),tr('用途来自建筑源属性，各范围使用各自模型数作为分母。','Uses come from source attributes; each area uses its own model-count denominator.','建物属性の用途を使い、区域ごとのモデル数を分母とする。'),commonmethod,tr('楼面代理是投影面积乘源层数或代理层数；真实延床面积和用能仍待获取。','Floor proxy is projection area times source or proxy levels. Actual floor area and energy remain missing.','延べ面積代理は投影面積と出典又は推定階数の積。実面積とエネルギーは未取得。'),[tr('区域','Area'),tr('用途','Use'),tr('模型数','Models'),tr('数量占比','Count share'),tr('楼面代理占比','Floor proxy share')],[[names(r['scope']),r['use'],int(r['models']),nice(float(r['count_share_pct']))+'%',nice(float(r['floor_proxy_share_pct']))+'%' if r['floor_proxy_share_pct'] else '—'] for r in data],'course_03_building_use'))
    data=rows(atlasdir/'tables/land_use.csv')
    charts.append(chart('03_land_use_area',tr('土地利用覆盖与分类面积','Land use coverage and class area','土地利用の被覆と分類面積'),tr('两区官方原始土地利用面已重新提取，并按三条来源边线分别裁剪。','Original land-use polygons from both ward packages are re-extracted and clipped to each source outline.','両区パッケージの土地利用原図を再抽出し、出典境界ごとに切り出す。'),tr('每类先求并集，再计算区域内面积；覆盖缺口和类别重叠另记。','Dissolve within each class, then intersect each area. Report unmapped area and overlap between classes.','分類内を統合して区域と交差。未被覆部分と分類間重複を別記。'),tr('2021 年调查与 2025 年模型年份分列。现状用地与法定用途地域分别成图。','Keep the 2021 survey and 2025 model years separate. Observed land use and planning zones use separate maps.','2021年調査と2025年モデルを分記。現況利用と法定用途地域は別図。'),[tr('区域','Area'),tr('分类','Class'),tr('面积 / m²','Area / m²'),tr('区域占比','Area share')],[[names(r['scope']),r['label'],nice(float(r['area_m2']),0),nice(float(r['scope_share_pct']))+'%'] for r in data],'course_05_land_use'))
    counts={}
    for r in rows(atlasdir/'tables/height_models.csv'):counts[(r['scope'],r['class'])]=counts.get((r['scope'],r['class']),0)+1
    charts.append(chart('04_building_height',tr('源高度与代理高度分列','Source and proxy heights','出典高さと推定高さ'),tr('每个范围重新统计源高度与代理高度；中位数只使用有效源高度。','Recount source and proxy heights for each area. Medians use valid source heights.','区域ごとに出典・推定高さを集計。中央値は有効な出典高さのみ。'),commonmethod,tr('PLATEAU measuredHeight 是模型源字段；代理高度单列。','PLATEAU measuredHeight is a model source field. Proxy heights form a separate class.','PLATEAU measuredHeightはモデルの出典属性。推定高さを別分類とする。'),[tr('区域','Area'),tr('高度组','Height class'),tr('模型数','Models')],[[names(s),k,v] for (s,k),v in counts.items()],'course_04_building_height'))
    data=rows(atlasdir/'tables/flood_scenarios.csv')
    charts.append(chart('05_flood_sources',tr('洪水情景分别叠加','Separate flood scenarios','洪水シナリオ別の重ね合わせ'),tr('2018、2021 与 2024 年源情景保留各自范围、日期和规模。','Keep the 2018, 2021 and 2024 source scenarios, dates and scales separate.','2018・2021・2024年の出典範囲、日付、規模を分ける。'),tr('建筑先按相应区域选择；暴露按区域内投影与情景面正面积相交计算。','Select buildings for each area. Exposure requires positive overlap between within-area footprints and scenario polygons.','区域ごとに抽出し、区域内投影とシナリオ面の正面積交差を算定。'),tr('没有记录到源面相交不等于安全。图示为 2018 神田川 L2；其余情景见表。','No recorded polygon overlap does not establish safety. The map shows Kanda 2018 L2; the table reports every scenario.','出典面との交差がないことは安全を意味しない。地図は神田川2018 L2、全シナリオは表に示す。'),[tr('区域','Area'),tr('源情景','Source scenario'),tr('源日期','Source date'),tr('相交面积 / m²','Overlap / m²'),tr('模型数','Models')],[[names(r['scope']),r['scenario'],r['source_date'],nice(float(r['recorded_overlap_m2']),0),int(r['exposed_selected_models'])] for r in data],'course_08_flood'))
    # These two source units are independent of a course boundary change.
    charts.extend(ctx['charts'][5:]);ctx['charts']=charts;ctx['boundary_release']='2026-10-16';ctx['source_scopes']=list(NAMES)
    write(ctxp,ctx)
    # Replace publicly served stale tables and plate images; source readings stay.
    analysis=dist/'context-study/analysis'
    if analysis.exists():shutil.rmtree(analysis)
    shutil.copytree(atlasdir/'tables',analysis)
    # Remove obsolete downloadable bundles from the served source.
    for folder in (dist/'portfolio',dist/'context-study'):
        for file in folder.glob('*.zip'):file.unlink()
    package=REPO+'/archive/refs/heads/main.zip'
    html=(dist/'index.html').read_text();html=html.replace('portfolio/maps/previews/01_figure_ground_map.jpg','boundary-atlas/maps/previews/course_00_overview.jpg').replace('Kajicho figure-ground map with core boundary, buildings, streets and north arrow','Registered primary, wider brief and poster study outlines').replace('01 / FIGURE GROUND','COURSE AREAS / 2026')
    html=html.replace('portfolio/mapping_data/map_manifest.json','boundary-atlas/source_manifest.json').replace('portfolio/mapping_data/atlas.geojson','boundary-atlas/atlas.geojson')
    html=re.sub(r'href="(?:https://drive.google.com/file/d/1zSJaSWM6WXMdMsgJQJG5Nd6M9kechosz/view\?usp=drivesdk|context-study/Kajicho_Context_Study_2026-10-15_EN.zip|portfolio/Kajicho_Field_Atlas_2026-10-15.zip)"',f'href="{package}"',html)
    html=html.replace('TAR.XZ · main · 2026.10.15','GitHub ZIP · current main')
    if 'id="course-boundaries"' not in html:html=html.replace('<div id="metrics"','<section id="course-boundaries" class="folio-section"><div class="section-head"><span class="number">00</span><div><p class="kicker">COURSE AREAS</p><h2 data-t="boundaryTitle">Read both study levels</h2></div><p data-t="boundaryIntro">Source outlines, registration and separate totals.</p></div><div id="boundary-content"></div></section>\n<div id="metrics"')
    js=(dist/'portfolio.js').read_text()
    if 'const plates=[' in js:
        start=js.index('const plates=[');end=js.index('\n];',start)+3;js=js[:start]+'let plates=[];'+js[end:]
    js=re.sub(r'\nconst boundaryCopy=.*?;for\(const l of Object.keys\(boundaryCopy\)\)Object.assign\(lex\[l\],boundaryCopy\[l\]\);\n','\n',js)
    js=re.sub(r'\nfetch\("boundary-atlas/atlas.json"\).*?\n','\n',js)
    replacements={
      'en':{'heroIntro':'Read the wider Kanda–Nihonbashi study area together with the Kajicho primary area, towards 2050.','heroCaption':'Official brief primary and approximate wider areas, with the poster blue outline','scopeLabel':'COURSE AREAS','scopeValue':'Kanda–Nihonbashi + Kajicho','mappingTitle':'Source areas, eight themes','mappingIntro':'Each source area has its own maps and totals. All outlines remain visible so their differences can be read directly.','mapFoot':'Purple: brief primary. Brown dashed: approximate wider area. Blue: official poster. Original raster line widths and registration residuals limit edge precision.','mapExtent':'Registered official source areas · EPSG:6677 · North up','edition':'Urban Design Studio 2026 · Theme B · 2026.10.16','footer':'Course boundary edition · 2026.10.16','packageLink':'Get current main · GitHub','atlasPackage':'Get maps and GIS · current main','atlasPackageNote':'26 PNG maps · three source areas · portable QGIS','contextPackage':'Get current data and methods','contextPackageNote':'CSV · source registration · separate area totals','boundaryTitle':'Read both study levels','boundaryIntro':'The official brief defines primary and approximate wider areas. The poster blue outline is traced separately.'},
      'zh':{'heroIntro':'先读神田—日本桥外围研究区，再进入鍛冶町重点区，连接面向 2050 年的建筑、街道和地区管理行动。','heroCaption':'任务书重点区与约略外围区，并列海报蓝线','scopeLabel':'COURSE AREAS / 课程范围','scopeValue':'神田—日本桥＋鍛冶町','mappingTitle':'按来源范围阅读八类专题','mappingIntro':'三个来源范围分别出图、分别统计；各图同时保留其他来源边线，便于对照。','mapFoot':'紫色为任务书重点区；棕色虚线为约略外围区；蓝色为官方海报线。原图线宽与配准残差限制边线精度。','mapExtent':'官方原图配准 · EPSG:6677 · 北向上','edition':'Urban Design Studio 2026 · Theme B · 2026.10.16','footer':'课程边界更新版 · 2026.10.16','packageLink':'领取当前 main · GitHub','atlasPackage':'领取地图与 GIS · 当前 main','atlasPackageNote':'26 幅 PNG · 三个来源范围 · 便携 QGIS','contextPackage':'领取当前数据与方法','contextPackageNote':'CSV · 边界配准 · 分区统计','boundaryTitle':'先读两级课程范围','boundaryIntro':'任务书区分重点区与约略外围区；海报蓝线按独立来源配准。'},
      'ja':{'heroIntro':'神田・日本橋の周辺研究区域と鍛冶町の重点区域を読み、2050年へ向けた建物・街路・地域運営を考える。','heroCaption':'課題書の重点・概略周辺区域とポスター青線','scopeLabel':'COURSE AREAS / 授業対象区域','scopeValue':'神田・日本橋＋鍛冶町','mappingTitle':'出典区域ごとの八つの主題','mappingIntro':'三つの出典区域を別々に作図・集計し、他の出典境界も併記する。','mapFoot':'紫：課題書重点区域。茶破線：概略周辺区域。青：公式ポスター。原図の線幅と位置合わせ残差が境界精度を制約する。','mapExtent':'公式原図の位置合わせ · EPSG:6677 · 北向き','edition':'Urban Design Studio 2026 · Theme B · 2026.10.16','footer':'授業対象区域の更新版 · 2026.10.16','packageLink':'現在の main を取得 · GitHub','atlasPackage':'地図と GIS を取得 · 現在の main','atlasPackageNote':'26 PNG · 三つの出典区域 · 可搬 QGIS','contextPackage':'現在のデータと方法','contextPackageNote':'CSV · 境界の位置合わせ · 区域別集計','boundaryTitle':'授業の二段階の区域を読む','boundaryIntro':'課題書は重点区域と概略周辺区域を分ける。ポスター青線は独立した出典として位置合わせする。'}}
    for key,value in replacements['en'].items():
        html=re.sub(r'(<([a-z0-9]+)\b[^>]*data-t="'+re.escape(key)+r'"[^>]*>)[^<]*(</\2>)',lambda m:m.group(1)+value+m.group(3),html)
    (dist/'index.html').write_text(html)
    insert='\nconst boundaryCopy='+json.dumps(replacements,ensure_ascii=False)+';for(const l of Object.keys(boundaryCopy))Object.assign(lex[l],boundaryCopy[l]);\n'
    anchor="let lang='en';";js=js.replace(anchor,insert+anchor)
    oldstart=js.index('function renderMaps(){');oldend=js.index('\nfunction render(){',oldstart)
    js=js[:oldstart]+'''function renderMaps(){const box=$('#all-maps');box.replaceChildren();plates.forEach((p,i)=>{const article=el('article',undefined,'map-reading');article.append(el('p','PLATE '+String(i+1).padStart(2,'0'),'kicker'),el('h3',localized(p.title)),plateFigure(localized(p.title),p.file,p.preview));box.append(article);});}
function renderBoundaries(data){const box=$('#boundary-content');box.replaceChildren();box.append(plateFigure(localized(data.plates[0].title),data.plates[0].file,data.plates[0].preview));const rows=Object.entries(data.scopes).map(([key,s])=>[localized(s.name),s.area_ha.toFixed(2),s.selected_models,s.land_use_coverage_pct.toFixed(2)+'%',s.model_membership_sensitivity.eroded_count+'–'+s.model_membership_sensitivity.buffered_count]);box.append(dataTable([localized({zh:'来源范围',en:'Source area',ja:'出典区域'}),'ha',localized({zh:'模型数',en:'Models',ja:'モデル数'}),localized({zh:'用地覆盖',en:'Land-use coverage',ja:'土地利用被覆'}),localized({zh:'边线敏感性',en:'Edge sensitivity',ja:'境界感度'})],rows));box.append(el('p',localized({zh:'敏感性范围：按配准记录的线宽与残差距离，分别内缩与外扩后重新选取模型；它不是置信区间。',en:'Sensitivity counts use the recorded registration/stroke distance to erode and buffer each outline. They are not confidence intervals.',ja:'感度の件数は記録した位置合わせ・線幅距離で区域を縮小・拡張して抽出する。信頼区間ではない。'}),'style-note'));box.append(link(localized({zh:'边界配准与控制点记录',en:'Boundary registration and control points',ja:'位置合わせ・制御点記録'}),'boundary-atlas/registration.json'),document.createTextNode(' · '),link(localized({zh:'重点区边线对照',en:'Primary edge comparison',ja:'重点区域の境界比較'}),'boundary-atlas/maps/00_primary_edge_comparison.png'));}
'''+js[oldend:]
    js=js.replace('let study=null,loadFailed=false;','let study=null,loadFailed=false,boundaryData=null;')
    js=js.replace('renderContext();renderEvidence();renderMaps();','renderContext();renderEvidence();renderMaps();if(boundaryData)renderBoundaries(boundaryData);')
    js+='\nfetch("boundary-atlas/atlas.json").then(r=>{if(!r.ok)throw Error("Boundary atlas "+r.status);return r.json();}).then(data=>{boundaryData=data;plates=data.plates;renderMaps();renderBoundaries(data);}).catch(e=>{$("#boundary-content").append(el("p",e.message));});\n'
    (dist/'portfolio.js').write_text(js)
    team=(dist/'team.js').read_text()
    team=re.sub(r'\nconst currentScopeCopy=.*?;for\(const l of Object.keys\(currentScopeCopy\)\)Object.assign\(copy\[l\],currentScopeCopy\[l\]\);\n','\n',team)
    teamcopy={
      'en':{'steps':[['Get current main','Use the GitHub main archive or clone the complete repository.'],['Open the current course project','Open Kanda_Nihonbashi_Course_2026-10-16.qgz. Use primary_brief, secondary_brief and poster_blue; census_legacy is the historical comparison.'],['Choose the matching area','Use course_membership and the scope column in the new CSV tables. Read source years and quality before analysis.'],['Save and return separate work','Keep project paths relative and coordinate one editor per shared GeoPackage.']],'rows':[['Current GIS','19 spatial layers + membership table','Three registered course outlines and the historical census reference'],['Building data','277 primary / 1,087 wider / 1,070 poster models','Representative-point selection; actual energy remains missing'],['Land and planning','Both-source land use and MLIT zones','Observed use and legal reference zones remain separate'],['Trees and parks','Inventory points, routes and polygons','Point absence is a source gap; full route counts are not local totals'],['Flood','Four source scenarios / three areas','Source dates and scales stay separate; no overlap does not establish safety'],['Weather','Tokyo 2025 hourly station','Background station; two wind hours missing'],['Historical CFD','2020 census ROI, 277 core objects','Original numerical fields and acceptance state retained']],'scope':'Current course totals come from the 2026-10-16 registered outlines. Earlier dated simulations and GIS retain their historical scope.'},
      'zh':{'steps':[['领取当前 main','使用 GitHub main 压缩包或克隆完整仓库。'],['打开当前课程工程','打开 Kanda_Nihonbashi_Course_2026-10-16.qgz。primary_brief、secondary_brief、poster_blue 是三条来源边线；census_legacy 是历史统计边界对照。'],['选取相应范围','使用 course_membership 和新 CSV 的 scope 列；先读来源年份与质量说明。'],['另存并交回成果','保持相对路径，每个共享 GeoPackage 协调一名编辑者。']],'rows':[['当前 GIS','19 个空间图层＋成员表','三条课程来源边线与历史统计边界'],['建筑数据','重点 277／外围 1,087／海报 1,070 个模型','代表点选取；真实用能仍缺失'],['用地与规划','两份源用地面与 MLIT 用途地域','现状利用与法定参考地域分别读取'],['树木与公园','单株、路线和范围记录','缺单株记录不等于无树；路线总数不是区内树数'],['洪水','四个源情景／三个范围','日期与规模分开；无相交不等于安全'],['气象','东京站 2025 逐小时','背景站；两个风小时缺失'],['历史 CFD','2020 统计边界／277 个核心对象','保留原数值场与验收状态']],'scope':'当前课程统计采用 2026-10-16 配准边线。此前日期版模拟与 GIS 保留历史口径。'},
      'ja':{'steps':[['現在の main を取得','GitHub main のアーカイブ又は完全なリポジトリを取得。'],['授業対象の現在のプロジェクトを開く','Kanda_Nihonbashi_Course_2026-10-16.qgz を開く。primary_brief、secondary_brief、poster_blue は出典境界、census_legacy は旧統計区域。'],['対応する区域を選ぶ','course_membership と新 CSV の scope 列を使い、出典年と品質を読む。'],['別名保存して返す','相対パスを保持し、共有 GeoPackage の編集者を一人にする。']],'rows':[['現在の GIS','19 空間レイヤー＋対応表','三つの出典境界と旧統計区域'],['建物データ','重点277／周辺1,087／ポスター1,070モデル','代表点抽出。実エネルギーは未取得'],['土地・計画','両出典の土地利用と MLIT 用途地域','現況と法定参考地域を区別'],['樹木・公園','単木・路線・範囲記録','単木記録の欠如は樹木なしを意味しない'],['洪水','四シナリオ／三区域','日付と規模を分記。交差なしは安全の証明ではない'],['気象','東京2025年毎時観測','背景観測所。風の二時間が欠測'],['旧 CFD','2020統計区域／277重点モデル','元の数値場と確認状態を保持']],'scope':'現在の授業対象集計は2026-10-16の位置合わせ境界を使う。旧日付版の計算とGISは旧対象区域を保持。'}}
    team=team.replace("let lang='en';",'\nconst currentScopeCopy='+json.dumps(teamcopy,ensure_ascii=False)+';for(const l of Object.keys(currentScopeCopy))Object.assign(copy[l],currentScopeCopy[l]);\n'+"let lang='en';")
    team=team.replace("'portfolio/Kajicho_Field_Atlas_2026-10-15.zip'",json.dumps(package)).replace("'context-study/Kajicho_Context_Study_2026-10-15_EN.zip'",json.dumps(package)).replace('2026-10-15','2026-10-16')
    (dist/'team.js').write_text(team)
    # Add current course outlines to historical simulation locator maps.
    dm=jread(dist/'data/domain-map.geojson');bound=atlas['boundaries']['features']
    for f in dm['features']:
        if f['properties'].get('role')=='design_area':f['properties'].update(name='Historical 2020 census ROI',boundary_status='Historical simulation footprint; course outlines are separate overlays')
    dm['features']=[f for f in dm['features'] if f['properties'].get('role') not in NAMES]
    for f in bound:
        sid=f['properties']['scope']
        if sid in NAMES:dm['features'].append({'type':'Feature','properties':{'role':sid,'name':NAMES[sid][1]},'geometry':f['geometry']})
    write(dist/'data/domain-map.geojson',dm)
    dj=(dist/'domain-map.js').read_text();marker="let language = 'zh'"
    dj=re.sub(r'const courseCopy=.*?;for\(const l of Object.keys\(courseCopy\)\)Object.assign\(copy\[l\],courseCopy\[l\]\);\n','',dj)
    copy={l:{'designLegend':v,'coreLabel':v,'note':n} for l,v,n in [('zh','历史模拟区 · 2020 统计边界','红色为历史模拟统计区；紫色为任务书重点区，棕色虚线为约略外围区，青色为海报线。计算域与建筑包络保持原试验范围。'),('en','Historical model / 2020 census','Red: historical simulation ROI. Purple: brief primary. Brown dashes: approximate wider area. Cyan: poster. Domain and building envelope retain the original trial scope.'),('ja','旧モデル・2020統計区域','赤：旧計算区域。紫：重点区域。茶破線：概略周辺。青：ポスター。計算領域と建物包絡は旧試行の範囲。')]}
    dj=dj.replace(marker,'const courseCopy='+json.dumps(copy,ensure_ascii=False)+';for(const l of Object.keys(courseCopy))Object.assign(copy[l],courseCopy[l]);\n'+marker)
    dj=dj.replace("['design_area', colors.design, null, 3, .18]","['design_area', colors.design, '2 3', 2, .03],\n    ['primary_brief','#59457f',null,3,.06],\n    ['secondary_brief','#a46d32','6 4',2,0],\n    ['poster_blue','#27abd1',null,2,0]")
    dj=dj.replace("design: L.geoJSON(feature(data, 'design_area')).getBounds()","design: L.geoJSON({type:'FeatureCollection',features:data.features.filter(f=>['primary_brief','secondary_brief','poster_blue'].includes(f.properties.role))}).getBounds()")
    dj=dj.replace('const designCenter = boundaries.design.getCenter();',"const designCenter = L.geoJSON(feature(data,'design_area')).getBounds().getCenter();")
    (dist/'domain-map.js').write_text(dj)
    # Historical numerical data keep their denominator; all entry pages display it.
    banner='''<aside class="course-scope-note" style="padding:14px 24px;background:#f7f5ef;color:#36353a;border-bottom:2px solid #59457f;font:14px sans-serif"><b>Course areas / 课程范围 / 授業対象区域 · 2026-10-16</b><p>Current maps and totals: <a href="index.html#course-boundaries">primary + wider course areas</a>. These retained simulations use the historical 2020 census ROI (10.79 ha; 277 model objects). 当前模拟沿用历史统计边界；课程边界与分区统计见总图。旧計算の対象は2020年統計区域で、更新した授業対象区域は総図に示す。</p></aside>'''
    for filename in ('team.html','studies.html','cfd.html','style-guide.html'):
        pp=dist/filename;t=pp.read_text();t=re.sub(r'<aside class="course-scope-note".*?</aside>','',t,flags=re.S);t=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+banner,t,count=1);pp.write_text(t)
    for pp in dist.rglob('*'):
        if pp.suffix in ('.html','.js'):
            text=pp.read_text().replace('https://drive.google.com/file/d/1zSJaSWM6WXMdMsgJQJG5Nd6M9kechosz/view?usp=drivesdk',package);pp.write_text(text)
    from consolidate_mapping import update_site
    update_site(a.team,a.site,atlas)
    # Update team-source snapshot verbatim, excluding nested Site Git metadata.
    mirror=a.team/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon'
    assert mirror.resolve()!=a.site.resolve(),'Use a separate opened Site checkout for assembly.'
    if (mirror/'dist').exists():shutil.rmtree(mirror/'dist')
    shutil.copytree(a.site,mirror,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','node_modules','.sites-runtime'))
    print(json.dumps({'status':'assembled','maps':len(atlas['plates']),'scopes':list(stats),'charts':len(ctx['charts']),'stale_site_zip_files':len(list(dist.glob('*/*.zip')))}))

if __name__=='__main__':main()
