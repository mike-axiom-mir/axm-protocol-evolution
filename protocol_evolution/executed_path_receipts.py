from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .compatibility import CompatibilityState, verify_migration_receipt_binding
from .path_execution_evidence import analyze_path_execution_observations


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_path(root: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative.strip():
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def analyze_executed_path_receipts(
    payload: dict[str, Any],
    root: Path,
    *,
    execution_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind migration receipts to separately grounded admitted-path execution evidence.

    The receipt self-digest remains only an integrity/binding mechanism. Execution
    evidence, donor identity and the checked semantic claim come from the separate
    path-execution observation layer.
    """
    failures: list[str] = []
    if not isinstance(payload, dict):
        payload = {}
        failures.append("payload-not-object")

    if payload.get("schema") != "axm.protocol-evolution.executed-path-receipts/v0.1":
        failures.append("unsupported-schema")

    entries = payload.get("receipts", [])
    if not isinstance(entries, list):
        entries = []
        failures.append("receipts-not-list")

    if execution_payload is None:
        execution_payload = _load_json(root / "fixtures" / "path_execution_observations.json")
    lower = analyze_path_execution_observations(execution_payload, root)
    if not lower.get("valid"):
        failures.append("path-execution-evidence-invalid")

    migration_payload = _load_json(root / "fixtures" / "migration_paths.json")
    admitted = {
        row.get("id"): row
        for row in migration_payload.get("paths", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    observations = {
        row.get("id"): row
        for row in execution_payload.get("observations", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    valid_execution_ids = {
        row.get("id")
        for row in lower.get("records", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    } if lower.get("valid") else set()

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    records: list[dict[str, Any]] = []

    for index, entry in enumerate(entries):
        prefix = f"receipt[{index}]"
        if not isinstance(entry, dict):
            failures.append(f"{prefix}:not-object")
            continue

        entry_id = entry.get("id")
        path_id = entry.get("path_id")
        observation_id = entry.get("execution_observation_id")
        if not isinstance(entry_id, str) or not entry_id:
            failures.append(f"{prefix}:missing-id")
            continue
        if entry_id in seen_ids:
            failures.append(f"{prefix}:duplicate-id:{entry_id}")
        seen_ids.add(entry_id)

        if not isinstance(path_id, str) or path_id not in admitted:
            failures.append(f"{prefix}:unknown-admitted-path:{path_id}")
            continue
        if path_id in seen_paths:
            failures.append(f"{prefix}:duplicate-path-receipt:{path_id}")
        seen_paths.add(path_id)

        observation = observations.get(observation_id)
        if not isinstance(observation, dict):
            failures.append(f"{prefix}:unknown-execution-observation:{observation_id}")
            continue
        if observation_id not in valid_execution_ids:
            failures.append(f"{prefix}:execution-observation-not-grounded:{observation_id}")
        if observation.get("path_id") != path_id:
            failures.append(f"{prefix}:execution-path-mismatch")

        path = admitted[path_id]
        for field in ("lineage_id", "source_generation", "target_generation"):
            if observation.get(field) != path.get(field):
                failures.append(f"{prefix}:path-{field}-mismatch")

        source_path = _safe_path(root, observation.get("source_fixture_path"))
        target_path = _safe_path(root, observation.get("observed_output_path"))
        if source_path is None or not source_path.exists():
            failures.append(f"{prefix}:source-fixture-missing-or-unsafe")
            continue
        if target_path is None or not target_path.exists():
            failures.append(f"{prefix}:observed-target-missing-or-unsafe")
            continue
        try:
            source = _load_json(source_path)
            target = _load_json(target_path)
        except (json.JSONDecodeError, OSError):
            failures.append(f"{prefix}:source-or-target-not-readable-json")
            continue

        receipt = entry.get("receipt")
        if not isinstance(receipt, dict):
            failures.append(f"{prefix}:receipt-not-object")
            continue
        binding = verify_migration_receipt_binding(receipt, source=source, target=target)
        for failure in binding.get("failures", []):
            failures.append(f"{prefix}:binding:{failure}")

        if receipt.get("source_digest") != observation.get("source_canonical_digest"):
            failures.append(f"{prefix}:source-digest-not-execution-observation")
        if receipt.get("target_digest") != observation.get("observed_output_canonical_digest"):
            failures.append(f"{prefix}:target-digest-not-execution-observation")

        transformer_binding = entry.get("transformer_binding")
        donor_file = transformer_binding.get("donor_file") if isinstance(transformer_binding, dict) else None
        callable_name = transformer_binding.get("callable") if isinstance(transformer_binding, dict) else None
        donor_paths = {
            row.get("path")
            for row in observation.get("donor_files", [])
            if isinstance(row, dict) and isinstance(row.get("path"), str)
        }
        if not isinstance(donor_file, str) or donor_file not in donor_paths:
            failures.append(f"{prefix}:transformer-donor-file-not-observed")
        if not isinstance(callable_name, str) or not callable_name:
            failures.append(f"{prefix}:invalid-transformer-callable")
        expected_transformer = (
            f"{observation.get('donor_repository')}@{observation.get('donor_commit')}:{donor_file}#{callable_name}"
            if isinstance(donor_file, str) and isinstance(callable_name, str) and callable_name
            else None
        )
        if receipt.get("transformer") != expected_transformer:
            failures.append(f"{prefix}:transformer-identity-mismatch")

        semantic_claim = observation.get("semantic_claim")
        claim_name = semantic_claim.get("name") if isinstance(semantic_claim, dict) else None
        legacy_value = semantic_claim.get("legacy_output_value") if isinstance(semantic_claim, dict) else None
        expected_assertions = [f"{claim_name}={legacy_value}"] if isinstance(claim_name, str) and claim_name else []
        if receipt.get("assertions_checked") != expected_assertions:
            failures.append(f"{prefix}:semantic-assertion-binding-mismatch")

        execution_record = next(
            (row for row in lower.get("records", []) if isinstance(row, dict) and row.get("id") == observation_id),
            None,
        )
        semantic_preserved = bool(
            isinstance(execution_record, dict)
            and execution_record.get("legacy_semantic_claim_preserved") is True
        )
        expected_state = CompatibilityState.LOSSLESS_MIGRATION.value if semantic_preserved and source != target else CompatibilityState.SAME.value
        if receipt.get("compatibility_state") != expected_state:
            failures.append(f"{prefix}:compatibility-state-not-grounded-in-observation")
        if receipt.get("losses") != []:
            failures.append(f"{prefix}:unexpected-loss-claims")
        if receipt.get("ambiguities") != []:
            failures.append(f"{prefix}:unexpected-ambiguity-claims")

        records.append(
            {
                "id": entry_id,
                "path_id": path_id,
                "execution_observation_id": observation_id,
                "lineage_id": path.get("lineage_id"),
                "source_generation": path.get("source_generation"),
                "target_generation": path.get("target_generation"),
                "source_digest": receipt.get("source_digest"),
                "target_digest": receipt.get("target_digest"),
                "transformer": receipt.get("transformer"),
                "compatibility_state": receipt.get("compatibility_state"),
                "assertions_checked": receipt.get("assertions_checked"),
                "receipt_digest": receipt.get("receipt_digest"),
            }
        )

    valid = not failures and bool(records)
    return {
        "schema": "axm.protocol-evolution.executed-path-receipt-evidence/v0.1",
        "scope": "receipt-binding-to-separately-grounded-admitted-path-execution",
        "valid": valid,
        "receipt_count": len(entries),
        "valid_receipt_count": len(records) if valid else 0,
        "records": records,
        "failures": failures,
        "receipt_self_digest_proves_authorship": False,
        "receipt_self_digest_proves_transformer_execution": False,
        "receipt_self_digest_proves_semantic_truth": False,
        "whole_project_semantic_equivalence_proven": False,
        "direct_vs_chain_equivalence_proven": False,
        "chain_experiment_input_ready": False,
        "canon_authority_granted": False,
        "adapter_translation_garden_ownership_changed": False,
    }
