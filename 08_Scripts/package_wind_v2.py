import json
from pathlib import Path
import numpy as np
from shapely.geometry import shape,Point
from shapely.prepared import prep
R=Path(__file__).resolve().parents[1];D=R/'04_Data/Ready/Simulation_Demo';I=D/'V2/wind';O=R/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data';(O/'wind-v2').mkdir(exist_ok=True)
c=json.loads((O/'city.json').read_text());m=c['meta'];mask=np.load(str(D/'grid.npz'))['mask'].ravel().astype(bool);core=prep(shape(c['boundary']))
inside=np.array([core.covers(Point(m['x0']+(i+.5)*m['dx'],m['y0']+(j+.5)*m['dx'])) for j in range(m['ny']) for i in range(m['nx'])])&~mask
cases=[];refs={}
for bearing in range(0,360,45):
 for count,radius in [(0,4)]+[(n,r) for n in [24,48] for r in [2,4,6]]:
  key=f'{bearing}_{count}_{radius}';p=json.loads((I/f'wind_{key}.json').read_text());u=np.array(p.pop('u'));v=np.array(p.pop('v'));speed=np.hypot(u,v)
  assert np.isfinite(u).all() and np.isfinite(v).all() and np.max(speed[mask])==0
  assert abs(p['mass_drift'])<1e-8 and p['last_relative_change_500']<1e-4 and .8<p['rho_min']<=p['rho_max']<1.2
  if count==0:refs[bearing]=float(np.percentile(speed[~mask],90));baseline=speed.copy()
  ref=refs[bearing];np.concatenate([u/ref,v/ref]).astype('<f4').tofile(str(O/'wind-v2'/f'{key}.bin'))
  cases.append(dict(key=key,bearing=bearing,tree_count=count,radius_m=radius,url=f'data/wind-v2/{key}.bin',core_mean=float(speed[inside].mean()/ref),relative_mean_change_pct=float((speed[inside].mean()/baseline[inside].mean()-1)*100),reference_lattice=ref,numerics=p))
(O/'wind-v2.json').write_text(json.dumps(dict(nx=m['nx'],ny=m['ny'],array_type='little-endian Float32; first N east velocity then N north velocity; normalized by baseline 90th percentile per bearing',cases=cases,host='iis-lab',drag=.006,method='2D D2Q9 BGK, periodic body forcing; 4500 steps, last 500 average; no m/s calibration',all_checks_passed=True),indent=2))
print('PASS',len(cases),'cases',min(z['relative_mean_change_pct'] for z in cases),max(z['relative_mean_change_pct'] for z in cases))
