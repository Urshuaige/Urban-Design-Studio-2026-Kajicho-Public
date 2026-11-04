#!/usr/bin/env python3
"""Write six portable raster layers from the paired native-field export."""
import json,sys
from pathlib import Path
import numpy as np
from osgeo import gdal,osr
from qgis.core import QgsApplication,QgsProject,QgsRasterLayer,QgsRasterShader,QgsColorRampShader,QgsSingleBandPseudoColorRenderer,QgsRectangle
from qgis.PyQt.QtGui import QColor
R=Path(__file__).resolve().parents[1];D=R/'04_Data/Ready/CFD_Baseline_2026-10-14';W=R/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data';meta=json.loads((W/'city.json').read_text())['meta'];result=json.loads((D/'CFD_Field_Results.json').read_text());nx,ny=meta['nx'],meta['ny'];iteration=result['iteration']
p=[np.fromfile(D/f'cfd-{name}.bin',dtype='<f4').reshape(ny,nx,5) for name in ['baseline','retrofit']];valid=(p[0][:,:,4]>0)&(p[1][:,:,4]>0);wind=[np.linalg.norm(x[:,:,:3],axis=2) for x in p];heat=[x[:,:,3] for x in p]
data=[('wind_existing',wind[0],'Wind · Existing / m/s',0,4),('wind_retrofit',wind[1],'Wind · Cool roofs / m/s',0,4),('wind_change',wind[1]-wind[0],'Wind change / m/s',-.5,.5),('heat_existing',heat[0],'Roof heat · Existing / K',0,.5),('heat_retrofit',heat[1],'Roof heat · Cool roofs / K',0,.5),('heat_change',heat[1]-heat[0],'Roof heat change / K',-.05,.05)]
out=D/'CFD_Rasters';out.mkdir(exist_ok=True);crs=osr.SpatialReference();crs.ImportFromEPSG(6677);left=meta['x0']+meta['origin_epsg6677'][0];top=meta['y0']+meta['origin_epsg6677'][1]+ny*meta['dx']
for name,a,label,lo,hi in data:
 ds=gdal.GetDriverByName('GTiff').Create(str(out/(name+'.tif')),nx,ny,1,gdal.GDT_Float32,options=['COMPRESS=DEFLATE','PREDICTOR=3','TILED=YES']);ds.SetGeoTransform((left,meta['dx'],0,top,0,-meta['dx']));ds.SetProjection(crs.ExportToWkt());ds.SetMetadata({'DESCRIPTION':label,'STATUS':'Intermediate; convergence and heat balance pending','ITERATION':str(iteration),'SOURCE':'OpenFOAM 2412 paired native export; nearest resampling','VELOCITY':'3D magnitude; plan arrows use horizontal direction'});b=ds.GetRasterBand(1);b.SetNoDataValue(-9999);b.WriteArray(np.where(valid,a,-9999)[::-1]);b.SetUnitType('m/s' if name.startswith('wind') else 'K');b.FlushCache();ds=None
app=QgsApplication([],False);app.initQgis();project=QgsProject.instance();qgz=R/'05_QGIS/Projects/Kajicho_CFD_Baseline_2026-10-14.qgz';assert project.read(str(qgz));root=project.layerTreeRoot();old=root.findGroup('Kajicho wind + heat / Intermediate')
if old:
 for node in list(old.findLayers()):project.removeMapLayer(node.layerId())
 root.removeChildNode(old)
group=root.insertGroup(0,'Kajicho wind + heat / Intermediate')
for i,(name,a,label,lo,hi) in enumerate(data):
 layer=QgsRasterLayer(str(out/(name+'.tif')),label+f' · Iteration {iteration}');assert layer.isValid(),name
 ramp=QgsColorRampShader();ramp.setColorRampType(QgsColorRampShader.Interpolated)
 palette=[(lo,'#23333c'),(hi*.33,'#488999'),(hi*.67,'#e5d59e'),(hi,'#d98052')] if lo==0 else [(lo,'#55b0d1'),(0,'#eeeeea'),(hi,'#df956b')]
 ramp.setColorRampItemList([QgsColorRampShader.ColorRampItem(v,QColor(c),str(v)) for v,c in palette]);shader=QgsRasterShader();shader.setRasterShaderFunction(ramp);renderer=QgsSingleBandPseudoColorRenderer(layer.dataProvider(),1,shader);renderer.setClassificationMin(lo);renderer.setClassificationMax(hi);layer.setRenderer(renderer);project.addMapLayer(layer,False);node=group.addLayer(layer);node.setItemVisibilityChecked(i==0)
extent=QgsRectangle(left,top-ny*meta['dx'],left+nx*meta['dx'],top);extent.scale(1.08);project.viewSettings().setDefaultViewExtent(__import__('qgis.core',fromlist=['QgsReferencedRectangle']).QgsReferencedRectangle(extent,project.crs()));assert project.write(str(qgz))
layers=list(project.mapLayers().values());quality={'layers':len(layers),'valid_layers':sum(x.isValid() for x in layers),'base_vector_layers':45,'cfd_raster_layers':6,'iteration':iteration,'crs':'EPSG:6677','paths':'relative project paths; preserve folder tree','raster_grid':'5 m; north-up GeoTIFF; paired valid mask; -9999 nodata','scientific_status':'intermediate, pending convergence and thermal balance'};assert quality['layers']==51 and quality['valid_layers']==51;(D/'QGIS_Quality.json').write_text(json.dumps(quality,indent=2));print(json.dumps(quality));project.clear();app.exitQgis()
