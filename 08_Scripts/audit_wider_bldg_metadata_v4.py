#!/usr/bin/env python3
"""Read only official b3dm headers/batch tables to screen distant building heights."""
import concurrent.futures,json,math,struct,urllib.request,urllib.parse,os
from pathlib import Path
from datetime import datetime,timezone
from pyproj import Transformer,datadir
from shapely.geometry import Polygon,shape
R=Path(__file__).resolve().parents[1];RAW=R/'04_Data/Raw/CFD_Domain_Audit_2026-10-14';OUT=R/'04_Data/Ready/CFD_Domain_Audit_2026-10-14'
screen=json.loads((RAW/'Wider_Tile_Screen.json').read_text());leaves=[x for x in screen['leaves'] if x['possible10H']]
old=json.loads((R/'06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data/cfd-context.json').read_text());ids={b['id'] for b in old['buildings']};core=shape(old['boundary'])
tr=Transformer.from_crs(4326,6677,always_xy=True);(RAW/'tile_ranges').mkdir(exist_ok=True)
os.environ.setdefault('PROJ_LIB',datadir.get_data_dir())
def read(tile):
 url=tile['url'];url_path=Path(urllib.parse.urlparse(url).path)
 name=tile['ward']+'_'+(url_path.parent.name+'_' if url_path.suffix=='.glb' else '')+url_path.name
 cache=RAW/'tile_ranges'/(name+'.header-batch.bin');receipt={'url':url,'ward':tile['ward']}
 try:
  if cache.exists():b=cache.read_bytes()
  else:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':'bytes=0-65535'}),timeout=40) as r:b=r.read(65536);receipt['http_status']=r.status
   if b[:4]==b'b3dm':
    v=struct.unpack('<4s6I',b[:28]);end=28+sum(v[3:7])
   elif b[:4]==b'glTF':
    json_size=struct.unpack_from('<I',b,12)[0]
    if len(b)<json_size+20:
     with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes=0-{json_size+19}'}),timeout=40) as r:b=r.read(json_size+20)
    gltf=json.loads(b[20:20+json_size]);ext=gltf['extensions']['EXT_structural_metadata'];table=ext['propertyTables'][0]
    need=['_xmin','_xmax','_ymin','_ymax','_zmin','_zmax','bldg:measuredHeight','gml_id','meshcode']
    refs=[p[key] for k,p in table['properties'].items() if k in need for key in ['values','stringOffsets'] if key in p]
    end=20+json_size+8+max(gltf['bufferViews'][i].get('byteOffset',0)+gltf['bufferViews'][i]['byteLength'] for i in refs)
   else:raise ValueError('Unsupported tile magic '+str(b[:4]))
   if len(b)<end:
    with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes=0-{end-1}'}),timeout=40) as r:
     assert r.status==206,'Range support required';b=r.read(end)
   b=b[:end];cache.write_bytes(b)
  if b[:4]==b'b3dm':
   v=struct.unpack('<4s6I',b[:28]);ft=json.loads(b[28:28+v[3]]);n=ft['BATCH_LENGTH'];start=28+v[3]+v[4]
   table=json.loads(b[start:start+v[5]]);binary=b[start+v[5]:start+v[5]+v[6]]
   def values(k):
    a=table.get(k,[None]*n)
    if isinstance(a,list):return a
    formats={'DOUBLE':'d','FLOAT':'f','INT':'i','UNSIGNED_INT':'I','SHORT':'h','BYTE':'b'}
    return struct.unpack_from('<'+str(n)+formats[a['componentType']],binary,a['byteOffset'])
  else:
   json_size=struct.unpack_from('<I',b,12)[0];gltf=json.loads(b[20:20+json_size]);ext=gltf['extensions']['EXT_structural_metadata'];table=ext['propertyTables'][0];n=table['count'];binary=b[20+json_size+8:]
   schema=ext['schema']['classes'][table['class']]['properties']
   def buf(index):
    view=gltf['bufferViews'][index];s=view.get('byteOffset',0);return binary[s:s+view['byteLength']]
   def values(k):
    a=table['properties'].get(k)
    if not a:return [None]*n
    spec=schema[k];data=buf(a['values'])
    if spec['type']=='STRING':
     fmt={'UINT32':'I','UINT64':'Q','UINT16':'H','UINT8':'B'}[a.get('stringOffsetType','UINT32')]
     offsets=struct.unpack('<'+str(n+1)+fmt,buf(a['stringOffsets']));return [data[offsets[i]:offsets[i+1]].decode('utf-8') for i in range(n)]
    fmt={'FLOAT64':'d','FLOAT32':'f','INT8':'b','INT16':'h','INT32':'i','UINT8':'B','UINT32':'I'}[spec['componentType']]
    return [None if v==spec.get('noData') else v for v in struct.unpack_from('<'+str(n)+fmt,data)]
  cols={k:values(k) for k in ['_xmin','_xmax','_ymin','_ymax','_zmin','_zmax','bldg:measuredHeight','gml_id','meshcode']}
  rows=[]
  for i in range(n):
   ident=cols['gml_id'][i];h=cols['bldg:measuredHeight'][i];z0,z1=cols['_zmin'][i],cols['_zmax'][i]
   method='bldg:measuredHeight'
   if h is None or not math.isfinite(float(h)) or not 0<float(h)<1000:
    h=float(z1-z0) if z0 is not None and z1 is not None else None;method='LOD1 zmax-zmin'
   h=float(h) if h is not None else None
   w,e,s,north=[cols[k][i] for k in ['_xmin','_xmax','_ymin','_ymax']]
   corners=[]
   for lon,lat in [(w,s),(e,s),(e,north),(w,north)]:
    x,y=tr.transform(lon,lat);corners.append((x+5600,y+34320))
   bbox=Polygon(corners);dist=bbox.distance(core)
   six=h is not None and dist<=max(500,6*h)+1
   ten=h is not None and dist<=max(500,10*h)+1
   if six or ten or h is None:
    rows.append({'id':ident,'ward':tile['ward'],'meshcode':str(cols['meshcode'][i]),'height_m':h,'height_source':method,
     'bbox_lonlat':[w,s,e,north],'distance_lower_bound_m':dist,'within6H_bbox':six,'within10H_bbox':ten,'retained':ident in ids,'source_url':url})
  receipt.update(objects=n,bytes_metadata=len(b),rows=rows);return receipt
 except Exception as e:receipt['error']=str(e);return receipt
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 receipts=list(pool.map(read,leaves))
unique={}
for receipt in receipts:
 for row in receipt.get('rows',[]):unique[row['id']]=row
