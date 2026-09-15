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

## Planned bounded implementation

The replay will remain outside donor implementation ownership:

- CI will checkout the exact G1 and G2 donor commits separately;
- the replay will verify donor HEADs and bounded file Git blob identities;
- a subprocess using the exact G1 donor will create a live invite plus a correctly authenticated G1 HELLO using G1's own `_mac()` implementation;
- the exact G2 donor will decode that invite and receive the G1 HELLO through its own `P2PHost._handle()` path with a fake datagram socket;
- the replay will require zero G2 reply packets, zero pending handshakes, and zero admitted peers for the valid G1 message;
- a same-run G2 control will generate a protocol-v2 HELLO using the exact G2 donor, require WELCOME but no admission yet, then send a valid ACK and require exactly one admitted peer;
- the exact G2 donor `tests/test_p2p.py` suite will run as an independent regression control.

No migration/translation adapter will be copied or implemented here. The Connected Monolith is not used as privileged truth for this cycle.

## Evidence meaning and limitations

If the falsifier is not triggered, the result will establish executable negative evidence only for this exact admitted donor pair and handshake boundary: the exact G2 host does not interpret a valid G1 HELLO as a G2 exchange, while its own G2 exchange works under the same bounded test setup.

That would not prove universal absence of a bridge, production-network incompatibility, whole-game incompatibility, semantic equivalence, or impossibility of a future Adapter & Translation Garden bridge. It would not admit a migration path or advance the chain experiment.

## Root gate before implementation

- **Truth:** require exact donor identity and a positive G2 control so rejection cannot masquerade as a broken harness.
- **Agency / non-domination:** replay is read-only and grants no migration, install, publish, network, device, user-data, or CANON authority.
- **Continuity:** preserve historical fixtures, manifests, lineage, HOLD state, donor refs, and source history unchanged.
- **Wisdom before speed:** strengthen one unresolved edge with executable evidence rather than inventing a bridge merely to increase readiness.

Merge is permitted only if the implemented replay matches these boundaries and repository CI passes. Otherwise this cycle remains HOLD/open with the exact blocker recorded.
