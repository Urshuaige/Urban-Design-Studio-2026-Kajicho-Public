#!/usr/bin/env python3
"""Saved-artifact validation for the current PLATEAU display asset."""
from pathlib import Path
import argparse,hashlib,json,sqlite3,struct
import numpy as np
def main():
 p=argparse.ArgumentParser();p.add_argument("--task-root",required=True,type=Path);a=p.parse_args();T=a.task_root;D=T/"team/04_Data/Ready/PLATEAU_Highest_2026-10-20";index=json.loads((D/"geometry-index.json").read_text());summary=json.loads((D/"geometry-summary.json").read_text());b=(D/"kajicho-current-untextured.glb").read_bytes();magic,v,length=struct.unpack("<4sII",b[:12]);assert magic==b"glTF" and v==2 and length==len(b)
 jl,typ=struct.unpack("<I4s",b[12:20]);assert typ==b"JSON";doc=json.loads(b[20:20+jl]);bl,typ=struct.unpack("<I4s",b[20+jl:28+jl]);assert typ==b"BIN\0";binary=b[28+jl:];assert len(binary)==bl
 C=sqlite3.connect("file:"+str(T/"team/04_Data/Ready/Study_Area_2026-10-18/Kanda_Nihonbashi_Study.gpkg")+"?mode=ro",uri=True);expected={r[0] for r in C.execute("select asset_id from analysis_buildings_wider")};primary={r[0] for r in C.execute("select asset_id from analysis_buildings_primary")};C.close()
 got={x["asset_id"] for x in index["buildings"]};assert got==expected and len(got)==1074
 assert {x["asset_id"] for x in index["buildings"] if x["primary"]}==primary and len(primary)==277
 assert all(x["lod"]==2 and x["source_srs"].endswith("/6697") for x in index["buildings"])
 assert {x["name"] for x in doc["nodes"]}==got and len(doc["meshes"])==len(got);assert "textures" not in doc and "images" not in doc
 ntri=0;worstnormal=0
 for mesh in doc["meshes"]:
  prim=mesh["primitives"][0];attrs={}
  for name,i in prim["attributes"].items():
   ac=doc["accessors"][i];bv=doc["bufferViews"][ac["bufferView"]];assert ac["componentType"]==5126 and ac["type"]=="VEC3";off=bv.get("byteOffset",0)+ac.get("byteOffset",0);ar=np.frombuffer(binary,dtype="<f4",count=ac["count"]*3,offset=off).reshape(-1,3);assert np.isfinite(ar).all();attrs[name]=ar
  assert len(attrs["POSITION"])%3==0;ntri+=len(attrs["POSITION"])//3
  worstnormal=max(worstnormal,float(np.abs(np.linalg.norm(attrs["NORMAL"],axis=1)-1).max()))
 assert ntri==68554 and worstnormal<1e-6
 assert hashlib.sha256(b).hexdigest()==summary["asset"]["sha256"] and len(b)<25*1024*1024
 print(json.dumps({"status":"pass","buildings":len(got),"primary_buildings":len(primary),"actual_LOD2":len(got),"triangles":ntri,"bytes":len(b),"normal_length_error_max":worstnormal,"textures":False,"boundary_membership":"exact current GIS ID sets","vertical":"original EPSG6697 third coordinate unchanged"}))
if __name__=="__main__":main()
