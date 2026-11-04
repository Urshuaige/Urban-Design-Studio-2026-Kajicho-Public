#!/usr/bin/env python3
"""Export each numerically accepted case at its own final iteration.

This concept-demo export retains pending grid/domain/empirical validation.
It never falls back to a common intermediate iteration or overwrites an export.
Run native reconstruction and pedestrian sampling at the accepted times first.
"""
import argparse
import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

from check_cfd_pair_v4 import inspect_pair

NAMES = ("baseline", "retrofit")


def checked_times(record):
    if not record.get("accepted_for_domain_comparisons"):
        raise ValueError("Both cases must pass the unchanged numerical policy")
    result = {}
    for name in NAMES:
        row = record["cases"][name]
        time = row.get("last_completed_iteration")
        if not row.get("accepted") or time is None or not math.isfinite(time) or time <= 0:
            raise ValueError("Missing accepted final state: " + name)
        if row.get("last_started_iteration", time) != time:
            raise ValueError("An unfinished later iteration exists: " + name)
        result[name] = time
    return result


def surface_directory(case, iteration):
    root = case / "postProcessing/pedestrian"
    matches = [p for p in root.glob("*") if p.is_dir()
               and re.fullmatch(r"\d+(?:\.\d+)?", p.name)
               and float(p.name) == iteration]
    if len(matches) != 1:
        raise ValueError(f"Native pedestrian surface missing at accepted time {iteration}: {case}")
    return matches[0]


