#!/usr/bin/env python3
"""Update the public QGIS age display using the supplied 277-building layer."""
from pathlib import Path
import json
from qgis.core import (QgsApplication, QgsProject, QgsVectorLayer, QgsFillSymbol,
                       QgsRuleBasedRenderer)
from qgis.PyQt.QtGui import QColor

base=Path(__file__).resolve().parent.parent
project_file=base/'04_Data/Ready/QGIS_Current_2026-11-04/Kajicho_Current_Data.qgz'
shp=base/'04_Data/Ready/QGIS_Current_2026-11-04/shp/Primary_Building_Age_2026-11-13/Buildings_Kajicho_BYear0.shp'
app=QgsApplication([], False)
app.initQgis()
p=QgsProject.instance()
if not p.read(str(project_file)): raise RuntimeError('Could not open saved QGIS project')
if p.mapLayersByName('Primary building age · supplied years'):
 raise RuntimeError('The primary age update is already present')
prior_invalid=sorted(l.name() for l in p.mapLayers().values() if not l.isValid())
names={'Age evidence classes','Building age · 2026','Building chronology · 2011 reference'}
changed=[]
for layer in p.mapLayers().values():
 if layer.name() not in names or not any(s in layer.source() for s in ('D008_building_2011_evidence','D026_buildings_current')): continue
 old=layer.subsetString()
 new=f'({old}) AND COALESCE("in_primary", 0) <> 1' if old else 'COALESCE("in_primary", 0) <> 1'
 if not layer.setSubsetString(new): raise RuntimeError(f'Could not filter {layer.name()}')
 changed.append((layer.name(),new,layer.featureCount()))
if len(changed)!=5: raise RuntimeError(f'Expected 5 age views; found {changed}')
layer=QgsVectorLayer(str(shp),'Primary building age · supplied years','ogr')
if not layer.isValid() or layer.featureCount()!=277: raise RuntimeError('Source age layer invalid or incomplete')
renderer=QgsRuleBasedRenderer(QgsFillSymbol.createSimple({'color':'217,221,218,255','outline_color':'78,103,95,255','outline_width':'0.14'}))
root=renderer.rootRule()
for child in list(root.children()): root.removeChild(child)
items=[('Before 1970','"Byear" < 1970','#315c66'),('1970–1979','"Byear" >= 1970 AND "Byear" < 1980','#45838a'),('1980–1989','"Byear" >= 1980 AND "Byear" < 1990','#8ab0a4'),('1990–1999','"Byear" >= 1990 AND "Byear" < 2000','#d8c87e'),('2000–2009','"Byear" >= 2000 AND "Byear" < 2010','#dc9865'),('2010 and later','"Byear" >= 2010','#ad5d49'),('No year','"Byear" IS NULL','#d9ddda')]
for label,expr,color in items:
 symbol=QgsFillSymbol.createSimple({'color':QColor(color).name(),'outline_color':'#556b64','outline_width':'0.14'})
 rule=QgsRuleBasedRenderer.Rule(symbol); rule.setLabel(label); rule.setFilterExpression(expr); root.appendChild(rule)
layer.setRenderer(renderer)
meta=layer.metadata();meta.setAbstract('User-supplied Buildings_Kajicho_BYear0.geojson, received 13 November 2026; exact Byear provenance and licence not supplied. 277 features; 221 recorded years and 56 null. Source polygons retain Z coordinates.');layer.setMetadata(meta)
p.addMapLayer(layer,False)
tree=p.layerTreeRoot();node=tree.insertLayer(0,layer);node.setItemVisibilityChecked(True)
if tree.hasCustomLayerOrder(): tree.setCustomLayerOrder([layer]+[x for x in tree.customLayerOrder() if x.id()!=layer.id()])
if not p.write(): raise RuntimeError('Could not save QGIS project')
print(json.dumps({'changed':changed,'new_layer_features':layer.featureCount(),'previous_invalid':prior_invalid,'after_invalid':sorted(l.name() for l in p.mapLayers().values() if not l.isValid())},ensure_ascii=False))
app.exitQgis()
