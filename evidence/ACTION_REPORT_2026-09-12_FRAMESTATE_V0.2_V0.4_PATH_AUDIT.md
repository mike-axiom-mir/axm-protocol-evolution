# Action Report — FrameState v0.2 -> v0.4 adjacent-path audit

Date: 2026-09-12
Status: **HOLD / investigated, not admitted**

## Question

Does the historical FrameState v0.2 -> v0.4 transition contain enough evidence to admit an actual project-state migration path, rather than repository implementation recovery plus newer-reader compatibility with older project state?

## Falsifier defined before implementation

If the inspected donor history contains an explicit v0.2-project -> v0.4-project transformer, a migration receipt binding that transition, or a derived v0.4 target artifact tied to the admitted v0.2 source state, this HOLD conclusion is falsified and the edge must be reviewed for admission instead. Repository code evolving forward or a newer reader accepting older schemas is not sufficient by itself.

## Donor evidence inspected

Repository: `mike-axiom-mir/axm-framestate`

- admitted v0.2 source ref: `5d46363fb30bf5d30198b8cdec473d3bb9ba6287`;
- admitted v0.4 fixture source ref: `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`;
- bounded compare between those refs spans 148 commits;
- recovery commit `e33e4e8abb0e7a491f1af4d01c523cedda98bc4a` is explicitly titled `feat: recover and extend FrameState into usable v0.4 video machine`;
- the v0.4 changelog says the uncommitted v0.3 source body was lost and recovery rebuilt forward from the surviving v0.1 source archive, the safe GitHub v0.2 branch, and v0.3 evidence rather than claiming byte-for-byte resurrection;
- that same v0.4 record advertises canonical v0.4 project state with v0.1-v0.4 input compatibility;
- the inspected later canonical reader accepts the historical project schemas and preserves historical v0.4-and-earlier speech meaning.

## Result

The historical record establishes a real and important transition in the **FrameState implementation repository**: v0.4 was recovered/rebuilt forward using v0.2 source plus preserved evidence, and the resulting reader supports older project generations.

That is not the same claim as a demonstrated migration of the admitted v0.2 **project artifact/state** into a v0.4 project artifact/state.

Within this bounded scan, no explicit project-state transformer, migration receipt, or derived v0.4 target artifact bound to the admitted v0.2 project was identified. Therefore:

- `framestate-project-v0.2 -> framestate-project-v0.4` remains **not admitted** as a migration path;
- it is now recorded as **investigated / HOLD** rather than uninvestigated;
- `admitted_path_count` remains `0`;
- FrameState now has two investigated missing adjacent edges and one uninvestigated missing edge;
- v0.4 -> v0.5 is the only FrameState adjacent edge not yet audited;
- the five-generation chain-vs-direct experiment remains **HOLD**.

## Exact repository delta

- append the v0.2 -> v0.4 HOLD result to the migration-path investigation catalog;
- regenerate checked-in chain-experiment readiness so investigation counts and remaining gaps match the catalog;
- strengthen the corpus regression to require both HOLD investigations and the one remaining uninvestigated FrameState edge;
- update the README evidence boundary;
- preserve the migration-path admission catalog unchanged.

## Truth boundary

This report does **not** prove that no v0.2 -> v0.4 migrator can be written, that no transition evidence exists outside the bounded history inspected here, or that v0.2 projects cannot be consumed by later FrameState code. It proves only that implementation recovery and multi-version reader support are insufficient evidence for admitting an actual project-state migration path.

The readiness analyzer still does not independently authenticate evidence refs, execute migrations, prove semantic equivalence, or prove direct-vs-chain equivalence.

## Donor boundary

Adapter Translation Garden remains the migration/translation implementation donor. Protocol Evolution records semantic compatibility evidence and path-admission boundaries; it does not copy a migration generator/router or take execution authority from the donor.

## Root gate

**Truth** — repository recovery and backward reader compatibility are not relabeled as project-state migration.

**Agency / non-domination** — no donor repository is mutated and no migration, install, publish, device, or canon authority is taken.

**Continuity** — the prior HOLD record and empty admission catalog remain intact; the new evidence is additive and exact source refs are preserved.

**Wisdom before speed** — the edge remains HOLD instead of being promoted merely to advance the larger experiment.

## Next bounded question

Audit FrameState v0.4 -> v0.5. The donor changelog explicitly describes preservation behavior for older speech semantics under v0.5, so that edge may contain stronger transition evidence than the first two. It still requires inspection of the actual project-state behavior before any migration-path admission.
