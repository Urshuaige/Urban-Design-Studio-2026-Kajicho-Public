#!/usr/bin/env python3
"""Prepare one isolated domain comparison from audited, solver-local geometry.

Original CityGML and the completed v3 pair are read-only. The three cases differ
only in explicit context or lateral box extent; all share the global 64 m grid.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('root', type=Path)
parser.add_argument('case', choices=['complete6H_wide', 'continuous750m_wide', 'complete6H_sides'])
parser.add_argument('--host-label', default=None, help='Optional execution-host label for provenance')
args = parser.parse_args()
root = args.root.resolve()
case = root / args.case
assert not (case / 'cases').exists(), 'Existing mesh/solution will not be overwritten'
source = 'continuous750m10H' if args.case == 'continuous750m_wide' else 'complete6H'
shutil.copytree(root / 'candidate_inputs' / source / 'inputs', case / 'inputs', dirs_exist_ok=True)
(case / 'logs').mkdir(exist_ok=True)
plan = json.loads((case / 'inputs/sensitivity_plan.json').read_text())
idx = {'complete6H_wide': 0, 'continuous750m_wide': 1, 'complete6H_sides': 2}[args.case]
domain = json.loads((case / 'inputs/domain.json').read_text())
domain['domain_m'] = plan['cases'][idx]['domain_m']
x0, y0, x1, y1, z1 = domain['domain_m']
assert all(v % 64 == 0 for v in [x0, y0, x1, y1, z1])
xb0, yb0, xb1, yb1 = domain['built_bounds_m']
domain.update(upstream_clearance_m=yb0-y0, downstream_clearance_m=y1-yb1,
              side_clearance_m=min(xb0-x0, x1-xb1),
              top_clearance_above_tallest_m=z1-domain['Hmax_m'],
              projected_frontal_blockage_fraction=domain['projected_frontal_area_m2']/((x1-x0)*z1),
              mesh_alignment_m=64)
(case / 'inputs/domain.json').write_text(json.dumps(domain, indent=2))
# No sub-square-metre object is simplified. Other footprints retain the same
# 0.05/0.3 m core/context simplification as the published pair.
surface_code = (root / 'scripts/repair_cfd_surface_v3.py').read_text()
surface_code = surface_code.replace(
    "poly=poly.simplify(.05 if p['core'] else .3,preserve_topology=True)",
    "poly=poly.simplify(0 if poly.area<4 else (.05 if p['core'] else .3),preserve_topology=True)")
assert 'poly.area<4' in surface_code
(case / 'build_surface.py').write_text(surface_code)
subprocess.run([str(root / 'venv/bin/python'), '-u', str(case / 'build_surface.py'), str(case)], check=True)
subprocess.run([str(root / 'venv/bin/python'), str(root / 'scripts/build_openfoam_v3.py'), str(case), '--strict', '--cartesian'], check=True)
mesh = case / 'cases/mesh_cartesian'
p = mesh / 'system/decomposeParDict'
p.write_text(p.read_text().replace('numberOfSubdomains 64', 'numberOfSubdomains 72'))
p = mesh / 'system/snappyHexMeshDict'
s = p.read_text()
small = json.loads((case / 'inputs/small_object_refinement.json').read_text())
features = json.loads((case / 'inputs/cfd_buildings_local.geojson').read_text())['features']
from shapely.geometry import shape
lookup = {f['properties']['id']: f for f in features}
geometry, refinements, records = [], [], []
for i, item in enumerate(small):
    f = lookup[item['id']]
    gx0, gy0, gx1, gy1 = shape(f['geometry']).bounds
    h = f['properties']['height_m']
    name = f'smallObject{i}'
    b = [gx0-2, gy0-2, 0, gx1+2, gy1+2, h+1]
    geometry.append(f'{name} {{type searchableBox;min ({b[0]} {b[1]} {b[2]});max ({b[3]} {b[4]} {b[5]});}}')
    refinements.append(f'{name} {{mode inside;levels ((1e15 8));}}')
    records.append({'id': item['id'], 'bounds_m': b, 'target_cell_m': .25,
                    'requirement': 'Check actual context patch near this object after meshing; refinement request is not proof of representation.'})
needle = 'castellatedMeshControls {'
pos = s.index(needle)
before = s[:pos].rstrip()
assert before.endswith('}')
s = before[:-1] + '\n' + '\n'.join(geometry) + '\n}\n' + s[pos:]
needle = 'refinementRegions {'
s = s.replace(needle, needle+'\n'+'\n'.join(refinements), 1)
p.write_text(s)
(case / 'inputs/actual_refinement_request.json').write_text(json.dumps(records, indent=2))
# Use the recorded final numerical settings, rather than the builder's older
# provisional defaults. Both roofs start with the same bounded 50 iterations.
for name in ['fvSchemes', 'fvSolution', 'setExprFieldsDict']:
    shutil.copy2(root / 'reference_settings' / name, mesh / 'system' / name)
scenario = json.loads((case / 'inputs/scenario.json').read_text())
scenario.update(mesh_ranks=72, ranks_per_case=36, max_iterations=6000,
                warmup_iterations=50, host=args.host_label,
                interpretation='Domain comparison; no environmental effect is accepted before convergence and heat balance checks.')
(case / 'inputs/scenario.json').write_text(json.dumps(scenario, indent=2))
print(json.dumps({'case': args.case, 'objects': domain['total_buildings'], 'domain_m': domain['domain_m'], 'mesh_ranks':72, 'pair_ranks':36}), flush=True)
