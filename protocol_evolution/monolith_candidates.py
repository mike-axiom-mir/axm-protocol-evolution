from __future__ import annotations

import copy
import re
from typing import Any, Mapping

HEX40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

PROMOTION_FLAGS = (
    "generation_admitted",
    "migration_path_admitted",
    "migration_executed",
    "semantic_equivalence_proven",
    "chain_experiment_input_ready",
)


def _version_key(value: str) -> tuple[int, int, int] | None:
    match = SEMVER.fullmatch(value)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _error(errors: list[str], code: str, *parts: Any) -> None:
    errors.append(":".join([code, *[str(part) for part in parts]]))


def analyze_monolith_candidate_observations(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate read-only monolith candidate observations.

    This layer is intentionally discovery-only. It may show that a pinned package
    contains multiple version-labelled schema documents and adjacent migration
    contract documents, but it cannot admit generation fixtures, migration paths,
    execution, semantic equivalence, or chain readiness.
    """

    errors: list[str] = []
    if payload.get("schema") != "axm.protocol-evolution.monolith-candidate-observations/v0.1":
        _error(errors, "unsupported-schema", payload.get("schema"))

    observations = payload.get("observations")
    if not isinstance(observations, list) or not observations:
        _error(errors, "observations-missing")
        observations = []

    seen_observation_ids: set[str] = set()
    results: list[dict[str, Any]] = []

    for index, raw in enumerate(observations):
        if not isinstance(raw, Mapping):
            _error(errors, "observation-not-object", index)
            continue
        observation = copy.deepcopy(dict(raw))
        observation_id = observation.get("id")
        if not isinstance(observation_id, str) or not observation_id:
            _error(errors, "observation-id-missing", index)
            observation_id = f"index-{index}"
        elif observation_id in seen_observation_ids:
            _error(errors, "duplicate-observation-id", observation_id)
        seen_observation_ids.add(observation_id)

        archive = observation.get("archive")
        if not isinstance(archive, Mapping):
            _error(errors, "archive-missing", observation_id)
            archive = {}
        archive_sha = archive.get("sha256")
        if not isinstance(archive_sha, str) or not SHA256.fullmatch(archive_sha):
            _error(errors, "invalid-archive-sha256", observation_id)
        archive_bytes = archive.get("bytes")
        if not isinstance(archive_bytes, int) or archive_bytes <= 0:
            _error(errors, "invalid-archive-bytes", observation_id)

        source = observation.get("source_module")
        if not isinstance(source, Mapping):
            _error(errors, "source-module-missing", observation_id)
            source = {}
        repository = source.get("repository")
        commit = source.get("commit")
        if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository):
            _error(errors, "invalid-source-repository", observation_id)
        if not isinstance(commit, str) or not HEX40.fullmatch(commit):
            _error(errors, "invalid-source-commit", observation_id)

        candidate = observation.get("candidate_lineage")
        if not isinstance(candidate, Mapping):
            _error(errors, "candidate-lineage-missing", observation_id)
            candidate = {}
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str) or not candidate_id:
            _error(errors, "candidate-id-missing", observation_id)
            candidate_id = "unknown"
        if candidate.get("status") != "candidate_only":
            _error(errors, "candidate-status-not-read-only", observation_id, candidate_id)

        promotion = candidate.get("promotion_claims")
        if not isinstance(promotion, Mapping):
            _error(errors, "promotion-claims-missing", observation_id, candidate_id)
            promotion = {}
        for flag in PROMOTION_FLAGS:
            if promotion.get(flag) is not False:
                _error(errors, "forbidden-promotion-claim", observation_id, candidate_id, flag)

        versions = candidate.get("versions")
        if not isinstance(versions, list) or len(versions) < 2:
            _error(errors, "insufficient-candidate-versions", observation_id, candidate_id)
            versions = []

        seen_versions: set[str] = set()
        seen_schema_ids: set[str] = set()
        seen_paths: set[str] = set()
        ordered_versions: list[str] = []
        version_keys: list[tuple[int, int, int]] = []

        for vindex, version_record in enumerate(versions):
            if not isinstance(version_record, Mapping):
                _error(errors, "version-record-not-object", observation_id, candidate_id, vindex)
                continue
            version = version_record.get("version")
            schema_id = version_record.get("schema_id")
            archive_path = version_record.get("archive_path")
            entry_sha = version_record.get("archive_sha256")
            github_blob_sha = version_record.get("github_blob_sha")
            archive_git_blob_sha = version_record.get("archive_git_blob_sha")

            key = _version_key(version) if isinstance(version, str) else None
            if key is None:
                _error(errors, "invalid-version", observation_id, candidate_id, version)
                continue
            if version in seen_versions:
                _error(errors, "duplicate-version", observation_id, candidate_id, version)
            seen_versions.add(version)
            ordered_versions.append(version)
            version_keys.append(key)

            if not isinstance(schema_id, str) or not schema_id.endswith(f"/v{version}"):
                _error(errors, "schema-id-version-mismatch", observation_id, candidate_id, version)
            elif schema_id in seen_schema_ids:
                _error(errors, "duplicate-schema-id", observation_id, candidate_id, schema_id)
            seen_schema_ids.add(schema_id if isinstance(schema_id, str) else "")

            if not isinstance(archive_path, str) or not archive_path:
                _error(errors, "archive-path-missing", observation_id, candidate_id, version)
            elif archive_path in seen_paths:
                _error(errors, "duplicate-archive-path", observation_id, candidate_id, archive_path)
            seen_paths.add(archive_path if isinstance(archive_path, str) else "")

            if not isinstance(entry_sha, str) or not SHA256.fullmatch(entry_sha):
                _error(errors, "invalid-entry-sha256", observation_id, candidate_id, version)
            if not isinstance(github_blob_sha, str) or not HEX40.fullmatch(github_blob_sha):
                _error(errors, "invalid-github-blob-sha", observation_id, candidate_id, version)
            if archive_git_blob_sha != github_blob_sha:
                _error(errors, "archive-github-byte-identity-mismatch", observation_id, candidate_id, version)

        if version_keys and version_keys != sorted(version_keys):
            _error(errors, "versions-not-ordered", observation_id, candidate_id)

        transitions = candidate.get("adjacent_transition_contracts")
        if not isinstance(transitions, list):
            _error(errors, "transition-contracts-missing", observation_id, candidate_id)
            transitions = []
        expected_pairs = list(zip(ordered_versions, ordered_versions[1:]))
        if len(transitions) != len(expected_pairs):
            _error(errors, "transition-count-mismatch", observation_id, candidate_id, len(expected_pairs), len(transitions))

        seen_transition_pairs: set[tuple[str, str]] = set()
        for tindex, transition in enumerate(transitions):
            if not isinstance(transition, Mapping):
                _error(errors, "transition-not-object", observation_id, candidate_id, tindex)
                continue
            pair = (transition.get("source_version"), transition.get("target_version"))
            if pair in seen_transition_pairs:
                _error(errors, "duplicate-transition", observation_id, candidate_id, *pair)
            seen_transition_pairs.add(pair)
            if tindex < len(expected_pairs) and pair != expected_pairs[tindex]:
                _error(errors, "transition-order-mismatch", observation_id, candidate_id, *pair)
            if transition.get("claim") != "documented_transition_contract_only":
                _error(errors, "transition-claim-too-strong", observation_id, candidate_id, *pair)
            path = transition.get("archive_path")
            entry_sha = transition.get("archive_sha256")
            github_blob_sha = transition.get("github_blob_sha")
            archive_git_blob_sha = transition.get("archive_git_blob_sha")
            if not isinstance(path, str) or not path:
                _error(errors, "transition-path-missing", observation_id, candidate_id, *pair)
            if not isinstance(entry_sha, str) or not SHA256.fullmatch(entry_sha):
                _error(errors, "invalid-transition-sha256", observation_id, candidate_id, *pair)
            if not isinstance(github_blob_sha, str) or not HEX40.fullmatch(github_blob_sha):
                _error(errors, "invalid-transition-github-blob-sha", observation_id, candidate_id, *pair)
            if archive_git_blob_sha != github_blob_sha:
                _error(errors, "transition-archive-github-byte-identity-mismatch", observation_id, candidate_id, *pair)

        five_plus_candidate = len(ordered_versions) >= 5
        results.append(
            {
                "observation_id": observation_id,
                "candidate_id": candidate_id,
                "repository": repository,
                "commit": commit,
                "version_count": len(ordered_versions),
                "versions": ordered_versions,
                "adjacent_transition_contract_count": len(transitions),
                "five_plus_generation_candidate": five_plus_candidate,
                "generation_admission_claimed": False,
                "migration_path_admission_claimed": False,
                "migration_execution_claimed": False,
                "semantic_equivalence_claimed": False,
                "chain_experiment_input_ready": False,
            }
        )

    return {
        "schema": "axm.protocol-evolution.monolith-candidate-census/v0.1",
        "valid": not errors,
        "errors": errors,
        "observation_count": len(results),
        "five_plus_generation_candidate_count": sum(1 for result in results if result["five_plus_generation_candidate"]),
        "candidates": results,
        "truth_boundary": {
            "candidate_discovery_only": True,
            "archive_identity_recorded_not_reopened_by_ci": True,
            "connected_source_commit_resolution_recorded_not_live_rechecked_by_ci": True,
            "candidate_file_archive_git_blob_identity_recorded": True,
            "version_labels_do_not_admit_generation_fixtures": True,
            "migration_documents_do_not_admit_migration_paths": True,
            "no_migration_execution_proven": True,
            "no_semantic_equivalence_proven": True,
            "no_chain_experiment_readiness_granted": True,
            "adapter_translation_garden_ownership_unchanged": True,
        },
    }