def export(base, output, policy_path, host):
    policy = json.loads(policy_path.read_text())
    trial = json.loads((base / "outputs/Trial_Status.json").read_text())
    if trial.get("state") != "awaiting_checkpoint_review":
        raise ValueError("The checkpoint must finish before export")
    record = inspect_pair(base, policy)
    iterations = checked_times(record)
    if output.exists():
        raise FileExistsError("Choose a new export directory")

    # Dependencies and output creation follow the acceptance gate.
    import numpy as np
    from scipy.spatial import cKDTree
    from shapely import contains_xy
    from shapely.geometry import shape
    from shapely.ops import unary_union

    city = json.loads((base / "inputs/city.json").read_text())
    scenario = json.loads((base / "inputs/scenario.json").read_text())
    meta = city["meta"]
    reference_temperature = scenario["air_temperature_c"] + 273.15
    xx, yy = np.meshgrid(meta["x0"] + (np.arange(meta["nx"]) + .5)*meta["dx"],
                         meta["y0"] + (np.arange(meta["ny"]) + .5)*meta["dx"])
    xy = np.column_stack((xx.ravel(), yy.ravel()))
    core = shape(city["boundary"])
    features = json.loads((base / "inputs/cfd_buildings_local.geojson").read_text())["features"]
    obstacles = unary_union([shape(f["geometry"]) for f in features if f["properties"]["height_m"] > 1.5])
    open_ground = ~contains_xy(obstacles, xy[:, 0], xy[:, 1])
    core_points = contains_xy(core, xy[:, 0], xy[:, 1])
    packs, sampling, balances = [], [], []
    for name in NAMES:
        directory = surface_directory(base / "cases" / name, iterations[name])
        paths = list(directory.rglob("*.raw"))
        def field_file(field):
            matches = [p for p in paths if field in re.split(r"[_.]", p.stem)]
            if len(matches) != 1:
                raise ValueError(f"Expected one native {field} surface in {directory}")
            return matches[0]
        tfile, ufile = field_file("T"), field_file("U")
        a = np.loadtxt(tfile, comments="#", ndmin=2)
        u = np.loadtxt(ufile, comments="#", ndmin=2)
        if a.shape[1] != 4 or u.shape[1] != 6:
            raise ValueError("Unexpected native raw surface columns")
        if not (np.allclose(a[:, 2], 1.5, atol=1e-6, rtol=0)
                and np.allclose(u[:, 2], 1.5, atol=1e-6, rtol=0)):
            raise ValueError("Only the declared1.5m pedestrian plane can be exported")
        def crop(data):
            mask = ((data[:, 0] >= meta["x0"]-5) & (data[:, 0] <= meta["x0"]+meta["nx"]*meta["dx"]+5)
                    & (data[:, 1] >= meta["y0"]-5) & (data[:, 1] <= meta["y0"]+meta["ny"]*meta["dx"]+5))
            return data[mask]
        a, u = crop(a), crop(u)
        if not len(a) or not len(u):
            raise ValueError("No native samples in the display crop")
        dist, idx = cKDTree(a[:, :2]).query(xy)
        udist, uidx = cKDTree(u[:, :2]).query(xy)
        limit = np.where(core_points, .75, 2.0)
        valid = open_ground & (dist <= limit) & (udist <= limit)
        delta_t, velocity = a[idx, 3]-reference_temperature, u[uidx, 3:6]
        if not (np.all(np.isfinite(delta_t[valid])) and np.all(np.isfinite(velocity[valid]))):
            raise ValueError("Nonfinite native value in valid sample")
        if not np.any(valid & core_points):
            raise ValueError("No valid core sample")
        pack = np.column_stack((velocity, delta_t, valid)).astype("<f4")
        pack[~valid, :4] = 0
        packs.append(pack)
        sampling.append({"case": name, "accepted_iteration": iterations[name],
                         "native_temperature_file": str(tfile.relative_to(base)),
                         "native_velocity_file": str(ufile.relative_to(base)),
                         "native_rows_in_crop": len(a), "core_distance_limit_m": .75,
                         "maximum_sample_distance_m": float(np.maximum(dist[valid], udist[valid]).max()),
                         "core_maximum_sample_distance_m": float(np.maximum(dist[valid & core_points], udist[valid & core_points]).max()),
                         "valid_grid_points": int(valid.sum()), "method": "nearest native surface point; same spatial grid"})
        heat = record["cases"][name]["heat"]
        row = heat["latest_row"]
        balances.append({"case": name, "diagnostic_iteration": row[0], "roof_input_W": row[1],
                         "other_outward_heat_W": row[2], "net_outward_heat_W": row[3],
                         "net_volume_flux_m3_s": row[4], "heated_roof_area_m2": row[5],
                         "relative_heat_imbalance": heat["latest_relative_imbalance"],
                         "maximum_tail_relative_imbalance": heat["maximum_tail_relative_imbalance"]})
    paired = (packs[0][:, 4] > 0) & (packs[1][:, 4] > 0)
    mask = paired & core_points
    if mask.sum() <= 100:
        raise ValueError("Insufficient common open core samples")
    statistics = {}
    for label, values in [("heat", [p[:, 3].astype(float) for p in packs]),
                          ("wind", [np.linalg.norm(p[:, :3].astype(float), axis=1) for p in packs])]:
        diff = values[1][mask]-values[0][mask]
        statistics[label] = {"baseline": float(values[0][mask].mean()), "retrofit": float(values[1][mask].mean()),
                             "mean_difference": float(diff.mean()), "difference_p05": float(np.quantile(diff, .05)),
                             "difference_p95": float(np.quantile(diff, .95))}
    quality = json.loads((base / "inputs/mesh_quality.json").read_text())
    result = {"schema_version": 2, "status": "numerically_checked_concept", "host": host,
              "snapshot_utc": datetime.now(timezone.utc).isoformat(), "iteration": None, "case_iterations": iterations,
              "mesh_selection": json.loads((base / "inputs/mesh_selection.json").read_text()),
              "fields": {"files": ["data/cfd-baseline.bin", "data/cfd-retrofit.bin"],
                         "components": ["Ux_m_s", "Uy_m_s", "Uz_m_s", "roof_temperature_contribution_K", "valid"],
                         "format": "little-endian Float32, row-major south to north", "temperature_component": "excess_K",
                         "sample_height_m": 1.5, "grid_spacing_m": meta["dx"], "core_common_open_points": int(mask.sum()),
                         "statistics": statistics},
              "checks": {"mesh": "partial", "convergence": "passed", "heat_balance": "passed", "street_stability": "passed",
                         "mesh_sensitivity": "pending", "domain_sensitivity": "pending", "inlet_preservation": "pending",
                         "empirical_validation": "pending"},
              "numerical": {"mesh": quality, "heat_balance": balances, "sampling": sampling, "acceptance": record,
                            "temperature_precision": "Subtract inlet temperature in Float64 before compact Float32 export",
                            "interpretation": "Numerically checked fixed-scenario concept; first-order diffusion and grid/domain/inlet/empirical limits retained"},
              "scenario": scenario, "domain": json.loads((base / "inputs/domain.json").read_text())}
    # Write only after every case, sample and statistic has passed its gate.
    output.mkdir(parents=True)
    for name, pack in zip(NAMES, packs):
        pack.tofile(output / f"cfd-{name}.bin")
    (output / "CFD_Field_Results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    with (output / "CFD_Pedestrian_Samples.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["x_epsg6677", "y_epsg6677", "baseline_U_m_s", "retrofit_U_m_s", "baseline_roof_deltaT_K",
                         "retrofit_roof_deltaT_K", "delta_roof_deltaT_K", "core"])
        for k in np.flatnonzero(paired):
            writer.writerow([xy[k, 0]+meta["origin_epsg6677"][0], xy[k, 1]+meta["origin_epsg6677"][1],
                             np.linalg.norm(packs[0][k, :3]), np.linalg.norm(packs[1][k, :3]), packs[0][k, 3],
                             packs[1][k, 3], packs[1][k, 3]-packs[0][k, 3], int(core_points[k])])
    return {"case_iterations": iterations, "core_common_points": int(mask.sum()), "statistics": statistics,
            "output": str(output), "scope": "Numerical concept demonstration; detailed validation pending"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_directory", type=Path)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host", required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.case_directory, args.output, args.policy, args.host), indent=2))
