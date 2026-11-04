#!/usr/bin/env python3
"""Build dated, portable QGIS baseline from saved official data; never edit originals.
Run with QGIS Python and QT_QPA_PLATFORM=offscreen, PROJ_LIB set to QGIS resources.
"""
import json,csv,os,collections,math
from pathlib import Path
from qgis.core import *
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor,QFont
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'04_Data/Raw/Public_Baseline_2026-10-14';OUT=ROOT/'04_Data/Ready/Public_Baseline_2026-10-14'
GPKG=OUT/'Kajicho_Public_Baseline.gpkg';QGZ=ROOT/'05_QGIS/Projects/Kajicho_Public_Baseline_2026-10-14.qgz';MAPS=ROOT/'06_Outputs/Maps/Public_Baseline_2026-10-14';MAPS.mkdir(parents=True,exist_ok=True)
app=QgsApplication([],False);app.initQgis();project=QgsProject();crs=QgsCoordinateReferenceSystem('EPSG:6677');project.setCrs(crs);project.setFilePathStorage(Qgis.FilePathType.Relative);project.setFileName(str(QGZ));project.setTitle('Kajicho | Public baseline 2026-10-14')
ctx=project.transformContext();audit={'crs':'EPSG:6677','layers':{},'sources':{},'core':{},'scope':'Kajicho 1 and 2; existing v2 core IDs; surrounding bbox 139.767,35.687,139.776,35.695'};layers={}
S=QVariant.String;D=QVariant.Double;I=QVariant.Int

def val(x):
 if QgsVariantUtils.isNull(x):return None
 return x.toString('yyyy-MM-dd') if hasattr(x,'toString') else x

def mem(key,geom,fields):
 l=QgsVectorLayer(geom+'?crs=EPSG:6677',key,'memory');l.dataProvider().addAttributes([QgsField(k,t) for k,t in fields]);l.updateFields();return l

def add(l,g,vs):
 f=QgsFeature(l.fields());f.setGeometry(g);f.setAttributes(vs);l.dataProvider().addFeatures([f])

def save(l,key):
 op=QgsVectorFileWriter.SaveVectorOptions();op.driverName='GPKG';op.layerName=key;op.fileEncoding='UTF-8';op.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteLayer if GPKG.exists() else QgsVectorFileWriter.CreateOrOverwriteFile
 r=QgsVectorFileWriter.writeAsVectorFormatV3(l,str(GPKG),ctx,op);assert r[0]==0,r
 layers[key]=l;audit['layers'][key]={'features':l.featureCount(),'geometry':QgsWkbTypes.displayString(l.wkbType()),'crs':l.crs().authid()};print(key,l.featureCount(),flush=True);return l

def write_csv(name,rows):
 if not rows:return
 with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

common=ROOT/'04_Data/Ready/Kanda_Nihonbashi_Common_Foundation.gpkg'
primary=QgsVectorLayer(str(common)+'|layername=primary_area','primary_area','ogr');core=next(primary.getFeatures()).geometry();save(primary,'primary_area')
tr=QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),crs,project);extent=QgsGeometry.fromRect(QgsRectangle(139.767,35.687,139.776,35.695));extent.transform(tr)
l=mem('analysis_extent','MultiPolygon',[('name',S)]);extent.convertToMultiType();add(l,extent,['Demo context; course boundary pending']);save(l,'analysis_extent')

def subset(path,key,encoding=None,clip=True,extra=True):
 src=QgsVectorLayer(str(path),key,'ogr');assert src.isValid(),str(path)
 if encoding:src.setProviderEncoding(encoding)
 typ=QgsWkbTypes.multiType(QgsWkbTypes.flatType(src.wkbType()));geom=QgsWkbTypes.displayString(typ)
 out=mem(key,geom,[]);out.dataProvider().addAttributes(src.fields().toList());out.updateFields()
 if extra:out.dataProvider().addAttributes([QgsField('source_path',S),QgsField('intersects_core',I)]);out.updateFields()
 transform=QgsCoordinateTransform(src.crs(),crs,project);back=QgsCoordinateTransform(crs,src.crs(),project)
 rect=back.transformBoundingBox(extent.boundingBox());repair=0
 for f in src.getFeatures(QgsFeatureRequest().setFilterRect(rect)):
  g=QgsGeometry(f.geometry());g.transform(transform);g.convertToMultiType()
  if g.type()==QgsWkbTypes.PolygonGeometry and not g.isGeosValid():
   repair+=1
   if 'fld' in key:g=QgsGeometry.unaryUnion(g.asGeometryCollection())
   if not g.isGeosValid():g=g.makeValid()
  if not g.intersects(extent):continue
  if clip:g=g.intersection(extent)
  if g.isEmpty():continue
  g.convertToMultiType()
  if g.type()!=src.geometryType():continue
  attrs=f.attributes()+([str(Path(path).relative_to(ROOT)),int(g.intersects(core))] if extra else [])
  add(out,g,attrs)
 audit['sources'][key]={'path':str(Path(path).relative_to(ROOT)),'source_crs':src.crs().authid(),'source_features':src.featureCount(),'invalid_geometries_repaired':repair,'clipped':clip}
 return save(out,key)

