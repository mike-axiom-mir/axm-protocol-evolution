# Action Report — matrix domain boundary truth correction

Date: 2026-09-12

## Question tested

Can the survivability matrix represent pairs that are outside one another's semantic domain without inventing a compatibility state?

## Falsifier defined before implementation

This cycle fails if the matrix still emits a state string that is not one of the declared `CompatibilityState` values, or if cross-domain pairs are coerced into `UNSUPPORTED` merely to make every row have a state.

The concrete pre-existing counterexample was `NOT_COMPARABLE`: the matrix emitted it for City Multiplayer versus FrameState rows, while the repository's declared compatibility vocabulary and enum did not contain that state.

## Donor and boundary inspection

- Current repository head and newest merged work were inspected before editing.
- No open pull request occupied this lane.
- Adapter & Translation Garden remains the implementation donor. Module 029 already tests producer/consumer compatibility combinations; this cycle does not rebuild that machinery.
- This repository owns the meaning of its cross-repository evidence rows, so repairing the matrix result contract is inside its existing lane.

## Exact delta

- Bumped survivability-matrix evidence shape from `v0.1` to `v0.2`.
- Cross-domain rows now carry `comparable: false`, `state: null`, `reason: different-domain`.
- Comparable rows carry `comparable: true` and only declared compatibility states.
- Added a regression that every non-null emitted state belongs to `CompatibilityState`.
- Added a regression that a concrete City/FrameState pair remains unjudged rather than receiving a fake state.
- Preserved the exact prior checked-in matrix as `evidence/generation_matrix_v0.1.json` before updating current evidence.

## Test/evidence result

Local authored verification after the change: **12/12 tests PASS**.

The existing semantic-change, unknown-field, capability-negotiation, receipt, five-fixture, and checked-in-matrix tests continue to pass alongside the two new domain-boundary regressions.

GitHub CI is still required before merge; local success does not grant the next evidence rung.

## Evidence limit

`comparable: true` currently means only that two fixtures share the same declared `domain`. It does not prove that their semantic-claim sets are complete, that runtime interoperability was executed, or that `UNSUPPORTED` is the final long-term relation for every differing claim.

This cycle does not advance the open chain-vs-direct migration experiment. It repairs the truth boundary of the matrix that will later report such experiments.

## Root check

**Truth:** removes an undeclared pseudo-state instead of normalizing it into the vocabulary after the fact; unperformed comparisons remain visibly unperformed.

**Agency / non-domination:** no donor code, canonical user data, release, device, network, or merge authority is assumed.

**Continuity:** the v0.1 matrix is preserved as historical evidence; current evidence advances under a new schema version.

**Wisdom before speed:** repairs a small contract inconsistency before building more migration-chain machinery on top of it.
