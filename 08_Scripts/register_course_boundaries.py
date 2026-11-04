#!/usr/bin/env python3
"""Register separately traced official outlines. Outputs stay on the selected host.

Pixel convention: x right, y down, origin at upper-left of original raster.
Brief pixels use PDF page 4 /Im8 (917 x 1495), excluding added labels.
Poster pixels use full 2026_Board_01.png (4961 x 7016).
"""
import argparse, json
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, mapping
from shapely.ops import transform
from pyproj import Transformer

CONTROL_XY = np.array([
 [-5690.995051723813,-33749.83993563471],
 [-5250.270550754818,-33772.84055002165],
 [-5548.128027964524,-34290.42172377812],
 [-5296.374687292489,-34200.074153934875],
 [-5462.715752102546,-34544.06082370612],
 [-5217.080637092027,-34448.96448885104],
])
CONTROL_NAMES = [
 'Chuo Street / Yasukuni-dori', 'Showa-dori / Yasukuni-dori',
 'Chuo Street / Kanda Kanamono-dori', 'Showa-dori / Kanda Kanamono-dori',
 'Chuo Street / Edo-dori', 'Showa-dori / Edo-dori',
]
BRIEF_CONTROL_PIXELS = np.array([[225,249],[750,273],[389,881],[707,778],[494,1184],[772,1081]])
POSTER_CONTROL_PIXELS = np.array([[4227,1993],[4629,2007],[4403,2462],[4625,2375],[4474,2690],[4693,2613]])

# Stroke centers and visible bends, traced independently before geographic registration.
PRIMARY_PIXELS = [[403,392],[344,413],[343,505],[320,577],[279,682],
 [249,756],[221,829],[198,936],[191,986],[146,1116],[590,936],[403,392]]
SECONDARY_PIXELS = [[463,192],[798,203],[819,281],[813,333],[798,454],
 [803,579],[905,848],[831,878],[890,1085],[149,1375],[90,1290],
 [146,1116],[191,986],[198,936],[221,829],[249,756],[279,682],
 [320,577],[343,505],[344,413],[403,392],[463,192]]
POSTER_PIXELS = [[4437,1932],[4662,1914],[4689,2048],[4668,2074],
 [4668,2198],[4734,2428],[4678,2451],[4736,2615],[4197,2812],
 [4102,2727],[4174,2647],[4437,1932]]

def fit(pixels, uncertainty):
 x=np.column_stack([pixels,np.ones(len(pixels))])
 matrix=np.linalg.lstsq(x,CONTROL_XY,rcond=None)[0]
 residual=np.linalg.norm(x@matrix-CONTROL_XY,axis=1)
 leave=[]
 for i in range(len(pixels)):
  select=np.arange(len(pixels))!=i
  m=np.linalg.lstsq(x[select],CONTROL_XY[select],rcond=None)[0]
  leave.append(float(np.linalg.norm(x[i]@m-CONTROL_XY[i])))
 return {'method':'Least-squares affine; no snapping to census edges',
  'pixel_origin':'upper-left; x right; y down',
  'formula':'[E,N] = [pixel_x,pixel_y,1] @ affine_matrix',
  'affine_matrix':matrix.tolist(),'rmse_m':float(np.sqrt(np.mean(residual**2))),
  'max_residual_m':float(max(residual)),'leave_one_out_errors_m':leave,
  'uncertainty_m':uncertainty,'uncertainty_definition':'Conservative cartographic screening band; includes leave-one-control-out error, source stroke width and manual point reading. Not a statistical confidence interval.',
  'control_source':'OSM source snapshot 2026-10-13, common foundation roads; average mapped carriageway intersections when divided',
  'controls':[{'name':n,'pixel':p.tolist(),'epsg6677':q.tolist(),'residual_m':float(r)} for n,p,q,r in zip(CONTROL_NAMES,pixels,CONTROL_XY,residual)]}

