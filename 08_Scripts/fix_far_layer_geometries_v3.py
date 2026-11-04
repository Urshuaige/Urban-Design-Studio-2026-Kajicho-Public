#!/usr/bin/env python3
"""Preserve the polygon components when makeValid also returns collapsed lines."""
import json
from pathlib import Path
from qgis.core import *
from qgis.PyQt.QtCore import QVariant
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'04_Data/Ready/CFD_Baseline_2026-10-14';app=QgsApplication([],False);app.initQgis();p=QgsProject()
city=json.loads((ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data/city.json').read_text());origin=city['meta']['origin_epsg6677'];bs={b['id']:b for b in city['buildings']};rows=json.loads((OUT/'FAR26_Official_Review.json').read_text());l=QgsVectorLayer('MultiPolygon?crs=EPSG:6677','far26_review','memory')
names=['building_id','source_far_pct','ward_far_set','dominant_far_pct','minor_share_pct','review_class','legal_parcel_status'];l.dataProvider().addAttributes([QgsField(k,QVariant.Double if k in ['source_far_pct','dominant_far_pct','minor_share_pct'] else QVariant.String) for k in names]);l.updateFields()
def parts(g):
 if g.type()==QgsWkbTypes.PolygonGeometry:return [g]
 if not g.isMultipart() and QgsWkbTypes.flatType(g.wkbType())!=QgsWkbTypes.GeometryCollection:return []
 return [p for c in g.asGeometryCollection() for p in parts(c)]
for r in rows:
 b=bs[r['building_id']];g=QgsGeometry.fromPolygonXY([[QgsPointXY(x+origin[0],y+origin[1]) for x,y in ring] for ring in b['rings']]);g=QgsGeometry.unaryUnion(parts(g.makeValid()));assert not g.isEmpty();g.convertToMultiType();f=QgsFeature(l.fields());f.setGeometry(g);f.setAttributes([r[k] for k in names]);ok,_=l.dataProvider().addFeatures([f]);assert ok,r['building_id']
assert l.featureCount()==26
opts=QgsVectorFileWriter.SaveVectorOptions();opts.driverName='GPKG';opts.layerName='far26_review';opts.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteLayer;r=QgsVectorFileWriter.writeAsVectorFormatV3(l,str(OUT/'Kajicho_CFD_Baseline.gpkg'),p.transformContext(),opts);assert r[0]==0,r;print('FAR26 polygon layer restored: 26 features; collapsed lines discarded',flush=True)
