#!/usr/bin/env python3
import csv,json
from pathlib import Path
from qgis.core import *
from qgis.PyQt.QtCore import QVariant
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'04_Data/Ready/CFD_Baseline_2026-10-14'
app=QgsApplication([],False);app.initQgis();p=QgsProject();crs=QgsCoordinateReferenceSystem('EPSG:6677');tr=QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),crs,p)
city=json.loads((ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data/city.json').read_text());origin=city['meta']['origin_epsg6677'];boundary_data=city['boundary'];polygons=[boundary_data['coordinates']] if boundary_data['type']=='Polygon' else boundary_data['coordinates'];boundary=QgsGeometry.fromMultiPolygonXY([[[QgsPointXY(x,y) for x,y in ring] for ring in poly] for poly in polygons]);boundary.translate(*origin)
l=QgsVectorLayer('Point?crs=EPSG:6677','street_trees_extended','memory');l.dataProvider().addAttributes([QgsField(n,t) for n,t in [('tree_id',QVariant.String),('species',QVariant.String),('height_m',QVariant.Double),('crown_m',QVariant.Double),('road_name',QVariant.String),('source_year',QVariant.Int),('inside_core',QVariant.Int),('distance_core_m',QVariant.Double)]]);l.updateFields();points=[]
rows=list(csv.DictReader((OUT/'Tokyo_Trees_Extended_Bbox.csv').open(encoding='utf-8-sig')))
for i,r in enumerate(rows):
 xy=tr.transform(QgsPointXY(float(r['経度']),float(r['緯度'])));g=QgsGeometry.fromPointXY(xy);inside=int(boundary.intersects(g));dist=boundary.distance(g)
 def num(k):
  try:v=float(r[k]);return v if v>0 else None
  except (ValueError,KeyError):return None
 vals=[f'tokyo-tree-csv-{i+1}',r['樹種'],num('樹高(m)'),num('枝張(m)'),r['通称道路名'] or r['路線名'],2020,inside,dist];f=QgsFeature(l.fields());f.setAttributes(vals);f.setGeometry(g);l.dataProvider().addFeatures([f]);points.append(dict(zip([f.name() for f in l.fields()],vals),x=xy.x()-origin[0],y=xy.y()-origin[1]))
opts=QgsVectorFileWriter.SaveVectorOptions();opts.driverName='GPKG';opts.layerName='street_trees_extended';opts.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteLayer
result=QgsVectorFileWriter.writeAsVectorFormatV3(l,str(OUT/'Kajicho_CFD_Baseline.gpkg'),p.transformContext(),opts);assert result[0]==0,result
path=ROOT/'05_QGIS/Projects/Kajicho_CFD_Baseline_2026-10-14.qgz';p.read(str(path));target=QgsVectorLayer(str(OUT/'Kajicho_CFD_Baseline.gpkg')+'|layername=street_trees_extended','Tokyo street trees | 都道单株树位','ogr');assert target.isValid();p.addMapLayer(target);p.layerTreeRoot().findLayer(target.id()).setItemVisibilityChecked(False);assert p.write()
quality={'source_url':'https://www.opendata.metro.tokyo.lg.jp/kensetsu/tokyo_gairoju.csv','catalog_url':'https://catalog.data.metro.tokyo.lg.jp/dataset/t000014d2000000029','license':'CC BY; Tokyo Metropolitan Government','source_year':'FY2020 for Chiyoda/Chuo','download_date':'2026-10-14','source_rows':144183,'selected_rows':len(points),'inside_core':sum(v['inside_core'] for v in points),'within_25m_of_core':sum(v['distance_core_m']<=25 for v in points),'positive_crowns':sum(v['crown_m'] is not None for v in points),'source_crs':'longitude latitude WGS84 as published','ready_crs':'EPSG:6677','processing':'CP932 decode; bbox filter 139.765,35.687,139.778,35.697; reproject; core intersection; no inferred tree positions','scope':'metropolitan roads inventory, not all ward/private trees; keep separate from duplicate inventory shapefile layer'}
(OUT/'Tree_Inventory_Quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2));(OUT/'Street_Trees_Local.json').write_text(json.dumps(points,ensure_ascii=False,separators=(',',':')));print(json.dumps(quality,ensure_ascii=False),flush=True)
