# Action Report — City Multiplayer G1 -> G2 executable HOLD replay

Date: 2026-09-15

## Bounded question

Can the existing City Multiplayer `G1 -> G2` migration-path `HOLD` be upgraded from source/history inspection to reproducible executable negative evidence by presenting a valid generation-1 HELLO to the exact admitted generation-2 donor host, while also proving that a valid generation-2 HELLO/ACK can complete admission under the same target implementation?

This asks whether the inspected boundary is an executable protocol replacement rather than a hidden compatibility bridge. It does not ask Protocol Evolution to build that bridge.

## Falsifier — defined before implementation

This cycle must fail closed or force the existing HOLD to be reconsidered if any of the following occurs:

1. either donor checkout is not exactly `mike-axiom-mir/axm-city-multiplayer` at the admitted G1 ref `d3b1bfb79d4e997781037ce0723c193be5f5df7a` or admitted G2 ref `241c613b58cf624bb852d84aba1136f2f61e91f3`;
2. the bounded donor handshake files no longer match their pinned Git blob identities;
3. the Protocol Evolution G1/G2 manifests no longer declare protocol version 1 / WELCOME admission without ACK versus protocol version 2 / ACK admission;
4. the exact G1 donor cannot produce a valid G1 HELLO bound to an invite accepted by the exact G2 donor;
5. the exact G2 host replies to, stages, or admits that valid G1 HELLO;
6. the exact G2 host cannot complete its own HELLO -> WELCOME -> authenticated ACK admission path under the same invite/control setup;
7. the pinned G2 donor handshake regression suite fails;
8. any executable rejection result is relabeled as proof that no bridge can ever exist, whole-system incompatibility, semantic equivalence, migration-path admission, chain readiness, CANON authority, or ownership of Adapter & Translation Garden.

The expected result from the already-inspected donor source is narrower: a valid G1 HELLO has no generation-2 protocol version field and uses the generation-1 MAC transcript, while the G2 host requires protocol version 2 and ACK-before-admission. If the exact G1 message is rejected while a same-run G2 control admits successfully, that strengthens the existing finding that the inspected boundary is an executable replacement/incompatibility boundary, not an observed G1 -> G2 migration bridge.

## Grounded starting state

- Existing investigation: `city-p2p-g1-to-g2-audit-2026-09-12`, status `HOLD`.
- Admitted G1 generation: `city-p2p-handshake-g1`, source ref `d3b1bfb79d4e997781037ce0723c193be5f5df7a`, semantic claims `protocol_version=1`, `admission_proof=WELCOME`, `ack_required=false`.
- Admitted G2 generation: `city-p2p-handshake-g2`, source ref `241c613b58cf624bb852d84aba1136f2f61e91f3`, semantic claims `protocol_version=2`, `admission_proof=ACK`, `ack_required=true`.
- Exact G1 donor `axm_p2p/udp.py` admits a peer after authenticated HELLO and WELCOME without an ACK phase.
- Exact G2 donor `axm_p2p/udp.py` requires `HANDSHAKE_PROTOCOL_VERSION = 2`, rejects a HELLO whose `pv` is not 2 before creating pending state, and admits only after an authenticated ACK.
- The G2 donor regression `tests/test_p2p.py` includes both ACK-before-admission and wrong-handshake-version rejection checks.
- No City G1 -> G2 migration path is admitted. The existing HOLD records no dual-stack negotiation, packet/state transformer, adapter, receipt, or derived G2 exchange bound to the G1 fixture.

## Implemented bounded improvement

The replay stays outside donor implementation ownership:

- CI checks out the exact G1 and G2 donor commits separately;
- the replay verifies donor HEADs and bounded file Git blob identities;
- a subprocess using the exact G1 donor creates a live invite plus a correctly authenticated G1 HELLO using G1's own `_mac()` implementation;
- the exact G2 donor decodes that invite and receives the G1 HELLO through its own `P2PHost._handle()` path with a fake datagram socket;
- the replay requires zero G2 reply packets, zero pending handshakes, and zero admitted peers for the valid G1 message;
- a same-run G2 control generates a protocol-v2 HELLO using the exact G2 donor, requires WELCOME but no admission yet, then sends a valid ACK and requires exactly one admitted peer;
- the exact G2 donor `tests/test_p2p.py` suite runs as an independent regression control.

No migration/translation adapter is copied or implemented here. The Connected Monolith is not used as privileged truth for this cycle.

## Observed result

Pull-request CI on head `50192ee3e922a2104ebcf4a51502e524b3aa40f5` passed all six jobs in workflow run `34962796240`:

- foundation verification on Python 3.11;
- foundation verification on Python 3.12;
- foundation verification on Python 3.13;
- exact-donor FrameState v0.4 -> v0.5 replay;
- exact-donor FrameState v0.1 -> v0.2 HOLD replay;
- the new exact-donor City G1 -> G2 HOLD replay.

The City replay itself returned `valid: true` and observed all of the bounded expected outcomes:

- the exact G1 donor generated a correctly authenticated G1 HELLO;
- that HELLO had no protocol-version field, matching generation 1;
- the exact admitted G2 host sent no reply to the G1 HELLO;
- the G2 host created no pending handshake for it;
- the G2 host admitted no peer from it;
- the same G2 host did send WELCOME for a valid generation-2 HELLO;
- it did not admit the generation-2 control before ACK;
- it admitted the generation-2 control after a valid authenticated ACK;
- the pinned G2 donor handshake regression suite passed.

No falsifier was triggered. This upgrades the existing City G1 -> G2 finding from source/history inspection to reproducible **executable negative evidence** for this exact donor pair: the admitted G2 host does not interpret a valid exact-donor G1 HELLO as a generation-2 exchange, while its own generation-2 exchange succeeds in the same harness.

## Evidence meaning and limitations

The City edge remains `HOLD`. This replay does not admit a migration path and does not advance chain-experiment readiness.

It does not prove universal absence of a bridge, production-network incompatibility, whole-game incompatibility, semantic equivalence, or impossibility of a future Adapter & Translation Garden bridge. The executable rejection is evidence about the exact admitted donor boundary, not a theorem about every possible translator or future implementation.

## Root gate after observation

- **Truth:** exact donor identities and a successful G2 positive control rule out treating a broken harness as incompatibility evidence; the observed G1 rejection is reported only at the tested boundary.
- **Agency / non-domination:** replay is read-only and grants no migration, install, publish, network, device, user-data, or CANON authority.
- **Continuity:** historical fixtures, manifests, lineage, HOLD state, donor refs, prior admissions, and source history remain unchanged.
- **Wisdom before speed:** one unresolved edge gained reproducible executable evidence without inventing a bridge merely to increase readiness.

The four roots support merging this bounded replay/evidence improvement while keeping the City G1 -> G2 edge on HOLD.
