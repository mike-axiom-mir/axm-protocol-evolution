from __future__ import annotations

import unittest

from protocol_evolution import CompatibilityState, digest, migration_receipt, verify_migration_receipt_chain


class MigrationReceiptChainTests(unittest.TestCase):
    def setUp(self):
        self.g1 = {"schema": "demo/v1", "value": 1}
        self.g2 = {"schema": "demo/v2", "value": 1}
        self.g3 = {"schema": "demo/v3", "value": 1}
        self.r12 = migration_receipt(
            source=self.g1,
            target=self.g2,
            transformer="demo-v1-to-v2/v1",
            state=CompatibilityState.LOSSLESS_MIGRATION,
            assertions_checked=["demo.value-preserved"],
        )
        self.r23 = migration_receipt(
            source=self.g2,
            target=self.g3,
            transformer="demo-v2-to-v3/v1",
            state=CompatibilityState.LOSSLESS_MIGRATION,
            assertions_checked=["demo.value-preserved"],
        )

    def test_contiguous_receipts_bind_as_declared_chain(self):
        result = verify_migration_receipt_chain([self.r12, self.r23], source=self.g1, target=self.g3)
        self.assertTrue(result["chain_valid"])
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["receipt_count"], 2)
        self.assertFalse(result["authenticity_proven"])
        self.assertFalse(result["transform_execution_proven"])
        self.assertFalse(result["semantic_truth_proven"])
        self.assertFalse(result["direct_equivalence_proven"])

    def test_individually_valid_but_discontinuous_receipts_fail_chain(self):
        unrelated = {"schema": "demo/v2", "value": 99}
        r_unrelated_to_3 = migration_receipt(
            source=unrelated,
            target=self.g3,
            transformer="demo-unrelated-v2-to-v3/v1",
            state=CompatibilityState.AMBIGUOUS,
        )
        result = verify_migration_receipt_chain([self.r12, r_unrelated_to_3])
        self.assertFalse(result["chain_valid"])
        self.assertIn("link-0-1-digest-mismatch", result["failures"])

    def test_endpoint_payload_mismatch_is_visible(self):
        wrong_source = {"schema": "demo/v1", "value": 2}
        result = verify_migration_receipt_chain([self.r12, self.r23], source=wrong_source, target=self.g3)
        self.assertFalse(result["chain_valid"])
        self.assertIn("receipt-0:source-digest-mismatch", result["failures"])

    def test_receipt_failure_is_prefixed_with_chain_position(self):
        mutated = dict(self.r23)
        mutated["transformer"] = "rewritten-without-rehash/v1"
        result = verify_migration_receipt_chain([self.r12, mutated])
        self.assertFalse(result["chain_valid"])
        self.assertIn("receipt-1:receipt-digest-mismatch", result["failures"])

    def test_empty_chain_refuses_to_claim_continuity(self):
        result = verify_migration_receipt_chain([])
        self.assertFalse(result["chain_valid"])
        self.assertEqual(result["failures"], ["empty-chain"])
        self.assertEqual(result["receipt_count"], 0)

    def test_rehashed_declared_chain_still_is_not_authentication_or_semantic_proof(self):
        rewritten = dict(self.r23)
        rewritten["compatibility_state"] = CompatibilityState.AMBIGUOUS.value
        body = {key: value for key, value in rewritten.items() if key != "receipt_digest"}
        rewritten["receipt_digest"] = digest(body)
        result = verify_migration_receipt_chain([self.r12, rewritten], source=self.g1, target=self.g3)
        self.assertTrue(result["chain_valid"])
        self.assertFalse(result["authenticity_proven"])
        self.assertFalse(result["semantic_truth_proven"])
        self.assertFalse(result["direct_equivalence_proven"])


if __name__ == "__main__":
    unittest.main()
