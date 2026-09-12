from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from protocol_evolution.compatibility import CompatibilityState


def load_manifests():
    manifests = []
    base = ROOT / "fixtures" / "generations"
    for path in sorted(base.glob("*/manifest.json")):
        manifests.append(json.loads(path.read_text(encoding="utf-8")))
    return manifests


def relation(left, right):
    if left["domain"] != right["domain"]:
        return "NOT_COMPARABLE"
    if left["semantic_claims"] == right["semantic_claims"]:
        return CompatibilityState.SAME.value
    return CompatibilityState.UNSUPPORTED.value


def build_matrix():
    manifests = load_manifests()
    rows = []
    for left in manifests:
        for right in manifests:
            rows.append({"from": left["id"], "to": right["id"], "state": relation(left, right)})
    return {"schema": "axm.protocol-evolution.survivability-matrix/v0.1", "fixture_count": len(manifests), "research_ladder_target": 5, "fixture_gap": max(0, 5 - len(manifests)), "rows": rows}


if __name__ == "__main__":
    print(json.dumps(build_matrix(), indent=2, sort_keys=True))
