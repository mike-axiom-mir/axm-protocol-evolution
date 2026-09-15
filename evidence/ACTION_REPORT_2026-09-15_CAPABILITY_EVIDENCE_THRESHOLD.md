# Action Report — capability evidence threshold

Date: 2026-09-15
Status: experiment in progress; merge gate pending

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

## Grounded trigger

FrameState commit `41c9c6827e64613b523b28536ab864dddf046d93` exposes `timeline.integer-sample` through `AXM_MODULE.json` with callable schema `axm.callable-capability/v0.1` and an evidence note saying the source is executable and regression-covered. The same descriptor's truth boundary explicitly says that the descriptor existing does not by itself prove Monolith execution. Protocol Evolution therefore needs a way to distinguish exact declaration agreement from a caller's stronger requirement for execution-grounded evidence without falling back to product/schema version inference.

This cycle does not claim that two independent FrameState generations executed the capability, does not create a new historical generation, and does not promote any migration path. The exact donor descriptor is the grounding example for the semantics, not privileged truth.

## Planned bounded delta

- keep capability inventories and exact version matching as the existing negotiation floor;
- add an optional minimum evidence threshold (`declared` by default, `executed` when explicitly requested);
- allow callers to state per-capability evidence for each side;
- report exact-version requirements below the requested threshold as explicit ambiguity, not incompatibility;
- preserve existing unsupported and incomplete-inventory behavior;
- add focused regressions and update capability-negotiation documentation.

## Donor / authority boundary

Adapter & Translation Garden remains the adapter/translation implementation owner. No adapter, migration router, canonical-state mutation, install, publish, network, merge/CANON, or user-data authority is added.

## Root gate before implementation

- Truth: declaration equality must not masquerade as stronger execution evidence.
- Agency / non-domination: callers choose the evidence threshold; no hidden promotion occurs.
- Continuity: default behavior remains backward-compatible and historical fixtures/source lineage remain untouched.
- Wisdom before speed: add the smallest evidence-sensitive negotiation rule instead of inferring execution from version or descriptor presence.
