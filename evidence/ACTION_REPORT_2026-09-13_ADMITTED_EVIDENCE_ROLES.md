# Action Report — Admitted Evidence Reference Roles

Date: 2026-09-13

## Bounded research question

Can the only currently admitted migration path keep its donor references as one undifferentiated evidence bag, forcing later reviewers to rediscover what each reference is supposed to contribute?

The previous evidence layers established structural full-SHA pinning, observed GitHub resolution, and repository-lineage binding. They intentionally stopped short of semantic-content validation. The smallest next step is therefore not to claim semantic proof, but to make the admitted bundle's intended reference roles explicit and machine-checkable.

## Falsifier defined before implementation

This improvement fails if any evidence reference on an admitted migration path cannot be assigned exactly one explicit bounded role without inventing new donor evidence, or if a role catalog can omit an admitted reference, add an unrelated extra reference, duplicate one reference, or use an unknown role while still passing.

The cycle must not rewrite `migration_paths.json`, historical generation fixtures, HOLD investigations, or donor repositories.

## Grounded donor read

The only admitted path remains `framestate-v0.4-to-v0.5-canonical-normalization`, with four already admitted donor references.

Connected reads of the exact pinned FrameState donor state show distinct roles:

1. transition commit `df019c55e6e2c4f46f7bda59ccc5bdc229921737` introduces the v0.5 native-speech change set and states the old/new undeclared-speech split;
2. pinned `src/axm_framestate/canonical.py` contains the transition mechanism: `normalize_project` accepts v0.1-v0.5 project schemas, emits canonical v0.5 state, and gives undeclared speech `espeak` for older schemas versus `native` for v0.5;
3. pinned `tests/test_speech.py` contains `test_project_schema_migrates_legacy_speech_without_rewriting_its_engine`, checking the v0.4 `espeak` / v0.5 `native` preservation split;
4. pinned `CHANGELOG.md` records the donor's intended interpretation: v0.4-and-earlier undeclared speech migrates as eSpeak to preserve historical intent while new v0.5 undeclared speech defaults to native.

No new migration claim is introduced by this cycle.

## Implementation

Added an additive role overlay at `fixtures/evidence_reference_roles.json` for admitted migration paths.

The new analyzer:

- requires every admitted path to have one role record;
- requires exact one-to-one coverage of that path's existing `evidence_refs`;
- rejects omitted references, unrelated extras, duplicate assignments, duplicate records, unknown paths, unknown roles, empty observations, and invalid lower-layer donor binding;
- preserves the existing path catalog unchanged;
- emits checked-in generated evidence at `evidence/evidence_reference_roles.json`.

Current bounded result:

- admitted path records: 1;
- admitted evidence references: 4;
- role-bound evidence references: 4;
- declared roles: transition introduction, transition mechanism, behavior-preservation check, donor interpretation note.

## Verification contract

Focused regressions cover:

- missing role -> fail closed;
- extra non-path reference -> fail closed;
- duplicate reference assignment -> fail closed;
- unknown role -> fail closed;
- invalid donor-binding lower layer -> fail closed;
- current real admitted path -> exact 4/4 role coverage;
- generated result -> byte-structure equality with checked-in JSON after parsing.

Repository-wide CI remains the merge prerequisite.

## Truth boundary

A passing role-binding result proves only that every current admitted-path reference has one explicit declared audit role and that the role overlay exactly covers the already admitted reference set.

It does **not** prove:

- that the declared role is a correct semantic interpretation of the target content;
- that the evidence bundle is sufficient to prove migration semantics;
- authorship, trustworthiness, or cryptographic attestation;
- migration execution by Protocol Evolution;
- whole-project semantic equivalence;
- chain-vs-direct equivalence.

This first role overlay deliberately covers admitted migration paths only. HOLD investigation evidence is unchanged and remains outside this bounded cycle.

## Donor boundary

Adapter & Translation Garden remains the adapter/translation implementation donor. No adapter generator, translation router, migration runtime, or donor implementation is copied or executed.

FrameState is read only as the already declared semantic-migration donor. No donor repository is mutated.

## Root gate

**Truth** — the current admitted evidence bundle becomes explicit about what each reference is being used to show, without upgrading those declarations into semantic proof.

**Agency / non-domination** — no migration, install, publish, network, device, user-data, canon, or merge authority is added.

**Continuity** — historical fixtures, path admission, HOLD records, lineage order, and donor refs remain untouched; the role layer is additive.

**Wisdom before speed** — improve auditability of the one admitted path before attempting stronger semantic-content validation or the larger five-generation experiment.

Merge only if repository-wide CI passes and these boundaries remain intact.
