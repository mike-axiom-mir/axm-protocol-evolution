from __future__ import annotations

from typing import Any, Mapping

ROUTE_SCHEMA = "axm.protocol-evolution.historical-fixture-routes/v0.1"
ROUTE_RESULT_SCHEMA = "axm.protocol-evolution.historical-fixture-routes-evidence/v0.1"
BINDING_RESULT_SCHEMA = "axm.protocol-evolution.historical-fixture-generation-binding-evidence/v0.1"
PATH_HISTORY_RESULT_SCHEMA = "axm.protocol-evolution.artifact-path-history-evidence/v0.1"
RESULT_SCHEMA = "axm.protocol-evolution.historical-fixture-evidence-closure/v0.1"


def _err(errors: list[str], code: str, *parts: Any) -> None:
    errors.append(":".join([code, *[str(part) for part in parts]]))


def analyze_historical_fixture_evidence_closure(
    route_payload: Mapping[str, Any],
    route_result: Mapping[str, Any],
    binding_result: Mapping[str, Any],
    path_history_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Require exact historical routes to close across existing evidence layers.

    This composes already-bounded provenance, generation-binding, and path-history
    evidence. It does not admit generations or migration paths and deliberately
    excludes candidate-gap routes from historical closure.
    """
    errors: list[str] = []

    if route_payload.get("schema") != ROUTE_SCHEMA:
        _err(errors, "unsupported-route-schema", route_payload.get("schema"))
    if route_result.get("schema") != ROUTE_RESULT_SCHEMA:
        _err(errors, "unsupported-route-result-schema", route_result.get("schema"))
    if binding_result.get("schema") != BINDING_RESULT_SCHEMA:
        _err(errors, "unsupported-binding-result-schema", binding_result.get("schema"))
    if path_history_result.get("schema") != PATH_HISTORY_RESULT_SCHEMA:
        _err(errors, "unsupported-path-history-result-schema", path_history_result.get("schema"))

    if route_result.get("valid") is not True:
        _err(errors, "historical-fixture-route-evidence-invalid")
    if binding_result.get("valid") is not True:
        _err(errors, "historical-fixture-generation-binding-evidence-invalid")
    if path_history_result.get("valid") is not True:
        _err(errors, "artifact-path-history-evidence-invalid")

    raw_routes = route_payload.get("records")
    if not isinstance(raw_routes, list):
        _err(errors, "route-records-missing")
        raw_routes = []

    route_kinds: dict[str, str] = {}
    exact_route_ids: set[str] = set()
    for position, raw in enumerate(raw_routes):
        if not isinstance(raw, Mapping):
            _err(errors, "route-not-object", position)
            continue
        route_id = raw.get("id")
        kind = raw.get("kind")
        if not isinstance(route_id, str) or not route_id:
            _err(errors, "route-id-missing", position)
            continue
        if route_id in route_kinds:
            _err(errors, "duplicate-route-id", route_id)
            continue
        if not isinstance(kind, str) or not kind:
            _err(errors, "route-kind-missing", route_id)
            continue
        route_kinds[route_id] = kind
        if kind == "exact-historical-artifact":
            exact_route_ids.add(route_id)

    route_ready_ids: set[str] = set()
    seen_route_results: set[str] = set()
    raw_route_results = route_result.get("records")
    if not isinstance(raw_route_results, list):
        _err(errors, "route-evidence-records-missing")
        raw_route_results = []
    for position, raw in enumerate(raw_route_results):
        if not isinstance(raw, Mapping):
            _err(errors, "route-evidence-record-not-object", position)
            continue
        route_id = raw.get("id")
        if not isinstance(route_id, str) or not route_id:
            _err(errors, "route-evidence-id-missing", position)
            continue
        if route_id in seen_route_results:
            _err(errors, "duplicate-route-evidence-id", route_id)
        seen_route_results.add(route_id)
        kind = route_kinds.get(route_id)
        if kind is None:
            _err(errors, "route-evidence-unknown-route", route_id)
            continue
        if raw.get("independent_fixture_provenance_ready") is True:
            if kind != "exact-historical-artifact":
                _err(errors, "non-exact-route-provenance-ready", route_id, kind)
            else:
                route_ready_ids.add(route_id)

    bound_route_ids: set[str] = set()
    binding_by_route: dict[str, Mapping[str, Any]] = {}
    raw_bindings = binding_result.get("records")
    if not isinstance(raw_bindings, list):
        _err(errors, "binding-evidence-records-missing")
        raw_bindings = []
    for position, raw in enumerate(raw_bindings):
        if not isinstance(raw, Mapping):
            _err(errors, "binding-evidence-record-not-object", position)
            continue
        route_id = raw.get("route_id")
        if not isinstance(route_id, str) or not route_id:
            _err(errors, "binding-route-id-missing", position)
            continue
        kind = route_kinds.get(route_id)
        if kind is None:
            _err(errors, "binding-unknown-route", route_id)
            continue
        if raw.get("identity_tuple_matches") is True:
            if kind != "exact-historical-artifact":
                _err(errors, "non-exact-route-generation-bound", route_id, kind)
                continue
            if route_id in bound_route_ids:
                _err(errors, "duplicate-successful-generation-binding", route_id)
                continue
            bound_route_ids.add(route_id)
            binding_by_route[route_id] = raw

    history_supported_ids: set[str] = set()
    history_by_route: dict[str, Mapping[str, Any]] = {}
    raw_history = path_history_result.get("records")
    if not isinstance(raw_history, list):
        _err(errors, "path-history-evidence-records-missing")
        raw_history = []
    for position, raw in enumerate(raw_history):
        if not isinstance(raw, Mapping):
            _err(errors, "path-history-evidence-record-not-object", position)
            continue
        route_id = raw.get("route_id")
        if not isinstance(route_id, str) or not route_id:
            _err(errors, "path-history-route-id-missing", position)
            continue
        kind = route_kinds.get(route_id)
        if kind is None:
            _err(errors, "path-history-unknown-route", route_id)
            continue
        if raw.get("historical_observation_supported_by_path_history") is True:
            if kind != "exact-historical-artifact":
                _err(errors, "non-exact-route-history-supported", route_id, kind)
                continue
            if raw.get("artifact_kind") != "exact-historical-artifact":
                _err(errors, "supported-history-kind-mismatch", route_id, raw.get("artifact_kind"))
                continue
            if route_id in history_supported_ids:
                _err(errors, "duplicate-positive-path-history-support", route_id)
                continue
            history_supported_ids.add(route_id)
            history_by_route[route_id] = raw

    for route_id in sorted(exact_route_ids - route_ready_ids):
        _err(errors, "exact-route-not-provenance-ready", route_id)
    for route_id in sorted(exact_route_ids - bound_route_ids):
        _err(errors, "exact-route-missing-successful-generation-binding", route_id)
    for route_id in sorted(exact_route_ids - history_supported_ids):
        _err(errors, "exact-route-missing-positive-path-history-support", route_id)
    for route_id in sorted(route_ready_ids - exact_route_ids):
        _err(errors, "unexpected-provenance-ready-route", route_id)
    for route_id in sorted(bound_route_ids - exact_route_ids):
        _err(errors, "unexpected-generation-bound-route", route_id)
    for route_id in sorted(history_supported_ids - exact_route_ids):
        _err(errors, "unexpected-history-supported-route", route_id)

    records: list[dict[str, Any]] = []
    for route_id in sorted(exact_route_ids):
        binding = binding_by_route.get(route_id, {})
        history = history_by_route.get(route_id, {})
        closed = (
            route_id in route_ready_ids
            and route_id in bound_route_ids
            and route_id in history_supported_ids
        )
        records.append(
            {
                "route_id": route_id,
                "provenance_ready": route_id in route_ready_ids,
                "generation_binding_id": binding.get("id"),
                "generation_id": binding.get("generation_id"),
                "path_history_observation_id": history.get("id"),
                "path_history_supports_historical_observation": route_id in history_supported_ids,
                "closed": closed,
            }
        )

    closure_ready = (
        bool(exact_route_ids)
        and route_ready_ids == exact_route_ids
        and bound_route_ids == exact_route_ids
        and history_supported_ids == exact_route_ids
        and not errors
    )

    return {
        "schema": RESULT_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "exact_historical_route_count": len(exact_route_ids),
        "provenance_ready_exact_route_count": len(route_ready_ids & exact_route_ids),
        "generation_bound_exact_route_count": len(bound_route_ids & exact_route_ids),
        "history_supported_exact_route_count": len(history_supported_ids & exact_route_ids),
        "closed_exact_route_count": sum(1 for record in records if record["closed"]),
        "all_exact_historical_routes_closed_across_evidence_layers": closure_ready,
        "records": records,
        "truth_boundary": {
            "closure_proves_internal_evidence_coverage_only": True,
            "generation_admission_revalidated_or_granted": False,
            "migration_path_admission_granted": False,
            "migration_execution_proven": False,
            "semantic_equivalence_proven": False,
            "candidate_gap_promoted": False,
            "adapter_translation_garden_ownership_unchanged": True,
        },
    }
