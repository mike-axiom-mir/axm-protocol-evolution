# Action Report — capability evidence threshold

Date: 2026-09-15
Status: implementation complete; root/CI gate passed at reviewed PR head

## Bounded question

Can exact capability-id/version agreement be reported as `SAME` when the caller explicitly requires execution-grounded capability evidence but one or both sides only have declaration-level evidence?

## Falsifier defined before implementation

The improvement fails if any of these occur:

1. exact id/version agreement can still return `SAME` when the requested evidence threshold is `executed` and either side is only `declared`;
2. exact id/version agreement with execution-grounded evidence on both sides cannot return `SAME`;
3. an observed version mismatch is weakened from `UNSUPPORTED` merely because evidence is below the requested threshold;
4. a required capability absent from a complete inventory stops being `UNSUPPORTED`;
5. a required capability absent only from an explicitly incomplete inventory stops being `AMBIGUOUS`;
6. existing callers that do not request an execution threshold change behavior;
7. malformed evidence-level vocabulary is silently accepted as compatibility evidence.

This falsifier was committed as the first branch commit before implementation.

## Grounded trigger

FrameState commit `41c9c6827e64613b523b28536ab864dddf046d93` exposes `timeline.integer-sample` through `AXM_MODULE.json` with callable schema `axm.callable-capability/v0.1` and an evidence note saying the source is executable and regression-covered. The same descriptor's truth boundary explicitly says that the descriptor existing does not by itself prove Monolith execution. Protocol Evolution therefore needs a way to distinguish exact declaration agreement from a caller's stronger requirement for execution-grounded evidence without falling back to product/schema version inference.

This cycle does not claim that two independent FrameState generations executed the capability, does not create a new historical generation, and does not promote any migration path. The exact donor descriptor is the grounding example for the semantics, not privileged truth.

## Implemented delta

- capability inventories and exact version matching remain the negotiation floor;
- `minimum_evidence` is optional and defaults to `declared`;
- per-capability evidence can be supplied for each side as `declared` or `executed`;
- exact declaration matches remain visible under `shared`;
- only exact pairs meeting the requested evidence threshold appear under `qualified_shared`;
- required exact-version pairs below an explicitly requested threshold produce `AMBIGUOUS` through `insufficient_evidence_required` plus side-specific `evidence_shortfalls`;
- observed version mismatch and complete-inventory absence remain `UNSUPPORTED`;
- incomplete-inventory absence remains `AMBIGUOUS`;
- unknown or stale evidence declarations are rejected instead of silently contributing compatibility evidence;
- existing callers retain declaration-level semantics by default.

## Verification

PR-head GitHub Actions completed successfully on the implementation head:

- repository `verify` workflow: **success**, including the Python 3.11 / 3.12 / 3.13 foundation matrix and the existing exact-donor replay jobs;
- dedicated `replay-framestate-v02-future-field` workflow: **success**;
- four new foundation regressions cover declaration-only ambiguity under an execution threshold, execution-grounded exact agreement, version-mismatch precedence, and invalid evidence vocabulary;
- existing capability/inventory regressions remain in the same suite and passed.

A final overlap scan found this PR as the only open Protocol Evolution lane and `main` remained at the tested base `342bcde8e0e3e3b1d7460ed90db701177e501df8` before the evidence-only finalization commit.

## Limits

This change does **not** prove FrameState capability execution merely from `AXM_MODULE.json`, does not authenticate caller-supplied evidence labels, does not define universal evidence levels beyond the current two-state vocabulary, does not infer version ranges, and does not prove whole-product compatibility. It changes no historical fixture, lineage, path admission, HOLD result, migration execution result, or candidate promotion state.

## Donor / authority boundary

Adapter & Translation Garden remains the adapter/translation implementation owner. No adapter, migration router, canonical-state mutation, install, publish, network, merge/CANON, or user-data authority is added.

## Root gate

- Truth: PASS — declaration equality can no longer satisfy a caller's explicitly stronger execution-evidence requirement.
- Agency / non-domination: PASS — the stronger threshold is opt-in and visible; no hidden promotion occurs.
- Continuity: PASS — default behavior remains backward-compatible and historical/source lineage is untouched.
- Wisdom before speed: PASS — the change adds one bounded semantic distinction instead of inferring execution from product/schema/version or descriptor presence.

Merge is justified only if the final PR head remains green after this evidence-only report finalization.
