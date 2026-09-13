#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from protocol_evolution.historical_fixture_routes import analyze_historical_fixture_routes

FIXTURE = ROOT / "fixtures" / "historical_fixture_routes.json"


def main() -> int:
    result = analyze_historical_fixture_routes(json.loads(FIXTURE.read_text(encoding="utf-8")), ROOT)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
