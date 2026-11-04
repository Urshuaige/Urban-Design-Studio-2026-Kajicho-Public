#!/usr/bin/env python3
"""Run one declared checkpoint of the single light concept pair.

No automatic extension, next case or publication. Each stage has its own log;
the acceptance checker sees only that stage, so old convergence messages cannot
be mistaken for a new normal end. Inspect hosts before every invocation.
"""
import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def cpu_set(text):
    result = set()
    for part in text.split(","):
        a, _, b = part.partition("-")
        result.update(range(int(a), int(b or a)+1))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case-directory", type=Path, required=True)
    p.add_argument("--scripts-directory", type=Path, required=True)
    p.add_argument("--image", required=True)
    p.add_argument("--ranks-per-case", type=int, required=True)
    p.add_argument("--cpu-set-baseline", required=True)
    p.add_argument("--cpu-set-retrofit", required=True)
    p.add_argument("--end-iteration", type=int, choices=[500, 1000, 2000], required=True)
    p.add_argument("--cases", nargs="+", choices=["baseline", "retrofit"], default=["baseline", "retrofit"])
    args = p.parse_args()
    b, scripts = args.case_directory.resolve(), args.scripts_directory.resolve()
    slots = {"baseline": args.cpu_set_baseline, "retrofit": args.cpu_set_retrofit}
    if cpu_set(slots["baseline"]) & cpu_set(slots["retrofit"]):
        raise ValueError("Paired CPU allocations overlap")
    if any(len(cpu_set(v)) < args.ranks_per_case for v in slots.values()) or "@sha256:" not in args.image:
        raise ValueError("Pass sufficient current CPU slots and the immutable image")
    mesh_status = json.loads((b / "outputs/Mesh_Status.json").read_text())
    if mesh_status["state"] != "preflight_passed":
        raise ValueError("Native mesh and street preflight must pass first")
    expected_probes = json.loads((b / "inputs/probes.json").read_text())
    if not (b / "cases/baseline").exists():
        if args.end_iteration != 500:
            raise ValueError("The first checkpoint is500")
        source = (scripts / "prepare_cfd_pair_v3.py").read_text()
        old = "for folder in ['system','constant','0']:shutil.copytree(mesh/folder,case/folder)"
        new = "for folder in ['system','0']:shutil.copytree(mesh/folder,case/folder)\n (case/'constant').symlink_to('../mesh_cartesian/constant')"
        if old not in source:
            raise ValueError("Pair template changed; review shared constant inputs")
        prepare = b / "prepare_light_pair.py"
        prepare.write_text(source.replace(old, new))
        subprocess.run([str(scripts.parent / "venv/bin/python"), str(prepare), str(b)], check=True)
        actual = json.loads((b / "inputs/probes.json").read_text())
        if actual != expected_probes:
            raise ValueError("Original probe positions changed during pair preparation")
    checkpoint = b / "outputs" / f"Checkpoint_{args.end_iteration}.json"
    if checkpoint.exists():
        raise FileExistsError("This declared checkpoint already has a record")
    record = {"started_utc": datetime.now(timezone.utc).isoformat(), "host": os.uname().nodename,
              "case_directory": str(b), "state": "running_checkpoint", "end_iteration": args.end_iteration,
              "image": args.image, "cases": {}, "automatic_next_checkpoint": False}
    def save():
        checkpoint.write_text(json.dumps(record, indent=2)+"\n")
        (b / "outputs/Trial_Status.json").write_text(json.dumps(record, indent=2)+"\n")
    jobs = []
    for name in args.cases:
        case = b / "cases" / name
        p = case / "system/decomposeParDict"
        p.write_text(re.sub(r"numberOfSubdomains\s+\d+", f"numberOfSubdomains {args.ranks_per_case}", p.read_text()))
        p = case / "system/controlDict"
        text = re.sub(r"endTime\s+\d+;", f"endTime {args.end_iteration};", p.read_text())
        text = re.sub(r"writeInterval\s+50;", "writeInterval 100;", text, count=1)
        p.write_text(text)
        if "linearUpwind" in (case / "system/fvSchemes").read_text():
            raise ValueError("This declared trial uses first-order upwind throughout")
        stage_log = b / "logs" / f"solver_{name}_{args.end_iteration}.log"
        if stage_log.exists():
            raise FileExistsError(stage_log)
        link = b / "logs" / f"solver_{name}.log"
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            raise ValueError("Unexpected unsaved stage log")
        link.symlink_to(stage_log.name)
        first = not (case / "processor0").exists()
        commands = ["cd /work/cases/"+name]
        if first:
            commands += [f"setExprFields -time 0 > /work/logs/initialize_{name}.log 2>&1",
                         f"decomposePar -force > /work/logs/decompose_{name}.log 2>&1"]
        commands += [shlex.join(["mpirun", "--bind-to", "none", "-np", str(args.ranks_per_case),
                                "buoyantBoussinesqSimpleFoam", "-parallel"])+f" > /work/logs/{stage_log.name} 2>&1"]
        script = "source /usr/lib/openfoam/openfoam2412/etc/bashrc\nset -e\n"+"\n".join(commands)
        container = f"kajicho-area-{b.name}-{name}"
        cmd = ["docker", "run", "--rm", "--name", container, "--entrypoint", "/bin/bash",
               "--user", f"{os.getuid()}:{os.getgid()}", "--cpuset-cpus", slots[name],
               "--memory", "48g", "--shm-size", "2g", "-v", f"{b}:/work:rw",
               "-v", f"{b}/cases/mesh_cartesian/constant:/work/cases/mesh_cartesian/constant:ro",
               args.image, "-lc", script]
        handle = (b / "logs" / f"container_{name}_{args.end_iteration}.log").open("w")
        process = subprocess.Popen(cmd, stdout=handle, stderr=subprocess.STDOUT)
        record["cases"][name] = {"container": container, "docker_client_pid": process.pid,
                                  "cpu_set": slots[name], "ranks": args.ranks_per_case,
                                  "solver_log": str(stage_log), "command": cmd}
        jobs.append((name, process, handle))
        save()
    for name, process, handle in jobs:
        code = process.wait()
        handle.close()
        record["cases"][name].update(exit_code=code, finished_utc=datetime.now(timezone.utc).isoformat())
        save()
    record.update(state="awaiting_checkpoint_review" if all(x.get("exit_code") == 0 for x in record["cases"].values()) else "failed",
                  finished_utc=datetime.now(timezone.utc).isoformat())
    save()
    print(json.dumps(record, indent=2))
    return 0 if record["state"] == "awaiting_checkpoint_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
