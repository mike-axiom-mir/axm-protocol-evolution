# Action Report — executed path receipt binding

Date: 2026-09-15

## Bounded question

Can the one admitted and independently replayed FrameState v0.4 -> v0.5 execution produce a migration receipt that binds exactly to the admitted source fixture and the retained observed target output, without turning a self-hash into proof of execution, authorship, whole-project semantic equivalence, or CANON authority?

## Why this is the smallest unresolved question

Protocol Evolution already has:

- one admitted adjacent path (`framestate-v0.4-to-v0.5-canonical-normalization`);
- retained exact execution evidence for that path;
- independent exact-donor CI replay of the same source -> output behavior;
- generic migration-receipt binding and receipt-chain verification.

The missing connection is whether the generic receipt contract can be grounded in the one real executed path rather than remaining demonstrated only with synthetic/demo payloads.

Adapter & Translation Garden remains the migration/translation implementation donor. This cycle must not copy its implementation or invent another migration runtime.

## Falsifier defined before implementation

The improvement fails closed if any of the following is possible:

1. a retained receipt binds while its `source_digest` differs from the canonical digest of the exact admitted FrameState v0.4 fixture;
2. a retained receipt binds while its `target_digest` differs from the canonical digest of the exact retained v0.5 execution output;
3. the receipt is attached to an unknown/unadmitted path or the wrong lineage/source/target generation;
4. a receipt can claim a different compatibility state, transformer identity, checked semantic assertion, loss, or ambiguity merely by recomputing its self-digest and still pass the executed-path binding;
5. the executed-path binder accepts a path without successful retained execution evidence;
6. receipt evidence promotes any existing HOLD edge, changes migration-path admission, changes historical fixtures/source lineage, or makes the larger chain experiment input-ready;
7. any output claims the receipt self-digest proves authorship, transformer execution, semantic truth, direct-vs-chain equivalence, whole-project equivalence, CANON authority, or Adapter Translation Garden ownership.

A positive result must require all of these identities to agree at once: admitted path, execution observation, admitted source fixture, retained observed target output, and migration receipt.

## Expected bounded result

If the current evidence is coherent, the FrameState v0.4 -> v0.5 receipt should bind to:

- source generation: `framestate-project-v0.4`;
- target generation: `framestate-project-v0.5`;
- source canonical digest: `sha256:ac55e91b3e17ca1cb6e996435a17b0fdbaf8001d480cb6d1932778f9ed3a1ea8`;
- target canonical digest: `sha256:102125a406d95a3738736d11505a340e8356efaf558ebc255d0d14c3058923a0`;
- compatibility state: `LOSSLESS_MIGRATION` only for the separately observed `undeclared_speech_engine=espeak` preservation claim.

The receipt remains evidence about identity and declared semantics, not independent proof that the donor executed. Execution proof remains in the separate exact execution/replay evidence.

## Root gate before implementation

- **Truth:** bind the generic receipt primitive to exact real evidence; fail on rehashed semantic drift.
- **Agency / non-domination:** no migration, install, publish, network, user-data, or CANON authority is added.
- **Continuity:** historical fixtures, manifests, lineages, path admissions, HOLD records, donor refs, and retained outputs must remain unchanged.
- **Wisdom before speed:** connect one real executed edge to receipts before attempting a larger receipt chain.

Implementation and merge are permitted only if the falsifier is exercised and repository-wide verification remains green.
