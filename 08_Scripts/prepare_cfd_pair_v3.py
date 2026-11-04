#!/usr/bin/env python3
import json,sys,shutil,re
from pathlib import Path
from shapely.geometry import shape,Point
from shapely.ops import unary_union
B=Path(sys.argv[1]);mesh=B/'cases'/json.loads((B/'inputs/mesh_selection.json').read_text())['case'];s=json.loads((B/'inputs/scenario.json').read_text())
quality=json.loads((B/'inputs/mesh_quality.json').read_text());assert quality['accepted_for_exploratory_pair'],'mesh diagnosis required before solving'
features=json.loads((B/'inputs/cfd_buildings_local.geojson').read_text())['features'];obstacles=unary_union([shape(f['geometry']) for f in features]);core=shape(json.loads((B/'inputs/city.json').read_text())['boundary']);xmin,ymin,xmax,ymax=core.bounds
points=[]
for j in range(1,13):
 for i in range(1,9):
  x=xmin+i*(xmax-xmin)/9;y=ymin+j*(ymax-ymin)/13;pt=Point(x,y)
  if core.covers(pt) and obstacles.distance(pt)>1:points.append((x,y,1.5))
assert len(points)>=3,points
points=points[::max(1,len(points)//12)][:12]
(B/'inputs/probes.json').write_text(json.dumps(points,indent=2))
for name,albedo in [('baseline',s['baseline_albedo']),('retrofit',s['retrofit_albedo'])]:
 case=B/'cases'/name;assert not case.exists(),f'Will not overwrite existing solver case {case}'
 for folder in ['system','constant','0']:shutil.copytree(mesh/folder,case/folder)
 (case/'system/decomposeParDict').write_text('FoamFile {version 2.0;format ascii;class dictionary;object decomposeParDict;} numberOfSubdomains 32;method scotch;')
 T=case/'0/T';text=T.read_text();q=(1-albedo)*s['GHI_W_m2']*s['sensible_conversion_fraction']/s['rho_kg_m3'];text=re.sub(r'q uniform [^;]+;',f'q uniform {q};',text);T.write_text(text)
 control=case/'system/controlDict';text=control.read_text().replace('writeInterval 500;','writeInterval 50;').replace('writePrecision 8;','writePrecision 14;')
 probes='\n monitoringPoints {type probes;libs (sampling);writeControl timeStep;writeInterval 10;fields (U T);probeLocations ('+' '.join('(%g %g %g)'%p for p in points)+');}\n'
 balance=r'''
 roofHeatBalance {
  type coded; libs (utilityFunctionObjects); name roofHeatBalance;
  writeControl timeStep; writeInterval 20;
  codeInclude #{ #include <fstream> #};
  codeOptions #{ -I$(LIB_SRC)/finiteVolume/lnInclude -I$(LIB_SRC)/meshTools/lnInclude #};
  codeLibs #{ -lfiniteVolume -lmeshTools #};
  codeWrite #{
   const fvMesh& m=mesh();
   const volScalarField& Tf=m.lookupObject<volScalarField>("T");
   const volScalarField& at=m.lookupObject<volScalarField>("alphat");
   const surfaceScalarField& ph=m.lookupObject<surfaceScalarField>("phi");
   tmp<surfaceScalarField> dn=fvc::snGrad(Tf);
   scalar net=0,roof=0,mass=0,roofArea=0;
   forAll(m.boundary(),pi) {
    // Processor-patch counts differ by rank; collective sums use physical patches only.
    if(m.boundary()[pi].coupled()) continue;
    const scalarField alpha=at.boundaryField()[pi]+1.65e-5/.71;
    const scalar diff=-1.13*1006*gSum(alpha*dn().boundaryField()[pi]*m.magSf().boundaryField()[pi]);
    const scalar adv=1.13*1006*gSum(ph.boundaryField()[pi]*(Tf.boundaryField()[pi]-311.55));
    net+=diff+adv;mass+=gSum(ph.boundaryField()[pi]);
    if(m.boundary()[pi].name()=="buildings_coreRoofs") {roof=-diff;roofArea=gSum(m.magSf().boundaryField()[pi]);}
   }
   if(Pstream::master()) {
    fileName dir=m.time().globalPath()/"postProcessing";mkDir(dir);
    std::ofstream out((dir/"roofHeatBalance.csv").c_str(),std::ios::app);
    out.precision(14);out<<m.time().value()<<","<<roof<<","<<net+roof<<","<<net<<","<<mass<<","<<roofArea<<std::endl;
   }
  #};
 }
'''
 additions=('' if 'monitoringPoints {' in text else probes)+('' if 'roofHeatBalance {' in text else balance)
 idx=text.index('functions {')+len('functions {');text=text[:idx]+additions+text[idx:];control.write_text(text)
 (case/'case.foam').touch()
print('Prepared baseline / retrofit using the same checked mesh; probes',len(points),flush=True)
