#!/usr/bin/env python3
"""Keep one shared-extent map per theme; run beside build_boundary_atlas.py."""
import argparse, concurrent.futures, json, re, shutil
from pathlib import Path


def patch_renderer(path):
    s = path.read_text()
    if "'scope_metrics':scope_metrics" in s:return
    start = s.index("    sid,theme=task;overview=")
    end = s.index("    x0,y0,x1,y1=scope.bounds", start)
    s = s[:start] + "    sid,theme=task;overview=sid=='overview';scope=unary_union([boundaries[k][1] for k in SCOPE_NAMES]);pad=100\n" + s[end:]
    start = s.index("    y=.82\n")
    end = s.index("    boundary_handles=", start)
    s = s[:start] + '''    y=.82
    fig.text(.79,y,'AREA / MODELS',fontsize=11,weight='bold');y-=.035
    scope_metrics=[]
    for key,label in [('primary_brief','Kajicho primary'),('secondary_brief','Brief wider (approx.)'),('poster_blue','Poster blue')]:
        sm=summaries[key]
        text=f"{label}  {sm['area_ha']:.2f} ha / {sm['selected_models']:,}"
        fig.text(.79,y,text,fontsize=9.5);y-=.027
        if idx==0:metric_label='Footprint union';value=sm['gross_footprint_coverage_pct'];unit='%';detail=f'{value:.2f}% footprint union'
        elif idx==1:metric_label='Mapped road length';value=sm['road_mapped_length_m']/1000;unit='km';detail=f'{value:.2f} km mapped roads'
        elif idx==2:metric_label='Known building use';value=sm['known_use_models'];unit='models';detail=f"{value:,} known use / {sm['unknown_use_models']:,} unknown"
        elif idx==3:metric_label='Source height median';value=sm['source_height_median_m'];unit='m';detail=f"{value:.1f} m source median / {sm['height_proxy_models']:,} proxies" if value is not None else f"No source height / {sm['height_proxy_models']:,} proxies"
        elif idx==4:metric_label='Land-use coverage';value=sm['land_use_coverage_pct'];unit='%';detail=f'{value:.2f}% land-use coverage'
        elif idx==5:
            value=unary_union([g.intersection(boundaries[key][1]) for r,g in raw.get('zones',[]) if g.intersects(boundaries[key][1])]).area/sm['area_m2']*100
            metric_label='Zone source coverage';unit='%';detail=f'{value:.2f}% zone source coverage'
        elif idx==6:metric_label='Tree point records';value=sm['tree_point_records'];unit='records';detail=f"{value:,} tree points / {sm['park_inventory_union_m2']/10000:.2f} ha parks"
        else:
            f=next(f for f in sm['flood'] if f['source_date']=='2018-03-30' and '神田' in f['scenario'])
            metric_label='Kanda 2018 L2 overlap';value=f['scope_overlap_pct'];unit='%';detail=f"{value:.2f}% overlap / {f['exposed_selected_models']:,} models"
        fig.text(.79,y,detail,fontsize=8.5,color='#6c6761');y-=.046
        scope_metrics.append({'scope':key,'area_ha':sm['area_ha'],'selected_models':sm['selected_models'],'metric':metric_label,'value':value,'unit':unit,'printed_text':text+'; '+detail})
    y-=.01
''' + s[end:]
    s = s.replace("filename=('00_course_overview' if theme==0 else '00_primary_edge_comparison') if overview else sid+'_'+THEMES[theme][0]", "filename='course_00_overview' if overview else 'course_'+THEMES[theme][0]")
    start = s.index("    return {'id':filename,'scope':sid")
    end = s.index("\n\ndef build_qgis", start)
    s = s[:start] + '''    return {'id':filename,'scope':'common_view','kind':'overview' if overview else 'theme','theme':None if overview else THEMES[theme][0],'title':{'en':title,'zh':subtitle,'ja':title},'file':'boundary-atlas/maps/'+file.name,'preview':'boundary-atlas/maps/previews/'+preview.name,'pixels':[3200,2400],'extent_6677':list(extent.bounds),'scope_metrics':scope_metrics}
''' + s[end:]
    s = s.replace("tasks=[('overview',0),('overview',1)]+[(s,i) for s in SCOPE_NAMES for i in range(len(THEMES))]", "tasks=[('overview',0)]+[('common_view',i) for i in range(len(THEMES))]")
    s = s.replace('16 OCT 2026', '17 OCT 2026')
    s = s.replace("label=name.replace('駅','')+", "label={'神田駅':'Kanda','新日本橋駅':'Shin-Nihonbashi','三越前駅':'Mitsukoshimae','小伝馬町駅':'Kodemmacho','淡路町駅':'Awajicho','岩本町駅':'Iwamotocho'}.get(name,name.replace('駅',''))+")
    path.write_text(s)


_DATA = None
def run_task(task):
    from build_boundary_atlas import render
    return render(task, *_DATA)


