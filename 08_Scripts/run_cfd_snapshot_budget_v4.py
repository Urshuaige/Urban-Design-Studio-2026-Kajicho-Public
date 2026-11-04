#!/usr/bin/env python3
"""Run a native snapshot budget in an isolated directory on a selected host.

This is not a CFD solver: postProcess loads only time6000 and does not advance
the reference. Inspect all hosts before invoking; pass the current allocation.
"""
import argparse
import json
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def cpus(text):
    result = set()
    for item in text.split(","):
        a, _, b = item.partition("-")
        result.update(range(int(a), int(b or a)+1))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-directory", type=Path, required=True)
    parser.add_argument("--audit-directory", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--ranks-per-case", type=int, required=True)
    parser.add_argument("--cpu-set-baseline", required=True)
    parser.add_argument("--cpu-set-retrofit", required=True)
    args = parser.parse_args()
    allocation = {"baseline": args.cpu_set_baseline, "retrofit": args.cpu_set_retrofit}
    if cpus(args.cpu_set_baseline) & cpus(args.cpu_set_retrofit):
        raise ValueError("Paired allocations overlap")
    if any(len(cpus(v)) < args.ranks_per_case for v in allocation.values()):
        raise ValueError("Allocation has fewer slots than ranks")
    if "@sha256:" not in args.image:
        raise ValueError("Use the recorded immutable image digest")
    reference, audit = args.reference_directory.resolve(), args.audit_directory.resolve()
    manifest = json.loads((audit / "Manifest.json").read_text())
    if manifest["reference"] != str(reference) or manifest["audit"] != str(audit):
        raise ValueError("Prepared manifest does not match these paths")
    logs = audit / "logs"
    logs.mkdir(exist_ok=True)
    status_path = audit / "Run_Status.json"
    if status_path.exists():
        raise FileExistsError("Use a new audit directory for another attempt")
    record = {"started_utc": datetime.now(timezone.utc).isoformat(), "host": os.uname().nodename,
              "state": "running", "image": args.image, "cases": {},
              "purpose": "saved-field unrelaxed thermal operator budget; no solve"}
    def save():
        status_path.write_text(json.dumps(record, indent=2)+"\n")
    jobs = []
    for name, slots in allocation.items():
        command = shlex.join(["mpirun", "--bind-to", "none", "-np", str(args.ranks_per_case),
                              "postProcess", "-parallel", "-case", "/audit/"+name, "-time", "6000",
                              "-fields", "(T phi alphat)"])
        script = "source /usr/lib/openfoam/openfoam2412/etc/bashrc\nset -e\nexec "+command
        container = "kajicho-snapshot6000-"+name
        cmd = ["docker", "run", "--rm", "--name", container, "--entrypoint", "/bin/bash",
               "--user", f"{os.getuid()}:{os.getgid()}", "--cpuset-cpus", slots,
               "--memory", "48g", "--shm-size", "2g", "-v", f"{reference}:/reference:ro",
               "-v", f"{audit}:/audit:rw", args.image, "-lc", script]
        handle = (logs / (name+".log")).open("w")
        process = subprocess.Popen(cmd, stdout=handle, stderr=subprocess.STDOUT)
        record["cases"][name] = {"container": container, "docker_client_pid": process.pid,
                                  "cpu_set": slots, "ranks": args.ranks_per_case, "command": cmd}
        jobs.append((name, process, handle))
        save()
    for name, process, handle in jobs:
        code = process.wait()
        handle.close()
        row = record["cases"][name]
        row.update(exit_code=code, finished_utc=datetime.now(timezone.utc).isoformat())
        result = audit / name / "postProcessing/snapshot_budget.json"
        row["output_present"] = result.is_file()
        if code == 0 and result.is_file():
            row["result"] = json.loads(result.read_text())
        save()
    record.update(state="completed" if all(r.get("exit_code") == 0 and r["output_present"] for r in record["cases"].values()) else "failed",
                  finished_utc=datetime.now(timezone.utc).isoformat())
    save()
    print(json.dumps(record, indent=2))
    return 0 if record["state"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
