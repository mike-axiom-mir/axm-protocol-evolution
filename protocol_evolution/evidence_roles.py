from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

RESULT_SCHEMA = "axm.protocol-evolution.edge-evidence-role-binding/v0.2"
ROLE_SCHEMA = "axm.protocol-evolution.evidence-reference-roles/v0.2"

ALLOWED_ROLES = {
    "transition-introduction",
    "transition-mechanism",
    "behavior-preservation-check",
    "donor-interpretation-note",
    "historical-range",
    "checkpoint-state",
    "reader-compatibility-behavior",
    "recovery-history",
    "protocol-baseline",
    "incompatibility-check",
}


def _index_evidence_records(
    records: Any,
    *,
    record_type: str,
    id_key: str,
    status_required: str | None = None,
) -> tuple[dict[str, Mapping[str, Any]], int, list[str]]:
    failures: list[str] = []
    index: dict[str, Mapping[str, Any]] = {}
    reference_count = 0

    if not isinstance(records, list):
        return {}, 0, [f"{record_type}-catalog:records-not-list"]

    for position, raw_record in enumerate(records):
        if not isinstance(raw_record, Mapping):
            failures.append(f"{record_type}-{position}:not-object")
            continue

        record_id = raw_record.get(id_key)
        if not isinstance(record_id, str) or not record_id:
            failures.append(f"{record_type}-{position}:invalid-id")
            continue
        if record_id in index:
            failures.append(f"{record_type}-{position}:duplicate-id:{record_id}")
            continue

        if status_required is not None:
            status = raw_record.get("status")
            if status != status_required:
                failures.append(
                    f"{record_type}-{record_id}:unsupported-status:{status}"
                )

        evidence_refs = raw_record.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            failures.append(
                f"{record_type}-{record_id}:missing-or-invalid-evidence-refs"
            )
            evidence_refs = []
        elif any(not isinstance(ref, str) or not ref for ref in evidence_refs):
            failures.append(f"{record_type}-{record_id}:invalid-evidence-ref")
        if len(set(evidence_refs)) != len(evidence_refs):
            failures.append(f"{record_type}-{record_id}:duplicate-evidence-ref")

        reference_count += len(evidence_refs)
        index[record_id] = raw_record

    return index, reference_count, failures


