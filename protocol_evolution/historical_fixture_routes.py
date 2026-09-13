from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Mapping

HEX40 = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_KINDS = {"exact-historical-artifact", "candidate-gap"}


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _err(errors: list[str], code: str, *parts: Any) -> None:
    errors.append(":".join([code, *[str(part) for part in parts]]))


def analyze_historical_fixture_routes(payload: Mapping[str, Any], root: Path) -> dict[str, Any]:
    """Validate routes for grounding a historical generation fixture.

    A sealed all-history archive may be useful evidence, but it is not the only valid route.
    An exact historical artifact preserved byte-for-byte and bound to a full donor commit/path/blob
    is independently sufficient evidence for *fixture provenance*. This does not admit a generation,
    prove a migration path, or prove semantic equivalence.
    """
    errors: list[str] = []
    if payload.get("schema") != "axm.protocol-evolution.historical-fixture-routes/v0.1":
        _err(errors, "unsupported-schema", payload.get("schema"))

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

        kind = raw.get("kind")
        if kind not in ALLOWED_KINDS:
            _err(errors, "unknown-kind", rid, kind)

        history_archive = raw.get("history_archive")
        if not isinstance(history_archive, Mapping):
            _err(errors, "history-archive-missing", rid)
            history_archive = {}
        archive_available = history_archive.get("available_for_inspection") is True

        exact_artifact_valid = False
        if kind == "exact-historical-artifact":
            repo = raw.get("repository")
            commit = raw.get("commit")
            source_path = raw.get("source_path")
            donor_blob = raw.get("donor_blob_sha")
            fixture_path = raw.get("fixture_path")
            observed = raw.get("historical_value_observed") is True
            if not isinstance(repo, str) or "/" not in repo:
                _err(errors, "invalid-repository", rid)
            if not isinstance(commit, str) or not HEX40.fullmatch(commit):
                _err(errors, "invalid-commit", rid)
            if not isinstance(source_path, str) or not source_path:
                _err(errors, "source-path-missing", rid)
            if not isinstance(donor_blob, str) or not HEX40.fullmatch(donor_blob):
                _err(errors, "invalid-donor-blob", rid)
            if not isinstance(fixture_path, str) or not fixture_path:
                _err(errors, "fixture-path-missing", rid)
                local_blob = None
            else:
                resolved = (root / fixture_path).resolve()
                try:
                    resolved.relative_to(root.resolve())
                except ValueError:
                    _err(errors, "fixture-path-escapes-root", rid)
                    local_blob = None
                else:
                    if not resolved.is_file():
                        _err(errors, "fixture-file-missing", rid, fixture_path)
                        local_blob = None
                    else:
                        local_blob = _git_blob_sha(resolved.read_bytes())
                        if local_blob != donor_blob:
                            _err(errors, "fixture-donor-byte-identity-mismatch", rid, local_blob, donor_blob)
            if not observed:
                _err(errors, "historical-observation-required", rid)
            exact_artifact_valid = (
                observed
                and isinstance(repo, str) and "/" in repo
                and isinstance(commit, str) and bool(HEX40.fullmatch(commit))
                and isinstance(source_path, str) and bool(source_path)
                and isinstance(donor_blob, str) and bool(HEX40.fullmatch(donor_blob))
                and local_blob == donor_blob
            )
            claimed = raw.get("independent_fixture_provenance_ready")
            if claimed is not exact_artifact_valid:
                _err(errors, "provenance-readiness-mismatch", rid, claimed, exact_artifact_valid)
        elif kind == "candidate-gap":
            if raw.get("historical_value_observed") is not False:
                _err(errors, "candidate-gap-cannot-claim-historical-value", rid)
            if raw.get("independent_fixture_provenance_ready") is not False:
                _err(errors, "candidate-gap-cannot-be-ready", rid)

        results.append({
            "id": rid,
            "kind": kind,
            "history_archive_available_for_inspection": archive_available,
            "independent_exact_historical_artifact_valid": exact_artifact_valid,
            "independent_fixture_provenance_ready": exact_artifact_valid,
        })

    return {
        "schema": "axm.protocol-evolution.historical-fixture-routes-evidence/v0.1",
        "valid": not errors,
        "errors": errors,
        "record_count": len(results),
        "independent_ready_count": sum(1 for r in results if r["independent_fixture_provenance_ready"]),
        "records": results,
        "truth_boundary": {
            "full_history_archive_is_not_mandatory_for_exact_fixture_provenance": True,
            "exact_fixture_provenance_is_not_generation_admission": True,
            "exact_fixture_provenance_is_not_migration_path_evidence": True,
            "exact_fixture_provenance_is_not_semantic_equivalence": True,
            "candidate_gap_remains_unpromoted": True,
            "adapter_translation_garden_ownership_unchanged": True,
        },
    }
