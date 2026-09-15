# Capability negotiation

Compatibility is negotiated from explicit capabilities, not inferred from product or protocol version numbers.

Each side advertises a map of `capability-id` to `capability-version`.

Negotiation computes the exact shared pairs. Required capability evidence now has three distinct non-success surfaces:

- **observed absence or observed version mismatch** -> `UNSUPPORTED`;
- **required capability absent from an explicitly incomplete inventory** -> `AMBIGUOUS`, with the capability listed under `unobserved_required` rather than `missing_required`;
- **exact id/version agreement below an explicitly requested evidence threshold** -> `AMBIGUOUS`, with the capability listed under `insufficient_evidence_required` rather than being promoted to `SAME`.

Existing callers remain complete-by-default and declaration-level-by-default. Therefore a required capability absent from either supplied inventory still produces `UNSUPPORTED` unless that side is explicitly marked incomplete, and exact id/version agreement still behaves as before unless a caller explicitly requests stronger evidence.

## Evidence threshold

The first evidence vocabulary is deliberately small:

- `declared` — the capability/version pair is present in the supplied inventory;
- `executed` — the caller has stronger execution-grounded evidence for that exact capability/version pair.

`minimum_evidence="declared"` is the backward-compatible default. A caller may instead request `minimum_evidence="executed"` and provide per-capability evidence maps for each side. Exact declaration agreement below that threshold remains visible under `shared`, but only pairs meeting the requested threshold appear under `qualified_shared`.

A requested evidence threshold is not inferred from repository age, schema version, product version, capability description, or declaration presence. Unknown evidence-level vocabulary is rejected rather than silently promoted.

This first implementation still requires exact capability-version agreement. Future evidence may justify richer compatibility ranges; version ranges are not assumed.

## Grounded FrameState observation

A real donor pair demonstrates why both inventory completeness and evidence strength matter. FrameState commit `60ea68ba72e4ad4df8dc5746c6bb18fcd6569a34` and later commit `41c9c6827e64613b523b28536ab864dddf046d93` both expose canonical project schema `axm.framestate.project/v0.5`. The later commit adds `AXM_MODULE.json`, including a callable declaration for `timeline.integer-sample`; the earlier exact commit has no `AXM_MODULE.json` file.

That historical absence is **not** proof that the underlying capability did not exist. It is only absence of a capability declaration at the inspected commit. Therefore product/schema-version equality cannot supply the missing evidence, and incomplete capability inventories must remain explicitly unjudged rather than being relabeled incompatibility.

The later `AXM_MODULE.json` also keeps a second boundary explicit: its descriptor says the integer sampler is source-executable and regression-covered, while its truth boundary says the descriptor existing does not by itself prove Monolith execution. Declaration agreement and execution-grounded agreement are therefore distinct evidence claims. Protocol Evolution can now represent that distinction when a caller explicitly asks for execution-level evidence instead of silently treating descriptor equality as stronger proof.

This observation does not prove historical capability absence, independent execution by two generations, whole-product compatibility, universal capability semantics, or any migration/CANON authority.
