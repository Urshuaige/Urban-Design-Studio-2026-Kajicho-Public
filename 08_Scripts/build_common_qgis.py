#!/usr/bin/env python3
"""Build a portable QGIS project and PNG maps from the acquired public data.

PROJ_LIB=/Applications/QGIS.app/Contents/Resources/proj QT_QPA_PLATFORM=offscreen \
/Applications/QGIS.app/Contents/MacOS/bin/python3 08_Scripts/build_common_qgis.py
"""
import csv
import json
import math
import os
import re
from pathlib import Path
from zipfile import ZipFile
from qgis.core import *
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor, QFont

ROOT=Path(__file__).resolve().parents[1]
GPKG=ROOT/'04_Data/Ready/Kanda_Nihonbashi_Common_Foundation.gpkg'
PROJECT=ROOT/'05_QGIS/Projects/Kanda_Nihonbashi_Common_Foundation_2026-10-13.qgz'
MAPS=ROOT/'06_Outputs/Maps/Common_Foundation'
STYLES=ROOT/'05_QGIS/Styles/Common_Foundation'
LAYOUTS=ROOT/'05_QGIS/Layouts/Common_Foundation'
for p in [GPKG.parent,PROJECT.parent,MAPS,STYLES,LAYOUTS]:p.mkdir(parents=True,exist_ok=True)
app=QgsApplication([],False);app.initQgis()
project=QgsProject();crs=QgsCoordinateReferenceSystem('EPSG:6677');project.setCrs(crs)
project.setTitle('Kanda–Nihonbashi | Common Foundation（小组共用基础包）')
project.setFilePathStorage(Qgis.FilePathType.Relative)
project.setFileName(str(PROJECT))
context=project.transformContext()
statistics={}


def memory(name,geom,fields):
    l=QgsVectorLayer(geom+'?crs=EPSG:6677',name,'memory')
    l.dataProvider().addAttributes([QgsField(n,t) for n,t in fields]);l.updateFields();return l


def feature(layer,geom,values):
    f=QgsFeature(layer.fields());f.setGeometry(geom)
    f.setAttributes(values);return f


def save(layer,key):
    options=QgsVectorFileWriter.SaveVectorOptions();options.driverName='GPKG';options.layerName=key
    options.fileEncoding='UTF-8';options.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteLayer if GPKG.exists() else QgsVectorFileWriter.CreateOrOverwriteFile
    result=QgsVectorFileWriter.writeAsVectorFormatV3(layer,str(GPKG),context,options)
    if result[0]!=QgsVectorFileWriter.NoError:raise RuntimeError(result)
    return layer


def value(v):
    return None if QgsVariantUtils.isNull(v) else v


def number(x):
    if x is None:return None
    try:return float(x)
    except (TypeError,ValueError):return None


census=memory('Census 2020（人口与边界）','MultiPolygon',[
    ('ward_code',QVariant.String),('town_code',QVariant.String),('town_name',QVariant.String),
    ('population_2020',QVariant.Int),('households_2020',QVariant.Int),('repeat_flag',QVariant.String),
    ('hcode',QVariant.Int),('area_m2',QVariant.Double),('population_per_ha',QVariant.Double),('data_year',QVariant.Int)])
ward_geometries={};core_parts=[];core_pop=0;core_households=0;source_crs=[]
raw_census=[]
for ward in ['Chiyoda','Chuo']:
    path=next(p for p in (ROOT/'04_Data/Working/Census_2020'/ward).glob('*.shp') if not p.name.startswith('._'))
    source=QgsVectorLayer(str(path),ward,'ogr');source_crs.append(source.crs().authid())
    transform=QgsCoordinateTransform(source.crs(),crs,project)
    fs=[]
    for f in source.getFeatures():
        geom=QgsGeometry(f.geometry());geom.transform(transform)
        if not geom.isGeosValid():geom=geom.makeValid()
        code=str(f['KEY_CODE']);wardcode=str(f['PREF'])+str(f['CITY']);name=str(f['S_NAME'])
        pop=int(f['JINKO']);house=int(f['SETAI']);flag=value(f['KIGO_E']);area=geom.area()
        density=None
        fs.append(feature(census,geom,[wardcode,code,name,pop,house,flag,int(f['HCODE']),area,density,2020]))
        ward_geometries.setdefault(wardcode,[]).append(geom)
        raw_census.append({'ward_code':wardcode,'town_code':code,'town_name':name,'population_2020':pop,'households_2020':house,'repeat_flag':flag,'hcode':int(f['HCODE'])})
        if code in ['13101035001','13101035002']:
            core_parts.append(geom);core_pop+=pop;core_households+=house
    census.dataProvider().addFeatures(fs)
