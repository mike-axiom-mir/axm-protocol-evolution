from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("survivability_matrix", ROOT / "tools" / "survivability_matrix.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class MatrixTests(unittest.TestCase):
    def test_matrix_is_explicit_about_open_fifth_fixture(self):
        matrix = MODULE.build_matrix()
        self.assertEqual(matrix["fixture_count"], 4)
        self.assertEqual(matrix["research_ladder_target"], 5)
        self.assertEqual(matrix["fixture_gap"], 1)

    def test_changed_meaning_is_not_called_compatible(self):
        matrix = MODULE.build_matrix()
        relation = {(row["from"], row["to"]): row["state"] for row in matrix["rows"]}
        self.assertEqual(relation[("framestate-project-v0.4", "framestate-project-v0.5")], "UNSUPPORTED")
        self.assertEqual(relation[("city-p2p-handshake-g1", "city-p2p-handshake-g2")], "UNSUPPORTED")


if __name__ == "__main__":
    unittest.main()
