#!/usr/bin/env python3
"""OpenCFD 2412 steady buoyant RANS pair: prescribed core-roof sensible heat.
All material/heat-conversion inputs are scenario assumptions; JMA is observation.
"""
import json,math,sys,shutil
from pathlib import Path
B=Path(sys.argv[1]);d=json.loads((B/'inputs/domain.json').read_text());cartesian='--cartesian' in sys.argv;fields_only='--fields-only' in sys.argv;strict='--strict' in sys.argv or cartesian;case=B/('cases/mesh_cartesian' if cartesian else 'cases/mesh_strict' if strict else 'cases/mesh');(case/'system').mkdir(parents=True,exist_ok=True);(case/'constant/triSurface').mkdir(parents=True,exist_ok=True)
if not fields_only:shutil.copyfile(B/'inputs/buildings.stl',case/'constant/triSurface/buildings.stl')
def header(obj,cls='dictionary'):return f'FoamFile {{ version 2.0; format ascii; class {cls}; object {obj}; }}\n'
def put(path,body,cls='dictionary'):
 if fields_only and not str(path).startswith('0/'):return
 p=case/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(header(p.name,cls)+body)
x0,y0,x1,y1,z1=d['domain_m'];nx=math.ceil((x1-x0)/64);ny=math.ceil((y1-y0)/64);nz=math.ceil(z1/64);xc0,yc0,xc1,yc1=d['core_bounds_m'];xb0,yb0,xb1,yb1=d['built_bounds_m']
put('system/blockMeshDict',f'''scale 1;
vertices (({x0} {y0} 0) ({x1} {y0} 0) ({x1} {y1} 0) ({x0} {y1} 0) ({x0} {y0} {z1}) ({x1} {y0} {z1}) ({x1} {y1} {z1}) ({x0} {y1} {z1}));
blocks (hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading (1 1 1)); edges ();
boundary (inlet {{type patch;faces ((0 1 5 4));}} outlet {{type patch;faces ((3 7 6 2));}} sides {{type symmetry;faces ((0 4 7 3) (1 2 6 5));}} ground {{type wall;faces ((0 3 2 1));}} top {{type symmetryPlane;faces ((4 5 6 7));}});mergePatchPairs ();''')
put('system/decomposeParDict','numberOfSubdomains 64; method scotch;')
put('system/surfaceFeatureExtractDict','buildings.stl { extractionMethod extractFromSurface; extractFromSurfaceCoeffs { includedAngle 150; } writeObj no; }')
put('system/snappyHexMeshDict',f'''
castellatedMesh true; snap true; addLayers false;
geometry {{ buildings.stl {{type triSurfaceMesh;name buildings;}}
 coreVolume {{type searchableBox;min ({xc0-40} {yc0-40} 0);max ({xc1+40} {yc1+40} 70);}}
 pedestrian {{type searchableBox;min ({xc0-15} {yc0-15} 0);max ({xc1+15} {yc1+15} 2.5);}} }}
castellatedMeshControls {{ maxLocalCells 1000000; maxGlobalCells 12000000; minRefinementCells 0; maxLoadUnbalance 0.1; nCellsBetweenLevels 3;
 features (); refinementSurfaces {{ buildings {{level (3 3);patchInfo {{type wall;}} regions {{coreRoofs {{level (6 6);patchInfo {{type wall;}}}} coreWalls {{level (6 6);patchInfo {{type wall;}}}} }} }} }}
 resolveFeatureAngle 30; refinementRegions {{ coreVolume {{mode inside;levels ((1e15 5));}} pedestrian {{mode inside;levels ((1e15 7));}} }}
 locationInMesh ({x0+100} {y0+100} 30); allowFreeStandingZoneFaces true; }}
snapControls {{nSmoothPatch 3;tolerance 2.0;nSolveIter 30;nRelaxIter 5;nFeatureSnapIter 5;implicitFeatureSnap true;explicitFeatureSnap false;multiRegionFeatureSnap false;}}
addLayersControls {{relativeSizes true;layers {{}};expansionRatio 1.2;finalLayerThickness .3;minThickness .1;nGrow 0;featureAngle 60;nRelaxIter 5;nSmoothSurfaceNormals 1;nSmoothNormals 3;nSmoothThickness 10;maxFaceThicknessRatio .5;maxThicknessToMedialRatio .3;minMedianAxisAngle 90;nBufferCellsNoExtrude 0;nLayerIter 50;}}
meshQualityControls {{maxNonOrtho 65;maxBoundarySkewness 20;maxInternalSkewness 4;maxConcave 80;minVol 1e-15;minTetQuality 1e-30;minArea -1;minTwist .02;minDeterminant .001;minFaceWeight .02;minVolRatio .01;minTriangleTwist -1;nSmoothScale 4;errorReduction .75;}}
mergeTolerance 1e-6;''')
put('system/fvSchemes','''ddtSchemes {default steadyState;} gradSchemes {default cellLimited Gauss linear 1;}
divSchemes {default none;div(phi,U) bounded Gauss linearUpwind grad(U);div(phi,T) bounded Gauss linearUpwind grad(T);div(phi,k) bounded Gauss upwind;div(phi,epsilon) bounded Gauss upwind;div((nuEff*dev2(T(grad(U))))) Gauss linear;}
laplacianSchemes {default Gauss linear limited .5;} interpolationSchemes {default linear;} snGradSchemes {default limited .5;} wallDist {method meshWave;}''')
put('system/fvSolution','''solvers {p_rgh {solver GAMG;tolerance 1e-7;relTol .05;smoother DICGaussSeidel;nPreSweeps 0;nPostSweeps 2;cacheAgglomeration true;nCellsInCoarsestLevel 30;agglomerator faceAreaPair;mergeLevels 1;} "(U|T|k|epsilon)" {solver PBiCGStab;preconditioner DILU;tolerance 1e-7;relTol .05;}}
SIMPLE {nNonOrthogonalCorrectors 1;pRefCell 0;pRefValue 0;consistent yes;residualControl {p_rgh 1e-4;U 1e-4;T 1e-5;"(k|epsilon)" 1e-4;}}
relaxationFactors {fields {p_rgh .3;} equations {U .4;T .5;k .5;epsilon .5;}}''')
T=311.55;rho=1.13;Cp=1006;GHI=866.6666666667;fH=.2
put('constant/transportProperties',f'transportModel Newtonian;nu 1.65e-5;beta {1/T};TRef {T};Pr .71;Prt .85;rhoRef {rho};CpRef {Cp};')
put('constant/turbulenceProperties','simulationType RAS;RAS {RASModel kEpsilon;turbulence on;printCoeffs on;}')
put('constant/g','dimensions [0 1 -2 0 0 0 0]; value (0 0 -9.81);','uniformDimensionedVectorField')
put('constant/radiationProperties','radiation off;radiationModel none;')
abl='flowDir (0 1 0);zDir (0 0 1);Uref 2.5;Zref 35.3;z0 uniform .1;zGround uniform 0;d uniform 0;'
wall='"buildings.*"'
# Incompressible alphaEff has m2/s; heat q is normalized by rho before Cp division.
def field(name,dims,internal,bcs):put('0/'+name,'dimensions '+dims+';internalField uniform '+internal+';boundaryField {'+bcs+'}','volVectorField' if name=='U' else 'volScalarField')
field('U','[0 1 -1 0 0 0 0]','(0 2.5 0)',f'inlet {{type atmBoundaryLayerInletVelocity;{abl} value uniform (0 2.5 0);}} outlet {{type pressureInletOutletVelocity;value uniform (0 2.5 0);}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} ground {{type noSlip;}} {wall} {{type noSlip;}}')
field('p_rgh','[0 2 -2 0 0 0 0]','0',f'inlet {{type fixedFluxPressure;rho rhok;value uniform 0;}} outlet {{type fixedValue;value uniform 0;}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} ground {{type fixedFluxPressure;rho rhok;value uniform 0;}} {wall} {{type fixedFluxPressure;rho rhok;value uniform 0;}}')
field('p','[0 2 -2 0 0 0 0]','0','sides {type symmetry;} top {type symmetryPlane;} ".*" {type calculated;value uniform 0;}')
for name,dim,default,bc,wallbc in [('k','[0 2 -2 0 0 0 0]','.1','atmBoundaryLayerInletK','kqRWallFunction'),('epsilon','[0 2 -3 0 0 0 0]','.001','atmBoundaryLayerInletEpsilon','epsilonWallFunction')]:
 field(name,dim,default,f'inlet {{type {bc};{abl} value uniform {default};}} outlet {{type inletOutlet;inletValue uniform {default};value uniform {default};}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} ground {{type {wallbc};value uniform {default};}} {wall} {{type {wallbc};value uniform {default};}}')
