import json,urllib.request,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'04_Data/Raw/Public_Baseline_2026-10-14'
index=json.loads((base/'Sources/plateau_full_zip_index.json').read_text())
output=ROOT/'04_Data/Raw/CFD_Context_2026-10-14';output.mkdir(exist_ok=True)
meshes={'53394610','53394611','53394620','53394630','53394640','53394641','53394642'}
receipts=[]
for m in index['members']:
 if not (m['name'].startswith('udx/bldg/') and m['name'].endswith('.gml') and Path(m['name']).name.split('_')[0] in meshes):continue
 p=output/Path(m['name']).name
 if not p.exists():
  start=m['offset'];end=start+30+len(m['name'].encode())+65536+m['compressed_bytes']-1
  with urllib.request.urlopen(urllib.request.Request(index['url'],headers={'Range':f'bytes={start}-{end}'}),timeout=90) as r:
   assert r.status==206;b=r.read()
  v=struct.unpack('<4s5H3L2H',b[:30]);k=30+v[9]+v[10];content=zlib.decompress(b[k:k+m['compressed_bytes']],-15);assert len(content)==m['bytes']
  if v[6]:assert zlib.crc32(content)==v[6]
  p.write_bytes(content)
 receipts.append(m);print(p.name,p.stat().st_size,flush=True)
(output/'Source_Members.json').write_text(json.dumps({'url':index['url'],'download_date':'2026-10-14','members':receipts},indent=2))
