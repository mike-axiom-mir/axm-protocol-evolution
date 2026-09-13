from __future__ import annotations

import json
from pathlib import Path
import unittest

from protocol_evolution.evidence_roles import analyze_evidence_roles
from tools.evidence_reference_roles import (
    build_admitted_evidence_roles,
    build_evidence_roles,
)

ROOT = Path(__file__).resolve().parents[1]
REF_A = "https://github.com/example/donor/commit/" + "a" * 40
REF_B = "https://github.com/example/donor/commit/" + "b" * 40
REF_C = "https://github.com/example/donor/commit/" + "c" * 40
REF_D = "https://github.com/example/donor/commit/" + "d" * 40


def _paths():
    return {"paths": [{"id": "admitted-edge", "evidence_refs": [REF_A, REF_B]}]}


def _investigations():
    return {
        "investigations": [
            {
                "id": "held-edge",
                "status": "HOLD",
                "evidence_refs": [REF_C, REF_D],
            }
        ]
    }


def _roles():
    return {
        "schema": "axm.protocol-evolution.evidence-reference-roles/v0.2",
        "records": [
            {
                "record_type": "path",
                "record_id": "admitted-edge",
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
            },
            {
                "record_type": "investigation",
                "record_id": "held-edge",
                "references": [
                    {
                        "ref": REF_C,
                        "role": "reader-compatibility-behavior",
                        "observation": "compatibility evidence",
                    },
                    {
                        "ref": REF_D,
                        "role": "historical-range",
                        "observation": "bounded search interval",
                    },
                ],
            },
        ],
    }


def _analyze(paths=None, investigations=None, roles=None, donor=None):
    return analyze_evidence_roles(
        paths or _paths(),
        investigations or _investigations(),
        roles or _roles(),
        donor or {"valid": True},
    )


class EdgeEvidenceRoleTests(unittest.TestCase):
    def test_missing_role_for_hold_reference_fails_closed(self):
        roles = _roles()
        roles["records"][1]["references"].pop()
        result = _analyze(roles=roles)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("missing-reference-role" in item for item in result["failures"])
        )

    def test_extra_reference_not_in_hold_investigation_fails_closed(self):
        roles = _roles()
        roles["records"][1]["references"].append(
            {
                "ref": "https://github.com/example/donor/commit/" + "e" * 40,
                "role": "protocol-baseline",
                "observation": "extra",
            }
        )
        result = _analyze(roles=roles)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("reference-not-in-investigation" in item for item in result["failures"])
        )

    def test_duplicate_hold_reference_assignment_fails_closed(self):
        roles = _roles()
        roles["records"][1]["references"][1]["ref"] = REF_C
        result = _analyze(roles=roles)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any(
                "duplicate-reference-assignment" in item
                for item in result["failures"]
            )
        )

    def test_unknown_role_fails_closed(self):
        roles = _roles()
        roles["records"][1]["references"][0]["role"] = "semantic-proof"
        result = _analyze(roles=roles)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("invalid-role:semantic-proof" in item for item in result["failures"])
        )

    def test_non_hold_investigation_status_fails_closed(self):
        investigations = _investigations()
        investigations["investigations"][0]["status"] = "ADMIT"
        result = _analyze(investigations=investigations)
        self.assertFalse(result["valid"])
        self.assertIn(
            "investigation-held-edge:unsupported-status:ADMIT",
            result["failures"],
        )
        self.assertFalse(result["hold_status_promoted_to_admission"])

    def test_unknown_investigation_role_record_fails_closed(self):
        roles = _roles()
        roles["records"][1]["record_id"] = "not-declared"
        result = _analyze(roles=roles)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("unknown-investigation:not-declared" in item for item in result["failures"])
        )

    def test_invalid_lower_evidence_layer_fails_closed(self):
        result = _analyze(donor={"valid": False})
        self.assertFalse(result["valid"])
        self.assertIn("donor-binding-invalid", result["failures"])

    def test_missing_admitted_path_role_still_fails_closed(self):
        roles = _roles()
        roles["records"] = [
            record for record in roles["records"] if record["record_type"] != "path"
        ]
        result = _analyze(roles=roles)
        self.assertFalse(result["valid"])
        self.assertIn(
            "path-admitted-edge:missing-role-record",
            result["failures"],
        )

    def test_current_corpus_has_exact_path_and_hold_role_coverage(self):
        result = build_evidence_roles()
        self.assertTrue(result["valid"])
        self.assertTrue(result["donor_binding_valid"])
        self.assertEqual(result["path_record_count"], 1)
        self.assertEqual(result["investigation_record_count"], 3)
        self.assertEqual(result["role_record_count"], 4)
        self.assertEqual(result["admitted_reference_count"], 4)
        self.assertEqual(result["hold_reference_count"], 11)
        self.assertEqual(result["total_reference_count"], 15)
        self.assertEqual(result["role_bound_path_reference_count"], 4)
        self.assertEqual(result["role_bound_hold_reference_count"], 11)
        self.assertEqual(result["role_bound_reference_count"], 15)
        self.assertTrue(result["all_edge_refs_have_exactly_one_declared_role"])
        self.assertTrue(result["all_hold_refs_have_exactly_one_declared_role"])
        self.assertFalse(result["hold_status_promoted_to_admission"])
        self.assertEqual(
            result["declared_role_counts"],
            {
                "behavior-preservation-check": 1,
                "donor-interpretation-note": 2,
                "historical-range": 3,
                "incompatibility-check": 1,
                "protocol-baseline": 1,
                "reader-compatibility-behavior": 2,
                "recovery-history": 2,
                "transition-introduction": 2,
                "transition-mechanism": 1,
            },
        )
        self.assertTrue(result["role_binding_only"])
        self.assertFalse(result["reference_target_content_semantically_verified"])
        self.assertFalse(result["evidence_sufficiency_verified"])
        self.assertFalse(result["migration_execution_proven"])
        self.assertFalse(result["chain_vs_direct_equivalence_proven"])

    def test_compatibility_builder_alias_matches_generalized_result(self):
        self.assertEqual(build_admitted_evidence_roles(), build_evidence_roles())

    def test_checked_in_role_evidence_matches_generated_truth(self):
        expected = json.loads(
            (ROOT / "evidence" / "evidence_reference_roles.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(build_evidence_roles(), expected)


if __name__ == "__main__":
    unittest.main()
