# B4.011-M2a Residual-M5 Modified Tracked Reports Review

Date: 2026-06-12
Branch: `wip/root-dirty-20260403`
Baseline HEAD: `0fbc6a592`
Mode: no-source modified tracked report decision review
Source edits authorized: false

## Scope

This review covers only the five modified tracked active reports left under
`docs/reports` after all tracked deletion-retirement packages were closed.

No file content is changed by this review. It does not stage, restore, archive,
delete, move, preserve, or normalize the five modified reports.

Explicitly out of scope:

- untracked `docs/reports` files
- `docs/guides/**`
- `docs/superpowers/**`
- `web/**`
- `src/**`
- `tests/**`
- `scripts/**`
- OpenSpec
- ST-HOLD
- `marketKlineData`
- external dirty paths

## Current Boundary

- HEAD: `0fbc6a592`
- Staged changes before review: empty
- Current parent residual node: `b4-docs-reports-residual-dirty-review`
- Remaining `docs/reports` dirty distribution before this review: `M 5 / ?? 12`
- All five M5 files are tracked active reports.
- None of the five files has a tracked `archive/docs/reports/**` counterpart.

## M5 Decision Matrix

| File | Diff | Archive counterpart | Source/test anchor | Observed change shape | Decision class |
| --- | ---: | --- | --- | --- | --- |
| `docs/reports/BACKTEST_API_DOCUMENTATION.md` | +2 / -0 | none | none | Adds historical prototype disposition for legacy backtest API server | Preserve active change candidate |
| `docs/reports/IMPLEMENT_WEB_FRONTEND_V2_NAVIGATION_STATUS_REPORT.md` | +9 / -0 | none | `tests/unit/scripts/test_repository_hygiene_paths.py` | Adds current repo-truth disposition for legacy navigation report | Preserve active change candidate; test-aware |
| `docs/reports/PHASE2_MENU_REFACTORING_COMPLETION_REPORT.md` | +9 / -0 | none | none | Adds current repo-truth disposition for legacy menu report | Preserve active change candidate |
| `docs/reports/codebase-cleanup-2026-03-29.md` | +1 / -1 | none | none | Updates cleanup result row for retired session-state directory | Preserve active change candidate |
| `docs/reports/frontend-optimization-implementation-status-2026-01-27.md` | +9 / -0 | none | `tests/unit/scripts/test_repository_hygiene_paths.py` | Adds current repo-truth disposition for legacy frontend optimization report | Preserve active change candidate; test-aware |

## Interpretation

These five changes are not archive drift and are not deletion-retirement
candidates under the previous HOLD-B flow. They are tracked active report edits
that annotate historical reports with current repo-truth boundaries or update a
cleanup result row.

Two files are anchored by `tests/unit/scripts/test_repository_hygiene_paths.py`:

- `docs/reports/IMPLEMENT_WEB_FRONTEND_V2_NAVIGATION_STATUS_REPORT.md`
- `docs/reports/frontend-optimization-implementation-status-2026-01-27.md`

Those anchors make deletion or path moves test-aware work. However, the current
dirty change itself is content-only and does not require path changes.

## Decision

Recommended implementation, if separately approved:

1. Preserve the five active report modifications in place.
2. Do not create archive counterparts in this package.
3. Do not move or delete the five active paths.
4. Do not edit tests or source files.
5. Stage only the five tracked report modifications plus FUNCTION_TREE
   governance metadata.

Rationale:

- The changes are small and targeted (`+30 / -1` total across five tracked
  reports).
- They clarify that historical reports are not current route/menu/task truth.
- There is no existing archive counterpart to overwrite.
- Path retirement would broaden scope and trigger test-anchor considerations.

## Required Gates For Preserve-Active Implementation

- Exact staging only.
- `git diff --cached --check`.
- GitNexus `verify-staged`.
- GitNexus `detect_changes --scope staged`.
- OPENDOG verification with no cleanup blockers.
- Post-commit GitNexus `analyze --index-only`.
- Final verification that no untracked reports, docs/guides, docs/superpowers,
  source, tests, scripts, OpenSpec, ST-HOLD, marketKlineData, or external dirty
  paths were staged.

## Authorization Request

Request `B4.011-M2a-Residual-M5 preserve tracked report annotations`
implementation authorization for only these five paths:

- `docs/reports/BACKTEST_API_DOCUMENTATION.md`
- `docs/reports/IMPLEMENT_WEB_FRONTEND_V2_NAVIGATION_STATUS_REPORT.md`
- `docs/reports/PHASE2_MENU_REFACTORING_COMPLETION_REPORT.md`
- `docs/reports/codebase-cleanup-2026-03-29.md`
- `docs/reports/frontend-optimization-implementation-status-2026-01-27.md`

Allowed action would be limited to preserving the current worktree content of
those five tracked active reports as-is. Archive creation, path retirement, test
edits, source edits, untracked report handling, and any unrelated dirty path
remain forbidden.
