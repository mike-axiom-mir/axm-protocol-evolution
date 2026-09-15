from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVESTIGATIONS = ROOT / "fixtures" / "migration_path_investigations.json"
G1_MANIFEST = ROOT / "fixtures" / "generations" / "city-p2p-g1" / "manifest.json"
G1_PACKET = ROOT / "fixtures" / "generations" / "city-p2p-g1" / "packet.json"
G2_MANIFEST = ROOT / "fixtures" / "generations" / "city-p2p-g2" / "manifest.json"
G2_PACKET = ROOT / "fixtures" / "generations" / "city-p2p-g2" / "packet.json"

INVESTIGATION_ID = "city-p2p-g1-to-g2-audit-2026-09-12"
EXPECTED_REPOSITORY = "mike-axiom-mir/axm-city-multiplayer"
G1_COMMIT = "d3b1bfb79d4e997781037ce0723c193be5f5df7a"
G2_COMMIT = "241c613b58cf624bb852d84aba1136f2f61e91f3"
EXPECTED_G1_FILES = {
    "axm_p2p/udp.py": "770db9c3efea995f4f7d8c0f1aecab8e2617543a",
    "axm_p2p/invite.py": "d91fdfc67309f538474df39a7f02430f9260e3c0",
}
EXPECTED_G2_FILES = {
    "axm_p2p/udp.py": "e15495244a0293dd5f53441862a163cfae0a9837",
    "axm_p2p/invite.py": "d91fdfc67309f538474df39a7f02430f9260e3c0",
    "tests/test_p2p.py": "84f3918c82391796dc692d5692f82174a58aa53e",
}


class ReplayError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayError(message)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def verify_checkout(root: Path, expected_commit: str, expected_files: dict[str, str], label: str) -> None:
    require((root / ".git").exists(), f"{label} root is not a Git checkout")
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    require(head == expected_commit, f"{label} HEAD mismatch: {head}")
    root_resolved = root.resolve()
    for relative, expected_blob in expected_files.items():
        path = (root / relative).resolve()
        try:
            path.relative_to(root_resolved)
        except ValueError as exc:
            raise ReplayError(f"unsafe {label} donor path: {relative}") from exc
        require(path.is_file(), f"{label} donor file missing: {relative}")
        observed = git_blob(path.read_bytes())
        require(observed == expected_blob, f"{label} donor Git blob mismatch for {relative}: {observed}")


def verify_research_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    investigations = load_json(INVESTIGATIONS)
    rows = [
        row
        for row in investigations.get("investigations", [])
        if isinstance(row, dict) and row.get("id") == INVESTIGATION_ID
    ]
    require(len(rows) == 1, f"expected exactly one {INVESTIGATION_ID} investigation")
    investigation = rows[0]
    require(investigation.get("status") == "HOLD", "City G1 -> G2 investigation is no longer HOLD")
    require(investigation.get("source_generation") == "city-p2p-handshake-g1", "City G1 source generation changed")
    require(investigation.get("target_generation") == "city-p2p-handshake-g2", "City G2 target generation changed")

    g1 = load_json(G1_MANIFEST)
    g2 = load_json(G2_MANIFEST)
    require(g1.get("id") == "city-p2p-handshake-g1", "unexpected G1 manifest id")
    require(g2.get("id") == "city-p2p-handshake-g2", "unexpected G2 manifest id")
    require(g1.get("repository") == EXPECTED_REPOSITORY, "G1 repository changed")
    require(g2.get("repository") == EXPECTED_REPOSITORY, "G2 repository changed")
    require(g1.get("source_ref") == G1_COMMIT, "G1 source ref changed")
    require(g2.get("source_ref") == G2_COMMIT, "G2 source ref changed")

    g1_claims = g1.get("semantic_claims", {})
    g2_claims = g2.get("semantic_claims", {})
    require(g1_claims == {"protocol_version": 1, "admission_proof": "WELCOME", "ack_required": False}, "G1 semantic claims changed")
    require(g2_claims == {"protocol_version": 2, "admission_proof": "ACK", "ack_required": True}, "G2 semantic claims changed")

    g1_packet = load_json(G1_PACKET)
    g2_packet = load_json(G2_PACKET)
    require(isinstance(g1_packet, dict) and g1_packet.get("t") == "HELLO", "G1 packet is not HELLO")
    require(set(g1_packet) == {"t", "s", "g", "b", "n", "m"}, "G1 packet shape changed")
    require("pv" not in g1_packet, "G1 fixture unexpectedly carries a G2 protocol-version field")
    require(isinstance(g2_packet, dict) and g2_packet.get("t") == "HELLO", "G2 packet is not HELLO")
    require(g2_packet.get("pv") == 2, "G2 packet protocol version changed")
    require(set(g2_packet) == {"t", "pv", "s", "g", "b", "n", "m"}, "G2 packet shape changed")
    return investigation, g1, g2


