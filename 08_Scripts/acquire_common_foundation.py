#!/usr/bin/env python3
"""Acquire bounded, public source data for the Studio common foundation."""
import json
import urllib.request
import urllib.parse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'03_Theme_B/Common_Foundation/Sources'
BASE.mkdir(parents=True,exist_ok=True)


def download(url,dest,post=None):
    p=ROOT/dest;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():return p
    data=urllib.parse.urlencode(post).encode() if post else None
    req=urllib.request.Request(url,data=data,headers={'User-Agent':'UTokyoStudioPersonalFoundation/1.0'})
    with urllib.request.urlopen(req,timeout=60) as r:
        payload=r.read()
    temp=p.with_suffix(p.suffix+'.part');temp.write_bytes(payload);temp.replace(p)
    print('Downloaded',dest,len(payload),flush=True)
    return p


if __name__=='__main__':
    bbox='35.682,139.763,35.698,139.787'
    query='[out:json][timeout:45];('+''.join([
        f'way[building]({bbox});',f'way[highway]({bbox});',
        f'way[railway~"rail|subway"]({bbox});',f'nwr[railway=station]({bbox});',
        f'nwr[leisure~"park|garden|playground"]({bbox});',
        f'way[waterway]({bbox});',f'way[natural=water]({bbox});'])+');out tags geom;'
    (BASE/'osm_query.overpassql').write_text(query)
    p=download('https://overpass-api.de/api/interpreter','04_Data/Raw/OSM_2026-10-13/Kanda_Nihonbashi_OSM.json',{'data':query})
    d=json.loads(p.read_text())
    if d.get('remark'):raise RuntimeError(d['remark'])
    print(json.dumps({'osm_elements':len(d['elements']),'osm_timestamp':d.get('osm3s',{}).get('timestamp_osm_base')},ensure_ascii=False),flush=True)