field('nut','[0 2 -1 0 0 0 0]','0',f'inlet {{type calculated;value uniform 0;}} outlet {{type calculated;value uniform 0;}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} ground {{type atmNutkWallFunction;z0 uniform .1;value uniform 0;}} {wall} {{type nutkWallFunction;value uniform 0;}}')
field('alphat','[0 2 -1 0 0 0 0]','0',f'inlet {{type calculated;value uniform 0;}} outlet {{type calculated;value uniform 0;}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} ground {{type zeroGradient;}} {wall} {{type zeroGradient;}}')
q=(1-.2)*GHI*fH
field('T','[0 0 0 1 0 0 0]',str(T),f'inlet {{type fixedValue;value uniform {T};}} outlet {{type inletOutlet;inletValue uniform {T};value uniform {T};}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} ground {{type zeroGradient;}} buildings_coreRoofs {{type atmTurbulentHeatFluxTemperature;heatSource flux;alphaEff alphaEff;Cp0 {Cp};q uniform {q/rho};value uniform {T};}} "buildings_(coreWalls|context)" {{type zeroGradient;}}')
functions='''
 extrema {type fieldMinMax;libs (fieldFunctionObjects);fields (T U k epsilon);writeControl timeStep;writeInterval 20;}
 pedestrian {type surfaces;libs (sampling);writeControl writeTime;surfaceFormat raw;interpolationScheme cellPoint;fields (U T);surfaces {pedestrian {type cuttingPlane;planeType pointAndNormal;pointAndNormalDict {point (0 0 1.5);normal (0 0 1);}interpolate true;}}}
'''
for patch in ['inlet','outlet','buildings_coreRoofs']:
 functions+=f'\n {patch}MeanT {{type surfaceFieldValue;libs (fieldFunctionObjects);regionType patch;name {patch};operation areaAverage;fields (T);writeFields false;writeControl timeStep;writeInterval 20;}}'
 if patch in ['inlet','outlet']:
  functions+=f'\n {patch}FluxT {{type surfaceFieldValue;libs (fieldFunctionObjects);regionType patch;name {patch};operation weightedAverage;weightField phi;fields (T);writeFields false;writeControl timeStep;writeInterval 20;}}'
  functions+=f'\n {patch}Flow {{type surfaceFieldValue;libs (fieldFunctionObjects);regionType patch;name {patch};operation sum;fields (phi);writeFields false;writeControl timeStep;writeInterval 20;}}'
