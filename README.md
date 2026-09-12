# AXM Protocol Evolution

Status: **research / non-canon**

`axm-protocol-evolution` studies whether independently evolving AXM systems can keep exchanging meaning across generations without silently dropping, inventing, or reinterpreting state.

It is a cross-repository compatibility laboratory. It does **not** own every project's schema, execute canonical migrations, or replace the Adapter & Translation Garden.

## Root boundary

Truth · Agency / non-domination · Continuity · Wisdom before speed

The roots are the merge gate. Passing tests proves only the claims those tests measure.

## First research floor

The initial bounded experiment contains four real AXM generation fixtures from two repositories:

- City Multiplayer handshake generation 1;
- City Multiplayer handshake generation 2;
- FrameState project v0.4 semantics;
- FrameState project v0.5 semantics.

The research ladder calls for five real generations. The fifth fixture is intentionally **OPEN** rather than fabricated.

The first executable questions are:

1. Can a parser-compatible migration still change meaning?
2. Can unknown future fields survive an older intermediary?
3. Can two versions negotiate exact capabilities instead of assuming version numbers imply feature equivalence?
4. Can compatibility evidence be receipted without granting migration or canon authority?

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
```

## Current evidence claim

The foundation tests demonstrate a bounded claim only:

> Serialization or parsing success does not prove semantic compatibility.

See `evidence/ACTION_REPORT.md` for exact limits.
