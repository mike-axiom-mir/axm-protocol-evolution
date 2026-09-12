# Action Report — migration receipt binding verifier

Date: 2026-09-12

## Question tested

Can a migration receipt prove that it still binds to the same canonical source/target values and canonical receipt content without pretending that a plain SHA-256 self-digest proves authorship, execution, original serialization bytes, or semantic truth?

## Falsifier defined before implementation

This cycle fails if any of these conditions hold:

1. a receipt verifies against a different supplied target value;
2. mutating a recorded receipt field without updating the receipt digest still verifies;
3. adding an out-of-contract field and recomputing the self-digest silently expands the receipt contract;
4. the verifier claims that a self-consistent receipt proves authorship or semantic correctness.

A deliberate negative-boundary test also rewrites the compatibility state and recomputes the plain self-digest. That rewritten receipt is expected to remain *binding-valid* because SHA-256 is not a signature. The verifier must therefore keep `authenticity_proven: false` and `semantic_truth_proven: false` visible.

## Repository and donor inspection

- Current `main` head and newest merged protocol-evolution work were inspected before editing.
- No open pull request occupied this lane.
- The newest matrix work explicitly leaves the five-generation chain-vs-direct experiment open.
- Adapter & Translation Garden remains the implementation donor and continues to own translation/migration implementation capabilities and proof packets.
- This cycle does not copy or execute Adapter Garden code. It strengthens only this repository's own evidence-receipt boundary.

## Exact delta

- Added `verify_migration_receipt_binding()`.
- Verification checks the existing v0.1 receipt contract shape, declared compatibility-state vocabulary, SHA-256 field shape, canonical receipt self-digest, and optional supplied source/target canonical-value digests.
- The runtime result explicitly declares the bounded scope: `receipt-self-digest-and-supplied-payload-identity`.
- The result always states that authenticity and semantic truth are not proven by this verifier.
- Added five focused regression tests covering valid binding, wrong-target rejection, mutation detection, out-of-contract field rejection, and the self-consistent-rewrite limitation.
- README now states the receipt claim and limitation directly.

## Evidence state before merge

The branch must pass the existing GitHub verification workflow before merge. CI success proves only that the authored regressions and existing repository tests pass in the configured Python environments. It does not upgrade the receipt into a signature, trusted timestamp, execution proof, byte-for-byte serialization proof, or semantic oracle.

## Known limits

- SHA-256 here is an integrity/binding primitive over canonical JSON values, not identity authentication.
- Canonical JSON intentionally normalizes representation details such as object key order and insignificant whitespace; original serialized bytes are not proven.
- A party able to rewrite the receipt can recompute its self-digest.
- The verifier does not prove that the named transformer executed.
- The verifier does not independently judge whether `compatibility_state`, losses, ambiguities, or assertions are semantically correct.
- No donor repositories or canonical user data are modified.
- The five-generation chain-vs-direct migration experiment remains open.

## Root check

**Truth:** the verifier exposes what a plain canonical-content digest can and cannot prove; the negative-boundary test prevents a self-hash from being mislabeled authentication or byte-for-byte serialization evidence.

**Agency / non-domination:** the receipt grants no merge, migration, execution, device, network, publish, or canon authority.

**Continuity:** the existing v0.1 receipt schema remains unchanged; this adds verification around the current contract rather than silently rewriting historical receipts.

**Wisdom before speed:** strengthens the evidence substrate before using receipts in the larger chain-vs-direct experiment.
