from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _canonical_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value)).hexdigest()


def _raw_sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _safe_path(root: Path, relative: str) -> Path | None:
    if not isinstance(relative, str) or not relative.strip():
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _generation_manifests(root: Path) -> dict[str, tuple[dict[str, Any], Path]]:
    result: dict[str, tuple[dict[str, Any], Path]] = {}
    for manifest_path in sorted((root / "fixtures" / "generations").glob("*/manifest.json")):
        manifest = _load_json(manifest_path)
        generation_id = manifest.get("id")
        if isinstance(generation_id, str):
            result[generation_id] = (manifest, manifest_path)
    return result


def _artifact_path(manifest: dict[str, Any], manifest_path: Path) -> Path:
    return manifest_path.parent / str(manifest.get("artifact", ""))


def analyze_path_execution_observations(payload: dict[str, Any], root: Path) -> dict[str, Any]:
    failures: list[str] = []
    observations = payload.get("observations", []) if isinstance(payload, dict) else []
    if not isinstance(observations, list):
        observations = []
        failures.append("observations-not-list")

    migration_payload = _load_json(root / "fixtures" / "migration_paths.json")
    admitted = {row.get("id"): row for row in migration_payload.get("paths", []) if isinstance(row, dict)}
    manifests = _generation_manifests(root)

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    records: list[dict[str, Any]] = []

    for index, observation in enumerate(observations):
        prefix = f"observation[{index}]"
        if not isinstance(observation, dict):
            failures.append(f"{prefix}:not-object")
            continue
        observation_id = observation.get("id")
        path_id = observation.get("path_id")
        if not isinstance(observation_id, str) or not observation_id:
            failures.append(f"{prefix}:missing-id")
            continue
        if observation_id in seen_ids:
            failures.append(f"{prefix}:duplicate-id:{observation_id}")
        seen_ids.add(observation_id)
        if not isinstance(path_id, str) or path_id not in admitted:
            failures.append(f"{prefix}:unknown-admitted-path:{path_id}")
            continue
        if path_id in seen_paths:
            failures.append(f"{prefix}:duplicate-path-observation:{path_id}")
        seen_paths.add(path_id)

        path = admitted[path_id]
        for field in ("lineage_id", "source_generation", "target_generation"):
            if observation.get(field) != path.get(field):
                failures.append(f"{prefix}:path-{field}-mismatch")

        source_id = path.get("source_generation")
        target_id = path.get("target_generation")
        source_pair = manifests.get(source_id)
        target_pair = manifests.get(target_id)
        if source_pair is None or target_pair is None:
            failures.append(f"{prefix}:unknown-generation-binding")
            continue
        source_manifest, source_manifest_path = source_pair
        target_manifest, target_manifest_path = target_pair

        donor_repo = observation.get("donor_repository")
        donor_commit = observation.get("donor_commit")
        if donor_repo != source_manifest.get("repository") or donor_repo != target_manifest.get("repository"):
            failures.append(f"{prefix}:donor-repository-mismatch")
        if not isinstance(donor_commit, str) or not _FULL_SHA.fullmatch(donor_commit):
            failures.append(f"{prefix}:weak-donor-commit")
        if donor_commit != source_manifest.get("source_ref") or donor_commit != target_manifest.get("source_ref"):
            failures.append(f"{prefix}:donor-commit-not-generation-ref")

        donor_files = observation.get("donor_files")
        if not isinstance(donor_files, list) or not donor_files:
            failures.append(f"{prefix}:missing-donor-files")
        else:
            donor_paths: set[str] = set()
            for donor_index, donor_file in enumerate(donor_files):
                if not isinstance(donor_file, dict):
                    failures.append(f"{prefix}:donor-file[{donor_index}]-not-object")
                    continue
                donor_path = donor_file.get("path")
                donor_blob = donor_file.get("git_blob")
                if not isinstance(donor_path, str) or not donor_path or donor_path in donor_paths:
                    failures.append(f"{prefix}:invalid-or-duplicate-donor-path")
                donor_paths.add(str(donor_path))
                if not isinstance(donor_blob, str) or not _FULL_SHA.fullmatch(donor_blob):
                    failures.append(f"{prefix}:weak-donor-file-blob:{donor_path}")

        source_path = _artifact_path(source_manifest, source_manifest_path)
        declared_source_path = _safe_path(root, str(observation.get("source_fixture_path", "")))
        if declared_source_path is None or declared_source_path != source_path.resolve():
            failures.append(f"{prefix}:source-fixture-path-mismatch")
        elif not source_path.exists():
            failures.append(f"{prefix}:source-fixture-missing")
        else:
            source_bytes = source_path.read_bytes()
            source_value = json.loads(source_bytes)
            if observation.get("source_fixture_git_blob") != _git_blob(source_bytes):
                failures.append(f"{prefix}:source-git-blob-mismatch")
            if observation.get("source_fixture_sha256") != _raw_sha256(source_bytes):
                failures.append(f"{prefix}:source-sha256-mismatch")
            if observation.get("source_canonical_digest") != _canonical_digest(source_value):
                failures.append(f"{prefix}:source-canonical-digest-mismatch")

        output_path = _safe_path(root, str(observation.get("observed_output_path", "")))
        output_value: dict[str, Any] | None = None
        if output_path is None or not output_path.exists():
            failures.append(f"{prefix}:observed-output-missing-or-unsafe")
        else:
            output_bytes = output_path.read_bytes()
            try:
                loaded_output = json.loads(output_bytes)
                output_value = loaded_output if isinstance(loaded_output, dict) else None
            except json.JSONDecodeError:
                output_value = None
            if output_value is None:
                failures.append(f"{prefix}:observed-output-not-object")
            else:
                if observation.get("observed_output_sha256") != _raw_sha256(output_bytes):
                    failures.append(f"{prefix}:output-sha256-mismatch")
                if observation.get("observed_output_canonical_digest") != _canonical_digest(output_value):
                    failures.append(f"{prefix}:output-canonical-digest-mismatch")

        target_fixture = _artifact_path(target_manifest, target_manifest_path)
        control_input_path = _safe_path(root, str(observation.get("control_input_path", "")))
        if control_input_path is None or control_input_path != target_fixture.resolve() or not target_fixture.exists():
            failures.append(f"{prefix}:control-input-path-mismatch")
        else:
            control_input_bytes = target_fixture.read_bytes()
            control_input_value = json.loads(control_input_bytes)
            if observation.get("control_input_git_blob") != _git_blob(control_input_bytes):
                failures.append(f"{prefix}:control-input-git-blob-mismatch")
            if observation.get("control_input_sha256") != _raw_sha256(control_input_bytes):
                failures.append(f"{prefix}:control-input-sha256-mismatch")
            if observation.get("control_input_canonical_digest") != _canonical_digest(control_input_value):
                failures.append(f"{prefix}:control-input-canonical-digest-mismatch")

        control_output_path = _safe_path(root, str(observation.get("control_output_path", "")))
        control_output_value: dict[str, Any] | None = None
        if control_output_path is None or not control_output_path.exists():
            failures.append(f"{prefix}:control-output-missing-or-unsafe")
        else:
            control_output_bytes = control_output_path.read_bytes()
            try:
                loaded_control = json.loads(control_output_bytes)
                control_output_value = loaded_control if isinstance(loaded_control, dict) else None
            except json.JSONDecodeError:
                control_output_value = None
            if control_output_value is None:
                failures.append(f"{prefix}:control-output-not-object")
            else:
                if observation.get("control_output_sha256") != _raw_sha256(control_output_bytes):
                    failures.append(f"{prefix}:control-output-sha256-mismatch")
                if observation.get("control_output_canonical_digest") != _canonical_digest(control_output_value):
                    failures.append(f"{prefix}:control-output-canonical-digest-mismatch")

        semantic_claim = observation.get("semantic_claim")
        claim_name = semantic_claim.get("name") if isinstance(semantic_claim, dict) else None
        source_expected = source_manifest.get("semantic_claims", {}).get(claim_name)
        target_expected = target_manifest.get("semantic_claims", {}).get(claim_name)
        if not claim_name or semantic_claim.get("legacy_output_value") != source_expected:
            failures.append(f"{prefix}:legacy-semantic-claim-mismatch")
        if not isinstance(semantic_claim, dict) or semantic_claim.get("current_control_output_value") != target_expected:
            failures.append(f"{prefix}:control-semantic-claim-mismatch")

        def speech_engine(value: dict[str, Any] | None) -> Any:
            if not isinstance(value, dict):
                return None
            audio = value.get("audio")
            if not isinstance(audio, list) or not audio or not isinstance(audio[0], dict):
                return None
            return audio[0].get("engine")

        target_fixture_value = _load_json(target_fixture) if target_fixture.exists() else {}
        expected_target_schema = target_fixture_value.get("schema") if isinstance(target_fixture_value, dict) else None
        if not output_value or output_value.get("schema") != expected_target_schema:
            failures.append(f"{prefix}:output-schema-not-target-schema")
        if speech_engine(output_value) != source_expected:
            failures.append(f"{prefix}:legacy-meaning-not-preserved")
        if speech_engine(control_output_value) != target_expected:
            failures.append(f"{prefix}:current-control-meaning-not-preserved")
        if not observation.get("source_object_unchanged"):
            failures.append(f"{prefix}:source-object-mutated-or-unverified")
        if not observation.get("control_object_unchanged"):
            failures.append(f"{prefix}:control-object-mutated-or-unverified")

        tests = observation.get("donor_targeted_tests", {})
        total = tests.get("total") if isinstance(tests, dict) else None
        passed = tests.get("passed") if isinstance(tests, dict) else None
        if not isinstance(total, int) or total <= 0 or passed != total:
            failures.append(f"{prefix}:donor-targeted-tests-not-all-passed")

        forbidden = observation.get("forbidden_promotions", {})
        required_false = (
            "whole_project_semantic_equivalence_proven",
            "direct_vs_chain_equivalence_proven",
            "chain_experiment_input_ready",
            "canon_authority_granted",
            "adapter_translation_garden_ownership_changed",
        )
        if not isinstance(forbidden, dict) or any(forbidden.get(key) is not False for key in required_false):
            failures.append(f"{prefix}:forbidden-promotion-claim")

        records.append(
            {
                "id": observation_id,
                "path_id": path_id,
                "lineage_id": path.get("lineage_id"),
                "source_generation": source_id,
                "target_generation": target_id,
                "donor_repository": donor_repo,
                "donor_commit": donor_commit,
                "execution_observed": True,
                "legacy_semantic_claim_preserved": speech_engine(output_value) == source_expected,
                "current_control_semantic_claim_preserved": speech_engine(control_output_value) == target_expected,
                "observed_output_schema": output_value.get("schema") if output_value else None,
            }
        )

    valid = not failures and bool(records)
    return {
        "schema": "axm.protocol-evolution.path-execution-evidence/v0.1",
        "scope": "retained-exact-donor-execution-observations-for-admitted-paths",
        "valid": valid,
        "observation_count": len(observations),
        "valid_observation_count": len(records) if valid else 0,
        "observed_execution_path_count": len({record["path_id"] for record in records}) if valid else 0,
        "records": records,
        "failures": failures,
        "migration_execution_observed_for_recorded_paths": valid,
        "donor_execution_replayed_in_ci": False,
        "whole_project_semantic_equivalence_proven": False,
        "direct_vs_chain_equivalence_proven": False,
        "chain_experiment_input_ready": False,
        "canon_authority_granted": False,
        "adapter_translation_garden_ownership_changed": False,
    }
