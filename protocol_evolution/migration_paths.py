from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .lineage import analyze_generation_lineages


CATALOG_SCHEMA = "axm.protocol-evolution.migration-path-admissions/v0.1"
RESULT_SCHEMA = "axm.protocol-evolution.chain-experiment-readiness/v0.1"


def analyze_chain_experiment_readiness(
    manifests: Iterable[Mapping[str, Any]],
    lineage_catalog: Mapping[str, Any],
    path_catalog: Mapping[str, Any],
    *,
    target_length: int = 5,
) -> dict[str, Any]:
    """Report lineage-length and adjacent-path admission readiness.

    A path admission is only a reviewed evidence reference. This function does not
    generate adapters, execute migrations, independently verify evidence refs, or
    prove semantic/direct-migration equivalence.
    """
    lineage = analyze_generation_lineages(manifests, lineage_catalog, target_length=target_length)
    failures = list(lineage["failures"])

    if not isinstance(path_catalog, Mapping):
        failures.append("path-catalog-not-object")
        raw_paths: list[Any] = []
    else:
        if path_catalog.get("schema") != CATALOG_SCHEMA:
            failures.append("unsupported-path-catalog-schema")
        raw_paths = path_catalog.get("paths", [])
        if not isinstance(raw_paths, list):
            failures.append("paths-not-list")
            raw_paths = []

    lineages = {row["id"]: row for row in lineage["lineages"]}
    expected_by_lineage: dict[str, list[tuple[str, str]]] = {}
    expected_edges: set[tuple[str, str, str]] = set()
    for lineage_id, row in lineages.items():
        generations = row["generations"]
        edges = list(zip(generations, generations[1:]))
        expected_by_lineage[lineage_id] = edges
        expected_edges.update((lineage_id, source, target) for source, target in edges)

    seen_path_ids: set[str] = set()
    admitted_edges: dict[tuple[str, str, str], str] = {}
    admitted_paths: list[dict[str, Any]] = []

    for index, raw in enumerate(raw_paths):
        if not isinstance(raw, Mapping):
            failures.append(f"path-{index}:not-object")
            continue
        path_id = raw.get("id")
        lineage_id = raw.get("lineage_id")
        source = raw.get("source_generation")
        target = raw.get("target_generation")
        evidence_refs = raw.get("evidence_refs")

        if not isinstance(path_id, str) or not path_id:
            failures.append(f"path-{index}:invalid-id")
            continue
        if path_id in seen_path_ids:
            failures.append(f"path-{index}:duplicate-id:{path_id}")
            continue
        seen_path_ids.add(path_id)

        if not isinstance(lineage_id, str) or lineage_id not in lineages:
            failures.append(f"path-{path_id}:unknown-lineage:{lineage_id}")
            continue
        if not isinstance(source, str) or not source or not isinstance(target, str) or not target:
            failures.append(f"path-{path_id}:invalid-endpoints")
            continue
        edge = (lineage_id, source, target)
        if edge not in expected_edges:
            failures.append(f"path-{path_id}:not-declared-adjacent-edge:{source}:{target}")
            continue
        if (
            not isinstance(evidence_refs, list)
            or not evidence_refs
            or any(not isinstance(ref, str) or not ref for ref in evidence_refs)
        ):
            failures.append(f"path-{path_id}:missing-or-invalid-evidence-refs")
            continue
        if edge in admitted_edges:
            failures.append(
                f"duplicate-adjacent-path:{lineage_id}:{source}:{target}:{admitted_edges[edge]}:{path_id}"
            )
            continue

        admitted_edges[edge] = path_id
        admitted_paths.append(
            {
                "id": path_id,
                "lineage_id": lineage_id,
                "source_generation": source,
                "target_generation": target,
                "evidence_refs": list(evidence_refs),
            }
        )

    lineage_results: list[dict[str, Any]] = []
    input_ready_lineages: list[str] = []
    for lineage_id, row in lineages.items():
        required = expected_by_lineage[lineage_id]
        missing = [
            {"source_generation": source, "target_generation": target}
            for source, target in required
            if (lineage_id, source, target) not in admitted_edges
        ]
        admitted = [
            {
                "source_generation": source,
                "target_generation": target,
                "path_id": admitted_edges[(lineage_id, source, target)],
            }
            for source, target in required
            if (lineage_id, source, target) in admitted_edges
        ]
        length_ready = row["generation_count"] >= target_length
        paths_complete = bool(required) and not missing
        input_ready = length_ready and paths_complete
        if input_ready:
            input_ready_lineages.append(lineage_id)
        lineage_results.append(
            {
                "id": lineage_id,
                "domain": row["domain"],
                "generation_count": row["generation_count"],
                "target_length": target_length,
                "lineage_length_ready": length_ready,
                "required_adjacent_path_count": len(required),
                "admitted_adjacent_path_count": len(admitted),
                "adjacent_path_catalog_complete": paths_complete,
                "chain_experiment_input_ready": input_ready,
                "admitted_adjacent_paths": admitted,
                "missing_adjacent_paths": missing,
            }
        )

    return {
        "schema": RESULT_SCHEMA,
        "valid": not failures,
        "failures": failures,
        "target_length": target_length,
        "fixture_count": lineage["fixture_count"],
        "max_lineage_length": lineage["max_lineage_length"],
        "admitted_path_count": len(admitted_paths),
        "chain_experiment_input_ready": bool(input_ready_lineages) and not failures,
        "input_ready_lineages": input_ready_lineages,
        "lineages": lineage_results,
        "admitted_paths": admitted_paths,
        "scope": "declared-adjacent-migration-path-admissions-and-lineage-length-only",
        "evidence_references_independently_verified": False,
        "migration_execution_proven": False,
        "semantic_equivalence_proven": False,
        "direct_migration_equivalence_proven": False,
    }
