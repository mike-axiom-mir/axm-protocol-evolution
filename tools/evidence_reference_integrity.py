from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from protocol_evolution.evidence_refs import analyze_evidence_reference_integrity


def build_evidence_reference_integrity():
    path_catalog = json.loads((ROOT / "fixtures" / "migration_paths.json").read_text(encoding="utf-8"))
    investigation_catalog = json.loads(
        (ROOT / "fixtures" / "migration_path_investigations.json").read_text(encoding="utf-8")
    )
    return analyze_evidence_reference_integrity(path_catalog, investigation_catalog)


if __name__ == "__main__":
    result = build_evidence_reference_integrity()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["valid"] else 1)
