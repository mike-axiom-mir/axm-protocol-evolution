from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from protocol_evolution.lineage import analyze_generation_lineages


def load_manifests():
    manifests = []
    base = ROOT / "fixtures" / "generations"
    for path in sorted(base.glob("*/manifest.json")):
        manifests.append(json.loads(path.read_text(encoding="utf-8")))
    return manifests


def build_lineage_readiness():
    catalog = json.loads((ROOT / "fixtures" / "lineages.json").read_text(encoding="utf-8"))
    return analyze_generation_lineages(load_manifests(), catalog, target_length=5)


if __name__ == "__main__":
    print(json.dumps(build_lineage_readiness(), indent=2, sort_keys=True))
