# Action Report — City Multiplayer G1 -> G2 Path Audit

Date: 2026-09-12

Status: **HOLD / investigated, not admitted**

## Bounded question

Does the admitted City Multiplayer handshake generation 1 -> generation 2 edge contain an actual compatibility or migration bridge, rather than only historical replacement of the handshake implementation?

## Falsifier defined before implementation

The HOLD hypothesis is falsified if the inspected donor history contains evidence that accepts G1 handshake semantics and deterministically upgrades or translates them into G2, a dual-stack negotiation/interoperability bridge that preserves admission meaning, an adapter or migration receipt bound to the admitted G1 fixture, a derived G2 exchange tied to that fixture, or an equivalent regression demonstrating G1 interoperability through the G2 implementation.

A repository code change from the old handshake to the new handshake is not sufficient by itself.

## Donor evidence inspected

- G1 admitted source: `d3b1bfb79d4e997781037ce0723c193be5f5df7a` — authenticated direct UDP join handshake.
- G2 semantic transition: `a260196340d706a9d5fda9cedb143f50873bca48` — requires guest ACK before host admission and introduces handshake protocol version 2.
- Matching regression: `558f0fdeba9d41d8e9a45a0ca1b08e53dca84409` — proves HELLO/WELCOME alone does not admit a peer and protocol version 1 is rejected by the v2 host.
- G2 admitted fixture source: `241c613b58cf624bb852d84aba1136f2f61e91f3`.
- Bounded donor compare: G1 source -> G2 source spans 37 commits.

## Findings

Generation 1 admits the host-side peer after the authenticated HELLO/WELCOME exchange. It has no explicit handshake protocol-version field and requires no guest ACK.

The later transition adds `HANDSHAKE_PROTOCOL_VERSION = 2`, includes the protocol version in authenticated messages, stores the HELLO/WELCOME state as pending, and admits the host-side peer only after an authenticated ACK. The matching regression also constructs a protocol-version-1 HELLO and verifies that the v2 host sends no response, creates no pending state, and admits no peer.

That is grounded evidence of a real semantic protocol boundary. It is not evidence of a bridge from G1 into G2.

## Result

**HOLD. Do not admit City G1 -> G2 as a migration path.**

No dual-stack negotiation, packet/state transformer, adapter, migration receipt, or derived G2 exchange bound to the admitted G1 fixture was identified in the bounded donor scan. The inspected G2 implementation explicitly rejects the older protocol version, so repository implementation evolution cannot be relabeled as migration evidence.

## Repository improvement

- appended the City G1 -> G2 HOLD investigation without rewriting prior investigations;
- regenerated chain-experiment readiness so the City edge is now `investigated missing`, not `uninvestigated missing`;
- kept admitted migration-path count at 1;
- added a regression requiring the exact City investigation state;
- documented the protocol-replacement-versus-migration boundary in the README.

All currently declared missing adjacent edges are now investigated, but investigation does not grant admission.

## Limitations

This bounded audit does not prove that no compatibility bridge could ever be written or exist elsewhere. It does not execute either donor handshake generation, prove real-network interoperability, prove semantic equivalence, or authenticate every evidence reference independently.

Adapter & Translation Garden remains the implementation donor. No adapter generator, migration router, or translation implementation was copied into Protocol Evolution; module 030 remains a `decision_only` migration-generator prototype in the donor system.

## AXM root gate

**Truth:** a protocol replacement that rejects its predecessor is not called a migration path merely because it occurs later in Git history.

**Agency / non-domination:** this audit takes no donor, user-data, install, publish, device, network, canon, or execution authority.

**Continuity:** historical fixtures, source refs, lineage order, admitted paths, and earlier HOLD records remain intact. The negative evidence is additive.

**Wisdom before speed:** the City edge stays HOLD rather than inflating path count to make the larger chain experiment appear closer to readiness.

## Next bounded question

The five-generation chain experiment remains blocked by lineage length and missing admitted paths. A useful next cycle should investigate whether a genuine fifth FrameState generation can be grounded from preserved historical evidence without reconstructing the lost v0.3 source, or choose another small semantic-compatibility prerequisite if that cannot be grounded.
