from __future__ import annotations

import re
from typing import Any, Mapping

HEX40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
PROMOTION_FLAGS = ("source_generation_admitted", "target_generation_admitted", "migration_path_admitted")
REQUIRED_EVIDENCE_ROLES = {
    "transition-contract",
    "synthetic-regression-test",
    "migration-implementation",
    "current-schema-declaration",
    "donor-recorded-test-output",
    "declared-history-archive",
}


def _err(errors: list[str], code: str, *parts: Any) -> None:
    errors.append(":".join([code, *[str(part) for part in parts]]))


def _candidate_index(candidate_payload: Mapping[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for obs in candidate_payload.get("observations", []):
        if not isinstance(obs, Mapping):
            continue
        candidate = obs.get("candidate_lineage")
        source = obs.get("source_module")
        if not isinstance(candidate, Mapping) or not isinstance(source, Mapping):
            continue
        versions = candidate.get("versions", [])
        version_map = {v.get("version"): v for v in versions if isinstance(v, Mapping)}
        transitions = candidate.get("adjacent_transition_contracts", [])
        for transition in transitions:
            if not isinstance(transition, Mapping):
                continue
            s, t = transition.get("source_version"), transition.get("target_version")
            if s in version_map and t in version_map:
                index[(obs.get("id"), f"{s}->{t}")] = {
                    "candidate_id": candidate.get("id"),
                    "repository": source.get("repository"),
                    "commit": source.get("commit"),
                    "source": version_map[s],
                    "target": version_map[t],
                    "transition": transition,
                }
    return index


def analyze_candidate_promotion_assessments(
    payload: Mapping[str, Any], candidate_payload: Mapping[str, Any]
) -> dict[str, Any]:
    """Audit whether candidate evidence is strong enough for fixture/path promotion.

    This layer is fail-closed: execution of a synthetic legacy-shaped regression is useful
    evidence, but is not a historical generation fixture and is not an exact adjacent
    migration when the observed migrator emits a later/current schema.
    """
    errors: list[str] = []
    if payload.get("schema") != "axm.protocol-evolution.candidate-promotion-assessments/v0.1":
        _err(errors, "unsupported-schema", payload.get("schema"))

    known = _candidate_index(candidate_payload)
    assessments = payload.get("assessments")
    if not isinstance(assessments, list) or not assessments:
        _err(errors, "assessments-missing")
        assessments = []

    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    for i, raw in enumerate(assessments):
        if not isinstance(raw, Mapping):
            _err(errors, "assessment-not-object", i)
            continue
        aid = raw.get("id")
        if not isinstance(aid, str) or not aid:
            _err(errors, "assessment-id-missing", i)
            aid = f"index-{i}"
        elif aid in seen:
            _err(errors, "duplicate-assessment-id", aid)
        seen.add(aid)

        if raw.get("status") != "HOLD":
            _err(errors, "status-must-hold", aid, raw.get("status"))

        ref = raw.get("candidate_ref")
        if not isinstance(ref, Mapping):
            _err(errors, "candidate-ref-missing", aid)
            ref = {}
        observation_id = ref.get("observation_id")
        source_version = ref.get("source_version")
        target_version = ref.get("target_version")
        key = (observation_id, f"{source_version}->{target_version}")
        expected = known.get(key)
        if expected is None:
            _err(errors, "unknown-candidate-edge", aid, observation_id, source_version, target_version)
            expected = {}
        elif ref.get("candidate_id") != expected.get("candidate_id"):
            _err(errors, "candidate-id-mismatch", aid)

        repository = expected.get("repository")
        commit = expected.get("commit")
        expected_target_schema = expected.get("target", {}).get("schema_id") if isinstance(expected.get("target"), Mapping) else None

        evidence = raw.get("evidence")
        if not isinstance(evidence, list):
            _err(errors, "evidence-missing", aid)
            evidence = []
        roles: set[str] = set()
        for item in evidence:
            if not isinstance(item, Mapping):
                _err(errors, "evidence-not-object", aid)
                continue
            role = item.get("role")
            if not isinstance(role, str):
                _err(errors, "evidence-role-missing", aid)
                continue
            if role in roles:
                _err(errors, "duplicate-evidence-role", aid, role)
            roles.add(role)
            if item.get("repository") != repository or item.get("commit") != commit:
                _err(errors, "evidence-donor-mismatch", aid, role)
            blob = item.get("github_blob_sha")
            archive_blob = item.get("archive_git_blob_sha")
            if not isinstance(blob, str) or not HEX40.fullmatch(blob):
                _err(errors, "invalid-evidence-blob", aid, role)
            if archive_blob != blob:
                _err(errors, "archive-github-byte-identity-mismatch", aid, role)
            archive_sha = item.get("archive_sha256")
            if not isinstance(archive_sha, str) or not SHA256.fullmatch(archive_sha):
                _err(errors, "invalid-evidence-sha256", aid, role)
        missing_roles = sorted(REQUIRED_EVIDENCE_ROLES - roles)
        for role in missing_roles:
            _err(errors, "missing-evidence-role", aid, role)

        source_fixture = raw.get("source_fixture")
        if not isinstance(source_fixture, Mapping):
            _err(errors, "source-fixture-missing", aid)
            source_fixture = {}
        fixture_kind = source_fixture.get("kind")
        historical_source = source_fixture.get("historical_value_observed") is True
        if fixture_kind == "retro_synthesized_legacy_shape" and historical_source:
            _err(errors, "synthetic-fixture-cannot-be-historical", aid)
        if fixture_kind not in {"retro_synthesized_legacy_shape", "historical_value"}:
            _err(errors, "unknown-source-fixture-kind", aid, fixture_kind)

        execution = raw.get("execution_observation")
        if not isinstance(execution, Mapping):
            _err(errors, "execution-observation-missing", aid)
            execution = {}
        execution_passed = (
            execution.get("exit_code") == 0
            and execution.get("named_regression_passed") is True
            and isinstance(execution.get("suite_passed"), int)
            and execution.get("suite_passed") == execution.get("suite_total")
            and execution.get("suite_passed", 0) > 0
        )
        observed_target_schema = execution.get("observed_target_schema")
        exact_adjacent_target = execution.get("exact_adjacent_target_observed") is True
        if exact_adjacent_target and observed_target_schema != expected_target_schema:
            _err(errors, "exact-target-claim-mismatch", aid, observed_target_schema, expected_target_schema)

        history = raw.get("history_archive")
        if not isinstance(history, Mapping):
            _err(errors, "history-archive-missing", aid)
            history = {}
        history_sha = history.get("declared_sha256")
        if not isinstance(history_sha, str) or not SHA256.fullmatch(history_sha):
            _err(errors, "invalid-history-archive-sha256", aid)
        history_available = history.get("available_for_inspection") is True
        copied = history.get("copied_into_donor_repository") is True

        promotion = raw.get("promotion_claims")
        if not isinstance(promotion, Mapping):
            _err(errors, "promotion-claims-missing", aid)
            promotion = {}
        for flag in PROMOTION_FLAGS:
            if promotion.get(flag) is not False:
                _err(errors, "forbidden-promotion-claim", aid, flag)

        generation_ready = historical_source and history_available
        path_ready = generation_ready and execution_passed and exact_adjacent_target
        if raw.get("generation_admission_ready") is not generation_ready:
            _err(errors, "generation-readiness-mismatch", aid)
        if raw.get("migration_path_admission_ready") is not path_ready:
            _err(errors, "path-readiness-mismatch", aid)

        blockers = raw.get("blockers")
        if not isinstance(blockers, list) or not blockers:
            _err(errors, "blockers-missing", aid)
            blockers = []

        results.append({
            "assessment_id": aid,
            "candidate_id": ref.get("candidate_id"),
            "edge": f"{source_version}->{target_version}",
            "status": "HOLD",
            "synthetic_regression_fixture_observed": fixture_kind == "retro_synthesized_legacy_shape",
            "historical_source_fixture_observed": historical_source,
            "donor_regression_executed_this_cycle": execution_passed,
            "observed_target_schema": observed_target_schema,
            "expected_adjacent_target_schema": expected_target_schema,
            "exact_adjacent_target_output_observed": exact_adjacent_target,
            "declared_history_archive_available_for_inspection": history_available,
            "declared_history_archive_copied_into_donor_repository": copied,
            "generation_admission_ready": generation_ready,
            "migration_path_admission_ready": path_ready,
            "blockers": blockers,
        })

    return {
        "schema": "axm.protocol-evolution.candidate-promotion-readiness/v0.1",
        "valid": not errors,
        "errors": errors,
        "assessment_count": len(results),
        "ready_generation_count": sum(1 for r in results if r["generation_admission_ready"]),
        "ready_migration_path_count": sum(1 for r in results if r["migration_path_admission_ready"]),
        "assessments": results,
        "truth_boundary": {
            "synthetic_legacy_shape_is_not_historical_fixture": True,
            "passing_current_migrator_regression_is_not_exact_adjacent_migration": True,
            "declared_but_unavailable_history_archive_is_not_inspected_history": True,
            "execution_observation_recorded_not_replayed_by_offline_ci": True,
            "no_generation_or_path_promotion_granted": True,
            "adapter_translation_garden_ownership_unchanged": True,
        },
    }
