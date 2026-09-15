# Capability negotiation

Compatibility is negotiated from explicit capabilities, not inferred from product or protocol version numbers.

Each side advertises a map of `capability-id` to `capability-version`.

Negotiation computes the exact shared pairs. Required capability evidence now has two distinct failure surfaces:

- **observed absence or observed version mismatch** -> `UNSUPPORTED`;
- **required capability absent from an explicitly incomplete inventory** -> `AMBIGUOUS`, with the capability listed under `unobserved_required` rather than `missing_required`.

Existing callers remain complete-by-default, so a required capability absent from either supplied inventory still produces `UNSUPPORTED` unless that side is explicitly marked incomplete.

This first implementation deliberately requires exact capability-version agreement. Future evidence may justify richer compatibility ranges; version ranges are not assumed.

## Grounded FrameState observation

A real donor pair demonstrates why evidence completeness matters. FrameState commit `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34` and later commit `41c9c6827e64613b523b28536ab864dddf046d93` both expose canonical project schema `axm.framestate.project/v0.5`. The later commit adds `AXM_MODULE.json`, including a callable declaration for `timeline.integer-sample`; the earlier exact commit has no `AXM_MODULE.json` file.

That historical absence is **not** proof that the underlying capability did not exist. It is only absence of a capability declaration at the inspected commit. Therefore product/schema-version equality cannot supply the missing evidence, and incomplete capability inventories must remain explicitly unjudged rather than being relabeled incompatibility.

This observation does not prove execution of `timeline.integer-sample`, historical capability absence, whole-product compatibility, or any migration/CANON authority.
