#!/usr/bin/env python3
"""Record solver exit separately from convergence and conservation evidence."""
import json,re,sys
from pathlib import Path
from datetime import datetime,timezone
b=Path(sys.argv[1]);record={'checked_utc':datetime.now(timezone.utc).isoformat(),'cases':{}}
for name in ['baseline','retrofit']:
 s=(b/'logs'/f'solver_{name}.log').read_text()
 rows=(b/'cases'/name/'postProcessing/roofHeatBalance.csv').read_text().splitlines()
 last=[float(x) for x in rows[-1].split(',')]
 error=abs(last[3])/max(abs(last[1]),1)
 record['cases'][name]={'last_iteration':float(re.findall(r'^Time = (.+)$',s,re.M)[-1]),
  'normal_end':'Finalising parallel run' in s and 'FOAM FATAL' not in s,
  'SIMPLE_residual_control_reached':'SIMPLE solution converged' in s,
  'relative_heat_imbalance':error,'heat_balance_passed':error<.01,
  'heated_roof_area_m2':last[5],'roof_input_W':last[1],
  'interpretation':'Exit, residual convergence and heat conservation are separate checks; street stability and sensitivity remain necessary.'}
record['domain_independence']='not established by one paired case'
(b/'outputs/Result_Checks.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
