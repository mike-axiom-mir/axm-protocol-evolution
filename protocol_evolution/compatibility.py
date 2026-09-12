from __future__ import annotations

from copy import deepcopy
from enum import StrEnum
import hashlib
import json
from typing import Any, Callable, Iterable, Mapping


class CompatibilityState(StrEnum):
    SAME = "SAME"
    LOSSLESS_MIGRATION = "LOSSLESS_MIGRATION"
    LOSSY_VISIBLE = "LOSSY_VISIBLE"
    UNKNOWN_FIELD_PRESERVED = "UNKNOWN_FIELD_PRESERVED"
    UNSUPPORTED = "UNSUPPORTED"
    AMBIGUOUS = "AMBIGUOUS"
    REFUSE = "REFUSE"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def compare_semantics(source_payload: Any, target_payload: Any, *, projector: Callable[[Any], Any], migrated: bool = False) -> CompatibilityState:
    """Compare meaning through a caller-owned semantic projector."""
    before = projector(deepcopy(source_payload))
    after = projector(deepcopy(target_payload))
    if before == after:
        return CompatibilityState.LOSSLESS_MIGRATION if migrated and source_payload != target_payload else CompatibilityState.SAME
    return CompatibilityState.AMBIGUOUS


def carry_unknown_fields(payload: Mapping[str, Any], *, known_fields: Iterable[str], transform_known: Callable[[dict[str, Any]], Mapping[str, Any]]) -> dict[str, Any]:
    """Transform known state while carrying unknown state opaquely."""
    known_set = set(known_fields)
    known = {k: deepcopy(v) for k, v in payload.items() if k in known_set}
    unknown = {k: deepcopy(v) for k, v in payload.items() if k not in known_set}
    transformed = dict(transform_known(known))
    collisions = sorted(set(transformed) & set(unknown))
    if collisions:
        raise ValueError(f"transformer attempted authority over unknown fields: {collisions}")
    result = deepcopy(transformed)
    result.update(unknown)
    return result


def migration_receipt(*, source: Any, target: Any, transformer: str, state: CompatibilityState, assertions_checked: Iterable[str] = (), losses: Iterable[str] = (), ambiguities: Iterable[str] = ()) -> dict[str, Any]:
    body = {
        "schema": "axm.protocol-evolution.migration-receipt/v0.1",
        "source_digest": digest(source),
        "target_digest": digest(target),
        "transformer": transformer,
        "compatibility_state": state.value,
        "losses": list(losses),
        "ambiguities": list(ambiguities),
        "assertions_checked": list(assertions_checked),
    }
    body["receipt_digest"] = digest(body)
    return body
