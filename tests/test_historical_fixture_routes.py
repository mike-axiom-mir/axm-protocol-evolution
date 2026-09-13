import copy
import json
import unittest
from pathlib import Path

from protocol_evolution.historical_fixture_routes import analyze_historical_fixture_routes

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "historical_fixture_routes.json"
EVIDENCE = ROOT / "evidence" / "historical_fixture_routes.json"


class HistoricalFixtureRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def analyze(self, payload=None):
        return analyze_historical_fixture_routes(payload or self.payload, ROOT)

    def test_real_control_proves_archive_is_not_mandatory_for_fixture_provenance(self):
        result = self.analyze()
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["independent_ready_count"], 1)
        control, gap = result["records"]
        self.assertFalse(control["history_archive_available_for_inspection"])
        self.assertTrue(control["independent_exact_historical_artifact_valid"])
        self.assertTrue(control["independent_fixture_provenance_ready"])
        self.assertFalse(gap["independent_fixture_provenance_ready"])

    def test_falsifier_rejects_byte_mismatch(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["donor_blob_sha"] = "0" * 40
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("fixture-donor-byte-identity-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_short_commit(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["commit"] = payload["records"][0]["commit"][:12]
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("invalid-commit:") for e in result["errors"]))

    def test_falsifier_rejects_missing_historical_observation(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["historical_value_observed"] = False
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("historical-observation-required:") for e in result["errors"]))

    def test_falsifier_rejects_candidate_gap_promoted_ready(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][1]["independent_fixture_provenance_ready"] = True
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("candidate-gap-cannot-be-ready:") for e in result["errors"]))

    def test_checked_in_evidence_matches_generated_truth(self):
        expected = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(self.analyze(), expected)

    def test_falsifier_rejects_path_escape(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["fixture_path"] = "../outside.json"
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("fixture-path-escapes-root:") for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()
