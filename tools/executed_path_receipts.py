from __future__ import annotations

import json
from pathlib import Path

from protocol_evolution.executed_path_receipts import analyze_executed_path_receipts


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    payload = json.loads((ROOT / "fixtures" / "executed_path_receipts.json").read_text(encoding="utf-8"))
    result = analyze_executed_path_receipts(payload, ROOT)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
