# AXM Protocol Evolution

Status: **research / non-canon**

`axm-protocol-evolution` studies whether independently evolving AXM systems can keep exchanging meaning across generations without silently dropping, inventing, or reinterpreting state.

It is a cross-repository compatibility laboratory. It does **not** own every project's schema, execute canonical migrations, or replace the Adapter & Translation Garden.

## Root boundary

Truth · Agency / non-domination · Continuity · Wisdom before speed

The roots are the merge gate. Passing tests proves only the claims those tests measure.

## First research floor

The bounded corpus now contains six real AXM generation fixtures from two repositories:

- City Multiplayer handshake generation 1;
- City Multiplayer handshake generation 2;
- FrameState project v0.1 semantics;
- FrameState project v0.2 semantics;
- FrameState project v0.4 semantics;
- FrameState project v0.5 semantics.

The original five-fixture corpus target is exceeded. **That is still not one five-generation migration chain.** The fixtures currently form two declared semantic lineages: City Multiplayer has 2 admitted handshake generations and FrameState has 4 admitted project generations. The longest current lineage is therefore 4, and the intended five-generation chain-vs-direct experiment remains HOLD until one real same-domain lineage reaches five admitted generations and migration paths are evidenced.

The current executable questions are:

1. Can a parser-compatible migration still change meaning?
2. Can unknown future fields survive an older intermediary?
3. Can two versions negotiate exact capabilities instead of assuming version numbers imply feature equivalence?
4. Can compatibility evidence be receipted without granting migration or canon authority?
5. Can two different schema versions preserve the same tested meaning?
6. Can a migration receipt prove that it still binds to the same canonical source/target values without pretending a plain hash proves authorship or semantic truth?
7. Can individually binding-valid migration receipts still fail to form a continuous declared chain?
8. Can a multi-fixture cross-domain corpus be prevented from masquerading as one five-generation migration lineage?
9. Can two same-domain generations with no shared tested semantic claim remain explicitly unjudged instead of being mislabeled incompatible?

The FrameState v0.2 and v0.4 fixtures deliberately test question 5: both preserve undeclared speech as eSpeak, while v0.5 changes that default to the native engine. Therefore a version-number change alone is not evidence of semantic change.

FrameState v0.1 predates that speech-default claim. Its exact historical `first_light.json` uses tone-only audio, and the matching v0.1 canonical reader accepts tone audio only. Therefore v0.1 versus later speech-default fixtures has **no common tested semantic claim** in this corpus. The matrix keeps those pairs unjudged rather than converting absence of evidence into `UNSUPPORTED`.

Receipt binding verification deliberately has a narrower claim: it checks the receipt's canonical JSON self-digest, contract shape, and optional supplied source/target value identity under the same canonical JSON encoding. It does **not** bind original whitespace/key-order bytes, authenticate who wrote the receipt, prove the transformer ran, or prove that the recorded compatibility state is semantically true.

Receipt-chain verification is narrower again: every receipt must pass the binding check, the first/last receipts can be bound to supplied endpoint values, and each receipt's target digest must exactly equal the next receipt's source digest. It does **not** prove the transformations ran, the semantic labels are true, or that a chained migration is equivalent or preferable to a direct migration.

Lineage readiness keeps another boundary explicit: total corpus size is not chain length. `fixtures/lineages.json` declares only the admitted research-fixture ordering within each semantic domain. It does **not** claim those fixtures cover every historical release, that the sequence is contiguous, or that migration paths exist between each pair.

## Donor boundary

The live implementation donor remains:

`mike-axiom-mir/axm-collaboration-platform/tools/adapter-translation-garden/`

Especially:

- module 029 — backward/forward compatibility matrix tester;
- module 030 — versioned schema migration generator;
- module 070 — strangler migration router (shadow-only).

This repository studies the general law of compatibility evolution and semantic survivability. It must not duplicate those adapter implementations.

## Run

No third-party runtime dependencies are required.

```bash
python -m unittest discover -s tests -v
python tools/survivability_matrix.py
python tools/lineage_readiness.py
```

## Current evidence claim

The bounded fixture tests currently establish narrow claims only:

> Serialization or parsing success does not prove semantic compatibility.

> A version-number difference does not prove semantic incompatibility.

> Same-domain membership does not prove two generations share a tested semantic claim; no shared claim remains visibly unjudged.

> A self-digest can bind a receipt to canonical content and supplied payload values, but it does not by itself prove authorship, execution, or semantic truth.

> Individually binding-valid receipts do not prove a continuous migration chain; adjacent target/source digests must also connect exactly.

> More than five real fixtures still do not prove one five-generation chain; same-lineage membership must be explicit and domain-consistent.

See `evidence/` for exact limits and action reports.
