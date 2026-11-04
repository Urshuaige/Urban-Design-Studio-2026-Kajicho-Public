#!/usr/bin/env python3
"""Preserve a failed numerical trial and prepare a bounded startup on the same mesh.

Run once on mdx1 with both project solvers stopped. Physical inputs are unchanged.
"""
import json,sys,shutil,os,re,math
from pathlib import Path
B=Path(sys.argv[1]);history=B/'trials/01_linearupwind_unstable';assert not history.exists()
history.mkdir(parents=True)
for name in ['baseline','retrofit']:
 shutil.move(B/'cases'/name,history/name)
for p in (B/'logs').glob('*'):
 if p.is_file() and any(token in p.name for token in ['solver_','container_','decompose_','pair_']):
  (history/'logs').mkdir(exist_ok=True);shutil.move(p,history/'logs'/p.name)
old=history/'baseline'
for name in ['baseline','retrofit']:
 src=history/name;case=B/'cases'/name
 shutil.copytree(src/'constant',case/'constant',copy_function=os.link)
 for folder in ['system','0']:shutil.copytree(src/folder,case/folder)
 p=case/'system/fvSchemes';s=p.read_text().replace('bounded Gauss linearUpwind grad(U)','bounded Gauss upwind').replace('bounded Gauss linearUpwind grad(T)','bounded Gauss upwind');p.write_text(s)
 p=case/'system/fvSolution';s=p.read_text().replace('consistent yes;','consistent no;').replace('p_rgh .3','p_rgh .15').replace('U .4','U .1').replace('T .5','T .2').replace('k .5','k .3').replace('epsilon .5','epsilon .3').replace('relTol .05;smoother','relTol .01;smoother');p.write_text(s)
 p=case/'system/controlDict';s=p.read_text().replace('endTime 1000;','endTime 300;');p.write_text(s)
 # Initialize the domain with the same neutral log law used at the inlet.
 ustar=.41*2.5/math.log((35.3+.1)/.1);kin=ustar**2/math.sqrt(.09)
 (case/'system/setExprFieldsDict').write_text('''FoamFile {version 2.0;format ascii;class dictionary;object setExprFieldsDict;}
expressions (
 wind {field U;expression "vector(0,2.5*log((pos().z()+0.1)/0.1)/log(354),0)";keepPatches true;}
 tke {field k;expression "%g";keepPatches true;}
 dissipation {field epsilon;expression "%g/(0.41*(pos().z()+0.1))";keepPatches true;}
);
'''%(kin,ustar**3))
 (case/'case.foam').touch()
record={'trial':'stable startup','mesh_unchanged':True,'physics_unchanged':True,'prior_trial':'trials/01_linearupwind_unstable','prior_issue':'nonphysical local velocities outside core; prior fields rejected','startup':{'convection':'upwind U/T','SIMPLE':'standard, consistent no','relaxation':{'p_rgh':.15,'U':.1,'T':.2,'k':.3,'epsilon':.3},'initial_fields':'inlet-consistent neutral ABL','end_iteration':300},'acceptance':'finite fields, physically plausible velocity and probe trends; second-order continuation and heat balance still required'}
(B/'inputs/numerical_startup.json').write_text(json.dumps(record,indent=2));print(json.dumps(record),flush=True)