# Official MLIT planning references; keep original fields including FAR/BCR.
for code in ['13101','13102']:
 folder=next(p for p in (RAW/'MLIT_Tokyo/13_東京都').iterdir() if p.is_dir() and p.name.startswith(code+'_'))
 for p in sorted(folder.glob('*.geojson')):
  if p.name.startswith('._'):continue
  suffix=p.stem.split('_',1)[1]
  if suffix in ['youto','chikukei','bouka','koudori','koudoti','tokureiyouseki','toshisaisei']:
   subset(p,'mlit_'+code+'_'+suffix)

for typ in ['urf','luse','tran','fld']:
 subset(OUT/f'CityGML_{typ}_source_extent.geojson','plateau_'+typ)

# Municipal park data include several inventory classes; only polygon records overlap here.
for p in (RAW/'Tokyo_Green').rglob('*.shp'):
 if p.name.startswith('._'):continue
 if '_pt' in p.name and '街路樹' in p.name:key='street_tree_points'
 elif '_line' in p.name and '街路樹' in p.name:key='street_tree_routes'
 elif p.stem=='区市町村立公園(都市公園)':key='parks_city'
 elif p.stem=='区市町村立公園(都市公園以外)':key='parks_other'
 elif p.stem=='都立公園':key='parks_metropolitan'
 else:continue
 subset(p,key,'CP932',clip=True)

crowns=mem('crown_circles','MultiPolygon',[('tree_inventory_fid',I),('species',S),('height_m',D),('spread_m',D),('method',S),('intersects_core',I)])
for f in layers['street_tree_points'].getFeatures():
 w=val(f['枝張ｍ']);h=val(f['樹高m'])
 if w is None or float(w)<=0:continue
 g=f.geometry().buffer(float(w)/2,24);g.convertToMultiType();add(crowns,g,[f.id(),val(f['樹種']),h,w,'Circle from inventory crown spread; not surveyed canopy polygon',int(g.intersects(core))])
save(crowns,'tree_crown_circles')

# Related facilities retain point geometry and each source year from the filename.
for code in ['13101','13102']:
 for p in (RAW/'PLATEAU'/f'{code}_related').glob('*.geojson'):
  if p.name.startswith('._') or not any(p.stem.endswith(x) for x in ['station','shelter','park','emergency_route']):continue
  subset(p,'related_'+code+'_'+p.stem.split('_')[-1])

