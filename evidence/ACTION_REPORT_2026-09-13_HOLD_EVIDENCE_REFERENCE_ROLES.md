# Action Report — HOLD Evidence Reference Roles

Date: 2026-09-13

## Bounded research question

Can the three current HOLD migration-path investigations remain as undifferentiated evidence-reference bags after admitted migration-path evidence gained explicit one-to-one audit roles?

The previous cycle deliberately scoped role binding to admitted paths only. That left negative and incomplete evidence less auditable: a later reviewer could see why an edge was held, but still had to rediscover what each pinned donor reference was intended to contribute.

## Falsifier defined before implementation

This improvement fails if any evidence reference on a current HOLD investigation cannot be assigned exactly one grounded, non-promoting audit role without inventing donor evidence.

The analyzer must also fail closed if a HOLD role record:

- omits a declared investigation reference;
- adds an unrelated reference;
- assigns one reference twice;
- uses an unknown role or unknown investigation id;
- binds a non-HOLD investigation status;
- passes while the lower donor-repository binding layer is invalid.

A passing role catalog must never convert a HOLD investigation into an admitted migration path or advance chain-experiment readiness.

## Grounded donor re-read

### FrameState v0.1 -> v0.2

The v0.2 changelog says the v0.2 canonical schema exists alongside v0.1 compatibility. The v0.2 canonical reader accepts both schemas and returns the incoming schema value in normalized project state. Those sources ground backward-reader compatibility, not an automatic v0.1 -> v0.2 schema migration.

The existing full-SHA compare remains only the bounded historical interval previously inspected for stronger migration evidence.

### FrameState v0.2 -> v0.4

The recovery changelog and recovery commit explicitly say the lost uncommitted v0.3 body was rebuilt forward from surviving material rather than claimed as byte-for-byte resurrection. The later canonical reader accepts older project schemas, but reader acceptance does not by itself demonstrate transformation of the admitted v0.2 project artifact into a v0.4 artifact.

The existing full-SHA compare remains search-scope evidence for the bounded donor-history audit.

### City Multiplayer G1 -> G2

The G1 handshake admits a peer after authenticated HELLO/WELCOME. The later transition introduces protocol version 2 and authenticated ACK before admission. Its regression checks both ACK-required admission and rejection of a protocol-version-1 HELLO by the v2 host.

That grounds a protocol baseline, a transition, and an explicit incompatibility check; it does not create a dual-stack bridge.

## Implementation

Extended the additive evidence-role overlay from admitted paths to both admitted paths and current HOLD investigations.

The generalized analyzer now:

- requires exact one-to-one role coverage for every admitted-path and HOLD-investigation evidence reference;
- requires investigation records to remain explicitly `HOLD`;
- rejects omitted references, unrelated extras, duplicate assignments, unknown ids, unknown roles, non-HOLD statuses, and invalid lower donor binding;
- keeps admitted and HOLD reference counts separate;
- emits an explicit `hold_status_promoted_to_admission: false` boundary;
- leaves `migration_paths.json`, `migration_path_investigations.json`, historical generation fixtures, and donor repositories unchanged.

Current bounded result:

- admitted path records: 1;
- HOLD investigation records: 3;
- admitted evidence references: 4;
- HOLD evidence references: 11;
- total role-bound references: 15 / 15.

## Verification contract

Focused regressions cover:

- missing HOLD role -> fail closed;
- extra HOLD reference -> fail closed;
- duplicate HOLD assignment -> fail closed;
- unknown role -> fail closed;
- non-HOLD investigation status -> fail closed;
- unknown investigation id -> fail closed;
- invalid donor-binding lower layer -> fail closed;
- admitted-path role coverage still required;
- current real corpus -> exact 15 / 15 role coverage;
- generated result -> equality with checked-in JSON.

Repository-wide CI remains the merge prerequisite.

## Truth boundary

Passing role binding proves only that every current admitted or HOLD edge-evidence reference has one explicit declared audit role and that those role overlays exactly cover the already-declared evidence sets.

It does **not** prove:

- that any declared role is the uniquely correct semantic interpretation of the donor content;
- that the evidence bundle is sufficient to prove or disprove a migration;
- authorship, trustworthiness, or cryptographic attestation;
- migration execution by Protocol Evolution;
- whole-project semantic equivalence;
- chain-vs-direct equivalence;
- universal absence of an adapter outside the bounded historical scans.

HOLD remains HOLD. This cycle adds auditability, not compatibility.

## Donor boundary

Adapter & Translation Garden remains the adapter/translation implementation donor. No adapter generator, translation router, migration runtime, or donor implementation is copied or executed.

FrameState and City Multiplayer are read only as already-declared semantic/protocol donors. No donor repository is mutated.

## Root gate

**Truth** — negative and incomplete evidence now states what each pinned reference contributes without relabeling it as stronger proof.

**Agency / non-domination** — no migration, install, publish, network, device, user-data, canon, or merge authority is added.

**Continuity** — historical fixtures, source lineage, path admissions, HOLD findings, blockers, and donor references remain unchanged; the role layer is additive.

**Wisdom before speed** — close the auditability asymmetry around HOLD evidence before attempting semantic-content validation, monolith-scale compatibility census work, or the larger five-generation experiment.

Merge only if repository-wide CI passes and these boundaries remain intact.
