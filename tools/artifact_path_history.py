#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from protocol_evolution.artifact_path_history import analyze_artifact_path_history

OBSERVATIONS = ROOT / "fixtures" / "artifact_path_history_observations.json"
ROUTES = ROOT / "fixtures" / "historical_fixture_routes.json"


def main() -> int:
    result = analyze_artifact_path_history(
        json.loads(OBSERVATIONS.read_text(encoding="utf-8")),
        json.loads(ROUTES.read_text(encoding="utf-8")),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
