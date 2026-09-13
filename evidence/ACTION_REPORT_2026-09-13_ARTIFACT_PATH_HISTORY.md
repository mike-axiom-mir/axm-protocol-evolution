# Action Report — Artifact Path-History Observation

Date: 2026-09-13
Status: bounded evidence improvement; no generation/path promotion

## Bounded question

Can Protocol Evolution distinguish an exact historical artifact whose accessible Git path history aligns with its declared historical commit from a legacy-labelled candidate artifact first visible only in a later cumulative intake, without turning Git chronology into a claim about true creation time?

## Falsifier defined before implementation

The layer must fail closed if:

1. an observed commit or blob identity is not a full 40-character Git identity;
2. the declared oldest observed commit is not the oldest item in the recorded newest-to-oldest bounded result;
3. the observed blob at that commit differs from the expected donor blob;
4. the observation is not bound to an existing historical-fixture route;
5. an exact historical control disagrees with its route repository/path/commit/blob;
6. a legacy-labelled candidate is promoted to historical-fixture support merely because its schema survives in Git history;
7. checked-in evidence drifts from deterministic analysis.

## Grounded observations

### FrameState v0.1 positive control

A path-filtered Git history query for `examples/first_light.json` returned one observed commit: `5b5f73cb78667d9af981af3b38cd7a7ce3a5dab7`, message `feat: establish standalone deterministic FrameState machine v0.1`. That is the same full commit already used by the exact historical fixture route. The donor blob remains `3a6f64e8f0355812360abd0546f2b997cdb0db28`.

Result: bounded path history supports the already-grounded historical observation. It does not newly admit the generation; the generation was already admitted through stronger fixture evidence.

### Living City v0.1-labelled schema negative/gap control

A path-filtered Git history query for `schemas/world-v0.1.0.schema.json` returned one observed commit: `4a24997221412d28b959ef02bb9b30f4a41271cb`, message `feat(simulator): intake Living City v0.11.3 headless branch`. The exact schema blob there is `90c8413d096accf26d16c27844d75da9d7be76a8`, matching the blob later observed in the connected monolith candidate.

The adjacent `docs/MIGRATION_v0_1_TO_v0_2.md` path was independently queried and is likewise first visible in the bounded accessible Git path history at the same cumulative v0.11.3 intake commit.

Result: this strengthens the reason to keep Living City historical-fixture promotion on HOLD. The repository preserves a v0.1-labelled schema and migration documentation, but the accessible Git history does not expose those files through a separate v0.1-era commit sequence. More importantly, neither file is a serialized historical v0.1 world value.

## Improvement

- add `artifact_path_history` evidence analysis;
- bind each observation to an existing `historical_fixture_routes` record;
- retain full commit/blob identities and explicit bounded result counts;
- keep the FrameState control positive and Living City candidate negative;
- add seven focused falsifier/regression tests;
- generate the evidence in repository CI.

## Truth boundary

`oldest_observed_commit` means only the oldest commit returned by the recorded bounded path query. It is **not** asserted to be the file's true creation time, the earliest existence of equivalent content outside accessible Git history, authorship proof, or historical release proof.

A legacy version label on a schema or migration document is not a serialized historical generation fixture. This cycle admits zero Living City generations and zero Living City migration paths, does not execute a migration, does not prove semantic equivalence, and does not make the five-generation chain experiment input-ready.

Adapter & Translation Garden remains the implementation donor. No adapter generator, migration router, or migration runtime is copied or reimplemented here.

## Merge gate

- **Truth:** path chronology is recorded with a deliberately narrow claim; the tempting Living City candidate remains unpromoted.
- **Agency / non-domination:** no canon, migration, install, publish, device, network, or user-data authority is added.
- **Continuity:** existing historical fixtures, admissions, HOLD records, lineages, and donor references remain unchanged.
- **Wisdom before speed:** improve provenance discrimination before seeking a Living City fixture/path admission.

Merge only if the focused regression set and repository-wide CI pass.
