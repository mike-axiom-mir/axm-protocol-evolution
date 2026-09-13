# Action Report — Connected Monolith Candidate Census

Date: 2026-09-13

## Bounded research question

Can a five-generation compatibility candidate discovered inside the connected AXM monolith be recorded without silently promoting version-labelled schema documents or migration documentation into admitted historical generation fixtures, admitted migration paths, execution proof, semantic equivalence, or chain-experiment readiness?

The current Protocol Evolution corpus still has no admitted five-generation lineage. The uploaded connected monolith exposed a promising Living City world-version sequence, but package presence alone must not bypass the repository's existing evidence ladder.

## Falsifier defined before implementation

This cycle fails if the candidate census accepts any observation that:

- claims a generation has been admitted;
- claims an adjacent migration path has been admitted;
- claims a migration was executed;
- claims semantic equivalence was proven;
- claims chain-experiment input readiness;
- lacks a strong package SHA-256 identity;
- contains duplicate, malformed, or out-of-order semantic versions;
- lacks exactly one documented transition contract for each ordered adjacent pair;
- orders a transition contract against the wrong version pair;
- records a candidate archive file whose Git-blob identity differs from the pinned GitHub source blob.

A valid observation with five or more version-labelled schema documents and all adjacent migration-contract documents must still report `chain_experiment_input_ready: false`.

## Read-only evidence inputs

The candidate source is the user-supplied `AXM_Connected_Monolith_v0.3.2` package, recorded as:

- size: 194,320,426 bytes;
- SHA-256: `f0a0d1d30007d71bb4ded6a9cc03259e5a12ceb7967cd532b12d366ae0cdf55e`;
- module record: `mike-axiom-mir/axm-living-city-simulator`;
- pinned source commit: `a299db639e87b2fa0dea1ded1bf651ab86e9cd3c`.

The source commit was independently observed to resolve through connected GitHub during this cycle. The checked-in observation records that fact; CI does not re-contact GitHub.

The bounded candidate covers only Living City world schemas v0.1.0 through v0.5.0 and the four adjacent migration-contract documents v0.1→v0.2, v0.2→v0.3, v0.3→v0.4, and v0.4→v0.5.

For all nine bounded files, the Git blob SHA calculated from the exact monolith entry bytes matched the blob SHA observed at the pinned GitHub commit. This grounds byte identity between the package copy and the pinned source files for this bounded set. It does not prove those files executed.

## Donor meaning re-read

The migration contracts contain explicit semantic non-invention boundaries rather than only version labels:

- v0.1→v0.2 says a legacy relationship label is not proof of household consent and the migrator must not manufacture a consent agreement;
- v0.2→v0.3 says habitat migration must not fabricate a partner/agreement, approvals, ownership, completed construction, or spend/history that did not exist;
- v0.3→v0.4 explicitly forbids invented intentions, stewardship requests, approvals, contributions, purchased materials, completed property change, and ownership;
- v0.4→v0.5 explicitly forbids inferred parenthood, dependents, accepted care plans, family units, room assignment, historical care records, custody, guardianship, or legal status.

Those documents make Living City a strong candidate for later semantic migration research. Documentation is still not transformation execution evidence.

## Implementation

Added a read-only monolith candidate-observation layer:

- `fixtures/monolith_candidate_observations.json` records package/source identity plus the bounded five-version candidate;
- `protocol_evolution/monolith_candidates.py` validates candidate-only status, package/source identity shape, ordered unique versions, adjacent transition coverage, recorded archive/Git byte identity, and explicit non-promotion flags;
- `tools/monolith_candidate_census.py` emits deterministic checked-in census evidence;
- `tests/test_monolith_candidate_census.py` exercises the falsifiers;
- `evidence/monolith_candidate_census.json` records the current bounded result.

Current result:

- observations: 1;
- five-plus-generation candidates: 1;
- candidate versions: 5;
- adjacent documented transition contracts: 4;
- admitted generations added: 0;
- admitted migration paths added: 0;
- migration execution claims added: 0;
- semantic-equivalence claims added: 0;
- chain-experiment readiness granted: no.

The existing historical fixtures, `fixtures/lineages.json`, `fixtures/migration_paths.json`, HOLD investigations, donor references, and source lineage are unchanged.

## Verification

Focused authored regressions cover:

- the real observation remaining valid but non-promoted;
- any promotion claim failing closed;
- a missing adjacent transition contract failing closed;
- wrong transition ordering failing closed;
- duplicate version identity failing closed;
- weak archive identity failing closed;
- archive/Git byte-identity mismatch failing closed.

The candidate census is also added to the repository verification workflow. Repository-wide CI remains the merge prerequisite.

## Truth boundary

This cycle establishes only a **candidate discovery record**.

It does **not** prove:

- that a schema document is an immutable historical world-value fixture;
- that every historical Living City release is represented;
- that any migration implementation executed against a candidate source value;
- that the migration-contract documents are sufficient proof of implementation behavior;
- that chained migration preserves all tested meaning;
- that a direct old→current migration exists;
- that chain and direct migration are equivalent;
- authorship or cryptographic attestation of the connected observation;
- canon, merge, install, publish, device, network, or user-data authority.

The package itself is not committed to this repository. Offline CI checks the recorded observation and cannot reopen the 194 MB archive. The connected source-resolution observation is likewise recorded rather than live-rechecked by CI.

## Donor boundary

Adapter & Translation Garden remains the migration/translation implementation donor. No adapter generator, router, migration runtime, or donor implementation was copied or executed.

Living City is read only as a newly discovered semantic-migration candidate donor. Its repository was not mutated by this cycle.

## Root gate

**Truth** — five version-labelled schemas plus migration documents are recorded as a candidate, not relabelled as an admitted migration chain. File identity is bounded to the exact package and pinned source blobs actually observed.

**Agency / non-domination** — the census grants no migration, canon, merge, install, publish, network, device, or user-data authority.

**Continuity** — all existing historical fixtures, lineages, admissions, HOLD findings, donor refs, and evidence layers remain unchanged; this layer is additive.

**Wisdom before speed** — use the monolith to locate promising evidence, but preserve the existing admission gates before running the larger five-generation experiment.

Merge only if repository-wide CI passes and these boundaries remain intact.

## Next smallest question

Can one actual historical Living City world value and the corresponding adjacent donor transformation be grounded strongly enough to admit **one** Living City generation/path pair without treating the migration documentation itself as execution proof?
