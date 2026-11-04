#!/usr/bin/env python3
"""Render the current ten PNG plates without recalculating metrics or GIS."""
import argparse,json,os,resource,concurrent.futures
from pathlib import Path
from shapely.geometry import shape
import build_study_atlas as a
def main():
 p=argparse.ArgumentParser();p.add_argument('--task-root',type=Path,required=True);p.add_argument('--workers',type=int,default=9);args=p.parse_args()
 root=args.task_root;out=root/'team/06_Outputs/Study_Area_2026-10-18';os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1');resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
 atlas=json.loads((out/'atlas.json').read_text());f=json.loads((out/'study_boundary_6677.geojson').read_text())['features'];bs={x['properties']['id']:(x['properties'],shape(x['geometry'])) for x in f}
 rows=[(x['properties'],shape(x['geometry'])) for x in json.loads((root/'team/04_Data/Ready/POI_OSM_2026-10-18/poi_6677.geojson').read_text())['features']]
 a._DATA=(a.b.read(root/'assets/assets.gpkg'),bs['study_area'][1],atlas['scopes']['study_area'],out,bs['study_area'][0],bs['primary_brief'][1],rows)
 with concurrent.futures.ProcessPoolExecutor(max_workers=min(args.workers,9)) as pool:atlas['plates']=list(pool.map(a.render,[-1]+list(range(len(a.THEMES)))))
 a.write(out/'atlas.json',atlas);print(json.dumps({'png_maps':len(atlas['plates']),'export_legend_wrap_columns':22,'new_cfd':False}))
if __name__=='__main__':main()

