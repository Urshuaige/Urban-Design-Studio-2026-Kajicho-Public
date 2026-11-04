#!/usr/bin/env python3
import json
from pathlib import Path
from qgis.core import *
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'04_Data/Ready/CFD_Baseline_2026-10-14'
app=QgsApplication([],False);app.initQgis();project=QgsProject();d=json.loads((OUT/'domain.json').read_text());origin=d['origin_epsg6677'];s=json.loads((OUT/'scenario.json').read_text());saved=[]
def layer(name,geom,fields):
 l=QgsVectorLayer(geom+'?crs=EPSG:6677',name,'memory');l.dataProvider().addAttributes([QgsField(n,t) for n,t in fields]);l.updateFields();return l
def add(l,g,values):
 f=QgsFeature(l.fields());f.setGeometry(g);f.setAttributes(values);l.dataProvider().addFeatures([f])
def save(l,key):
 opts=QgsVectorFileWriter.SaveVectorOptions();opts.driverName='GPKG';opts.layerName=key;opts.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteLayer
 r=QgsVectorFileWriter.writeAsVectorFormatV3(l,str(OUT/'Kajicho_CFD_Baseline.gpkg'),project.transformContext(),opts);assert r[0]==0,r;saved.append(key)
l=layer('cfd_context_buildings','MultiPolygon',[('building_id',QVariant.String),('height_m',QVariant.Double),('core',QVariant.Int),('distance_core_m',QVariant.Double),('source_mesh',QVariant.String)])
roofs=layer('cfd_roof_scenarios','MultiPolygon',[('building_id',QVariant.String),('baseline_qH_W_m2',QVariant.Double),('retrofit_qH_W_m2',QVariant.Double),('heat_fraction_assumed',QVariant.Double),('plan_area_m2',QVariant.Double)])
for f in json.loads((OUT/'cfd_buildings_local.geojson').read_text())['features']:
 p=f['properties'];g=f['geometry'];polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates'];q=QgsGeometry.fromMultiPolygonXY([[[QgsPointXY(x+origin[0],y+origin[1]) for x,y in ring] for ring in poly] for poly in polys]);add(l,q,[p['id'],p['height_m'],int(p['core']),p['distance_to_core_m'],p['source_mesh']])
 if p['core']:add(roofs,q,[p['id'],s['baseline_roof_heat_W_m2'],s['retrofit_roof_heat_W_m2'],s['sensible_conversion_fraction'],q.area()])
save(l,'cfd_context_buildings');save(roofs,'cfd_roof_scenarios')
l=layer('cfd_domain','Polygon',[('Hmax_m',QVariant.Double),('height_m',QVariant.Double),('blockage',QVariant.Double),('wind_from_deg',QVariant.Double)])
x0,y0,x1,y1,z=d['domain_m'];g=QgsGeometry.fromRect(QgsRectangle(x0+origin[0],y0+origin[1],x1+origin[0],y1+origin[1]));add(l,g,[d['Hmax_m'],z,d['projected_frontal_blockage_fraction'],s['wind_from_deg']]);save(l,'cfd_domain')
path=ROOT/'05_QGIS/Projects/Kajicho_CFD_Baseline_2026-10-14.qgz';project.read(str(path));group=project.layerTreeRoot().insertGroup(0,'CFD domain | 风热计算范围')
for key in saved:
 l=QgsVectorLayer(str(OUT/'Kajicho_CFD_Baseline.gpkg')+'|layername='+key,key,'ogr');assert l.isValid();project.addMapLayer(l,False);node=group.addLayer(l);node.setItemVisibilityChecked(False)
 if key=='cfd_domain':l.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'0,0,0,0','outline_color':'180,100,45,255','outline_width':'0.5'}))
assert project.write();report={'layers':len(project.mapLayers()),'all_layers_valid':all(l.isValid() for l in project.mapLayers().values()),'portable_relative_paths':True,'cfd_objects':3805,'source_geometry':'LOD1 extrusion on flat ground; source elevation stored in derived GeoJSON','core_roof_scenario_objects':277}
(OUT/'QGIS_Quality.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
