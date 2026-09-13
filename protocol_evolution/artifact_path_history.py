from __future__ import annotations

import re
from typing import Any, Mapping

HEX40 = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_KINDS = {"exact-historical-artifact", "legacy-labelled-candidate-artifact"}


def _err(errors: list[str], code: str, *parts: Any) -> None:
    errors.append(":".join([code, *[str(part) for part in parts]]))


def _full_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX40.fullmatch(value))


def analyze_artifact_path_history(
    payload: Mapping[str, Any],
    historical_routes: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate bounded Git path-history observations against fixture provenance routes.

    This layer records only what was observed in accessible path-filtered Git history.  The
    oldest observed commit is not claimed to be the artifact's creation time, and a legacy
    label is not converted into a historical serialized fixture merely because Git preserves
    the labelled schema or migration documentation.
    """
    errors: list[str] = []
    if payload.get("schema") != "axm.protocol-evolution.artifact-path-history-observations/v0.1":
        _err(errors, "unsupported-schema", payload.get("schema"))
    if historical_routes.get("schema") != "axm.protocol-evolution.historical-fixture-routes/v0.1":
        _err(errors, "unsupported-routes-schema", historical_routes.get("schema"))

    route_records = historical_routes.get("records")
    if not isinstance(route_records, list):
        _err(errors, "route-records-missing")
        route_records = []
    route_index: dict[str, Mapping[str, Any]] = {}
    for i, raw in enumerate(route_records):
        if not isinstance(raw, Mapping):
            _err(errors, "route-not-object", i)
            continue
        rid = raw.get("id")
        if not isinstance(rid, str) or not rid:
            _err(errors, "route-id-missing", i)
            continue
        if rid in route_index:
            _err(errors, "duplicate-route-id", rid)
        route_index[rid] = raw

    records = payload.get("records")
    if not isinstance(records, list) or not records:
        _err(errors, "records-missing")
        records = []

    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    for i, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            _err(errors, "record-not-object", i)
            continue
        rid = raw.get("id")
        if not isinstance(rid, str) or not rid:
            _err(errors, "record-id-missing", i)
            rid = f"index-{i}"
        elif rid in seen:
            _err(errors, "duplicate-record-id", rid)
        seen.add(rid)

        route_id = raw.get("route_id")
        route = route_index.get(route_id) if isinstance(route_id, str) else None
        if route is None:
            _err(errors, "unknown-route", rid, route_id)
            route = {}

        kind = raw.get("artifact_kind")
        if kind not in ALLOWED_KINDS:
            _err(errors, "unknown-artifact-kind", rid, kind)

        repository = raw.get("repository")
        source_path = raw.get("source_path")
        expected_blob = raw.get("expected_blob_sha")
        if not isinstance(repository, str) or "/" not in repository:
            _err(errors, "invalid-repository", rid)
        if not isinstance(source_path, str) or not source_path or source_path.startswith("/") or ".." in source_path.split("/"):
            _err(errors, "invalid-source-path", rid, source_path)
        if not _full_sha(expected_blob):
            _err(errors, "invalid-expected-blob", rid, expected_blob)

        if route and route.get("repository") != repository:
            _err(errors, "route-repository-mismatch", rid, route.get("repository"), repository)

        observation = raw.get("path_history_observation")
        if not isinstance(observation, Mapping):
            _err(errors, "path-history-observation-missing", rid)
            observation = {}
        observed_commits = observation.get("observed_commits_newest_to_oldest")
        if not isinstance(observed_commits, list) or not observed_commits:
            _err(errors, "observed-commits-missing", rid)
            observed_commits = []
        elif len(set(observed_commits)) != len(observed_commits):
            _err(errors, "duplicate-observed-commit", rid)
        for commit in observed_commits:
            if not _full_sha(commit):
                _err(errors, "invalid-observed-commit", rid, commit)

        count = observation.get("bounded_result_count")
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            _err(errors, "invalid-bounded-result-count", rid, count)
        elif count != len(observed_commits):
            _err(errors, "bounded-result-count-mismatch", rid, count, len(observed_commits))

        oldest = observation.get("oldest_observed_commit")
        if not _full_sha(oldest):
            _err(errors, "invalid-oldest-observed-commit", rid, oldest)
        elif observed_commits and oldest != observed_commits[-1]:
            _err(errors, "oldest-observed-order-mismatch", rid, oldest, observed_commits[-1])

        observed_blob = observation.get("artifact_blob_sha_at_oldest_observed_commit")
        if not _full_sha(observed_blob):
            _err(errors, "invalid-observed-blob", rid, observed_blob)
        elif _full_sha(expected_blob) and observed_blob != expected_blob:
            _err(errors, "oldest-observed-blob-mismatch", rid, observed_blob, expected_blob)

        claimed_support = raw.get("historical_observation_supported_by_path_history")
        supports_history = False
        classification = "unresolved"

        if kind == "exact-historical-artifact":
            if route and route.get("kind") != "exact-historical-artifact":
                _err(errors, "route-kind-mismatch", rid, route.get("kind"), kind)
            declared = raw.get("declared_historical_commit")
            if not _full_sha(declared):
                _err(errors, "invalid-declared-historical-commit", rid, declared)
            if route and route.get("commit") != declared:
                _err(errors, "route-commit-mismatch", rid, route.get("commit"), declared)
            if route and route.get("source_path") != source_path:
                _err(errors, "route-source-path-mismatch", rid, route.get("source_path"), source_path)
            if route and route.get("donor_blob_sha") != expected_blob:
                _err(errors, "route-blob-mismatch", rid, route.get("donor_blob_sha"), expected_blob)
            route_ready = route.get("historical_value_observed") is True and route.get("independent_fixture_provenance_ready") is True
            supports_history = (
                route_ready
                and _full_sha(declared)
                and declared == oldest
                and observed_blob == expected_blob
                and bool(observed_commits)
            )
            classification = (
                "declared-historical-commit-is-oldest-observed-path-commit"
                if supports_history
                else "historical-route-not-aligned-with-bounded-path-history"
            )
        elif kind == "legacy-labelled-candidate-artifact":
            if route and route.get("kind") != "candidate-gap":
                _err(errors, "route-kind-mismatch", rid, route.get("kind"), kind)
            pinned = raw.get("pinned_candidate_commit")
            if not _full_sha(pinned):
                _err(errors, "invalid-pinned-candidate-commit", rid, pinned)
            if route and route.get("commit") != pinned:
                _err(errors, "route-commit-mismatch", rid, route.get("commit"), pinned)
            supports_history = False
            classification = "legacy-labelled-artifact-first-visible-only-in-bounded-cumulative-history"

        if claimed_support is not supports_history:
            _err(errors, "historical-support-claim-mismatch", rid, claimed_support, supports_history)

        results.append(
            {
                "id": rid,
                "route_id": route_id,
                "artifact_kind": kind,
                "oldest_observed_commit": oldest,
                "bounded_result_count": count,
                "classification": classification,
                "historical_observation_supported_by_path_history": supports_history,
            }
        )

    return {
        "schema": "axm.protocol-evolution.artifact-path-history-evidence/v0.1",
        "valid": not errors,
        "errors": errors,
        "record_count": len(results),
        "historical_support_count": sum(1 for result in results if result["historical_observation_supported_by_path_history"]),
        "records": results,
        "truth_boundary": {
            "oldest_observed_path_commit_is_not_claimed_creation_time": True,
            "legacy_version_label_is_not_historical_fixture_proof": True,
            "schema_or_document_history_is_not_serialized_state_history": True,
            "path_history_observation_is_not_generation_admission": True,
            "path_history_observation_is_not_migration_path_evidence": True,
            "path_history_observation_is_not_semantic_equivalence": True,
            "adapter_translation_garden_ownership_unchanged": True,
        },
    }
