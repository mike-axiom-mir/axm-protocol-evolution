# Action Report — Candidate Promotion Provenance Readiness

Date: 2026-09-13
Status: bounded evidence-policy repair; no admission change

## Bounded question

After the repository established that one exact historical artifact can ground fixture provenance without requiring a sealed all-history archive, can `candidate_promotion.py` still treat history-archive availability as a mandatory condition for generation readiness?

Current state says yes: the candidate promotion analyzer computes generation readiness from `historical_source AND history_archive_available`. That is stricter than the later independent historical-fixture route evidence, which explicitly records that a full history archive is not mandatory for exact fixture provenance.

## Falsifier defined before implementation

The improvement fails if any of these conditions remain possible:

1. a candidate can become generation-ready merely because a declared history archive is available, while no independent exact historical fixture provenance route is ready;
2. a candidate with an exact observed historical value and a provenance-ready independent route remains blocked solely because the sealed all-history archive is unavailable;
3. a candidate assessment's source repository, commit, candidate id, or source version can disagree with the historical-fixture route it relies on;
4. candidate promotion can proceed when the lower historical-fixture-route evidence layer is invalid;
5. a `candidate-gap` route can masquerade as provenance-ready;
6. current Living City v0.1.0 changes from HOLD or gains generation/path admission without new historical evidence;
7. migration-path readiness can become true without both generation provenance readiness and exact adjacent target execution evidence.

A synthetic unit-control must demonstrate that archive unavailability alone is not a blocker when exact historical provenance is independently ready. The real Living City assessment must remain HOLD because its historical value is unobserved and its independent route is not provenance-ready.

## Repository and donor boundary read first

Protocol Evolution remains the cross-repository semantic compatibility research layer. Adapter & Translation Garden remains the adapter/translation implementation donor. This cycle changes readiness composition only; it does not copy or execute adapter/migration implementation.

Existing historical fixtures, generation manifests, lineages, migration-path admissions, HOLD investigations, donor references, monolith candidate observations, and source lineage must remain unchanged.

## Intended improvement

Bind each candidate promotion assessment to the matching historical-fixture route by candidate id, source version, repository, and commit. Derive generation readiness from:

- an actually observed historical source value; and
- a provenance-ready exact historical-fixture route.

History-archive availability remains recorded evidence but becomes neither necessary nor sufficient for generation readiness.

## Truth boundary

Passing this repair proves only that candidate promotion readiness composes the repository's current provenance policy consistently. It does not admit a generation, admit a migration path, prove migration execution, prove semantic equivalence, authenticate authorship, or make the five-generation chain experiment ready.

## AXM root gate

- **Truth:** archive availability must not masquerade as provenance, and archive absence must not override stronger exact-artifact provenance.
- **Agency / non-domination:** no canon, merge, migration, install, publish, network, device, or user-data authority is added.
- **Continuity:** existing historical artifacts and donor lineage remain unchanged; only readiness composition is repaired.
- **Wisdom before speed:** reconcile the newer provenance rule before attempting any Living City promotion.

Merge only if focused falsifier regressions and repository-wide verification pass and current Living City maturity remains unchanged.
