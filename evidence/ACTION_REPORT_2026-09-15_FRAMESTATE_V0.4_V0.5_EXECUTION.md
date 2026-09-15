# Action Report — FrameState v0.4 -> v0.5 execution evidence

Date: 2026-09-15

## Bounded research question

Can the already-admitted `framestate-v0.4-to-v0.5-canonical-normalization` path advance from source-evidence-only admission to **observed execution evidence** by running the exact pinned FrameState donor snapshot against Protocol Evolution's admitted v0.4 fixture, without copying FrameState migration machinery into this repository or promoting one execution into chain-wide compatibility proof?

## Falsifier — defined before implementation

The execution observation must be rejected or remain HOLD if any of the following is true:

1. the donor snapshot is not exactly `mike-axiom-mir/axm-framestate@60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`;
2. the executed donor `src/axm_framestate/canonical.py` bytes do not match the Git blob at that pinned commit;
3. the source input is not byte-identical to checked-in `fixtures/generations/framestate-v0.4/project.json`;
4. normalization mutates the supplied source object in place;
5. the observed output schema is not exactly `axm.framestate.project/v0.5`;
6. the undeclared legacy speech meaning is not materialized as `engine=espeak`;
7. the observation is bound to any path other than the already-admitted exact v0.4 -> v0.5 path;
8. an observation with weak donor identity, unknown path, mismatched source/target generations, duplicate identity, mismatched input/output digest, or contradictory semantic claim can pass validation;
9. this bounded execution is allowed to imply five-generation chain readiness, direct-vs-chain equivalence, universal/whole-project semantic equivalence, CANON authority, or Adapter & Translation Garden ownership.

A useful control is the admitted v0.5 fixture: under the same pinned donor snapshot, undeclared v0.5 speech should normalize to `engine=native`. If the old/new split collapses, the preservation claim is falsified.

## Pre-implementation grounded observation

The Connected Monolith is used only as a composition surface containing the pinned donor snapshot. Its `AXM_MONOLITH_SOURCE.json` identifies `mike-axiom-mir/axm-framestate` at commit `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`. The local donor `canonical.py` computes to Git blob `c44122ce84a238587ee263ca4df95be762992f6e`, matching GitHub at that exact commit. The bundled `tests/test_speech.py` computes to Git blob `e263a996d0f91ddd922e26fbda19150de3a941b0`, also matching GitHub.

Before this implementation, direct execution of that pinned snapshot against the exact checked-in v0.4 fixture produced v0.5 canonical output with `engine=espeak`; the v0.5 control produced `engine=native`; neither input object was mutated. The donor's targeted speech suite also passed 5/5 locally. These observations still need a fail-closed repository evidence contract before they count as retained Protocol Evolution evidence.

## Donor / authority boundary

Protocol Evolution will record and validate an execution observation only. It will not copy or reimplement FrameState's normalizer, and it will not duplicate Adapter & Translation Garden. The Connected Monolith is not privileged truth; source identity is independently pinned back to the donor repository.

## Merge gate

- **Truth:** exact donor/input/output identities and narrow semantic claim must fail closed.
- **Agency / non-domination:** no automatic migration, install, publish, CANON, device, network, or user-data authority.
- **Continuity:** existing fixtures, admissions, HOLD records, lineage, and source provenance remain unchanged.
- **Wisdom before speed:** one observed path execution is retained only at its actual scope; the five-generation experiment remains blocked.

Merge only after focused regressions and repository-wide CI pass and the current chain-readiness boundary remains false.