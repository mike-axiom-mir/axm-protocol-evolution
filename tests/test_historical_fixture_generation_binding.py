import copy
import json
import unittest
from pathlib import Path

from protocol_evolution.historical_fixture_generation_binding import (
    analyze_historical_fixture_generation_bindings,
)
from protocol_evolution.historical_fixture_routes import analyze_historical_fixture_routes
from tools.historical_fixture_generation_binding import (
    build_historical_fixture_generation_binding,
)

ROOT = Path(__file__).resolve().parents[1]
BINDINGS = ROOT / "fixtures" / "historical_fixture_generation_bindings.json"
ROUTES = ROOT / "fixtures" / "historical_fixture_routes.json"
EVIDENCE = ROOT / "evidence" / "historical_fixture_generation_binding.json"


class HistoricalFixtureGenerationBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
        cls.routes = json.loads(ROUTES.read_text(encoding="utf-8"))
        cls.generations = [
            {
                "manifest_path": path.relative_to(ROOT).as_posix(),
                "manifest": json.loads(path.read_text(encoding="utf-8")),
            }
            for path in sorted((ROOT / "fixtures" / "generations").glob("*/manifest.json"))
        ]

    def analyze(self, bindings=None, routes=None, generations=None, route_result=None):
        binding_payload = bindings if bindings is not None else self.bindings
        route_payload = routes if routes is not None else self.routes
        generation_records = generations if generations is not None else self.generations
        lower = route_result if route_result is not None else analyze_historical_fixture_routes(route_payload, ROOT)
        return analyze_historical_fixture_generation_bindings(
            binding_payload,
            route_payload,
            lower,
            generation_records,
        )

    def test_real_exact_route_binds_to_the_same_admitted_generation_identity(self):
        result = self.analyze()
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["exact_historical_route_count"], 1)
        self.assertEqual(result["binding_count"], 1)
        self.assertEqual(result["bound_exact_historical_route_count"], 1)
        self.assertTrue(result["all_exact_historical_routes_bound_to_generation_manifests"])
        record = result["records"][0]
        self.assertEqual(record["generation_id"], "framestate-project-v0.1")
        self.assertEqual(
            record["expected_fixture_path"],
            "fixtures/generations/framestate-v0.1/project.json",
        )
        self.assertTrue(record["identity_tuple_matches"])

    def test_falsifier_rejects_route_repository_drift(self):
        routes = copy.deepcopy(self.routes)
        routes["records"][0]["repository"] = "example/other"
        result = self.analyze(routes=routes)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("route-generation-repository-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_route_commit_drift(self):
        routes = copy.deepcopy(self.routes)
        routes["records"][0]["commit"] = "1" * 40
        result = self.analyze(routes=routes)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("route-generation-commit-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_route_source_path_drift(self):
        routes = copy.deepcopy(self.routes)
        routes["records"][0]["source_path"] = "examples/not_first_light.json"
        result = self.analyze(routes=routes)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("route-generation-source-path-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_unknown_generation(self):
        bindings = copy.deepcopy(self.bindings)
        bindings["bindings"][0]["generation_id"] = "missing-generation"
        result = self.analyze(bindings=bindings)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("unknown-generation:") for e in result["errors"]))

    def test_falsifier_rejects_candidate_gap_as_generation_binding(self):
        bindings = copy.deepcopy(self.bindings)
        bindings["bindings"][0]["route_id"] = "living-city-world-v0.1.0-independent-historical-artifact-gap"
        result = self.analyze(bindings=bindings)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("route-not-exact-historical-artifact:") for e in result["errors"]))
        self.assertTrue(any(e.startswith("exact-route-missing-generation-binding:") for e in result["errors"]))

    def test_falsifier_rejects_missing_exact_route_binding(self):
        bindings = copy.deepcopy(self.bindings)
        bindings["bindings"] = []
        result = self.analyze(bindings=bindings)
        self.assertFalse(result["valid"])
        self.assertIn(
            "exact-route-missing-generation-binding:framestate-v0.1-independent-historical-artifact-control",
            result["errors"],
        )

    def test_falsifier_rejects_same_exact_route_bound_twice(self):
        bindings = copy.deepcopy(self.bindings)
        duplicate = copy.deepcopy(bindings["bindings"][0])
        duplicate["id"] = "second-binding-for-same-route"
        bindings["bindings"].append(duplicate)
        result = self.analyze(bindings=bindings)
        self.assertFalse(result["valid"])
        self.assertIn(
            "route-bound-more-than-once:framestate-v0.1-independent-historical-artifact-control",
            result["errors"],
        )

    def test_falsifier_rejects_manifest_artifact_drift(self):
        generations = copy.deepcopy(self.generations)
        target = next(
            item for item in generations if item["manifest"].get("id") == "framestate-project-v0.1"
        )
        target["manifest"]["artifact"] = "different.json"
        result = self.analyze(generations=generations)
        self.assertFalse(result["valid"])
        self.assertTrue(any(e.startswith("route-generation-fixture-path-mismatch:") for e in result["errors"]))

    def test_falsifier_rejects_invalid_lower_route_evidence(self):
        result = self.analyze(route_result={"valid": False, "records": []})
        self.assertFalse(result["valid"])
        self.assertIn("historical-fixture-route-evidence-invalid", result["errors"])

    def test_checked_in_evidence_matches_generated_truth(self):
        expected = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(build_historical_fixture_generation_binding(), expected)


if __name__ == "__main__":
    unittest.main()
