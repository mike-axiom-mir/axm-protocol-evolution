from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit
import re

FULL_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
REPO_PART_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
RESULT_SCHEMA = "axm.protocol-evolution.evidence-reference-integrity/v0.1"


def _failure(ref: Any, reason: str) -> dict[str, Any]:
    return {
        "ref": ref,
        "valid": False,
        "reason": reason,
        "kind": None,
        "repository": None,
        "commit_refs": [],
    }


def inspect_pinned_github_reference(ref: Any) -> dict[str, Any]:
    """Inspect one donor evidence URL for immutable full-SHA pinning.

    Supported evidence carriers are deliberately narrow: GitHub commit URLs,
    blob URLs pinned to a full commit SHA, and compare URLs whose two endpoints
    are full commit SHAs.

    This is structural verification only. It does not contact GitHub, prove the
    resource exists, authenticate authorship, or validate the semantic claim
    attributed to the resource.
    """
    if not isinstance(ref, str) or not ref:
        return _failure(ref, "reference-not-nonempty-string")

    parsed = urlsplit(ref)
    if parsed.scheme != "https" or parsed.netloc != "github.com":
        return _failure(ref, "reference-not-https-github")
    if parsed.query:
        return _failure(ref, "query-not-allowed")

    segments = [segment for segment in parsed.path.split("/") if segment]
    if len(segments) < 4:
        return _failure(ref, "unsupported-github-reference-shape")

    owner, repo, kind = segments[0], segments[1], segments[2]
    if not REPO_PART_RE.fullmatch(owner) or not REPO_PART_RE.fullmatch(repo):
        return _failure(ref, "invalid-repository-identity")

    repository = f"{owner}/{repo}"

    if kind == "commit" and len(segments) == 4:
        sha = segments[3]
        if not FULL_SHA_RE.fullmatch(sha):
            return _failure(ref, "commit-reference-not-full-sha")
        return {
            "ref": ref,
            "valid": True,
            "reason": "full-sha-commit",
            "kind": "commit",
            "repository": repository,
            "commit_refs": [sha.lower()],
        }

    if kind == "blob" and len(segments) >= 5:
        sha = segments[3]
        if not FULL_SHA_RE.fullmatch(sha):
            return _failure(ref, "blob-reference-not-full-sha")
        if not any(segment for segment in segments[4:]):
            return _failure(ref, "blob-reference-missing-path")
        return {
            "ref": ref,
            "valid": True,
            "reason": "full-sha-blob",
            "kind": "blob",
            "repository": repository,
            "commit_refs": [sha.lower()],
        }

    if kind == "compare" and len(segments) == 4:
        compare_spec = segments[3]
        if "..." not in compare_spec:
            return _failure(ref, "compare-reference-missing-three-dot-range")
        base, head = compare_spec.split("...", 1)
        if not FULL_SHA_RE.fullmatch(base) or not FULL_SHA_RE.fullmatch(head):
            return _failure(ref, "compare-reference-endpoint-not-full-sha")
        return {
            "ref": ref,
            "valid": True,
            "reason": "full-sha-compare",
            "kind": "compare",
            "repository": repository,
            "commit_refs": [base.lower(), head.lower()],
        }

    return _failure(ref, "unsupported-github-reference-shape")


def analyze_evidence_reference_integrity(
    path_catalog: Mapping[str, Any],
    investigation_catalog: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify immutable pinning for donor refs in the checked-in edge catalogs."""
    failures: list[str] = []
    records: list[dict[str, Any]] = []
    total_reference_count = 0
    pinned_reference_count = 0

    catalogs = (
        ("path", path_catalog, "paths"),
        ("investigation", investigation_catalog, "investigations"),
    )

    for record_type, catalog, key in catalogs:
        raw_records = catalog.get(key, []) if isinstance(catalog, Mapping) else []
        if not isinstance(raw_records, list):
            failures.append(f"{record_type}-catalog:{key}-not-list")
            continue

        for index, raw in enumerate(raw_records):
            if not isinstance(raw, Mapping):
                failures.append(f"{record_type}-{index}:not-object")
                continue

            record_id = raw.get("id")
            if not isinstance(record_id, str) or not record_id:
                record_id = f"index-{index}"
                failures.append(f"{record_type}-{index}:invalid-id")

            evidence_refs = raw.get("evidence_refs")
            if not isinstance(evidence_refs, list) or not evidence_refs:
                failures.append(f"{record_type}-{record_id}:missing-or-invalid-evidence-refs")
                records.append(
                    {
                        "record_type": record_type,
                        "id": record_id,
                        "reference_count": 0,
                        "pinned_reference_count": 0,
                        "valid": False,
                        "references": [],
                    }
                )
                continue

            seen_refs: set[str] = set()
            reference_results: list[dict[str, Any]] = []
            record_failures_before = len(failures)
            record_pinned = 0

            for ref_index, ref in enumerate(evidence_refs):
                total_reference_count += 1
                inspected = inspect_pinned_github_reference(ref)
                reference_results.append(inspected)

                if isinstance(ref, str) and ref in seen_refs:
                    failures.append(
                        f"{record_type}-{record_id}:duplicate-evidence-ref:{ref_index}:{ref}"
                    )
                elif isinstance(ref, str):
                    seen_refs.add(ref)

                if inspected["valid"]:
                    pinned_reference_count += 1
                    record_pinned += 1
                else:
                    failures.append(
                        f"{record_type}-{record_id}:evidence-ref-{ref_index}:{inspected['reason']}"
                    )

            records.append(
                {
                    "record_type": record_type,
                    "id": record_id,
                    "reference_count": len(evidence_refs),
                    "pinned_reference_count": record_pinned,
                    "valid": len(failures) == record_failures_before,
                    "references": reference_results,
                }
            )

    return {
        "schema": RESULT_SCHEMA,
        "valid": not failures,
        "failures": failures,
        "record_count": len(records),
        "reference_count": total_reference_count,
        "pinned_reference_count": pinned_reference_count,
        "all_references_structurally_pinned": (
            total_reference_count > 0
            and pinned_reference_count == total_reference_count
            and not failures
        ),
        "records": records,
        "scope": "checked-in-migration-path-and-hold-donor-reference-pinning",
        "supported_reference_shapes": [
            "https://github.com/<owner>/<repo>/commit/<40-hex-sha>",
            "https://github.com/<owner>/<repo>/blob/<40-hex-sha>/<path>",
            "https://github.com/<owner>/<repo>/compare/<40-hex-sha>...<40-hex-sha>",
        ],
        "resource_existence_verified": False,
        "reference_target_content_verified": False,
        "authorship_verified": False,
        "semantic_claim_verified": False,
        "migration_execution_proven": False,
    }
