# Action Report — admit FrameState v0.2 generation

Date: 2026-09-12

## Question tested

Can two different schema versions preserve the same tested meaning, or does a version-number change alone force an incompatibility claim?

## Falsifier defined before implementation

If the semantic survivability matrix classifies FrameState v0.2 and v0.4 as incompatible solely because their schema versions differ, this experiment fails. Both historical generations use eSpeak semantics for speech without an explicit engine. FrameState v0.5 must remain semantically distinct because its undeclared speech default is native.

## Donor evidence inspected

- `mike-axiom-mir/axm-framestate` commit `5d46363fb30bf5d30198b8cdec473d3bb9ba6287` — v0.2 project reader and historical `examples/narrated_motion.json`.
- At the same commit, `src/axm_framestate/audio.py` resolves speech through `espeak` / `espeak-ng`.
- Current FrameState explicitly preserves v0.4-and-earlier undeclared speech as `espeak` and v0.5 undeclared speech as `native`.
- Existing Protocol Evolution donor boundary remains Adapter & Translation Garden; no adapter implementation is copied.

## Exact delta

- Admitted the exact historical FrameState v0.2 narrated project as the fifth real generation fixture.
- Preserved donor commit, source path and source blob SHA in the manifest.
- Closed the fixture corpus gap from 1 to 0 without inventing a generation.
- Added a regression proving v0.2 <-> v0.4 is `SAME` for the tested semantic claim while v0.2 -> v0.5 remains `UNSUPPORTED`.
- Added a regression binding checked-in `evidence/generation_matrix.json` to the generated matrix so evidence cannot silently drift stale.

## Evidence limit

`SAME` means only that the declared semantic claim `undeclared_speech_engine=espeak` is equal. It does not claim whole-project compatibility between FrameState v0.2 and v0.4. The current matrix remains claim-level evidence, not donor-runtime execution.

The five-generation fixture target is now met, but the seed's five-generation migration-chain versus direct-migration experiment is still open.

## Root check

**Truth:** the fifth fixture is an exact historical donor artifact with commit/path/blob provenance; the compatibility claim is deliberately narrow.

**Agency / non-domination:** no donor repo is modified, no user data is migrated, and no canon/install/publish authority is created.

**Continuity:** prior fixtures and the original action report remain intact; this run appends evidence instead of rewriting history.

**Wisdom before speed:** this cycle closes one explicit corpus gap and adds one falsifiable semantic claim rather than starting generalized migration machinery early.
