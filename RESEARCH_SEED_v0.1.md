AXM / AXIOM–MIR
RESEARCH SEED
Date: 2026-09-11

STATUS
------
RESEARCH SEED / NOT CANON / NOT BUILT / NO REPO CREATED BY THIS FILE

ROOTS
-----
Truth · Agency · Continuity · Wisdom before speed

FOUNDING RULE
-------------
This file preserves a research direction. It does not create authority, canon,
a merge decision, or a claim that the proposed architecture is correct.

Preserve existing AXM work. Do not rebuild working systems merely because this
research lane exists. Fresh evidence outranks this document.

REPO CANDIDATE
--------------
axm-protocol-evolution

FIELD
-----
Protocol & Compatibility Evolution

ESTIMATED MULTIPLIER
--------------------
9.8/10

1. CORE RESEARCH QUESTION
-------------------------
Can independently evolving AXM systems keep exchanging meaning across versions without silently dropping, inventing, or reinterpreting state?

2. WHY THIS COULD MULTIPLY AXM
------------------------------
AXM is growing faster than any one repo can remain static. Compatibility will
become a larger problem than file loss: old WALMI saves, old games, old organs,
future device bodies, schemas, invitations, evidence packets and state snapshots
must survive evolution.

Workshop already contains serious adapter and versioned-schema migration work.
Therefore this repo must research the GENERAL LAW of compatibility evolution,
not rebuild those adapters.

3. LIVE AXM OVERLAP / DONOR BOUNDARY
------------------------------------
Strong existing donor:
- axm-collaboration-platform/tools/adapter-translation-garden/
  - module 030: versioned schema migration generator
  - module 070: strangler migration router
  - translation-loss / ambiguity helpers and offline queue adapters.
- Universal Creation already has exact versioned interfaces/packages.
- City Multiplayer carries protocol/build compatibility.
- Factual/Living/Theme Park systems use save migrations.

New lane should own:
- compatibility semantics across repositories and generations;
- how meaning is preserved, refused, approximated or quarantined;
- protocol negotiation and capability discovery;
- long-horizon survivability tests.

DO NOT duplicate Adapter Translation Garden.

4. THIS REPO WOULD OWN
----------------------
- A compatibility-state vocabulary: SAME, LOSSLESS_MIGRATION,
  LOSSY_VISIBLE, UNKNOWN_FIELD_PRESERVED, UNSUPPORTED, AMBIGUOUS, REFUSE.
- Forward/backward compatibility fixtures.
- Capability/version negotiation.
- Unknown-field preservation.
- Long-lived corpus of old packets/saves.
- Migration-chain compression and migration-proof receipts.
- Compatibility stress experiments across N versions.

5. THIS REPO MUST NOT OWN
-------------------------
- Every project's schema.
- Silent automatic migrations of canonical user data.
- Rewriting historical artifacts to newest shape.
- One universal schema.
- Adapter implementation already owned by Workshop unless extracted deliberately.

6. WORKING HYPOTHESES
---------------------
- H1: Preserving unknown fields and explicit loss is more important than forcing every old object into the newest schema.
- H2: Compatibility can be tested as meaning preservation, not merely JSON parse success.
- H3: N-step migration chains eventually need compaction/direct migration evidence.
- H4: Capability negotiation is safer than assuming version numbers imply feature equivalence.
- H5: Old clients can remain useful when unsupported meaning is preserved rather than erased.

7. FALSIFICATION / STOP CONDITIONS
---------------------------------
- If a migration changes meaning without a visible loss/ambiguity record, fail.
- If compatibility requires central coordination of every repo release, reject the architecture.
- If unknown fields are dropped by default, reject.
- If an adapter cannot prove source identity and target semantics, keep it detached.
- If old fixtures are continually rewritten, the experiment has lost its evidence.

8. FIRST RESEARCH LADDER
------------------------
1. Build a corpus of 5 real AXM packet/save/schema versions from existing repos.
2. Define canonical semantic assertions independent of serialization shape.
3. Run old->new and new->old round trips and expose losses.
4. Test an unknown future field through an old intermediary.
5. Add capability negotiation between two versions with partially overlapping features.
6. Test 5-generation migration chain; compare chain vs direct migration.
7. Reuse Adapter Translation Garden as donor/reference, not dependency authority.
8. Publish a survivability matrix showing which generations can still interoperate.