attrs=json.loads((OUT/'CityGML_Building_Attributes.json').read_text());city=json.loads((ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data/city.json').read_text());demo={b['id']:b for b in city['buildings']};src=QgsVectorLayer(str(ROOT/'04_Data/Ready/Simulation_Demo/plateau_buildings_6677.geojson'),'buildings','ogr')
fields=[('building_id',S),('plateau_building_id',S),('core',I),('usage',S),('detailed_use',S),('height_m',D),('height_source',S),('levels',D),('levels_source',S),('plan_area_m2',D),('floor_proxy_m2',D),('source_roof_edge_area_m2',D),('source_floor_factor',D),('survey_year',I),('model_year',I),('creation_date',S),('construction_year',I),('fire_structure',S),('source_far_pct',D),('source_bcr_pct',D),('mlit_far_pct_set',S),('mlit_far_match',S),('actual_electricity_kwh',D),('actual_gas_m3',D),('actual_co2_t',D),('scenario_eui_kwh_m2_y',D),('scenario_electricity_kwh',D),('scenario_grid_kgco2_kwh',D),('scenario_electricity_co2_t',D),('source_attributes_json',S)]
bld=mem('buildings','MultiPolygon',fields);rows=[];zone_rows=[];qc=collections.Counter();zones=[f for key,l in layers.items() if key.startswith('mlit_') and key.endswith('_youto') for f in l.getFeatures()]
for f in src.getFeatures():
 id=f['id'];a=attrs[id];b=demo[id];g=f.geometry();g.convertToMultiType();floor=b['area']*b['levels'];far=float(a['specifiedFloorAreaRate']);fars=[]
 for z in zones:
  if not g.boundingBox().intersects(z.geometry().boundingBox()):continue
  area=g.intersection(z.geometry()).area()
  if area<=0.01:continue
  v=val(z['FAR'])
  if v is not None:fars.append(float(v))
  if b['core']:zone_rows.append({'building_id':id,'zone_ward':val(z['Citycode']),'zone_name':val(z['YoutoName']),'far_pct':v,'bcr_pct':val(z['BCR']),'intersection_m2':area,'model_plan_share':area/g.area(),'basis':'Building LOD1 plan overlap, not cadastral parcel'})
 fars=sorted(set(fars));match='match' if fars==[far] else 'multiple_zones' if len(fars)>1 else 'different' if fars else 'no_overlap'
 sy=a.get('surveyYear');sy=int(sy) if sy and sy!='0001' else None
 factor=a.get('generic_延べ面積換算係数');factor=float(factor) if factor else None
 d={'building_id':id,'plateau_building_id':a.get('buildingID'),'core':int(b['core']),'usage':a.get('usage_label'),'detailed_use':a.get('detailedUsage_label'),'height_m':b['h'],'height_source':b['height_source'],'levels':b['levels'],'levels_source':b['levels_source'],'plan_area_m2':b['area'],'floor_proxy_m2':floor,'source_roof_edge_area_m2':float(a['buildingRoofEdgeArea']),'source_floor_factor':factor,'survey_year':sy,'model_year':2025,'creation_date':a['creationDate'],'construction_year':None,'fire_structure':a.get('fireproofStructureType_label'),'source_far_pct':far,'source_bcr_pct':float(a['specifiedBuildingCoverageRate']),'mlit_far_pct_set':','.join(str(x) for x in fars),'mlit_far_match':match,'actual_electricity_kwh':None,'actual_gas_m3':None,'actual_co2_t':None,'scenario_eui_kwh_m2_y':120.0,'scenario_electricity_kwh':floor*120,'scenario_grid_kgco2_kwh':0.421,'scenario_electricity_co2_t':floor*120*0.421/1000,'source_attributes_json':json.dumps(a,ensure_ascii=False)}
 add(bld,g,[d[k] for k,t in fields])
 if b['core']:
  rows.append({k:v for k,v in d.items() if k!='source_attributes_json'});qc[match]+=1
save(bld,'buildings');write_csv('Kajicho_Buildings.csv',rows);write_csv('Building_Zoning_Overlap.csv',zone_rows)
assert len(rows)==277 and len({r['building_id'] for r in rows})==277
uses=[]
for use in sorted({r['usage'] for r in rows}):
 rs=[r for r in rows if r['usage']==use];uses.append({'usage':use,'building_objects':len(rs),'floor_proxy_m2':sum(r['floor_proxy_m2'] for r in rs),'scenario_electricity_kwh':sum(r['scenario_electricity_kwh'] for r in rs),'scenario_electricity_co2_t':sum(r['scenario_electricity_co2_t'] for r in rs)})
write_csv('Kajicho_Use_Mix.csv',uses)
audit['core']={'buildings':len(rows),'usage_known':sum(r['usage']!='不明' for r in rows),'levels_source':sum(r['levels_source']=='source' for r in rows),'survey_year_known':sum(r['survey_year'] is not None for r in rows),'construction_year_known':0,'floor_proxy_m2':sum(r['floor_proxy_m2'] for r in rows),'scenario_electricity_kwh':sum(r['scenario_electricity_kwh'] for r in rows),'scenario_electricity_co2_t':sum(r['scenario_electricity_co2_t'] for r in rows),'far_crosscheck':dict(qc),'source_floor_factors':dict(collections.Counter(str(r['source_floor_factor']) for r in rows))}

# Exposure separately by source river scenario; no mixing scenario maxima into flood probability.
exposure=[]
for f in layers['buildings'].getFeatures():
 if f['core']!=1:continue
 for z in layers['plateau_fld'].getFeatures():
  g=f.geometry();zg=z.geometry()
  if not g.boundingBox().intersects(zg.boundingBox()):continue
  area=g.intersection(zg).area()
  if area>0.01:exposure.append({'building_id':f['building_id'],'flood_gml_id':val(z['gml_id']),'scenario_name':val(z['name']),'rank_label':val(z['rank_label']),'intersect_area_m2':area,'plan_share':area/g.area(),'source_file':val(z['source_file'])})
write_csv('Building_Flood_Exposure.csv',exposure)
audit['flood_exposure']={'core_buildings_any_overlap':len({r['building_id'] for r in exposure}),'by_scenario':{s:len({r['building_id'] for r in exposure if r['scenario_name']==s}) for s in sorted({r['scenario_name'] for r in exposure})}}
for key in ['street_tree_points','street_tree_routes','tree_crown_circles','parks_city','parks_other']:
 audit['layers'][key]['core_intersections']=sum(f['intersects_core'] for f in layers[key].getFeatures())

# Reference context from existing package.
for key in ['roads','water','water_lines','rail']:
 l=QgsVectorLayer(str(common)+'|layername='+key,key,'ogr')
 if l.isValid():save(l,key)

# Load disk layers only after all writes; avoid OGR cached schema during creation.
for key in list(layers):
 l=QgsVectorLayer(str(GPKG)+'|layername='+key,key,'ogr');assert l.isValid(),key;layers[key]=l
# Simple source-backed map styles.
def fill(l,color,stroke='#ffffff',opacity=1):
 sym=QgsFillSymbol.createSimple({'color':color,'outline_color':stroke,'outline_width':'0.12'});l.renderer().setSymbol(sym);l.setOpacity(opacity)
for key,l in layers.items():
 if l.geometryType()==QgsWkbTypes.PolygonGeometry:fill(l,'#d7d5cc','#ffffff')
 elif l.geometryType()==QgsWkbTypes.LineGeometry:l.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':'#a6a29b','line_width':'0.25'}))
 else:l.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'circle','color':'#326e51','outline_style':'no','size':'1.7'}))
 if 'park' in key or key=='tree_crown_circles':fill(l,'#78a684','#4f7b61') if l.geometryType()==2 else None
 if key=='plateau_fld':fill(l,'#82b6d0','#82b6d0',0.35)
 if key=='water':fill(l,'#b4ccd4','#b4ccd4')
 if key.endswith('_chikukei'):l.renderer().setSymbol(QgsFillSymbol.createSimple({'style':'no','outline_color':'#566459','outline_style':'dash','outline_width':'0.5'}))
 if key in ['primary_area','analysis_extent']:
  sym=QgsFillSymbol.createSimple({'style':'no','outline_color':'#b94b34' if key=='primary_area' else '#777777','outline_width':'0.65' if key=='primary_area' else '0.25'});l.renderer().setSymbol(sym)
 if key=='street_tree_routes':l.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':'#3b7757','line_width':'1.0','line_style':'dash'}))
