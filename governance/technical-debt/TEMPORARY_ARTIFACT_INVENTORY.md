# Temporary Artifact Inventory

## Purpose

This document is the canonical class-level review inventory for temporary entrypoints,
mechanical splits, and backup files in the governance baseline.

It does not replace deletion evidence, migration-closeout records, or focused governance audits.
Its role is narrower:

- keep one canonical review path for these artifact classes
- state the accepted lifecycle target for each class
- prevent new sidecar governance layers from being created just to describe temporary files

## Inventory Classes

| Class | Typical Markers | Governed State | Canonical Active Target | Historical / Frozen Target | Review References |
| --- | --- | --- | --- | --- | --- |
| Temporary entrypoints | temp wrappers, stopgap CLI entry files, one-off migration launchers | governance debt until retired or formally accepted | converge into the real canonical module, route, script, or entrypoint instead of keeping a stopgap file | none by default; keep only focused closeout evidence if needed | `governance/technical-debt/WEEKLY_GOVERNANCE_CADENCE.md`, `reports/governance/README.md`, `reports/governance/2026-04-06-directory-entrypoint-completeness-audit.md` |
| Mechanical splits | `part1` / `part2` / `part3`, duplicated summary copies, parallel slices created only to make a temporary view | governance debt unless one canonical file cannot yet be formed and the split is explicitly accepted | one directory-level README, one canonical board, or one focused closeout file | archive only after the split becomes frozen history with a clear redirect | `reports/governance/README.md`, `reports/governance/2026-04-06-directory-entrypoint-completeness-audit.md` |
| Backup files | `.bak`, `.backup`, timestamped duplicate files, ad-hoc `backups/` payloads in active trees | accepted only when stored in governed lifecycle directories; otherwise governance debt | `var/backups/` for active or runtime-generated backups | `archive/backups/` for frozen historical backup payloads retained for traceability | `openspec/specs/file-organization/spec.md`, `reports/governance/2026-03-09-root-coverage-backups-convergence.md` |

## Current Canonical Interpretation

1. These classes are governed as artifact classes, not as a second task board.
2. A path that matches one of these classes is not automatically deletion-ready.
3. A path in one of these classes may stay temporarily only when its canonical source, verification path, and exit condition are explicit in the current governance record.
4. If no such record exists, the artifact remains open governance debt.

## Review Triggers

Review this inventory when any of the following occurs:

1. A new `*_new.py`, shim-like stopgap entrypoint, or temporary wrapper is proposed.
2. A directory or document review surfaces `.bak`, `.backup`, timestamped duplicates, or `backups/` drift outside governed lifecycle locations.
3. A report, board, or closeout record proposes `part1` / `part2` / `part3` style splitting instead of converging to one canonical source.
4. A cleanup or archival batch wants to delete one of these artifacts.

## Decision Rules

1. Single source of truth still applies:
   use one canonical governance record plus the real code or lifecycle target, not repeated sidecar explanations.
2. Compatibility retirement is separate:
   if an artifact is also a shim, compatibility layer, or `*_new.py`, cite migration completion and exit criteria from `architecture/STANDARDS.md` before retirement.
3. Deletion is separate:
   if the review escalates from classification to deletion, deletion approval still requires both code-path and function-tree verdicts from the canonical deletion-governance sources.
4. Metrics are separate:
   any count of these artifacts in governance reporting must still distinguish `measured`, `inferred`, and `historical_baseline`.

## Working Examples

- `reports/governance/2026-03-09-root-coverage-backups-convergence.md`
  - documents the governed move from root `backups/` drift to `var/backups/` and `archive/backups/`
- `reports/governance/2026-04-06-directory-entrypoint-completeness-audit.md`
  - states that no temporary entrypoint should be added as a stopgap and rejects mechanical proliferation
- `reports/governance/README.md`
  - forbids this directory from becoming a dumping ground for temporary migration notes, backups, or mechanical splits
