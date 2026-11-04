#!/usr/bin/env python3
"""Build current untextured PLATEAU visual geometry on a remote server.
Source IDs and Figure 5 GIS membership are preserved; no simulation is run.
"""
import argparse,collections,concurrent.futures,hashlib,json,math,os,sqlite3,struct,sys,time
from pathlib import Path
import numpy as np
import DracoPy
from pyproj import Transformer
ORIGIN=np.array([-5600.,-34320.])
FIELDS=["gml_id","_lod","_lod_type","_zmin","_zmax","bldg:measuredHeight","core:creationDate","uro:BuildingDetailAttribute_uro:surveyYear","uro:BuildingIDAttribute_uro:buildingID"]
DT={"DOUBLE":"<f8","FLOAT":"<f4","UNSIGNED_SHORT":"<u2","SHORT":"<i2","UNSIGNED_INT":"<u4","INT":"<i4","UNSIGNED_BYTE":"u1","BYTE":"i1"}
def decode(path):
 cache=Path(path).parent/"decoded"/(Path(path).stem+".npz")
 cache.parent.mkdir(exist_ok=True)
 if cache.exists():
  with np.load(cache,allow_pickle=False) as old:
   info=json.loads(str(old["metadata"].item()))
   return [(a,old[f"xyz_{i}"]) for i,a in enumerate(info["items"])],info["quality"]
 b=Path(path).read_bytes();magic,ver,length,fj,fb,bj,bb=struct.unpack("<4s6I",b[:28]);assert magic==b"b3dm" and len(b)==length
 n=json.loads(b[28:28+fj])["BATCH_LENGTH"];bt=json.loads(b[28+fj+fb:28+fj+fb+bj]);bbuf=b[28+fj+fb+bj:28+fj+fb+bj+bb]
 def attr(k):
  x=bt.get(k,[None]*n)
  return np.frombuffer(bbuf,dtype=DT[x["componentType"]],count=n,offset=x["byteOffset"]).tolist() if isinstance(x,dict) and "byteOffset" in x else x
 fields={k:attr(k) for k in FIELDS}
 gl=b[28+fj+fb+bj+bb:];jl=struct.unpack("<I",gl[12:16])[0];j=json.loads(gl[20:20+jl]);prim=j["meshes"][0]["primitives"][0];ext=prim["extensions"]["KHR_draco_mesh_compression"];bv=j["bufferViews"][ext["bufferView"]];o=20+jl+8
 mesh=DracoPy.decode(gl[o+bv.get("byteOffset",0):o+bv.get("byteOffset",0)+bv["byteLength"]])
 batch=mesh.get_attribute_by_unique_id(ext["attributes"]["_BATCHID"])["data"].ravel().astype(int)
 pts=mesh.points.astype(float);ecef=pts[:,[0,2,1]]*np.array([1,-1,1])+np.array(j["extensions"]["CESIUM_RTC"]["center"])
 lon,lat,elev=Transformer.from_crs(4978,4979,always_xy=True).transform(ecef[:,0],ecef[:,1],ecef[:,2]);east,north=Transformer.from_crs(4326,6677,always_xy=True).transform(lon,lat)
 metric=np.column_stack((east,north,elev));out=[];mixed=0
 faceids=batch[mesh.faces];ok=np.all(faceids==faceids[:,0,None],axis=1);mixed=int((~ok).sum());faces=mesh.faces[ok];batches=faceids[ok,0]
 for bi in np.unique(batches):
  fs=faces[batches==bi];a={k:v[int(bi)] for k,v in fields.items()};a["source_tile"]=Path(path).name;a["source_sha256"]=hashlib.sha256(b).hexdigest()
  xyz=metric[fs].reshape(-1,3);minimum=xyz[:,2].min();offset=minimum-float(a["_zmin"]);xyz[:,2]-=offset
  xyz=np.column_stack((xyz[:,0]-ORIGIN[0],xyz[:,2],-(xyz[:,1]-ORIGIN[1])))
  out.append((a,xyz))
 quality={"tile":Path(path).name,"source_buildings":n,"mixed_batch_faces":mixed,"bytes":len(b)}
 np.savez_compressed(cache,metadata=np.array(json.dumps({"items":[a for a,_ in out],"quality":quality})),**{f"xyz_{i}":xyz for i,(_,xyz) in enumerate(out)})
 return out,quality
