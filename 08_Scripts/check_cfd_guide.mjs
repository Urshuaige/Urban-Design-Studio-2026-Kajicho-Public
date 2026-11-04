import assert from 'node:assert/strict';
import katex from '../06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/vendor/katex/katex.mjs';
import {lessons,symbols} from '../06_Outputs/Simulation_Demo/Kajicho_Wind_Heat_Carbon/dist/cfd-lessons.js';

let rendered=0;
for(const lesson of lessons){
  for(const tex of lesson.tex){
    const html=katex.renderToString(tex,{throwOnError:true,strict:'error',trust:false,output:'htmlAndMathml'});
    assert(html.includes('<math'), 'An equation needs accessible MathML');
    rendered++;
  }
  for(const key of lesson.keys)assert(symbols[key],`Undefined symbol: ${key}`);
  for(const field of ['plain','example','meaning']){
    assert.equal(lesson[field].length,3,`Missing lesson language: ${field}`);
    assert(lesson[field].every(s=>typeof s==='string'&&s.trim().length>0));
  }
}
for(const [key,row] of Object.entries(symbols)){
  assert.equal(row.length,5,`Symbol needs TeX, unit and three definitions: ${key}`);
  assert(row.every(s=>typeof s==='string'&&s.trim().length>0),`Empty symbol definition: ${key}`);
  katex.renderToString(row[0],{throwOnError:true,strict:'error',trust:false});
}
console.log(`CFD guide: ${rendered} equations render with MathML; ${Object.keys(symbols).length} symbols have units and three definitions.`);
