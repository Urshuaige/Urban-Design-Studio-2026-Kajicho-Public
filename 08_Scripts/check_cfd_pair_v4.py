#!/usr/bin/env python3
"""Read a paired case without changing solver files or process state.

Normal exit, outer convergence, heat conservation and probe stability are
independent checks. The caller decides whether to launch the next experiment.
"""
import argparse
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
RESIDUAL = re.compile(r"Solving for (\w+), Initial residual = (" + NUMBER + r"), Final residual = (" + NUMBER + r")")


def numeric_rows(path, columns=None):
    rows = {}
    if not path.is_file():
        return rows
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            row = [float(x) for x in line.split(",")]
        except ValueError:
            continue
        if (columns is None or len(row) == columns) and all(math.isfinite(x) for x in row):
            rows[row[0]] = row
    return rows


def probe_rows(case, field, count):
    rows = {}
    errors = []
    root = case / "postProcessing/monitoringPoints"
    paths = [p for p in root.glob("*/" + field) if re.fullmatch(NUMBER, p.parent.name)]
    for path in sorted(paths, key=lambda p: float(p.parent.name)):
        for line in path.read_text().splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            values = [float(x) for x in re.findall(NUMBER, line)]
            wanted = 1 + count * (3 if field == "U" else 1)
            if len(values) != wanted or not all(math.isfinite(x) and abs(x) < 1e100 for x in values):
                errors.append({"file": str(path), "iteration": values[0] if values else None})
                continue
            rows[values[0]] = values[1:]
    return rows, errors


def stable_probes(case, count, last_iteration, policy):
    u, u_errors = probe_rows(case, "U", count)
    t, t_errors = probe_rows(case, "T", count)
    interval = policy["probes"]["sample_interval_iterations"]
    window = policy["history_window_iterations"]
    common = sorted(x for x in u.keys() & t.keys() if x <= last_iteration)
    end = common[-1] if common else None
    times = [x for x in common if x >= end - window] if end is not None else []
    coverage = bool(times) and end - times[0] >= window and last_iteration - end <= interval
    coverage = coverage and all(b - a <= interval + 1e-9 for a, b in zip(times, times[1:]))
    errors = [x for x in u_errors + t_errors if x["iteration"] is None or (times and times[0] <= x["iteration"] <= last_iteration)]
    result = {"passed": False, "expected_probes": count, "history_coverage": coverage, "invalid_tail_rows": errors,
              "first_iteration": times[0] if times else None, "last_iteration": end, "samples": len(times)}
    if not coverage or errors:
        return result
    speed = [[math.sqrt(sum(v * v for v in u[x][3 * i:3 * i + 3])) for i in range(count)] for x in times]
    temp = [t[x] for x in times]
    half = end - window / 2
    first = [i for i, x in enumerate(times) if x <= half]
    second = [i for i, x in enumerate(times) if x > half]
    def drift(values):
        a = sum(sum(values[i]) / count for i in first) / len(first)
        b = sum(sum(values[i]) / count for i in second) / len(second)
        return abs(b - a)
    def spread(values):
        return max(max(row[i] for row in values) - min(row[i] for row in values) for i in range(count))
    p = policy["probes"]
    metrics = {"half_window_mean_speed_change_ms": drift(speed), "half_window_mean_temperature_change_K": drift(temp),
               "maximum_probe_speed_peak_to_peak_ms": spread(speed), "maximum_probe_temperature_peak_to_peak_K": spread(temp)}
    limits = [p["half_window_mean_speed_change_max_ms"], p["half_window_mean_temperature_change_max_K"],
              p["per_probe_speed_peak_to_peak_max_ms"], p["per_probe_temperature_peak_to_peak_max_K"]]
    result.update(metrics)
    result["passed"] = all(v <= limit for v, limit in zip(metrics.values(), limits))
    result["interpretation"] = "Equal-weight probe stability; not an areal street average or empirical validation."
    return result


def solver_controls(case, policy):
    path = case / "system/fvSolution"
    text = path.read_text() if path.is_file() else ""
    match = re.search(r"residualControl\s*\{([^}]+)\}", text)
    actual = {}
    if match:
        for field, value in re.findall(r'("[^"\n]+"|\w+)\s+(' + NUMBER + r')\s*;', match.group(1)):
            names = ("k", "epsilon") if field == '"(k|epsilon)"' else (field.strip('"'),)
            for name in names:
                actual[name] = float(value)
    targets = policy["outer_initial_residual_targets"]
    passed = all(name in actual and actual[name] <= target for name, target in targets.items())
    return {"passed": passed, "actual_outer_targets": actual, "required_outer_targets": targets}


