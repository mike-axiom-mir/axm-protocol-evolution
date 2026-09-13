from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .evidence_refs import FULL_SHA_RE, analyze_evidence_reference_integrity, inspect_pinned_github_reference

OBSERVATION_SCHEMA = "axm.protocol-evolution.evidence-reference-resolution-observations/v0.1"
RESULT_SCHEMA = "axm.protocol-evolution.evidence-reference-resolution/v0.1"


def _catalog_reference_expectations(
    path_catalog: Mapping[str, Any],
    investigation_catalog: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Collect structurally inspectable reference occurrences and unique expectations."""
    occurrences: list[dict[str, Any]] = []
    unique: dict[str, dict[str, Any]] = {}

    catalogs = (
        ("path", path_catalog, "paths"),
        ("investigation", investigation_catalog, "investigations"),
    )
    for record_type, catalog, key in catalogs:
        raw_records = catalog.get(key, []) if isinstance(catalog, Mapping) else []
        if not isinstance(raw_records, list):
            continue
        for record_index, raw in enumerate(raw_records):
            if not isinstance(raw, Mapping):
                continue
            record_id = raw.get("id")
            evidence_refs = raw.get("evidence_refs")
            if not isinstance(evidence_refs, list):
                continue
            for ref_index, ref in enumerate(evidence_refs):
                inspected = inspect_pinned_github_reference(ref)
                occurrences.append(
                    {
                        "record_type": record_type,
                        "record_id": record_id,
                        "record_index": record_index,
                        "ref_index": ref_index,
                        "inspection": inspected,
                    }
                )
                if inspected["valid"] and isinstance(ref, str):
                    unique.setdefault(ref, inspected)
    return occurrences, unique


def analyze_evidence_reference_resolution(
    path_catalog: Mapping[str, Any],
    investigation_catalog: Mapping[str, Any],
    observation_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind checked-in donor refs to explicit successful GitHub resolution observations.

    The observation snapshot is external evidence gathered before this offline
    analysis. This function never contacts GitHub. It verifies that every current
    catalog reference has exactly identified resolution evidence whose repository,
    reference kind, and commit identities match the pinned URL.

    A passing result proves only that the checked-in snapshot says each exact
    pinned resource was observed to resolve through the named method. It does not
    cryptographically attest that snapshot, re-run the network lookup, validate
    semantic relevance, authenticate authorship, or prove migration execution.
    """
    failures: list[str] = []

    structural = analyze_evidence_reference_integrity(path_catalog, investigation_catalog)
    if not structural["valid"]:
        failures.append("structural-reference-integrity-invalid")
        failures.extend(f"structural:{item}" for item in structural["failures"])

    occurrences, expected = _catalog_reference_expectations(path_catalog, investigation_catalog)

    observed_at: str | None = None
    method: str | None = None
    raw_observations: list[Any] = []
    if not isinstance(observation_snapshot, Mapping):
        failures.append("observation-snapshot-not-object")
    else:
        if observation_snapshot.get("schema") != OBSERVATION_SCHEMA:
            failures.append("unsupported-observation-snapshot-schema")
        observed_at_raw = observation_snapshot.get("observed_at")
        if not isinstance(observed_at_raw, str) or not observed_at_raw.strip():
            failures.append("invalid-observed-at")
        else:
            observed_at = observed_at_raw
        method_raw = observation_snapshot.get("method")
        if method_raw != "github-api-connected-read":
            failures.append(f"unsupported-observation-method:{method_raw}")
        else:
            method = method_raw
        raw_observations = observation_snapshot.get("observations", [])
        if not isinstance(raw_observations, list):
            failures.append("observations-not-list")
            raw_observations = []

    seen_refs: set[str] = set()
    observation_results: list[dict[str, Any]] = []
    resolved_observation_count = 0

    for index, raw in enumerate(raw_observations):
        if not isinstance(raw, Mapping):
            failures.append(f"observation-{index}:not-object")
            continue

        ref = raw.get("ref")
        if not isinstance(ref, str) or not ref:
            failures.append(f"observation-{index}:invalid-ref")
            continue
        if ref in seen_refs:
            failures.append(f"observation-{index}:duplicate-ref:{ref}")
            continue
        seen_refs.add(ref)

        expected_ref = expected.get(ref)
        if expected_ref is None:
            failures.append(f"observation-{index}:not-current-catalog-ref:{ref}")
            continue

        before = len(failures)
        if raw.get("resolved") is not True:
            failures.append(f"observation-{index}:not-resolved:{ref}")
        if raw.get("repository") != expected_ref["repository"]:
            failures.append(f"observation-{index}:repository-mismatch:{ref}")
        if raw.get("kind") != expected_ref["kind"]:
            failures.append(f"observation-{index}:kind-mismatch:{ref}")
        if raw.get("commit_refs") != expected_ref["commit_refs"]:
            failures.append(f"observation-{index}:commit-refs-mismatch:{ref}")

        kind = expected_ref["kind"]
        if kind == "commit":
            if raw.get("observed_commit_sha") != expected_ref["commit_refs"][0]:
                failures.append(f"observation-{index}:commit-sha-mismatch:{ref}")
        elif kind == "blob":
            blob_sha = raw.get("observed_blob_sha")
            if not isinstance(blob_sha, str) or not FULL_SHA_RE.fullmatch(blob_sha):
                failures.append(f"observation-{index}:invalid-observed-blob-sha:{ref}")
        elif kind == "compare":
            if raw.get("observed_base_sha") != expected_ref["commit_refs"][0]:
                failures.append(f"observation-{index}:compare-base-mismatch:{ref}")
            if raw.get("observed_head_sha") != expected_ref["commit_refs"][1]:
                failures.append(f"observation-{index}:compare-head-mismatch:{ref}")
            if raw.get("status") not in {"ahead", "behind", "identical", "diverged"}:
                failures.append(f"observation-{index}:invalid-compare-status:{ref}")
            for field in ("ahead_by", "behind_by", "total_commits"):
                value = raw.get(field)
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    failures.append(f"observation-{index}:invalid-{field}:{ref}")

        valid = len(failures) == before
        if valid:
            resolved_observation_count += 1
        observation_results.append(
            {
                "ref": ref,
                "valid": valid,
                "repository": expected_ref["repository"],
                "kind": kind,
                "commit_refs": list(expected_ref["commit_refs"]),
            }
        )

    missing_refs = [ref for ref in expected if ref not in seen_refs]
    for ref in missing_refs:
        failures.append(f"missing-resolution-observation:{ref}")

    all_observed = (
        bool(expected)
        and resolved_observation_count == len(expected)
        and not missing_refs
        and not failures
    )

    return {
        "schema": RESULT_SCHEMA,
        "valid": not failures,
        "failures": failures,
        "observed_at": observed_at,
        "method": method,
        "catalog_reference_occurrence_count": len(occurrences),
        "unique_catalog_reference_count": len(expected),
        "observation_count": len(observation_results),
        "resolved_observation_count": resolved_observation_count,
        "all_catalog_references_have_resolution_observations": all_observed,
        "observations": observation_results,
        "scope": "checked-in-migration-path-and-hold-donor-reference-resolution-observations",
        "live_resolution_reverified_by_analyzer": False,
        "observation_snapshot_cryptographically_attested": False,
        "reference_target_content_semantically_verified": False,
        "authorship_verified": False,
        "migration_execution_proven": False,
    }
