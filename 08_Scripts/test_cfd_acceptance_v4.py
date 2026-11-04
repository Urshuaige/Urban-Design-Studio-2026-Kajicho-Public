#!/usr/bin/env python3
"""Regressions for the validity decisions that control the next expensive run."""
import json
import tempfile
import unittest
from pathlib import Path
from check_cfd_pair_v4 import inspect_pair

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "03_Theme_B/Simulation_V3/CFD_Acceptance_v4.json").read_text())


def make_pair(root, converged=True, balanced_tail=True):
    (root / "inputs").mkdir()
    (root / "logs").mkdir()
    scenario = {"baseline_albedo": .2, "retrofit_albedo": .6, "GHI_W_m2": 1000, "sensible_conversion_fraction": .2}
    (root / "inputs/scenario.json").write_text(json.dumps(scenario))
    (root / "inputs/probes.json").write_text(json.dumps([[i, 0, 1.5] for i in range(12)]))
    for name, roof_power in (("baseline", 160000), ("retrofit", 80000)):
        system = root / "cases" / name / "system"
        system.mkdir(parents=True)
        (system / "fvSolution").write_text('SIMPLE {residualControl {p_rgh 1e-4;U 1e-4;T 1e-8;"(k|epsilon)" 1e-4;}}')
        log = "Time = 400\nSolving for T, Initial residual = 1e-9, Final residual = 1e-12\nExecutionTime = 1 s\n"
        if converged:
            log += "SIMPLE solution converged in 400 iterations\n"
        (root / "logs" / f"solver_{name}.log").write_text(log + "End\nFinalising parallel run\n")
        pp = root / "cases" / name / "postProcessing"
        probes = pp / "monitoringPoints/50"
        probes.mkdir(parents=True)
        (probes / "T").write_text("\n".join(str(i) + " " + " ".join(["311.6"] * 12) for i in range(200, 401, 10)))
        (probes / "U").write_text("\n".join(str(i) + " " + " ".join(["(0 1 0)"] * 12) for i in range(200, 401, 10)))
        rows = []
        for iteration in range(200, 401, 20):
            fraction = .005 if balanced_tail or iteration == 400 else .3
            net = -roof_power * fraction
            rows.append(f"{iteration},{roof_power},{roof_power+net},{net},0,1000")
        (pp / "roofHeatBalance.csv").write_text("\n".join(rows))


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_end_alone_is_not_convergence(self):
        make_pair(self.root, converged=False)
        r = inspect_pair(self.root, POLICY)
        self.assertTrue(r["cases"]["baseline"]["normal_end"])
        self.assertFalse(r["accepted_for_domain_comparisons"])

    def test_one_balanced_last_row_is_not_a_balanced_history(self):
        make_pair(self.root, balanced_tail=False)
        r = inspect_pair(self.root, POLICY)
        self.assertEqual(r["cases"]["baseline"]["heat"]["latest_relative_imbalance"], .005)
        self.assertFalse(r["accepted_for_domain_comparisons"])

    def test_complete_pair_passes_only_numerical_screening(self):
        make_pair(self.root)
        r = inspect_pair(self.root, POLICY)
        self.assertTrue(r["accepted_for_domain_comparisons"])
        self.assertFalse(r["eligible_to_publish_final_comparison"])

    def test_unfinished_iteration_is_excluded_and_missing_probe_fails(self):
        make_pair(self.root)
        with (self.root / "logs/solver_baseline.log").open("a") as stream:
            stream.write("Time = 401\nSolving for T, Initial residual = 1e-10, Final residual = 1e-12\n")
        p = self.root / "cases/baseline/postProcessing/monitoringPoints/50/U"
        p.write_text(p.read_text().replace("(0 1 0) (0 1 0)", "(0 1 0)", 1))
        r = inspect_pair(self.root, POLICY)
        self.assertEqual(r["cases"]["baseline"]["last_completed_iteration"], 400)
        self.assertEqual(r["cases"]["baseline"]["last_started_iteration"], 401)
        self.assertFalse(r["accepted_for_domain_comparisons"])

    def test_oscillating_probe_blocks_pass_even_when_mean_is_stable(self):
        make_pair(self.root)
        p = self.root / "cases/baseline/postProcessing/monitoringPoints/50/U"
        lines = p.read_text().splitlines()
        for i in range(len(lines)):
            lines[i] = lines[i].replace("(0 1 0)", "(0 1.1 0)" if i % 2 else "(0 0.9 0)")
        p.write_text("\n".join(lines))
        r = inspect_pair(self.root, POLICY)
        self.assertFalse(r["cases"]["baseline"]["street_probe_stability"]["passed"])

    def test_zero_heat_input_blocks_pass_with_json_safe_record(self):
        make_pair(self.root)
        p = self.root / "cases/baseline/postProcessing/roofHeatBalance.csv"
        p.write_text(p.read_text().replace("160000,159200.0,-800.0", "0,0,0"))
        r = inspect_pair(self.root, POLICY)
        self.assertFalse(r["accepted_for_domain_comparisons"])
        json.dumps(r, allow_nan=False)

    def test_loosened_solver_target_cannot_use_old_acceptance_label(self):
        make_pair(self.root)
        p = self.root / "cases/baseline/system/fvSolution"
        p.write_text(p.read_text().replace("T 1e-8", "T 1e-4"))
        r = inspect_pair(self.root, POLICY)
        self.assertFalse(r["cases"]["baseline"]["solver_controls"]["passed"])
        self.assertFalse(r["accepted_for_domain_comparisons"])


if __name__ == "__main__":
    unittest.main()
