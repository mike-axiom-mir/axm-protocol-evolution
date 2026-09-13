# Action Report — Historical Fixture Route / Generation Binding

Date: 2026-09-13
Status: bounded evidence-integrity improvement; no admission change

## Bounded question

Can an `exact-historical-artifact` route be internally valid as byte/provenance evidence while silently drifting away from the admitted generation manifest it is intended to support?

The current FrameState v0.1 route repeats repository, commit, source path, donor blob and local fixture path that also appear in the admitted generation manifest, but the route layer does not machine-bind those two declarations. A later edit could therefore leave both documents individually plausible while their identities disagree.

## Falsifier defined before implementation

The improvement fails if a route can remain generation-bound when any of these are true:

1. an exact historical route has no explicit binding to one admitted generation manifest;
2. a binding names an unknown route or unknown generation;
3. one exact route is bound more than once or one binding is duplicated;
4. route repository differs from the generation manifest repository;
5. route commit differs from the generation manifest `source_ref`;
6. route donor source path differs from the generation manifest `source_path`;
7. route donor blob differs from the generation manifest `source_blob_sha`;
8. route local `fixture_path` is not the exact generation directory plus the manifest's declared `artifact`;
9. a `candidate-gap` route is allowed to masquerade as an admitted-generation binding;
10. generation binding reports valid while the lower historical-fixture-route evidence is invalid.

The known-positive FrameState v0.1 control must bind exactly to `framestate-project-v0.1`. If this stronger contract cannot preserve that control, the hypothesis also fails.

## Repository and donor boundary read first

Protocol Evolution remains the cross-repository semantic compatibility research layer. This cycle changes only its evidence-consistency contract. It does not implement or execute migration adapters, and Adapter & Translation Garden remains the adapter/translation implementation donor.

The Living City route remains a `candidate-gap`; this cycle must not bind it to an admitted generation, create a historical value, admit a migration path, or advance chain readiness.

## Intended improvement

Add a small fail-closed binding layer between exact historical fixture routes and existing admitted generation manifests. The layer should verify that duplicated provenance fields agree and that the route points to the manifest's own local artifact path.

No existing historical fixture bytes, generation manifest identities, lineage order, migration-path admission, HOLD investigation, donor reference, or Living City candidate evidence may be rewritten to make the check pass.

## Truth boundary

A passing binding will prove only that an already-valid exact fixture-provenance route and an already-admitted generation manifest identify the same repository/ref/source-path/blob/local-artifact tuple.

It will not prove authorship, creation time, migration execution, semantic equivalence, generation admission correctness, migration-path admission, or chain-vs-direct equivalence.

## AXM root gate

- **Truth:** duplicated provenance declarations must agree or fail closed.
- **Agency / non-domination:** no canon, merge, migration, install, publish, network, device, or user-data authority is added.
- **Continuity:** existing fixtures, manifests, lineages, admissions, HOLDs and donor lineage remain unchanged; the binding is additive.
- **Wisdom before speed:** close this provenance-consistency gap before promoting any newly discovered historical candidate.

Merge only if the falsifier regressions and repository-wide verification pass and these boundaries remain true.
