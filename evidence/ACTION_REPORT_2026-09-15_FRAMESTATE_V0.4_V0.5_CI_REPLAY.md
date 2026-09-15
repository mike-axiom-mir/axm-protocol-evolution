# Action Report — FrameState v0.4 -> v0.5 exact donor CI replay

Date: 2026-09-15
Status: **PASS / bounded replay grounded; merge still requires final-head CI**

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

The existing generated retained-evidence analyzer does not itself execute the donor. This cycle tests that remaining reproducibility gap through a separate exact-donor CI gate rather than pretending an offline generator can observe another job's execution.

## Implemented bounded delta

- added `tools/replay_framestate_v04_v05.py`;
- the harness imports FrameState from an external exact-commit checkout and copies none of its normalizer implementation;
- it verifies donor HEAD and the `canonical.py` / `tests/test_speech.py` Git blobs already bound by the retained observation;
- it verifies exact admitted source/control fixture identities;
- it reruns source and control normalization and requires both input objects to remain unchanged;
- it requires exact equality with both retained outputs and their canonical digests;
- it requires the legacy `espeak` and current `native` semantic outcomes;
- it reruns the donor's targeted five-test speech suite and fails unless all five pass;
- added CI job `replay-framestate-v04-v05`, which checks out the donor at the exact pinned commit and runs the harness.

## Observed evidence

GitHub Actions workflow run `34951974927` on PR #29 head `c41c88957e545190a2521db435958a1e41b4e22d` completed with conclusion **success**.

The dedicated replay job `104324839243` completed with conclusion **success**. Its exact donor checkout step succeeded, followed by the replay harness. Because the harness is fail-closed, that successful exit means the donor HEAD/blob checks, fixture identity checks, source/control non-mutation checks, exact retained-output reproduction, `espeak`/`native` semantic assertions, and the targeted donor 5-test speech regression all passed for this run.

The repository-wide verification matrix in the same workflow also completed successfully. The historical observation of this run is preserved separately in `evidence/path_execution_ci_replay_observation.json`.

## Result

**PASS for the bounded question.** The admitted FrameState v0.4 -> v0.5 execution is no longer supported only by retained output evidence: one exact cross-repository CI replay has now reproduced it from the pinned donor snapshot without copying donor migration code.

This upgrades reproducibility for one already-admitted path only. It does not admit another path or generation and does not make the larger chain experiment ready.

## Limitations

- the retained-evidence generator still validates retained artifacts offline; it does not itself execute the donor;
- the new result is one observed CI replay, not a claim that every future replay will pass;
- GitHub's run record is observed evidence, not a cryptographic attestation produced by this repository;
- only the declared speech-default semantic distinction is checked here, not whole-project semantic equivalence;
- no direct-vs-chain comparison was performed;
- no Living City candidate was promoted;
- no Adapter & Translation Garden implementation was copied or displaced.

## Donor and authority boundary

Protocol Evolution checks out and calls the pinned FrameState donor as evidence. It does not copy the donor normalizer into this repository. Adapter & Translation Garden remains the adapter/translation implementation donor and is not duplicated or displaced.

## Root gate

- **Truth** — retained evidence was reconnected to exact executable donor state and the replay remained bounded to what actually ran.
- **Agency / non-domination** — replay is read-only evidence work and grants no migration, install, publish, device, network, merge, or CANON authority.
- **Continuity** — historical fixtures, path admissions, HOLD records, source lineage, and the original execution observation remain unchanged; the CI observation is additive.
- **Wisdom before speed** — one real path gained reproducible cross-repo evidence without widening claims or manufacturing another admission.

## Merge condition

Merge only if the final PR head again passes both the repository-wide verification matrix and the exact donor replay job.
