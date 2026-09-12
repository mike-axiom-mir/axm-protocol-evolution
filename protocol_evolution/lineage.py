from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
from typing import Any


def analyze_generation_lineages(
    manifests: Iterable[Mapping[str, Any]],
    lineage_catalog: Mapping[str, Any],
    *,
    target_length: int = 5,
) -> dict[str, Any]:
    """Validate declared fixture lineages and report same-lineage chain readiness.

    This function deliberately distinguishes total fixture count from the length of
    any one declared semantic lineage. A corpus can contain five fixtures without
    containing one five-generation migration chain.
    """
    if isinstance(target_length, bool) or not isinstance(target_length, int) or target_length <= 0:
        raise ValueError("target_length must be a positive integer")

    manifest_rows = [dict(row) for row in manifests]
    failures: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}

    for index, row in enumerate(manifest_rows):
        fixture_id = row.get("id")
        domain = row.get("domain")
        if not isinstance(fixture_id, str) or not fixture_id:
            failures.append(f"manifest-{index}:invalid-id")
            continue
        if fixture_id in by_id:
            failures.append(f"manifest-{index}:duplicate-id:{fixture_id}")
            continue
        if not isinstance(domain, str) or not domain:
            failures.append(f"manifest-{index}:invalid-domain:{fixture_id}")
            continue
        by_id[fixture_id] = row

    if not isinstance(lineage_catalog, Mapping):
        failures.append("catalog-not-object")
        raw_lineages: list[Any] = []
        catalog_schema = None
    else:
        catalog_schema = lineage_catalog.get("schema")
        raw_lineages = lineage_catalog.get("lineages", [])
        if catalog_schema != "axm.protocol-evolution.generation-lineages/v0.1":
            failures.append("unsupported-catalog-schema")
        if not isinstance(raw_lineages, list):
            failures.append("lineages-not-list")
            raw_lineages = []

    seen_lineage_ids: set[str] = set()
    assigned: dict[str, str] = {}
    lineage_results: list[dict[str, Any]] = []

    for index, raw in enumerate(raw_lineages):
        if not isinstance(raw, Mapping):
            failures.append(f"lineage-{index}:not-object")
            continue
        row = deepcopy(dict(raw))
        lineage_id = row.get("id")
        domain = row.get("domain")
        generations = row.get("generations")

        if not isinstance(lineage_id, str) or not lineage_id:
            failures.append(f"lineage-{index}:invalid-id")
            continue
        if lineage_id in seen_lineage_ids:
            failures.append(f"lineage-{index}:duplicate-id:{lineage_id}")
            continue
        seen_lineage_ids.add(lineage_id)

        if not isinstance(domain, str) or not domain:
            failures.append(f"lineage-{lineage_id}:invalid-domain")
            continue
        if not isinstance(generations, list) or not generations:
            failures.append(f"lineage-{lineage_id}:empty-or-invalid-generations")
            continue
        if any(not isinstance(item, str) or not item for item in generations):
            failures.append(f"lineage-{lineage_id}:invalid-generation-id")
            continue
        if len(set(generations)) != len(generations):
            failures.append(f"lineage-{lineage_id}:duplicate-generation")

        admitted: list[str] = []
        for fixture_id in generations:
            manifest = by_id.get(fixture_id)
            if manifest is None:
                failures.append(f"lineage-{lineage_id}:unknown-generation:{fixture_id}")
                continue
            if manifest.get("domain") != domain:
                failures.append(
                    f"lineage-{lineage_id}:domain-mismatch:{fixture_id}:{manifest.get('domain')}"
                )
                continue
            owner = assigned.get(fixture_id)
            if owner is not None and owner != lineage_id:
                failures.append(f"generation-multiple-lineages:{fixture_id}:{owner}:{lineage_id}")
                continue
            assigned[fixture_id] = lineage_id
            admitted.append(fixture_id)

        lineage_results.append(
            {
                "id": lineage_id,
                "domain": domain,
                "generation_count": len(admitted),
                "generations": admitted,
                "target_length": target_length,
                "target_gap": max(0, target_length - len(admitted)),
                "chain_ready": len(admitted) >= target_length,
            }
        )

    unassigned = sorted(set(by_id) - set(assigned))
    for fixture_id in unassigned:
        failures.append(f"unassigned-generation:{fixture_id}")

    max_lineage_length = max((row["generation_count"] for row in lineage_results), default=0)
    ready_lineages = [row["id"] for row in lineage_results if row["chain_ready"]]

    return {
        "schema": "axm.protocol-evolution.lineage-readiness/v0.1",
        "valid": not failures,
        "failures": failures,
        "fixture_count": len(by_id),
        "lineage_count": len(lineage_results),
        "target_length": target_length,
        "max_lineage_length": max_lineage_length,
        "five_fixture_corpus_is_not_five_generation_chain": len(by_id) >= target_length and max_lineage_length < target_length,
        "chain_ready": bool(ready_lineages) and not failures,
        "ready_lineages": ready_lineages,
        "lineages": lineage_results,
        "unassigned_generations": unassigned,
        "scope": "declared-fixture-lineage-membership-and-count-only",
        "contiguous_release_history_proven": False,
        "migration_paths_proven": False,
        "semantic_equivalence_proven": False,
    }