town_totals={}
for f in census.getFeatures():
    v=town_totals.setdefault(f['town_code'],[0,0]);v[0]+=f['population_2020'];v[1]+=f['area_m2']
density_idx=census.fields().indexFromName('population_per_ha')
census.dataProvider().changeAttributeValues({f.id():{density_idx:town_totals[f['town_code']][0]*10000/town_totals[f['town_code']][1]} for f in census.getFeatures() if town_totals[f['town_code']][1]>0})
assert len(core_parts)==2
core=QgsGeometry.unaryUnion(core_parts)
primary=memory('Kajicho 1 & 2（重点区）','MultiPolygon',[
    ('name',QVariant.String),('population_2020',QVariant.Int),('households_2020',QVariant.Int),
    ('area_m2',QVariant.Double),('boundary_status',QVariant.String)])
primary.dataProvider().addFeatures([feature(primary,core,['Kajicho 1 & 2',core_pop,core_households,core.area(),'2020 census town boundaries; course outline to confirm'])])

to_project=QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),crs,project)
rect4326=QgsRectangle(139.763,35.682,139.787,35.698)
context_geom=QgsGeometry.fromRect(rect4326);context_geom.transform(to_project)
download_extent=memory('Download extent（数据下载范围）','Polygon',[('purpose',QVariant.String)])
download_extent.dataProvider().addFeatures([feature(download_extent,context_geom,['Technical extent for the demo; secondary course boundary pending'])])

common=[('osm_id',QVariant.String),('name',QVariant.String),('tag',QVariant.String)]
buildings=memory('Buildings（建筑）','Polygon',common+[
    ('levels',QVariant.Double),('height_m',QVariant.Double),('footprint_m2',QVariant.Double),
    ('intersects_primary',QVariant.Int),('area_in_primary_m2',QVariant.Double),
    ('levels_status',QVariant.String),('energy_status',QVariant.String),
    ('electricity_kwh',QVariant.Double),('annual_electricity_co2_t',QVariant.Double)])
roads=memory('Roads & paths（道路与步道）','LineString',common+[('length_m',QVariant.Double)])
rail=memory('Rail（轨道）','LineString',common)
greens=memory('Mapped green space（已标注绿地）','Polygon',common)
water=memory('Water（河道）','Polygon',common)
water_lines=memory('Waterways（河道中心线）','LineString',common)
stations=memory('Stations（车站）','Point',common)
target_layers={'buildings':buildings,'roads':roads,'rail':rail,'greens':greens,'water':water,'water_lines':water_lines,'stations':stations}
pending={k:[] for k in target_layers};skipped_relations=0;invalid_polygons=0
osm=json.loads((ROOT/'04_Data/Raw/OSM_2026-10-13/Kanda_Nihonbashi_OSM.json').read_text())


def geometry(element,polygon=False):
    global invalid_polygons
    pts=[QgsPointXY(p['lon'],p['lat']) for p in element.get('geometry',[]) if 'lon' in p and 'lat' in p]
    if polygon:
        if len(pts)<4 or pts[0]!=pts[-1]:return None
        geom=QgsGeometry.fromPolygonXY([pts])
        if not geom.isGeosValid():
            invalid_polygons+=1;geom=geom.makeValid()
        if geom.isMultipart():
            parts=geom.asMultiPolygon()
            if len(parts)==1:geom=QgsGeometry.fromPolygonXY(parts[0])
            else:return None
    else:
        if len(pts)<2:return None
        geom=QgsGeometry.fromPolylineXY(pts)
    geom.transform(to_project);return geom


