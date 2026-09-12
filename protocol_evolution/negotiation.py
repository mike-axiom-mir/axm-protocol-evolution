from __future__ import annotations

from typing import Iterable, Mapping
from .compatibility import CompatibilityState


def negotiate_capabilities(left: Mapping[str, str], right: Mapping[str, str], *, required: Iterable[str] = ()) -> dict:
    """Negotiate exact shared capability versions; infer nothing from product versions."""
    shared = {capability: left[capability] for capability in sorted(set(left) & set(right)) if left[capability] == right[capability]}
    missing = sorted(capability for capability in set(required) if capability not in shared)
    state = CompatibilityState.UNSUPPORTED if missing else CompatibilityState.SAME
    return {"state": state.value, "shared": shared, "missing_required": missing}