def update_site(team, site, atlas):
    dist=site/'dist'
    old=dist/'boundary-atlas'
    shutil.rmtree(old)
    shutil.copytree(team/'06_Outputs/Boundary_Atlas_2026-10-16',old)
    readme=old/'README.md'
    readme.write_text(readme.read_text().replace('../../05_QGIS/','https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho/blob/main/05_QGIS/').replace('../../04_Data/','https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho/blob/main/04_Data/'))
    ctxp=dist/'context-study/context.json';ctx=json.loads(ctxp.read_text())
    targets=['course_00_overview','course_03_building_use','course_05_land_use','course_04_building_height','course_08_flood']
    for c,name in zip(ctx['charts'][:5],targets):
        c['file']='boundary-atlas/maps/'+name+'.png';c['preview']='boundary-atlas/maps/previews/'+name+'.jpg'
        c['design_meaning']={'en':'Use the shared course view to choose field checks; read each total with its named source area.','zh':'在统一课程视图中选择现场核查位置，按各来源范围读取统计。','ja':'共通の授業対象図から現地確認箇所を選び、各集計を出典区域別に読む。'}
    ctx['mapping_view']='one common extent per theme';ctx['presentation_updated']='2026-10-17'
    ctxp.write_text(json.dumps(ctx,ensure_ascii=False,indent=2)+'\n')
    # Remove stale served maps and duplicate aliases, including their source metadata.
    for folder in [dist/'portfolio/maps',dist/'portfolio/mapping_data']:
        if folder.exists():shutil.rmtree(folder)
    for folder in [dist/'context-study/figures',dist/'context-study/figures/previews']:
        for file in folder.glob('*'):
            if file.is_file() and file.name[:2] in ('01','02','03','04','05'):file.unlink()
    js=(dist/'portfolio.js').read_text()
    js=re.sub(r"\nconst boundaryCopy=.*?;for\(const l of Object.keys\(boundaryCopy\)\)Object.assign\(lex\[l\],boundaryCopy\[l\]\);\n",'\n',js)
    copy={
        'en':{'mappingTitle':'One view, eight themes','mappingIntro':'Each theme uses the same full-course view. Primary, approximate wider and poster outlines appear together; totals are labelled by source area.','atlasPackageNote':'8 thematic PNG maps + overview · portable QGIS','footer':'Shared course view · 2026.10.17','edition':'Urban Design Studio 2026 · Theme B · 2026.10.17'},
        'zh':{'mappingTitle':'同一视角，八类专题','mappingIntro':'每个专题只保留一张全区视图，同时标明重点区、约略外围区和海报边线；统计注明来源范围。','atlasPackageNote':'8 张专题 PNG＋总图 · 便携 QGIS','footer':'统一课程视图 · 2026.10.17','edition':'Urban Design Studio 2026 · Theme B · 2026.10.17'},
        'ja':{'mappingTitle':'同じ視点、八つの主題','mappingIntro':'各主題は共通の全体図一枚。重点区域、概略周辺区域、ポスター境界を同時に示し、集計には出典区域を記す。','atlasPackageNote':'主題図8枚＋全体図 · PNG · 可搬QGIS','footer':'共通授業対象図 · 2026.10.17','edition':'Urban Design Studio 2026 · Theme B · 2026.10.17'}}
    # Keep other current copy, eliminating outdated literals instead of appending overrides.
    original=(site/'dist/portfolio.js').read_text()
    bc=json.loads(re.search(r'const boundaryCopy=(.*?);for\(const l',original).group(1))
    for lang,values in copy.items():bc[lang].update(values)
    js=js.replace("let lang='en';",'const boundaryCopy='+json.dumps(bc,ensure_ascii=False)+';for(const l of Object.keys(boundaryCopy))Object.assign(lex[l],boundaryCopy[l]);\n'+"let lang='en';",1)
    js=js.replace('plates.forEach((p,i)=>','plates.filter(p=>p.kind===\'theme\').forEach((p,i)=>')
    # The overview belongs with the scope table and hero, not in the theme gallery.
    js=re.sub(r"box.append\(link\(localized\(\{zh:'边界配准与控制点记录'.*?\);\}","box.append(link(localized({zh:'边界配准与控制点记录',en:'Boundary registration and control points',ja:'位置合わせ・制御点記録'}),'boundary-atlas/registration.json'));}",js)
    js=re.sub(r'(?:if\(boundaryData\)renderBoundaries\(boundaryData\);)+','if(boundaryData)renderBoundaries(boundaryData);',js)
    js=js.replace("img.decoding='async';f.append(img);", "img.decoding='async';if(url.startsWith('boundary-atlas/maps/')){img.width=3200;img.height=2400;}f.append(img);")
    js=js.replace('renderMaps();renderBoundaries(data);}).catch',"renderMaps();renderBoundaries(data);if(location.hash)requestAnimationFrame(()=>document.getElementById(location.hash.slice(1))?.scrollIntoView({behavior:'instant'}));}).catch")
    (dist/'portfolio.js').write_text(js)
    for path in dist.rglob('*'):
        if path.suffix not in ('.html','.js'):continue
        s=re.sub(r"(['\"])kajicho-lang\1",lambda m:m.group(1)+'kajicho-language-20261017'+m.group(1),path.read_text())
        s=s.replace("let language = 'zh'", "let language = 'en'")
        s=s.replace('portfolio/mapping_data/map_manifest.json','boundary-atlas/source_manifest.json')
        s=s.replace('portfolio/maps/03_building_use.png','boundary-atlas/maps/course_03_building_use.png').replace('portfolio/maps/previews/03_building_use.jpg','boundary-atlas/maps/previews/course_03_building_use.jpg')
        s=s.replace('boundary-atlas/maps/previews/00_course_overview.jpg','boundary-atlas/maps/previews/course_00_overview.jpg')
        if path.name=='index.html':
            for key,value in bc['en'].items():
                s=re.sub(r'(<([a-z0-9]+)\b[^>]*data-t="'+re.escape(key)+r'"[^>]*>)[^<]*(</\2>)',lambda m:m.group(1)+value+m.group(3),s)
        # Fingerprinted top-level scripts/styles keep each publication internally consistent.
        if path.suffix=='.html':
            s=re.sub(r'((?:src|href)="(?:portfolio|team|app|cfd|domain-map|styles)[^"/?]*\.(?:js|css))(?:\?[^\"]*)?"',r'\1?v=20261017-common"',s)
            s=re.sub(r'(<button[^>]*data-lang="zh"[^>]*>.*?</button>)(<button[^>]*data-lang="en"[^>]*>.*?</button>)',r'\2\1',s)
        path.write_text(s)
    # Rewrite old map paths in the maintained assembler so a later run preserves this layout.
    assembler=team/'08_Scripts/assemble_boundary_site.py'
    code=assembler.read_text()
    if 'from consolidate_mapping import update_site' not in code:
        marker='    # Update team-source snapshot verbatim, excluding nested Site Git metadata.'
        code=code.replace(marker,'    from consolidate_mapping import update_site\n    update_site(a.team,a.site,atlas)\n'+marker)
        # Old alias generation is superseded by update_site; skip obsolete image copies.
        start=code.index('    # Keep the old asset URLs useful')
        end=code.index('    # Remove obsolete downloadable bundles',start)
        code=code[:start]+code[end:]
        start=code.index('    for c in charts[:5]:')
        end=code.index('    # Remove obsolete downloadable bundles',start)
        code=code[:start]+code[end:]
        for oldname,newname in zip(['00_course_overview','primary_brief_03_building_use','secondary_brief_05_land_use','primary_brief_04_building_height','secondary_brief_08_flood'],targets):code=code.replace(oldname,newname)
        assembler.write_text(code)
    mirror=team/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist'
    if mirror.exists():shutil.rmtree(mirror)
    shutil.copytree(dist,mirror)


