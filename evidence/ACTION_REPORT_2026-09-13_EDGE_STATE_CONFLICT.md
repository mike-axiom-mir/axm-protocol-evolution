# Action Report — contradictory adjacent-edge state rejection

Date: 2026-09-13

## Bounded question

Can Protocol Evolution accidentally treat one declared adjacent edge as both an admitted migration path and an investigated `HOLD` without invalidating readiness?

This is an evidence-integrity question inside Protocol Evolution. It does not generate adapters, execute migrations, or replace Adapter Translation Garden.

## Falsifier defined before implementation

Construct one valid two-generation lineage where the exact same ordered edge appears in both catalogs:

- one syntactically valid migration-path admission with evidence references; and
- one syntactically valid `HOLD` investigation with evidence references, finding, and blocker.

If `analyze_chain_experiment_readiness()` still returns `valid: true` or allows `chain_experiment_input_ready: true`, the evidence layer fails the falsifier. The same edge cannot truthfully be both admitted and held at the same time.

## Finding before change

The analyzer validated duplicate admissions and duplicate investigations independently, but it did not compare the two catalogs against each other. Because admissions are processed first, a later `HOLD` record for the same edge could coexist in the parsed result without producing a validation failure. The current checked-in corpus does not contain such a contradiction, but the contract permitted one.

## Improvement

`protocol_evolution.migration_paths.analyze_chain_experiment_readiness()` now rejects a valid `HOLD` investigation when its exact `(lineage_id, source_generation, target_generation)` edge is already admitted.

The failure is explicit:

`conflicting-admission-and-hold:<lineage>:<source>:<target>:<path_id>:<investigation_id>`

The conflicting HOLD record is not counted as a valid investigation, and any catalog containing the contradiction is invalid, which keeps chain-experiment input readiness false.

## Regression evidence

Added `tests/test_edge_state_conflict.py` with two bounded checks:

1. a synthetic two-generation edge that is simultaneously admitted and held must fail closed;
2. the current checked-in catalogs remain valid and contain no admission/HOLD conflict.

No historical fixture, lineage declaration, migration admission, HOLD investigation, source reference, or donor artifact was rewritten.

## Donor boundary

Adapter Translation Garden remains the live adapter / translation implementation donor. Its runtime can list and explicitly run working organs while shadow organs refuse execution; Protocol Evolution does not copy that machinery here. This cycle changes only the semantic consistency rules for Protocol Evolution's evidence catalogs.

## Limitations

This improvement proves only catalog-state consistency for the same exact declared adjacent edge. It does not:

- independently authenticate evidence references;
- decide whether an admission should supersede an older historical HOLD record in some future append-only history model;
- prove migration execution;
- prove whole-state semantic equivalence;
- prove chain-vs-direct equivalence;
- create the missing fifth FrameState project-schema generation;
- repair the still-HOLD FrameState v0.1→v0.2, FrameState v0.2→v0.4, or City G1→G2 edges.

A future design that wants to preserve both historical HOLD and later ADMIT states will need an explicit supersession/history contract rather than two simultaneously active catalog claims.

## Root gate

**Truth:** contradictory active claims for one edge now invalidate the evidence state rather than being silently tolerated.

**Agency / non-domination:** no migration, donor mutation, publication, install, network, or canon authority is added.

**Continuity:** all existing fixtures, lineage ordering, admissions, investigations, and source lineage remain unchanged; the validation rule and regression evidence are additive.

**Wisdom before speed:** strengthen the measurement layer before expanding the migration experiment or inventing a fifth generation.

Merge is justified only if the regression and repository verification pass. Otherwise this work remains held/open.
