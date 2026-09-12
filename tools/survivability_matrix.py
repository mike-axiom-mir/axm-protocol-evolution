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
        return {"comparable": False, "state": None, "reason": "different-domain"}

    left_claims = left["semantic_claims"]
    right_claims = right["semantic_claims"]
    if left_claims == right_claims:
        return {"comparable": True, "state": CompatibilityState.SAME.value, "reason": "tested-semantic-claims-equal"}

    common_claims = sorted(set(left_claims) & set(right_claims))
    if not common_claims:
        return {"comparable": False, "state": None, "reason": "no-common-semantic-claim"}

    if all(left_claims[key] == right_claims[key] for key in common_claims):
        return {"comparable": False, "state": None, "reason": "partial-semantic-claim-overlap"}

    return {
        "comparable": True,
        "state": CompatibilityState.UNSUPPORTED.value,
        "reason": "tested-common-semantic-claims-differ",
    }


def build_matrix():
    manifests = load_manifests()
    rows = []
    for left in manifests:
        for right in manifests:
            rows.append({"from": left["id"], "to": right["id"], **relation(left, right)})
    return {
        "schema": "axm.protocol-evolution.survivability-matrix/v0.3",
        "fixture_count": len(manifests),
        "research_ladder_target": 5,
        "fixture_gap": max(0, 5 - len(manifests)),
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(build_matrix(), indent=2, sort_keys=True))
