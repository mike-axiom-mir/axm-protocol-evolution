from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from protocol_evolution.migration_paths import analyze_chain_experiment_readiness
from tools.lineage_readiness import load_manifests


def build_chain_experiment_readiness():
    lineage_catalog = json.loads((ROOT / "fixtures" / "lineages.json").read_text(encoding="utf-8"))
    path_catalog = json.loads((ROOT / "fixtures" / "migration_paths.json").read_text(encoding="utf-8"))
    investigation_catalog = json.loads(
        (ROOT / "fixtures" / "migration_path_investigations.json").read_text(encoding="utf-8")
    )
    return analyze_chain_experiment_readiness(
        load_manifests(),
        lineage_catalog,
        path_catalog,
        investigation_catalog,
        target_length=5,
    )


if __name__ == "__main__":
    print(json.dumps(build_chain_experiment_readiness(), indent=2, sort_keys=True))