def main():
    p=argparse.ArgumentParser();p.add_argument('--team',type=Path,required=True);p.add_argument('--site',type=Path,required=True);p.add_argument('--task-root',type=Path,required=True);p.add_argument('--workers',type=int,default=9);a=p.parse_args()
    if (a.site/'dist/study-atlas').exists():
        p.error('Current study-area release is active. Use assemble_study_site.py --task-root <task-root>; this dated assembler cannot overwrite current maps.')
    patch_renderer(a.team/'08_Scripts/build_boundary_atlas.py')
    import build_boundary_atlas as b
    out=a.team/'06_Outputs/Boundary_Atlas_2026-10-16';atlas=json.loads((out/'atlas.json').read_text());stats=json.loads((out/'statistics.json').read_text())['scopes']
    raw=b.read(a.task_root/'assets/assets.gpkg');_,boundaries=b.source_boundaries(a.task_root/'registration/course_boundaries_6677.geojson')
    temp=a.task_root/'Mapping_Common_2026-10-17';temp.mkdir(exist_ok=True)
    global _DATA
    _DATA=(raw,boundaries,stats,temp)
    tasks=[('overview',0)]+[('common_view',i) for i in range(len(b.THEMES))]
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:plates=list(pool.map(run_task,tasks))
    shutil.rmtree(out/'maps');shutil.move(str(temp/'maps'),str(out/'maps'))
    atlas.update(schema_version=3,plates=plates,mapping_presentation='one shared extent per theme',presentation_date='2026-10-17')
    (out/'atlas.json').write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+'\n')
    update_site(a.team,a.site,atlas)
    print(json.dumps({'plates':len(plates),'themes':8,'extent':plates[0]['extent_6677'],'legacy_served_maps':'removed','first_open_language':'en'}))


if __name__=='__main__':main()
