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
SOURCE_MANIFEST = ROOT / "fixtures" / "generations" / "framestate-v0.2" / "manifest.json"

DONOR_REPOSITORY = "mike-axiom-mir/axm-framestate"
OLD_DONOR_COMMIT = "5d46363fb30bf5d30198b8cdec473d3bb9ba6287"
OLD_DONOR_FILES = {
    "src/axm_framestate/canonical.py": "e9ebd3798a0c9695053bf6e6477567fb405eefe5",
    "tests/test_machine.py": "56713f7130bc86309a0b708b54a108f4b31c1f38",
}
LATER_DONOR_COMMIT = "60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34"
LATER_DONOR_FILES = {
    "src/axm_framestate/canonical.py": "c44122ce84a238587ee263ca4df95be762992f6e",
    "examples/native_speech.json": "d40eb283960f11f6b8fb0676a90b398e805eb0bb",
}
LATER_EXAMPLE = "examples/native_speech.json"
SOURCE_SCHEMA = "axm.framestate.project/v0.2"
FUTURE_FIELD = "engine"


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


def verify_checkout(root: Path, expected_commit: str, expected_files: dict[str, str], label: str) -> None:
    require((root / ".git").exists(), f"{label} root is not a Git checkout")
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    require(head == expected_commit, f"{label} HEAD mismatch: {head}")
    resolved_root = root.resolve()
    for relative, expected_blob in expected_files.items():
        path = (root / relative).resolve()
        try:
            path.relative_to(resolved_root)
        except ValueError as exc:
            raise ReplayError(f"unsafe {label} path: {relative}") from exc
        require(path.is_file(), f"{label} file missing: {relative}")
        require(git_blob(path.read_bytes()) == expected_blob, f"{label} Git blob mismatch: {relative}")


def source_fixture() -> dict[str, Any]:
    manifest = load_json(SOURCE_MANIFEST)
    require(manifest.get("id") == "framestate-project-v0.2", "unexpected source manifest id")
    require(manifest.get("repository") == DONOR_REPOSITORY, "source repository changed")
    require(manifest.get("source_ref") == OLD_DONOR_COMMIT, "source donor commit changed")
    require(manifest.get("source_path") == "examples/narrated_motion.json", "source path changed")
    artifact = SOURCE_MANIFEST.parent / str(manifest.get("artifact", ""))
    require(artifact.is_file(), "source fixture missing")
    data = artifact.read_bytes()
    require(git_blob(data) == manifest.get("source_blob_sha"), "source fixture Git blob no longer matches manifest")
    value = json.loads(data)
    require(isinstance(value, dict), "source fixture must be an object")
    require(value.get("schema") == SOURCE_SCHEMA, "source fixture schema changed")
    audio = value.get("audio")
    require(isinstance(audio, list), "source fixture audio must be an array")
    speech = [row for row in audio if isinstance(row, dict) and row.get("kind") == "speech"]
    require(len(speech) == 1, "expected exactly one source speech event")
    require(FUTURE_FIELD not in speech[0], "source fixture already contains the future field")
    return value


def later_field_observation(later_root: Path) -> tuple[str, str]:
    payload = load_json(later_root / LATER_EXAMPLE)
    require(isinstance(payload, dict), "later donor example must be an object")
    require(payload.get("schema") == "axm.framestate.project/v0.5", "later donor example schema changed")
    audio = payload.get("audio")
    require(isinstance(audio, list), "later donor example audio must be an array")
    speech = [row for row in audio if isinstance(row, dict) and row.get("kind") == "speech"]
    require(len(speech) == 1, "expected exactly one later speech event")
    value = speech[0].get(FUTURE_FIELD)
    require(isinstance(value, str) and value, "later donor example no longer carries a concrete engine value")
    return FUTURE_FIELD, value


