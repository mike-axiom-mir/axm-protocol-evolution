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

`v3 > v2` never implies that v3 is a semantic superset of v2. Compatibility is established by explicit claims, capabilities, fixtures and tests.
