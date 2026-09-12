# Action Report — receipt chain continuity

Date: 2026-09-12

## Question tested

Can individually binding-valid migration receipts still fail to form one continuous declared migration chain?

## Donor boundary inspected

The live Adapter & Translation Garden remains the migration implementation donor. Module 030 still owns migration-candidate generation and remains `decision_only`; Protocol Evolution does not copy, execute, or replace that implementation.

## Falsifier defined before implementation

Construct two individually self-consistent migration receipts where the first receipt's `target_digest` does not equal the second receipt's `source_digest`.

If the chain verifier reports that pair as a valid chain, this experiment fails.

## Exact delta

- added `verify_migration_receipt_chain()`;
- retained the existing per-receipt binding verifier as the lower-level contract;
- verifies optional supplied first-source and last-target canonical value identity;
- requires exact adjacent `target_digest -> source_digest` continuity;
- prefixes receipt-local failures with the receipt position;
- refuses an empty chain;
- explicitly reports that authenticity, transformer execution, semantic truth, and direct-migration equivalence are **not proven**;
- added six focused regressions for valid continuity, discontinuity, endpoint mismatch, mutated receipt binding, empty-chain refusal, and a self-consistent rewritten receipt whose semantic claim still is not independently proven.

## Evidence claim

A chain can be internally continuous at the receipt/digest layer only when each receipt is binding-valid and every adjacent digest joins exactly.

That is a structural evidence claim. It is not evidence that the transformer code actually ran, that the recorded semantic labels are correct, that the migration was lossless, or that a multi-step chain is equivalent to a direct migration.

## Why this belongs here

This is evidence about long-horizon compatibility and lineage continuity across migration generations. It does not generate migrations and therefore does not duplicate Adapter Translation Garden.

## Known gaps

- The full five-generation chain-vs-direct experiment remains open.
- No donor migration implementation is invoked by this experiment.
- No signature or trusted signer authenticates receipts.
- A party able to rewrite a receipt can recompute its plain digest.
- Digest continuity cannot detect a semantically wrong intermediate value when the receipts consistently describe that wrong value.
- No claim is made yet that a direct migration and an N-step chain preserve identical meaning.

## Root check

**Truth:** the result is limited to binding and digest continuity; semantic truth and execution are explicitly false claims.

**Agency / non-domination:** the verifier gains no migration, canon, merge, install, device, or network authority.

**Continuity:** it strengthens lineage evidence without rewriting historical fixtures or donor systems.

**Wisdom before speed:** it establishes the smallest prerequisite for the larger chain-vs-direct experiment instead of pretending that experiment already exists.
