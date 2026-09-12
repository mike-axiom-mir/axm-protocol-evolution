# Action Report — Donor Evidence Reference Pinning

Date: 2026-09-13

## Bounded research question

Can a mutable or weakly identified donor URL masquerade as durable migration-path evidence merely because `evidence_refs` contains a non-empty string?

## Falsifier defined before implementation

The new integrity check fails if a checked donor reference uses a mutable branch such as `blob/main/...`, a short commit identifier, a compare range with a mutable endpoint, a duplicate reference used as evidence padding, or a non-GitHub free-form string.

If those references pass as structurally pinned, this cycle fails.

## Repository and donor boundary inspected first

Protocol Evolution remains the cross-repository semantic compatibility research layer. It owns evidence about compatibility, lineage, survivability, and migration-path claims; it does not own project runtime authority or adapter execution.

Adapter & Translation Garden remains the live adapter/translation implementation donor under:

`mike-axiom-mir/axm-collaboration-platform/tools/adapter-translation-garden/`

No adapter generator, router, migration implementation, donor runtime, or donor fixture was copied or executed in this cycle.

## Improvement

Added a narrow donor-reference integrity verifier for the checked-in migration-path admission and HOLD-investigation catalogs.

Accepted reference shapes are intentionally limited to:

- `https://github.com/<owner>/<repo>/commit/<40-hex-sha>`
- `https://github.com/<owner>/<repo>/blob/<40-hex-sha>/<path>`
- `https://github.com/<owner>/<repo>/compare/<40-hex-sha>...<40-hex-sha>`

The verifier also rejects duplicate evidence references inside one record so repeated URLs cannot inflate apparent evidence volume.

The CLI exits non-zero when the checked-in catalogs fail this gate. The discovered regression suite exercises the generated result on the repository’s existing Python 3.11/3.12/3.13 CI matrix.

## Grounded result

The current real catalogs contain 4 records and 15 donor evidence references.

Result: **15 / 15 are structurally pinned to full commit SHA identities.**

This changes no migration-path admission, HOLD result, fixture, lineage ordering, source reference, or historical artifact.

## Tests

Focused authored regressions cover:

1. current checked-in catalogs pass with 15/15 structurally pinned refs;
2. `blob/main/...` is rejected;
3. short commit SHA is rejected;
4. compare ranges require both endpoints to be full SHAs;
5. duplicate evidence-reference padding is rejected;
6. a non-GitHub free-form string cannot masquerade as pinned donor evidence;
7. checked-in generated integrity evidence must equal generated truth.

## Truth boundary / limitations

A full commit SHA in a URL proves only structural pinning of the reference identity used by this repository.

This verifier does **not**:

- contact GitHub or prove the referenced resource still resolves;
- prove the referenced file content supports the claim attributed to it;
- authenticate authorship or reviewer identity;
- prove migration execution;
- prove semantic equivalence;
- define every future evidence carrier.

A future non-GitHub or local evidence carrier should gain its own explicit validator rather than silently weakening this rule.

The existing chain-experiment readiness analyzer therefore remains honest when it says its evidence references are not independently verified. This cycle adds one narrower fact: the current donor URLs are not mutable branch references.

## Root merge gate

**Truth** — mutable branch URLs and short hashes cannot pass as durable donor evidence.

**Agency / non-domination** — no adapter, migration, install, publish, network, device, user-data, or canon authority is added.

**Continuity** — historical fixtures, lineage declarations, admissions, HOLD records, and donor source refs are unchanged; the new evidence is additive.

**Wisdom before speed** — evidence-reference hygiene is strengthened before any attempt to advance the larger five-generation chain experiment.

## Remaining open boundary

The five-generation chain-vs-direct experiment remains HOLD. FrameState still has four admitted generations and only one admitted adjacent migration path.

Reference pinning also does not close resource-resolution or semantic-support verification; those remain separate research questions.