def inspect_case(base, name, policy, scenario, probe_count):
    path = base / "logs" / f"solver_{name}.log"
    if not path.is_file():
        return {"accepted": False, "phase": "solver log absent"}
    text = path.read_text()
    blocks = re.split(r"^Time = (.+)$", text, flags=re.M)
    completed = []
    started = []
    for i in range(1, len(blocks), 2):
        iteration = float(blocks[i])
        started.append(iteration)
        block = blocks[i + 1]
        if "ExecutionTime =" in block:
            initial = {}
            final = {}
            for field, a, b in RESIDUAL.findall(block):
                initial.setdefault(field, float(a))
                final[field] = float(b)
            completed.append((iteration, initial, final))
    last = completed[-1][0] if completed else 0
    residuals = completed[-1][1] if completed else {}
    normal = "Finalising parallel run" in text and "FOAM FATAL" not in text
    converged = "SIMPLE solution converged" in text
    rows = numeric_rows(base / "cases" / name / "postProcessing/roofHeatBalance.csv", 6)
    times = sorted(x for x in rows if x <= last)
    end = times[-1] if times else None
    window = policy["history_window_iterations"]
    tail = [rows[x] for x in times if x >= end - window] if end is not None else []
    interval = policy["heat"]["diagnostic_interval_iterations"]
    coverage = bool(tail) and tail[-1][0] - tail[0][0] >= window and last - end <= interval
    coverage = coverage and all(b[0] - a[0] <= interval + 1e-9 for a, b in zip(tail, tail[1:]))
    albedo = scenario["baseline_albedo"] if name == "baseline" else scenario["retrofit_albedo"]
    q = (1 - albedo) * scenario["GHI_W_m2"] * scenario["sensible_conversion_fraction"]
    imbalance = [abs(row[3]) / abs(row[1]) if row[1] > 0 else None for row in tail]
    input_errors = [abs(row[1] - q * row[5]) / max(abs(q * row[5]), 1) for row in tail]
    heat_pass = coverage and all(x is not None and x < policy["heat"]["relative_imbalance_max_exclusive"] for x in imbalance)
    heat_pass = heat_pass and all(x <= policy["heat"]["roof_input_relative_error_max"] for x in input_errors)
    heat = {"passed": bool(heat_pass), "history_coverage": coverage, "window_iterations": window,
            "first_iteration": tail[0][0] if tail else None, "last_iteration": end,
            "latest_relative_imbalance": imbalance[-1] if imbalance else None,
            "maximum_tail_relative_imbalance": max(imbalance) if imbalance and all(x is not None for x in imbalance) else None,
            "maximum_roof_input_relative_error": max(input_errors) if input_errors else None,
            "latest_row": tail[-1] if tail else None}
    probes = stable_probes(base / "cases" / name, probe_count, last, policy)
    controls = solver_controls(base / "cases" / name, policy)
    accepted = normal and converged and controls["passed"] and heat_pass and probes["passed"]
    return {"accepted": bool(accepted), "last_started_iteration": started[-1] if started else None,
            "last_completed_iteration": last, "fatal": "FOAM FATAL" in text, "normal_end": normal,
            "SIMPLE_residual_control_reached": converged, "latest_initial_residuals": residuals,
            "latest_linear_final_residuals": completed[-1][2] if completed else {},
            "solver_controls": controls,
            "log_mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            "heat": heat, "street_probe_stability": probes}


def inspect_pair(base, policy, processes=False):
    scenario = json.loads((base / "inputs/scenario.json").read_text())
    count = len(json.loads((base / "inputs/probes.json").read_text()))
    if count < 3:
        raise ValueError("At least three identical street probes are required")
    record = {"checked_utc": datetime.now(timezone.utc).isoformat(), "case_directory": str(base),
              "policy": policy, "cases": {}, "acceptance_scope": "Numerical screening before extent comparisons; mesh, inlet and empirical validation remain separate."}
    for name in ("baseline", "retrofit"):
        row = inspect_case(base, name, policy, scenario, count)
        if processes:
            container = f"kajicho-area-{base.name}-{name}"
            p = subprocess.run(["docker", "inspect", container], capture_output=True, text=True)
            if p.returncode == 0:
                d = json.loads(p.stdout)[0]
                top = subprocess.run(["docker", "top", container, "-eo", "pid,ppid,comm,args"], capture_output=True, text=True)
                solver_lines = [x for x in top.stdout.splitlines()[1:] if re.search(r"\bbuoyantBoussinesqSimpleFoam -parallel$", x)]
                row["process"] = {"container": container, "state": d["State"]["Status"], "container_pid": d["State"]["Pid"],
                                  "cpuset": d["HostConfig"].get("CpusetCpus"), "solver_pids": [int(x.split()[0]) for x in solver_lines if "mpirun" not in x]}
            else:
                row["process"] = {"container": container, "state": "absent", "inspect_message": p.stderr.strip()[-250:]}
        record["cases"][name] = row
    record["accepted_for_domain_comparisons"] = all(x["accepted"] for x in record["cases"].values())
    record["eligible_to_publish_final_comparison"] = False
    record["next_action"] = ("inspect hosts and run the prepared extent comparisons" if record["accepted_for_domain_comparisons"]
                             else "continue healthy reference solve; diagnose completed or failed cases before further experiments")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_directory", type=Path)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--processes", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    record = inspect_pair(args.case_directory, json.loads(args.policy.read_text()), args.processes)
    data = json.dumps(record, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)
    print(data, end="")


if __name__ == "__main__":
    main()
