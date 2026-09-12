from __future__ import annotations

import json
from pathlib import Path
import unittest

from protocol_evolution.lineage import analyze_generation_lineages
from tools.lineage_readiness import build_lineage_readiness, load_manifests

ROOT = Path(__file__).resolve().parents[1]


class LineageReadinessTests(unittest.TestCase):
    def test_six_fixtures_do_not_fake_one_five_generation_chain(self):
        result = build_lineage_readiness()
        self.assertTrue(result["valid"])
        self.assertEqual(result["fixture_count"], 6)
        self.assertEqual(result["max_lineage_length"], 4)
        self.assertTrue(result["fixture_count_meets_target_but_no_lineage_does"])
        self.assertFalse(result["chain_ready"])
        self.assertEqual(result["ready_lineages"], [])

    def test_current_declared_lineages_preserve_domain_boundaries(self):
        result = build_lineage_readiness()
        rows = {row["id"]: row for row in result["lineages"]}
        self.assertEqual(rows["city-p2p-handshake"]["generation_count"], 2)
        self.assertEqual(rows["framestate-project"]["generation_count"], 4)
        self.assertEqual(rows["framestate-project"]["target_gap"], 1)
        self.assertEqual(
            rows["framestate-project"]["generations"],
            [
                "framestate-project-v0.1",
                "framestate-project-v0.2",
                "framestate-project-v0.4",
                "framestate-project-v0.5",
            ],
        )

    def test_cross_domain_fixture_in_one_lineage_is_rejected(self):
        manifests = load_manifests()
        catalog = {
            "schema": "axm.protocol-evolution.generation-lineages/v0.1",
            "lineages": [
                {
                    "id": "invalid-mixed",
                    "domain": "framestate.project",
                    "generations": ["framestate-project-v0.1", "city-p2p-handshake-g1"],
                }
            ],
        }
        result = analyze_generation_lineages(manifests, catalog, target_length=5)
        self.assertFalse(result["valid"])
        self.assertIn(
            "lineage-invalid-mixed:domain-mismatch:city-p2p-handshake-g1:city.multiplayer.handshake",
            result["failures"],
        )

    def test_checked_in_readiness_matches_generated_truth(self):
        expected = json.loads((ROOT / "evidence" / "lineage_readiness.json").read_text(encoding="utf-8"))
        self.assertEqual(build_lineage_readiness(), expected)

    def test_unknown_or_unassigned_generation_is_visible(self):
        manifests = load_manifests()
        catalog = json.loads((ROOT / "fixtures" / "lineages.json").read_text(encoding="utf-8"))
        catalog["lineages"][1]["generations"].append("framestate-project-v9.9")
        result = analyze_generation_lineages(manifests, catalog, target_length=5)
        self.assertFalse(result["valid"])
        self.assertIn(
            "lineage-framestate-project:unknown-generation:framestate-project-v9.9",
            result["failures"],
        )


if __name__ == "__main__":
    unittest.main()
