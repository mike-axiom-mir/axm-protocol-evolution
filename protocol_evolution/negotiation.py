from __future__ import annotations

from typing import Iterable, Mapping
from .compatibility import CompatibilityState


_EVIDENCE_RANK = {
    "declared": 0,
    "executed": 1,
}


def _normalize_evidence(
    inventory: Mapping[str, str],
    evidence: Mapping[str, str] | None,
    *,
    side: str,
) -> dict[str, str]:
    normalized = {capability: "declared" for capability in inventory}
    if evidence is None:
        return normalized

    stale = sorted(set(evidence) - set(inventory))
    if stale:
        raise ValueError(f"{side}_evidence references absent capabilities: {stale}")

    for capability, level in evidence.items():
        if level not in _EVIDENCE_RANK:
            raise ValueError(f"unsupported {side} evidence level for {capability}: {level!r}")
        normalized[capability] = level
    return normalized


def negotiate_capabilities(
    left: Mapping[str, str],
    right: Mapping[str, str],
    *,
    required: Iterable[str] = (),
    left_complete: bool = True,
    right_complete: bool = True,
    left_evidence: Mapping[str, str] | None = None,
    right_evidence: Mapping[str, str] | None = None,
    minimum_evidence: str = "declared",
) -> dict:
    """Negotiate exact shared capability versions with explicit evidence strength.

    ``left_complete`` and ``right_complete`` describe the evidence boundary of the
    supplied inventories, not the underlying product. When a required capability is
    absent from an incomplete inventory, that absence is unobserved evidence rather
    than proof of incompatibility. Existing callers remain complete-by-default.

    Capability evidence is declaration-level by default, preserving existing caller
    behavior. A caller may explicitly require ``minimum_evidence="executed"`` and
    supply per-capability evidence levels. Exact id/version agreement below that
    requested threshold remains AMBIGUOUS rather than being promoted to SAME.
    """
    if minimum_evidence not in _EVIDENCE_RANK:
        raise ValueError(f"unsupported minimum evidence level: {minimum_evidence!r}")

    normalized_left_evidence = _normalize_evidence(left, left_evidence, side="left")
    normalized_right_evidence = _normalize_evidence(right, right_evidence, side="right")
    minimum_rank = _EVIDENCE_RANK[minimum_evidence]

    shared = {
        capability: left[capability]
        for capability in sorted(set(left) & set(right))
        if left[capability] == right[capability]
    }
    qualified_shared = {
        capability: version
        for capability, version in shared.items()
        if _EVIDENCE_RANK[normalized_left_evidence[capability]] >= minimum_rank
        and _EVIDENCE_RANK[normalized_right_evidence[capability]] >= minimum_rank
    }
    required_set = set(required)

    version_mismatches = sorted(
        capability
        for capability in required_set & set(left) & set(right)
        if left[capability] != right[capability]
    )
    missing_left = required_set - set(left)
    missing_right = required_set - set(right)

    unsupported = set(version_mismatches)
    if left_complete:
        unsupported.update(missing_left)
    if right_complete:
        unsupported.update(missing_right)

    unobserved = set()
    if not left_complete:
        unobserved.update(missing_left)
    if not right_complete:
        unobserved.update(missing_right)
    unobserved.difference_update(unsupported)

    evidence_shortfalls: dict[str, list[str]] = {}
    for capability in sorted(required_set & set(shared)):
        shortfall_sides: list[str] = []
        if _EVIDENCE_RANK[normalized_left_evidence[capability]] < minimum_rank:
            shortfall_sides.append("left")
        if _EVIDENCE_RANK[normalized_right_evidence[capability]] < minimum_rank:
            shortfall_sides.append("right")
        if shortfall_sides:
            evidence_shortfalls[capability] = shortfall_sides

    missing_required = sorted(unsupported)
    unobserved_required = sorted(unobserved)
    insufficient_evidence_required = sorted(evidence_shortfalls)

    if missing_required:
        state = CompatibilityState.UNSUPPORTED
    elif unobserved_required or insufficient_evidence_required:
        state = CompatibilityState.AMBIGUOUS
    else:
        state = CompatibilityState.SAME

    return {
        "state": state.value,
        "shared": shared,
        "qualified_shared": qualified_shared,
        "missing_required": missing_required,
        "unobserved_required": unobserved_required,
        "insufficient_evidence_required": insufficient_evidence_required,
        "evidence_shortfalls": evidence_shortfalls,
        "version_mismatches": version_mismatches,
        "minimum_evidence": minimum_evidence,
        "left_inventory_complete": left_complete,
        "right_inventory_complete": right_complete,
    }
