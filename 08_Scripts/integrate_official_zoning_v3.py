#!/usr/bin/env python3
"""Create a new portable QGIS edition and review the 26 FAR intersections.
Run with the QGIS Python environment; baseline/original files stay unchanged.
"""
import csv,json,shutil
from pathlib import Path
from qgis.core import *
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'04_Data/Ready/CFD_Baseline_2026-10-14';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'03_Theme_B/Simulation_V3/Sources';OLD=ROOT/'04_Data/Ready/Public_Baseline_2026-10-14'
GPKG=OUT/'Kajicho_CFD_Baseline.gpkg'
for suffix in ['', '-wal','-shm']:
 p=Path(str(GPKG)+suffix)
 if p.exists():p.unlink()
shutil.copy2(OLD/'Kajicho_Public_Baseline.gpkg',GPKG)
app=QgsApplication([],False);app.initQgis();project=QgsProject();saved=[]
def save(layer,key):
 opts=QgsVectorFileWriter.SaveVectorOptions();opts.driverName='GPKG';opts.layerName=key;opts.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteLayer
 result=QgsVectorFileWriter.writeAsVectorFormatV3(layer,str(GPKG),project.transformContext(),opts);assert result[0]==0,result;print(key,result,flush=True)
 saved.append(key);return layer
layers={}
for i,key in [(11,'ward_use_far'),(13,'ward_boundary_distance_lines'),(14,'ward_boundary_distance_labels'),(15,'ward_road_center_basis')]:
 source=QgsVectorLayer(str(SOURCE/f'Chiyoda_Zoning_{i}.geojson'),key,'ogr');assert source.isValid();layers[i]=save(source,key)
zones=[(f.geometry().makeValid(),f['容積率'],f['OBJECTID']) for f in layers[11].getFeatures()]
city=json.loads((ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data/city.json').read_text());origin=city['meta']['origin_epsg6677'];byid={b['id']:b for b in city['buildings']}
reviews=list(csv.DictReader((OLD/'Building_FAR_Review.csv').open(encoding='utf-8-sig')))
out=QgsVectorLayer('MultiPolygon?crs=EPSG:6677','far26_review','memory')
fields=[('building_id',QVariant.String),('source_far_pct',QVariant.Double),('ward_far_set',QVariant.String),('dominant_far_pct',QVariant.Double),('minor_share_pct',QVariant.Double),('review_class',QVariant.String),('legal_parcel_status',QVariant.String)]
out.dataProvider().addAttributes([QgsField(n,t) for n,t in fields]);out.updateFields();rows=[]
for r in reviews:
 b=byid[r['building_id']];g=QgsGeometry.fromPolygonXY([[QgsPointXY(x+origin[0],y+origin[1]) for x,y in ring] for ring in b['rings']]);g=g.makeValid();area=g.area();over=[]
 for z,far,oid in zones:
  if not g.intersects(z):continue
  a=g.intersection(z).area()
  if a>.01:over.append({'objectid':oid,'far_pct':far,'overlap_m2':a,'share_pct':100*a/area})
 over.sort(key=lambda a:-a['overlap_m2']);significant=[a for a in over if a['overlap_m2']>=1 and a['share_pct']>=.5];farset=sorted({float(a['far_pct']) for a in significant})
 cls='crosses official FAR boundary' if len(farset)>1 else ('minor edge/sliver only' if len(over)>1 else 'single official zone')
 vals=[r['building_id'],float(r['source_far_pct']),','.join(f'{v:g}' for v in farset),over[0]['far_pct'] if over else None,sum(a['share_pct'] for a in over[1:]),cls,'parcel boundary / legal capacity pending']
 if g.type()!=QgsWkbTypes.PolygonGeometry:
  polygons=[part for part in g.asGeometryCollection() if part.type()==QgsWkbTypes.PolygonGeometry]
  assert polygons,r['building_id'];g=QgsGeometry.unaryUnion(polygons)
 g.convertToMultiType();f=QgsFeature(out.fields());f.setGeometry(g);f.setAttributes(vals);out.dataProvider().addFeatures([f]);rows.append(dict(zip([n for n,t in fields],vals),ward_overlaps=json.dumps(over,ensure_ascii=False)))
assert out.featureCount()==len(reviews),(out.featureCount(),len(reviews))
save(out,'far26_review')
with (OUT/'FAR26_Official_Review.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'FAR26_Official_Review.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
summary={'count':len(rows),'classes':{k:sum(r['review_class']==k for r in rows) for k in sorted({r['review_class'] for r in rows})},'threshold':'significant overlap >=1 m2 AND >=0.5% of building footprint; all raw overlaps retained','source_url':'https://tokei-gis2.chiyodatoshikei.jp/server/rest/services/Map_services/youtochiiki/MapServer','source_crs':'EPSG:2451, official service transforms to requested EPSG:6677','download_date':'2026-10-14','website_year':'current service; individual decision date not exposed','official_map_document_date':'2026-03-31','legal_scope':'building projection intersection; legal site/parcel and frontage constraints remain pending','original_baseline_unchanged':True}
(OUT/'Planning_Review_Quality.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
# Read the project only after all GeoPackage writes have closed.
project.read(str(ROOT/'05_QGIS/Projects/Kajicho_Public_Baseline_2026-10-14.qgz'))
for layer in project.mapLayers().values():
 uri=layer.source()
 if 'Kajicho_Public_Baseline.gpkg' in uri:layer.setDataSource(str(GPKG)+uri[uri.index('|'):],layer.name(),'ogr')
project.setFileName(str(ROOT/'05_QGIS/Projects/Kajicho_CFD_Baseline_2026-10-14.qgz'));project.setFilePathStorage(Qgis.FilePathType.Relative);project.setTitle('Kajicho | CFD baseline and official planning review')
group=project.layerTreeRoot().insertGroup(0,'Official planning | 千代田区公式境界')
for key in saved:
 target=QgsVectorLayer(str(GPKG)+'|layername='+key,key,'ogr');assert target.isValid(),target.error().summary();project.addMapLayer(target,False);node=group.addLayer(target);node.setItemVisibilityChecked(key in ['ward_use_far','far26_review'])
assert project.write();print(json.dumps(summary,ensure_ascii=False),flush=True)