for element in osm['elements']:
    tags=element.get('tags',{});oid=element['type']+'/'+str(element['id']);name=tags.get('name:en') or tags.get('name','')
    if element['type']=='relation':skipped_relations+=1
    if element['type']=='way' and tags.get('building') and tags['building']!='no':
        geom=geometry(element,True)
        if geom and not geom.isEmpty():
            levels=number(tags.get('building:levels'));height=number(tags.get('height','').replace(' m',''))
            inside=int(geom.intersects(core));area_inside=geom.intersection(core).area() if inside else 0
            pending['buildings'].append(feature(buildings,geom,[oid,name,tags['building'],levels,height,geom.area(),inside,area_inside,'Known' if levels is not None else 'Missing','Missing',None,None]))
    for key,tag in [('roads','highway'),('rail','railway'),('water_lines','waterway')]:
        if element['type']=='way' and tags.get(tag):
            geom=geometry(element)
            if geom:
                vals=[oid,name,tags[tag]]+([geom.length()] if key=='roads' else [])
                pending[key].append(feature(target_layers[key],geom,vals))
    for key,allowed in [('greens',tags.get('leisure') in ['park','garden','playground']),('water',tags.get('natural')=='water')]:
        if element['type']=='way' and allowed:
            geom=geometry(element,True)
            if geom:pending[key].append(feature(target_layers[key],geom,[oid,name,tags.get('leisure') or tags.get('natural','')]))
    if tags.get('railway')=='station':
        if element['type']=='node':pt=QgsPointXY(element['lon'],element['lat'])
        elif element.get('bounds'):
            b=element['bounds'];pt=QgsPointXY((b['minlon']+b['maxlon'])/2,(b['minlat']+b['maxlat'])/2)
        else:continue
        geom=QgsGeometry.fromPointXY(pt);geom.transform(to_project)
        pending['stations'].append(feature(stations,geom,[oid,name,tags['railway']]))
for k,l in target_layers.items():l.dataProvider().addFeatures(pending[k])

carbon=list(csv.DictReader((ROOT/'04_Data/Ready/Carbon/Ward_CO2_2023_Published.csv').open(encoding='utf-8-sig')))
ghg=list(csv.DictReader((ROOT/'04_Data/Ready/Carbon/Ward_GHG_Total_1990-2023.csv').open(encoding='utf-8-sig')))
ward_layer=memory('Ward CO2 2023（区级公开估算）','MultiPolygon',[
    ('ward_code',QVariant.String),('ward_name',QVariant.String),('co2_kt',QVariant.Double),('ghg_kt_co2eq',QVariant.Double),
    ('industry_kt',QVariant.Double),('household_kt',QVariant.Double),('business_kt',QVariant.Double),('transport_kt',QVariant.Double),('waste_kt',QVariant.Double),
    ('year',QVariant.Int),('factor_basis',QVariant.String),('label',QVariant.String)])
for code,jp,en in [('13101','千代田区','Chiyoda'),('13102','中央区','Chuo')]:
    vals={r['sector']:float(r['co2_kt']) for r in carbon if r['ward_code']==code}
    g=next(float(r['ghg_kt_co2eq']) for r in ghg if r['ward_code']==code and r['fiscal_year']=='2023' and r['electricity_factor_basis']=='non_fossil_adjusted_basis')
    geom=QgsGeometry.unaryUnion(ward_geometries[code]);label=en+'（'+jp+'）\n'+format(vals['Total'],',.0f')+' kt CO2 / 2023'
    ward_layer.dataProvider().addFeatures([feature(ward_layer,geom,[code,jp,vals['Total'],g,vals['Industry'],vals['Household'],vals['Business'],vals['Transport'],vals['Waste'],2023,'Non-fossil-adjusted basis',label])])

layers={}
for key,l in [('census_areas_2020',census),('primary_area',primary),('download_extent',download_extent),*target_layers.items(),('wards_co2_2023',ward_layer)]:
    layers[key]=save(l,key)
# Open GeoPackage providers after every table is written, avoiding stale GDAL
# connection schemas while adding tables to a file that already has readers.
for key,original in list(layers.items()):
    loaded=QgsVectorLayer(str(GPKG)+'|layername='+key,original.name(),'ogr')
    assert loaded.isValid(),key
    loaded.setAbstract('Common foundation 2026-10-13. Source and quality records: 03_Theme_B/Common_Foundation.')
    layers[key]=loaded
statistics['source_census_features']=len(raw_census)
statistics['census_source_crs']=source_crs
statistics['primary_town_codes']=['13101035001','13101035002']
statistics['primary_population_2020']=core_pop;statistics['primary_households_2020']=core_households
statistics['primary_area_m2']=core.area()
statistics['feature_counts']={k:l.featureCount() for k,l in layers.items()}
statistics['osm_timestamp']=osm['osm3s']['timestamp_osm_base']
statistics['osm_relation_records_not_polygonized']=skipped_relations
statistics['osm_invalid_polygons_repaired']=invalid_polygons
bf=list(layers['buildings'].getFeatures());core_bf=[f for f in bf if f['intersects_primary']==1]
statistics['buildings_intersecting_primary']=len(core_bf)
statistics['building_levels_known_all']=sum(f['levels_status']=='Known' for f in bf)
statistics['building_levels_known_primary']=sum(f['levels_status']=='Known' for f in core_bf)
statistics['primary_footprint_intersection_sum_m2']=sum(f['area_in_primary_m2'] for f in core_bf)
statistics['census_population_by_ward']={c:sum(r['population_2020'] for r in raw_census if r['ward_code']==c) for c in ['13101','13102']}
statistics['census_duplicate_town_codes']=len(raw_census)-len(set(r['town_code'] for r in raw_census))
statistics['census_repeated_geometry_flags']=sum(bool(r['repeat_flag']) for r in raw_census)


