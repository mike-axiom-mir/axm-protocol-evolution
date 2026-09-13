import copy
import json
import unittest
from pathlib import Path

from protocol_evolution.candidate_promotion import analyze_candidate_promotion_assessments
from protocol_evolution.historical_fixture_routes import analyze_historical_fixture_routes

ROOT = Path(__file__).resolve().parents[1]
ASSESSMENTS = ROOT / "fixtures" / "candidate_promotion_assessments.json"
CANDIDATES = ROOT / "fixtures" / "monolith_candidate_observations.json"
ROUTES = ROOT / "fixtures" / "historical_fixture_routes.json"
EVIDENCE = ROOT / "evidence" / "candidate_promotion_readiness.json"


class CandidatePromotionReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ASSESSMENTS.read_text(encoding="utf-8"))
        cls.candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
        cls.routes = json.loads(ROUTES.read_text(encoding="utf-8"))
        cls.route_result = analyze_historical_fixture_routes(cls.routes, ROOT)

    def analyze(self, payload=None, routes=None, route_result=None):
        return analyze_candidate_promotion_assessments(
            payload or self.payload,
            self.candidates,
            routes or self.routes,
            route_result or self.route_result,
        )

    def test_real_assessment_is_valid_and_held(self):
        result = self.analyze()
        self.assertTrue(result["valid"], result["errors"])
        assessment = result["assessments"][0]
        self.assertTrue(assessment["donor_regression_executed_this_cycle"])
        self.assertTrue(assessment["synthetic_regression_fixture_observed"])
        self.assertFalse(assessment["historical_source_fixture_observed"])
        self.assertFalse(assessment["independent_fixture_provenance_ready"])
        self.assertFalse(assessment["history_archive_required_for_generation_readiness"])
        self.assertFalse(assessment["exact_adjacent_target_output_observed"])
        self.assertFalse(assessment["generation_admission_ready"])
        self.assertFalse(assessment["migration_path_admission_ready"])

    def test_archive_availability_alone_does_not_make_generation_ready(self):
        payload = copy.deepcopy(self.payload)
        payload["assessments"][0]["history_archive"]["available_for_inspection"] = True
        result = self.analyze(payload)
        self.assertTrue(result["valid"], result["errors"])
        assessment = result["assessments"][0]
        self.assertTrue(assessment["declared_history_archive_available_for_inspection"])
        self.assertFalse(assessment["independent_fixture_provenance_ready"])
        self.assertFalse(assessment["generation_admission_ready"])

    def test_archive_unavailable_does_not_block_independent_exact_provenance_control(self):
        payload = copy.deepcopy(self.payload)
        routes = copy.deepcopy(self.routes)
        route_result = copy.deepcopy(self.route_result)

        payload["assessments"][0]["source_fixture"] = {
            "kind": "historical_value",
            "historical_value_observed": True,
            "observation": "Synthetic readiness-composition control only; not donor evidence.",
        }
        payload["assessments"][0]["generation_admission_ready"] = True
        payload["assessments"][0]["history_archive"]["available_for_inspection"] = False

        route = routes["records"][1]
        route["kind"] = "exact-historical-artifact"
        route["historical_value_observed"] = True
        route["independent_fixture_provenance_ready"] = True

        route_evidence = route_result["records"][1]
        route_evidence["kind"] = "exact-historical-artifact"
        route_evidence["independent_exact_historical_artifact_valid"] = True
        route_evidence["independent_fixture_provenance_ready"] = True
        route_result["independent_ready_count"] = 2

        result = self.analyze(payload, routes, route_result)
        self.assertTrue(result["valid"], result["errors"])
        assessment = result["assessments"][0]
        self.assertTrue(assessment["historical_source_fixture_observed"])
        self.assertTrue(assessment["independent_fixture_provenance_ready"])
        self.assertFalse(assessment["declared_history_archive_available_for_inspection"])
        self.assertTrue(assessment["generation_admission_ready"])
        self.assertFalse(assessment["migration_path_admission_ready"])

    def test_falsifier_rejects_synthetic_fixture_promoted_as_historical(self):
        payload = copy.deepcopy(self.payload)
        payload["assessments"][0]["source_fixture"]["historical_value_observed"] = True
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("historical-source-observation-route-mismatch:") for e in result["errors"]))
        self.assertTrue(any(e.startswith("synthetic-fixture-cannot-be-historical:") for e in result["errors"]))

    def test_falsifier_rejects_candidate_gap_claiming_provenance_ready(self):
        route_result = copy.deepcopy(self.route_result)
        route_result["records"][1]["independent_fixture_provenance_ready"] = True
        result = self.analyze(route_result=route_result)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("non-exact-historical-route-cannot-be-provenance-ready:") for e in result["errors"]))

    def test_falsifier_rejects_invalid_lower_route_evidence(self):
        route_result = copy.deepcopy(self.route_result)
        route_result["valid"] = False
        result = self.analyze(route_result=route_result)
        self.assertFalse(result["valid"])
        self.assertIn("historical-route-evidence-invalid", result["errors"])

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

    def test_checked_in_evidence_matches_current_analysis(self):
        expected = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(self.analyze(), expected)


if __name__ == "__main__":
    unittest.main()