use_colors={'業務施設':'#657f9c','商業施設':'#c89567','店舗等併用住宅':'#d7b593','住宅':'#b3b392','共同住宅':'#a0a98b','宿泊施設':'#aa8592','文教厚生施設':'#8eacc1','不明':'#d8d5cd'}
cats=[]
for use in sorted({r['usage'] for r in rows}):
 cats.append(QgsRendererCategory(use,QgsFillSymbol.createSimple({'color':use_colors.get(use,'#939388'),'outline_color':'#ffffff','outline_width':'0.12'}),use))
layers['buildings'].setRenderer(QgsCategorizedSymbolRenderer('usage',cats))
for code in ['13101','13102']:
 l=layers['mlit_'+code+'_youto'];cats=[]
 for value in sorted({str(val(f['FAR'])) for f in l.getFeatures()}):
  color={'600.0':'#e4c99c','800.0':'#c78b5e','700.0':'#d5ad7c','500.0':'#eee0c5'}.get(value,'#d9c9b5');cats.append(QgsRendererCategory(value,QgsFillSymbol.createSimple({'color':color,'outline_color':'#faf8f3','outline_width':'0.25'}),value+'%'))
 l.setRenderer(QgsCategorizedSymbolRenderer('FAR',cats))
root=project.layerTreeRoot()
for group,keys in [('Boundaries',['primary_area','analysis_extent']),('Buildings',['buildings']),('Green',['street_tree_points','tree_crown_circles','street_tree_routes','parks_city','parks_other','parks_metropolitan']),('Planning',[k for k in layers if k.startswith('mlit_')]),('PLATEAU themes',['plateau_urf','plateau_luse','plateau_tran','plateau_fld']),('Facilities',[k for k in layers if k.startswith('related_')]),('Context',['roads','rail','water','water_lines'])]:
 gr=root.addGroup(group)
 for key in keys:
  if key not in layers:continue
  l=layers[key];project.addMapLayer(l,False);node=gr.addLayer(l);node.setItemVisibilityChecked(key in ['primary_area','buildings','street_tree_points','parks_city','parks_other','roads','water'])
