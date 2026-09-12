from __future__ import annotations

import unittest

from protocol_evolution import CompatibilityState, digest, migration_receipt, verify_migration_receipt_binding


class MigrationReceiptBindingTests(unittest.TestCase):
    def setUp(self):
        self.source = {"schema": "demo/v1", "value": 1}
        self.target = {"schema": "demo/v2", "value": 1}
        self.receipt = migration_receipt(
            source=self.source,
            target=self.target,
            transformer="demo-schema-bump/v1",
            state=CompatibilityState.LOSSLESS_MIGRATION,
            assertions_checked=["demo.value-preserved"],
        )

    def test_generated_receipt_binds_supplied_payloads(self):
        result = verify_migration_receipt_binding(self.receipt, source=self.source, target=self.target)
        self.assertTrue(result["binding_valid"])
        self.assertEqual(result["failures"], [])
        self.assertFalse(result["authenticity_proven"])
        self.assertFalse(result["semantic_truth_proven"])

    def test_wrong_target_fails_binding(self):
        wrong_target = {"schema": "demo/v2", "value": 2}
        result = verify_migration_receipt_binding(self.receipt, source=self.source, target=wrong_target)
        self.assertFalse(result["binding_valid"])
        self.assertIn("target-digest-mismatch", result["failures"])

    def test_mutated_receipt_without_rehash_fails(self):
        mutated = dict(self.receipt)
        mutated["transformer"] = "different-transformer/v1"
        result = verify_migration_receipt_binding(mutated, source=self.source, target=self.target)
        self.assertFalse(result["binding_valid"])
        self.assertIn("receipt-digest-mismatch", result["failures"])

    def test_rehashed_unexpected_field_remains_outside_contract(self):
        expanded = dict(self.receipt)
        expanded["authority"] = "merge"
        body = {key: value for key, value in expanded.items() if key != "receipt_digest"}
        expanded["receipt_digest"] = digest(body)
        result = verify_migration_receipt_binding(expanded, source=self.source, target=self.target)
        self.assertFalse(result["binding_valid"])
        self.assertIn("unexpected-fields:authority", result["failures"])

    def test_self_consistent_rewrite_is_not_authentication_or_semantic_proof(self):
        rewritten = dict(self.receipt)
        rewritten["compatibility_state"] = CompatibilityState.AMBIGUOUS.value
        body = {key: value for key, value in rewritten.items() if key != "receipt_digest"}
        rewritten["receipt_digest"] = digest(body)
        result = verify_migration_receipt_binding(rewritten, source=self.source, target=self.target)
        self.assertTrue(result["binding_valid"])
        self.assertFalse(result["authenticity_proven"])
        self.assertFalse(result["semantic_truth_proven"])


if __name__ == "__main__":
    unittest.main()
