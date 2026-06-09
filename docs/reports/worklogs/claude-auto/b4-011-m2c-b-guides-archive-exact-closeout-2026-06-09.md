# B4.011-M2c-B Guides Archive Exact Closeout

Date: 2026-06-09

Commit: `c484ab398 B4.011-M2c-B: archive exact docs guides`

Mode: docs archive/deletion-retirement closeout

Source edits authorized: `false`

## Scope Closed

This closeout covers only the `docs/guides/**` archive exact package identified in `B4.011-M2c-pre`.

Implemented scope:

- 30 exact archive renames from active `docs/guides/**` paths to ignored archive paths under `archive/docs/guides-merged/**`.
- All 30 staged archive moves were detected by Git as `R100`.
- Archive targets were force-added by exact path only.
- FUNCTION_TREE metadata and task card were included for this package.

Closed source groups:

- `docs/guides/features/**`
- `docs/guides/openspec-cmd/**`
- `docs/guides/quant-trading/**`
- `docs/guides/superpowers/**`
- `docs/guides/templates/**`

Archive targets:

- `archive/docs/guides-merged/features/**`
- `archive/docs/guides-merged/openspec-cmd/**`
- `archive/docs/guides-merged/quant-trading/**`
- `archive/docs/guides-merged/superpowers/**`
- `archive/docs/guides-merged/templates/**`

## Out Of Scope

Not touched by this package:

- Active reparent paths already closed by `B4.011-M2c-A`
- `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`
- modified active `docs/guides/**` index/sidecar docs
- `docs/reports/**`
- `docs/superpowers/**` root package
- `src/**`
- `tests/**`
- `scripts/**`
- `web/**`

## Verification

Pre-commit:

- Staged set contained 30 `R100` archive renames and 4 governance metadata files.
- No `OMC_WORKFLOW_GUIDE` path staged.
- No active reparent path staged.
- No source, test, frontend, backend, script, report, or root superpowers paths staged.
- `git diff --cached --check` passed.
- GitNexus `verify-staged` risk: `low`.
- GitNexus affected processes: `0`.
- OPENDOG verification: `fresh`; failing runs `0`; cleanup blockers `0`; refactor blockers `0`.

Post-commit:

- GitNexus `analyze --index-only` completed successfully.
- GitNexus indexed/current HEAD: `c484ab398`.

## Residuals

The following B4.011 items remain separate:

- `B4.011-M2c-HOLD`: `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`.
- Modified/untracked active `docs/guides/**` sidecars and root guide index docs.
- `B4.011-M2b`: `docs/superpowers` exact archive-retirement outside `docs/guides`.
- `B4.011-M2a`: `docs/reports` large archive proof package.

## Decision

The guides archive exact package is complete and should be closed. It must not be interpreted as approval for the unresolved HOLD item, active guide sidecars, docs/reports, docs/superpowers, or source/test cleanup.
