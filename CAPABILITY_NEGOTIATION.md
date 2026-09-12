# Capability negotiation

Compatibility is negotiated from explicit capabilities, not inferred from product or protocol version numbers.

Each side advertises a map of `capability-id` to `capability-version`.

Negotiation computes the exact shared pairs. A required capability absent on either side produces `UNSUPPORTED`.

This first implementation deliberately requires exact capability-version agreement. Future evidence may justify richer compatibility ranges; version ranges are not assumed in v0.1.
