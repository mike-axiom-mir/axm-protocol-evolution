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
OBSERVATIONS = ROOT / "fixtures" / "path_execution_observations.json"
OBSERVATION_ID = "framestate-v0.4-to-v0.5-execution-2026-09-15"


class ReplayError(RuntimeError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def raw_sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayError(message)


def speech_engine(value: dict[str, Any]) -> Any:
    audio = value.get("audio")
    if not isinstance(audio, list) or not audio or not isinstance(audio[0], dict):
        return None
    return audio[0].get("engine")


def observation() -> dict[str, Any]:
    payload = load_json(OBSERVATIONS)
    rows = [row for row in payload.get("observations", []) if isinstance(row, dict) and row.get("id") == OBSERVATION_ID]
    require(len(rows) == 1, f"expected exactly one {OBSERVATION_ID} observation")
    return rows[0]


def verify_json_identity(path: Path, expected_blob: str, expected_sha256: str, expected_canonical: str) -> dict[str, Any]:
    data = path.read_bytes()
    value = json.loads(data)
    require(git_blob(data) == expected_blob, f"Git blob mismatch: {path}")
    require(raw_sha256(data) == expected_sha256, f"raw SHA-256 mismatch: {path}")
    require(canonical_digest(value) == expected_canonical, f"canonical digest mismatch: {path}")
    require(isinstance(value, dict), f"expected object JSON: {path}")
    return value


def verify_donor(donor_root: Path, obs: dict[str, Any]) -> None:
    require((donor_root / ".git").exists(), "donor root is not a Git checkout")
    head = subprocess.check_output(["git", "-C", str(donor_root), "rev-parse", "HEAD"], text=True).strip()
    require(head == obs.get("donor_commit"), f"donor HEAD mismatch: {head}")
    for record in obs.get("donor_files", []):
        require(isinstance(record, dict), "donor file record is not an object")
        relative = record.get("path")
        require(isinstance(relative, str) and relative, "donor file path missing")
        path = (donor_root / relative).resolve()
        try:
            path.relative_to(donor_root.resolve())
        except ValueError as exc:
            raise ReplayError(f"unsafe donor path: {relative}") from exc
        require(path.is_file(), f"donor file missing: {relative}")
        require(git_blob(path.read_bytes()) == record.get("git_blob"), f"donor Git blob mismatch: {relative}")


def run_targeted_donor_test(donor_root: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(donor_root / "src")
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.test_speech", "-v"],
        cwd=donor_root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        raise ReplayError("targeted donor speech tests failed:\n" + proc.stdout)
    require("Ran 5 tests" in proc.stdout and "OK" in proc.stdout, "targeted donor speech test count/result changed")


def replay(donor_root: Path) -> dict[str, Any]:
    obs = observation()
    require(obs.get("donor_repository") == "mike-axiom-mir/axm-framestate", "unexpected donor repository")
    verify_donor(donor_root, obs)

    source_path = ROOT / str(obs["source_fixture_path"])
    control_path = ROOT / str(obs["control_input_path"])
    source = verify_json_identity(
        source_path,
        str(obs["source_fixture_git_blob"]),
        str(obs["source_fixture_sha256"]),
        str(obs["source_canonical_digest"]),
    )
    control = verify_json_identity(
        control_path,
        str(obs["control_input_git_blob"]),
        str(obs["control_input_sha256"]),
        str(obs["control_input_canonical_digest"]),
    )

    donor_src = str(donor_root / "src")
    sys.path.insert(0, donor_src)
    try:
        from axm_framestate.canonical import normalize_project  # type: ignore
    finally:
        if sys.path and sys.path[0] == donor_src:
            sys.path.pop(0)

    source_before = copy.deepcopy(source)
    control_before = copy.deepcopy(control)
    output = normalize_project(source)
    control_output = normalize_project(control)
    require(source == source_before, "donor normalizer mutated admitted v0.4 source object")
    require(control == control_before, "donor normalizer mutated admitted v0.5 control object")

    retained_output = load_json(ROOT / str(obs["observed_output_path"]))
    retained_control = load_json(ROOT / str(obs["control_output_path"]))
    require(output == retained_output, "replayed v0.4 output differs from retained observation")
    require(control_output == retained_control, "replayed v0.5 control differs from retained observation")
    require(canonical_digest(output) == obs.get("observed_output_canonical_digest"), "replayed v0.4 output digest mismatch")
    require(canonical_digest(control_output) == obs.get("control_output_canonical_digest"), "replayed v0.5 control digest mismatch")

    claim = obs.get("semantic_claim")
    require(isinstance(claim, dict), "semantic claim missing")
    require(output.get("schema") == control.get("schema"), "replayed legacy output is not target schema")
    require(speech_engine(output) == claim.get("legacy_output_value"), "legacy semantic claim was not preserved")
    require(speech_engine(control_output) == claim.get("current_control_output_value"), "current control semantic claim was not preserved")

    run_targeted_donor_test(donor_root)

    forbidden = obs.get("forbidden_promotions")
    require(isinstance(forbidden, dict) and all(value is False for value in forbidden.values()), "forbidden promotion boundary changed")

    return {
        "schema": "axm.protocol-evolution.path-execution-ci-replay-result/v0.1",
        "valid": True,
        "observation_id": OBSERVATION_ID,
        "path_id": obs.get("path_id"),
        "donor_repository": obs.get("donor_repository"),
        "donor_commit": obs.get("donor_commit"),
        "source_fixture_identity_verified": True,
        "control_fixture_identity_verified": True,
        "donor_file_identities_verified": True,
        "source_object_unchanged": True,
        "control_object_unchanged": True,
        "retained_outputs_reproduced_exactly": True,
        "legacy_semantic_claim_preserved": True,
        "current_control_semantic_claim_preserved": True,
        "targeted_donor_tests_passed": True,
        "whole_project_semantic_equivalence_proven": False,
        "direct_vs_chain_equivalence_proven": False,
        "chain_experiment_input_ready": False,
        "canon_authority_granted": False,
        "adapter_translation_garden_ownership_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay the admitted FrameState v0.4 -> v0.5 donor execution.")
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
