# Action Report — Independent Historical Fixture Route

## Bounded question

Can Protocol Evolution ground an exact historical generation fixture without making one sealed all-history archive a mandatory prerequisite, while keeping Living City v0.1.0 on HOLD until an actual historical world value is inspected?

## Falsifier defined before implementation

The route fails if any of these pass:

- a preserved local artifact whose Git blob identity differs from the pinned donor blob;
- a short/mutable donor commit identity;
- an `exact-historical-artifact` record without an explicit historical observation;
- a candidate gap promoted to ready without a historical value;
- a fixture path that escapes the repository root.

A known-positive historical artifact must remain independently provenance-ready even when no sealed all-history archive is available for inspection. If the analyzer requires such an archive anyway, the bounded hypothesis is falsified.

## Grounded control

FrameState v0.1 is an already-admitted historical generation. Its checked-in `fixtures/generations/framestate-v0.1/project.json` is the exact historical donor artifact from:

- repository: `mike-axiom-mir/axm-framestate`
- commit: `5b5f73cb78667d9af981af3b38cd7a7ce3a5dab7`
- path: `examples/first_light.json`
- Git blob: `3a6f64e8f0355812360abd0546f2b997cdb0db28`

The donor file was re-read through connected GitHub during this cycle and reported the same Git blob identity. The connected monolith also carries the already-preserved Protocol Evolution copy with that exact blob identity. This positive control does not depend on a sealed all-history archive.

## Living City boundary

Living City still has no inspected historical v0.1 world value in Protocol Evolution. The pinned donor metadata declares `AXM_LIVING_CITY_SIM_FULL_HISTORY_ARCHIVE_v0_11_0(1).zip` with SHA-256 `a62dce40aa8c456e9f8b22bfb832df965b829a91d44e36ab554da4b9ee3de7f7` and explicitly records `historyCopiedIntoRepository: false`. The supplied connected monolith contains zero entries with that archive filename.

Therefore this cycle adds an alternate *evidence route*, not a Living City promotion.

## Improvement

Added a fail-closed `historical_fixture_routes` analyzer that distinguishes:

1. `exact-historical-artifact` — an observed historical value preserved locally whose bytes match a full-SHA-pinned donor artifact; and
2. `candidate-gap` — a candidate for which no exact historical value has yet been inspected.

The analyzer computes the local Git blob identity from bytes, checks the donor commit/blob structure, blocks path traversal, and refuses candidate-gap promotion.

The generated evidence records one valid independent route (FrameState v0.1 positive control) and one unresolved candidate gap (Living City world v0.1.0).

## Verification

Focused authored verification before publication:

- 7/7 focused tests passed locally, including a checked-in-evidence drift regression;
- generated JSON parsed successfully;
- FrameState positive-control local blob matched `3a6f64e8f0355812360abd0546f2b997cdb0db28`;
- Living City sealed-history archive filename had 0 entries in the supplied connected monolith.

Repository-wide CI remains the merge gate after publication.

## Truth boundary

This layer proves only a route for exact fixture provenance. It does **not**:

- admit a new generation;
- admit a migration path;
- prove migration execution;
- prove semantic equivalence;
- prove authorship from SHA-1 alone;
- make the Living City candidate chain experiment-ready;
- copy or implement Adapter & Translation Garden behavior.

The sealed history archive remains useful evidence if later supplied, but it is no longer conceptually treated as the only possible route to historical fixture provenance.

## AXM root gate

- **Truth:** exact bytes and pinned donor identity are required; Living City remains explicitly ungrounded at the historical-value layer.
- **Agency / non-domination:** no donor, runtime, install, publish, user-data, merge/canon, or migration authority is added.
- **Continuity:** all existing historical fixtures, admissions, HOLDs, lineages, and source references remain unchanged.
- **Wisdom before speed:** repair the evidence prerequisite before attempting to promote the tempting five-generation Living City candidate.

Merge only if repository-wide CI passes and these boundaries remain true.
