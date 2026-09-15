from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVESTIGATIONS = ROOT / "fixtures" / "migration_path_investigations.json"
SOURCE_MANIFEST = ROOT / "fixtures" / "generations" / "framestate-v0.1" / "manifest.json"
TARGET_MANIFEST = ROOT / "fixtures" / "generations" / "framestate-v0.2" / "manifest.json"
INVESTIGATION_ID = "framestate-v0.1-to-v0.2-audit-2026-09-12"
EXPECTED_DONOR_REPOSITORY = "mike-axiom-mir/axm-framestate"
EXPECTED_DONOR_COMMIT = "5d46363fb30bf5d30198b8cdec473d3bb9ba6287"
EXPECTED_DONOR_FILES = {
    "src/axm_framestate/canonical.py": "e9ebd3798a0c9695053bf6e6477567fb405eefe5",
    "tests/test_machine.py": "56713f7130bc86309a0b708b54a108f4b31c1f38",
}
SOURCE_SCHEMA = "axm.framestate.project/v0.1"
TARGET_SCHEMA = "axm.framestate.project/v0.2"


class ReplayError(RuntimeError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayError(message)


def verify_donor(donor_root: Path) -> None:
    require((donor_root / ".git").exists(), "donor root is not a Git checkout")
    head = subprocess.check_output(["git", "-C", str(donor_root), "rev-parse", "HEAD"], text=True).strip()
    require(head == EXPECTED_DONOR_COMMIT, f"donor HEAD mismatch: {head}")
    for relative, expected_blob in EXPECTED_DONOR_FILES.items():
        path = (donor_root / relative).resolve()
        try:
            path.relative_to(donor_root.resolve())
        except ValueError as exc:
            raise ReplayError(f"unsafe donor path: {relative}") from exc
        require(path.is_file(), f"donor file missing: {relative}")
        require(git_blob(path.read_bytes()) == expected_blob, f"donor Git blob mismatch: {relative}")


def investigation() -> dict[str, Any]:
    payload = load_json(INVESTIGATIONS)
    rows = [
        row
        for row in payload.get("investigations", [])
        if isinstance(row, dict) and row.get("id") == INVESTIGATION_ID
    ]
    require(len(rows) == 1, f"expected exactly one {INVESTIGATION_ID} investigation")
    row = rows[0]
    require(row.get("status") == "HOLD", "investigation is no longer HOLD")
    require(row.get("source_generation") == "framestate-project-v0.1", "source generation changed")
    require(row.get("target_generation") == "framestate-project-v0.2", "target generation changed")
    return row


def source_fixture() -> dict[str, Any]:
    manifest = load_json(SOURCE_MANIFEST)
    require(manifest.get("id") == "framestate-project-v0.1", "unexpected source manifest id")
    require(manifest.get("repository") == EXPECTED_DONOR_REPOSITORY, "source repository changed")
    require(manifest.get("source_ref") == "5b5f73cb78667d9af981af3b38cd7a7ce3a5dab7", "source ref changed")
    artifact = SOURCE_MANIFEST.parent / str(manifest.get("artifact", ""))
    require(artifact.is_file(), "source fixture missing")
    data = artifact.read_bytes()
    require(git_blob(data) == manifest.get("source_blob_sha"), "source fixture Git blob no longer matches manifest")
    value = json.loads(data)
    require(isinstance(value, dict), "source fixture must be an object")
    require(value.get("schema") == SOURCE_SCHEMA, "source fixture schema changed")
    require(manifest.get("semantic_claims", {}).get("audio_model") == "tone_only", "source semantic claim changed")
    audio = value.get("audio", [])
    require(isinstance(audio, list) and all(isinstance(row, dict) and row.get("kind") == "tone" for row in audio), "source fixture is not tone-only")
    return value


def verify_target_manifest() -> None:
    manifest = load_json(TARGET_MANIFEST)
    require(manifest.get("id") == "framestate-project-v0.2", "unexpected target manifest id")
    require(manifest.get("repository") == EXPECTED_DONOR_REPOSITORY, "target repository changed")
    require(manifest.get("source_ref") == EXPECTED_DONOR_COMMIT, "target donor commit changed")
    artifact = TARGET_MANIFEST.parent / str(manifest.get("artifact", ""))
    require(artifact.is_file(), "target fixture missing")
    value = load_json(artifact)
    require(isinstance(value, dict) and value.get("schema") == TARGET_SCHEMA, "target fixture schema changed")


def run_donor_tests(donor_root: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(donor_root / "src")
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_machine.py", "-v"],
        cwd=donor_root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        raise ReplayError("pinned donor tests failed:\n" + proc.stdout)
    require("OK" in proc.stdout, "pinned donor tests did not report OK")


def replay(donor_root: Path) -> dict[str, Any]:
    row = investigation()
    verify_target_manifest()
    verify_donor(donor_root)
    source = source_fixture()

    donor_src = str(donor_root / "src")
    sys.path.insert(0, donor_src)
    try:
        from axm_framestate.canonical import normalize_project  # type: ignore
    finally:
        if sys.path and sys.path[0] == donor_src:
            sys.path.pop(0)

    before = copy.deepcopy(source)
    first = normalize_project(source)
    second = normalize_project(copy.deepcopy(source))

    require(source == before, "v0.2 donor normalizer mutated admitted v0.1 source object")
    require(first == second, "v0.2 donor normalization of v0.1 is not deterministic")
    require(isinstance(first, dict), "v0.2 donor output is not an object")
    require(first.get("schema") == SOURCE_SCHEMA, "v0.2 donor rewrote v0.1 schema; HOLD must be reconsidered")
    require(first.get("schema") != TARGET_SCHEMA, "reader compatibility became a target-schema transformation")
    output_audio = first.get("audio", [])
    require(isinstance(output_audio, list) and all(isinstance(item, dict) and item.get("kind") == "tone" for item in output_audio), "tone-only source meaning was not preserved")

    run_donor_tests(donor_root)

    return {
        "schema": "axm.protocol-evolution.hold-path-execution-replay-result/v0.1",
        "valid": True,
        "investigation_id": row.get("id"),
        "status": "HOLD",
        "donor_repository": EXPECTED_DONOR_REPOSITORY,
        "donor_commit": EXPECTED_DONOR_COMMIT,
        "donor_file_identities_verified": True,
        "source_fixture_identity_verified": True,
        "source_object_unchanged": True,
        "deterministic_replay_verified": True,
        "source_schema": SOURCE_SCHEMA,
        "target_schema": TARGET_SCHEMA,
        "observed_output_schema": first.get("schema"),
        "observed_output_canonical_digest": canonical_digest(first),
        "tone_only_semantic_claim_preserved": True,
        "pinned_donor_tests_passed": True,
        "reader_compatibility_observed": True,
        "migration_path_admitted": False,
        "whole_project_semantic_equivalence_proven": False,
        "chain_experiment_input_ready": False,
        "canon_authority_granted": False,
        "adapter_translation_garden_ownership_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay FrameState v0.1 through the exact v0.2 donor while preserving the HOLD boundary.")
    parser.add_argument("--donor-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = replay(args.donor_root.resolve())
    except (ReplayError, OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
