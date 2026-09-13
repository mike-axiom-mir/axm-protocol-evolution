from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from protocol_evolution.evidence_roles import analyze_evidence_roles
from tools.evidence_donor_binding import build_evidence_donor_binding


def build_evidence_roles():
    path_catalog = json.loads(
        (ROOT / "fixtures" / "migration_paths.json").read_text(encoding="utf-8")
    )
    investigation_catalog = json.loads(
        (ROOT / "fixtures" / "migration_path_investigations.json").read_text(
            encoding="utf-8"
        )
    )
    role_catalog = json.loads(
        (ROOT / "fixtures" / "evidence_reference_roles.json").read_text(
            encoding="utf-8"
        )
    )
    donor_binding_result = build_evidence_donor_binding()
    return analyze_evidence_roles(
        path_catalog,
        investigation_catalog,
        role_catalog,
        donor_binding_result,
    )


def build_admitted_evidence_roles():
    """Compatibility alias retained for callers of the first role-binding cycle."""
    return build_evidence_roles()


if __name__ == "__main__":
    result = build_evidence_roles()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["valid"] else 1)
