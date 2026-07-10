import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_contract():
    path = ROOT / "scripts" / "artifact_contract.py"
    spec = importlib.util.spec_from_file_location("artifact_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load contract: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ArtifactContractTests(unittest.TestCase):
    def test_contract_defines_one_canonical_loop_schema(self):
        contract = load_contract()
        self.assertEqual(contract.CONTRACT_VERSION, "1.0")
        self.assertEqual(
            contract.REQUIRED_LOOP_SECTIONS,
            [
                "## Goal",
                "## Classification",
                "## Done When",
                "## Non-Goals",
                "## Never Touch",
                "## Stop If",
                "## Plan",
                "## Active Slice",
                "## Evidence Log",
                "## Decisions",
            ],
        )
        self.assertEqual(
            contract.EVIDENCE_HEADER,
            "| Time | Command / Check | Result | Notes |",
        )

    def test_loop_template_implements_canonical_contract(self):
        contract = load_contract()
        template = (ROOT / "templates" / "LOOP.md").read_text()
        for section in contract.REQUIRED_LOOP_SECTIONS:
            self.assertIn(section, template)
        self.assertIn(contract.EVIDENCE_HEADER, template)
        self.assertIn("contract_version: 1.0", template)

    def test_skill_minimum_contract_matches_template(self):
        contract = load_contract()
        skill = (ROOT / "SKILL.md").read_text()
        contract_block = skill.split("Create or update `.hermes-loop/LOOP.md`", 1)[1].split("```", 2)[1]
        for section in contract.REQUIRED_LOOP_SECTIONS:
            self.assertIn(section, contract_block)
        self.assertIn(contract.EVIDENCE_HEADER, contract_block)
        self.assertIn("contract_version: 1.0", contract_block)

    def test_harness_imports_canonical_contract(self):
        source = (ROOT / "scripts" / "harness_check.py").read_text()
        self.assertIn("from artifact_contract import", source)
        self.assertNotIn("REQUIRED_LOOP_SECTIONS = [", source)


if __name__ == "__main__":
    unittest.main()