def run_old_donor_tests(old_root: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(old_root / "src")
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_machine.py", "-v"],
        cwd=old_root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        raise ReplayError("pinned v0.2 donor tests failed:\n" + proc.stdout)
    require("OK" in proc.stdout, "pinned v0.2 donor tests did not report OK")


def replay(old_root: Path, later_root: Path) -> dict[str, Any]:
    verify_checkout(old_root, OLD_DONOR_COMMIT, OLD_DONOR_FILES, "old donor")
    verify_checkout(later_root, LATER_DONOR_COMMIT, LATER_DONOR_FILES, "later donor")
    source = source_fixture()
    future_field, future_value = later_field_observation(later_root)

    donor_src = str(old_root / "src")
    sys.path.insert(0, donor_src)
    try:
        from axm_framestate.canonical import ProjectError, normalize_project  # type: ignore
    finally:
        if sys.path and sys.path[0] == donor_src:
            sys.path.pop(0)

    control_before = copy.deepcopy(source)
    control_first = normalize_project(source)
    control_second = normalize_project(copy.deepcopy(source))
    require(source == control_before, "v0.2 donor mutated admitted v0.2 positive-control input")
    require(control_first == control_second, "v0.2 positive-control normalization is not deterministic")
    require(isinstance(control_first, dict) and control_first.get("schema") == SOURCE_SCHEMA, "v0.2 positive control did not normalize as v0.2")

    probe = copy.deepcopy(source)
    speech_indexes = [
        index for index, row in enumerate(probe.get("audio", []))
        if isinstance(row, dict) and row.get("kind") == "speech"
    ]
    require(len(speech_indexes) == 1, "probe requires exactly one speech event")
    probe["audio"][speech_indexes[0]][future_field] = future_value
    probe_before = copy.deepcopy(probe)

    outcome = None
    refusal_message = None
    preserved = False
    silent_drop = False
    reinterpretation = False
    try:
        normalized = normalize_project(probe)
    except ProjectError as exc:
        outcome = "REFUSE"
        refusal_message = str(exc)
        require(probe == probe_before, "v0.2 donor mutated future-field probe before refusing")
        require("unsupported fields" in refusal_message, "v0.2 donor refused for an unrelated reason")
    else:
        require(probe == probe_before, "v0.2 donor mutated future-field probe")
        normalized_audio = normalized.get("audio", []) if isinstance(normalized, dict) else []
        normalized_speech = [row for row in normalized_audio if isinstance(row, dict) and row.get("kind") == "speech"]
        require(len(normalized_speech) == 1, "v0.2 donor accepted probe but speech event disappeared")
        if normalized_speech[0].get(future_field) == future_value:
            outcome = "OPAQUE_PRESERVE"
            preserved = True
        elif future_field not in normalized_speech[0]:
            outcome = "SILENT_DROP"
            silent_drop = True
        else:
            outcome = "REINTERPRET"
            reinterpretation = True
        require(not silent_drop, "v0.2 donor silently dropped a real later field")
        require(not reinterpretation, "v0.2 donor reinterpreted a real later field")

    require(outcome in {"REFUSE", "OPAQUE_PRESERVE"}, f"unsafe old-intermediary outcome: {outcome}")
    run_old_donor_tests(old_root)

    return {
        "schema": "axm.protocol-evolution.future-field-boundary-replay-result/v0.1",
        "valid": True,
        "donor_repository": DONOR_REPOSITORY,
        "old_donor_commit": OLD_DONOR_COMMIT,
        "later_donor_commit": LATER_DONOR_COMMIT,
        "donor_file_identities_verified": True,
        "source_fixture_identity_verified": True,
        "source_fixture_id": "framestate-project-v0.2",
        "probe_is_historical_fixture": False,
        "probe_is_migration_fixture": False,
        "future_field_source": LATER_EXAMPLE,
        "future_field": future_field,
        "future_value": future_value,
        "positive_control_normalized": True,
        "positive_control_deterministic": True,
        "old_intermediary_outcome": outcome,
        "refusal_message": refusal_message,
        "probe_object_unchanged": True,
        "unknown_field_preserved": preserved,
        "silent_drop_observed": silent_drop,
        "reinterpretation_observed": reinterpretation,
        "probe_canonical_digest": canonical_digest(probe_before),
        "pinned_old_donor_tests_passed": True,
        "migration_path_admitted": False,
        "whole_project_compatibility_proven": False,
        "universal_bridge_absence_proven": False,
        "canon_authority_granted": False,
        "adapter_translation_garden_ownership_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay one real later FrameState field against the exact v0.2 donor without inventing a bridge.")
    parser.add_argument("--old-donor-root", required=True, type=Path)
    parser.add_argument("--later-donor-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = replay(args.old_donor_root.resolve(), args.later_donor_root.resolve())
    except (ReplayError, OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
