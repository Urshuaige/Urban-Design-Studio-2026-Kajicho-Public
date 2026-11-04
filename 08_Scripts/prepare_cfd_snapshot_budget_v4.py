#!/usr/bin/env python3
"""Prepare an isolated native-OpenFOAM budget of a saved field, without solving.

Run on the chosen host. The launch mounts reference_directory at /reference:ro
and audit_directory at /audit:rw. Original fields and dictionaries stay intact.
The current-phi operator is a snapshot consistency check, not a reconstruction
of the pre-pressure-correction temperature equation used during the last step.
"""
import argparse
import json
import shutil
from pathlib import Path

CODE = r'''
const fvMesh& cm=mesh();
fvMesh& m=const_cast<fvMesh&>(cm);
volScalarField& T=const_cast<volScalarField&>(m.lookupObject<volScalarField>("T"));
volScalarField& at=const_cast<volScalarField&>(m.lookupObject<volScalarField>("alphat"));
const surfaceScalarField& ph=m.lookupObject<surfaceScalarField>("phi");
const scalar rhoCp=1.13*1006.0;
const scalar Tref=311.55;
volScalarField alphaEff
(
 IOobject("alphaEff",m.time().timeName(),m,IOobject::NO_READ,IOobject::NO_WRITE),
 at+dimensionedScalar("nuPr",dimViscosity,1.65e-5/.71)
);
at.correctBoundaryConditions();
alphaEff=at+dimensionedScalar("nuPr",dimViscosity,1.65e-5/.71);
T.correctBoundaryConditions();
tmp<volScalarField> divPhi=fvc::div(ph);
const scalarField theta(T.primitiveField()-Tref);
const scalar cb=rhoCp*gSum(m.V()*theta*divPhi().primitiveField());
const scalar absDivV=gSum(m.V()*mag(divPhi().primitiveField()));
const scalar maxTheta=gMax(mag(theta));
const scalar vtotal=gSum(m.V());
const scalar tmin=gMin(T.primitiveField());
const scalar tmax=gMax(T.primitiveField());
// No relaxation, solution, fvOptions or radiation is applied here. Those
// volume sources are absent in the reference case and checked in preparation.
fvScalarMatrix eq(fvm::div(ph,T)-fvm::laplacian(alphaEff,T));
tmp<scalarField> rr=eq.residual();
const scalar rawResidualSum=rhoCp*gSum(rr());
scalarField residual(rr());
scalar extraCoupled=0;
// In pinned OpenCFD2412, scalar residual() applies ldu interface terms and
// then addBoundarySource with couples=true. Remove its extra neighbour-source
// contribution once; the actual scalar solve uses couples=false.
forAll(T.boundaryField(),pi)
{
 if(!T.boundaryField()[pi].coupled()) continue;
 const tmp<scalarField> tn=T.boundaryField()[pi].patchNeighbourField();
 const scalarField& neighbour=tn();
 const scalarField& coefficient=eq.boundaryCoeffs()[pi];
 const labelUList& addr=m.lduAddr().patchAddr(pi);
 forAll(addr,facei)
 {
  const scalar value=coefficient[facei]*neighbour[facei];
  residual[addr[facei]]-=value;
  extraCoupled+=value;
 }
}
reduce(extraCoupled,sumOp<scalar>());
const scalar residualSum=rhoCp*gSum(residual);
const scalar residualAbs=rhoCp*gSum(mag(residual));
tmp<surfaceScalarField> dn=fvc::snGrad(T);
scalar net=0,roof=0,qnet=0;
std::ostringstream patches;
patches<<std::setprecision(17)<<"[";
bool first=true;
forAll(m.boundary(),pi)
{
 if(m.boundary()[pi].coupled()) continue;
 const scalar diff=-rhoCp*gSum(alphaEff.boundaryField()[pi]*dn().boundaryField()[pi]*m.magSf().boundaryField()[pi]);
 const scalar adv=rhoCp*gSum(ph.boundaryField()[pi]*(T.boundaryField()[pi]-Tref));
 const scalar q=gSum(ph.boundaryField()[pi]);
 const scalar area=gSum(m.magSf().boundaryField()[pi]);
 net+=diff+adv; qnet+=q;
 if(m.boundary()[pi].name()=="buildings_coreRoofs") roof=-diff;
 if(!first) patches<<",";
 first=false;
 patches<<"{\"patch\":\""<<m.boundary()[pi].name()<<"\",\"advective_outward_W\":"<<adv
        <<",\"diffusive_outward_W\":"<<diff<<",\"net_outward_W\":"<<adv+diff
        <<",\"volume_flow_m3_s\":"<<q<<",\"area_m2\":"<<area<<"}";
}
patches<<"]";
fileName dir=m.time().globalPath()/"postProcessing";
mkDir(dir);
// Per-rank largest unrelaxed operator residuals locate spatial concentrations.
std::vector<label> order(residual.size());
std::iota(order.begin(),order.end(),0);
const label keep=std::min<label>(8,order.size());
std::partial_sort(order.begin(),order.begin()+keep,order.end(),[&](label a,label b){return mag(residual[a])>mag(residual[b]);});
std::ofstream hot((dir/("snapshot_hotspots_rank"+Foam::name(Pstream::myProcNo())+".csv")).c_str());
hot<<std::setprecision(17)<<"rank,local_cell,x_m,y_m,z_m,volume_m3,theta_K,div_phi_s_1,unrelaxed_residual_W\n";
for(label j=0;j<keep;++j)
{
 const label i=order[j]; const vector& p=m.C()[i];
 hot<<Pstream::myProcNo()<<","<<i<<","<<p.x()<<","<<p.y()<<","<<p.z()<<","<<m.V()[i]
    <<","<<theta[i]<<","<<divPhi().primitiveField()[i]<<","<<rhoCp*residual[i]<<"\n";
}
if(Pstream::master())
{
 std::ofstream out((dir/"snapshot_budget.json").c_str());
 out<<std::setprecision(17)<<"{\"iteration\":"<<m.time().value()
    <<",\"rhoCp_J_m3K\":"<<rhoCp<<",\"Tref_K\":"<<Tref<<",\"fluid_volume_m3\":"<<vtotal
    <<",\"minimum_internal_T_K\":"<<tmin<<",\"maximum_internal_T_K\":"<<tmax
    <<",\"physical_net_outward_W\":"<<net<<",\"roof_input_W\":"<<roof
    <<",\"net_volume_flow_m3_s\":"<<qnet<<",\"bounded_correction_current_phi_W\":"<<cb
    <<",\"bounded_absolute_upper_bound_W\":"<<rhoCp*maxTheta*absDivV
    <<",\"sum_absolute_cell_volume_imbalance_m3_s\":"<<absDivV
    <<",\"unrelaxed_matrix_residual_sum_W\":"<<residualSum
    <<",\"unrelaxed_matrix_residual_L1_W\":"<<residualAbs
    <<",\"raw_fvMatrix_residual_sum_W\":"<<rawResidualSum
    <<",\"extra_coupled_neighbour_source_W\":"<<rhoCp*extraCoupled
    <<",\"closure_net_minus_bounded_plus_residual_W\":"<<net-cb+residualSum
    <<",\"patches\":"<<patches.str()<<"}\n";
}
'''


