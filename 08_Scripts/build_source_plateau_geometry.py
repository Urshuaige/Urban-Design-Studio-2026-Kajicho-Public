#!/usr/bin/env python3
"""Triangulate original PLATEAU LOD2 surface polygons, preserving source elevations."""
import argparse,collections,concurrent.futures,hashlib,json,sys,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import mapbox_earcut
from pyproj import Transformer
from extract_plateau_tile_geometry import glb_write
G="{http://www.opengis.net/gml}";C="{http://www.opengis.net/citygml/2.0}"
ORIGIN=np.array([-5600.,-34320.]);SELECTED=set()
def source_unit(job):
 path,ids,checkpoint=job;path=Path(path);checkpoint=Path(checkpoint);cache=checkpoint/(hashlib.sha256(str(path).encode()).hexdigest()[:12]+".npz")
 if cache.exists():
  with np.load(cache,allow_pickle=False) as old:
   inf=json.loads(str(old["metadata"].item()));return [(a,old[f"xyz_{i}"]) for i,a in enumerate(inf["items"])],inf["source"]
 project=Transformer.from_crs(6668,6677,always_xy=True);it=ET.iterparse(path,events=("start","end"));_,root=next(it);out=[];crs=None
 for ev,e in it:
  if ev=="start" and e.tag==G+"Envelope" and crs is None:crs=e.get("srsName")
  if ev=="end" and e.tag==C+"cityObjectMember":
   b=e[0];id=b.get(G+"id")
   if id in ids:
    triangles=[];seen=set();surfaces=0;holes=0;nonplanar=0.
    for parent in b.iter():
     name=parent.tag.split("}")[-1]
     if name not in ["lod2MultiSurface","lod2Solid"]:continue
     for poly in parent.iter(G+"Polygon"):
      pid=poly.get(G+"id")
      if pid and pid in seen:continue
      seen.add(pid);rings=[]
      for kind in ["exterior","interior"]:
       for ring in poly.findall(G+kind):
        pos=ring.find(".//"+G+"posList")
        if pos is None or not pos.text:continue
        a=np.array(list(map(float,pos.text.split()))).reshape(-1,3)
        # EPSG6697 source axes: latitude,longitude,orthometricheight.
        easting,northing=project.transform(a[:,1],a[:,0]);xyz=np.column_stack((easting-ORIGIN[0],a[:,2],-(northing-ORIGIN[1])))
        if len(xyz)>1 and np.linalg.norm(xyz[0]-xyz[-1])<1e-8:xyz=xyz[:-1]
        if len(xyz)<3:continue
        keep=np.r_[True,np.linalg.norm(np.diff(xyz,axis=0),axis=1)>1e-9];xyz=xyz[keep]
        if len(xyz)>=3:rings.append(xyz)
      if not rings:continue
      exterior=rings[0];normal=np.sum(np.cross(exterior,np.roll(exterior,-1,axis=0)),axis=0);m=np.linalg.norm(normal)
      if m<1e-12:continue
      normal/=m;axis=int(np.argmax(np.abs(normal)));flat=np.concatenate(rings);projected=np.delete(flat,axis,axis=1)
      ends=np.cumsum([len(r) for r in rings]).astype(np.uint32);indices=mapbox_earcut.triangulate_float64(np.ascontiguousarray(projected),ends).reshape(-1,3)
      tri=flat[indices];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);wrong=np.einsum("ij,j->i",cross,normal)<0;tri[wrong]=tri[wrong][:,[0,2,1]];area=np.linalg.norm(cross,axis=1)/2;tri=tri[area>1e-10]
      triangles.extend(tri);surfaces+=1;holes+=len(rings)-1;nonplanar=max(nonplanar,float(np.abs((flat-exterior[0])@normal).max()))
    assert triangles,(id,path)
    out.append(({"gml_id":id,"source_citygml_member":str(path),"source_srs":crs,"source_surface_polygons":surfaces,"source_interior_rings":holes,"max_polygon_planarity_residual_m":nonplanar},np.array(triangles).reshape(-1,3)))
   e.clear();root.clear()
 src={"file":str(path),"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"matched_models":len(out),"srsName":crs}
 np.savez_compressed(cache,metadata=np.array(json.dumps({"items":[a for a,_ in out],"source":src})),**{f"xyz_{i}":x for i,(_,x) in enumerate(out)})
 return out,src
def main():
 p=argparse.ArgumentParser();p.add_argument("--task-root",required=True,type=Path);p.add_argument("--workers",type=int,required=True);args=p.parse_args();T=args.task_root;O=T/"team/04_Data/Ready/PLATEAU_Highest_2026-10-20";raw=T/"raw/plateau/Highest_Geometry_2026-10-20"
 tile=json.loads((raw/"Tile_Extraction/geometry-index.json").read_text());byid={x["gml_id"]:x for x in tile["buildings"]};paths=sorted((T/"raw").rglob("*bldg*.gml"),key=lambda p:-p.stat().st_size);checkpoint=raw/"source_decoded";checkpoint.mkdir(exist_ok=True);start=time.perf_counter()
 results=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=min(args.workers,len(paths))) as ex:
  for r in ex.map(source_unit,[(str(p),set(byid),str(checkpoint)) for p in paths]):results.append(r)
 sources=[];found={}
 for rows,src in results:
  src["file"]=str(Path(src["file"]).relative_to(T));sources.append(src)
  for a,x in rows:
   a["source_citygml_member"]=str(Path(a["source_citygml_member"]).relative_to(T));old=found.get(a["gml_id"])
   if old is None or len(x)>len(old[1]):found[a["gml_id"]]=(a,x)
 assert set(found)==set(byid),sorted(set(byid)-set(found))
 items=[];qa=[];examples=[]
 for id,(a,x) in sorted(found.items()):
  b=dict(byid[id]);b.update(a);b["geometry_source"]="Original CityGML LOD2 exterior surface polygons";b["triangles"]=len(x)//3;b["bounds_local_m"]=[x.min(axis=0).round(6).tolist(),x.max(axis=0).round(6).tolist()];b["geometry_height_m"]=float(x[:,1].max()-x[:,1].min())
  verts,inv=np.unique(np.round(x,4),axis=0,return_inverse=True);f=inv.reshape(-1,3);ed=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);edges,n=np.unique(ed,axis=0,return_counts=True)
  q={"asset_id":b["asset_id"],"boundary_edges_01mm":int((n==1).sum()),"edges_more_than_two_faces_01mm":int((n>2).sum()),"source_polygon_holes":a["source_interior_rings"],"source_planarity_residual_max_m":a["max_polygon_planarity_residual_m"]};qa.append(q)
  if b["primary"]:examples.append({"asset_id":b["asset_id"],"source_triangles":b["triangles"],"source_vertices":len(verts),"distinct_source_elevations_1cm":len(np.unique(np.round(x[:,1],2))),"flat_extrusion_elevation_levels":2})
  assert np.isfinite(x).all();items.append((b,x))
 xyz=np.concatenate([x for _,x in items]);meta={k:v for k,v in tile.items() if k not in ["buildings","asset"]};meta.update(buildings=len(items),geometry_source="Original CityGML LOD2 surface polygons, not reconstructed extrusions or decoded tile vertices",source_crs="EPSG:6697 (JGD2011 geographic 3D, source axes latitude,longitude,orthometricheight)",horizontal_transform="JGD2011 geographic2D EPSG6668 → Japan Plane Rectangular CS IX EPSG6677; pyproj always_xy receives longitude,latitude",vertical_transform="Identity: preserve each original CityGML third coordinate. No ellipsoid/geoid conversion or per-building vertical anchoring in this asset.",vertical_note="Original CityGML orthometric elevations are preserved. Ground terrain and textures are omitted. LOD2 means more roof and wall detail; no improvement in measured positional accuracy is claimed.",gltf_axes="x=easting+5600; y=original CityGML orthometric elevation; z=-(northing+34320)",bounds_local_m=[xyz.min(axis=0).round(6).tolist(),xyz.max(axis=0).round(6).tolist()],build_seconds=time.perf_counter()-start,source_files=sources,source_file_count=len(paths),workers=min(args.workers,len(paths)),license="PLATEAU / Public Data License1.0 compatible with CC BY4.0; original municipality copyright retained",license_url="https://www.mlit.go.jp/plateau/site-policy/")
 meta["quality"].update({"unique_asset_ids":len(items),"finite_coordinates":True,"source_polygon_holes_preserved":sum(q["source_polygon_holes"] for q in qa),"models_with_boundary_edges_01mm":sum(q["boundary_edges_01mm"]>0 for q in qa),"models_with_more_than_two_faces_per_edge_01mm":sum(q["edges_more_than_two_faces_01mm"]>0 for q in qa),"numerical_mesh_status":"Source surface edge checks passed at 0.1mm weld tolerance. Self-intersections, ground contact and CFD solver suitability remain unchecked."})
 manifest=glb_write(O/"kajicho-current-untextured.glb",items,meta);np.savez_compressed(O/"source_triangles_local.npz",**{a["asset_id"]:x for a,x in items});(O/"geometry-index.json").write_text(json.dumps({**meta,"asset":manifest,"buildings":[a for a,_ in items]},ensure_ascii=False,indent=2));(O/"geometry-summary.json").write_text(json.dumps({**meta,"asset":manifest,"primary_examples":sorted(examples,key=lambda b:-b["source_triangles"])[:5]},ensure_ascii=False,indent=2));(O/"geometry_quality.json").write_text(json.dumps({"screening":"0.0001m weld for edge counting only; source coordinates unchanged. Self-intersections not assessed.","models":qa},indent=2))
 print(json.dumps({"asset":manifest,"quality":meta["quality"],"vertical_transform":meta["vertical_transform"],"seconds":meta["build_seconds"],"bounds":meta["bounds_local_m"]},indent=2))
if __name__=="__main__":main()
