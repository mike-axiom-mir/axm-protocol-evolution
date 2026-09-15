# Action Report — Capability observation boundary

Date: 2026-09-15
Status at question definition: OPEN / falsifier defined before implementation

## Bounded question

Can Protocol Evolution's exact-capability negotiation distinguish **observed absence or version mismatch** from **missing capability evidence**, instead of labeling both `UNSUPPORTED`?

The real motivating donor pair is FrameState at two exact commits that expose the same canonical project schema generation (`axm.framestate.project/v0.5`) while differing in capability-discovery evidence:

- historical admitted-v0.5 donor commit `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34` has no `AXM_MODULE.json` capability descriptor at that commit;
- later donor commit `41c9c6827e64613b523b28536ab864dddf046d93` keeps `PROJECT_SCHEMA='axm.framestate.project/v0.5'` and adds `AXM_MODULE.json`, including the callable `timeline.integer-sample` capability contract.

The absence of a capability descriptor in the older snapshot is **not** evidence that the underlying capability was absent. Therefore treating an unobserved declaration as explicit incompatibility would violate truth-before-story.

## Falsifier

The improvement fails if any of these cases are accepted incorrectly:

1. a required capability missing from a side whose capability inventory is explicitly complete is not classified `UNSUPPORTED`;
2. a required capability present on both complete sides with conflicting versions is not classified `UNSUPPORTED`;
3. a required capability absent only because one side's capability evidence is incomplete is classified `UNSUPPORTED` rather than explicitly unjudged/ambiguous;
4. a capability shared at the same exact version is lost from the shared result merely because another required capability is unobserved;
5. existing callers that provide complete inventories change behavior without opting into the incomplete-evidence boundary;
6. the real FrameState historical/current observation is described as proof that the historical donor lacked the capability, rather than only proof that the declaration was not observed;
7. product/schema version equality is used as substitute capability evidence.

## Intended bounded change

- extend exact capability negotiation with explicit inventory-completeness inputs while preserving current defaults;
- separate `missing_required` (grounded unsupported) from `unobserved_required` (insufficient evidence);
- return `AMBIGUOUS` when required compatibility cannot be decided because an inventory is incomplete;
- retain exact-version matching and current `UNSUPPORTED` behavior for complete inventories and explicit version mismatches;
- add regressions for the falsifier cases;
- record a small machine-readable FrameState observation tying the rule to the exact donor commits above without promoting the observation into a historical generation or runtime claim.

## Truth / donor boundary

This is capability-evidence semantics only. It does not prove whether the historical FrameState snapshot could or could not perform `timeline.integer-sample`; it proves only that no `AXM_MODULE.json` declaration was observed at that exact commit while one exists at the later exact commit. It does not execute or duplicate Adapter & Translation Garden, create a migration, alter historical fixtures, grant CANON/install/network authority, or infer capability from project schema version.

## Root gate before implementation

- **Truth:** unknown evidence must remain unknown instead of being relabeled unsupported.
- **Agency / non-domination:** capability observation grants no execution or authority.
- **Continuity:** existing complete-inventory negotiation remains backward compatible; historical fixtures/source lineage stay untouched.
- **Wisdom before speed:** refine the semantic distinction before using capability negotiation against more real donors.