def prepare(reference, audit):
    reference, audit = reference.resolve(), audit.resolve()
    if audit.exists():
        raise FileExistsError(f"New audit directory required: {audit}")
    for name in ("baseline", "retrofit"):
        source = reference / "cases" / name
        if not (source / "6000/T").is_file():
            raise FileNotFoundError(source / "6000/T")
        for rel in ("constant/fvOptions", "system/fvOptions"):
            if (source / rel).is_file():
                raise ValueError(f"Review volume sources before use: {source / rel}")
        radiation = (source / "constant/radiationProperties").read_text()
        if "radiation off" not in radiation or "radiationModel none" not in radiation:
            raise ValueError("This budget assumes the recorded radiation-off case")
    for name in ("baseline", "retrofit"):
        source = reference / "cases" / name
        case = audit / name
        (case / "system").mkdir(parents=True)
        (case / "postProcessing").mkdir()
        for f in ("fvSchemes", "fvSolution", "decomposeParDict"):
            shutil.copy2(source / "system" / f, case / "system" / f)
        (case / "constant").symlink_to(f"/reference/cases/{name}/constant")
        (case / "6000").symlink_to(f"/reference/cases/{name}/6000")
        for p in source.glob("processor[0-9]*"):
            if p.is_dir():
                (case / p.name).symlink_to(f"/reference/cases/{name}/{p.name}")
        control = '''FoamFile {version 2.0;format ascii;class dictionary;object controlDict;}
application postProcess;startFrom startTime;startTime 6000;stopAt endTime;endTime 6000;deltaT 1;
writeControl timeStep;writeInterval 1;writeFormat binary;runTimeModifiable false;
libs ("libatmosphericModels.so");
functions {
 snapshotBudget {
  type coded;libs (utilityFunctionObjects);name snapshotBudget_v2;
  codeInclude #{
   #include "fvCFD.H"
   #include <fstream>
   #include <iomanip>
   #include <sstream>
   #include <vector>
   #include <numeric>
   #include <algorithm>
  #};
  codeOptions #{ -I$(LIB_SRC)/finiteVolume/lnInclude -I$(LIB_SRC)/meshTools/lnInclude #};
  codeLibs #{ -lfiniteVolume -lmeshTools #};
  codeExecute #{
'''+CODE+'''
  #};
 }
}
'''
        (case / "system/controlDict").write_text(control)
    manifest = {"reference": str(reference), "audit": str(audit), "time": 6000,
                "fields": ["T", "phi", "alphat"], "source_mount": "/reference:ro",
                "audit_mount": "/audit:rw", "action": "postProcess only; no solve or field write",
                "matrix_residual_method": "OpenCFD2412 scalar residual minus its extra coupled neighbour-source contribution; checked against physical boundary closure",
                "interpretation": "Current-final-phi unrelaxed operator; cannot recover the pre-pressure flux or last-step relaxation contribution."}
    (audit / "Manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps(manifest))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference_directory", type=Path)
    parser.add_argument("audit_directory", type=Path)
    args = parser.parse_args()
    prepare(args.reference_directory, args.audit_directory)
