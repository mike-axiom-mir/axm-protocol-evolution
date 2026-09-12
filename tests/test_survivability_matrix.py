from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from protocol_evolution import CompatibilityState

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("survivability_matrix", ROOT / "tools" / "survivability_matrix.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class MatrixTests(unittest.TestCase):
    def test_matrix_tracks_six_real_fixtures_without_moving_target(self):
        matrix = MODULE.build_matrix()
        self.assertEqual(matrix["fixture_count"], 6)
        self.assertEqual(matrix["research_ladder_target"], 5)
        self.assertEqual(matrix["fixture_gap"], 0)
        self.assertEqual(matrix["schema"], "axm.protocol-evolution.survivability-matrix/v0.3")

    def test_changed_meaning_is_not_called_compatible(self):
        matrix = MODULE.build_matrix()
        relation = {(row["from"], row["to"]): row["state"] for row in matrix["rows"]}
        self.assertEqual(relation[("framestate-project-v0.4", "framestate-project-v0.5")], "UNSUPPORTED")
        self.assertEqual(relation[("city-p2p-handshake-g1", "city-p2p-handshake-g2")], "UNSUPPORTED")

    def test_version_difference_does_not_imply_semantic_difference(self):
        matrix = MODULE.build_matrix()
        relation = {(row["from"], row["to"]): row["state"] for row in matrix["rows"]}
        self.assertEqual(relation[("framestate-project-v0.2", "framestate-project-v0.4")], "SAME")
        self.assertEqual(relation[("framestate-project-v0.4", "framestate-project-v0.2")], "SAME")
        self.assertEqual(relation[("framestate-project-v0.2", "framestate-project-v0.5")], "UNSUPPORTED")

    def test_same_domain_without_shared_claim_is_unjudged(self):
        matrix = MODULE.build_matrix()
        rows = {(row["from"], row["to"]): row for row in matrix["rows"]}
        row = rows[("framestate-project-v0.1", "framestate-project-v0.2")]
        self.assertFalse(row["comparable"])
        self.assertIsNone(row["state"])
        self.assertEqual(row["reason"], "no-common-semantic-claim")

    def test_cross_domain_pairs_are_unjudged_not_fake_states(self):
        matrix = MODULE.build_matrix()
        rows = {(row["from"], row["to"]): row for row in matrix["rows"]}
        cross = rows[("city-p2p-handshake-g1", "framestate-project-v0.1")]
        self.assertFalse(cross["comparable"])
        self.assertIsNone(cross["state"])
        self.assertEqual(cross["reason"], "different-domain")

    def test_every_emitted_compatibility_state_is_declared(self):
        matrix = MODULE.build_matrix()
        declared = {state.value for state in CompatibilityState}
        emitted = {row["state"] for row in matrix["rows"] if row["state"] is not None}
        self.assertLessEqual(emitted, declared)

    def test_checked_in_matrix_matches_generated_evidence(self):
        checked_in = json.loads((ROOT / "evidence" / "generation_matrix.json").read_text(encoding="utf-8"))
        self.assertEqual(checked_in, MODULE.build_matrix())


if __name__ == "__main__":
    unittest.main()
