# Action Report — Generation Lineage Readiness

Date: 2026-09-12  
Status: bounded research delta

## Question tested

Does a corpus of five real fixtures prove that AXM Protocol Evolution has one five-generation migration chain ready for chain-vs-direct comparison?

## Falsifier defined before implementation

The current corpus contains five fixtures but they are split across two semantic domains. If the readiness check reports a five-generation chain merely because the global fixture count is five, the experiment fails.

## Donor and repository state inspected

- `axm-protocol-evolution` main after receipt-chain continuity work;
- five admitted generation manifests;
- survivability matrix domain boundary;
- Adapter Translation Garden boundary remains implementation donor, not duplicated here.

## Exact delta

- added `fixtures/lineages.json` as a separate declaration of admitted research lineages without rewriting historical fixture manifests;
- added `analyze_generation_lineages()` to validate lineage membership and domain consistency;
- added `tools/lineage_readiness.py`;
- added checked-in `evidence/lineage_readiness.json` plus regression binding it to generated truth;
- added failures for cross-domain membership, unknown fixtures, duplicate membership, unassigned fixtures, malformed catalogs/manifests;
- corrected README wording so five fixtures are not described as one five-generation chain.

## Result

Current corpus:

- total fixtures: 5;
- declared lineages: 2;
- City Multiplayer handshake lineage: 2 admitted generations;
- FrameState project lineage: 3 admitted generations;
- longest declared lineage: 3;
- five-generation same-lineage chain ready: **NO**;
- current gap to a five-generation FrameState lineage: 2 admitted real generations.

The bounded new tests pass locally: **5/5**.

## Truth boundary

This analysis proves only declared fixture membership/count and domain consistency. It does not prove:

- that admitted fixtures represent every historical release;
- that releases are contiguous;
- that a migration path exists between adjacent admitted fixtures;
- that any migration executed;
- semantic equivalence across a chain;
- direct-vs-chain equivalence.

The ordering in `fixtures/lineages.json` is the ordering of admitted research fixtures, not a claim that skipped product versions did not exist.

## Root check

**Truth** — global fixture count is no longer allowed to masquerade as same-lineage chain length.

**Agency / non-domination** — this check grants no migration, donor, product, merge, user-data, or canon authority.

**Continuity** — existing historical fixture manifests and artifacts remain untouched; lineage declarations are additive evidence.

**Wisdom before speed** — the larger chain-vs-direct experiment remains HOLD until a real same-domain lineage is long enough and actual migration paths are evidenced.

## Next unresolved question

Find and admit real historical generations that extend one existing lineage, rather than padding the experiment with unrelated domains. Only after one lineage reaches five admitted generations should the repo attempt the intended five-generation chain-vs-direct experiment.
