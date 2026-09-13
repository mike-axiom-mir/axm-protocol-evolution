import copy
import json
import unittest
from pathlib import Path

from protocol_evolution.artifact_path_history import analyze_artifact_path_history

ROOT = Path(__file__).resolve().parents[1]
OBSERVATIONS = ROOT / "fixtures" / "artifact_path_history_observations.json"
ROUTES = ROOT / "fixtures" / "historical_fixture_routes.json"
EVIDENCE = ROOT / "evidence" / "artifact_path_history.json"


class ArtifactPathHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
        cls.routes = json.loads(ROUTES.read_text(encoding="utf-8"))

    def analyze(self, payload=None, routes=None):
        return analyze_artifact_path_history(payload or self.payload, routes or self.routes)

    def test_real_observations_keep_candidate_gap_unpromoted(self):
        result = self.analyze()
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["record_count"], 2)
        self.assertEqual(result["historical_support_count"], 1)
        control, candidate = result["records"]
        self.assertTrue(control["historical_observation_supported_by_path_history"])
        self.assertFalse(candidate["historical_observation_supported_by_path_history"])
        self.assertIn("cumulative-history", candidate["classification"])

    def test_falsifier_rejects_oldest_commit_not_last_in_observed_order(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["path_history_observation"]["observed_commits_newest_to_oldest"].append("1" * 40)
        payload["records"][0]["path_history_observation"]["bounded_result_count"] = 2
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("oldest-observed-order-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_short_observed_commit(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][1]["path_history_observation"]["observed_commits_newest_to_oldest"][0] = "4a2499722141"
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("invalid-observed-commit:") for e in result["errors"]))

    def test_falsifier_rejects_exact_control_blob_mismatch(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["path_history_observation"]["artifact_blob_sha_at_oldest_observed_commit"] = "0" * 40
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("oldest-observed-blob-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_candidate_promoted_by_labelled_schema_history(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][1]["historical_observation_supported_by_path_history"] = True
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("historical-support-claim-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_unbound_route(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["route_id"] = "missing-route"
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("unknown-route:") for e in result["errors"]))

    def test_checked_in_evidence_matches_generated_truth(self):
        expected = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(self.analyze(), expected)


if __name__ == "__main__":
    unittest.main()
