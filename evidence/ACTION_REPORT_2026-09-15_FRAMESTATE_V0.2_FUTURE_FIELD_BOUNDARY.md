# Action Report — FrameState v0.2 future-field boundary

## Bounded question
Can the generic unknown-field survivability question be grounded against a real AXM donor pair by taking a field that actually exists in later FrameState (`audio[*].engine`) and presenting it to the exact admitted FrameState v0.2 donor, without fabricating a historical fixture or pretending refusal is opaque preservation?

## Falsifier defined before implementation
This cycle fails or must be reinterpreted if any of the following occurs:

1. the exact v0.2 donor checkout or its canonical-normalizer Git blob does not match the already admitted donor identity;
2. the later exact donor/example used to establish `audio[*].engine` as a real later field does not match its pinned Git identity;
3. the admitted v0.2 fixture no longer normalizes successfully under the exact v0.2 donor as a positive control;
4. adding only the later `engine` field causes the v0.2 donor to silently drop or reinterpret it and still return normalized state;
5. the v0.2 donor mutates the supplied input before refusing;
6. a refusal is mislabeled as `UNKNOWN_FIELD_PRESERVED`, migration evidence, whole-project incompatibility, or proof that no external intermediary could preserve the field;
7. a synthetic future-enriched probe is promoted into a historical generation fixture, migration-path admission, or source-lineage claim;
8. Adapter & Translation Garden code is copied or reimplemented to manufacture a passing bridge.

A grounded positive result for this question is narrower: the exact old donor either preserves the real later field opaquely or explicitly refuses it without mutation. Silent loss/reinterpretation is the foundation failure this experiment is designed to detect.

## Current evidence before implementation
- The admitted FrameState v0.2 fixture contains a speech event but no `engine` field.
- FrameState at the exact later donor commit `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34` contains `examples/native_speech.json` with explicit `"engine": "native"` on a speech event.
- Source inspection of the exact v0.2 donor at `5d46363fb30bf5d30198b8cdec473d3bb9ba6287` shows speech-event fields are closed and do not include `engine`; executable behavior had not yet been recorded in Protocol Evolution.
- Protocol Evolution's existing `carry_unknown_fields()` test is synthetic and proves only the generic helper contract, not FrameState donor behavior.

## Grounded result
The exact-donor replay verifies both donor checkouts and the admitted v0.2 fixture by pinned Git identity. The untouched admitted v0.2 fixture normalizes successfully and deterministically under the exact v0.2 donor.

A synthetic probe is then derived by adding only the real later `engine="native"` field to that fixture's existing speech event. The exact v0.2 donor returns its explicit unsupported-field error. The replay gate requires the machine-readable result to say `old_intermediary_outcome: REFUSE`, requires the probe to remain unchanged, and rejects any silent drop or reinterpretation. The dedicated exact-donor workflow passed those assertions.

Therefore this real old-intermediary boundary demonstrates **safe refusal**, not opaque preservation. It complements rather than upgrades the generic synthetic `carry_unknown_fields()` preservation test.

## Verification
- exact v0.2 donor: `5d46363fb30bf5d30198b8cdec473d3bb9ba6287`;
- exact later donor: `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`;
- exact donor file/blob identities are checked before execution;
- admitted v0.2 fixture identity is checked before execution;
- exact future-field replay workflow passed, including explicit `REFUSE`, no mutation, no silent drop, and no reinterpretation assertions;
- repository `verify` workflow passed on Python 3.11, 3.12, and 3.13 together with all pre-existing exact-donor replay jobs.

## Limitations
This does not prove that every FrameState future field will be refused, that an external translation bridge cannot safely preserve or translate `engine`, that the v0.2 and later projects are wholly incompatible, or that refusal is preferable to opaque preservation in every protocol. The synthetic probe is not historical state. No migration path or generation is admitted by this result.

## Donor boundary
Protocol Evolution observes and classifies the compatibility boundary only. It does not add a FrameState migration/adapter and does not duplicate Adapter & Translation Garden. The probe created by this experiment is synthetic test input derived from an admitted fixture plus one real later field; it is not historical evidence.

## Root gate
- **Truth:** real exact-donor behavior is distinguished from the synthetic preservation helper; refusal is not mislabeled preservation.
- **Agency / non-domination:** read-only donor replay grants no migration, install, publish, or CANON authority.
- **Continuity:** historical fixtures, admissions, and source lineage remain unchanged.
- **Wisdom before speed:** one real future-field boundary is now grounded without manufacturing a bridge to improve a metric.

Result: roots permit integration if the final head remains green and non-overlapping.