def fill(layer,color,stroke='#ffffff',width='.15'):
    layer.renderer().setSymbol(QgsFillSymbol.createSimple({'color':color,'outline_color':stroke,'outline_width':width}))


fill(layers['census_areas_2020'],'#f1f0e9','#deded3','.13')
fill(layers['primary_area'],'transparent','#ce5a32','.85')
fill(layers['download_extent'],'transparent','#83918c','.25')
fill(layers['buildings'],'#b5c0bd','#f9f9f2','.05')
fill(layers['greens'],'#b8d8b8','#89ac8c','.12')
fill(layers['water'],'#b8d7e1','#94bccd','.1')
for k,color,width in [('roads','#aaa99e','.16'),('rail','#76716b','.23'),('water_lines','#9ebfcd','.5')]:
    layers[k].renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':color,'line_width':width}))
layers['stations'].renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'circle','color':'#245b57','outline_color':'white','size':'2.0'}))


def labeling(l,field,size=8,color='#263b3c'):
    p=QgsPalLayerSettings();p.fieldName=field;p.placement=QgsPalLayerSettings.OverPoint if l.geometryType()==QgsWkbTypes.PointGeometry else QgsPalLayerSettings.Horizontal
    tf=QgsTextFormat();tf.setFont(QFont('PingFang SC',size));tf.setSize(size);tf.setColor(QColor(color))
    buffer=QgsTextBufferSettings();buffer.setEnabled(True);buffer.setSize(.7);buffer.setColor(QColor('white'));tf.setBuffer(buffer);p.setFormat(tf)
    l.setLabeling(QgsVectorLayerSimpleLabeling(p));l.setLabelsEnabled(True)


labeling(layers['stations'],'name',7)
labeling(layers['wards_co2_2023'],'label',11)
fill(layers['wards_co2_2023'],'#a8c4ba','#ffffff','.4')
cats=[]
for val,col,lab in [('13101','#82afa5','Chiyoda（千代田区）'),('13102','#bdd1b3','Chuo（中央区）')]:
    cats.append(QgsRendererCategory(val,QgsFillSymbol.createSimple({'color':col,'outline_color':'white','outline_width':'.4'}),lab))
layers['wards_co2_2023'].setRenderer(QgsCategorizedSymbolRenderer('ward_code',cats))
groups={n:project.layerTreeRoot().addGroup(n) for n in ['Study area（研究范围）','Base layers（基础图层）','Census（人口）','Carbon context（碳背景）']}
for k,l in layers.items():
    g=groups['Study area（研究范围）'] if k in ['primary_area','download_extent'] else groups['Census（人口）'] if k=='census_areas_2020' else groups['Carbon context（碳背景）'] if k=='wards_co2_2023' else groups['Base layers（基础图层）']
    project.addMapLayer(l,False);g.addLayer(l)
    if k in ['download_extent','wards_co2_2023']:project.layerTreeRoot().findLayer(l.id()).setItemVisibilityChecked(False)
    l.saveNamedStyle(str(STYLES/(k+'.qml')))
base_keys=['primary_area','stations','rail','roads','greens','water_lines','water','buildings','census_areas_2020']
base_layers=[layers[k] for k in base_keys]
project.layerTreeRoot().setHasCustomLayerOrder(True);project.layerTreeRoot().setCustomLayerOrder(base_layers+[layers['download_extent'],layers['wards_co2_2023']])
project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(context_geom.boundingBox(),crs))


def label(layout,text,x,y,w,h,size=9):
    l=QgsLayoutItemLabel(layout);l.setText(text);l.setFont(QFont('PingFang SC',size));l.setFontColor(QColor('#253b3c'))
    l.attemptMove(QgsLayoutPoint(x,y));l.attemptResize(QgsLayoutSize(w,h));layout.addLayoutItem(l);return l


