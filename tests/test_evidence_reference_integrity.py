from __future__ import annotations

import json
from pathlib import Path
import unittest

from protocol_evolution.evidence_refs import (
    analyze_evidence_reference_integrity,
    inspect_pinned_github_reference,
)
from tools.evidence_reference_integrity import build_evidence_reference_integrity

ROOT = Path(__file__).resolve().parents[1]


class EvidenceReferenceIntegrityTests(unittest.TestCase):
    def test_current_catalogs_use_structurally_pinned_donor_refs(self):
        result = build_evidence_reference_integrity()
        self.assertTrue(result["valid"])
        self.assertTrue(result["all_references_structurally_pinned"])
        self.assertEqual(result["record_count"], 4)
        self.assertEqual(result["reference_count"], 15)
        self.assertEqual(result["pinned_reference_count"], 15)
        self.assertFalse(result["resource_existence_verified"])
        self.assertFalse(result["reference_target_content_verified"])
        self.assertFalse(result["authorship_verified"])
        self.assertFalse(result["semantic_claim_verified"])
        self.assertFalse(result["migration_execution_proven"])

    def test_mutable_branch_blob_is_rejected(self):
        result = inspect_pinned_github_reference(
            "https://github.com/mike-axiom-mir/axm-framestate/blob/main/CHANGELOG.md"
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "blob-reference-not-full-sha")

    def test_short_commit_hash_is_rejected(self):
        result = inspect_pinned_github_reference(
            "https://github.com/mike-axiom-mir/axm-framestate/commit/df019c5"
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "commit-reference-not-full-sha")

    def test_compare_requires_both_full_commit_hashes(self):
        result = inspect_pinned_github_reference(
            "https://github.com/mike-axiom-mir/axm-framestate/compare/"
            "5d46363fb30bf5d30198b8cdec473d3bb9ba6287...main"
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "compare-reference-endpoint-not-full-sha")

    def test_duplicate_reference_padding_is_rejected(self):
        pinned = (
            "https://github.com/mike-axiom-mir/axm-framestate/commit/"
            "df019c55e6e2c4f46f7bda59ccc5bdc229921737"
        )
        path_catalog = {
            "paths": [
                {
                    "id": "same-ref-twice",
                    "evidence_refs": [pinned, pinned],
                }
            ]
        }
        investigation_catalog = {"investigations": []}
        result = analyze_evidence_reference_integrity(path_catalog, investigation_catalog)
        self.assertFalse(result["valid"])
        self.assertTrue(any("duplicate-evidence-ref" in item for item in result["failures"]))

    def test_non_github_string_cannot_masquerade_as_pinned_donor_evidence(self):
        result = inspect_pinned_github_reference("trust-me-this-was-tested")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "reference-not-https-github")

    def test_checked_in_integrity_evidence_matches_generated_truth(self):
        expected = json.loads(
            (ROOT / "evidence" / "evidence_reference_integrity.json").read_text(encoding="utf-8")
        )
        self.assertEqual(build_evidence_reference_integrity(), expected)


if __name__ == "__main__":
    unittest.main()
