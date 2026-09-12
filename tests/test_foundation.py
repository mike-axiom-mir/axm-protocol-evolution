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
        self.assertEqual(result["missing_required"], ["handshake.ack-admission"])

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
