import copy
import json
import unittest
from pathlib import Path

from protocol_evolution.monolith_candidates import analyze_monolith_candidate_observations

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "monolith_candidate_observations.json"


class MonolithCandidateCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_real_observation_is_valid_but_not_promoted(self):
        result = analyze_monolith_candidate_observations(self.payload)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["five_plus_generation_candidate_count"], 1)
        candidate = result["candidates"][0]
        self.assertEqual(candidate["version_count"], 5)
        self.assertEqual(candidate["adjacent_transition_contract_count"], 4)
        self.assertTrue(candidate["five_plus_generation_candidate"])
        self.assertFalse(candidate["generation_admission_claimed"])
        self.assertFalse(candidate["migration_path_admission_claimed"])
        self.assertFalse(candidate["chain_experiment_input_ready"])

    def test_falsifier_rejects_candidate_promotion(self):
        payload = copy.deepcopy(self.payload)
        payload["observations"][0]["candidate_lineage"]["promotion_claims"]["migration_path_admitted"] = True
        result = analyze_monolith_candidate_observations(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(error.endswith(":migration_path_admitted") for error in result["errors"]))

    def test_falsifier_rejects_missing_adjacent_contract(self):
        payload = copy.deepcopy(self.payload)
        payload["observations"][0]["candidate_lineage"]["adjacent_transition_contracts"].pop()
        result = analyze_monolith_candidate_observations(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(error.startswith("transition-count-mismatch:") for error in result["errors"]))

    def test_falsifier_rejects_wrong_transition_order(self):
        payload = copy.deepcopy(self.payload)
        transition = payload["observations"][0]["candidate_lineage"]["adjacent_transition_contracts"][0]
        transition["target_version"] = "0.3.0"
        result = analyze_monolith_candidate_observations(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(error.startswith("transition-order-mismatch:") for error in result["errors"]))

    def test_falsifier_rejects_duplicate_version(self):
        payload = copy.deepcopy(self.payload)
        payload["observations"][0]["candidate_lineage"]["versions"][1]["version"] = "0.1.0"
        payload["observations"][0]["candidate_lineage"]["versions"][1]["schema_id"] = "axm.living-city-sim.world/v0.1.0"
        result = analyze_monolith_candidate_observations(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(error.startswith("duplicate-version:") for error in result["errors"]))

    def test_falsifier_rejects_archive_github_byte_identity_mismatch(self):
        payload = copy.deepcopy(self.payload)
        payload["observations"][0]["candidate_lineage"]["versions"][0]["archive_git_blob_sha"] = "0" * 40
        result = analyze_monolith_candidate_observations(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(error.startswith("archive-github-byte-identity-mismatch:") for error in result["errors"]))

    def test_falsifier_rejects_weak_archive_identity(self):
        payload = copy.deepcopy(self.payload)
        payload["observations"][0]["archive"]["sha256"] = "sha256:not-a-real-digest"
        result = analyze_monolith_candidate_observations(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(error.startswith("invalid-archive-sha256:") for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