def build_valid_g1_exchange(g1_root: Path) -> dict[str, Any]:
    helper = r'''
import json
from axm_p2p.invite import create_invite, decode_invite
from axm_p2p.udp import _mac

token = create_invite(
    game_id="axm.protocol-evolution.city-hold",
    build="bounded-control",
    host="127.0.0.1",
    port=29997,
    lifetime_seconds=600,
)
invite = decode_invite(token)
guest_nonce = "g1-valid-guest"
hello = {
    "t": "HELLO",
    "s": invite.session_id,
    "g": invite.game_id,
    "b": invite.build,
    "n": guest_nonce,
    "m": _mac(
        invite.session_key,
        "hello",
        invite.session_id,
        guest_nonce,
        invite.game_id,
        invite.build,
    ),
}
print(json.dumps({"token": token, "hello": hello}, sort_keys=True, separators=(",", ":")))
'''
    env = os.environ.copy()
    env["PYTHONPATH"] = str(g1_root)
    proc = subprocess.run(
        [sys.executable, "-c", helper],
        cwd=g1_root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        raise ReplayError("exact G1 donor could not construct a valid G1 exchange:\n" + proc.stdout)
    try:
        value = json.loads(proc.stdout.strip())
    except json.JSONDecodeError as exc:
        raise ReplayError("G1 helper did not emit valid JSON") from exc
    require(isinstance(value, dict), "G1 helper output must be an object")
    hello = value.get("hello")
    require(isinstance(hello, dict), "G1 helper did not emit a HELLO object")
    require(set(hello) == {"t", "s", "g", "b", "n", "m"}, "generated G1 HELLO shape drifted")
    require(hello.get("t") == "HELLO" and "pv" not in hello, "generated G1 HELLO is not generation-1 shaped")
    require(isinstance(value.get("token"), str) and value["token"], "G1 helper did not emit an invite token")
    return value


class FakeSocket:
    def __init__(self) -> None:
        self.sent: list[tuple[dict[str, Any], tuple[str, int]]] = []

    def sendto(self, payload: bytes, addr: tuple[str, int]) -> None:
        self.sent.append((json.loads(payload.decode("utf-8")), addr))


def run_g2_tests(g2_root: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(g2_root)
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_p2p.py", "-v"],
        cwd=g2_root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        raise ReplayError("pinned G2 donor handshake tests failed:\n" + proc.stdout)
    require("OK" in proc.stdout, "pinned G2 donor handshake tests did not report OK")


def replay(g1_root: Path, g2_root: Path) -> dict[str, Any]:
    investigation, _, _ = verify_research_state()
    verify_checkout(g1_root, G1_COMMIT, EXPECTED_G1_FILES, "G1")
    verify_checkout(g2_root, G2_COMMIT, EXPECTED_G2_FILES, "G2")

    g1_exchange = build_valid_g1_exchange(g1_root)
    g1_hello = g1_exchange["hello"]

    g2_src = str(g2_root)
    sys.path.insert(0, g2_src)
    try:
        from axm_p2p.invite import decode_invite  # type: ignore
        from axm_p2p.udp import HANDSHAKE_PROTOCOL_VERSION, P2PHost, _mac  # type: ignore

        require(HANDSHAKE_PROTOCOL_VERSION == 2, "G2 donor handshake protocol version is no longer 2")
        invite = decode_invite(g1_exchange["token"])
        host = P2PHost(invite)
        fake = FakeSocket()
        host._sock = fake

        g1_addr = ("127.0.0.1", 40101)
        host._handle(dict(g1_hello), g1_addr)
        require(host.peer_count == 0, "G2 host admitted a valid G1 HELLO")
        require(getattr(host, "_pending", None) == {}, "G2 host staged a valid G1 HELLO as pending G2 state")
        require(fake.sent == [], "G2 host replied to a valid G1 HELLO")
        require(host.wait_for_peer(timeout=0) is None, "G2 host emitted peer state for a valid G1 HELLO")

        g2_addr = ("127.0.0.1", 40102)
        g2_guest_nonce = "g2-control-guest"
        g2_hello = {
            "t": "HELLO",
            "pv": HANDSHAKE_PROTOCOL_VERSION,
            "s": invite.session_id,
            "g": invite.game_id,
            "b": invite.build,
            "n": g2_guest_nonce,
            "m": _mac(
                invite.session_key,
                "hello",
                str(HANDSHAKE_PROTOCOL_VERSION),
                invite.session_id,
                g2_guest_nonce,
                invite.game_id,
                invite.build,
            ),
        }
        host._handle(g2_hello, g2_addr)
        require(host.peer_count == 0, "G2 host admitted before ACK")
        require(len(getattr(host, "_pending", {})) == 1, "G2 host did not stage a valid G2 HELLO")
        require(len(fake.sent) == 1 and fake.sent[0][0].get("t") == "WELCOME", "G2 host did not emit WELCOME for valid G2 HELLO")

        welcome = fake.sent[0][0]
        ack = {
            "t": "ACK",
            "pv": HANDSHAKE_PROTOCOL_VERSION,
            "s": invite.session_id,
            "gn": g2_guest_nonce,
            "hn": welcome["hn"],
            "m": _mac(
                invite.session_key,
                "ack",
                str(HANDSHAKE_PROTOCOL_VERSION),
                invite.session_id,
                g2_guest_nonce,
                welcome["hn"],
            ),
        }
        host._handle(ack, g2_addr)
        require(host.peer_count == 1, "valid G2 ACK did not complete admission")
        require(host.wait_for_peer(timeout=0) is not None, "valid G2 ACK did not emit admitted peer state")
    finally:
        if sys.path and sys.path[0] == g2_src:
            sys.path.pop(0)
        for name in list(sys.modules):
            if name == "axm_p2p" or name.startswith("axm_p2p."):
                sys.modules.pop(name, None)

    run_g2_tests(g2_root)

    return {
        "schema": "axm.protocol-evolution.hold-path-execution-replay-result/v0.1",
        "valid": True,
        "investigation_id": investigation.get("id"),
        "status": "HOLD",
        "source_generation": "city-p2p-handshake-g1",
        "target_generation": "city-p2p-handshake-g2",
        "source_donor": {"repository": EXPECTED_REPOSITORY, "commit": G1_COMMIT},
        "target_donor": {"repository": EXPECTED_REPOSITORY, "commit": G2_COMMIT},
        "observations": {
            "g1_donor_generated_valid_hello": True,
            "g1_hello_has_protocol_version_field": False,
            "g2_replied_to_g1_hello": False,
            "g2_staged_g1_hello": False,
            "g2_admitted_g1_hello": False,
            "g2_control_welcome_observed": True,
            "g2_control_admitted_before_ack": False,
            "g2_control_admitted_after_valid_ack": True,
            "g2_donor_handshake_tests_passed": True,
        },
        "promotion": {
            "migration_path_admitted": False,
            "semantic_equivalence_proven": False,
            "chain_experiment_advanced": False,
            "universal_bridge_absence_proven": False,
        },
        "truth_boundary": [
            "This replay proves only that the exact admitted G2 host does not interpret one exact-donor-valid G1 HELLO as a G2 exchange while a G2 HELLO/ACK control succeeds.",
            "It does not prove that no G1-to-G2 adapter, dual-stack bridge, or translation could exist elsewhere or be built later.",
            "It does not prove production-network behavior or whole-game incompatibility.",
            "Adapter & Translation Garden remains the migration/translation implementation donor.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay City Multiplayer G1 HELLO against exact G2 host as executable HOLD evidence")
    parser.add_argument("--g1-donor-root", type=Path, required=True)
    parser.add_argument("--g2-donor-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = replay(args.g1_donor_root.resolve(), args.g2_donor_root.resolve())
    except (ReplayError, subprocess.CalledProcessError, OSError, ValueError, TypeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
