#!/usr/bin/env python3
"""Assemble derived context readings, PNG plates and source tables for the Site.

Original source PDFs and execution receipts stay in the local research workspace.
This command does not run a model or modify source GIS data.
"""
import json, shutil, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / '06_Outputs/Context_Study_2026-10-15'
SITE = ROOT / '06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/context-study'

def read(path):
    return json.loads(path.read_text())

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def tr(zh, en, ja):
    return dict(zh=zh, en=en, ja=ja)

def format_chart(chart, sources):
    c = dict(chart)
    rows = c['rows']
    category = tr('类别', 'Category', '区分')
    count = tr('模型数', 'Models', 'モデル数')
    pct = lambda n: f'{n:.2f}%'
    area = lambda n: f'{n:,.0f}'
    if c['id'].startswith('01'):
        r = rows[0]
        c['headers'] = [tr('统计项', 'Measure', '項目'), tr('数值', 'Value', '値')]
        c['rows'] = [
            [tr('核心总面积 / ha','Core area / ha','対象総面積 / ha'), f"{r['boundary_area_ha']:.2f}"],
            [tr('建筑投影并集 / m²','Union building projection / m²','建物投影の和集合 / m²'),area(r['union_building_projection_m2'])],
            [tr('总体投影覆盖率','Gross footprint coverage','総面積の投影被覆率'),pct(r['gross_coverage_pct'])],
            [tr('核心模型密度 / 个·ha⁻¹','Core model density / objects·ha⁻¹','中心部モデル密度 / 件·ha⁻¹'),f"{r['objects_per_gross_ha']:.2f}"],
            [tr('代表点入区的模型数','Models selected by representative point','代表点が区域内にあるモデル'),r['core_id_objects']],
            [tr('投影有面积相交的模型数','Models with positive area overlap','投影が面積で交わるモデル'),r['any_overlap_objects']]]
    elif c['id'].startswith('02'):
        c['headers'] = [category, count, tr('数量占比','Count share','件数比'),tr('楼面代理占比','Floor proxy share','延べ面積代理比')]
        c['rows'] = [[tr(r['label_zh'],r['label_en'],r['source_use']),r['objects'],pct(r['object_share_pct']),pct(r['floor_proxy_share_pct'])] for r in rows]
    elif c['id'].startswith('03'):
        ja = ['商業','道路','交通施設','公益施設','住宅・住商混合','平面駐車場','低未利用地','その他屋外利用']
        c['headers'] = [category,tr('面积 / m²','Area / m²','面積 / m²'),tr('核心区占比','Core share','対象面積比')]
        c['rows'] = [[tr(r['label_zh'],r['label_en'],ja[i]),area(r['area_m2']),pct(r['core_share_pct'])] for i,r in enumerate(rows)]
    elif c['id'].startswith('04'):
        c['headers'] = [tr('高度组','Height class','高さ区分'), count]
        c['rows'] = [[tr('代理高度','Proxy height','推定高さ') if r['bin']=='Proxy height' else r['bin'],r['count']] for r in rows]
    elif c['id'].startswith('05'):
        c['headers'] = [tr('来源与情景','Source and scenario','出典とシナリオ'),tr('核心浸水面积 / m²','Flooded core / m²','対象内浸水面積 / m²'),tr('相交模型','Intersecting models','相交モデル')]
        c['rows'] = [[tr(r['title_zh'],r['title_en']+' / '+r['source_date'][:4],r['source_name']+' / '+r['source_date'][:4]+' / '+r['scale']),area(r['core_flood_area_m2']),r['exposed_core_objects']] for r in rows]
    elif c['id'].startswith('06'):
        c['headers'] = [tr('月','Month','月'),tr('均温 / °C','Mean / °C','平均 / °C'),tr('≥30°C小时','Hours ≥30°C','≥30°C時間'),tr('≥35°C小时','Hours ≥35°C','≥35°C時間')]
        c['rows'] = [[r['month'],f"{r['temperature_mean_c']:.1f}",r['hours_ge30'],r['hours_ge35']] for r in rows]
    else:
        c['headers'] = [tr('地区','Town','町丁目'),tr('倒塌 / 棟·ha⁻¹','Collapse / buildings·ha⁻¹','倒壊 / 棟·ha⁻¹'),tr('火灾 / 棟·ha⁻¹','Fire / buildings·ha⁻¹','火災 / 棟·ha⁻¹')]
        c['rows'] = [[tr(f'鍛冶町{i}丁目',f'Kajicho {i}',f'鍛冶町{i}丁目'),r['建物倒壊危険度危険量（棟/ha）'],r['火災危険度危険量（棟/ha）']] for i,r in enumerate(rows,1)]
    source_ids = {
        '01':['P0_PLATEAU_BUILDINGS_2025'], '02':['P0_PLATEAU_BUILDINGS_2025'],
        '03':['P0_PLATEAU_LANDUSE'], '04':['P0_PLATEAU_BUILDINGS_2025']}
    chosen = [s for s in sources if s.get('dataset_id') in source_ids.get(c['id'][:2], [])]
    if not chosen:
        word = {'05':'flood','06':'weather','07':'earthquake'}[c['id'][:2]]
        chosen = [s for s in sources if word in (s.get('dataset_id','')+' '+s.get('name','')).lower()]
    c['sources'] = [{'document_title':s.get('name'), 'url':s.get('source_url'),
                     'year':s.get('data_year'), 'page':f"Download: {s.get('download_date','2026-10-15')}"} for s in chosen]
    design = {
      '01': tr('道路、铁路也计入核心总面积。应继续区分可进入的公共空间、私有空地和交通空间，再选择休息与绿化位置。','Roads and rail are part of the denominator. Distinguish accessible public space, private gaps and transport land before choosing places to rest or plant.','分母には道路・鉄道も含む。公共的に使える場所、私有空地、交通空間を分け、休憩・緑化の位置を選ぶ。'),
      '02': tr('办公楼面占比较高，为优先核查办公用能提供了数量依据；首层商业和生活服务仍需按营业时段另做观察。','The large office floor share supports prioritising office energy records. Ground-floor retail and local services still need observation by opening hours.','業務用途の延べ面積比から、オフィスのエネルギー記録を優先して調べる。低層商業・生活サービスは営業時間別に観察する。'),
      '03': tr('道路与交通设施占地过半，场地机会很大程度在街道边缘、站口和高架周边。是否能改善这些位置，取决于管理权限、通行与装卸条件。','Roads and transport occupy over half the core. Many opportunities lie at street edges, station exits and the viaduct, subject to management rights, movement and deliveries.','道路・交通施設が半分以上を占める。街路端、駅出口、高架周辺が重要で、管理権限、通行、荷捌き条件を確認する。'),
      '04': tr('高度差为遮阴与屋顶利用分析提供条件。后续需把高度与街宽、朝向、退台和实际使用时间一起读，才能判断哪个街段需要补阴。','Height differences help frame shade and roof studies. Combine height with street width, orientation, setbacks and use times to identify streets needing more shade.','高さの違いを、街路幅員、方位、セットバック、利用時刻と合わせ、日陰を補う街路を考える。'),
      '05': tr('把相交建筑和街段作为入口、地下坡道及配电设备的调查清单，核查门槛、挡水和向上避难路径；官方深度类别本身不包含这些建筑细节。','Use the intersecting buildings and streets to target surveys of entrances, basement ramps and electrical equipment. Check thresholds, barriers and routes to upper floors.','相交する建物・街路から入口、地下スロープ、電気設備を調査し、敷居、防水、上階への避難動線を確認する。'),
      '06': tr('观测说明暑热调查不能只选一个舒适时段。应覆盖午间和下午的高温时段，记录遮阴、停留者和可进入的避暑点，并用当地测量补充背景站。','Include hot midday and afternoon periods in fieldwork. Record shade, people staying and accessible cooling places, with local measurements alongside the background station.','昼・午後の暑い時間帯を調査し、日陰、滞在、利用可能な涼み場所を記録する。背景観測点に現地測定を補う。'),
      '07': tr('两丁目倒塌等级相同而火灾等级不同，应同时记录老旧楼更新条件、外墙与招牌、狭窄道路和消防通行，不能只按综合等级安排调查。','The town units share a collapse rank but differ in fire rank. Survey building renewal needs, façades, signs, narrow streets and fire-service access alongside the overall rank.','倒壊ランクは同じでも火災ランクは異なる。建物更新、外壁・看板、狭い道路、消防活動の通行を併せて調査する。')}
    c['design_meaning'] = design[c['id'][:2]]
    return c

