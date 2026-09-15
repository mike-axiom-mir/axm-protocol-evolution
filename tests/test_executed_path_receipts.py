from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from protocol_evolution.compatibility import digest
from protocol_evolution.executed_path_receipts import analyze_executed_path_receipts


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "executed_path_receipts.json"
EXECUTION_FIXTURE = ROOT / "fixtures" / "path_execution_observations.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rehash(receipt: dict) -> None:
    body = {key: deepcopy(value) for key, value in receipt.items() if key != "receipt_digest"}
    receipt["receipt_digest"] = digest(body)


class ExecutedPathReceiptTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_json(FIXTURE)

    def analyze(self, payload=None, *, execution_payload=None):
        return analyze_executed_path_receipts(
            deepcopy(payload if payload is not None else self.payload),
            ROOT,
            execution_payload=deepcopy(execution_payload) if execution_payload is not None else None,
        )

    def test_current_real_executed_path_receipt_binds(self):
        result = self.analyze()
        self.assertTrue(result["valid"], result["failures"])
        self.assertEqual(result["valid_receipt_count"], 1)
        record = result["records"][0]
        self.assertEqual(record["path_id"], "framestate-v0.4-to-v0.5-canonical-normalization")
        self.assertEqual(record["compatibility_state"], "LOSSLESS_MIGRATION")
        self.assertEqual(record["assertions_checked"], ["undeclared_speech_engine=espeak"])
        self.assertFalse(result["receipt_self_digest_proves_authorship"])
        self.assertFalse(result["receipt_self_digest_proves_transformer_execution"])
        self.assertFalse(result["receipt_self_digest_proves_semantic_truth"])
        self.assertFalse(result["whole_project_semantic_equivalence_proven"])
        self.assertFalse(result["direct_vs_chain_equivalence_proven"])
        self.assertFalse(result["chain_experiment_input_ready"])
        self.assertFalse(result["canon_authority_granted"])
        self.assertFalse(result["adapter_translation_garden_ownership_changed"])

    def test_rehashed_wrong_source_digest_fails(self):
        payload = deepcopy(self.payload)
        receipt = payload["receipts"][0]["receipt"]
        receipt["source_digest"] = receipt["target_digest"]
        rehash(receipt)
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("source-digest" in failure for failure in result["failures"]))

    def test_rehashed_wrong_target_digest_fails(self):
        payload = deepcopy(self.payload)
        receipt = payload["receipts"][0]["receipt"]
        receipt["target_digest"] = receipt["source_digest"]
        rehash(receipt)
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("target-digest" in failure for failure in result["failures"]))

    def test_rehashed_transformer_drift_fails(self):
        payload = deepcopy(self.payload)
        receipt = payload["receipts"][0]["receipt"]
        receipt["transformer"] = "invented/translator#run"
        rehash(receipt)
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("transformer-identity-mismatch" in failure for failure in result["failures"]))

    def test_rehashed_compatibility_state_drift_fails(self):
        payload = deepcopy(self.payload)
        receipt = payload["receipts"][0]["receipt"]
        receipt["compatibility_state"] = "SAME"
        rehash(receipt)
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("compatibility-state-not-grounded" in failure for failure in result["failures"]))

    def test_rehashed_semantic_assertion_drift_fails(self):
        payload = deepcopy(self.payload)
        receipt = payload["receipts"][0]["receipt"]
        receipt["assertions_checked"] = ["whole_project_equivalent=true"]
        rehash(receipt)
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("semantic-assertion-binding-mismatch" in failure for failure in result["failures"]))

    def test_unknown_path_cannot_gain_receipt_binding(self):
        payload = deepcopy(self.payload)
        payload["receipts"][0]["path_id"] = "invented-path"
        result = self.analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("unknown-admitted-path" in failure for failure in result["failures"]))

    def test_invalid_lower_execution_evidence_fails_closed(self):
        execution_payload = load_json(EXECUTION_FIXTURE)
        execution_payload["observations"][0]["donor_commit"] = "0" * 40
        result = self.analyze(execution_payload=execution_payload)
        self.assertFalse(result["valid"])
        self.assertIn("path-execution-evidence-invalid", result["failures"])

    def test_rehashed_loss_or_ambiguity_claim_fails(self):
        for field in ("losses", "ambiguities"):
            with self.subTest(field=field):
                payload = deepcopy(self.payload)
                receipt = payload["receipts"][0]["receipt"]
                receipt[field] = ["invented"]
                rehash(receipt)
                result = self.analyze(payload)
                self.assertFalse(result["valid"])
                self.assertTrue(any(f"unexpected-{field[:-1] if field.endswith('s') else field}" in failure or field[:-1] in failure for failure in result["failures"]))


if __name__ == "__main__":
    unittest.main()