9. FIRST ARTIFACTS TO CREATE
----------------------------
- `COMPATIBILITY_STATES.md`
- `SEMANTIC_ASSERTION.schema.json`
- `fixtures/generations/`
- `MIGRATION_RECEIPT.schema.json`
- `CAPABILITY_NEGOTIATION.md`
- `UNKNOWN_FIELD_RULE.md`
- `tools/survivability_matrix.*`
- `evidence/generation_matrix.json`

10. FIRST TEN QUESTIONS
-----------------------
1. What does 'same meaning' mean across schema versions?
2. When is loss acceptable if it is explicit?
3. Should unknown state be carried as opaque data rather than discarded?
4. Can an old runtime safely transport a future packet it cannot understand?
5. How are deprecated capabilities represented without pretending they vanished?
6. How do save migrations preserve rollback?
7. How do protocol and product versions differ?
8. When can two implementations claim compatibility?
9. How do we prevent migration code from becoming hidden authority?
10. What evidence justifies deleting an old migration path?

11. EVIDENCE LADDER
-------------------
0. IDEA — question only.
1. SOURCE-MAPPED — existing AXM overlap and relevant precedents identified.
2. CONTRACTED — exact inputs, outputs, authority and failure states declared.
3. FIXTURE-TESTED — deterministic authored fixtures pass and fail as expected.
4. ADVERSARIAL — counterexamples/failure injection tested.
5. CROSS-IMPLEMENTATION — a second implementation or independent verifier agrees
   on a bounded claim.
6. CROSS-REPO — at least two real AXM systems use the result without semantic
   rewriting.
7. REAL-ENVIRONMENT — tested on real users/hardware/networks/platforms where the
   field requires it.
8. RETAIN / REVISE / RETIRE — evidence decides whether the direction continues.

Passing one rung never silently grants the next.

12. ROOT CHECK
--------------
TRUTH
- Unknown, unsupported and conflicting states stay visible.
- A test proves only the claim it actually measures.

AGENCY
- Research output never grants itself execution, merge, device, network or
  CANON authority.
- Existing repo owners remain authoritative for their own systems.

CONTINUITY
- Preserve source identity, lineage, rollback and donor boundaries.
- New research must not require destructive migration of existing AXM work.

WISDOM BEFORE SPEED
- Prefer the smallest falsifiable experiment.
- No-change / HOLD is better than building a duplicate or misleading substrate.

13. REPO CREATION GATE
----------------------
Create the repo only as a cross-repo research layer. Before creation, confirm
Adapter Translation Garden remains the implementation donor and identify at
least three incompatible generations from two or more AXM repos to use as a real
fixture corpus.

14. FIRST FUTURE-BUILDER PROMPT
-------------------------------
/returncore /soulcheck /mergegate

You are opening research candidate `axm-protocol-evolution`.

Read this seed first. Then inspect current AXM repositories before creating code.
Treat semantic overlap as overlap even when filenames differ.

Your job is NOT to prove this idea correct.

1. Re-scan current AXM implementations and newest PRs.
2. Mark every relevant capability EXISTING / EXTEND / ADAPT / NEW / HOLD.
3. Choose the smallest unresolved research question from this seed.
4. Define the falsifier before implementation.
5. Build one bounded experiment.
6. Produce evidence and explicit limitations.
7. Do not merge, promote, install, migrate, publish, or declare CANON automatically.
8. If existing AXM work already closes the gap, stop and report that finding.

Return:
- question tested;
- donor systems inspected;
- exact delta;
- test/evidence result;
- what remains unknown;
- whether this candidate still deserves its own repository.

15. ACTION REPORT
-----------------
Created as a stronger future-start file.
No repository was created.
No implementation was claimed.
No existing AXM component was replaced.
The research direction remains optional until its repo-creation gate is met.
