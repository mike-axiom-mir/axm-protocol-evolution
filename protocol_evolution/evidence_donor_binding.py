from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .evidence_refs import REPO_PART_RE, inspect_pinned_github_reference
from .evidence_resolution import analyze_evidence_reference_resolution

RESULT_SCHEMA = "axm.protocol-evolution.evidence-donor-binding/v0.1"


def _valid_repository_identity(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parts = value.split("/")
    return len(parts) == 2 and all(REPO_PART_RE.fullmatch(part) for part in parts)


def analyze_evidence_donor_binding(
    path_catalog: Mapping[str, Any],
    investigation_catalog: Mapping[str, Any],
    observation_snapshot: Mapping[str, Any],
    generation_manifests: list[Any],
) -> dict[str, Any]:
    """Bind edge evidence repositories to repositories declared by its generations.

    This is deliberately narrower than semantic validation. A full-SHA reference
    may resolve successfully and still be evidence from an unrelated repository.
    For this v0.1 contract, every path/HOLD evidence reference must come from one
    of the repositories declared by that record's source or target generation.

    Cross-repository edges remain possible: when source and target generations
    declare different repositories, evidence from either declared repository is
    accepted. Evidence from a third repository requires a future explicit schema
    rather than silent acceptance.
    """
    failures: list[str] = []

    resolution = analyze_evidence_reference_resolution(
        path_catalog, investigation_catalog, observation_snapshot
    )
    if not resolution["valid"]:
        failures.append("resolution-evidence-invalid")
        failures.extend(f"resolution:{item}" for item in resolution["failures"])

    generation_index: dict[str, Mapping[str, Any]] = {}
    declared_repositories: set[str] = set()
    if not isinstance(generation_manifests, list):
        failures.append("generation-manifests-not-list")
        generation_manifests = []

    for index, raw_manifest in enumerate(generation_manifests):
        if not isinstance(raw_manifest, Mapping):
            failures.append(f"generation-manifest-{index}:not-object")
            continue
        generation_id = raw_manifest.get("id")
        if not isinstance(generation_id, str) or not generation_id:
            failures.append(f"generation-manifest-{index}:invalid-id")
            continue
        if generation_id in generation_index:
            failures.append(f"generation-manifest-{index}:duplicate-id:{generation_id}")
            continue
        repository = raw_manifest.get("repository")
        if not _valid_repository_identity(repository):
            failures.append(f"generation-manifest-{generation_id}:invalid-repository:{repository}")
            continue
        generation_index[generation_id] = raw_manifest
        declared_repositories.add(repository)

    records: list[dict[str, Any]] = []
    reference_count = 0
    donor_bound_reference_count = 0

    catalogs = (
        ("path", path_catalog, "paths"),
        ("investigation", investigation_catalog, "investigations"),
    )
    for record_type, catalog, key in catalogs:
        raw_records = catalog.get(key, []) if isinstance(catalog, Mapping) else []
        if not isinstance(raw_records, list):
            failures.append(f"{record_type}-catalog:{key}-not-list")
            continue

        for index, raw_record in enumerate(raw_records):
            if not isinstance(raw_record, Mapping):
                failures.append(f"{record_type}-{index}:not-object")
                continue

            record_failures_before = len(failures)
            record_id = raw_record.get("id")
            if not isinstance(record_id, str) or not record_id:
                record_id = f"index-{index}"
                failures.append(f"{record_type}-{index}:invalid-id")

            source_generation = raw_record.get("source_generation")
            target_generation = raw_record.get("target_generation")
            allowed_repositories: set[str] = set()

            for role, generation_id in (
                ("source", source_generation),
                ("target", target_generation),
            ):
                if not isinstance(generation_id, str) or not generation_id:
                    failures.append(f"{record_type}-{record_id}:invalid-{role}-generation")
                    continue
                manifest = generation_index.get(generation_id)
                if manifest is None:
                    failures.append(
                        f"{record_type}-{record_id}:unknown-{role}-generation:{generation_id}"
                    )
                    continue
                repository = manifest.get("repository")
                if isinstance(repository, str):
                    allowed_repositories.add(repository)

            evidence_refs = raw_record.get("evidence_refs")
            if not isinstance(evidence_refs, list) or not evidence_refs:
                failures.append(f"{record_type}-{record_id}:missing-or-invalid-evidence-refs")
                evidence_refs = []

            record_bound_reference_count = 0
            evidence_repositories: set[str] = set()
            for ref_index, ref in enumerate(evidence_refs):
                reference_count += 1
                inspected = inspect_pinned_github_reference(ref)
                repository = inspected.get("repository")
                if isinstance(repository, str):
                    evidence_repositories.add(repository)

                if not inspected["valid"]:
                    failures.append(
                        f"{record_type}-{record_id}:evidence-ref-{ref_index}:"
                        f"not-structurally-inspectable:{inspected['reason']}"
                    )
                elif repository not in allowed_repositories:
                    failures.append(
                        f"{record_type}-{record_id}:evidence-ref-{ref_index}:"
                        f"repository-outside-declared-generations:{repository}"
                    )
                else:
                    donor_bound_reference_count += 1
                    record_bound_reference_count += 1

            records.append(
                {
                    "record_type": record_type,
                    "id": record_id,
                    "source_generation": source_generation,
                    "target_generation": target_generation,
                    "declared_generation_repositories": sorted(allowed_repositories),
                    "evidence_repositories": sorted(evidence_repositories),
                    "reference_count": len(evidence_refs),
                    "donor_bound_reference_count": record_bound_reference_count,
                    "valid": len(failures) == record_failures_before,
                }
            )

    all_bound = (
        reference_count > 0
        and donor_bound_reference_count == reference_count
        and not failures
    )

    return {
        "schema": RESULT_SCHEMA,
        "valid": not failures,
        "failures": failures,
        "generation_manifest_count": len(generation_manifests),
        "declared_generation_repository_count": len(declared_repositories),
        "declared_generation_repositories": sorted(declared_repositories),
        "record_count": len(records),
        "reference_count": reference_count,
        "donor_bound_reference_count": donor_bound_reference_count,
        "all_catalog_references_bound_to_declared_generation_repositories": all_bound,
        "records": records,
        "scope": "checked-in-migration-path-and-hold-evidence-repository-binding",
        "resolution_evidence_valid": resolution["valid"],
        "repository_binding_only": True,
        "reference_target_content_semantically_verified": False,
        "authorship_verified": False,
        "migration_execution_proven": False,
    }
