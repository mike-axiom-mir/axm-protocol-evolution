from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from protocol_evolution.evidence_roles import analyze_admitted_evidence_roles
from tools.evidence_reference_roles import build_admitted_evidence_roles

ROOT = Path(__file__).resolve().parents[1]
REF_A = "https://github.com/example/donor/commit/" + "a" * 40
REF_B = "https://github.com/example/donor/commit/" + "b" * 40


def _paths():
    return {
        "paths": [
            {
                "id": "edge",
                "evidence_refs": [REF_A, REF_B],
            }
        ]
    }


def _roles():
    return {
        "schema": "axm.protocol-evolution.evidence-reference-roles/v0.1",
        "records": [
            {
                "record_type": "path",
                "record_id": "edge",
                "references": [
                    {
                        "ref": REF_A,
                        "role": "transition-mechanism",
                        "observation": "mechanism evidence",
                    },
                    {
                        "ref": REF_B,
                        "role": "behavior-preservation-check",
                        "observation": "preservation evidence",
                    },
                ],
            }
        ],
    }


class AdmittedEvidenceRoleTests(unittest.TestCase):
    def test_missing_role_for_admitted_reference_fails_closed(self):
        roles = _roles()
        roles["records"][0]["references"].pop()
        result = analyze_admitted_evidence_roles(_paths(), roles, {"valid": True})
        self.assertFalse(result["valid"])
        self.assertTrue(any("missing-reference-role" in item for item in result["failures"]))

    def test_extra_reference_not_in_admitted_path_fails_closed(self):
        roles = _roles()
        roles["records"][0]["references"].append(
            {
                "ref": "https://github.com/example/donor/commit/" + "c" * 40,
                "role": "transition-introduction",
                "observation": "extra",
            }
        )
        result = analyze_admitted_evidence_roles(_paths(), roles, {"valid": True})
        self.assertFalse(result["valid"])
        self.assertTrue(any("reference-not-in-path" in item for item in result["failures"]))

    def test_duplicate_reference_assignment_fails_closed(self):
        roles = _roles()
        roles["records"][0]["references"][1]["ref"] = REF_A
        result = analyze_admitted_evidence_roles(_paths(), roles, {"valid": True})
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("duplicate-reference-assignment" in item for item in result["failures"])
        )

    def test_unknown_role_fails_closed(self):
        roles = _roles()
        roles["records"][0]["references"][0]["role"] = "semantic-proof"
        result = analyze_admitted_evidence_roles(_paths(), roles, {"valid": True})
        self.assertFalse(result["valid"])
        self.assertTrue(any("invalid-role:semantic-proof" in item for item in result["failures"]))

    def test_invalid_lower_evidence_layer_fails_closed(self):
        result = analyze_admitted_evidence_roles(_paths(), _roles(), {"valid": False})
        self.assertFalse(result["valid"])
        self.assertIn("donor-binding-invalid", result["failures"])

    def test_current_admitted_path_has_exact_role_coverage(self):
        result = build_admitted_evidence_roles()
        self.assertTrue(result["valid"])
        self.assertTrue(result["donor_binding_valid"])
        self.assertEqual(result["path_record_count"], 1)
        self.assertEqual(result["role_record_count"], 1)
        self.assertEqual(result["admitted_reference_count"], 4)
        self.assertEqual(result["role_bound_reference_count"], 4)
        self.assertTrue(result["all_admitted_path_refs_have_exactly_one_declared_role"])
        self.assertEqual(
            result["declared_role_counts"],
            {
                "behavior-preservation-check": 1,
                "donor-interpretation-note": 1,
                "transition-introduction": 1,
                "transition-mechanism": 1,
            },
        )
        self.assertTrue(result["role_binding_only"])
        self.assertFalse(result["reference_target_content_semantically_verified"])
        self.assertFalse(result["evidence_sufficiency_verified"])
        self.assertFalse(result["migration_execution_proven"])
        self.assertFalse(result["chain_vs_direct_equivalence_proven"])

    def test_checked_in_role_evidence_matches_generated_truth(self):
        expected = json.loads(
            (ROOT / "evidence" / "evidence_reference_roles.json").read_text(encoding="utf-8")
        )
        self.assertEqual(build_admitted_evidence_roles(), expected)


if __name__ == "__main__":
    unittest.main()
