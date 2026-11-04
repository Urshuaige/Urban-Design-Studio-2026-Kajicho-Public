"""Flat-ground geometric shadow sampling; no air-temperature estimate."""
import json, math
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, Point, shape
from shapely.ops import unary_union
from shapely.prepared import prep
from shapely.affinity import translate, scale, rotate
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'04_Data/Ready/Simulation_Demo'; D=ROOT/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data'
data=json.loads((D/'city.json').read_text());m=data['meta']; core=prep(shape(data['boundary'])); pol=[Polygon(b['rings'][0],b['rings'][1:]) for b in data['buildings']]
grid=np.load(str(R/'grid.npz'));mask=grid['mask']; nx,ny=m['nx'],m['ny']; points=[Point(m['x0']+(i+.5)*m['dx'],m['y0']+(j+.5)*m['dx']) for j in range(ny) for i in range(nx)]
open_core=np.array([core.covers(p) for p in points])&~mask.ravel().astype(bool);out=[]
for sun in json.loads((R/'sun_positions.json').read_text()):
    alt,az=sun['altitude'],sun['azimuth']; sx,sy=math.sin(az)/math.tan(alt),math.cos(az)/math.tan(alt); shadows=[]
    for b,p in zip(data['buildings'],pol):
        dx,dy=sx*b['h'],sy*b['h']; shadows.extend([p,translate(p,dx,dy)])
        for a,c in zip(b['rings'][0][:-1],b['rings'][0][1:]): shadows.append(Polygon([a,c,[c[0]+dx,c[1]+dy],[a[0]+dx,a[1]+dy]]))
    before=prep(unary_union(shadows)); tree=[]
    for t in data['trees']:
        e=scale(Point(0,0).buffer(t['r'],resolution=24),1/math.sin(alt),1)
        e=rotate(e,math.degrees(math.atan2(sy,sx)),origin=(0,0));tree.append(translate(e,t['x']+sx*t['h'],t['y']+sy*t['h']))
    tree_shadow=prep(unary_union(tree));a=np.array([before.covers(p) for p in points],dtype=np.uint8);b=np.maximum(a,np.array([tree_shadow.covers(p) for p in points],dtype=np.uint8))
    out.append(dict(**sun,before=a.tolist(),after=b.tolist(),before_fraction=float(a[open_core].mean()),after_fraction=float(b[open_core].mean()),open_core_cells=int(open_core.sum())))
    print(sun['hour'],out[-1]['before_fraction'],out[-1]['after_fraction'],flush=True)
(D/'shade.json').write_text(json.dumps(dict(method='2.5D extruded buildings and spherical proposed tree crowns; flat ground; 5 m cell-center sampling; existing vegetation not inventoried',date='2026-07-15',timezone='Asia/Tokyo',samples=out),separators=(',',':')))