def build():
    plans = read(STUDY / 'research/Brief_Plans_Deep.json')
    rules = read(STUDY / 'research/Local_Rules_Deep.json')
    analysis = read(STUDY / 'analysis/Context_Evidence.json')
    topics = [dict(t, group='plans') for t in plans['topics']]
    topics += [dict(t, group='rules') for t in rules['topics']]
    brief_url = plans['topics'][0]['evidence'][0]['url']
    checklist = plans.get('brief_checklist') or [
        {'requirement': r['label'], 'response': r['completion_evidence'],
         'evidence': [{'document_title': '2026 Theme B brief', 'url': brief_url,
                       'year': 2026, 'page': r['page']}]}
        for r in plans['course_checklist']]
    charts = []
    for chart in analysis.get('charts', []):
        c = format_chart(chart, analysis['sources'])
        for key in ('file', 'preview'):
            if c.get(key):
                p = Path(c[key])
                if 'figures' in p.parts:
                    c[key] = 'context-study/' + '/'.join(p.parts[p.parts.index('figures'):])
        charts.append(c)
    metrics = analysis['metrics'] if isinstance(analysis['metrics'], list) else []
    if metrics:
        metrics[0]['value'] = round(metrics[0]['value'], 2)
        for m in metrics:
            if m['unit'] == 'objects': m['unit'] = ''
    seismic = {'rows': [], 'sources': [{'document_title': '東京都 第9回地域危険度測定',
               'url': rules['seismic_risk']['source_page'], 'year': 2022}]}
    for i, r in enumerate(rules['seismic_risk']['rows'], 1):
        seismic['rows'].append({
            'name': {'zh': f'鍛冶町{i}丁目', 'en': f'Kajicho {i}', 'ja': f'鍛冶町{i}丁目'},
            'collapse': r['建物倒壊危険度危険量（棟/ha）'],
            'collapse_rank': r['建物倒壊危険度ランク'],
            'fire': r['火災危険度危険量（棟/ha）'],
            'fire_rank': r['火災危険度ランク'],
            'overall_rank': r['総合危険度ランク']})
    data = {'schema_version': 1, 'date': '2026-10-15', 'brief_checklist': checklist,
            'course_schedule': plans['course_schedule'],
            'topics': topics, 'metrics': metrics, 'charts': charts, 'seismic': seismic,
            'no_new_cfd': True, 'map_export_formats': ['PNG']}
    write(SITE / 'context.json', data)
    for directory in ('figures',):
        shutil.copytree(STUDY / directory, SITE / directory, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('._*', '*.svg'))
    for p in (STUDY / 'analysis').glob('*.csv'):
        if p.name.startswith('._'): continue
        (SITE / 'analysis').mkdir(exist_ok=True)
        shutil.copy2(p, SITE / 'analysis' / p.name)
    public_analysis = {k: v for k, v in analysis.items() if k not in ('runtime', 'inputs')}
    write(SITE / 'analysis/Context_Evidence.json', public_analysis)
    for name in ('Brief_Plans_Deep', 'Local_Rules_Deep'):
        for ext in ('json', 'md'):
            p = STUDY / 'research' / f'{name}.{ext}'
            if p.exists():
                (SITE / 'research').mkdir(exist_ok=True)
                shutil.copy2(p, SITE / 'research' / p.name)
    for name in ('README.md', 'analysis/Analysis.md'):
        if (STUDY / name).exists():
            shutil.copy2(STUDY / name, SITE / name)
    out = SITE / 'Kajicho_Context_Study_2026-10-15_EN.zip'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SITE.rglob('*')):
            if not p.is_file() or p.suffix == '.zip' or p.name.startswith('._'): continue
            z.write(p, 'Kajicho_Context_Study_2026-10-15/' + str(p.relative_to(SITE)))
        for name in ('build_context_evidence.py', 'assemble_context_study.py'):
            z.write(ROOT / '08_Scripts' / name, 'Kajicho_Context_Study_2026-10-15/scripts/' + name)
    print(json.dumps({'topics': len(topics), 'requirements': len(checklist),
                      'charts': len(charts), 'metrics': len(metrics), 'zip_bytes': out.stat().st_size}))

if __name__ == '__main__':
    build()