def build():
 brief=fit(BRIEF_CONTROL_PIXELS,25)
 poster=fit(POSTER_CONTROL_PIXELS,45)
 to_wgs=Transformer.from_crs(6677,4326,always_xy=True).transform
 features=[]
 for key,label,pixels,reg,source,approx in [
  ('primary_brief','Kajicho 1 & 2 — brief primary area',PRIMARY_PIXELS,brief,'Theme B official brief, page 4, Figure 5 solid black outline',False),
  ('secondary_brief','Kanda–Nihonbashi — approximate secondary area',SECONDARY_PIXELS,brief,'Theme B official brief, page 4, Figure 5 dashed black outline',True),
  ('poster_blue','Kanda–Nihonbashi — 2026 poster blue outline',POSTER_PIXELS,poster,'2026 official recruitment poster blue Theme B outline',True),
 ]:
  coords=np.column_stack([pixels,np.ones(len(pixels))])@np.array(reg['affine_matrix'])
  poly=Polygon(coords)
  if not poly.is_valid:raise ValueError(key+' invalid trace')
  props={'id':key,'name':label,'source':source,'source_pixel_vertices':pixels,
   'source_raster':'PDF page 4 /Im8' if key!='poster_blue' else '2026_Board_01.png',
   'source_image_size':[917,1495] if key!='poster_blue' else [4961,7016],
   'source_original':'01_Course/2026_Briefs/2026_Theme_B_Official_Brief.pdf' if key!='poster_blue' else '01_Course/2026_Briefs/2026_Board_01.png',
   'source_url':'https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view' if key!='poster_blue' else 'https://www.due.t.u-tokyo.ac.jp/english/wp-content/uploads/sites/2/2026/09/urbandesignstudio2026_a2.png',
   'source_document_year':2026,'download_date':'2026-10-13',
   'approximate':approx,'boundary_status':'Cartographic source-stroke trace; geographic registration uncertainty retained',
   'outline_definition':'Stroke center, preserving visible bends; separate traces by source',
   'registration':reg,'area_ha':poly.area/10000,'bounds_wgs84':list(transform(to_wgs,poly).bounds)}
  features.append({'type':'Feature','geometry':mapping(poly),'properties':props})
 return {'type':'FeatureCollection','name':'Official course outline traces 2026-10-16',
  'crs':{'type':'name','properties':{'name':'EPSG:6677'}},
  'features':features,'method_note':'The brief supplies the primary and approximate secondary study levels. The poster is registered independently. Neither raster provides surveyed legal boundary coordinates. Census geometry is retained only for comparison. No CFD is recalculated.'}

def qa(data, source_dir, output):
 from PIL import Image,ImageDraw,ImageFont
 import subprocess,tempfile
 output.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='course-source-',dir=output) as temp:
  prefix=Path(temp)/'p4'
  subprocess.run(['pdfimages','-f','4','-l','4','-png',str(source_dir/'2026_Theme_B_Official_Brief.pdf'),str(prefix)],check=True)
  candidates=list(Path(temp).glob('p4-*.png'))
  brief=next(Image.open(p).convert('RGB') for p in candidates if Image.open(p).size==(917,1495))
 source_images={
  'brief':brief,
  'poster':Image.open(source_dir/'2026_Board_01.png').convert('RGB')}
 font=ImageFont.load_default()
 for kind,ids,crop in [('brief',['primary_brief','secondary_brief'],None),('poster',['poster_blue'],(4000,1800,4800,2900))]:
  im=source_images[kind];d=ImageDraw.Draw(im)
  for feature in data['features']:
   p=feature['properties']
   if p['id'] not in ids:continue
   color='#ef3c78' if p['id']=='primary_brief' else '#ff7800'
   vertices=[tuple(q) for q in p['source_pixel_vertices']]
   d.line(vertices,fill=color,width=2)
   for i,(x,y) in enumerate(vertices[:-1]):
    d.ellipse((x-3,y-3,x+3,y+3),fill=color);d.text((x+4,y+3),str(i+1),fill=color,font=font)
  reg=next(f['properties']['registration'] for f in data['features'] if f['properties']['id'] in ids)
  for i,c in enumerate(reg['controls']):
   x,y=c['pixel'];d.ellipse((x-6,y-6,x+6,y+6),outline='#c500e8',width=2)
   d.text((x+9,y-9),f"C{i+1}: {c['residual_m']:.1f} m",fill='#8f00aa',font=font)
  if crop:im=im.crop(crop)
  panel=Image.new('RGB',(im.width,im.height+80),'white');panel.paste(im,(0,80));dr=ImageDraw.Draw(panel)
  dr.text((10,10),kind.upper()+' source trace and road controls',fill='black',font=font)
  dr.text((10,30),f"Affine RMSE {reg['rmse_m']:.1f} m; screening band {reg['uncertainty_m']} m; stroke-center trace",fill='black',font=font)
  dr.text((10,50),'Pixel origin: original raster upper-left, x right, y down. Orange: secondary/poster; pink: primary.',fill='black',font=font)
  panel.save(output/f'{kind}_registration.png')

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);ap.add_argument('--sources',type=Path);ap.add_argument('--qa',type=Path);a=ap.parse_args()
 data=build();encoded=json.dumps(data,ensure_ascii=False,indent=2)
 if a.output:a.output.write_text(encoded+'\n')
 else:print(encoded)
 if a.qa:qa(data,a.sources,a.qa)
