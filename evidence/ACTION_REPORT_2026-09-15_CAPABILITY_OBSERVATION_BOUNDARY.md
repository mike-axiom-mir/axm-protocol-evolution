# Action Report — Capability observation boundary

Date: 2026-09-15
Status: IMPLEMENTED / root-gated pending merge

## Bounded question

Can Protocol Evolution's exact-capability negotiation distinguish **observed absence or version mismatch** from **missing capability evidence**, instead of labeling both `UNSUPPORTED`?

The real motivating donor pair is FrameState at two exact commits that expose the same canonical project schema generation (`axm.framestate.project/v0.5`) while differing in capability-discovery evidence:

- historical admitted-v0.5 donor commit `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34` has no `AXM_MODULE.json` capability descriptor at that commit;
- later donor commit `41c9c6827e64613b523b28536ab864dddf046d93` keeps `PROJECT_SCHEMA='axm.framestate.project/v0.5'` and adds `AXM_MODULE.json`, including the callable `timeline.integer-sample` capability contract.

The absence of a capability descriptor in the older snapshot is **not** evidence that the underlying capability was absent. Therefore treating an unobserved declaration as explicit incompatibility would violate truth-before-story.

## Falsifier defined before implementation

The improvement fails if any of these cases are accepted incorrectly:

1. a required capability missing from a side whose capability inventory is explicitly complete is not classified `UNSUPPORTED`;
2. a required capability present on both sides with conflicting observed versions is not classified `UNSUPPORTED`;
3. a required capability absent only because one side's capability evidence is incomplete is classified `UNSUPPORTED` rather than explicitly unjudged/ambiguous;
4. a capability shared at the same exact version is lost from the shared result merely because another required capability is unobserved;
5. existing callers that provide complete inventories change behavior without opting into the incomplete-evidence boundary;
6. the real FrameState historical/current observation is described as proof that the historical donor lacked the capability, rather than only proof that the declaration was not observed;
7. product/schema version equality is used as substitute capability evidence.

## Implemented delta

- `negotiate_capabilities()` now accepts optional `left_complete` and `right_complete` evidence-boundary flags, both defaulting to `True` so existing callers retain complete-inventory behavior.
- Exact shared capability/version pairs are unchanged.
- Grounded required absence and observed version mismatch produce `UNSUPPORTED` and are reported through `missing_required`; observed mismatches are also exposed through `version_mismatches`.
- A required capability absent from an explicitly incomplete inventory is reported through `unobserved_required` and produces `AMBIGUOUS` unless stronger observed incompatibility exists.
- Four focused regressions cover incomplete evidence, complete absence, observed version mismatch, and preservation of an exact shared capability alongside another unobserved requirement.
- `CAPABILITY_NEGOTIATION.md` records the exact FrameState donor observation and the boundary that same schema version is not capability evidence.

A separate machine-readable donor observation was **not** added. That would have introduced another retained evidence artifact without an external replay gate. The exact donor identities and narrow observation are instead retained in this Action Report and the capability-negotiation documentation; future work should add machine-readable donor evidence only when it can be independently replayed or otherwise justified.

## Verification

PR-head GitHub Actions passed:

- repository `verify` workflow: **success**, including the Python 3.11 / 3.12 / 3.13 foundation jobs and the existing exact-donor replay jobs;
- `replay-framestate-v02-future-field`: **success**.

The final overlap scan found no competing Protocol Evolution lane, and `main` remained at `968c87ca8f1f40446ba3aa872ad3c947188fdb33`, the branch base.

## Truth / donor boundary

This is capability-evidence semantics only. It does not prove whether the historical FrameState snapshot could or could not perform `timeline.integer-sample`; it proves only that no `AXM_MODULE.json` declaration was observed at that exact commit while one exists at the later exact commit. It does not execute or duplicate Adapter & Translation Garden, create a migration, alter historical fixtures, grant CANON/install/network authority, or infer capability from project schema version.

`AMBIGUOUS` means evidence is insufficient for the required capability comparison; it does not mean the systems are probably compatible. `UNSUPPORTED` remains reserved here for an observed mismatch or absence within a declared complete inventory.

## Root gate

- **Truth:** unknown evidence remains unknown rather than being relabeled unsupported; explicit absence/mismatch still fails closed.
- **Agency / non-domination:** capability observation grants no execution or authority.
- **Continuity:** complete-inventory negotiation remains backward compatible; historical fixtures/source lineage stay untouched.
- **Wisdom before speed:** the evidence distinction is made before expanding capability negotiation to more real donors.

Root result: **PASS for this bounded change**, contingent on merging the tested head without drift.