def map_layout(name,title,subtitle,maplayers,extent,legend_layers,notes,scale_segment,source_text=None):
    layout=QgsPrintLayout(project);layout.initializeDefaults();layout.setName(name)
    layout.pageCollection().pages()[0].setPageSize('A4',QgsLayoutItemPage.Landscape)
    layout.renderContext().setDpi(200)
    label(layout,title,8,5,281,10,17);label(layout,subtitle,8,17,281,10,8)
    m=QgsLayoutItemMap(layout)
    # Seed both geometry and geographic extent before resizing. An empty map
    # extent gives a NaN height in the bundled QGIS 3.32 layout implementation.
    m.setRect(0,0,215,150);m.setCrs(crs);m.setExtent(extent)
    layout.addLayoutItem(m);m.attemptMove(QgsLayoutPoint(8,31));m.attemptResize(QgsLayoutSize(215,150))
    m.setLayers(maplayers);m.setKeepLayerSet(True);m.zoomToExtent(extent)
    m.setBackgroundColor(QColor('#f8f8f2'));m.setFrameEnabled(True)
    assert math.isfinite(m.sizeWithUnits().height()) and m.sizeWithUnits().height()>0
    assert math.isfinite(m.scale()) and m.scale()>0 and not m.extent().isEmpty()
    legend=QgsLayoutItemLegend(layout);legend.setTitle('Layers（图层）');legend.setLinkedMap(m);legend.setAutoUpdateModel(False);legend.model().rootGroup().removeAllChildren()
    for layer in legend_layers:legend.model().rootGroup().addLayer(layer)
    legend.attemptMove(QgsLayoutPoint(228,31));legend.attemptResize(QgsLayoutSize(61,70));legend.setStyleFont(QgsLegendStyle.Title,QFont('PingFang SC',10));legend.setStyleFont(QgsLegendStyle.Subgroup,QFont('PingFang SC',8));legend.setStyleFont(QgsLegendStyle.SymbolLabel,QFont('PingFang SC',8));layout.addLayoutItem(legend)
    label(layout,notes,228,106,61,75,8)
    label(layout,'N ↑',208,33,12,8,10)
    bar=QgsLayoutItemScaleBar(layout);bar.setStyle('Single Box');bar.setLinkedMap(m);bar.applyDefaultSize();bar.setUnits(Qgis.DistanceUnit.Meters);bar.setUnitsPerSegment(scale_segment);bar.setNumberOfSegments(2);bar.setNumberOfSegmentsLeft(0);bar.setUnitLabel('m');bar.setFont(QFont('PingFang SC',7));bar.setHeight(1.5);bar.setBoxContentSpace(.5);bar.setLabelBarSpace(1);bar.attemptMove(QgsLayoutPoint(9,183));layout.addLayoutItem(bar)
    label(layout,'CRS: EPSG:6677 · JGD2011 / Japan Plane Rectangular CS IX · units: m',8,194,281,6,7)
    label(layout,source_text or 'Sources: e-Stat Census 2020; © OpenStreetMap contributors (openstreetmap.org/copyright), 2026-10-13. Derived by Studio workspace.',8,200,281,6,6.5)
    project.layoutManager().addLayout(layout)
    template=LAYOUTS/(name+'.qpt')
    layout.saveAsTemplate(str(template),QgsReadWriteContext())
    template.write_text(template.read_text().replace(str(GPKG),os.path.relpath(GPKG,template.parent)),encoding='utf-8')
    exporter=QgsLayoutExporter(layout);settings=QgsLayoutExporter.ImageExportSettings();settings.dpi=200
    settings.exportMetadata=False;settings.generateWorldFile=False;settings.cropToContents=False
    result=exporter.exportToImage(str(MAPS/(name+'.png')),settings)
    assert result==QgsLayoutExporter.Success,result
    return layout


map_layout('01_Context_Base_Map','Kanda–Nihonbashi | Base map（基础底图）',
    'Common foundation / 小组共用底图 · 2026-10-13',base_layers,context_geom.boundingBox(),
    [layers[k] for k in ['primary_area','buildings','roads','greens','water','stations']],
    'Kajicho 1 & 2\n鍛冶町一、二丁目\n\nOrange outline:\n2020 census towns.\n\nContext is a download\nextent. Secondary course\nboundary is pending.\n\nGreen space reflects\nOSM mapped features.',200)

