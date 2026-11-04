#!/usr/bin/env python3
"""Check that portable history collection preserves native validity and time bounds."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from test_cfd_acceptance_v4 import make_pair, ROOT


class HistoryTests(unittest.TestCase):
    def test_cli_works_without_personal_state_and_preserves_failed_convergence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            case = root / "case"
            case.mkdir()
            make_pair(case, converged=False)
            config = root / "history.json"
            config.write_text(json.dumps({"host": None,
                "policy_path": str(ROOT / "03_Theme_B/Simulation_V3/CFD_Acceptance_v4.json"),
                "runs": [{"key": "fixture", "directory": str(case), "cells": 100,
                          "label": {"zh": "测试", "en": "Test", "ja": "テスト"}}]}))
            output = root / "output.json"
            subprocess.run([sys.executable, str(ROOT / "08_Scripts/collect_cfd_numerical_history_v5.py"),
                            "--config", str(config), "--output", str(output)],
                           cwd=root, check=True, capture_output=True, text=True)
            run = json.loads(output.read_text())["runs"][0]
            self.assertFalse(run["checks"]["accepted_for_domain_comparisons"])
            self.assertTrue(run["checks"]["cases"]["baseline"]["heat"]["passed"])
            self.assertEqual(run["heat"]["baseline"][-1], [400, .5])

    def test_history_excludes_heat_rows_after_last_completed_solver_iteration(self):
        from collect_cfd_numerical_history_v5 import collect_runs
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_pair(root)
            heat = root / "cases/baseline/postProcessing/roofHeatBalance.csv"
            with heat.open("a") as stream:
                stream.write("\n500,160000,100000,-60000,0,1000\n")
            runs = collect_runs({"policy_path": str(ROOT / "03_Theme_B/Simulation_V3/CFD_Acceptance_v4.json"),
                "runs": [{"key": "fixture", "directory": str(root), "cells": 100,
                          "label": {"zh": "测试", "en": "Test", "ja": "テスト"}}]})
            self.assertEqual(runs[0]["heat"]["baseline"][-1], [400, .5])
            self.assertTrue(runs[0]["checks"]["accepted_for_domain_comparisons"])


if __name__ == "__main__":
    unittest.main()
