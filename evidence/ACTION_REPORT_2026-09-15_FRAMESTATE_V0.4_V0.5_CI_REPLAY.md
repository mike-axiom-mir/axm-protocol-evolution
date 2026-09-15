# Action Report — FrameState v0.4 -> v0.5 exact donor CI replay

Date: 2026-09-15
Status: **IN PROGRESS / falsifier committed before implementation**

## Bounded question

Can Protocol Evolution replay the already-observed FrameState v0.4 -> v0.5 path from the exact pinned donor snapshot in CI, instead of validating only retained output evidence?

## Falsifier defined before implementation

The improvement fails closed if any of the following occurs:

1. the donor checkout is not exactly `mike-axiom-mir/axm-framestate@60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`;
2. the donor `canonical.py` or `tests/test_speech.py` Git blob identity differs from the retained execution observation;
3. the admitted v0.4 source fixture or admitted v0.5 control fixture differs from the identities already bound in `fixtures/path_execution_observations.json`;
4. executing the donor normalizer on the exact admitted v0.4 fixture does not reproduce the retained v0.5 output exactly;
5. the v0.4 source object is mutated while normalizing;
6. the replayed legacy output does not preserve `undeclared_speech_engine=espeak`;
7. the admitted v0.5 control does not normalize to the retained control output or loses `undeclared_speech_engine=native`;
8. the control object is mutated while normalizing;
9. the donor targeted speech regression does not pass completely;
10. the replay requires copying FrameState migration/normalization implementation into Protocol Evolution;
11. a passing replay is used to claim whole-project semantic equivalence, direct-vs-chain equivalence, five-generation chain readiness, CANON authority, or ownership of Adapter & Translation Garden.

If the donor cannot be checked out or the exact replay cannot run in the CI environment, the result is **HOLD**, not inferred success.

## Starting evidence

PR #28 retained one exact execution observation for the admitted path `framestate-v0.4-to-v0.5-canonical-normalization`. It records:

- donor repository `mike-axiom-mir/axm-framestate`;
- donor commit `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`;
- donor blobs for `canonical.py` and `tests/test_speech.py`;
- exact source/control fixture identities;
- exact retained source/control outputs;
- legacy `espeak` and current `native` semantic expectations;
- 5/5 targeted donor tests observed during the original bounded run.

The existing generated evidence deliberately states `donor_execution_replayed_in_ci: false`. This cycle tests that exact remaining limitation rather than adding a broader migration abstraction.

## Donor and authority boundary

Protocol Evolution may check out and call the pinned FrameState donor as evidence. It must not copy the donor normalizer into this repository. Adapter & Translation Garden remains the adapter/translation implementation donor and is not duplicated or displaced.

## Root gate before implementation

- **Truth** — a retained output is not the same thing as a reproducible cross-repo execution; exact replay must either run or remain HOLD.
- **Agency / non-domination** — replay is read-only evidence work and grants no migration, install, publish, device, network, merge, or CANON authority.
- **Continuity** — historical fixtures, path admissions, HOLD records, source lineage, and the original execution observation remain unchanged.
- **Wisdom before speed** — strengthen one real admitted path before widening the experiment.

## Intended bounded delta

Add a small replay harness that imports the pinned donor implementation from an external checkout, verifies donor and fixture identities, reruns the exact source/control normalization and targeted donor regression, and compares the replay byte-for-meaning result against the retained evidence. Add one dedicated CI job for this replay. Do not change chain readiness or admit any new path.

## Result

Pending implementation and CI evidence.