def glb_write(path,items,metadata):
 chunks=[];views=[];access=[];meshes=[];nodes=[];offset=0
 def arr(a,typ):
  nonlocal offset
  a=np.asarray(a,dtype="<f4");raw=a.tobytes();view=len(views);views.append({"buffer":0,"byteOffset":offset,"byteLength":len(raw),"target":34962});chunks.append(raw);offset+=len(raw);i=len(access);ac={"bufferView":view,"componentType":5126,"count":len(a),"type":typ}
  if typ=="VEC3":ac.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
  access.append(ac);return i
 for i,(a,xyz) in enumerate(items):
  triangles=xyz.reshape(-1,3,3);normal=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None];norm=np.repeat(normal,3,axis=0)
  attrs={"POSITION":arr(xyz,"VEC3"),"NORMAL":arr(norm,"VEC3")}
  meshes.append({"name":a["asset_id"],"primitives":[{"attributes":attrs,"mode":4,"material":0}]})
  nodes.append({"name":a["asset_id"],"mesh":i,"extras":a})
 doc={"asset":{"version":"2.0","generator":"Kajicho PLATEAU source-triangle extraction 2026-10-20"},"scene":0,"scenes":[{"nodes":list(range(len(nodes)))}],"nodes":nodes,"meshes":meshes,"materials":[{"name":"Untextured building","pbrMetallicRoughness":{"baseColorFactor":[0.71,0.73,0.76,1],"metallicFactor":0,"roughnessFactor":1},"doubleSided":True}],"buffers":[{"byteLength":offset}],"bufferViews":views,"accessors":access,"extras":metadata}
 jb=json.dumps(doc,ensure_ascii=False,separators=(",",":")).encode();jb+=b" "*((-len(jb))%4);bb=b"".join(chunks);bb+=b"\0"*((-len(bb))%4);total=12+8+len(jb)+8+len(bb)
 path.write_bytes(struct.pack("<4sII",b"glTF",2,total)+struct.pack("<I4s",len(jb),b"JSON")+jb+struct.pack("<I4s",len(bb),b"BIN\0")+bb)
 return {"file":path.name,"bytes":total,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"triangles":sum(len(x)//3 for _,x in items),"buildings":len(items)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--task-root",type=Path,required=True);p.add_argument("--workers",type=int,default=1);args=p.parse_args();T=args.task_root
 D=T/"raw/plateau/Highest_Geometry_2026-10-20";O=D/"Tile_Extraction";O.mkdir(exist_ok=True,parents=True)
 C=sqlite3.connect("file:"+str(T/"team/04_Data/Ready/Study_Area_2026-10-18/Kanda_Nihonbashi_Study.gpkg")+"?mode=ro",uri=True);C.row_factory=sqlite3.Row
 selected={r["asset_id"]:dict(r) for r in C.execute("select asset_id,ward_code,gml_id,height_m,height_source,levels,levels_source,plan_area_m2,usage,survey_year,creation_date,model_year,in_primary_area from analysis_buildings_wider")};C.close()
 paths=sorted(D.glob("*.b3dm"),key=lambda x:-x.stat().st_size)
 start=time.perf_counter()
 # A representative decoder unit was timed separately before this full batch.
 results=[];checkpoint=D/"decoded";checkpoint.mkdir(exist_ok=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=min(args.workers,len(paths))) as ex:
  for result in ex.map(decode,paths):
   results.append(result)
 candidates=collections.defaultdict(list);qa=[]
 for items,check in results:
  qa.append(check)
  for a,xyz in items:
   # Source overlap includes both wards, while current membership keeps true ward code.
   matches=[r for r in selected.values() if r["gml_id"]==a["gml_id"]]
   for r in matches:candidates[r["asset_id"]].append((a,xyz))
 items=[];coverage=[];warnings=[];totaldegenerate=0
 for asset,r in sorted(selected.items()):
  options=candidates.get(asset,[])
  if not options:continue
  a,xyz=max(options,key=lambda pair:(int(pair[0]["_lod"]),len(pair[1])))
  a=dict(a);a.update(asset_id=asset,ward_code=r["ward_code"],primary=bool(r["in_primary_area"]),model_release_year=r["model_year"],use_survey_year=r["survey_year"],usage=r["usage"],full_footprint_membership=True)
  tri=xyz.reshape(-1,3,3);area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2;keep=area>1e-8;removed=int((~keep).sum());totaldegenerate+=removed;xyz=tri[keep].reshape(-1,3)
  a["triangles"]=int(len(xyz)//3);a["lod"]=int(a["_lod"]);a["lod_fallback"]=a["lod"]<2;a["bounds_local_m"]=[xyz.min(axis=0).round(4).tolist(),xyz.max(axis=0).round(4).tolist()];a["source_height_m"]=r["height_m"];a["geometry_height_m"]=float(xyz[:,1].max()-xyz[:,1].min());a["degenerate_triangles_removed"]=removed
  assert np.isfinite(xyz).all() and a["geometry_height_m"]>0
  items.append((a,xyz));coverage.append(a)
 missing=sorted(set(selected)-{a["asset_id"] for a,_ in items});assert not missing,missing
 allxyz=np.concatenate([x for _,x in items]);counts=collections.Counter(a["lod"] for a,_ in items);primary=collections.Counter(a["lod"] for a,_ in items if a["primary"])
 meta={"title":"Kanda–Nihonbashi current source building geometry","date":"2026-10-20","source_model_year":2025,"buildings":len(items),"primary_buildings":sum(a["primary"] for a,_ in items),"actual_lod_counts":dict(counts),"primary_actual_lod_counts":dict(primary),"missing_source_ids":missing,"source_match_rule":"Exact original gml_id joined to current asset_id; current GIS membership is unchanged.","selection_rule":"Full original footprint covered by fixed registered official Figure 5 study outline; no clipping or enlargement.","horizontal_crs":"EPSG:6677","origin_epsg6677":ORIGIN.tolist(),"gltf_axes":"x=easting-originE; y=source orthometric height; z=-(northing-originN)","units":"metres","vertical_note":"Source _zmin is the original CityGML orthometric lower elevation. ECEF tile vertices are transformed to ellipsoidal height, then shifted per building so their minimum equals source _zmin. Relative vertex elevations are preserved; terrain is not included.","vertical_ground_offset_m":0,"bounds_local_m":[allxyz.min(axis=0).round(4).tolist(),allxyz.max(axis=0).round(4).tolist()],"textures":False,"highest_available_check":"PLATEAU delivery API maxlod4, lod3 and lod4 queried for both wards on 2026-10-20; maxlod4 resolves 2025 LOD2, lod3/lod4 empty. Actual _lod checked for every selected object.","display_use":"Visual survey and geometry review. The mesh is not validated for CFD and must not be overlaid on old solver fields.","source_documentation":"https://docs.plateauview.mlit.go.jp/api/rest/operations/datacatalog3dtilesspectilesetjson/","license":"PLATEAU / Public Data License 1.0 compatible with CC BY 4.0; original municipality copyright retained","license_url":"https://www.mlit.go.jp/plateau/site-policy/","attribution":"PLATEAU 3D City Model, Chiyoda and Chuo wards, 2025; Ministry of Land, Infrastructure, Transport and Tourism. Extracted, coordinates transformed, textures omitted for Urban Design Studio 2026.","source_catalogs":[f"https://api.plateauview.mlit.go.jp/datacatalog/3dtiles/{ward}-bldg-maxlod4-latest/tileset.json" for ward in ["13101","13102"]],"build_seconds":time.perf_counter()-start,"workers":args.workers,"quality":{"unique_asset_ids":len(set(a["asset_id"] for a,_ in items)),"mixed_batch_faces":sum(x["mixed_batch_faces"] for x in qa),"degenerate_triangles_removed":totaldegenerate,"finite_coordinates":True}}
 manifest=glb_write(O/"kajicho-current-untextured.glb",items,meta)
 (O/"geometry-index.json").write_text(json.dumps({**meta,"asset":manifest,"buildings":coverage},ensure_ascii=False,indent=2))
 (O/"geometry-summary.json").write_text(json.dumps({**meta,"asset":manifest,"source_tiles":qa},ensure_ascii=False,indent=2))
 np.savez_compressed(O/"source_triangles_local.npz",**{a["asset_id"]:x.astype("<f8") for a,x in items})
 print(json.dumps({**meta,"asset":manifest},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