project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(extent.boundingBox(),crs))
assert project.write()
# Export QGIS layout previews in English; attributes retain Japanese source labels.
def export_map(name,title,subtitle,keys,legend):
 layout=QgsPrintLayout(project);layout.initializeDefaults();layout.pageCollection().pages()[0].setPageSize(QgsLayoutSize(297,210));layout.setName(name)
 def label(text,x,y,w,h,size=10):
  a=QgsLayoutItemLabel(layout);a.setText(text);a.setFont(QFont('Arial',size));a.setFontColor(QColor('#24322d'));layout.addLayoutItem(a);a.attemptMove(QgsLayoutPoint(x,y));a.attemptResize(QgsLayoutSize(w,h));return a
 label(title,12,6,270,12,20);label(subtitle,12,20,270,10,9)
 m=QgsLayoutItemMap(layout);m.setRect(0,0,210,160);m.setCrs(crs);m.setExtent(extent.boundingBox());layout.addLayoutItem(m);m.attemptMove(QgsLayoutPoint(12,34));m.attemptResize(QgsLayoutSize(210,160));m.setCrs(crs);m.setLayers([layers[k] for k in keys if k in layers]);m.setKeepLayerSet(True);rect=QgsRectangle(extent.boundingBox());rect.scale(1.04);m.zoomToExtent(rect);assert math.isfinite(m.extent().xMinimum()) and math.isfinite(m.scale());m.setBackgroundColor(QColor('#f6f4ee'));m.setBackgroundEnabled(True)
 label('N ↑',230,34,45,10,11);label(legend,230,48,55,105,9);label('PLATEAU / MLIT / Tokyo\n© OpenStreetMap contributors\nEPSG:6677 • Draft study boundary\n14 Oct 2026',228,164,58,27,8)
 scale=QgsLayoutItemScaleBar(layout);scale.setStyle('Single Box');scale.setLinkedMap(m);scale.applyDefaultSize();scale.setUnits(QgsUnitTypes.DistanceMeters);scale.setUnitsPerSegment(100);scale.setNumberOfSegments(2);scale.setNumberOfSegmentsLeft(0);scale.setUnitLabel('m');scale.setFont(QFont('Arial',8));layout.addLayoutItem(scale);scale.attemptMove(QgsLayoutPoint(20,181));scale.setHeight(1.5)
 project.layoutManager().addLayout(layout);opts=QgsLayoutExporter.ImageExportSettings();opts.dpi=150;r=QgsLayoutExporter(layout).exportToImage(str(MAPS/(name+'.png')),opts);assert r==0,r
export_map('01_Building_Use','Kajicho | Building use','277 core objects · 250 with known use · source survey mainly 2021',['primary_area','buildings','water'], 'BLUE\nOffice\n\nOCHRE\nRetail / mixed use\n\nGREY\nUnknown use\n\nRED OUTLINE\nKajicho 1 & 2')
export_map('02_Planning','Kajicho | Planning reference','MLIT FY2025 reference GIS · July 2026 revision · verify parcel conditions with the ward',['primary_area','mlit_13101_chikukei','mlit_13102_chikukei','mlit_13101_youto','mlit_13102_youto','water'],'FAR bands\nLight ochre: 600%\nDark ochre: 800%\n\nDistrict plan edges\nshown dashed\n\nBuilding capacity also\ndepends on road and\nparcel conditions.')
export_map('03_Green','Kajicho | Trees and parks','Points: individual inventory · Dashed lines: route inventory · circles use recorded crown spread',['primary_area','street_tree_points','tree_crown_circles','street_tree_routes','parks_city','parks_other','buildings','water'],'GREEN POINTS\nIndividual trees\n\nGREEN CIRCLES\nEstimated crown shape\n\nDASHED GREEN\nRoute tree records\n\nGREEN AREAS\nPark boundaries')
project.write();
from zipfile import ZipFile
portable=QGZ.with_suffix('.portable.qgz')
with ZipFile(QGZ) as source,ZipFile(portable,'w') as target:
 for info in source.infolist():
  payload=source.read(info.filename)
  if info.filename.endswith('.qgs'):payload=payload.decode().replace(str(GPKG),os.path.relpath(GPKG,QGZ.parent)).encode()
  target.writestr(info,payload)
portable.replace(QGZ)
(OUT/'Spatial_Quality.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));print(json.dumps(audit['core'],ensure_ascii=False,indent=2));print(audit['flood_exposure']);project.clear();os._exit(0)
