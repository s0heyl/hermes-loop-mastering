import json
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "harness_check.py"


class HarnessCliTests(unittest.TestCase):
    def run_harness(self, *args):
        return subprocess.run(
            ["python", str(HARNESS), *map(str, args)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_json_output_is_machine_readable(self):
        result = self.run_harness("--json", "--mode", "standard", ROOT / "examples" / "good-loop")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["passed"])
        self.assertEqual(data["mode"], "standard")
        self.assertEqual(data["contract_version"], "1.0")
        self.assertEqual(data["score"], data["max_score"])

    def test_critical_fixture_passes_strict_behavioral_gates(self):
        result = self.run_harness("--json", "--strict", "--mode", "critical", ROOT / "examples" / "critical-loop")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["passed"])
        self.assertEqual(data["behavioral_gates_passed"], 7)
        self.assertEqual(data["behavioral_gates_required"], 7)

    def test_standard_fixture_fails_when_forced_into_critical_mode(self):
        result = self.run_harness("--json", "--strict", "--mode", "critical", ROOT / "examples" / "good-loop")
        self.assertEqual(result.returncode, 1)
        data = json.loads(result.stdout)
        self.assertFalse(data["passed"])
        self.assertTrue(any("critical evidence missing" in issue for issue in data["issues"]))

    def test_strict_mode_fails_on_any_contract_issue(self):
        result = self.run_harness("--json", "--strict", "--mode", "standard", ROOT / "examples" / "bad-loop")
        self.assertEqual(result.returncode, 1)
        data = json.loads(result.stdout)
        self.assertFalse(data["passed"])
        self.assertGreater(len(data["issues"]), 0)


if __name__ == "__main__":
    unittest.main()
