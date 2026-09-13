from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from protocol_evolution.evidence_donor_binding import analyze_evidence_donor_binding


def build_evidence_donor_binding():
    path_catalog = json.loads(
        (ROOT / "fixtures" / "migration_paths.json").read_text(encoding="utf-8")
    )
    investigation_catalog = json.loads(
        (ROOT / "fixtures" / "migration_path_investigations.json").read_text(encoding="utf-8")
    )
    observation_snapshot = json.loads(
        (
            ROOT
            / "evidence"
            / "evidence_reference_resolution_observations_2026-09-13.json"
        ).read_text(encoding="utf-8")
    )
    generation_manifests = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "fixtures" / "generations").glob("*/manifest.json"))
    ]
    return analyze_evidence_donor_binding(
        path_catalog,
        investigation_catalog,
        observation_snapshot,
        generation_manifests,
    )


if __name__ == "__main__":
    result = build_evidence_donor_binding()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["valid"] else 1)