put('system/controlDict','application buoyantBoussinesqSimpleFoam;startFrom latestTime;startTime 0;stopAt endTime;endTime 1000;deltaT 1;writeControl timeStep;writeInterval 500;purgeWrite 1;writeFormat binary;writePrecision 8;writeCompression off;timeFormat general;runTimeModifiable true;libs ("libatmosphericModels.so");functions {'+functions+'}')
# Mesh control uses no solution fields, but preserve pair template before initial solve.
(B/'inputs/scenario.json').write_text(json.dumps({'case':'Cool roofs in Kajicho 1 & 2','weather_timestamp_jst':'2025-08-30T13:00:00+09:00','air_temperature_c':38.4,'wind_from_deg':180,'wind_speed_ms':2.5,'wind_reference_height_m':35.3,'GHI_W_m2':GHI,'baseline_albedo':.2,'retrofit_albedo':.6,'sensible_conversion_fraction':fH,'fH_sensitivity':[.1,.3],'baseline_roof_heat_W_m2':q,'retrofit_roof_heat_W_m2':(1-.6)*GHI*fH,'rho_kg_m3':rho,'Cp_J_kgK':Cp,'thermal_scope':'Core-roof imposed sensible heat; other surfaces adiabatic. Coupled Boussinesq buoyancy, no closed outdoor surface-energy model.','missing_core_trees':'same unmapped-tree assumption in pair','DECC':'pending user; no building energy savings inferred','ranks_per_case':32,'mesh_ranks':64},indent=2))
print('case generated',nx,ny,nz,nx*ny*nz,flush=True)
# A symmetry patch supports the two parallel lateral planes in one patch.
for p in (case/'0').iterdir():
 p.write_text(p.read_text().replace('sides {type symmetryPlane;}','sides {type symmetry;}'))
if strict and not fields_only:
 p=case/'system/snappyHexMeshDict';p.write_text(p.read_text().replace('maxBoundarySkewness 20','maxBoundarySkewness 4').replace('minFaceWeight .02','minFaceWeight .05'))
if cartesian and not fields_only:
 p=case/'system/snappyHexMeshDict';p.write_text(p.read_text().replace('snap true','snap false'))
if not fields_only:(B/'inputs/mesh_selection.json').write_text(json.dumps({'case':case.name,'strict_boundary_skewness':4 if strict else 20,'minimum_face_weight':.05 if strict else .02},indent=2))
