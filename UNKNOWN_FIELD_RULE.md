# Unknown-field rule

An implementation that does not understand a field must not silently erase, reinterpret, normalize, or claim authority over that field merely because it can parse the surrounding object.

Preferred states:

1. preserve the unknown field opaquely;
2. expose that it is unknown;
3. refuse if transporting it would be unsafe or dishonest.

Dropping unknown state by default is a foundation failure.

Opaque preservation is not understanding. It proves only that state owned elsewhere was carried without mutation inside the tested boundary.

## Grounded FrameState boundary

Protocol Evolution's generic `carry_unknown_fields()` helper demonstrates one explicit opaque-preservation mechanism, but that synthetic helper is not evidence about donor behavior.

The exact FrameState v0.2 donor at `5d46363fb30bf5d30198b8cdec473d3bb9ba6287` was therefore replayed against a synthetic probe derived from the admitted v0.2 fixture plus one field grounded in a real later donor: speech `engine="native"`, present in `examples/native_speech.json` at FrameState commit `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34`.

At that exact boundary the v0.2 donor **REFUSES** the later field as unsupported. The positive-control v0.2 fixture still normalizes, the future-field probe is unchanged by the failed attempt, and the replay gate rejects silent drop or reinterpretation.

That result is a safe refusal, not opaque preservation. It does not prove whole-project incompatibility, universal absence of an external bridge, or a historical migration path. The future-enriched probe is synthetic test input and is not a historical generation fixture.
