# Action Report — Evidence Reference Resolution

Date: 2026-09-13

## Bounded research question

Can a donor evidence URL be structurally pinned to a full commit SHA and still fail to identify a resource that was actually observed to resolve?

The previous cycle proved only URL shape and full-SHA pinning. It explicitly left `resource_existence_verified` false. This cycle takes the smallest next step: bind the current checked-in migration-path and HOLD evidence references to explicit successful GitHub resolution observations without turning Protocol Evolution into a network-dependent adapter or migration runtime.

## Falsifier defined before implementation

The improvement fails if any of these can pass:

1. a structurally valid full-SHA reference with no resolution observation;
2. a commit observation whose observed SHA does not equal the pinned commit;
3. a blob observation with no concrete Git blob identity;
4. a compare observation whose observed base/head do not equal the pinned endpoints;
5. an extra or duplicate observation that is not bound to a current catalog reference.

A passing snapshot must cover every current unique evidence reference.

## Grounded observation

The current catalogs contain 15 evidence-reference occurrences and 15 unique URLs.

Using connected GitHub reads on 2026-09-13:

- all 5 commit references resolved to their exact pinned commit SHAs;
- all 7 pinned blob references resolved and returned concrete Git blob SHAs;
- all 3 compare references resolved with the exact pinned base/head identities;
- the FrameState v0.1 -> v0.2 compare reports 2 commits;
- the FrameState v0.2 -> v0.4 compare reports 148 commits;
- the City Multiplayer G1 -> G2 compare reports 37 commits.

The observations are preserved in `evidence/evidence_reference_resolution_observations_2026-09-13.json`. The deterministic analyzer binds that snapshot back to the current catalogs and emits `evidence/evidence_reference_resolution.json`.

## Implementation

Added `analyze_evidence_reference_resolution()` as a separate evidence layer beside the existing structural reference inspector.

It:

- starts from the existing structural integrity gate;
- derives the exact current donor-reference expectations from the path and HOLD catalogs;
- requires one bound observation for every current unique reference;
- checks repository, reference kind, and pinned commit identities;
- requires exact commit identity for commit observations;
- requires a concrete full Git blob SHA for blob observations;
- requires exact base/head plus bounded compare metadata for compare observations;
- rejects missing, duplicate, extra, mismatched, or unresolved observations.

The offline analyzer does not contact GitHub. This keeps CI deterministic and makes the external observation boundary visible instead of hiding network state inside tests.

## Verification

Focused authored regression suite: 5/5 PASS in the bounded local harness.

The regressions prove that:

- structural pinning alone does not count as resolution;
- a mismatched observed commit SHA fails;
- a blob observation without a concrete blob identity fails;
- all 15 current references are covered by the checked-in observation snapshot;
- generated resolution evidence exactly matches the checked-in result.

Repository-wide GitHub verification is the merge prerequisite.

## Truth boundary

This cycle proves only a narrower claim:

> Every donor URL currently used by the one admitted migration path and three HOLD investigations was observed to resolve through connected GitHub reads on 2026-09-13, and the checked-in observation identities bind to the exact pinned references.

It does **not** prove:

- that the offline analyzer independently re-contacted GitHub;
- that the observation snapshot is cryptographically attested;
- that a referenced file or commit supports the semantic interpretation attributed to it;
- authorship or trustworthiness of donor content;
- migration execution;
- whole-project semantic equivalence;
- chain-vs-direct equivalence;
- future availability of the referenced resources.

The larger five-generation chain experiment remains HOLD.

## Donor boundary

Adapter & Translation Garden remains the live migration/adapter implementation donor. No adapter generator, migration router, translation runtime, or donor implementation was copied or executed.

FrameState and City Multiplayer were read only as evidence donors. Their repositories were not mutated.

No historical generation fixture, source lineage, migration-path admission, or HOLD investigation was rewritten.

## Root gate

**Truth** — structurally plausible URLs no longer stand in for observed resolution; the remaining semantic/authorship/execution limits stay explicit.

**Agency / non-domination** — the change adds no migration, install, publish, network, device, user-data, canon, or merge authority.

**Continuity** — all historical fixtures, donor refs, path admissions, HOLD records, and lineage order remain unchanged; the observation snapshot is additive.

**Wisdom before speed** — resolve the identity/existence layer before attempting stronger semantic-evidence validation or advancing the larger chain experiment.

Merge only if repository-wide CI passes and these boundaries remain intact.
