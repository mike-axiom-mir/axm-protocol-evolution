# Action Report — foundation/semantic-survivability-v0.1

Date: 2026-09-12

## Question tested

Can a migration remain syntactically readable while silently changing meaning?

## Donor systems inspected

- `mike-axiom-mir/axm-collaboration-platform`: Adapter & Translation Garden modules 029, 030 and 070.
- `mike-axiom-mir/axm-city-multiplayer`: historical direct UDP handshake and later ACK-gated admission semantics.
- `mike-axiom-mir/axm-framestate`: v0.1-v0.5 project-reader compatibility and v0.4-and-earlier vs v0.5 speech-default semantics.

## Exact delta

This branch adds a bounded compatibility research floor: seven compatibility states, caller-owned semantic projection, opaque unknown-field preservation, exact capability negotiation, migration receipts with digests, four real generation fixtures across two donor repositories, a deterministic survivability matrix, and CI on Python 3.11/3.12/3.13.

## Falsifier

If a naive FrameState v0.4 -> v0.5 schema-label change is classified as meaning-preserving, the experiment fails. Expected result: `AMBIGUOUS`, because undeclared speech changes effective engine from `espeak` to `native`. Adding explicit `engine: espeak` must classify as `LOSSLESS_MIGRATION`.

## Evidence state

Authored fixture tests passed locally before commit. CI is required as an independent repository-environment confirmation. Passing these tests establishes only a bounded fixture-tested claim; it does not establish donor adoption.

## Known gaps

- Research ladder target is five real generation fixtures; only four are admitted here. The fifth remains explicitly open.
- No Adapter Garden code is copied or executed.
- No migration touches donor repositories or canonical user data.
- Capability negotiation uses exact capability versions only.
- The matrix compares declared semantic claims; it is not yet a full donor-runtime execution harness.
- No claim is made that every semantic difference is automatically discoverable.

## Root check

**Truth:** unknowns and unsupported states remain visible; the fifth fixture is not fabricated.

**Agency:** no migration, merge, install, publish, network or canon authority is granted by this code.

**Continuity:** donor identity and source refs are retained; fixtures append rather than rewrite donor history.

**Wisdom before speed:** the branch tests one small falsifiable semantic break before attempting generalized migration machinery.
