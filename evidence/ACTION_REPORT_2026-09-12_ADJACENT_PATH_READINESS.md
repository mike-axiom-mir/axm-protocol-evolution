# Action Report — Adjacent migration-path readiness

Date: 2026-09-12
Status: MERGE CANDIDATE / BOUNDED RESEARCH DELTA

## Question tested

Can a same-domain lineage become eligible for the five-generation chain-vs-direct experiment from generation count alone, without evidence for every adjacent migration path?

## Falsifier defined before implementation

A five-generation lineage with zero admitted adjacent migration-path evidence must remain **not input-ready**. A declared path that skips an admitted generation (for example G1 -> G3 when G2 sits between them) must be rejected as evidence for adjacent-chain readiness.

If either condition is accepted, the readiness gate is misleading and this delta fails.

## Donors and current state inspected

- `axm-protocol-evolution` main, newest commits, open PRs, fixture corpus, lineage analyzer and evidence outputs.
- Adapter & Translation Garden remains the migration/translation implementation donor; no adapter generation or migration execution was copied here.
- FrameState history was checked before trying to fill the remaining lineage slot. Its own changelog states that the uncommitted v0.3 source body was lost and only v0.3 evidence documents survived; v0.4 was rebuilt forward rather than claiming byte-for-byte resurrection. Therefore this cycle does **not** fabricate or admit v0.3 as the fifth executable generation.

## Exact delta

- add `fixtures/migration_paths.json` as an explicit admission catalog;
- add `analyze_chain_experiment_readiness()` to enumerate required adjacent edges and reject non-adjacent/duplicate/unreferenced path admissions;
- add a CLI evidence generator;
- add checked-in `evidence/chain_experiment_readiness.json`;
- add regressions for the falsifier and failure boundaries;
- add CI generation/JSON validation for the new readiness evidence.

## Current measured result

The corpus has six fixtures, but the longest declared lineage is FrameState at four generations. No adjacent migration path is currently admitted.

Current required adjacent path gaps:

- City Multiplayer: G1 -> G2 (1 missing path);
- FrameState: v0.1 -> v0.2, v0.2 -> v0.4, v0.4 -> v0.5 (3 missing paths).

Therefore `chain_experiment_input_ready` remains **false**.

## Truth boundary

A path admission is a reviewed catalog entry with explicit evidence references. This analyzer does not independently fetch or validate those references. Even when all required path admissions eventually exist, this layer will still report that it has **not** proved migration execution, semantic equivalence, or chain-vs-direct equivalence.

The word `input-ready` means only that the declared lineage length and admitted adjacent-path prerequisites are present for the experiment to begin.

## Root check

**Truth** — missing paths are explicit; v0.3 is not reconstructed from evidence-only history; path count cannot masquerade as execution proof.

**Agency / non-domination** — no donor data is migrated, rewritten, installed, promoted or made canonical.

**Continuity** — historical fixtures and lineage ordering remain unchanged; the new catalog is additive.

**Wisdom before speed** — formalize the missing prerequisite before attempting a five-generation experiment that current evidence cannot support.

## What remains unknown

- whether any current adjacent FrameState pair has a real migration path suitable for admission;
- whether reader compatibility should ever count as migration-path evidence (not assumed here);
- whether a fifth grounded FrameState executable generation can be admitted without inventing lost v0.3 source;
- whether an eventual multi-step chain is semantically equivalent to a direct migration.
