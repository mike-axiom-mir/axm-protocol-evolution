from __future__ import annotations

import unittest

from protocol_evolution.migration_paths import (
    CATALOG_SCHEMA,
    INVESTIGATION_SCHEMA,
    analyze_chain_experiment_readiness,
)
from tools.chain_experiment_readiness import build_chain_experiment_readiness


LINEAGE_SCHEMA = "axm.protocol-evolution.generation-lineages/v0.1"


def two_generation_lineage():
    manifests = [
        {"id": "g1", "domain": "synthetic.domain"},
        {"id": "g2", "domain": "synthetic.domain"},
    ]
    lineages = {
        "schema": LINEAGE_SCHEMA,
        "lineages": [
            {
                "id": "synthetic",
                "domain": "synthetic.domain",
                "generations": ["g1", "g2"],
            }
        ],
    }
    return manifests, lineages


class EdgeStateConflictTests(unittest.TestCase):
    def test_same_edge_cannot_be_admitted_and_held(self):
        manifests, lineages = two_generation_lineage()
        paths = {
            "schema": CATALOG_SCHEMA,
            "paths": [
                {
                    "id": "admit-g1-g2",
                    "lineage_id": "synthetic",
                    "source_generation": "g1",
                    "target_generation": "g2",
                    "evidence_refs": ["evidence/admission.json"],
                }
            ],
        }
        investigations = {
            "schema": INVESTIGATION_SCHEMA,
            "investigations": [
                {
                    "id": "hold-g1-g2",
                    "lineage_id": "synthetic",
                    "source_generation": "g1",
                    "target_generation": "g2",
                    "status": "HOLD",
                    "evidence_refs": ["evidence/hold.json"],
                    "finding": "The available evidence does not establish a migration.",
                    "blocker": "The exact edge remains unproven.",
                }
            ],
        }

        result = analyze_chain_experiment_readiness(
            manifests,
            lineages,
            paths,
            investigations,
            target_length=2,
        )

        self.assertFalse(result["valid"])
        self.assertFalse(result["chain_experiment_input_ready"])
        self.assertEqual(result["admitted_path_count"], 1)
        self.assertEqual(result["investigation_count"], 0)
        self.assertIn(
            "conflicting-admission-and-hold:synthetic:g1:g2:admit-g1-g2:hold-g1-g2",
            result["failures"],
        )

    def test_current_catalogs_remain_non_conflicting(self):
        result = build_chain_experiment_readiness()
        self.assertTrue(result["valid"])
        self.assertFalse(
            any(item.startswith("conflicting-admission-and-hold:") for item in result["failures"])
        )


if __name__ == "__main__":
    unittest.main()
