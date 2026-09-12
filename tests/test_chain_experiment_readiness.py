from __future__ import annotations

import json
from pathlib import Path
import unittest

from protocol_evolution.migration_paths import CATALOG_SCHEMA, analyze_chain_experiment_readiness
from tools.chain_experiment_readiness import build_chain_experiment_readiness

ROOT = Path(__file__).resolve().parents[1]
LINEAGE_SCHEMA = "axm.protocol-evolution.generation-lineages/v0.1"


def synthetic_lineage(count: int = 5):
    manifests = [{"id": f"g{i}", "domain": "synthetic.domain"} for i in range(1, count + 1)]
    catalog = {
        "schema": LINEAGE_SCHEMA,
        "lineages": [
            {
                "id": "synthetic",
                "domain": "synthetic.domain",
                "generations": [f"g{i}" for i in range(1, count + 1)],
            }
        ],
    }
    return manifests, catalog


class ChainExperimentReadinessTests(unittest.TestCase):
    def test_current_corpus_exposes_adjacent_path_gap(self):
        result = build_chain_experiment_readiness()
        self.assertTrue(result["valid"])
        self.assertEqual(result["fixture_count"], 6)
        self.assertEqual(result["max_lineage_length"], 4)
        self.assertEqual(result["admitted_path_count"], 0)
        self.assertFalse(result["chain_experiment_input_ready"])

        rows = {row["id"]: row for row in result["lineages"]}
        self.assertEqual(rows["city-p2p-handshake"]["required_adjacent_path_count"], 1)
        self.assertEqual(rows["framestate-project"]["required_adjacent_path_count"], 3)
        self.assertEqual(
            rows["framestate-project"]["missing_adjacent_paths"],
            [
                {"source_generation": "framestate-project-v0.1", "target_generation": "framestate-project-v0.2"},
                {"source_generation": "framestate-project-v0.2", "target_generation": "framestate-project-v0.4"},
                {"source_generation": "framestate-project-v0.4", "target_generation": "framestate-project-v0.5"},
            ],
        )

    def test_five_generation_lineage_without_paths_is_not_input_ready(self):
        manifests, lineages = synthetic_lineage(5)
        result = analyze_chain_experiment_readiness(
            manifests, lineages, {"schema": CATALOG_SCHEMA, "paths": []}, target_length=5
        )
        self.assertTrue(result["valid"])
        self.assertFalse(result["chain_experiment_input_ready"])
        self.assertTrue(result["lineages"][0]["lineage_length_ready"])
        self.assertEqual(len(result["lineages"][0]["missing_adjacent_paths"]), 4)

    def test_complete_adjacent_path_admissions_enable_input_not_proof(self):
        manifests, lineages = synthetic_lineage(5)
        paths = []
        for index in range(1, 5):
            paths.append(
                {
                    "id": f"path-{index}",
                    "lineage_id": "synthetic",
                    "source_generation": f"g{index}",
                    "target_generation": f"g{index + 1}",
                    "evidence_refs": [f"evidence/path-{index}.json"],
                }
            )
        result = analyze_chain_experiment_readiness(
            manifests, lineages, {"schema": CATALOG_SCHEMA, "paths": paths}, target_length=5
        )
        self.assertTrue(result["valid"])
        self.assertTrue(result["chain_experiment_input_ready"])
        self.assertFalse(result["evidence_references_independently_verified"])
        self.assertFalse(result["migration_execution_proven"])
        self.assertFalse(result["semantic_equivalence_proven"])
        self.assertFalse(result["direct_migration_equivalence_proven"])

    def test_non_adjacent_path_is_rejected(self):
        manifests, lineages = synthetic_lineage(5)
        paths = {
            "schema": CATALOG_SCHEMA,
            "paths": [
                {
                    "id": "skip",
                    "lineage_id": "synthetic",
                    "source_generation": "g1",
                    "target_generation": "g3",
                    "evidence_refs": ["evidence/skip.json"],
                }
            ],
        }
        result = analyze_chain_experiment_readiness(manifests, lineages, paths, target_length=5)
        self.assertFalse(result["valid"])
        self.assertIn("path-skip:not-declared-adjacent-edge:g1:g3", result["failures"])

    def test_path_without_evidence_refs_is_rejected(self):
        manifests, lineages = synthetic_lineage(2)
        paths = {
            "schema": CATALOG_SCHEMA,
            "paths": [
                {
                    "id": "unproven",
                    "lineage_id": "synthetic",
                    "source_generation": "g1",
                    "target_generation": "g2",
                    "evidence_refs": [],
                }
            ],
        }
        result = analyze_chain_experiment_readiness(manifests, lineages, paths, target_length=2)
        self.assertFalse(result["valid"])
        self.assertIn("path-unproven:missing-or-invalid-evidence-refs", result["failures"])

    def test_duplicate_admission_for_same_edge_is_rejected(self):
        manifests, lineages = synthetic_lineage(2)
        base = {
            "lineage_id": "synthetic",
            "source_generation": "g1",
            "target_generation": "g2",
            "evidence_refs": ["evidence/path.json"],
        }
        paths = {"schema": CATALOG_SCHEMA, "paths": [dict(base, id="a"), dict(base, id="b")]}
        result = analyze_chain_experiment_readiness(manifests, lineages, paths, target_length=2)
        self.assertFalse(result["valid"])
        self.assertTrue(any(item.startswith("duplicate-adjacent-path:") for item in result["failures"]))

    def test_checked_in_readiness_matches_generated_truth(self):
        expected = json.loads(
            (ROOT / "evidence" / "chain_experiment_readiness.json").read_text(encoding="utf-8")
        )
        self.assertEqual(build_chain_experiment_readiness(), expected)


if __name__ == "__main__":
    unittest.main()