# A dedicated style highlights the presence of floor-count tags, not emissions.
level_layer=QgsVectorLayer(str(GPKG)+'|layername=buildings','Floor-count tags（层数资料）','ogr')
level_layer.setSubsetString('"intersects_primary"=1')
categories=[]
for val,col,lab in [('Known','#6b9f9d','Known levels（已有层数）'),('Missing','#d9c5ae','Missing levels（待补层数）')]:
    categories.append(QgsRendererCategory(val,QgsFillSymbol.createSimple({'color':col,'outline_color':'white','outline_width':'.06'}),lab))
level_layer.setRenderer(QgsCategorizedSymbolRenderer('levels_status',categories));project.addMapLayer(level_layer,False);groups['Base layers（基础图层）'].addLayer(level_layer);project.layerTreeRoot().findLayer(level_layer.id()).setItemVisibilityChecked(False);level_layer.saveNamedStyle(str(STYLES/'primary_building_levels.qml'))
extent=QgsRectangle(core.boundingBox());extent.scale(1.35)
map_layout('02_Kajicho_Building_Data','Kajicho 1 & 2 | Buildings（建筑资料准备）',
    'Floor-count tag coverage / 建筑层数记录覆盖 · Energy inputs pending（能耗资料待补）',
    [layers['primary_area'],layers['stations'],layers['rail'],layers['roads'],level_layer,layers['census_areas_2020']],extent,
    [layers['primary_area'],level_layer,layers['roads']],
    'OSM buildings touching\nprimary area: '+str(len(core_bf))+'\n\nLevels recorded: '+str(statistics['building_levels_known_primary'])+'\n\nResidents (2020): '+str(core_pop)+'\nHouseholds (2020): '+str(core_households)+'\n\nResidential population\nis distinct from daytime\nworkers and visitors.\n\nCO2 inputs remain null.',100)
extent=QgsRectangle(layers['wards_co2_2023'].extent());extent.scale(1.1)
map_layout('03_Ward_CO2_Context','Chiyoda & Chuo | CO2 context（区级碳排放背景）',
    'Fiscal year 2023 · Published estimate（公开估算） · Unit: 1,000 tonnes CO2',
    [layers['primary_area'],layers['wards_co2_2023']],extent,[layers['wards_co2_2023'],layers['primary_area']],
    '2023 CO2 totals\nChiyoda: 2,231 kt\nChuo: 1,658 kt\n\nScope: whole wards.\nKajicho is shown for\nlocation only.\n\n2023 uses a changed\nelectricity-factor basis.\nOld-basis reference:\nChiyoda 2,451 kt;\nChuo 1,812 kt.\n\nCO2eq totals are kept\nin a separate data table.',1000,
    'Sources: e-Stat Census 2020 boundaries; All Tokyo 62, fiscal-year 2023 estimates, report published 2026. Derived by Studio workspace.')
project.setFileName(str(PROJECT));assert project.write(),str(PROJECT)
# QGIS 3.32 writes absolute fallback sources inside layout LayerSet elements
# even with relative project paths. Normalize these references for handover.
portable=PROJECT.with_suffix('.portable.qgz')
with ZipFile(PROJECT) as source,ZipFile(portable,'w') as target:
    for info in source.infolist():
        payload=source.read(info.filename)
        if info.filename.endswith('.qgs'):
            payload=payload.decode('utf-8').replace(str(GPKG),os.path.relpath(GPKG,PROJECT.parent)).encode('utf-8')
        target.writestr(info,payload)
portable.replace(PROJECT)
(ROOT/'03_Theme_B/Common_Foundation/Sources/gis_build_summary.json').write_text(json.dumps(statistics,ensure_ascii=False,indent=2))
with (ROOT/'04_Data/Ready/Census_Town_Population_2020.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,list(raw_census[0]));w.writeheader();w.writerows(raw_census)
print(json.dumps(statistics,ensure_ascii=False,indent=2),flush=True)
check=QgsProject();assert check.read(str(PROJECT));assert len(check.mapLayers())==len(project.mapLayers());assert all(l.isValid() for l in check.mapLayers().values())
for layout in check.layoutManager().layouts():
    for item in layout.items():
        if isinstance(item,QgsLayoutItemMap):
            assert math.isfinite(item.scale()) and item.scale()>0 and not item.extent().isEmpty(),layout.name()
print('Project readback: OK',len(check.mapLayers()),flush=True)
check.clear();project.clear()
# QGIS.app 3.32 on macOS can crash during process teardown with live Python
# provider wrappers. Files are fully saved and read back before this CLI exit.
os._exit(0)
