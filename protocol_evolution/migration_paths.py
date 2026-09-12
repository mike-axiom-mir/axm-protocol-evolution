from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .lineage import analyze_generation_lineages


CATALOG_SCHEMA = "axm.protocol-evolution.migration-path-admissions/v0.1"
INVESTIGATION_SCHEMA = "axm.protocol-evolution.migration-path-investigations/v0.1"
RESULT_SCHEMA = "axm.protocol-evolution.chain-experiment-readiness/v0.2"


def _valid_evidence_refs(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(ref, str) and bool(ref) for ref in value)
    )


def analyze_chain_experiment_readiness(
    manifests: Iterable[Mapping[str, Any]],
    lineage_catalog: Mapping[str, Any],
    path_catalog: Mapping[str, Any],
    investigation_catalog: Mapping[str, Any] | None = None,
    *,
    target_length: int = 5,
) -> dict[str, Any]:
    """Report lineage-length and adjacent-path admission readiness.

    Path admissions count toward readiness. Investigation records are negative or
    incomplete evidence only: they explain why an edge remains missing and never
    become migration-path admissions by themselves.

    This function does not generate adapters, execute migrations, independently
    verify evidence refs, or prove semantic/direct-migration equivalence.
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

    if investigation_catalog is None:
        raw_investigations: list[Any] = []
    elif not isinstance(investigation_catalog, Mapping):
        failures.append("investigation-catalog-not-object")
        raw_investigations = []
    else:
        if investigation_catalog.get("schema") != INVESTIGATION_SCHEMA:
            failures.append("unsupported-investigation-catalog-schema")
        raw_investigations = investigation_catalog.get("investigations", [])
        if not isinstance(raw_investigations, list):
            failures.append("investigations-not-list")
            raw_investigations = []

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
        if not _valid_evidence_refs(evidence_refs):
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

    seen_investigation_ids: set[str] = set()
    investigated_edges: dict[tuple[str, str, str], dict[str, Any]] = {}
    investigations: list[dict[str, Any]] = []

    for index, raw in enumerate(raw_investigations):
        if not isinstance(raw, Mapping):
            failures.append(f"investigation-{index}:not-object")
            continue
        investigation_id = raw.get("id")
        lineage_id = raw.get("lineage_id")
        source = raw.get("source_generation")
        target = raw.get("target_generation")
        status = raw.get("status")
        evidence_refs = raw.get("evidence_refs")
        finding = raw.get("finding")
        blocker = raw.get("blocker")

        if not isinstance(investigation_id, str) or not investigation_id:
            failures.append(f"investigation-{index}:invalid-id")
            continue
        if investigation_id in seen_investigation_ids:
            failures.append(f"investigation-{index}:duplicate-id:{investigation_id}")
            continue
        seen_investigation_ids.add(investigation_id)

        if not isinstance(lineage_id, str) or lineage_id not in lineages:
            failures.append(f"investigation-{investigation_id}:unknown-lineage:{lineage_id}")
            continue
        if not isinstance(source, str) or not source or not isinstance(target, str) or not target:
            failures.append(f"investigation-{investigation_id}:invalid-endpoints")
            continue
        edge = (lineage_id, source, target)
        if edge not in expected_edges:
            failures.append(
                f"investigation-{investigation_id}:not-declared-adjacent-edge:{source}:{target}"
            )
            continue
        if status != "HOLD":
            failures.append(f"investigation-{investigation_id}:unsupported-status:{status}")
            continue
        if not _valid_evidence_refs(evidence_refs):
            failures.append(f"investigation-{investigation_id}:missing-or-invalid-evidence-refs")
            continue
        if not isinstance(finding, str) or not finding.strip():
            failures.append(f"investigation-{investigation_id}:missing-finding")
            continue
        if not isinstance(blocker, str) or not blocker.strip():
            failures.append(f"investigation-{investigation_id}:missing-blocker")
            continue
        if edge in investigated_edges:
            failures.append(
                f"duplicate-adjacent-investigation:{lineage_id}:{source}:{target}:"
                f"{investigated_edges[edge]['id']}:{investigation_id}"
            )
            continue

        row = {
            "id": investigation_id,
            "lineage_id": lineage_id,
            "source_generation": source,
            "target_generation": target,
            "status": status,
            "evidence_refs": list(evidence_refs),
            "finding": finding,
            "blocker": blocker,
        }
        investigated_edges[edge] = row
        investigations.append(row)

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
        investigated_missing = [
            {
                "source_generation": source,
                "target_generation": target,
                "investigation_id": investigated_edges[(lineage_id, source, target)]["id"],
                "status": investigated_edges[(lineage_id, source, target)]["status"],
                "blocker": investigated_edges[(lineage_id, source, target)]["blocker"],
            }
            for source, target in required
            if (lineage_id, source, target) not in admitted_edges
            and (lineage_id, source, target) in investigated_edges
        ]
        uninvestigated_missing = [
            {"source_generation": source, "target_generation": target}
            for source, target in required
            if (lineage_id, source, target) not in admitted_edges
            and (lineage_id, source, target) not in investigated_edges
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
                "investigated_missing_path_count": len(investigated_missing),
                "uninvestigated_missing_path_count": len(uninvestigated_missing),
                "adjacent_path_catalog_complete": paths_complete,
                "chain_experiment_input_ready": input_ready,
                "admitted_adjacent_paths": admitted,
                "investigated_missing_paths": investigated_missing,
                "uninvestigated_missing_paths": uninvestigated_missing,
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
        "investigation_count": len(investigations),
        "chain_experiment_input_ready": bool(input_ready_lineages) and not failures,
        "input_ready_lineages": input_ready_lineages,
        "lineages": lineage_results,
        "admitted_paths": admitted_paths,
        "investigations": investigations,
        "scope": "declared-adjacent-path-admissions-plus-non-admitting-investigation-records",
        "investigations_count_as_admissions": False,
        "evidence_references_independently_verified": False,
        "migration_execution_proven": False,
        "semantic_equivalence_proven": False,
        "direct_migration_equivalence_proven": False,
    }