rows=list(unique.values());summary={'snapshot_utc':datetime.now(timezone.utc).isoformat(),'tile_metadata_reads':len(receipts),'tile_errors':[r for r in receipts if 'error' in r],
 'objects_screened':sum(r.get('objects',0) for r in receipts),'metadata_bytes':sum(r.get('bytes_metadata',0) for r in receipts),
 'method':'LOD1 batch-table measuredHeight with z-range fallback; transformed geographic footprint bounding boxes give conservative distance lower bounds. 1m screening allowance. Candidates require exact source polygon review.',
 'sources_screened':screen['wards'],'candidates':rows,
 'new6H_bbox_candidates':[b for b in rows if b['within6H_bbox'] and not b['retained']],
 'new10H_bbox_candidates':[b for b in rows if b['within10H_bbox'] and not b['retained']],
 'per_tile_receipts':[{k:v for k,v in r.items() if k!='rows'} for r in receipts],
 'coverage':'Seven selected wards, official LOD1 representation, not a claim that all2026 physical obstacles or non-building towers are present.'}
(OUT/'Wider_Building_Screen.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in summary.items() if k in ['tile_metadata_reads','tile_errors','objects_screened','metadata_bytes','new6H_bbox_candidates','new10H_bbox_candidates']}),flush=True)
