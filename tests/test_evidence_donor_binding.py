from __future__ import annotations

import json
from pathlib import Path
import unittest

from protocol_evolution.evidence_donor_binding import analyze_evidence_donor_binding
from tools.evidence_donor_binding import build_evidence_donor_binding

ROOT = Path(__file__).resolve().parents[1]
SHA_A = "a" * 40


def _snapshot(ref: str, repository: str, sha: str):
    return {
        "schema": "axm.protocol-evolution.evidence-reference-resolution-observations/v0.1",
        "observed_at": "2026-09-13",
        "method": "github-api-connected-read",
        "observations": [
            {
                "ref": ref,
                "resolved": True,
                "repository": repository,
                "kind": "commit",
                "commit_refs": [sha],
                "observed_commit_sha": sha,
            }
        ],
    }


def _path_catalog(ref: str, source: str = "g1", target: str = "g2"):
    return {
        "paths": [
            {
                "id": "edge",
                "source_generation": source,
                "target_generation": target,
                "evidence_refs": [ref],
            }
        ]
    }


class EvidenceDonorBindingTests(unittest.TestCase):
    def test_resolved_reference_from_unrelated_repository_fails(self):
        ref = f"https://github.com/example/other/commit/{SHA_A}"
        result = analyze_evidence_donor_binding(
            _path_catalog(ref),
            {"investigations": []},
            _snapshot(ref, "example/other", SHA_A),
            [
                {"id": "g1", "repository": "example/donor"},
                {"id": "g2", "repository": "example/donor"},
            ],
        )
        self.assertFalse(result["valid"])
        self.assertFalse(
            result["all_catalog_references_bound_to_declared_generation_repositories"]
        )
        self.assertTrue(
            any(
                "repository-outside-declared-generations:example/other" in item
                for item in result["failures"]
            )
        )

    def test_cross_repository_edge_can_use_either_declared_generation_repository(self):
        ref = f"https://github.com/example/target/commit/{SHA_A}"
        result = analyze_evidence_donor_binding(
            _path_catalog(ref),
            {"investigations": []},
            _snapshot(ref, "example/target", SHA_A),
            [
                {"id": "g1", "repository": "example/source"},
                {"id": "g2", "repository": "example/target"},
            ],
        )
        self.assertTrue(result["valid"])
        self.assertEqual(
            result["records"][0]["declared_generation_repositories"],
            ["example/source", "example/target"],
        )

    def test_unknown_generation_fails_closed(self):
        ref = f"https://github.com/example/donor/commit/{SHA_A}"
        result = analyze_evidence_donor_binding(
            _path_catalog(ref, target="missing"),
            {"investigations": []},
            _snapshot(ref, "example/donor", SHA_A),
            [{"id": "g1", "repository": "example/donor"}],
        )
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("unknown-target-generation:missing" in item for item in result["failures"])
        )

    def test_duplicate_generation_manifest_id_fails_closed(self):
        ref = f"https://github.com/example/donor/commit/{SHA_A}"
        result = analyze_evidence_donor_binding(
            _path_catalog(ref),
            {"investigations": []},
            _snapshot(ref, "example/donor", SHA_A),
            [
                {"id": "g1", "repository": "example/donor"},
                {"id": "g1", "repository": "example/donor"},
                {"id": "g2", "repository": "example/donor"},
            ],
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("duplicate-id:g1" in item for item in result["failures"]))

    def test_current_catalogs_bind_all_evidence_to_declared_generation_repositories(self):
        result = build_evidence_donor_binding()
        self.assertTrue(result["valid"])
        self.assertTrue(result["resolution_evidence_valid"])
        self.assertTrue(
            result["all_catalog_references_bound_to_declared_generation_repositories"]
        )
        self.assertEqual(result["generation_manifest_count"], 6)
        self.assertEqual(result["declared_generation_repository_count"], 2)
        self.assertEqual(result["record_count"], 4)
        self.assertEqual(result["reference_count"], 15)
        self.assertEqual(result["donor_bound_reference_count"], 15)
        self.assertTrue(result["repository_binding_only"])
        self.assertFalse(result["reference_target_content_semantically_verified"])
        self.assertFalse(result["authorship_verified"])
        self.assertFalse(result["migration_execution_proven"])

    def test_checked_in_donor_binding_evidence_matches_generated_truth(self):
        expected = json.loads(
            (ROOT / "evidence" / "evidence_donor_binding.json").read_text(encoding="utf-8")
        )
        self.assertEqual(build_evidence_donor_binding(), expected)


if __name__ == "__main__":
    unittest.main()
