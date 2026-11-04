#!/usr/bin/env python3
"""Selection regressions for accepted per-case export; no simulated results."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from export_cfd_checked_pair_v5 import checked_times, export, surface_directory


def accepted_record():
    return {"accepted_for_domain_comparisons": True, "cases": {
        "baseline": {"accepted": True, "last_completed_iteration": 640, "last_started_iteration": 640},
        "retrofit": {"accepted": True, "last_completed_iteration": 780, "last_started_iteration": 780}}}


class CheckedExportTests(unittest.TestCase):
    def test_distinct_accepted_iterations_are_preserved(self):
        self.assertEqual(checked_times(accepted_record()), {"baseline": 640, "retrofit": 780})

    def test_one_unaccepted_case_blocks_pair(self):
        record = accepted_record()
        record["cases"]["retrofit"]["accepted"] = False
        with self.assertRaises(ValueError):
            checked_times(record)

    def test_unfinished_later_iteration_blocks_stale_acceptance(self):
        record = accepted_record()
        record["cases"]["baseline"]["last_started_iteration"] = 641
        with self.assertRaises(ValueError):
            checked_times(record)

    def test_missing_final_surface_does_not_fall_back_to_intermediate(self):
        with tempfile.TemporaryDirectory() as temp:
            case = Path(temp)
            (case / "postProcessing/pedestrian/500").mkdir(parents=True)
            with self.assertRaises(ValueError):
                surface_directory(case, 640)
            final = case / "postProcessing/pedestrian/640"
            final.mkdir()
            self.assertEqual(surface_directory(case, 640), final)

    @unittest.skipUnless(importlib.util.find_spec("scipy") is not None, "Run the full export fixture in the existing CFD Python environment")
    def test_full_export_preserves_times_and_temperature_units(self):
        from test_cfd_acceptance_v4 import make_pair, ROOT
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp) / "case"
            base.mkdir()
            make_pair(base)
            # Distinct final iterations with complete, unchanged numerical checks.
            log = base / "logs/solver_retrofit.log"
            log.write_text(log.read_text().replace("400", "420"))
            for field in ["U", "T"]:
                p = base / "cases/retrofit/postProcessing/monitoringPoints/50" / field
                p.write_text("\n".join(str(int(line.split()[0])+20)+" "+line.partition(" ")[2]
                                       for line in p.read_text().splitlines()))
            p = base / "cases/retrofit/postProcessing/roofHeatBalance.csv"
            p.write_text("\n".join(str(int(line.split(",")[0])+20)+","+line.partition(",")[2]
                                   for line in p.read_text().splitlines()))
            scenario_path = base / "inputs/scenario.json"
            scenario = json.loads(scenario_path.read_text())
            scenario["air_temperature_c"] = 38.4
            scenario_path.write_text(json.dumps(scenario))
            city = {"meta": {"nx": 12, "ny": 12, "x0": 0, "y0": 0, "dx": 1, "origin_epsg6677": [0, 0]},
                    "boundary": {"type": "Polygon", "coordinates": [[[0, 0], [12, 0], [12, 12], [0, 12], [0, 0]]]}}
            for name, value in {"city.json": city, "cfd_buildings_local.geojson": {"features": []},
                                "mesh_quality.json": {"accepted_for_exploratory_pair": True, "fixture": True},
                                "mesh_selection.json": {"case": "fixture"}, "domain.json": {"fixture": True}}.items():
                (base / "inputs" / name).write_text(json.dumps(value))
            (base / "outputs").mkdir()
            (base / "outputs/Trial_Status.json").write_text(json.dumps({"state": "awaiting_checkpoint_review"}))
            for name, iteration, delta in [("baseline", 400, .2), ("retrofit", 420, .1)]:
                directory = base / "cases" / name / "postProcessing/pedestrian" / str(iteration)
                directory.mkdir(parents=True)
                xy = [(x+.5, y+.5) for y in range(12) for x in range(12)]
                (directory / "pedestrian_T.raw").write_text("\n".join(f"{x} {y} 1.5 {311.55+delta:.12f}" for x, y in xy))
                (directory / "pedestrian_U.raw").write_text("\n".join(f"{x} {y} 1.5 0 1 0" for x, y in xy))
            output = Path(temp) / "export"
            result = export(base, output, ROOT / "03_Theme_B/Simulation_V3/CFD_Acceptance_v4.json", "fixture")
            self.assertEqual(result["case_iterations"], {"baseline": 400, "retrofit": 420})
            self.assertAlmostEqual(result["statistics"]["heat"]["baseline"], .2, places=6)
            self.assertAlmostEqual(result["statistics"]["heat"]["mean_difference"], -.1, places=6)
            self.assertEqual((output / "cfd-baseline.bin").stat().st_size, 144*5*4)
            metadata = json.loads((output / "CFD_Field_Results.json").read_text())
            self.assertIsNone(metadata["iteration"])
            self.assertEqual(metadata["checks"]["empirical_validation"], "pending")


if __name__ == "__main__":
    unittest.main()
