# Foundation

## Research question

Can independently evolving AXM systems keep exchanging meaning across versions without silently dropping, inventing, or reinterpreting state?

## What this repository owns

- compatibility semantics across repositories and generations;
- explicit compatibility-state vocabulary;
- semantic assertions separated from serialization shape;
- immutable historical generation fixtures;
- capability negotiation experiments;
- unknown-field preservation experiments;
- migration receipts and lineage evidence;
- long-horizon survivability matrices.

## What it does not own

- every project's schema;
- project-specific runtime authority;
- silent migration of canonical user data;
- rewriting historical artifacts into current shapes;
- a universal AXM schema;
- adapter implementations already owned by the Adapter & Translation Garden;
- canon, merge, install, publish, device, or network authority.

## Donor systems

### Adapter & Translation Garden

Implementation donor and reference system. This repository may compare against, call, or deliberately extract bounded donor ideas later, but does not become authority over that donor.

### City Multiplayer

First protocol-evolution donor. The historical handshake changed from a WELCOME-completes-admission model to a versioned HELLO -> WELCOME -> ACK -> admitted-peer model.

### FrameState

First semantic-migration donor. Project schemas v0.1-v0.5 remain readable, but speech default meaning changed: v0.4-and-earlier undeclared speech engines mean `espeak`; v0.5 undeclared speech engines mean `native`.

That makes FrameState a useful proof that a migration can parse successfully and still change meaning.

## Founding falsifiers

Reject or revise the foundation if:

1. a migration changes meaning without visible loss/ambiguity evidence;
2. unknown fields are dropped by default;
3. compatibility requires one central coordinator for every repository release;
4. fixture history is rewritten instead of appended;
5. a migration receipt cannot identify source, target and transformation;
6. version-number comparison is treated as capability proof.

## Evidence ladder

IDEA -> SOURCE-MAPPED -> CONTRACTED -> FIXTURE-TESTED -> ADVERSARIAL -> CROSS-IMPLEMENTATION -> CROSS-REPO -> REAL-ENVIRONMENT -> RETAIN/REVISE/RETIRE.

Passing one rung never silently grants the next.
