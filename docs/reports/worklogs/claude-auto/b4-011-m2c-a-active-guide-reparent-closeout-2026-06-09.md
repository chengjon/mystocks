# B4.011-M2c-A Active Guide Reparent Closeout

Date: 2026-06-09

Commit: `89fb2bf06 B4.011-M2c-A: reparent active docs guides`

Mode: docs-only implementation closeout

Source edits authorized: `false`

## Scope Closed

This closeout covers only the active guide reparent exact package from the B4.011 documentation archive/reorganization line.

Implemented scope:

- 27 exact guide reparent pairs committed as Git renames.
- Old active roots under:
  - `docs/guides/akshare/**`
  - `docs/guides/buger/INDEX.md`
  - `docs/guides/chrome-devtools/**`
  - `docs/guides/data-interface/**`
  - `docs/guides/tdx-integration/**`
  - `docs/guides/wencai/**`
- New active roots under:
  - `docs/guides/data-source/akshare/**`
  - `docs/guides/ai-tools/buger/INDEX.md`
  - `docs/guides/ai-tools/chrome-devtools/**`
  - `docs/guides/data-source/data-interface/**`
  - `docs/guides/data-source/tdx-integration/**`
  - `docs/guides/data-source/wencai/**`

Also committed:

- FUNCTION_TREE authorization metadata and task card for the package.

## Out Of Scope

Not touched by this package:

- `archive/docs/guides-merged/**`
- `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`
- `docs/guides/features/**`
- `docs/guides/openspec-cmd/**`
- `docs/guides/quant-trading/**`
- `docs/guides/superpowers/**`
- `docs/guides/templates/**`
- modified root/index/sidecar guide docs
- `docs/reports/**`
- `docs/superpowers/**`
- `src/**`
- `tests/**`
- `scripts/**`
- `web/**`

## Verification

Pre-commit:

- Staged set contained 27 `R` guide renames and 4 governance metadata files.
- No `archive/**` paths staged.
- No `OMC_WORKFLOW_GUIDE` path staged.
- No source, test, frontend, backend, script, report, or superpowers paths staged.
- `git diff --cached --check` passed.
- GitNexus `verify-staged` risk: `low`.
- GitNexus affected processes: `0`.
- OPENDOG verification: `fresh`; failing runs `0`; cleanup blockers `0`; refactor blockers `0`.

Post-commit:

- GitNexus `analyze --index-only` completed successfully.
- GitNexus indexed/current HEAD: `89fb2bf0648d5d31a402e7dc26969732984d3633`.
- Staged set is empty.

## Residuals

The following B4.011 work remains open and must be handled by separate authorization:

- `B4.011-M2c-B` guides archive exact package: 30 exact archive mappings under `archive/docs/guides-merged/**`.
- `B4.011-M2c-HOLD`: `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`.
- `B4.011-M2b`: `docs/superpowers` six-file exact archive-retirement package.
- `B4.011-M2a`: `docs/reports` large archive proof package.
- Modified/untracked active guide sidecars and root index docs.

## Decision

The active guide reparent package is complete and should be closed. The broader B4.011 documentation archive/reorganization line remains active through follow-up nodes or explicitly authorized packages.
