import copy
import json
import unittest
from pathlib import Path

from protocol_evolution.artifact_path_history import analyze_artifact_path_history
from protocol_evolution.historical_evidence_closure import (
    analyze_historical_fixture_evidence_closure,
)
from protocol_evolution.historical_fixture_generation_binding import (
    analyze_historical_fixture_generation_bindings,
)
from protocol_evolution.historical_fixture_routes import analyze_historical_fixture_routes
from tools.historical_evidence_closure import build_historical_evidence_closure

ROOT = Path(__file__).resolve().parents[1]
BINDINGS = ROOT / "fixtures" / "historical_fixture_generation_bindings.json"
OBSERVATIONS = ROOT / "fixtures" / "artifact_path_history_observations.json"
ROUTES = ROOT / "fixtures" / "historical_fixture_routes.json"
EVIDENCE = ROOT / "evidence" / "historical_evidence_closure.json"


class HistoricalEvidenceClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
        cls.observations = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
        cls.routes = json.loads(ROUTES.read_text(encoding="utf-8"))
        cls.generations = [
            {
                "manifest_path": path.relative_to(ROOT).as_posix(),
                "manifest": json.loads(path.read_text(encoding="utf-8")),
            }
            for path in sorted((ROOT / "fixtures" / "generations").glob("*/manifest.json"))
        ]

    def lower_results(self):
        route_result = analyze_historical_fixture_routes(self.routes, ROOT)
        binding_result = analyze_historical_fixture_generation_bindings(
            self.bindings,
            self.routes,
            route_result,
            self.generations,
        )
        path_history_result = analyze_artifact_path_history(self.observations, self.routes)
        return route_result, binding_result, path_history_result

    def analyze(self, route_result=None, binding_result=None, path_history_result=None):
        lower_route, lower_binding, lower_history = self.lower_results()
        return analyze_historical_fixture_evidence_closure(
            self.routes,
            route_result if route_result is not None else lower_route,
            binding_result if binding_result is not None else lower_binding,
            path_history_result if path_history_result is not None else lower_history,
        )

    def test_real_exact_route_closes_once_across_all_evidence_layers(self):
        result = self.analyze()
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["exact_historical_route_count"], 1)
        self.assertEqual(result["closed_exact_route_count"], 1)
        self.assertTrue(result["all_exact_historical_routes_closed_across_evidence_layers"])
        record = result["records"][0]
        self.assertEqual(
            record["route_id"],
            "framestate-v0.1-independent-historical-artifact-control",
        )
        self.assertEqual(record["generation_id"], "framestate-project-v0.1")
        self.assertEqual(
            record["path_history_observation_id"],
            "framestate-v0.1-first-light-path-history-control",
        )
        self.assertTrue(record["closed"])

    def test_falsifier_rejects_invalid_lower_route_evidence(self):
        route_result, _, _ = self.lower_results()
        route_result = copy.deepcopy(route_result)
        route_result["valid"] = False
        result = self.analyze(route_result=route_result)
        self.assertFalse(result["valid"])
        self.assertIn("historical-fixture-route-evidence-invalid", result["errors"])

    def test_falsifier_rejects_binding_without_positive_path_history_support(self):
        _, _, path_history = self.lower_results()
        path_history = copy.deepcopy(path_history)
        path_history["records"][0]["historical_observation_supported_by_path_history"] = False
        result = self.analyze(path_history_result=path_history)
        self.assertFalse(result["valid"])
        self.assertIn(
            "exact-route-missing-positive-path-history-support:framestate-v0.1-independent-historical-artifact-control",
            result["errors"],
        )

    def test_falsifier_rejects_history_support_without_successful_generation_binding(self):
        _, binding, _ = self.lower_results()
        binding = copy.deepcopy(binding)
        binding["records"][0]["identity_tuple_matches"] = False
        result = self.analyze(binding_result=binding)
        self.assertFalse(result["valid"])
        self.assertIn(
            "exact-route-missing-successful-generation-binding:framestate-v0.1-independent-historical-artifact-control",
            result["errors"],
        )

    def test_falsifier_rejects_duplicate_successful_generation_binding(self):
        _, binding, _ = self.lower_results()
        binding = copy.deepcopy(binding)
        duplicate = copy.deepcopy(binding["records"][0])
        duplicate["id"] = "duplicate-successful-binding"
        binding["records"].append(duplicate)
        result = self.analyze(binding_result=binding)
        self.assertFalse(result["valid"])
        self.assertIn(
            "duplicate-successful-generation-binding:framestate-v0.1-independent-historical-artifact-control",
            result["errors"],
        )

    def test_falsifier_rejects_duplicate_positive_path_history_support(self):
        _, _, path_history = self.lower_results()
        path_history = copy.deepcopy(path_history)
        duplicate = copy.deepcopy(path_history["records"][0])
        duplicate["id"] = "duplicate-positive-history"
        path_history["records"].append(duplicate)
        result = self.analyze(path_history_result=path_history)
        self.assertFalse(result["valid"])
        self.assertIn(
            "duplicate-positive-path-history-support:framestate-v0.1-independent-historical-artifact-control",
            result["errors"],
        )

    def test_falsifier_rejects_candidate_gap_counted_as_positive_history(self):
        _, _, path_history = self.lower_results()
        path_history = copy.deepcopy(path_history)
        candidate = path_history["records"][1]
        candidate["historical_observation_supported_by_path_history"] = True
        candidate["artifact_kind"] = "exact-historical-artifact"
        result = self.analyze(path_history_result=path_history)
        self.assertFalse(result["valid"])
        self.assertIn(
            "non-exact-route-history-supported:living-city-world-v0.1.0-independent-historical-artifact-gap:candidate-gap",
            result["errors"],
        )

    def test_falsifier_rejects_unknown_route_in_successful_binding(self):
        _, binding, _ = self.lower_results()
        binding = copy.deepcopy(binding)
        binding["records"][0]["route_id"] = "missing-route"
        result = self.analyze(binding_result=binding)
        self.assertFalse(result["valid"])
        self.assertIn("binding-unknown-route:missing-route", result["errors"])
        self.assertIn(
            "exact-route-missing-successful-generation-binding:framestate-v0.1-independent-historical-artifact-control",
            result["errors"],
        )

    def test_checked_in_evidence_matches_generated_truth(self):
        expected = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(build_historical_evidence_closure(), expected)


if __name__ == "__main__":
    unittest.main()
