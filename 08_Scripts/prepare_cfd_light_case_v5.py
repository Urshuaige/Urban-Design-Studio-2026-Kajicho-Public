#!/usr/bin/env python3
"""Prepare one new concept case from preserved reference inputs, mesh only.

The source case is read-only. Both physical inputs and the air box are retained;
only refinement and the declared first-order advection recipe change.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path


def street_check(target, mesh):
    from shapely.geometry import LineString, shape
    from shapely.ops import unary_union
    city = json.loads((target / "inputs/city.json").read_text())
    core = shape(city["boundary"])
    features = json.loads((target / "inputs/cfd_buildings_local.geojson").read_text())["features"]
    obstacles = unary_union([shape(f["geometry"]) for f in features])
    probes = json.loads((target / "inputs/probes.json").read_text())
    points = [{"xyz": p, "role": "original_street_probe"} for p in probes]
    links = []
    for road_index, coords in enumerate(city["roads"]):
        line = LineString(coords).intersection(core)
        pieces = list(line.geoms) if line.geom_type == "MultiLineString" else [line]
        for piece_index, part in enumerate(pieces):
            if part.geom_type != "LineString" or part.length == 0:
                continue
            distances = [float(i*2) for i in range(int(part.length/2)+1)]
            if part.length-distances[-1] > 1e-6:
                distances.append(part.length)
            previous = None
            for along in distances:
                p = part.interpolate(along)
                if obstacles.distance(p) < 2:
                    previous = None
                    continue
                index = len(points)
                points.append({"xyz": [p.x, p.y, 1.5], "role": "road_air_sample",
                               "source_road_index": road_index, "piece": piece_index,
                               "distance_along_piece_m": along})
                if previous is not None:
                    links.append([previous, index])
                previous = index
    record = {"points": points, "links": links, "original_probe_count": len(probes),
              "road_interval_m": 2, "source_footprint_clearance_min_m": 2,
              "connectivity_check": "Local fluid-cell paths between consecutive eligible road samples; centres below3m, segment buffer3m, depth16.",
              "scope": "Native near-ground airflow connectivity along source-open road portions; not pedestrian accessibility or empirical validation."}
    (target / "inputs/street_probe_points.json").write_text(json.dumps(record, indent=2)+"\n")
    xyz = ",\n".join("point("+",".join(format(v, ".16g") for v in p["xyz"])+")" for p in points)
    pairs = ",".join("{"+str(a)+","+str(b)+"}" for a, b in links)
    body = r'''
const fvMesh& m=mesh();
const std::vector<point> pts={POINTS};
const std::vector<std::pair<label,label>> links={LINKS};
std::vector<label> cells;
for(const point& p:pts) cells.push_back(m.findCell(p));
const labelListList& adjacent=m.cellCells();
auto connected=[&](label a,label b)
{
 if(cells[a]<0 || cells[b]<0) return false;
 if(cells[a]==cells[b]) return true;
 scalar x0=std::min(pts[a].x(),pts[b].x())-3, x1=std::max(pts[a].x(),pts[b].x())+3;
 scalar y0=std::min(pts[a].y(),pts[b].y())-3, y1=std::max(pts[a].y(),pts[b].y())+3;
 std::queue<std::pair<label,label>> q;
 std::unordered_set<label> seen;
 q.push({cells[a],0}); seen.insert(cells[a]);
 while(!q.empty())
 {
  auto item=q.front(); q.pop();
  if(item.second>=16) continue;
  for(label c:adjacent[item.first])
  {
   const vector& p=m.C()[c];
   if(p.x()<x0 || p.x()>x1 || p.y()<y0 || p.y()>y1 || p.z()>3.000001) continue;
   if(c==cells[b]) return true;
   if(seen.insert(c).second) q.push({c,item.second+1});
  }
 }
 return false;
};
label missingProbes=0,missingRoad=0,failedLinks=0;
std::ostringstream missing,failed;
missing<<"["; failed<<"[";
for(label i=0;i<label(cells.size());++i)
 if(cells[i]<0)
 {
  if(missingProbes+missingRoad) missing<<",";
  missing<<i;
  if(i<PROBECOUNT) ++missingProbes; else ++missingRoad;
 }
for(const auto& link:links)
 if(!connected(link.first,link.second))
 {
  if(failedLinks++) failed<<",";
  failed<<"["<<link.first<<","<<link.second<<"]";
 }
missing<<"]";failed<<"]";
const label roof=m.boundaryMesh().findPatchID("buildings_coreRoofs");
const scalar area=roof>=0?gSum(m.magSf().boundaryField()[roof]):0;
fileName dir=m.time().globalPath()/"postProcessing";mkDir(dir);
std::ofstream out((dir/"street_probe_check.json").c_str());
out<<std::setprecision(17)<<"{\"cells\":"<<m.nCells()<<",\"samples\":"<<cells.size()
   <<",\"original_probes\":"<<PROBECOUNT<<",\"missing_probes\":"<<missingProbes
   <<",\"missing_road_samples\":"<<missingRoad<<",\"tested_road_links\":"<<links.size()
   <<",\"failed_links\":"<<failedLinks<<",\"core_roof_area_m2\":"<<area
   <<",\"missing_point_indices\":"<<missing.str()<<",\"failed_point_pairs\":"<<failed.str()<<"}\n";
'''.replace("POINTS", xyz).replace("LINKS", pairs).replace("PROBECOUNT", str(len(probes)))
    control = '''FoamFile {version 2.0;format ascii;class dictionary;object StreetProbeDict;}
application postProcess;startFrom startTime;startTime 0;stopAt endTime;endTime 0;deltaT 1;
writeControl timeStep;writeInterval 1;runTimeModifiable false;
functions {streetProbeCheck {type coded;libs (utilityFunctionObjects);name streetProbeCheck;
codeInclude #{
#include "fvCFD.H"
#include <fstream>
#include <iomanip>
#include <sstream>
#include <vector>
#include <utility>
#include <queue>
#include <unordered_set>
#include <algorithm>
#};
codeOptions #{ -I$(LIB_SRC)/finiteVolume/lnInclude -I$(LIB_SRC)/meshTools/lnInclude #};
codeLibs #{ -lfiniteVolume -lmeshTools #};
codeExecute #{
'''+body+'''
#};}}
'''
    (mesh / "system/StreetProbeDict").write_text(control)


def prepare(reference, target, scripts, mesh_ranks):
    reference, target, scripts = reference.resolve(), target.resolve(), scripts.resolve()
    if target.exists():
        raise FileExistsError(f"New case directory required: {target}")
    (target / "inputs").mkdir(parents=True)
    (target / "logs").mkdir()
    (target / "outputs").mkdir()
    required = ("cfd_buildings_local.geojson", "domain.json", "scenario.json", "city.json", "buildings.stl", "probes.json")
    for name in required:
        shutil.copy2(reference / "inputs" / name, target / "inputs" / name)
    for name in ("sensitivity_plan.json", "small_object_refinement.json"):
        p = reference / "inputs" / name
        if p.is_file():
            shutil.copy2(p, target / "inputs" / ("source_"+name))
    scenario = json.loads((reference / "inputs/scenario.json").read_text())
    subprocess.run([str(scripts.parent / "venv/bin/python"), str(scripts / "build_openfoam_v3.py"),
                    str(target), "--strict", "--cartesian"], check=True)
    mesh = target / "cases/mesh_cartesian"
    p = mesh / "system/decomposeParDict"
    p.write_text(p.read_text().replace("numberOfSubdomains 64", f"numberOfSubdomains {mesh_ranks}"))
    p = mesh / "system/snappyHexMeshDict"
    text = p.read_text()
    for old, new in (("coreVolume {mode inside;levels ((1e15 5));}", "coreVolume {mode inside;levels ((1e15 4));}"),
                     ("pedestrian {mode inside;levels ((1e15 7));}", "pedestrian {mode inside;levels ((1e15 6));}"),
                     ("maxGlobalCells 12000000", "maxGlobalCells 6000000")):
        if old not in text:
            raise ValueError("Builder changed: "+old)
        text = text.replace(old, new)
    p.write_text(text)
    for name in ("fvSchemes", "fvSolution", "setExprFieldsDict"):
        shutil.copy2(reference / "cases/baseline/system" / name, mesh / "system" / name)
    p = mesh / "system/fvSchemes"
    text = p.read_text().replace("bounded Gauss linearUpwind grad(U)", "bounded Gauss upwind").replace("bounded Gauss linearUpwind grad(T)", "bounded Gauss upwind")
    p.write_text(text)
    # This file lists current explicit micro-refinement requests, not source
    # objects. Their original IDs remain in the geometry and source inventory.
    (target / "inputs/small_object_refinement.json").write_text("[]\n")
    original_micro = reference / "inputs/small_object_refinement.json"
    micro = json.loads(original_micro.read_text()) if original_micro.is_file() else []
    (target / "inputs/mesh_resolution_inventory.json").write_text(json.dumps({
        "source_small_objects": micro, "quarter_metre_refinement_requested": False,
        "status": "native representation not yet checked; unresolved objects will be recorded",
        "source_building_objects_retained": 3806}, indent=2)+"\n")
    scenario.update(case="Kajicho concept demonstration, first-order light grid",
                    max_iterations=2000, review_iterations=[500, 1000],
                    advection_scheme="bounded Gauss upwind", numerical_order=1,
                    interpretation="Fixed-scenario feasibility trial; numerical, mesh/domain and empirical checks remain distinct.")
    (target / "inputs/scenario.json").write_text(json.dumps(scenario, indent=2)+"\n")
    street_check(target, mesh)
    manifest = {"reference": str(reference), "target": str(target), "source_preserved": True,
                "cell_target": [2000000, 4000000], "pedestrian_band_m": 1,
                "core_bulk_m": 4, "core_surface_m": 1,
                "near_surface_transition_m": [1, 2, 4], "small_object_quarter_metre": False,
                "scheme": "bounded Gauss upwind", "physical_change_between_pair": "roof albedo only",
                "mesh_ranks": mesh_ranks,
                "solver_started": False, "next_action": "generate and inspect the new native mesh"}
    (target / "inputs/Light_Manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps(manifest))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("scripts", type=Path)
    parser.add_argument("--mesh-ranks", type=int, required=True)
    args = parser.parse_args()
    prepare(args.reference, args.target, args.scripts, args.mesh_ranks)
