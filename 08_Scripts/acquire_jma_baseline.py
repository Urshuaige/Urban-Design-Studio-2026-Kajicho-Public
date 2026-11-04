#!/usr/bin/env python3
"""Fetch Tokyo 2025 hourly CSV through the official form endpoint.
Parameters and codes are from JMA top.bundle.js and whatsnewHistory.js,
saved with the source receipts. No authentication or registration required.
"""
import json,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'04_Data/Raw/Public_Baseline_2026-10-14/JMA';OUT.mkdir(parents=True,exist_ok=True)
payload={'stationNumList':json.dumps(['s47662']),'aggrgPeriod':'9','elementNumList':json.dumps([[s,''] for s in ['201','101','301','605','610','401','601']]),'interAnnualType':'1','ymdList':json.dumps(['2025','2025','1','12','1','31']),'option':json.dumps({'list':['obs'],'nyear':0}),'downloadFlag':'true','rmkFlag':'1','disconnectFlag':'1','csvFlag':'1','ymdLiteral':'1','youbiFlag':'0','fukenFlag':'0','kijiFlag':'0','jikantaiFlag':'0','jikantaiList':'[]'}
url='https://www.data.jma.go.jp/risk/obsdl/show/table'
(OUT/'request.json').write_text(json.dumps({'url':url,'method':'POST','body':payload,'download_date':'2026-10-14'},ensure_ascii=False,indent=2))
with urllib.request.urlopen(urllib.request.Request(url,data=urllib.parse.urlencode(payload).encode(),headers={'Content-Type':'application/x-www-form-urlencoded','Accept':'text/html,application/xhtml+xml'}),timeout=90) as r:
 content=r.read();headers=dict(r.headers)
 (OUT/'response_headers.json').write_text(json.dumps(headers,indent=2))
 if 'attachment' not in r.headers.get('Content-Disposition',''):raise RuntimeError(content[:2000].decode(errors='replace'))
 (OUT/'Tokyo_2025_hourly_original.csv').write_bytes(content)
 print(len(content),headers)
 print(content[:2500].decode('cp932',errors='replace'))
