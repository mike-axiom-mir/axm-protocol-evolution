# Action Report — FrameState v0.1 -> v0.2 HOLD replay

Date: 2026-09-15

## Bounded question

Can the existing FrameState v0.1 -> v0.2 `HOLD` be upgraded from source-inspection evidence to reproducible executable evidence by replaying the admitted v0.1 historical fixture through the exact pinned v0.2 donor reader/normalizer, without turning reader compatibility into a migration-path admission?

## Falsifier — defined before implementation

This cycle must fail closed or force the existing HOLD to be reconsidered if any of the following occurs:

1. the donor checkout is not exactly `mike-axiom-mir/axm-framestate@5d46363fb30bf5d30198b8cdec473d3bb9ba6287`;
2. the donor `src/axm_framestate/canonical.py` or bounded donor test file no longer matches the pinned Git blob identities observed at that commit;
3. the admitted Protocol Evolution v0.1 fixture no longer matches its historical source blob / manifest identity;
4. the exact v0.2 donor cannot normalize the admitted v0.1 fixture;
5. normalization mutates the admitted source object;
6. the replay output changes the source schema from `axm.framestate.project/v0.1` to `axm.framestate.project/v0.2` (or any other schema), because that would be evidence of a state transformation and the current reader-compatibility-only HOLD would need review;
7. the replay output is not deterministic across two runs;
8. the pinned donor's bounded test suite fails;
9. any new evidence is used to claim migration-path admission, whole-project semantic equivalence, chain readiness, CANON authority, or Adapter & Translation Garden ownership.

The expected result, based on the already-inspected v0.2 donor source, is narrower: the v0.2 normalizer accepts the v0.1 project and returns canonicalized state while preserving the input `schema` value. If reproduced, that strengthens the existing negative distinction: **executable backward reader compatibility is still not an adjacent migration.**

## Grounded starting state

- Existing investigation: `framestate-v0.1-to-v0.2-audit-2026-09-12`, status `HOLD`.
- Admitted historical source generation: `framestate-project-v0.1`, pinned to `5b5f73cb78667d9af981af3b38cd7a7ce3a5dab7`, `examples/first_light.json`, Git blob `3a6f64e8f0355812360abd0546f2b997cdb0db28`.
- Target donor checkpoint: `framestate-project-v0.2`, source ref `5d46363fb30bf5d30198b8cdec473d3bb9ba6287`.
- At that exact v0.2 checkpoint, `normalize_project()` accepts both v0.1 and v0.2 project schemas and returns the incoming `schema` rather than rewriting it to v0.2.
- The existing chain experiment remains blocked and FrameState v0.1 -> v0.2 has no admitted migration path.

## Planned bounded improvement

Add one exact-donor CI replay for this HOLD edge. The replay will:

- verify exact donor HEAD and donor file Git blobs;
- verify the admitted v0.1 fixture identity;
- import and execute the donor's own `normalize_project()` from the external checkout;
- run the same input twice and require exact deterministic equality;
- require source-object immutability;
- require the output schema to remain v0.1;
- run the pinned donor test module;
- emit explicit non-promotion boundaries.

No donor migration/adapter implementation will be copied into Protocol Evolution. The Connected Monolith is not needed as a truth source for this replay.

## Root gate before implementation

- **Truth:** executable behavior must decide whether the source-inspection HOLD description is accurate.
- **Agency / non-domination:** replay is read-only and grants no migration/install/publish/CANON authority.
- **Continuity:** historical fixtures, manifests, lineage, HOLD records, and prior admissions remain unchanged.
- **Wisdom before speed:** strengthen one existing unresolved edge with execution before seeking a larger chain.

Implementation and merge are permitted only if the replay result matches the bounded claim and repository CI remains green.