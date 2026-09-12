# Action Report — FrameState v0.1 -> v0.2 adjacent-path audit

Date: 2026-09-12
Status: **HOLD / investigated, not admitted**

## Question

Does the historical FrameState v0.1 -> v0.2 transition contain enough evidence to admit an actual migration path, rather than merely newer-reader compatibility with older project state?

## Falsifier defined before implementation

If the only evidence is that the v0.2 reader accepts v0.1 input unchanged, the edge must remain missing. Reader compatibility must not increment `admitted_path_count`, complete the adjacent-path catalog, or make a lineage chain-experiment-ready.

## Donor evidence inspected

Repository: `mike-axiom-mir/axm-framestate`

- v0.1 admitted source ref: `5b5f73cb78667d9af981af3b38cd7a7ce3a5dab7`
- v0.2 admitted source ref: `5d46363fb30bf5d30198b8cdec473d3bb9ba6287`
- compare range: v0.2 is two commits ahead of the admitted v0.1 ref; the intervening commit is `test: align effect engine bytes with verified local build`
- v0.2 changelog: explicitly says `v0.2 canonical schema alongside v0.1 compatibility`
- v0.2 `canonical.py`: accepts both `axm.framestate.project/v0.1` and `/v0.2`
- v0.2 `normalize_project`: returns the input `schema` value rather than rewriting a v0.1 project as v0.2

## Result

The inspected historical evidence proves a useful but narrower fact: **FrameState v0.2 can read/normalize v0.1 project state while preserving its v0.1 schema identity.**

That is backward reader compatibility. It is not evidence that a v0.1 artifact was transformed into a v0.2 artifact.

No explicit transformer, migration receipt, or derived v0.2 target artifact for the admitted v0.1 fixture was found in this bounded history scan. Therefore:

- `framestate-project-v0.1 -> framestate-project-v0.2` remains **not admitted** as a migration path;
- `admitted_path_count` remains `0`;
- the FrameState lineage remains missing all three adjacent migration-path admissions;
- the five-generation chain-vs-direct experiment remains **HOLD**.

## Exact repository delta

- added an append-only migration-path investigation catalog;
- recorded this edge as `HOLD` with exact donor evidence refs and blocker;
- extended chain readiness to distinguish investigated missing edges from uninvestigated missing edges;
- added regressions proving an investigation can never masquerade as an admission;
- advanced the chain-readiness result schema to v0.2 because its evidence surface changed.

## Truth boundary

This report does **not** prove that no v0.1 -> v0.2 migrator could ever be written or that no additional historical evidence exists outside the bounded donor range inspected here. It proves only that the inspected evidence is insufficient for migration-path admission.

The analyzer still does not independently fetch or authenticate evidence refs, execute migrations, prove semantic equivalence, or prove direct-vs-chain equivalence.

## Donor boundary

Adapter Translation Garden remains the migration/translation implementation donor. This repository records compatibility evidence and admission boundaries; it does not copy or seize implementation authority from that donor.

## Root gate

**Truth** — compatibility is not relabeled as migration, and negative evidence remains visible.

**Agency / non-domination** — no donor data, migration, canon, install, device, or network authority is taken.

**Continuity** — the existing empty admission catalog is preserved; this audit is additive and source refs remain exact.

**Wisdom before speed** — the first adjacent edge stays HOLD instead of being admitted to make the larger experiment advance faster.

## Next bounded question

Audit the next real FrameState adjacent edge, v0.2 -> v0.4, with the same rule: admit only if there is evidence of an actual transition into the target generation, not merely multi-version reader support.
