import json, math, shutil
from pathlib import Path
import numpy as np
from shapely.geometry import shape,Point
from shapely.prepared import prep
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'04_Data/Ready/Simulation_Demo';S=ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon';D=S/'dist/data'
c=json.loads((D/'city.json').read_text());m=c['meta'];mask=np.load(str(R/'grid.npz'))['mask'].ravel().astype(bool);core=prep(shape(c['boundary']))
inside=np.array([core.covers(Point(m['x0']+(i+.5)*m['dx'],m['y0']+(j+.5)*m['dx'])) for j in range(m['ny']) for i in range(m['nx'])])&~mask
cases=[];checks=[]
for direction in range(2):
    reference=None
    for scenario in range(2):
        p=json.loads((R/f'wind_{direction}_{scenario}.json').read_text());u=np.array(p.pop('u'));v=np.array(p.pop('v'));speed=np.hypot(u,v)
        assert np.isfinite(u).all() and np.isfinite(v).all()
        assert np.max(speed[mask])==0 and abs(p['mass_drift'])<1e-8 and p['last_relative_change_500']<1e-4
        assert p['rho_min']>.8 and p['rho_max']<1.2 and p['peak_lattice_speed']<.1
        if reference is None:reference=float(np.percentile(speed[~mask],90))
        p.update(reference_speed_lattice=reference,core_mean=float(speed[inside].mean()/reference),solid_velocity_max=0,checks_passed=True)
        checks.append(p.copy());cases.append(dict(**p,u=np.round(u/reference,5).tolist(),v=np.round(v/reference,5).tolist()))
out=dict(method='D2Q9 BGK + Guo forcing; periodic 2D obstacle field; mean of steps 4001–4500; no physical wind-speed calibration',grid=m,cases=cases)
(D/'wind.json').write_text(json.dumps(out,separators=(',',':')))
validation=dict(status='passed numerical consistency checks; not field validation',host='iis-lab',remote_directory='/mnt/free/shi/urban-design-studio-2026/demo-20261013',resource_limit='one CPU process; 1 GiB address-space limit; 120 CPU seconds per case',checks=checks,grid_cells=int(mask.size),solid_cells=int(mask.sum()),core_open_cells=int(inside.sum()),reference='before-scenario 90th percentile over fluid cells per forcing direction; shared with proposal',limitations=['2D projected obstacles omit vertical bypass and real urban turbulence','periodic boundaries and lattice forcing are educational assumptions','tree drag 0.006 is a scenario parameter, not calibrated vegetation','ground geometry simplified to a plane'])
(D/'validation.json').write_text(json.dumps(validation,indent=2))
host=json.loads((S/'.openai/hosting.json').read_text());host['static']={'directory':'dist'};(S/'.openai/hosting.json').write_text(json.dumps(host,indent=2)+'\n')
for file in ['demo_wind.cpp','prepare_simulation_demo.py','demo_shade.py','finalize_demo_wind.py']:
    (S/'reproduce').mkdir(exist_ok=True);shutil.copy2(ROOT/'08_Scripts'/file,S/'reproduce'/file)
print(json.dumps(validation,indent=2))
