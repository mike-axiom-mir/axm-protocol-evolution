# Action Report — FrameState v0.2 -> v0.4 HOLD replay

Date: 2026-09-15
Status: **FALSIFIER DEFINED / implementation not yet claimed**

## Bounded question

Can the existing FrameState v0.2 -> v0.4 `HOLD` be strengthened with reproducible executable evidence by replaying the admitted historical v0.2 fixture through the exact donor snapshot named by the admitted v0.4 generation, without confusing later-reader normalization or repository recovery with an adjacent v0.2 -> v0.4 migration?

## Falsifier — defined before implementation

This cycle must fail closed or force the existing HOLD to be reconsidered if any of the following occurs:

1. the donor checkout is not exactly `mike-axiom-mir/axm-framestate@60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`;
2. the bounded donor implementation/test files no longer match their pinned Git blob identities at that commit;
3. the admitted Protocol Evolution v0.2 source fixture no longer matches its historical manifest/source blob identity;
4. the target v0.4 manifest no longer points to the expected donor repository/ref or its preserved artifact no longer has schema `axm.framestate.project/v0.4`;
5. the exact donor cannot normalize the admitted v0.2 fixture;
6. normalization mutates the admitted source object or produces nondeterministic output across repeated runs;
7. the replay emits schema `axm.framestate.project/v0.4`, because that would be direct executable evidence of an adjacent target-schema transformation and the existing HOLD would require review for possible admission;
8. the replay loses the admitted v0.2 `undeclared_speech_engine=espeak` meaning;
9. the bounded pinned donor regression fails;
10. any result is promoted into whole-project semantic equivalence, chain-vs-direct equivalence, chain readiness, CANON authority, or Adapter & Translation Garden ownership without separate evidence.

The expected narrow result from the already-inspected donor is that this exact later checkpoint accepts historical project schemas but canonicalizes them to its then-current project schema rather than deriving the preserved v0.4 target generation. If execution reproduces that behavior while preserving the v0.2 speech meaning, it strengthens the current distinction: **a later implementation consuming old state is not evidence of the missing adjacent v0.2 -> v0.4 migration.**

## Grounded starting state

- Existing investigation: `framestate-v0.2-to-v0.4-audit-2026-09-12`, status `HOLD`.
- Admitted source generation: `framestate-project-v0.2`, pinned to `5d46363fb30bf5d30198b8cdec473d3bb9ba6287`, `examples/narrated_motion.json`, Git blob `cf6568ff0cb7384d03f3e7f807670e06e34e9820`.
- Admitted target generation: `framestate-project-v0.4`, whose manifest points to donor ref `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34` and preserves a v0.4 project artifact.
- At that exact donor ref, `src/axm_framestate/canonical.py` has Git blob `c44122ce84a238587ee263ca4df95be762992f6e` and accepts project schemas v0.1 through v0.5 while emitting the donor's current canonical schema.
- The historical audit records repository recovery/rebuild plus multi-version reader support, not a demonstrated v0.2-project -> v0.4-project transformer.
- The chain experiment remains blocked and this edge has no admitted migration path.

## Donor / authority boundary

Adapter & Translation Garden remains the migration/translation implementation donor. Protocol Evolution may execute pinned donor code as bounded evidence but must not copy or recreate a migration generator/router here. The Connected Monolith is not a privileged truth source and is not required for this replay.

Historical fixtures, manifests, lineages, existing path admission, and HOLD records must remain unchanged in this cycle unless the falsifier produces evidence that requires explicit review rather than silent promotion.
