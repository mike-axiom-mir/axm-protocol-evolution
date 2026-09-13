# Action Report — Evidence Donor Repository Binding

Date: 2026-09-13

## Bounded research question

Can a donor evidence reference be structurally full-SHA-pinned and successfully observed as resolving, yet still come from a repository unrelated to the source/target generation lineage and pass the evidence gate?

The previous cycles established URL pinning and observed GitHub resolution. Neither establishes that the resolved resource belongs to a repository declared by the generation pair whose migration-path claim it is being used to support.

## Falsifier defined before implementation

A synthetic edge declares source and target generations from `example/donor`, while its evidence reference is a valid full-SHA commit in `example/other` and has a matching successful resolution observation.

If that unrelated repository can still pass the new gate, the improvement fails.

The contract must also avoid creating a same-repository assumption: when a source generation and target generation legitimately declare different repositories, evidence from either declared endpoint repository must remain admissible.

## Grounded current observation

The checked-in edge catalogs currently contain:

- 1 admitted migration path;
- 3 HOLD investigations;
- 15 donor evidence references;
- 6 admitted generation manifests;
- 2 repositories declared by those generations: `mike-axiom-mir/axm-framestate` and `mike-axiom-mir/axm-city-multiplayer`.

All 15 current references are already structurally full-SHA-pinned and have matching observed-resolution evidence. Under the new repository-binding contract, all 15 also come from a repository declared by the source or target generation of their exact edge.

This does not change any path admission, HOLD result, fixture, lineage ordering, source reference, or historical artifact.

## Implementation

Added `analyze_evidence_donor_binding()` as a separate deterministic evidence layer above the existing structural-pinning and resolution checks.

For every admitted path or HOLD investigation it:

- resolves the exact source and target generation manifests;
- reads the repositories those manifests explicitly declare;
- permits evidence from either declared endpoint repository;
- rejects evidence from an unrelated third repository;
- rejects missing/unknown generations, duplicate generation identities, malformed repository identities, and structurally invalid references;
- fails closed if the existing resolution-evidence layer is invalid.

The checked-in generator discovers existing generation manifests under `fixtures/generations/*/manifest.json`; it does not rewrite them.

## Verification

Before repository publication, a bounded local synthetic harness exercised the core rule and passed 4/4 cases:

- unrelated but resolved repository evidence fails;
- a cross-repository edge may use either declared endpoint repository;
- unknown generation identity fails;
- duplicate generation-manifest identity fails.

Repository-wide CI is the merge prerequisite. The checked-in suite also verifies the real corpus counts and binds generated evidence to `evidence/evidence_donor_binding.json`.

## Truth boundary

A passing donor-repository binding proves only:

> each current edge evidence reference is attached to one of the repositories explicitly declared by that edge's source or target generation, after the existing structural and resolution gates pass.

It does **not** prove:

- that the referenced file/commit is semantically relevant to the attributed claim;
- that the cited content is sufficient evidence for the claim;
- authorship, trustworthiness, or cryptographic attestation;
- migration execution;
- whole-project semantic equivalence;
- chain-vs-direct equivalence.

This v0.1 contract also deliberately does not silently admit third-repository evidence. If future cross-repository compatibility research needs evidence from a separate adapter or observer repository, that relationship needs an explicit evidence-role/provenance contract rather than an implicit exception.

The five-generation chain experiment remains HOLD.

## Donor boundary

Adapter & Translation Garden remains the live migration/adapter implementation donor. No adapter generator, migration router, translation runtime, or donor implementation is copied or executed here.

The new rule does not grant Protocol Evolution authority over FrameState, City Multiplayer, or the Garden. It only checks the declared repository identity of evidence already used by Protocol Evolution's own research records.

## Root gate

**Truth** — a resolved GitHub URL from an unrelated repository can no longer masquerade as lineage-bound donor evidence.

**Agency / non-domination** — no migration, install, publish, network, device, user-data, canon, or merge authority is added.

**Continuity** — historical fixtures, donor refs, path admissions, HOLD records, and lineage ordering remain untouched; the new evidence layer is additive.

**Wisdom before speed** — bind evidence to the declared donor lineage before attempting stronger semantic-content validation or advancing the larger chain experiment.

Merge only if repository-wide CI passes and these boundaries remain intact.
