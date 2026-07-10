import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "compare_benchmarks.py"


class BenchmarkComparisonTests(unittest.TestCase):
    def run_compare(self, baseline, candidate, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            base_path = pathlib.Path(tmp) / "baseline.json"
            candidate_path = pathlib.Path(tmp) / "candidate.json"
            base_path.write_text(json.dumps(baseline))
            candidate_path.write_text(json.dumps(candidate))
            return subprocess.run(
                ["python", str(SCRIPT), str(base_path), str(candidate_path), *extra],
                text=True,
                capture_output=True,
                check=False,
            )

    def test_json_report_calculates_quality_and_efficiency_deltas(self):
        baseline = {"name": "v1.3.0", "hidden_passed": 11, "hidden_total": 16, "visible_passed": 14, "visible_total": 14, "elapsed_seconds": 195.745, "tool_calls": 37}
        candidate = {"name": "v1.4.0", "hidden_passed": 16, "hidden_total": 16, "visible_passed": 18, "visible_total": 18, "elapsed_seconds": 180.0, "tool_calls": 30}
        result = self.run_compare(baseline, candidate, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["quality_gate_passed"])
        self.assertAlmostEqual(data["hidden_accuracy_delta_points"], 31.25)
        self.assertLess(data["elapsed_delta_percent"], 0)
        self.assertLess(data["tool_call_delta_percent"], 0)

    def test_correctness_regression_fails_quality_gate(self):
        baseline = {"name": "base", "hidden_passed": 8, "hidden_total": 10, "visible_passed": 5, "visible_total": 5, "elapsed_seconds": 10, "tool_calls": 10}
        candidate = {"name": "candidate", "hidden_passed": 7, "hidden_total": 10, "visible_passed": 5, "visible_total": 5, "elapsed_seconds": 5, "tool_calls": 5}
        result = self.run_compare(baseline, candidate, "--json")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["quality_gate_passed"])

    def test_invalid_snapshot_is_rejected(self):
        result = self.run_compare({"name": "bad"}, {"name": "bad"}, "--json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing required keys", result.stderr)


if __name__ == "__main__":
    unittest.main()
