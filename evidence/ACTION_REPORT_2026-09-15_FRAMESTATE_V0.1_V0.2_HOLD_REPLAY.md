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

## Implemented bounded improvement

An exact-donor replay now:

- verifies exact donor HEAD and the pinned Git blobs for `canonical.py` and `test_machine.py`;
- verifies the admitted v0.1 fixture against its historical manifest/source blob;
- imports and executes the donor's own `normalize_project()` from the external checkout;
- runs the same input twice and requires exact deterministic equality;
- requires source-object immutability;
- requires the output schema to remain v0.1 rather than becoming v0.2;
- preserves the admitted v0.1 tone-only semantic claim;
- runs the pinned donor `test_machine.py` suite;
- emits explicit non-promotion boundaries.

No donor migration/adapter implementation is copied into Protocol Evolution. The Connected Monolith is not used as a truth source for this replay.

## Observed result

The pull-request CI run on head `97f385b797982ea43722e6ab875e386a91de32fd` passed the new exact-donor replay job. Because the replay script fails closed on each falsifier above, that successful job grounds the following bounded observation for this exact fixture/donor pair:

- the exact v0.2 donor accepted the admitted historical v0.1 fixture;
- the source object remained unchanged;
- two executions were exactly equal;
- the observed normalized output remained schema `axm.framestate.project/v0.1`, not v0.2;
- the tone-only source meaning remained intact;
- the pinned donor test module completed successfully.

The repository-wide foundation/evidence matrix also passed on Python 3.11, 3.12, and 3.13, and the existing exact-donor v0.4 -> v0.5 replay remained green.

## Evidence meaning and limitations

This is now **executable negative evidence** for the current migration question: the newer v0.2 implementation can read/canonicalize this exact v0.1 state, but the observed operation does not transform it into v0.2 state. Therefore the v0.1 -> v0.2 edge remains `HOLD`; no migration path is admitted.

This does not prove that no v0.1 -> v0.2 migrator could exist elsewhere or be built later. It does not prove whole-project semantic equivalence, chain-vs-direct equivalence, or chain-experiment readiness. It grants no CANON, migration, install, publish, network, device, or user-data authority. Adapter & Translation Garden remains the migration/translation implementation donor.

## Root gate after observation

- **Truth:** the executable result agrees with the existing HOLD distinction and does not get relabeled as migration.
- **Agency / non-domination:** replay is read-only and grants no new authority.
- **Continuity:** historical fixtures, manifests, lineage, HOLD records, and prior admissions remain unchanged.
- **Wisdom before speed:** one unresolved edge gained stronger evidence without lowering the admission gate.

The four roots support merging this bounded replay/evidence improvement while keeping the edge on HOLD.