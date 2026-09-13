from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

RESULT_SCHEMA = "axm.protocol-evolution.admitted-evidence-role-binding/v0.1"
ROLE_SCHEMA = "axm.protocol-evolution.evidence-reference-roles/v0.1"

ALLOWED_ROLES = {
    "transition-introduction",
    "transition-mechanism",
    "behavior-preservation-check",
    "donor-interpretation-note",
    "historical-range",
    "checkpoint-state",
}


def analyze_admitted_evidence_roles(
    path_catalog: Mapping[str, Any],
    role_catalog: Mapping[str, Any],
    donor_binding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind each admitted migration-path reference to one explicit evidence role.

    This layer is intentionally descriptive rather than semantic proof. It makes
    the current evidence bundle auditable without claiming that a declared role
    is correct, sufficient, trustworthy, or execution proof.
    """
    failures: list[str] = []

    donor_binding_valid = bool(
        isinstance(donor_binding_result, Mapping) and donor_binding_result.get("valid") is True
    )
    if not donor_binding_valid:
        failures.append("donor-binding-invalid")

    raw_paths = path_catalog.get("paths", []) if isinstance(path_catalog, Mapping) else []
    if not isinstance(raw_paths, list):
        failures.append("path-catalog:paths-not-list")
        raw_paths = []

    path_index: dict[str, Mapping[str, Any]] = {}
    admitted_reference_count = 0
    for index, raw_path in enumerate(raw_paths):
        if not isinstance(raw_path, Mapping):
            failures.append(f"path-{index}:not-object")
            continue
        path_id = raw_path.get("id")
        if not isinstance(path_id, str) or not path_id:
            failures.append(f"path-{index}:invalid-id")
            continue
        if path_id in path_index:
            failures.append(f"path-{index}:duplicate-id:{path_id}")
            continue
        evidence_refs = raw_path.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            failures.append(f"path-{path_id}:missing-or-invalid-evidence-refs")
            evidence_refs = []
        elif any(not isinstance(ref, str) or not ref for ref in evidence_refs):
            failures.append(f"path-{path_id}:invalid-evidence-ref")
        if len(set(evidence_refs)) != len(evidence_refs):
            failures.append(f"path-{path_id}:duplicate-evidence-ref")
        admitted_reference_count += len(evidence_refs)
        path_index[path_id] = raw_path

    if role_catalog.get("schema") != ROLE_SCHEMA:
        failures.append(f"role-catalog:unexpected-schema:{role_catalog.get('schema')}")

    raw_role_records = role_catalog.get("records", []) if isinstance(role_catalog, Mapping) else []
    if not isinstance(raw_role_records, list):
        failures.append("role-catalog:records-not-list")
        raw_role_records = []

    seen_role_records: set[tuple[str, str]] = set()
    covered_path_ids: set[str] = set()
    role_bound_reference_count = 0
    role_counts: Counter[str] = Counter()
    records: list[dict[str, Any]] = []

    for index, raw_record in enumerate(raw_role_records):
        if not isinstance(raw_record, Mapping):
            failures.append(f"role-record-{index}:not-object")
            continue

        record_type = raw_record.get("record_type")
        record_id = raw_record.get("record_id")
        if record_type != "path":
            failures.append(f"role-record-{index}:unsupported-record-type:{record_type}")
            continue
        if not isinstance(record_id, str) or not record_id:
            failures.append(f"role-record-{index}:invalid-record-id")
            continue

        record_key = (record_type, record_id)
        if record_key in seen_role_records:
            failures.append(f"role-record-{index}:duplicate-record:{record_type}:{record_id}")
            continue
        seen_role_records.add(record_key)

        path = path_index.get(record_id)
        if path is None:
            failures.append(f"role-record-{index}:unknown-path:{record_id}")
            continue
        covered_path_ids.add(record_id)

        raw_refs = raw_record.get("references")
        if not isinstance(raw_refs, list) or not raw_refs:
            failures.append(f"role-record-{record_id}:references-not-list-or-empty")
            raw_refs = []

        assigned_refs: list[str] = []
        record_roles: list[dict[str, str]] = []
        for ref_index, raw_ref in enumerate(raw_refs):
            if not isinstance(raw_ref, Mapping):
                failures.append(f"role-record-{record_id}:reference-{ref_index}:not-object")
                continue
            ref = raw_ref.get("ref")
            role = raw_ref.get("role")
            observation = raw_ref.get("observation")
            if not isinstance(ref, str) or not ref:
                failures.append(f"role-record-{record_id}:reference-{ref_index}:invalid-ref")
                continue
            if not isinstance(role, str) or role not in ALLOWED_ROLES:
                failures.append(
                    f"role-record-{record_id}:reference-{ref_index}:invalid-role:{role}"
                )
                continue
            if not isinstance(observation, str) or not observation.strip():
                failures.append(
                    f"role-record-{record_id}:reference-{ref_index}:missing-observation"
                )
                continue
            assigned_refs.append(ref)
            role_counts[role] += 1
            record_roles.append(
                {"ref": ref, "role": role, "observation": observation.strip()}
            )

        if len(set(assigned_refs)) != len(assigned_refs):
            failures.append(f"role-record-{record_id}:duplicate-reference-assignment")

        path_refs = path.get("evidence_refs", [])
        path_ref_set = set(path_refs) if isinstance(path_refs, list) else set()
        assigned_ref_set = set(assigned_refs)
        for missing in sorted(path_ref_set - assigned_ref_set):
            failures.append(f"role-record-{record_id}:missing-reference-role:{missing}")
        for extra in sorted(assigned_ref_set - path_ref_set):
            failures.append(f"role-record-{record_id}:reference-not-in-path:{extra}")

        if path_ref_set == assigned_ref_set and len(assigned_refs) == len(path_refs):
            role_bound_reference_count += len(assigned_refs)

        records.append(
            {
                "record_type": "path",
                "record_id": record_id,
                "reference_count": len(path_refs),
                "role_bound_reference_count": len(assigned_refs),
                "references": record_roles,
            }
        )

    for path_id in sorted(set(path_index) - covered_path_ids):
        failures.append(f"path-{path_id}:missing-role-record")

    valid = not failures
    return {
        "schema": RESULT_SCHEMA,
        "scope": "admitted-migration-path-evidence-reference-role-binding",
        "valid": valid,
        "donor_binding_valid": donor_binding_valid,
        "path_record_count": len(path_index),
        "role_record_count": len(raw_role_records),
        "admitted_reference_count": admitted_reference_count,
        "role_bound_reference_count": role_bound_reference_count,
        "all_admitted_path_refs_have_exactly_one_declared_role": (
            valid and role_bound_reference_count == admitted_reference_count
        ),
        "declared_role_counts": dict(sorted(role_counts.items())),
        "records": records,
        "failures": failures,
        "role_binding_only": True,
        "reference_target_content_semantically_verified": False,
        "evidence_sufficiency_verified": False,
        "authorship_verified": False,
        "migration_execution_proven": False,
        "chain_vs_direct_equivalence_proven": False,
    }
