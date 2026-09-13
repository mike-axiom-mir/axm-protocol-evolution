from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any, Mapping

BINDING_SCHEMA = "axm.protocol-evolution.historical-fixture-generation-bindings/v0.1"
RESULT_SCHEMA = "axm.protocol-evolution.historical-fixture-generation-binding-evidence/v0.1"


def _err(errors: list[str], code: str, *parts: Any) -> None:
    errors.append(":".join([code, *[str(part) for part in parts]]))


def _valid_repo_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts


def analyze_historical_fixture_generation_bindings(
    binding_payload: Mapping[str, Any],
    route_payload: Mapping[str, Any],
    route_result: Mapping[str, Any],
    generation_records: list[Any],
) -> dict[str, Any]:
    """Bind exact historical fixture routes to existing generation manifests.

    This checks identity agreement only. It does not admit generations or migration
    paths and deliberately refuses to bind candidate-gap routes as if they were
    admitted historical generations.
    """
    errors: list[str] = []

    if binding_payload.get("schema") != BINDING_SCHEMA:
        _err(errors, "unsupported-binding-schema", binding_payload.get("schema"))
    if route_payload.get("schema") != "axm.protocol-evolution.historical-fixture-routes/v0.1":
        _err(errors, "unsupported-route-schema", route_payload.get("schema"))
    if not isinstance(route_result, Mapping) or route_result.get("valid") is not True:
        _err(errors, "historical-fixture-route-evidence-invalid")

    raw_routes = route_payload.get("records")
    if not isinstance(raw_routes, list):
        _err(errors, "route-records-missing")
        raw_routes = []

    route_index: dict[str, Mapping[str, Any]] = {}
    exact_route_ids: set[str] = set()
    for position, raw in enumerate(raw_routes):
        if not isinstance(raw, Mapping):
            _err(errors, "route-not-object", position)
            continue
        route_id = raw.get("id")
        if not isinstance(route_id, str) or not route_id:
            _err(errors, "route-id-missing", position)
            continue
        if route_id in route_index:
            _err(errors, "duplicate-route-id", route_id)
            continue
        route_index[route_id] = raw
        if raw.get("kind") == "exact-historical-artifact":
            exact_route_ids.add(route_id)

    route_result_index: dict[str, Mapping[str, Any]] = {}
    if isinstance(route_result, Mapping):
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
                _err(errors, "route-evidence-record-id-missing", position)
                continue
            if route_id in route_result_index:
                _err(errors, "duplicate-route-evidence-id", route_id)
                continue
            route_result_index[route_id] = raw

    generation_index: dict[str, dict[str, Any]] = {}
    if not isinstance(generation_records, list):
        _err(errors, "generation-records-not-list")
        generation_records = []
    for position, raw_record in enumerate(generation_records):
        if not isinstance(raw_record, Mapping):
            _err(errors, "generation-record-not-object", position)
            continue
        manifest_path = raw_record.get("manifest_path")
        manifest = raw_record.get("manifest")
        if not _valid_repo_relative_path(manifest_path) or not str(manifest_path).endswith("/manifest.json"):
            _err(errors, "invalid-generation-manifest-path", position, manifest_path)
            continue
        if not isinstance(manifest, Mapping):
            _err(errors, "generation-manifest-not-object", position)
            continue
        generation_id = manifest.get("id")
        if not isinstance(generation_id, str) or not generation_id:
            _err(errors, "generation-id-missing", position)
            continue
        if generation_id in generation_index:
            _err(errors, "duplicate-generation-id", generation_id)
            continue
        generation_index[generation_id] = {
            "manifest_path": manifest_path,
            "manifest": manifest,
        }

    raw_bindings = binding_payload.get("bindings")
    if not isinstance(raw_bindings, list):
        _err(errors, "bindings-missing")
        raw_bindings = []

    seen_binding_ids: set[str] = set()
    bound_route_ids: set[str] = set()
    records: list[dict[str, Any]] = []

    for position, raw in enumerate(raw_bindings):
        if not isinstance(raw, Mapping):
            _err(errors, "binding-not-object", position)
            continue

        binding_id = raw.get("id")
        if not isinstance(binding_id, str) or not binding_id:
            _err(errors, "binding-id-missing", position)
            binding_id = f"index-{position}"
        elif binding_id in seen_binding_ids:
            _err(errors, "duplicate-binding-id", binding_id)
        seen_binding_ids.add(binding_id)

        route_id = raw.get("route_id")
        generation_id = raw.get("generation_id")
        route = route_index.get(route_id) if isinstance(route_id, str) else None
        generation_record = generation_index.get(generation_id) if isinstance(generation_id, str) else None

        before = len(errors)
        if route is None:
            _err(errors, "unknown-route", binding_id, route_id)
        elif route.get("kind") != "exact-historical-artifact":
            _err(errors, "route-not-exact-historical-artifact", binding_id, route_id, route.get("kind"))

        if isinstance(route_id, str):
            if route_id in bound_route_ids:
                _err(errors, "route-bound-more-than-once", route_id)
            bound_route_ids.add(route_id)

        if generation_record is None:
            _err(errors, "unknown-generation", binding_id, generation_id)
            manifest = {}
            manifest_path = None
        else:
            manifest = generation_record["manifest"]
            manifest_path = generation_record["manifest_path"]

        route_evidence = route_result_index.get(route_id) if isinstance(route_id, str) else None
        if route is not None:
            if route_evidence is None:
                _err(errors, "route-evidence-missing", binding_id, route_id)
            elif route_evidence.get("independent_fixture_provenance_ready") is not True:
                _err(errors, "route-not-provenance-ready", binding_id, route_id)

        expected_fixture_path = None
        if generation_record is not None:
            artifact = manifest.get("artifact")
            if not isinstance(artifact, str) or not artifact or "/" in artifact or artifact in {".", ".."}:
                _err(errors, "invalid-generation-artifact", binding_id, artifact)
            else:
                expected_fixture_path = str(PurePosixPath(str(manifest_path)).parent / artifact)

        if route is not None and generation_record is not None:
            comparisons = (
                ("repository", route.get("repository"), manifest.get("repository")),
                ("commit", route.get("commit"), manifest.get("source_ref")),
                ("source-path", route.get("source_path"), manifest.get("source_path")),
                ("donor-blob", route.get("donor_blob_sha"), manifest.get("source_blob_sha")),
                ("fixture-path", route.get("fixture_path"), expected_fixture_path),
            )
            for label, route_value, manifest_value in comparisons:
                if route_value != manifest_value:
                    _err(errors, f"route-generation-{label}-mismatch", binding_id, route_value, manifest_value)

        records.append(
            {
                "id": binding_id,
                "route_id": route_id,
                "generation_id": generation_id,
                "expected_fixture_path": expected_fixture_path,
                "identity_tuple_matches": len(errors) == before,
            }
        )

    for route_id in sorted(exact_route_ids - bound_route_ids):
        _err(errors, "exact-route-missing-generation-binding", route_id)
    for route_id in sorted(bound_route_ids - exact_route_ids):
        if route_id in route_index:
            _err(errors, "non-exact-route-bound", route_id)

    all_bound = bool(exact_route_ids) and bound_route_ids == exact_route_ids and not errors

    return {
        "schema": RESULT_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "exact_historical_route_count": len(exact_route_ids),
        "binding_count": len(records),
        "bound_exact_historical_route_count": len(exact_route_ids & bound_route_ids),
        "all_exact_historical_routes_bound_to_generation_manifests": all_bound,
        "records": records,
        "truth_boundary": {
            "binding_proves_identity_agreement_only": True,
            "generation_admission_revalidated_or_granted": False,
            "migration_path_admission_granted": False,
            "migration_execution_proven": False,
            "semantic_equivalence_proven": False,
            "candidate_gap_bound_to_admitted_generation": False,
            "adapter_translation_garden_ownership_unchanged": True,
        },
    }
