# Action Report — FrameState v0.4 -> v0.5 adjacent-path admission

Date: 2026-09-12
Status: **ADMIT / bounded path evidence only**

## Question

Does the historical FrameState v0.4 -> v0.5 transition contain explicit project-state transformation evidence strong enough to admit this exact adjacent migration path, rather than only newer-reader compatibility or a runtime reinterpretation?

## Falsifier defined before implementation

Keep the edge **HOLD** if the donor evidence only accepts v0.4 unchanged, preserves the output schema as v0.4, or changes speech behavior only at runtime without materializing a v0.5 canonical state. Admission requires an explicit v0.4 input -> v0.5 canonical-output transformation with the historical undeclared-speech meaning preserved rather than silently changed.

## Donor evidence inspected

Repository: `mike-axiom-mir/axm-framestate`

Admitted Protocol Evolution fixtures:

- FrameState v0.4 source ref: `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`;
- FrameState v0.5 source ref: `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`;
- the two research artifacts differ in project schema while using the same undeclared speech event, so the preservation/default split is directly observable in the corpus.

Exact donor transition introduction:

- commit `df019c55e6e2c4f46f7bda59ccc5bdc229921737` — `feat: add native deterministic speech organ v0.8`;
- parent `4402258282e0fe864692f2b54c7e7c2d5f2e3d9f` had `PROJECT_SCHEMA='axm.framestate.project/v0.4'`, accepted project schemas only through v0.4, and speech normalization had no engine field;
- the transition commit changes the canonical project schema to v0.5 and accepts v0.1-v0.5 input;
- for speech with no explicit engine, the v0.5 normalizer selects `native` only when the input schema is the current v0.5 schema; older schemas select `espeak`;
- the normalized return state uses `PROJECT_SCHEMA`, so a v0.4 input is emitted as canonical v0.5 state with `engine: espeak` materialized;
- donor test `test_project_schema_migrates_legacy_speech_without_rewriting_its_engine` asserts v0.4 undeclared speech -> `espeak` and v0.5 undeclared speech -> `native`;
- the matching changelog explicitly states that v0.4-and-earlier speech without an engine migrates as eSpeak to preserve historical intent.

## Result

The falsifier is not triggered. Unlike the earlier v0.1 -> v0.2 and v0.2 -> v0.4 audits, this edge has an explicit donor project-state transformer behavior: v0.4 input is normalized into v0.5 canonical output while the older undeclared speech meaning is made explicit as eSpeak.

Therefore `framestate-project-v0.4 -> framestate-project-v0.5` is admitted as the first grounded adjacent migration path in this research corpus.

This changes the readiness facts to:

- admitted migration paths: `1`;
- FrameState required adjacent paths: `3`;
- FrameState admitted adjacent paths: `1`;
- FrameState investigated/HOLD missing paths: `2`;
- FrameState uninvestigated missing paths: `0`;
- FrameState lineage length: `4`, still below the five-generation target;
- chain-vs-direct experiment input-ready: **false**.

## Exact repository delta

- add one evidence-bound entry to `fixtures/migration_paths.json`;
- update generated/check-in chain readiness truth to reflect one admitted path and two remaining HOLD gaps;
- strengthen the current-corpus regression around the exact admitted edge and remaining missing edges;
- update the README boundary;
- leave both prior HOLD investigations unchanged;
- preserve every historical fixture and source reference unchanged.

## Truth boundary

This admission proves only that reviewed donor evidence contains an explicit canonical v0.4 -> v0.5 state-transition rule for the tested project shape and preservation claim.

It does **not** prove that Protocol Evolution executed that donor transformer during this cycle, authenticate the donor evidence beyond the pinned Git history, prove all possible v0.4 projects migrate losslessly, prove whole-application interoperability, prove semantic equivalence outside the tested speech-default claim, or prove chain-vs-direct equivalence.

The readiness analyzer itself still reports `evidence_references_independently_verified: false`, `migration_execution_proven: false`, `semantic_equivalence_proven: false`, and `direct_migration_equivalence_proven: false`.

## Donor boundary

Adapter Translation Garden remains the migration/translation implementation donor. No migration generator, router, or adapter implementation is copied into Protocol Evolution. This repository records and tests cross-repository semantic compatibility evidence only.

## Root gate

**Truth** — the edge is admitted because the donor contains an explicit state transformer and preservation regression, not because the versions are adjacent or the changelog uses the word migration.

**Agency / non-domination** — no donor repository is mutated and no migration, install, publish, device, user-data, or canon authority is taken.

**Continuity** — prior HOLD investigations, historical fixtures, exact source refs, and lineage order remain unchanged; the admission is additive.

**Wisdom before speed** — only this evidenced edge advances. The larger chain experiment remains blocked by the four-generation lineage length and the two earlier HOLD edges.

## Next bounded question

The FrameState adjacent-edge audit is now complete for the currently admitted four generations. The next useful question should not re-audit these edges; it should either establish a fifth real FrameState generation with preserved source lineage or investigate another declared missing edge such as City Multiplayer G1 -> G2. Neither may be inferred merely to advance the chain target.
