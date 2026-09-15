# Action Report — FrameState v0.2 -> v0.4 HOLD replay

Date: 2026-09-15
Status: **HOLD / executable negative evidence reproduced**

## Bounded question

Can the existing FrameState v0.2 -> v0.4 `HOLD` be strengthened with reproducible executable evidence by replaying the admitted historical v0.2 fixture through the exact donor snapshot named by the admitted v0.4 generation, without confusing later-reader normalization or repository recovery with an adjacent v0.2 -> v0.4 migration?

## Falsifier — defined before implementation

This cycle was required to fail closed or force the existing HOLD to be reconsidered if any of the following occurred:

1. the donor checkout was not exactly `mike-axiom-mir/axm-framestate@60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`;
2. the bounded donor implementation/test files no longer matched their pinned Git blob identities at that commit;
3. the admitted Protocol Evolution v0.2 source fixture no longer matched its historical manifest/source blob identity;
4. the target v0.4 manifest no longer pointed to the expected donor repository/ref or its preserved artifact no longer had schema `axm.framestate.project/v0.4`;
5. the exact donor could not normalize the admitted v0.2 fixture;
6. normalization mutated the admitted source object or produced nondeterministic output across repeated runs;
7. the replay emitted schema `axm.framestate.project/v0.4`, because that would be direct executable evidence of an adjacent target-schema transformation and the existing HOLD would require review for possible admission;
8. the replay lost the admitted v0.2 `undeclared_speech_engine=espeak` meaning;
9. the bounded pinned donor regression failed;
10. any result was promoted into whole-project semantic equivalence, chain-vs-direct equivalence, chain readiness, CANON authority, or Adapter & Translation Garden ownership without separate evidence.

The falsifier was committed before the replay implementation.

## Grounded starting state

- Existing investigation: `framestate-v0.2-to-v0.4-audit-2026-09-12`, status `HOLD`.
- Admitted source generation: `framestate-project-v0.2`, pinned to `5d46363fb30bf5d30198b8cdec473d3bb9ba6287`, `examples/narrated_motion.json`, Git blob `cf6568ff0cb7384d03f3e7f807670e06e34e9820`.
- Admitted target generation: `framestate-project-v0.4`, whose manifest points to donor ref `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34` and preserves a v0.4 project artifact.
- At that exact donor ref, `src/axm_framestate/canonical.py` has Git blob `c44122ce84a238587ee263ca4df95be762992f6e` and `tests/test_speech.py` has Git blob `e263a996d0f91ddd922e26fbda19150de3a941b0`.
- The historical audit records repository recovery/rebuild plus multi-version reader support, not a demonstrated v0.2-project -> v0.4-project transformer.
- The chain experiment remains blocked and this edge has no admitted migration path.

## Implemented bounded improvement

`tools/replay_framestate_v02_v04_hold.py` now:

- verifies the exact donor HEAD and pinned implementation/test Git blobs;
- verifies the existing HOLD record and source/target generation identities;
- verifies the admitted v0.2 fixture byte identity and undeclared-speech semantic claim;
- verifies the preserved v0.4 target artifact remains an actual v0.4 generation;
- imports and executes the external donor's own `normalize_project()` without copying migration implementation into this repository;
- runs the admitted v0.2 input twice, requiring deterministic equality and source-object immutability;
- fails if the donor emits the adjacent target schema v0.4;
- requires the actually observed donor-canonical schema v0.5;
- requires historical undeclared speech to materialize as `engine=espeak`;
- runs the exact pinned donor `test_speech.py` suite;
- emits explicit non-promotion fields.

The repository workflow now executes this replay from an exact external FrameState checkout on every verification run.

## Observed result

Pull-request CI on head `609eabc1e0d163d27e153fe3d4ff3a5237e7ed74` completed successfully. The dedicated `replay-framestate-v02-v04-hold` job passed, including exact donor checkout, identity checks, the replay, and the bounded donor speech regression.

Because the replay script fails closed on the falsifiers above, that green job grounds this narrow observation for the exact fixture/donor pair:

- the exact donor snapshot named by the v0.4 evidence accepted the admitted historical v0.2 fixture;
- the source object remained unchanged;
- two executions produced exactly equal canonical output;
- the output was **v0.5**, not the adjacent target generation v0.4;
- undeclared historical speech was preserved as `engine=espeak`;
- the pinned donor speech tests passed.

The whole verify workflow also passed all seven jobs: repository/evidence verification on Python 3.11, 3.12, and 3.13; the admitted v0.4 -> v0.5 replay; the v0.1 -> v0.2 HOLD replay; the City G1 -> G2 HOLD replay; and this new v0.2 -> v0.4 HOLD replay.

## Evidence meaning and limitations

This is **executable negative evidence** for the current adjacent migration question. A later FrameState implementation can consume this exact historical v0.2 state and preserve its tested speech meaning, but the observed operation canonicalizes directly to v0.5 rather than deriving the preserved v0.4 target generation. That is not evidence of an adjacent v0.2 -> v0.4 migration.

Therefore `framestate-project-v0.2 -> framestate-project-v0.4` remains `HOLD`; no migration path is admitted.

This does not prove that no v0.2 -> v0.4 migrator could exist elsewhere or be built later. It does not prove whole-project semantic equivalence, chain-vs-direct equivalence, or chain-experiment readiness. It does not rewrite the historical recovery story into a migration story.

With the prior executable HOLD replays for FrameState v0.1 -> v0.2 and City Multiplayer G1 -> G2, every currently declared HOLD adjacent edge now has bounded executable evidence as well as its historical/source audit. This does not make any of those edges admitted.

## Donor / authority boundary

Adapter & Translation Garden remains the migration/translation implementation donor. No migration generator/router is copied or recreated here. Protocol Evolution only executes pinned donor code as bounded evidence.

The Connected Monolith was not used as a truth source for this replay. Historical fixtures, manifests, lineages, existing path admission, and HOLD records remain unchanged.

## Root gate after observation

- **Truth:** later-version consumption is kept distinct from the missing adjacent target-state transformation; v0.5 output is not relabeled v0.4 migration evidence.
- **Agency / non-domination:** replay is read-only and grants no migration, CANON, install, publish, network, device, or user-data authority.
- **Continuity:** historical fixtures, source lineage, HOLD state, and the sole admitted path remain unchanged.
- **Wisdom before speed:** the last current HOLD edge gained reproducible execution evidence without lowering the path-admission gate.

The four roots support merging this bounded replay/evidence improvement while keeping the edge on HOLD, provided the final PR-head verification remains green and no overlapping semantic lane appears before merge.