def analyze_evidence_roles(
    path_catalog: Mapping[str, Any],
    investigation_catalog: Mapping[str, Any],
    role_catalog: Mapping[str, Any],
    donor_binding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind each admitted or HOLD edge evidence reference to one explicit audit role.

    This layer is descriptive only. Exact role coverage improves auditability but
    does not convert a HOLD investigation into an admitted path and does not prove
    that a role declaration is semantically correct or sufficient.
    """
    failures: list[str] = []

    donor_binding_valid = bool(
        isinstance(donor_binding_result, Mapping)
        and donor_binding_result.get("valid") is True
    )
    if not donor_binding_valid:
        failures.append("donor-binding-invalid")

    raw_paths = path_catalog.get("paths", []) if isinstance(path_catalog, Mapping) else []
    path_index, admitted_reference_count, path_failures = _index_evidence_records(
        raw_paths,
        record_type="path",
        id_key="id",
    )
    failures.extend(path_failures)

    raw_investigations = (
        investigation_catalog.get("investigations", [])
        if isinstance(investigation_catalog, Mapping)
        else []
    )
    investigation_index, hold_reference_count, investigation_failures = (
        _index_evidence_records(
            raw_investigations,
            record_type="investigation",
            id_key="id",
            status_required="HOLD",
        )
    )
    failures.extend(investigation_failures)

    if role_catalog.get("schema") != ROLE_SCHEMA:
        failures.append(
            f"role-catalog:unexpected-schema:{role_catalog.get('schema')}"
        )

    raw_role_records = (
        role_catalog.get("records", []) if isinstance(role_catalog, Mapping) else []
    )
    if not isinstance(raw_role_records, list):
        failures.append("role-catalog:records-not-list")
        raw_role_records = []

    record_indexes = {
        "path": path_index,
        "investigation": investigation_index,
    }
    covered_record_ids: dict[str, set[str]] = {
        "path": set(),
        "investigation": set(),
    }
    seen_role_records: set[tuple[str, str]] = set()
    role_counts: Counter[str] = Counter()
    role_bound_path_reference_count = 0
    role_bound_hold_reference_count = 0
    records: list[dict[str, Any]] = []

    for position, raw_record in enumerate(raw_role_records):
        if not isinstance(raw_record, Mapping):
            failures.append(f"role-record-{position}:not-object")
            continue

        record_type = raw_record.get("record_type")
        record_id = raw_record.get("record_id")
        if record_type not in record_indexes:
            failures.append(
                f"role-record-{position}:unsupported-record-type:{record_type}"
            )
            continue
        if not isinstance(record_id, str) or not record_id:
            failures.append(f"role-record-{position}:invalid-record-id")
            continue

        record_key = (record_type, record_id)
        if record_key in seen_role_records:
            failures.append(
                f"role-record-{position}:duplicate-record:{record_type}:{record_id}"
            )
            continue
        seen_role_records.add(record_key)

        source_record = record_indexes[record_type].get(record_id)
        if source_record is None:
            failures.append(
                f"role-record-{position}:unknown-{record_type}:{record_id}"
            )
            continue
        covered_record_ids[record_type].add(record_id)

        raw_refs = raw_record.get("references")
        if not isinstance(raw_refs, list) or not raw_refs:
            failures.append(
                f"role-record-{record_type}-{record_id}:references-not-list-or-empty"
            )
            raw_refs = []

        assigned_refs: list[str] = []
        record_roles: list[dict[str, str]] = []
        for ref_position, raw_ref in enumerate(raw_refs):
            if not isinstance(raw_ref, Mapping):
                failures.append(
                    f"role-record-{record_type}-{record_id}:"
                    f"reference-{ref_position}:not-object"
                )
                continue

            ref = raw_ref.get("ref")
            role = raw_ref.get("role")
            observation = raw_ref.get("observation")
            if not isinstance(ref, str) or not ref:
                failures.append(
                    f"role-record-{record_type}-{record_id}:"
                    f"reference-{ref_position}:invalid-ref"
                )
                continue
            if not isinstance(role, str) or role not in ALLOWED_ROLES:
                failures.append(
                    f"role-record-{record_type}-{record_id}:"
                    f"reference-{ref_position}:invalid-role:{role}"
                )
                continue
            if not isinstance(observation, str) or not observation.strip():
                failures.append(
                    f"role-record-{record_type}-{record_id}:"
                    f"reference-{ref_position}:missing-observation"
                )
                continue

            assigned_refs.append(ref)
            role_counts[role] += 1
            record_roles.append(
                {
                    "ref": ref,
                    "role": role,
                    "observation": observation.strip(),
                }
            )

        if len(set(assigned_refs)) != len(assigned_refs):
            failures.append(
                f"role-record-{record_type}-{record_id}:"
                "duplicate-reference-assignment"
            )

        source_refs = source_record.get("evidence_refs", [])
        source_ref_set = set(source_refs) if isinstance(source_refs, list) else set()
        assigned_ref_set = set(assigned_refs)

        for missing in sorted(source_ref_set - assigned_ref_set):
            failures.append(
                f"role-record-{record_type}-{record_id}:"
                f"missing-reference-role:{missing}"
            )
        for extra in sorted(assigned_ref_set - source_ref_set):
            failures.append(
                f"role-record-{record_type}-{record_id}:"
                f"reference-not-in-{record_type}:{extra}"
            )

        exact_coverage = (
            source_ref_set == assigned_ref_set
            and isinstance(source_refs, list)
            and len(assigned_refs) == len(source_refs)
        )
        if exact_coverage:
            if record_type == "path":
                role_bound_path_reference_count += len(assigned_refs)
            else:
                role_bound_hold_reference_count += len(assigned_refs)

        records.append(
            {
                "record_type": record_type,
                "record_id": record_id,
                "reference_count": len(source_refs)
                if isinstance(source_refs, list)
                else 0,
                "role_bound_reference_count": len(assigned_refs),
                "references": record_roles,
            }
        )

    for record_type, source_index in record_indexes.items():
        for record_id in sorted(
            set(source_index) - covered_record_ids[record_type]
        ):
            failures.append(
                f"{record_type}-{record_id}:missing-role-record"
            )

    total_reference_count = admitted_reference_count + hold_reference_count
    role_bound_reference_count = (
        role_bound_path_reference_count + role_bound_hold_reference_count
    )
    valid = not failures

    return {
        "schema": RESULT_SCHEMA,
        "scope": "admitted-and-hold-edge-evidence-reference-role-binding",
        "valid": valid,
        "donor_binding_valid": donor_binding_valid,
        "path_record_count": len(path_index),
        "investigation_record_count": len(investigation_index),
        "role_record_count": len(raw_role_records),
        "admitted_reference_count": admitted_reference_count,
        "hold_reference_count": hold_reference_count,
        "total_reference_count": total_reference_count,
        "role_bound_path_reference_count": role_bound_path_reference_count,
        "role_bound_hold_reference_count": role_bound_hold_reference_count,
        "role_bound_reference_count": role_bound_reference_count,
        "all_edge_refs_have_exactly_one_declared_role": (
            valid and role_bound_reference_count == total_reference_count
        ),
        "all_hold_refs_have_exactly_one_declared_role": (
            valid
            and role_bound_hold_reference_count == hold_reference_count
        ),
        "hold_status_promoted_to_admission": False,
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


def analyze_admitted_evidence_roles(
    path_catalog: Mapping[str, Any],
    role_catalog: Mapping[str, Any],
    donor_binding_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Backward-compatible admitted-only view using the v0.2 role catalog."""
    filtered_records = []
    if isinstance(role_catalog, Mapping):
        raw_records = role_catalog.get("records", [])
        if isinstance(raw_records, list):
            filtered_records = [
                record
                for record in raw_records
                if isinstance(record, Mapping) and record.get("record_type") == "path"
            ]

    filtered_role_catalog = {
        "schema": role_catalog.get("schema")
        if isinstance(role_catalog, Mapping)
        else None,
        "records": filtered_records,
    }
    return analyze_evidence_roles(
        path_catalog,
        {"investigations": []},
        filtered_role_catalog,
        donor_binding_result,
    )
