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

## Grounded donor execution

The Connected Monolith was used only as a composition surface containing the pinned donor snapshot. Its `AXM_MONOLITH_SOURCE.json` identifies `mike-axiom-mir/axm-framestate` at commit `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`.

Independent source binding:

- executed `src/axm_framestate/canonical.py` -> Git blob `c44122ce84a238587ee263ca4df95be762992f6e`, matching GitHub at the pinned donor commit;
- executed `tests/test_speech.py` -> Git blob `e263a996d0f91ddd922e26fbda19150de3a941b0`, matching GitHub at the pinned donor commit;
- admitted v0.4 input fixture -> Git blob `2531173347a861574d732832b548cb05c2b07ff4`, raw SHA-256 `8e17619c38577478ab737e52d3a52c150f07949cc2c3242f750e157cbf7c830e`;
- admitted v0.5 control fixture -> Git blob `77379e44fce715b616711f3cf54b166f0eca7455`, raw SHA-256 `8129fed796b7c34529dd72ec15c0c70cfe7be8ff36da01b478abb040e3c49ea7`.

Observed execution:

- v0.4 source canonical digest: `sha256:ac55e91b3e17ca1cb6e996435a17b0fdbaf8001d480cb6d1932778f9ed3a1ea8`;
- v0.4 -> v0.5 observed output canonical digest: `sha256:102125a406d95a3738736d11505a340e8356efaf558ebc255d0d14c3058923a0`;
- observed output schema: `axm.framestate.project/v0.5`;
- observed legacy speech engine: `espeak`;
- v0.5 control output canonical digest: `sha256:446658230447f4184a11bdd0a9859488edfabcff1d1ef683dab30015b1fec1c2`;
- observed current-control speech engine: `native`;
- neither supplied input object was mutated in place.

The exact pinned donor's targeted speech suite was also run directly: `PYTHONPATH=src python -m unittest tests.test_speech -v` -> **5/5 PASS**.

## Implemented evidence contract

The repository now retains the exact execution/control outputs outside the immutable historical-generation fixtures and validates a machine-readable observation against the already-admitted path, source/target manifests, local fixture identities, output identities, declared semantic claim, donor commit shape, targeted-test result, and explicit no-promotion boundaries.

Nine focused falsifier/regression tests pass locally. They include an adversarial case that rewrites the retained output from `espeak` to `native`, recomputes both output hashes, and still requires rejection because the preserved semantic claim is wrong. This distinguishes byte-integrity success from semantic-survivability success.

CI re-generates and validates the retained evidence record but deliberately does **not** replay the external donor snapshot. Therefore this layer means "a bounded execution was observed and its retained identities/meaning are internally closed," not "GitHub CI independently reran FrameState."

## Result

**ADVANCE, narrowly:** the already-admitted FrameState v0.4 -> v0.5 path now has one grounded observed-execution record for the exact admitted v0.4 fixture under the exact pinned donor snapshot. The declared historical `espeak` meaning survives into canonical v0.5 output, while the v0.5 control retains the distinct `native` default.

This does not add a new path admission or generation. It does not change the two earlier FrameState HOLD edges, the City HOLD edge, or the blocked five-generation experiment.

## Limitations

- one execution and one declared semantic claim do not prove whole-project semantic equivalence;
- the donor execution occurred in this bounded run, not inside repository CI;
- exact donor Git-blob identity proves which bytes were executed, not authorship or universal environmental equivalence;
- the Connected Monolith remains only the composition carrier used to obtain the pinned snapshot;
- no direct-vs-chain migration comparison was performed;
- no user data, canonical AXM state, donor repository, or Adapter & Translation Garden implementation was modified.

## Donor / authority boundary

Protocol Evolution records and validates an execution observation only. It does not copy or reimplement FrameState's normalizer, and it does not duplicate Adapter & Translation Garden. The Connected Monolith is not privileged truth; source identity is independently pinned back to the donor repository.

## Merge gate

- **Truth:** exact donor/input/output identities and narrow semantic outcome are retained and falsifiable.
- **Agency / non-domination:** no automatic migration, install, publish, CANON, device, network, or user-data authority.
- **Continuity:** existing historical fixtures, admissions, HOLD records, lineage, and source provenance remain unchanged.
- **Wisdom before speed:** one observed path execution advances only its actual evidence rung; the five-generation experiment remains blocked.

Merge only if repository-wide CI passes at the final PR head and the current chain-readiness boundary remains false.