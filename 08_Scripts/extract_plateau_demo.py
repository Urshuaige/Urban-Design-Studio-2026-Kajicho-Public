"""Extract a bounded PLATEAU 3D Tiles plan projection with original heights.

Run with DracoPy, numpy, shapely, pyproj. Raw tiles are retained unchanged.
Outputs are visualization/screening geometry, not surveyed ground footprints.
"""
import json, struct, pathlib, hashlib, collections, urllib.parse, statistics
import numpy as np
import DracoPy
from pyproj import Transformer
from shapely.geometry import Polygon, box, mapping
from shapely.ops import unary_union, transform
from shapely import make_valid

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / "04_Data/Ready/Simulation_Demo"
HERE.mkdir(parents=True, exist_ok=True)
RAW = ROOT / '04_Data/Raw/PLATEAU_Demo'
BBOX = [139.767, 35.687, 139.776, 35.695]
TO_GEO = Transformer.from_crs(4978,4979,always_xy=True)
TO_METRIC = Transformer.from_crs(4326,6677,always_xy=True)
TO_LONLAT = Transformer.from_crs(6677,4326,always_xy=True)
AOI = transform(TO_METRIC.transform,box(*BBOX))
features=[]
sources=[]
checks={'duplicate_ids':0,'mixed_batch_faces':0,'empty_geometry':0,'repaired_geometry':0,'bbox_center_error_max_deg':0}
seen=set()
for tile in sorted(RAW.glob('*.b3dm')):
    if tile.name.startswith('._'): continue
    b=tile.read_bytes()
    magic,version,length,fj,fb,bj,bb=struct.unpack('<4s6I',b[:28])
    assert magic==b'b3dm' and length==len(b)
    ft=json.loads(b[28:28+fj]);n=ft['BATCH_LENGTH']
    bt=json.loads(b[28+fj+fb:28+fj+fb+bj])
    binary=b[28+fj+fb+bj:28+fj+fb+bj+bb]
    def attr(k):
        x=bt.get(k,[None]*n)
        if isinstance(x,dict) and 'byteOffset' in x:
            dt={'DOUBLE':'<f8','FLOAT':'<f4','UNSIGNED_SHORT':'<u2','UNSIGNED_INT':'<u4','UNSIGNED_BYTE':'u1'}[x['componentType']]
            return np.frombuffer(binary,dtype=dt,count=n,offset=x['byteOffset']).tolist()
        return x
    fields={k:attr(k) for k in ['gml_id','bldg:measuredHeight','bldg:storeysAboveGround','bldg:usage','bldg:address','core:creationDate','uro:BuildingDetailAttribute_uro:surveyYear','_x','_y','_xmin','_xmax','_ymin','_ymax','_zmin','_zmax']}
    candidate={i for i in range(n) if fields['_xmax'][i]>=BBOX[0] and fields['_xmin'][i]<=BBOX[2] and fields['_ymax'][i]>=BBOX[1] and fields['_ymin'][i]<=BBOX[3]}
    gl=b[28+fj+fb+bj+bb:];jl=struct.unpack('<I',gl[12:16])[0];j=json.loads(gl[20:20+jl]);binary_start=20+jl+8
    prim=j['meshes'][0]['primitives'][0];ext=prim['extensions']['KHR_draco_mesh_compression'];v=j['bufferViews'][ext['bufferView']]
    mesh=DracoPy.decode(gl[binary_start+v.get('byteOffset',0):binary_start+v.get('byteOffset',0)+v['byteLength']])
    batch=mesh.get_attribute_by_unique_id(ext['attributes']['_BATCHID'])['data'].ravel().astype(int)
    pts=mesh.points.astype(float)
    # glTF Y-up to 3D Tiles Z-up, then CESIUM_RTC Earth-centred metres.
    ecef=pts[:,[0,2,1]]*np.array([1,-1,1])+np.array(j['extensions']['CESIUM_RTC']['center'])
    lon,lat,elev=TO_GEO.transform(ecef[:,0],ecef[:,1],ecef[:,2])
    east,north=TO_METRIC.transform(lon,lat)
    metric=np.column_stack((east,north,elev))
    by_building=collections.defaultdict(list)
    for face in mesh.faces:
        ids=batch[face]
        if not np.all(ids==ids[0]): checks['mixed_batch_faces']+=1;continue
        bi=int(ids[0])
        if bi not in candidate: continue
        tri=metric[face]
        cross=np.cross(tri[1]-tri[0],tri[2]-tri[0]);norm=np.linalg.norm(cross)
        # Near-horizontal LOD1 top/bottom faces give the model plan projection.
        if norm<1e-8 or abs(cross[2])/norm<0.95:continue
        poly=Polygon(tri[:,:2])
        if poly.area>0.003:by_building[bi].append(poly)
    count=0
    for bi in sorted(candidate):
        identifier=fields['gml_id'][bi]
        if identifier in seen:checks['duplicate_ids']+=1;continue
        polys=by_building.get(bi,[])
        if not polys:checks['empty_geometry']+=1;continue
        geom=unary_union(polys).simplify(0.03,preserve_topology=True)
        if not geom.is_valid:geom=make_valid(geom);checks['repaired_geometry']+=1
        if geom.geom_type=='GeometryCollection':geom=unary_union([g for g in geom.geoms if g.geom_type in ('Polygon','MultiPolygon')])
        if geom.is_empty or not geom.intersects(AOI):continue
        height=fields['bldg:measuredHeight'][bi]
        height_source='bldg:measuredHeight'
        if height is None or height<=0:
            height=fields['_zmax'][bi]-fields['_zmin'][bi];height_source='PLATEAU LOD1 _zmax minus _zmin'
        if height<=0:raise ValueError((identifier,height))
        glon,glat=TO_LONLAT.transform(geom.centroid.x,geom.centroid.y)
        # FME _x/_y need not equal polygon centroid, but large errors detect axis mistakes.
        error=max(abs(glon-fields['_x'][bi]),abs(glat-fields['_y'][bi]))
        checks['bbox_center_error_max_deg']=max(checks['bbox_center_error_max_deg'],error)
        props={'id':identifier,'height_m':round(float(height),3),'height_source':height_source,'height_is_source':True,'measured_height_m':fields['bldg:measuredHeight'][bi],'storeys':fields['bldg:storeysAboveGround'][bi],'storeys_is_source':fields['bldg:storeysAboveGround'][bi] is not None,'usage':fields['bldg:usage'][bi],'address':fields['bldg:address'][bi],'survey_year_raw':fields['uro:BuildingDetailAttribute_uro:surveyYear'][bi],'creation_date':fields['core:creationDate'][bi],'model_year':2025,'source_tile':tile.name,'geometry_type':'LOD1 model horizontal projection','area_m2':round(geom.area,3),'lon':round(glon,9),'lat':round(glat,9),'ground_elevation_source_m':fields['_zmin'][bi],'roof_elevation_source_m':fields['_zmax'][bi]}
        features.append({'type':'Feature','properties':props,'geometry':mapping(geom)})
        seen.add(identifier);count+=1
    if tile.name.startswith('chuo_'):
        wrapper=json.loads((RAW/'chuo_lod1_tileset.json').read_text())
        relative='data/'+tile.name.removeprefix('chuo_')
    else:
        wrapper=json.loads((RAW/'chiyoda_lod1_tileset.json').read_text());relative='data/'+tile.name
    source_url=urllib.parse.urljoin(wrapper['root']['children'][0]['content']['uri'],relative)
    sources.append({'file':str(tile.relative_to(ROOT)),'url':source_url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_buildings':n,'selected_buildings':count})
    print(tile.name,n,count,flush=True)

assert checks['mixed_batch_faces']==0
assert checks['bbox_center_error_max_deg']<0.001
fc={'type':'FeatureCollection','name':'PLATEAU Kanda Kajicho 2025 LOD1 model projection','crs':{'type':'name','properties':{'name':'EPSG:6677'}},'features':features}
(HERE/'plateau_buildings_6677.geojson').write_text(json.dumps(fc,ensure_ascii=False,separators=(',',':')))
from shapely.geometry import shape
geo=[]
for feature in features:
    geo.append({**feature,'geometry':mapping(transform(TO_LONLAT.transform,shape(feature['geometry'])))})
(HERE/'plateau_buildings_4326.geojson').write_text(json.dumps({'type':'FeatureCollection','features':geo},ensure_ascii=False,separators=(',',':')))
meta={'title':'PLATEAU Kanda–Kajicho building model projection','download_date':'2026-10-13','model_release_year':2025,'survey_year_values':dict(collections.Counter(f['properties']['survey_year_raw'] for f in features)),'creation_date_values':dict(collections.Counter(f['properties']['creation_date'] for f in features)),'bbox_lonlat':BBOX,'projected_crs':'EPSG:6677','geographic_crs':'EPSG:4326','buildings':len(features),'height_sources':dict(collections.Counter(f['properties']['height_source'] for f in features)),'license':'CC BY 4.0 under PLATEAU open data terms; attribution and edits stated','license_url':'https://www.mlit.go.jp/plateau/faq/','attribution':'PLATEAU 3D city model, Chiyoda/Chuo, Tokyo; processed for Urban Design Studio 2026. Original model copyright belongs to local authorities.','source_documentation':'https://docs.plateauview.mlit.go.jp/datasets/3d-tiles/','source_year_note':'2025 is the dataset release year. Per-building survey and creation dates are retained separately; raw survey value 0001 is a sentinel, not a historical survey year.','method':['Select leaf tiles intersecting specified geographic box; preserve originals.','Decode Draco mesh and batch ID, apply glTF Y-up to Z-up rotation and CESIUM_RTC offset.','Convert ECEF to geographic positions and EPSG:6677 east/north metres.','Union near-horizontal LOD1 triangle projections per building; simplify at 0.03 m; retain full building geometry intersecting box.','Retain original measuredHeight where available; otherwise use source LOD1 zmax-zmin, explicitly tagged.'],'geometry_note':'Output is a horizontal projection of the LOD1 model top/bottom surfaces. It approximates the LOD1 building outline and is not a surveyed street-level ground footprint. Render as an extrusion for demonstration.','scope_note':'Geometric input for display and simplified screening. CFD requires watertight mesh preparation, domain and boundary choices, and validation.','checks':checks,'sources':sources}
geoms=[shape(f['geometry']) for f in features]
heights=[f['properties']['height_m'] for f in features]
bounds=[g.bounds for g in geoms]
meta['geometry_checks']={'count':len(features),'unique_ids':len(seen),'invalid_count':sum(not g.is_valid for g in geoms),'empty_count':sum(g.is_empty for g in geoms),'geometry_types':dict(collections.Counter(g.geom_type for g in geoms)),'height_min_m':min(heights),'height_median_m':statistics.median(heights),'height_max_m':max(heights),'known_storeys':sum(f['properties']['storeys'] is not None for f in features),'bounds_epsg6677':[min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)],'source_raw_total_bytes':sum(s['bytes'] for s in sources),'outputs_bytes':{x.name:x.stat().st_size for x in HERE.glob('plateau*.geojson')}}
(HERE/'plateau_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print(json.dumps({k:meta[k] for k in ['buildings','height_sources','survey_year_values','checks']},ensure_ascii=False,indent=2))
