#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from protocol_evolution.historical_fixture_generation_binding import (
    analyze_historical_fixture_generation_bindings,
)
from protocol_evolution.historical_fixture_routes import analyze_historical_fixture_routes

BINDINGS = ROOT / "fixtures" / "historical_fixture_generation_bindings.json"
ROUTES = ROOT / "fixtures" / "historical_fixture_routes.json"


def build_historical_fixture_generation_binding():
    binding_payload = json.loads(BINDINGS.read_text(encoding="utf-8"))
    route_payload = json.loads(ROUTES.read_text(encoding="utf-8"))
    route_result = analyze_historical_fixture_routes(route_payload, ROOT)
    generation_records = [
        {
            "manifest_path": path.relative_to(ROOT).as_posix(),
            "manifest": json.loads(path.read_text(encoding="utf-8")),
        }
        for path in sorted((ROOT / "fixtures" / "generations").glob("*/manifest.json"))
    ]
    return analyze_historical_fixture_generation_bindings(
        binding_payload,
        route_payload,
        route_result,
        generation_records,
    )


def main() -> int:
    result = build_historical_fixture_generation_binding()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
