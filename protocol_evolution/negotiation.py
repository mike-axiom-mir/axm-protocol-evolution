from __future__ import annotations

from typing import Iterable, Mapping
from .compatibility import CompatibilityState


def negotiate_capabilities(
    left: Mapping[str, str],
    right: Mapping[str, str],
    *,
    required: Iterable[str] = (),
    left_complete: bool = True,
    right_complete: bool = True,
) -> dict:
    """Negotiate exact shared capability versions without inferring from product versions.

    ``left_complete`` and ``right_complete`` describe the evidence boundary of the
    supplied inventories, not the underlying product. When a required capability is
    absent from an incomplete inventory, that absence is unobserved evidence rather
    than proof of incompatibility. Existing callers remain complete-by-default.
    """
    shared = {
        capability: left[capability]
        for capability in sorted(set(left) & set(right))
        if left[capability] == right[capability]
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

    missing_required = sorted(unsupported)
    unobserved_required = sorted(unobserved)

    if missing_required:
        state = CompatibilityState.UNSUPPORTED
    elif unobserved_required:
        state = CompatibilityState.AMBIGUOUS
    else:
        state = CompatibilityState.SAME

    return {
        "state": state.value,
        "shared": shared,
        "missing_required": missing_required,
        "unobserved_required": unobserved_required,
        "version_mismatches": version_mismatches,
        "left_inventory_complete": left_complete,
        "right_inventory_complete": right_complete,
    }
