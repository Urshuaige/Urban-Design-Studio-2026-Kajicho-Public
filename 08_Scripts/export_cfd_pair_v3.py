#!/usr/bin/env python3
"""Export a common saved pedestrian plane to a compact demo grid.
Native solver values stay in the case; this export is nearest-point sampling.
"""
import sys,json,csv,re
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely import contains_xy
B=Path(sys.argv[1]);OUT=B/'outputs';OUT.mkdir(exist_ok=True)
city=json.loads((B/'inputs/city.json').read_text());meta=city['meta'];N=meta['nx']*meta['ny']
xx,yy=np.meshgrid(meta['x0']+(np.arange(meta['nx'])+.5)*meta['dx'],meta['y0']+(np.arange(meta['ny'])+.5)*meta['dx']);xy=np.column_stack((xx.ravel(),yy.ravel()))
core=shape(city['boundary']);obstacles=unary_union([shape(f['geometry']) for f in json.loads((B/'inputs/cfd_buildings_local.geojson').read_text())['features'] if f['properties']['height_m']>1.5])
open_ground=~contains_xy(obstacles,xy[:,0],xy[:,1]);core_points=contains_xy(core,xy[:,0],xy[:,1])
def times(name):
 d=B/'cases'/name/'postProcessing/pedestrian';return {float(p.name):p for p in d.iterdir() if p.is_dir() and re.fullmatch(r'\d+(?:\.\d+)?',p.name)}
dirs=[times(name) for name in ['baseline','retrofit']];common=set(dirs[0])&set(dirs[1]);assert common,'No common saved surface yet';iteration=max(common)
packs=[];details=[]
for i,name in enumerate(['baseline','retrofit']):
 paths=list(dirs[i][iteration].rglob('*.raw'))
 def field_file(field):
  matches=[p for p in paths if field in re.split(r'[_.]',p.stem)];assert len(matches)==1,(field,[str(p) for p in paths]);return matches[0]
 tfile=field_file('T');ufile=field_file('U');a=np.loadtxt(tfile,comments='#',ndmin=2);u=np.loadtxt(ufile,comments='#',ndmin=2)
 assert a.shape[1]==4 and u.shape[1]==6,(a.shape,u.shape)
 crop=(a[:,0]>=meta['x0']-5)&(a[:,0]<=meta['x0']+meta['nx']*meta['dx']+5)&(a[:,1]>=meta['y0']-5)&(a[:,1]<=meta['y0']+meta['ny']*meta['dx']+5)
 ucrop=(u[:,0]>=meta['x0']-5)&(u[:,0]<=meta['x0']+meta['nx']*meta['dx']+5)&(u[:,1]>=meta['y0']-5)&(u[:,1]<=meta['y0']+meta['ny']*meta['dx']+5)
 a=a[crop];u=u[ucrop];dist,idx=cKDTree(a[:,:2]).query(xy);udist,uidx=cKDTree(u[:,:2]).query(xy)
 limit=np.where(core_points,.75,2.0);valid=open_ground&(dist<=limit)&(udist<=limit);deltaT=a[idx,3]-311.55;velocity=u[uidx,3:6]
 assert np.all(np.isfinite(deltaT[valid])) and np.all(np.isfinite(velocity[valid]))
 pack=np.column_stack((velocity,deltaT,valid)).astype('<f4');pack[~valid,:4]=0;pack.tofile(OUT/f'cfd-{name}.bin');packs.append(pack)
 details.append({'case':name,'native_temperature_file':str(tfile.relative_to(B)),'native_velocity_file':str(ufile.relative_to(B)),'native_rows_in_crop':len(a),'maximum_sample_distance_m':float(dist[valid].max()),'core_distance_limit_m':.75,'core_maximum_sample_distance_m':float(dist[valid&core_points].max()),'valid_grid_points':int(valid.sum())})
paired=(packs[0][:,4]>0)&(packs[1][:,4]>0);mask=paired&core_points;assert mask.sum()>100
statistics={}
for label,values in [('heat',[p[:,3].astype(float) for p in packs]),('wind',[np.linalg.norm(p[:,:3].astype(float),axis=1) for p in packs])]:
 statistics[label]={'baseline':float(values[0][mask].mean()),'retrofit':float(values[1][mask].mean()),'mean_difference':float((values[1][mask]-values[0][mask]).mean()),'difference_p05':float(np.quantile((values[1][mask]-values[0][mask]),.05)),'difference_p95':float(np.quantile((values[1][mask]-values[0][mask]),.95))}
balances=[]
for name in ['baseline','retrofit']:
 path=B/'cases'/name/'postProcessing/roofHeatBalance.csv';a=np.loadtxt(path,delimiter=',',ndmin=2);a=a[a[:,0]<=iteration];row=a[-1];balances.append({'case':name,'diagnostic_iteration':int(row[0]),'roof_input_W':float(row[1]),'other_outward_heat_W':float(row[2]),'net_outward_heat_W':float(row[3]),'net_volume_flux_m3_s':float(row[4]),'heated_roof_area_m2':float(row[5]),'relative_heat_imbalance':float(abs(row[3])/max(1,abs(row[1])))})
quality=json.loads((B/'inputs/mesh_quality.json').read_text())
result={'schema_version':1,'mesh_selection':json.loads((B/'inputs/mesh_selection.json').read_text()),'status':'solving','host':'mdx1','snapshot_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'iteration':int(iteration),'fields':{'files':['data/cfd-baseline.bin','data/cfd-retrofit.bin'],'components':['Ux_m_s','Uy_m_s','Uz_m_s','roof_temperature_contribution_K','valid'],'format':'little-endian Float32, row-major south to north','temperature_component':'excess_K','sample_height_m':1.5,'grid_spacing_m':meta['dx'],'core_common_open_points':int(mask.sum()),'statistics':statistics},'checks':{'mesh':'partial','convergence':'pending','heat_balance':'passed' if all(b['relative_heat_imbalance']<.01 for b in balances) else 'pending','mesh_sensitivity':'pending','domain_sensitivity':'pending','inlet_preservation':'pending'},'numerical':{'mesh':quality,'heat_balance':balances,'sampling':details,'temperature_precision':'subtract TRef in Float64 before compact Float32 export','interpretation':'saved intermediate iteration; convergence and sensitivity still required'},'scenario':json.loads((B/'inputs/scenario.json').read_text()),'domain':json.loads((B/'inputs/domain.json').read_text())}
(OUT/'CFD_Field_Results.json').write_text(json.dumps(result,indent=2))
with (OUT/'CFD_Pedestrian_Samples.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['x_epsg6677','y_epsg6677','baseline_U_m_s','retrofit_U_m_s','baseline_roof_deltaT_K','retrofit_roof_deltaT_K','delta_roof_deltaT_K','core'])
 for k in np.flatnonzero(paired):w.writerow([xy[k,0]+meta['origin_epsg6677'][0],xy[k,1]+meta['origin_epsg6677'][1],np.linalg.norm(packs[0][k,:3]),np.linalg.norm(packs[1][k,:3]),packs[0][k,3],packs[1][k,3],packs[1][k,3]-packs[0][k,3],int(core_points[k])])
print(json.dumps({'iteration':iteration,'core_points':int(mask.sum()),'statistics':statistics,'heat_balance':balances}),flush=True)
