import assert from 'node:assert/strict';
import fs from 'node:fs';
import katex from '../06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/vendor/katex/katex.mjs';

const data=JSON.parse(fs.readFileSync(new URL('../06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/data/cfd-numerical-checks.json',import.meta.url),'utf8'));
assert(data.runs.some(r=>r.key===data.default_run));
for(const run of data.runs){
 for(const lang of ['zh','en','ja'])assert(run.label[lang]?.trim());
 assert.equal(run.checks.policy.heat.relative_imbalance_max_exclusive,.01);
 assert.equal(run.checks.policy.history_window_iterations,200);
 for(const name of ['baseline','retrofit']){
  const points=run.heat[name],check=run.checks.cases[name];
  assert(points.length>10);
  for(let i=0;i<points.length;i++){
   assert(points[i].every(Number.isFinite));
   assert(points[i][1]>=0);
   assert(points[i][0]<=check.last_completed_iteration);
   if(i)assert(points[i][0]>points[i-1][0]);
  }
  assert.equal(points.at(-1)[0],check.heat.last_iteration);
  assert(Math.abs(points.at(-1)[1]-100*check.heat.latest_relative_imbalance)<1e-9);
 }
 assert.equal(run.checks.accepted_for_domain_comparisons,Object.values(run.checks.cases).every(c=>c.accepted));
}
for(const tex of ['\\eta_Q=\\frac{|P_{\\mathrm{net}}|}{P_{\\mathrm{roof}}},\\qquad \\eta_Q<0.01','\\eta_Q','P_{\\mathrm{net}}','P_{\\mathrm{roof}}']){
 assert(katex.renderToString(tex,{throwOnError:true,trust:false,output:'htmlAndMathml'}).includes('<math'));
}
console.log('Numerical guide: native heat histories, percent units, case checks and four MathML renders verified.');
