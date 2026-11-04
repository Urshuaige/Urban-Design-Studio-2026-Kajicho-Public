"""Bounded DSM cell-prism ray tracing. Run on IIS using supplied input directory.

One CPU, one GiB address space, 120 CPU seconds. External timeout bounds wall time.
All grid rows advance north. Cell centres sample a flat ground plane.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import resource, time, json, math, hashlib, sys
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
resource.setrlimit(resource.RLIMIT_CPU,(120,120))
if hasattr(os,'sched_getaffinity'):
    os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
import numpy as np

work=Path(sys.argv[1] if len(sys.argv)>1 else '.')
started=time.monotonic()
city=json.loads((work/'city.json').read_text()); meta=city['meta']
sun=json.loads((work/'shade-sun.json').read_text())
old=json.loads((work/'shade-v1.json').read_text())
source=json.loads((work/'plateau_buildings_6677.geojson').read_text())
grid=np.load(str(work/'grid.npz'))
height=grid['height'].astype(np.float64); solid=grid['mask'].astype(bool)
ny,nx=height.shape; dx=meta['dx']; x0,y0=meta['x0'],meta['y0']
assert (nx,ny)==(184,220)
assert np.isfinite(height).all() and np.all(height>=0)
assert np.array_equal(height>0,solid)
xx,yy=np.meshgrid(x0+(np.arange(nx)+.5)*dx,y0+(np.arange(ny)+.5)*dx)
X,Y=xx.ravel(),yy.ravel()

def ring_covers(x,y,ring):
    """Even-odd ring rule with explicit boundary inclusion."""
    ring=np.asarray(ring,dtype=float)
    inside=np.zeros(x.shape,dtype=bool); boundary=inside.copy()
    for a,b in zip(ring[:-1],ring[1:]):
        ax,ay=a;bx,by=b
        vx,vy=bx-ax,by-ay
        if vx*vx+vy*vy<1e-20:continue
        cross=(x-ax)*vy-(y-ay)*vx
        boundary|=(abs(cross)<1e-8)&((x-ax)*(x-bx)+(y-ay)*(y-by)<=1e-8)
        crossing=(ay>y)!=(by>y)
        if abs(vy)>1e-15:inside^=crossing&(x<(vx*(y-ay)/vy+ax))
    return inside|boundary

def poly_covers(x,y,rings):
    use=ring_covers(x,y,rings[0])
    for hole in rings[1:]:use&=~ring_covers(x,y,hole)
    return use

def geometry_covers(x,y,g):
    result=np.zeros(x.shape,dtype=bool)
    polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
    for rings in polygons:result|=poly_covers(x,y,rings)
    return result

core_ground=geometry_covers(X,Y,city['boundary']).reshape(ny,nx)&~solid
assert core_ground.sum()==2830,('core ground changed',int(core_ground.sum()))

# Original precision coordinates reproduce the existing cell-centre raster.
# The city JSON retains which buildings belong to the proposal core.
lookup={b['id']:b for b in city['buildings']}
ox,oy=meta['origin_epsg6677']; core_height=np.zeros_like(height); other_height=np.zeros_like(height)
for feature in source['features']:
    b=lookup[feature['properties']['id']]
    rings=[[[x-ox,y-oy] for x,y in ring] for ring in feature['geometry']['coordinates']]
    pts=np.asarray(rings[0]); xmin,ymin=pts.min(axis=0); xmax,ymax=pts.max(axis=0)
    valid=(X>=xmin)&(X<=xmax)&(Y>=ymin)&(Y<=ymax)
    indices=np.flatnonzero(valid)
    if not len(indices):continue
    selected=indices[poly_covers(X[indices],Y[indices],rings)]
    target=core_height if b['core'] else other_height
    flat=target.ravel();flat[selected]=np.maximum(flat[selected],b['h'])
reproduced=np.maximum(core_height,other_height)
raster_diff=np.abs(reproduced-height)
assert np.array_equal(reproduced>0,solid)
assert raster_diff.max()<1e-4,float(raster_diff.max())
# Source float32 rounding is retained exactly at factor=1.
# Adjustment is applied only where a core building supplies height.
variants={f:(height if f==1 else np.maximum(core_height*f,other_height)) for f in [.75,1,1.25,1.5]}

def trace(h,altitude,azimuth):
    if altitude<=0:
        return np.ones((ny,nx),dtype=np.uint8),0,True
    vx,vy=-math.sin(azimuth),-math.cos(azimuth) # ray towards sun
    stepx=1 if vx>=0 else -1;stepy=1 if vy>=0 else -1
    tx=dx/(2*abs(vx)) if abs(vx)>1e-14 else math.inf
    ty=dx/(2*abs(vy)) if abs(vy)>1e-14 else math.inf
    deltax=2*tx;deltay=2*ty;ix=iy=0; count=0
    shadow=h>0; maxdist=float(h.max())/math.tan(altitude)
    while min(tx,ty)<maxdist:
        entry=min(tx,ty)
        same=math.isclose(tx,ty,rel_tol=1e-12,abs_tol=1e-10)
        if same:ix+=stepx;iy+=stepy;tx+=deltax;ty+=deltay
        elif tx<ty:ix+=stepx;tx+=deltax
        else:iy+=stepy;ty+=deltay
        if abs(ix)>=nx or abs(iy)>=ny:break
        target_x=slice(max(0,-ix),min(nx,nx-ix)); target_y=slice(max(0,-iy),min(ny,ny-iy))
        source_x=slice(max(0,ix),min(nx,nx+ix)); source_y=slice(max(0,iy),min(ny,ny+iy))
        shadow[target_y,target_x]|=h[source_y,source_x]>entry*math.tan(altitude)+1e-8
        count+=1
    return shadow.astype(np.uint8),count,False

# Analytic cardinal-direction check: a 20 m raster prism at 45 degrees
# shades four 5 m cell centres beyond its edge, plus its own solid cell.
synthetic=np.zeros_like(height);sj,si=ny//2,nx//2;synthetic[sj,si]=20
expected=np.zeros((ny,nx),dtype=np.uint8);expected[sj-4:sj+1,si]=1
cardinal,_,_=trace(synthetic,math.pi/4,math.pi)
assert np.array_equal(cardinal,expected),'North-sun ray direction/length check failed'
night,_,is_night=trace(synthetic,0,0)
assert is_night and np.all(night==1),'At-horizon handling failed'

catalog=[];arrays=[];monotone_failures=0;noon_comparison=None
for sample in sun['samples']:
    previous=None
    for factor,h in variants.items():
        a,steps,night=trace(h,sample['altitude'],sample['azimuth'])
        if previous is not None:monotone_failures+=int(np.any(a<previous))
        previous=a
        assert a.shape==(ny,nx) and set(np.unique(a)).issubset({0,1})
        item={**sample,'heightFactor':factor,'offset':len(arrays)*nx*ny,'length':nx*ny,
            'coreOpenShadeFraction':float(a[core_ground].mean()),'coreOpenCells':int(core_ground.sum()),
            'raySteps':steps,'atOrBelowHorizon':night}
        catalog.append(item);arrays.append(a)
        if sample['date']=='2026-07-15' and sample['hour']==12 and factor==1:
            reference=next(s for s in old['samples'] if s['hour']==12)
            prior=np.asarray(reference['before'],dtype=np.uint8).reshape(ny,nx)
            noon_comparison={'priorMethod':'geometric polygon projection sampled at grid centres','priorShadeFraction':reference['before_fraction'],'v2ShadeFraction':item['coreOpenShadeFraction'],'differencePercentagePoints':100*(item['coreOpenShadeFraction']-reference['before_fraction']),'coreChangedCells':int(np.count_nonzero(a[core_ground]!=prior[core_ground])),'priorSunAltitudeRadians':reference['altitude'],'v2SunAltitudeRadians':sample['altitude'],'priorSunAzimuthRadians':reference['azimuth'],'v2SunAzimuthRadians':sample['azimuth']}
            matched_sun,_,_=trace(h,reference['altitude'],reference['azimuth'])
            noon_comparison['v2WithPriorSunShadeFraction']=float(matched_sun[core_ground].mean())
            noon_comparison['coreCellsChangedBySunCoordinateDifference']=int(np.count_nonzero(matched_sun[core_ground]!=a[core_ground]))
    print(sample['date'],sample['hour'],[round(x['coreOpenShadeFraction'],4) for x in catalog[-4:]],flush=True)
assert monotone_failures==0,monotone_failures
payload=b''.join(a.tobytes(order='C') for a in arrays)
(work/'shade-v2.bin').write_bytes(payload)
(work/'core-mask.bin').write_bytes(core_ground.astype(np.uint8).tobytes(order='C'))
result={'version':2,'method':'5 m cell-centred building DSM; exact cell-boundary ray traversal to sun through vertical raster prisms; flat ground; no vegetation baked in','binary':'shade-v2.bin','mask':'core-mask.bin','dtype':'uint8','encoding':{'0':'sun','1':'shadow'},'arrayOrder':'row-major; rows increase north; index=j*nx+i','nx':nx,'ny':ny,'dx':dx,'x0':x0,'y0':y0,'originEPSG6677':meta['origin_epsg6677'],'crs':'EPSG:6677','timezone':'Asia/Tokyo','sunLocation':{k:sun[k] for k in ['latitude','longitude']},'azimuthConvention':sun['azimuthConvention'],'heightFactors':list(variants),'baselineHeightFactor':1,'heightChangeScope':'Only buildings marked core in city.json; all surrounding buildings retain source heights','coreOpenCells':int(core_ground.sum()),'horizonHandling':'At or below the horizon all ground cells have shadow=1 (no direct sunlight); all requested samples are tested individually','outsideDomainHandling':'Rays terminate at the grid boundary; buildings outside the supplied height grid cannot cast shade in this calculation','limits':['Buildings are vertical 5 m raster prisms; narrow passages and edge locations can differ from polygon geometry.','Flat ground and direct-sun occlusion only; excludes terrain, facade details, diffuse radiation and air temperature.','Original precision PLATEAU outlines reproduce the existing source raster; model classification uses city.json core flags.','Arrays mark solid cells shadowed; all reported ground fractions use the same 2830 open core cells.','Tree shadows are intentionally omitted for dynamic frontend calculation.'],'cases':catalog,'checks':{'caseCount':len(catalog),'bytes':len(payload),'expectedBytes':96*nx*ny,'binarySha256':hashlib.sha256(payload).hexdigest(),'finiteInputHeights':bool(np.isfinite(height).all()),'sourceRasterMaxDifferenceM':float(raster_diff.max()),'sourceSolidRasterEqual':bool(np.array_equal(reproduced>0,solid)),'arrayValues':[0,1],'monotoneHeightFailures':monotone_failures,'belowHorizonCases':sum(c['atOrBelowHorizon'] for c in catalog),'summerNoonBaseline':noon_comparison,'elapsedSeconds':time.monotonic()-started,'resourceLimits':{'cpuCount':1,'addressSpaceBytes':1024**3,'cpuSeconds':120,'wallSecondsExternal':120}}}
assert len(payload)==96*nx*ny
(work/'shade-v2.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result['checks'],ensure_ascii=False,indent=2),flush=True)
