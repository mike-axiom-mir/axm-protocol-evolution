from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("survivability_matrix", ROOT / "tools" / "survivability_matrix.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class MatrixTests(unittest.TestCase):
    def test_matrix_reaches_five_real_generation_target(self):
        matrix = MODULE.build_matrix()
        self.assertEqual(matrix["fixture_count"], 5)
        self.assertEqual(matrix["research_ladder_target"], 5)
        self.assertEqual(matrix["fixture_gap"], 0)

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

    def test_checked_in_matrix_matches_generated_evidence(self):
        checked_in = json.loads((ROOT / "evidence" / "generation_matrix.json").read_text(encoding="utf-8"))
        self.assertEqual(checked_in, MODULE.build_matrix())


if __name__ == "__main__":
    unittest.main()
