from __future__ import annotations

import json
from pathlib import Path
import unittest

from protocol_evolution import CompatibilityState, carry_unknown_fields, compare_semantics, migration_receipt, negotiate_capabilities

ROOT = Path(__file__).resolve().parents[1]


def framestate_speech_meaning(project):
    schema = project["schema"]
    speech = next(row for row in project["audio"] if row["kind"] == "speech")
    engine = speech.get("engine")
    if engine is None:
        engine = "native" if schema == "axm.framestate.project/v0.5" else "espeak"
    return {"speech_engine": engine, "text": speech.get("text", "")}


class SemanticCompatibilityTests(unittest.TestCase):
    def load(self, relative):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_naive_framestate_schema_bump_changes_meaning(self):
        old = self.load("fixtures/generations/framestate-v0.4/project.json")
        naive = dict(old)
        naive["schema"] = "axm.framestate.project/v0.5"
        state = compare_semantics(old, naive, projector=framestate_speech_meaning, migrated=True)
        self.assertEqual(state, CompatibilityState.AMBIGUOUS)

    def test_explicit_engine_preserves_old_meaning(self):
        old = self.load("fixtures/generations/framestate-v0.4/project.json")
        migrated = json.loads(json.dumps(old))
        migrated["schema"] = "axm.framestate.project/v0.5"
        migrated["audio"][0]["engine"] = "espeak"
        state = compare_semantics(old, migrated, projector=framestate_speech_meaning, migrated=True)
        self.assertEqual(state, CompatibilityState.LOSSLESS_MIGRATION)

    def test_unknown_future_field_survives_old_intermediary(self):
        future = {"schema": "demo/v2", "known": {"counter": 1}, "future_extension": {"meaning": "owned-by-v2", "bits": [1, 0, 1]}}
        carried = carry_unknown_fields(future, known_fields={"schema", "known"}, transform_known=lambda known: {**known, "known": {"counter": known["known"]["counter"] + 1}})
        self.assertEqual(carried["future_extension"], future["future_extension"])
        self.assertEqual(carried["known"]["counter"], 2)

    def test_unknown_field_cannot_be_claimed_by_transformer(self):
        with self.assertRaises(ValueError):
            carry_unknown_fields({"known": 1, "future": 2}, known_fields={"known"}, transform_known=lambda known: {"known": 3, "future": "rewrite"})

    def test_capabilities_do_not_follow_product_version(self):
        left = {"handshake.hello": "1", "handshake.ack-admission": "2"}
        right = {"handshake.hello": "1"}
        result = negotiate_capabilities(left, right, required={"handshake.hello", "handshake.ack-admission"})
        self.assertEqual(result["state"], CompatibilityState.UNSUPPORTED.value)
        self.assertEqual(result["shared"], {"handshake.hello": "1"})
        self.assertEqual(result["qualified_shared"], {"handshake.hello": "1"})
        self.assertEqual(result["missing_required"], ["handshake.ack-admission"])
        self.assertEqual(result["unobserved_required"], [])
        self.assertEqual(result["insufficient_evidence_required"], [])

    def test_incomplete_inventory_does_not_turn_missing_evidence_into_unsupported(self):
        result = negotiate_capabilities(
            {},
            {"timeline.integer-sample": "axm.callable-capability/v0.1"},
            required={"timeline.integer-sample"},
            left_complete=False,
        )
        self.assertEqual(result["state"], CompatibilityState.AMBIGUOUS.value)
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["unobserved_required"], ["timeline.integer-sample"])
        self.assertEqual(result["insufficient_evidence_required"], [])

    def test_complete_inventory_missing_required_capability_is_unsupported(self):
        result = negotiate_capabilities(
            {},
            {"timeline.integer-sample": "axm.callable-capability/v0.1"},
            required={"timeline.integer-sample"},
            left_complete=True,
        )
        self.assertEqual(result["state"], CompatibilityState.UNSUPPORTED.value)
        self.assertEqual(result["missing_required"], ["timeline.integer-sample"])
        self.assertEqual(result["unobserved_required"], [])
        self.assertEqual(result["insufficient_evidence_required"], [])

    def test_observed_version_mismatch_is_unsupported_even_with_incomplete_inventories(self):
        result = negotiate_capabilities(
            {"timeline.integer-sample": "v0.1"},
            {"timeline.integer-sample": "v0.2"},
            required={"timeline.integer-sample"},
            left_complete=False,
            right_complete=False,
        )
        self.assertEqual(result["state"], CompatibilityState.UNSUPPORTED.value)
        self.assertEqual(result["version_mismatches"], ["timeline.integer-sample"])
        self.assertEqual(result["unobserved_required"], [])
        self.assertEqual(result["insufficient_evidence_required"], [])

    def test_shared_exact_capability_survives_unobserved_second_requirement(self):
        result = negotiate_capabilities(
            {"handshake.hello": "1"},
            {"handshake.hello": "1", "handshake.ack-admission": "2"},
            required={"handshake.hello", "handshake.ack-admission"},
            left_complete=False,
        )
        self.assertEqual(result["state"], CompatibilityState.AMBIGUOUS.value)
        self.assertEqual(result["shared"], {"handshake.hello": "1"})
        self.assertEqual(result["qualified_shared"], {"handshake.hello": "1"})
        self.assertEqual(result["unobserved_required"], ["handshake.ack-admission"])

    def test_execution_threshold_does_not_promote_declaration_equality(self):
        capability = "timeline.integer-sample"
        version = "axm.callable-capability/v0.1"
        result = negotiate_capabilities(
            {capability: version},
            {capability: version},
            required={capability},
            left_evidence={capability: "declared"},
            right_evidence={capability: "declared"},
            minimum_evidence="executed",
        )
        self.assertEqual(result["state"], CompatibilityState.AMBIGUOUS.value)
        self.assertEqual(result["shared"], {capability: version})
        self.assertEqual(result["qualified_shared"], {})
        self.assertEqual(result["insufficient_evidence_required"], [capability])
        self.assertEqual(result["evidence_shortfalls"], {capability: ["left", "right"]})

    def test_execution_threshold_accepts_exact_execution_grounded_pair(self):
        capability = "timeline.integer-sample"
        version = "axm.callable-capability/v0.1"
        result = negotiate_capabilities(
            {capability: version},
            {capability: version},
            required={capability},
            left_evidence={capability: "executed"},
            right_evidence={capability: "executed"},
            minimum_evidence="executed",
        )
        self.assertEqual(result["state"], CompatibilityState.SAME.value)
        self.assertEqual(result["qualified_shared"], {capability: version})
        self.assertEqual(result["insufficient_evidence_required"], [])

    def test_version_mismatch_stays_unsupported_under_execution_threshold(self):
        capability = "timeline.integer-sample"
        result = negotiate_capabilities(
            {capability: "v0.1"},
            {capability: "v0.2"},
            required={capability},
            left_evidence={capability: "declared"},
            right_evidence={capability: "declared"},
            minimum_evidence="executed",
        )
        self.assertEqual(result["state"], CompatibilityState.UNSUPPORTED.value)
        self.assertEqual(result["version_mismatches"], [capability])
        self.assertEqual(result["insufficient_evidence_required"], [])

    def test_unknown_capability_evidence_level_is_rejected(self):
        capability = "timeline.integer-sample"
        with self.assertRaises(ValueError):
            negotiate_capabilities(
                {capability: "v0.1"},
                {capability: "v0.1"},
                required={capability},
                left_evidence={capability: "probably"},
            )

    def test_receipt_binds_source_target_and_result(self):
        source = {"schema": "demo/v1", "value": 1}
        target = {"schema": "demo/v2", "value": 1}
        receipt = migration_receipt(source=source, target=target, transformer="test-explicit-schema-bump/v1", state=CompatibilityState.LOSSLESS_MIGRATION, assertions_checked=["demo.value-preserved"])
        self.assertTrue(receipt["source_digest"].startswith("sha256:"))
        self.assertTrue(receipt["target_digest"].startswith("sha256:"))
        self.assertNotEqual(receipt["source_digest"], receipt["target_digest"])
        self.assertTrue(receipt["receipt_digest"].startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
