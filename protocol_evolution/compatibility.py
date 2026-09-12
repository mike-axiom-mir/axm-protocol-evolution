from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Callable, Iterable


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


def verify_migration_receipt_binding(receipt: Mapping[str, Any], *, source: Any | None = None, target: Any | None = None) -> dict[str, Any]:
    """Verify only the receipt's self-digest and optional supplied payload identity.

    This deliberately does not authenticate an author, transformer, or semantic claim.
    A party that can rewrite a receipt can also recompute its plain SHA-256 digest.
    """
    failures: list[str] = []
    required = {
        "schema",
        "source_digest",
        "target_digest",
        "transformer",
        "compatibility_state",
        "losses",
        "ambiguities",
        "receipt_digest",
    }
    allowed = required | {"assertions_checked"}

    if not isinstance(receipt, Mapping):
        failures.append("receipt-not-object")
        return {
            "binding_valid": False,
            "failures": failures,
            "binding_scope": "receipt-self-digest-and-supplied-payload-identity",
            "authenticity_proven": False,
            "semantic_truth_proven": False,
        }

    raw = dict(receipt)
    missing = sorted(required - set(raw))
    extra = sorted(set(raw) - allowed)
    if missing:
        failures.append("missing-fields:" + ",".join(missing))
    if extra:
        failures.append("unexpected-fields:" + ",".join(extra))

    if raw.get("schema") != "axm.protocol-evolution.migration-receipt/v0.1":
        failures.append("unsupported-schema")

    digest_pattern = re.compile(r"^sha256:[0-9a-f]{64}$")
    for name in ("source_digest", "target_digest", "receipt_digest"):
        value = raw.get(name)
        if not isinstance(value, str) or digest_pattern.fullmatch(value) is None:
            failures.append(f"invalid-{name.replace('_', '-')}")

    transformer = raw.get("transformer")
    if not isinstance(transformer, str) or not transformer:
        failures.append("invalid-transformer")

    state = raw.get("compatibility_state")
    if state not in {member.value for member in CompatibilityState}:
        failures.append("invalid-compatibility-state")

    for name in ("losses", "ambiguities", "assertions_checked"):
        if name not in raw and name == "assertions_checked":
            continue
        value = raw.get(name)
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            failures.append(f"invalid-{name.replace('_', '-')}")

    body = {key: deepcopy(value) for key, value in raw.items() if key != "receipt_digest"}
    try:
        expected_receipt_digest = digest(body)
    except (TypeError, ValueError):
        failures.append("receipt-not-canonical-json")
    else:
        if raw.get("receipt_digest") != expected_receipt_digest:
            failures.append("receipt-digest-mismatch")

    if source is not None:
        try:
            expected_source_digest = digest(source)
        except (TypeError, ValueError):
            failures.append("source-not-canonical-json")
        else:
            if raw.get("source_digest") != expected_source_digest:
                failures.append("source-digest-mismatch")

    if target is not None:
        try:
            expected_target_digest = digest(target)
        except (TypeError, ValueError):
            failures.append("target-not-canonical-json")
        else:
            if raw.get("target_digest") != expected_target_digest:
                failures.append("target-digest-mismatch")

    return {
        "binding_valid": not failures,
        "failures": failures,
        "binding_scope": "receipt-self-digest-and-supplied-payload-identity",
        "authenticity_proven": False,
        "semantic_truth_proven": False,
    }


def verify_migration_receipt_chain(receipts: Iterable[Mapping[str, Any]], *, source: Any | None = None, target: Any | None = None) -> dict[str, Any]:
    """Verify receipt binding plus adjacent digest continuity for a declared chain.

    A valid result proves only that each receipt is structurally/self-digest valid,
    optional supplied endpoint values match the declared endpoint digests, and every
    receipt target digest equals the next receipt source digest. It does not prove
    that any transformer executed, that any semantic claim is true, or that the
    chain is preferable to a direct migration.
    """
    try:
        chain = list(receipts)
    except TypeError:
        chain = []
        failures = ["chain-not-iterable"]
    else:
        failures: list[str] = []

    if not chain:
        if "chain-not-iterable" not in failures:
            failures.append("empty-chain")
        return {
            "chain_valid": False,
            "failures": failures,
            "receipt_count": 0,
            "chain_scope": "receipt-binding-and-adjacent-digest-continuity",
            "authenticity_proven": False,
            "transform_execution_proven": False,
            "semantic_truth_proven": False,
            "direct_equivalence_proven": False,
        }

    for index, receipt in enumerate(chain):
        binding = verify_migration_receipt_binding(
            receipt,
            source=source if index == 0 and source is not None else None,
            target=target if index == len(chain) - 1 and target is not None else None,
        )
        for failure in binding["failures"]:
            failures.append(f"receipt-{index}:{failure}")

    for index, (left, right) in enumerate(zip(chain, chain[1:])):
        if not isinstance(left, Mapping) or not isinstance(right, Mapping):
            continue
        if left.get("target_digest") != right.get("source_digest"):
            failures.append(f"link-{index}-{index + 1}-digest-mismatch")

    return {
        "chain_valid": not failures,
        "failures": failures,
        "receipt_count": len(chain),
        "chain_scope": "receipt-binding-and-adjacent-digest-continuity",
        "authenticity_proven": False,
        "transform_execution_proven": False,
        "semantic_truth_proven": False,
        "direct_equivalence_proven": False,
    }
