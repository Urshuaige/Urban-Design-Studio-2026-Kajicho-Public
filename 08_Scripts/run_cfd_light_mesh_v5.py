#!/usr/bin/env python3
"""Generate and inspect one isolated light grid. Never launches a solver."""
import argparse
import json
import os
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case-directory", type=Path, required=True)
    p.add_argument("--scripts-directory", type=Path, required=True)
    p.add_argument("--image", required=True)
    p.add_argument("--ranks", type=int, required=True)
    p.add_argument("--cpu-set", required=True)
    args = p.parse_args()
    b, scripts = args.case_directory.resolve(), args.scripts_directory.resolve()
    manifest = json.loads((b / "inputs/Light_Manifest.json").read_text())
    if manifest["mesh_ranks"] != args.ranks or "@sha256:" not in args.image:
        raise ValueError("Use the prepared allocation and recorded immutable image")
    log = b / "logs/mesh_launcher.log"
    status = {"started_utc": datetime.now(timezone.utc).isoformat(), "host": os.uname().nodename,
              "case_directory": str(b), "state": "meshing", "ranks": args.ranks,
              "cpu_set": args.cpu_set, "image": args.image, "solver_started": False}
    def save():
        (b / "outputs/Mesh_Status.json").write_text(json.dumps(status, indent=2)+"\n")
    def docker(script, container):
        cmd = ["docker", "run", "--rm", "--name", container, "--entrypoint", "/bin/bash",
               "--user", f"{os.getuid()}:{os.getgid()}", "--cpuset-cpus", args.cpu_set,
               "--memory", "96g", "--shm-size", "4g", "-v", f"{b}:/work:rw",
               args.image, "-lc", "source /usr/lib/openfoam/openfoam2412/etc/bashrc\nset -e\n"+script]
        with log.open("a") as f:
            return subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT).returncode
    save()
    marker = b / "logs/mesh_completed_utc"
    if not marker.exists():
        script = "\n".join([
            "cd /work/cases/mesh_cartesian",
            "blockMesh > /work/logs/blockMesh.log 2>&1",
            "decomposePar -force -no-fields > /work/logs/decomposeMesh.log 2>&1",
            shlex.join(["mpirun", "--bind-to", "none", "-np", str(args.ranks), "snappyHexMesh", "-parallel", "-overwrite"])+" > /work/logs/snappyHexMesh.log 2>&1",
            shlex.join(["mpirun", "--bind-to", "none", "-np", str(args.ranks), "checkMesh", "-parallel", "-allTopology", "-allGeometry"])+" > /work/logs/checkMesh.log 2>&1",
            "reconstructParMesh -constant > /work/logs/reconstructMesh.log 2>&1"])
        if docker(script, "kajicho-light-mesh-v1"):
            status.update(state="failed_native_mesh", finished_utc=datetime.now(timezone.utc).isoformat())
            save()
            return 1
        marker.write_text(datetime.now(timezone.utc).isoformat()+"\n")
    status["state"] = "mesh_preflight"
    save()
    python = scripts.parent / "venv/bin/python"
    with (b / "logs/mesh_quality.json").open("w") as f:
        qcode = subprocess.run([str(python), str(scripts / "check_cfd_domain_mesh_v4.py"), str(b)], stdout=f, stderr=subprocess.STDOUT).returncode
    if qcode:
        status.update(state="failed_quality", finished_utc=datetime.now(timezone.utc).isoformat())
        save()
        return 1
    if docker("cd /work/cases/mesh_cartesian\npostProcess -dict system/StreetProbeDict -time 0 > /work/logs/street_probe_preflight.log 2>&1", "kajicho-light-street-check-v1"):
        status.update(state="failed_street_check_execution", finished_utc=datetime.now(timezone.utc).isoformat())
        save()
        return 1
    shutil.copy2(b / "cases/mesh_cartesian/postProcessing/street_probe_check.json", b / "inputs/street_probe_check.json")
    quality = json.loads((b / "inputs/mesh_quality.json").read_text())
    street = json.loads((b / "inputs/street_probe_check.json").read_text())
    status.update(mesh_quality=quality, street_check=street)
    passed = 2000000 <= quality["cells"] <= 4000000 and quality["accepted_for_exploratory_pair"]
    passed = passed and street["missing_probes"] == 0 and street["missing_road_samples"] == 0 and street["failed_links"] == 0
    passed = passed and street["samples"]-street["original_probes"] >= 50 and street["core_roof_area_m2"] > 0
    status.update(state="preflight_passed" if passed else "preflight_requires_review",
                  finished_utc=datetime.now(timezone.utc).isoformat(), solver_started=False)
    save()
    print(json.dumps(status, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
