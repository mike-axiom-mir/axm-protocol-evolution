import copy
import json
import unittest
from pathlib import Path

from protocol_evolution.candidate_promotion import analyze_candidate_promotion_assessments

ROOT = Path(__file__).resolve().parents[1]
ASSESSMENTS = ROOT / "fixtures" / "candidate_promotion_assessments.json"
CANDIDATES = ROOT / "fixtures" / "monolith_candidate_observations.json"


class CandidatePromotionReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ASSESSMENTS.read_text(encoding="utf-8"))
        cls.candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))

    def analyze(self, payload=None):
        return analyze_candidate_promotion_assessments(payload or self.payload, self.candidates)

    def test_real_assessment_is_valid_and_held(self):
        result = self.analyze()
        self.assertTrue(result["valid"], result["errors"])
        assessment = result["assessments"][0]
        self.assertTrue(assessment["donor_regression_executed_this_cycle"])
        self.assertTrue(assessment["synthetic_regression_fixture_observed"])
        self.assertFalse(assessment["historical_source_fixture_observed"])
        self.assertFalse(assessment["exact_adjacent_target_output_observed"])
        self.assertFalse(assessment["generation_admission_ready"])
        self.assertFalse(assessment["migration_path_admission_ready"])

    def test_falsifier_rejects_synthetic_fixture_promoted_as_historical(self):
        payload = copy.deepcopy(self.payload)
        payload["assessments"][0]["source_fixture"]["historical_value_observed"] = True
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("synthetic-fixture-cannot-be-historical:") for e in result["errors"]))

    def test_falsifier_rejects_exact_target_claim_when_migrator_emits_current(self):
        payload = copy.deepcopy(self.payload)
        payload["assessments"][0]["execution_observation"]["exact_adjacent_target_observed"] = True
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("exact-target-claim-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_path_readiness_without_exact_adjacent_evidence(self):
        payload = copy.deepcopy(self.payload)
        payload["assessments"][0]["migration_path_admission_ready"] = True
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("path-readiness-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_donor_byte_identity_mismatch(self):
        payload = copy.deepcopy(self.payload)
        payload["assessments"][0]["evidence"][1]["archive_git_blob_sha"] = "0" * 40
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("archive-github-byte-identity-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_promotion_claim(self):
        payload = copy.deepcopy(self.payload)
        payload["assessments"][0]["promotion_claims"]["migration_path_admitted"] = True
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.endswith(":migration_path_admitted") for e in result["errors"]))

    def test_falsifier_rejects_unknown_candidate_edge(self):
        payload = copy.deepcopy(self.payload)
        payload["assessments"][0]["candidate_ref"]["target_version"] = "0.5.0"
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("unknown-candidate-edge:") for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()
