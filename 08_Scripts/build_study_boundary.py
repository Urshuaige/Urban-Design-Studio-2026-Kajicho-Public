#!/usr/bin/env python3
"""Keep the two Figure 5 source-stroke traces; never alter them to retain buildings."""
import argparse,json,csv,hashlib
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import shape,mapping
from shapely.ops import transform

def main():
 p=argparse.ArgumentParser();p.add_argument('--task-root',type=Path,required=True);a=p.parse_args()
 root=a.task_root;out=root/'team/06_Outputs/Study_Area_2026-10-18';out.mkdir(parents=True,exist_ok=True)
 original=json.loads((root/'registration/course_boundaries_6677.geojson').read_text())
 features=[];register=[]
 for source_id,sid in [('secondary_brief','study_area'),('primary_brief','primary_brief')]:
  f=next(f for f in original['features'] if f['properties']['id']==source_id)
  props=dict(f['properties']);g=shape(f['geometry']);assert g.is_valid
  geom=f['geometry'];digest=hashlib.sha256(json.dumps(geom,separators=(',',':')).encode()).hexdigest()
  props.update(id=sid,source_scope_id=source_id,geometry_sha256=digest,boundary_revision='2026-10-18-brief-figure5',
   authority='Official Theme B brief p.4 Figure 5 source stroke. Raster reference; geographic registration uncertainty retained.',
   basis='Figure 5 dashed secondary outline' if sid=='study_area' else 'Figure 5 solid primary outline',
   line_style='dash' if sid=='study_area' else 'solid',
   selection_rule='Complete original source building footprints covered by the fixed registered trace; exterior and crossing buildings remain context only. Geometry is not clipped. Boundary sensitivity is reported.',
   name={'en':'Kanda–Nihonbashi wider area (approx.)','zh':'神田—日本桥外围区（概略）','ja':'神田・日本橋の周辺区域（概略）'} if sid=='study_area' else {'en':'Kajicho 1 & 2 primary area','zh':'鍛冶町一、二丁目重点区','ja':'鍛冶町一・二丁目の重点区域'},
   source_outline_role='Two official study levels overlaid in one common map view. No poster, census boundary or inferred operational outline.',
   construction_method='Source-pixel vertices transformed with the recorded affine matrix; no road snapping, building expansion, straight trimming or branch interpretation.',
   date='2026-10-18',crs='EPSG:6677')
  # Independent reconstruction from source pixels is a prerequisite for every release.
  m=props['registration']['affine_matrix']
  reconstructed=[[x*m[0][0]+y*m[1][0]+m[2][0],x*m[0][1]+y*m[1][1]+m[2][1]] for x,y in props['source_pixel_vertices']]
  assert max(abs(v-w) for p,q in zip(reconstructed,geom['coordinates'][0]) for v,w in zip(p,q))<1e-7
  features.append({'type':'Feature','properties':props,'geometry':geom})
  register.append({'scope':sid,'source_scope':source_id,'line_style':props['line_style'],'source':'Theme B brief p.4 Figure 5','area_ha':g.area/10000,'registration_rmse_m':props['registration']['rmse_m'],'screening_band_m':props['registration']['uncertainty_m'],'geometry_sha256':digest})
 payload={'type':'FeatureCollection','crs':{'type':'name','properties':{'name':'EPSG:6677'}},'features':features}
 (out/'study_boundary_6677.geojson').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
 tr=Transformer.from_crs(6677,4326,always_xy=True).transform
 (out/'study_boundary.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[dict(f,geometry=mapping(transform(tr,shape(f['geometry'])))) for f in features]},ensure_ascii=False,indent=2)+'\n')
 with (out/'boundary_edges.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(register[0]));w.writeheader();w.writerows(register)
 print(json.dumps(register,ensure_ascii=False))
if __name__=='__main__':main()

