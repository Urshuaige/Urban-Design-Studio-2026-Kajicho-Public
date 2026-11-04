#!/usr/bin/env python3
"""Read selected unchanged ZIP members with HTTP Range; retain parent URL/member paths.
The public bbox API loses nested flood scenario paths. Use the full archive's
central-directory receipt to resolve each river/scenario without downloading 2 GB.
"""
import urllib.request,json,struct,zlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'04_Data/Raw/Public_Baseline_2026-10-14';INDEX=json.loads((BASE/'Sources/plateau_full_zip_index.json').read_text());out=BASE/'PLATEAU/flood_members';out.mkdir(parents=True,exist_ok=True)
meshes={'53394621','53394622','53394631','53394632'}
fs=[m for m in INDEX['members'] if '/fld/' in m['name'] and Path(m['name']).name.split('_')[0] in meshes and m['name'].endswith('.gml')]
for m in fs:
 p=out/m['name'];p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():continue
 start=m['offset'];end=start+30+len(m['name'].encode())+65536+m['compressed_bytes']-1
 with urllib.request.urlopen(urllib.request.Request(INDEX['url'],headers={'Range':f'bytes={start}-{end}'}),timeout=60) as r:
  assert r.status==206
  b=r.read()
 v=struct.unpack('<4s5H3L2H',b[:30]);assert v[0]==b'PK\x03\x04';k=30+v[9]+v[10];compressed=b[k:k+m['compressed_bytes']]
 content=zlib.decompress(compressed,-15) if m['compression']==8 else compressed
 assert len(content)==m['bytes']
 if v[6]:assert zlib.crc32(content)==v[6]
 p.write_bytes(content);print(m['name'],len(content),flush=True)
with zipfile.ZipFile(BASE/'PLATEAU/Chiyoda_Flood_Selected_Original_Members.zip','w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
 for m in fs:z.write(out/m['name'],m['name'])
(BASE/'Sources/flood_member_receipts.json').write_text(json.dumps({'parent_archive_url':INDEX['url'],'method':'HTTP Range ZIP member extraction; original uncompressed bytes preserved','download_date':'2026-10-14','members':fs},ensure_ascii=False,indent=2))
