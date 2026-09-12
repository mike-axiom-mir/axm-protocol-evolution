# Compatibility states

The initial vocabulary is deliberately small.

| State | Meaning |
|---|---|
| `SAME` | No relevant semantic delta was observed. |
| `LOSSLESS_MIGRATION` | Shape changed, but the tested meaning survived. |
| `LOSSY_VISIBLE` | Meaning or information was lost and the loss is explicit. |
| `UNKNOWN_FIELD_PRESERVED` | An implementation carried state it did not understand without erasing or reinterpreting it. |
| `UNSUPPORTED` | A required capability or interpretation is not implemented by one side. |
| `AMBIGUOUS` | Evidence permits multiple materially different interpretations. |
| `REFUSE` | Continuing would require pretending compatibility, inventing meaning, or violating a declared boundary. |

These are evidence labels, not a maturity ladder. `REFUSE` can be the safest result when no truthful translation exists.

## Comparability boundary

Whether two generations are meaningfully comparable is decided **before** assigning a compatibility state. A City Multiplayer handshake and a FrameState project do not become `UNSUPPORTED`, `AMBIGUOUS`, or a new compatibility state merely because both are present in the same research corpus. They are different domains, so the matrix records `comparable: false`, `state: null`, and an explicit reason.

This keeps the compatibility vocabulary closed until evidence justifies changing it. Tooling must not emit undeclared state strings to represent an evaluation that never happened.

`v3 > v2` never implies that v3 is a semantic superset of v2. Compatibility is established by explicit claims, capabilities, fixtures and tests.
