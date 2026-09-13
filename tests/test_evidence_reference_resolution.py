from __future__ import annotations

import json
from pathlib import Path
import unittest

from protocol_evolution.evidence_resolution import analyze_evidence_reference_resolution
from tools.evidence_reference_resolution import build_evidence_reference_resolution

ROOT = Path(__file__).resolve().parents[1]
FULL = "a" * 40


def _catalog(ref: str):
    return {"paths": [{"id": "edge", "evidence_refs": [ref]}]}, {"investigations": []}


def _snapshot(observations):
    return {
        "schema": "axm.protocol-evolution.evidence-reference-resolution-observations/v0.1",
        "observed_at": "2026-09-13",
        "method": "github-api-connected-read",
        "observations": observations,
    }


class EvidenceReferenceResolutionTests(unittest.TestCase):
    def test_structural_pinning_alone_does_not_prove_resolution(self):
        ref = f"https://github.com/example/repo/commit/{FULL}"
        paths, investigations = _catalog(ref)
        result = analyze_evidence_reference_resolution(paths, investigations, _snapshot([]))
        self.assertFalse(result["valid"])
        self.assertFalse(result["all_catalog_references_have_resolution_observations"])
        self.assertIn(f"missing-resolution-observation:{ref}", result["failures"])

    def test_resolution_observation_must_bind_to_exact_commit(self):
        ref = f"https://github.com/example/repo/commit/{FULL}"
        paths, investigations = _catalog(ref)
        observation = {
            "ref": ref,
            "resolved": True,
            "repository": "example/repo",
            "kind": "commit",
            "commit_refs": [FULL],
            "observed_commit_sha": "b" * 40,
        }
        result = analyze_evidence_reference_resolution(paths, investigations, _snapshot([observation]))
        self.assertFalse(result["valid"])
        self.assertTrue(any("commit-sha-mismatch" in item for item in result["failures"]))

    def test_current_catalogs_have_complete_observed_resolution_snapshot(self):
        result = build_evidence_reference_resolution()
        self.assertTrue(result["valid"])
        self.assertTrue(result["all_catalog_references_have_resolution_observations"])
        self.assertEqual(result["catalog_reference_occurrence_count"], 15)
        self.assertEqual(result["unique_catalog_reference_count"], 15)
        self.assertEqual(result["observation_count"], 15)
        self.assertEqual(result["resolved_observation_count"], 15)
        self.assertFalse(result["live_resolution_reverified_by_analyzer"])
        self.assertFalse(result["observation_snapshot_cryptographically_attested"])
        self.assertFalse(result["reference_target_content_semantically_verified"])
        self.assertFalse(result["authorship_verified"])
        self.assertFalse(result["migration_execution_proven"])

    def test_missing_blob_identity_fails_closed(self):
        ref = f"https://github.com/example/repo/blob/{FULL}/proof.txt"
        paths, investigations = _catalog(ref)
        observation = {
            "ref": ref,
            "resolved": True,
            "repository": "example/repo",
            "kind": "blob",
            "commit_refs": [FULL],
        }
        result = analyze_evidence_reference_resolution(paths, investigations, _snapshot([observation]))
        self.assertFalse(result["valid"])
        self.assertTrue(any("invalid-observed-blob-sha" in item for item in result["failures"]))

    def test_checked_in_resolution_evidence_matches_generated_truth(self):
        expected = json.loads(
            (ROOT / "evidence" / "evidence_reference_resolution.json").read_text(encoding="utf-8")
        )
        self.assertEqual(build_evidence_reference_resolution(), expected)


if __name__ == "__main__":
    unittest.main()
