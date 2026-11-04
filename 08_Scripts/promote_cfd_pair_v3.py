#!/usr/bin/env python3
"""Continue both scenarios from the same saved checkpoint with final target schemes.

Run only with both project containers stopped; keep decomposed checkpoint fields.
"""
import json,sys,re
from pathlib import Path
B=Path(sys.argv[1]);checkpoint=int(sys.argv[2])
for name in ['baseline','retrofit']:
 case=B/'cases'/name
 for rank in range(32):assert (case/f'processor{rank}'/str(checkpoint)/'T').exists(),(name,rank,checkpoint)
 p=case/'system/fvSchemes';p.write_text(p.read_text().replace('div(phi,U) bounded Gauss upwind','div(phi,U) bounded Gauss linearUpwind grad(U)').replace('div(phi,T) bounded Gauss upwind','div(phi,T) bounded Gauss linearUpwind grad(T)'))
 (case/'system/fvSolution').write_text('''FoamFile {version 2.0;format ascii;class dictionary;object fvSolution;}
solvers {
 p_rgh {solver GAMG;tolerance 1e-7;relTol .01;smoother DICGaussSeidel;nPreSweeps 0;nPostSweeps 2;cacheAgglomeration true;nCellsInCoarsestLevel 30;agglomerator faceAreaPair;mergeLevels 1;}
 "(U|k|epsilon)" {solver PBiCGStab;preconditioner DILU;tolerance 1e-7;relTol .05;}
 T {solver PBiCGStab;preconditioner DILU;tolerance 1e-10;relTol .001;}
}
SIMPLE {nNonOrthogonalCorrectors 1;pRefCell 0;pRefValue 0;residualControl {p_rgh 1e-4;U 1e-4;T 1e-8;"(k|epsilon)" 1e-4;}}
relaxationFactors {fields {p_rgh .3;} equations {U .4;T .5;k .5;epsilon .5;}}
''')
 p=case/'system/controlDict';s=p.read_text();s=re.sub(r'endTime \d+;', 'endTime 1000;',s);p.write_text(s)
record={'checkpoint':checkpoint,'mesh_unchanged':True,'physical_conditions_unchanged':True,'advection':'second-order linearUpwind with cellLimited gradient','T_linear_tolerance':1e-10,'T_linear_relTol':.001,'T_outer_residual_target':1e-8,'reason':'resolve small roof-heat signal against absolute temperature; require heat balance separately','interpretation':'convergence, thermal balance and sensitivity still pending'}
(B/'inputs/numerical_continuation.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))
