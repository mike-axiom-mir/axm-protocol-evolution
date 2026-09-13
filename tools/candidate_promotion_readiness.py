#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from protocol_evolution.candidate_promotion import analyze_candidate_promotion_assessments
from protocol_evolution.historical_fixture_routes import analyze_historical_fixture_routes

ASSESSMENTS = ROOT / "fixtures" / "candidate_promotion_assessments.json"
CANDIDATES = ROOT / "fixtures" / "monolith_candidate_observations.json"
ROUTES = ROOT / "fixtures" / "historical_fixture_routes.json"


def main() -> int:
    route_payload = json.loads(ROUTES.read_text(encoding="utf-8"))
    route_result = analyze_historical_fixture_routes(route_payload, ROOT)
    result = analyze_candidate_promotion_assessments(
        json.loads(ASSESSMENTS.read_text(encoding="utf-8")),
        json.loads(CANDIDATES.read_text(encoding="utf-8")),
        route_payload,
        route_result,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
