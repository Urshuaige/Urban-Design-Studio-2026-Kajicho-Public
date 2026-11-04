import json,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];D=R/'04_Data/Ready/Simulation_Demo';O=D/'V2/wind';O.mkdir(parents=True,exist_ok=True)
c=json.loads((R/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data/city.json').read_text());m=c['meta'];mask=np.load(str(D/'grid.npz'))['mask'];ny,nx=mask.shape
y,x=np.mgrid[:ny,:nx];xx=m['x0']+(x+.5)*m['dx'];yy=m['y0']+(y+.5)*m['dx']
scenarios=[(0,4)]+[(n,r) for n in [24,48] for r in [2,4,6]]
for count,radius in scenarios:
 drag=np.zeros_like(xx)
 for t in c['trees'][:count]:drag[((xx-t['x'])**2+(yy-t['y'])**2<radius**2)&~mask.astype(bool)]=.006
 with (O/f'input_{count}_{radius}.txt').open('w') as f:f.write(f'{nx} {ny}\n'+' '.join(map(str,mask.ravel()))+'\n'+' '.join(map(str,drag.ravel()))+'\n')
lines=['#!/usr/bin/env bash','set -euo pipefail','g++ -O3 -std=c++17 demo_wind_v2.cpp -o demo_wind_v2']
for bearing in range(0,360,45):
 for count,radius in scenarios:
  key=f'{bearing}_{count}_{radius}';lines.append(f'(ulimit -v 1048576; ulimit -t 120; ./demo_wind_v2 input_{count}_{radius}.txt wind_{key}.json {bearing} {int(count>0)} > wind_{key}.log)');lines.append(f'echo completed_{key}')
(O/'run.sh').write_text('\n'.join(lines)+'\n');print('56 cases; 7 masks prepared')
