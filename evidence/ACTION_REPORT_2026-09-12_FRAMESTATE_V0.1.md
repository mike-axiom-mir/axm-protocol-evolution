# Action Report — Admit FrameState v0.1 Without Inventing Compatibility

Date: 2026-09-12  
Status: bounded research delta

## Question tested

Can Protocol Evolution extend the real FrameState project lineage with historical v0.1 without falsely classifying v0.1 and later speech-capable generations as incompatible when the corpus contains no shared tested semantic claim between them?

## Falsifier defined before implementation

FrameState v0.1 has a real project artifact and belongs to the same `framestate.project` lineage, but its admitted claim is tone-only audio while v0.2/v0.4/v0.5 currently carry an undeclared-speech-engine claim. If the survivability matrix emits `UNSUPPORTED` merely because those claim dictionaries differ, the experiment fails. Absence of a shared tested claim must remain unjudged.

## Repository and donor state inspected

- `axm-protocol-evolution` main after lineage-readiness work;
- current six-step research direction remains held at the same-domain lineage boundary;
- `mike-axiom-mir/axm-framestate` founding v0.1 commit `5b5f73cb78667d9af981af3b38cd7a7ce3a5dab7`;
- exact donor artifact `examples/first_light.json`, Git blob `3a6f64e8f0355812360abd0546f2b997cdb0db28`;
- donor v0.1 `canonical.py`, which accepts only `tone` audio events;
- Adapter Translation Garden module 030 remains the migration-candidate implementation donor and is not duplicated here.

## Exact delta

- admitted exact historical FrameState v0.1 `first_light.json` as a new generation fixture;
- recorded donor commit, path, Git blob SHA, and bounded `audio_model=tone_only` claim;
- extended the FrameState lineage from 3 to 4 admitted generations;
- advanced survivability matrix schema v0.2 -> v0.3;
- changed same-domain comparison so disjoint semantic-claim sets emit `comparable: false`, `state: null`, `reason: no-common-semantic-claim`;
- added a conservative `partial-semantic-claim-overlap` unjudged state for future partially overlapping claim sets;
- preserved the exact pre-change v0.2 matrix as `evidence/generation_matrix_v0.2.json`;
- added regression coverage for fixture Git-blob identity, bounded v0.1 semantics, lineage count, and no-common-claim handling.

## Evidence result

The exact copied v0.1 artifact recomputes to donor Git blob SHA `3a6f64e8f0355812360abd0546f2b997cdb0db28`.

Repository CI is the merge evidence gate for the complete suite; final workflow result is recorded in the pull request before merge.

## Truth boundary

This delta proves only that:

- the admitted v0.1 artifact is byte-identical to the named donor Git blob;
- v0.1 is a real FrameState project-schema generation;
- the donor v0.1 reader supports tone-only audio;
- this corpus has no shared tested semantic assertion between v0.1's tone-only claim and later undeclared-speech-engine claims;
- lack of a shared tested claim is not evidence of incompatibility.

It does **not** prove:

- v0.1 can migrate directly to v0.2, v0.4, or v0.5;
- runtime interoperability;
- contiguous historical release coverage;
- semantic equivalence outside the declared claims;
- a four-step or five-step migration path.

## Root check

**Truth** — no shared claim is represented as no judgment, not fake incompatibility.

**Agency / non-domination** — no migration executes and no donor/product/canon authority is taken.

**Continuity** — the historical artifact is preserved exactly, donor identity is explicit, and prior matrix v0.2 is retained unchanged.

**Wisdom before speed** — the chain-vs-direct experiment remains HOLD; the FrameState lineage is now 4/5 admitted generations, but migration paths are still unproven.

## Next unresolved question

Find one more real FrameState project generation that can be admitted with source provenance, or prove that no suitable historical generation exists. Reaching 5/5 lineage membership still will not authorize the chain-vs-direct experiment until adjacent migration paths are evidenced.
