# Action Report — Living City v0.1.0 -> v0.2.0 promotion audit

Date: 2026-09-13
Status: **HOLD**

## Bounded question

Can the first Living City candidate edge, world v0.1.0 -> v0.2.0, be promoted from monolith discovery evidence into a historical generation fixture and admitted migration path without weakening Protocol Evolution's evidence ladder?

## Falsifier defined before implementation

The promotion must stay blocked if any of these are true:

1. the only v0.1-shaped executable fixture is synthesized from a current world rather than observed as a historical v0.1 value;
2. the observed migrator emits a later/current schema rather than the exact adjacent v0.2.0 target;
3. the declared full-history archive is not available for inspection;
4. any donor file used by the audit fails archive-byte -> pinned-Git-blob identity;
5. any generated readiness result grants admission despite one of those blockers.

## Repository and donor boundary read first

Protocol Evolution remains a cross-repository semantic compatibility research layer. It owns immutable historical fixtures, migration evidence and compatibility semantics, but not donor runtime authority or Adapter & Translation Garden's adapter implementations. Existing generation fixtures, lineages, admitted paths and HOLD investigations are unchanged.

The connected-monolith candidate remains pinned to `mike-axiom-mir/axm-living-city-simulator` commit `a299db639e87b2fa0dea1ded1bf651ab86e9cd3c`.

## Grounded observations

### 1. The donor regression is executable, but its source is synthetic

`tests/household_agreement_test.js` creates a **current** world, deep-clones it, rewrites `schema`/`version` to v0.1.0, deletes later fields, and then calls `Systems.migrateWorld(...)`.

I executed the exact connected-monolith donor snapshot used by the candidate census:

```text
node tests/household_agreement_test.js
```

Observed result: **13/13 tests passed**, including `testLegacyMigrationIsExplicitAndNoConsentIsInvented`.

The relevant archive bytes match the pinned GitHub blobs for the regression test, migration implementation, current schema declaration, donor-recorded test output, migration contract, and source-archive declaration.

This is useful executable evidence, but it is not a historical v0.1 world value.

### 2. The observed migrator is old -> current, not exact v0.1 -> v0.2

At the pinned donor commit, `Core.SCHEMA` is `axm.living-city-sim.world/v0.11.0`; v0.1.0 is one accepted legacy schema. `migrateWorld` rewrites accepted legacy input to `Core.SCHEMA` / `Core.VERSION` before later initializers run.

Therefore the passing regression demonstrates a bounded semantic property of the **current** migration route (not inventing a household consent agreement and retaining the legacy relationship label), but it does not produce or observe an exact v0.2.0 output fixture.

### 3. A stronger historical source is declared, but unavailable here

`.axm-intake/SOURCE_ARCHIVES.json` declares `AXM_LIVING_CITY_SIM_FULL_HISTORY_ARCHIVE_v0_11_0(1).zip`, SHA-256 `a62dce40aa8c456e9f8b22bfb832df965b829a91d44e36ab554da4b9ee3de7f7`, with role `SEALED_V0_1_0_THROUGH_V0_11_0_HISTORY`.

The same declaration explicitly says the history archive was **not copied into the repository**. It is also not present in the connected-monolith ZIP supplied for this research cycle. Its contents were therefore not inspected and cannot be used as historical fixture evidence yet.

GitHub history also shows the v0.1 schema entered this repository in the root intake commit for the cumulative v0.11.3 package, not through a visible chain of historical v0.1 -> ... commits.

## Improvement built

Added a deterministic `candidate_promotion_readiness` evidence layer that distinguishes:

- a retro-synthesized legacy-shaped regression input from a historical fixture;
- a passing current migration regression from an exact adjacent migration;
- a declared-but-unavailable history archive from inspected historical evidence;
- execution evidence from promotion authority.

The layer fails closed on contradictory promotion claims, donor/blob identity mismatches, false exact-target claims, and readiness claims unsupported by historical + exact-adjacent evidence.

## Verification

Focused regressions: **7/7 passed locally**.

Donor execution observation: **13/13 household-agreement tests passed** from the exact connected-monolith module snapshot.

Repository-wide GitHub Actions must pass before merge.

## Result / limitations

- Living City v0.1.0 source generation admission: **HOLD**.
- Living City v0.1.0 -> v0.2.0 migration-path admission: **HOLD**.
- Five-generation chain experiment input readiness: **unchanged / false**.
- No historical fixture was fabricated.
- No candidate was silently promoted.
- No Adapter & Translation Garden implementation was copied.

The smallest remaining blocker is concrete: inspect the declared sealed full-history archive (or another independently grounded historical v0.1 value) and look for an exact v0.1 -> v0.2 transformation/output. A declaration that the archive exists is not enough.

## AXM merge gate

- **Truth:** executable evidence was strengthened while the historical/adjoining gaps remain explicit.
- **Agency / non-domination:** no canon, runtime, install, network, device or user-data authority was added.
- **Continuity:** existing fixtures, lineage order, admissions, HOLD findings and donor lineage remain untouched.
- **Wisdom before speed:** the tempting passing migration test is not promoted beyond what it actually proves.
