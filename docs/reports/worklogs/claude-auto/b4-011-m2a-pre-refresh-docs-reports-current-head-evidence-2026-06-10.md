# B4.011-M2a-pre refresh docs/reports current-head evidence

Date: 2026-06-10

## Scope

This is a no-source refresh for `B4.011-M2a` after an external commit advanced
the current branch.

It does not authorize or stage deletion-retirement, archive evidence, source,
test, runtime, route, UI, `docs/guides`, or `docs/superpowers` changes.

## Reason for Refresh

`B4.011-M2a-pre` was committed at `b8a40b680`, but the branch later advanced to
`6f77ad17d` through an external commit:

`6f77ad17d feat: add openstock runtime migration boundary`

That commit added tracked files under `docs/reports/architecture/**`,
`openspec/changes/extract-data-source-runtime-service/**`, `scripts/**`,
`src/**`, and `tests/**`. Those additions are outside this B4.011 docs archive
retirement package and must not be touched here.

## Current HEAD Evidence

Current HEAD: `6f77ad17d`

Path-scoped `docs/reports/**` status:

- Modified tracked files: 5
- Deleted tracked files: 699
- Untracked entries: 11
- Archive files under `archive/docs/reports/**`: 3795

Deleted-file archive proof:

- 681 deleted files have exact relative archive matches.
- 18 deleted files have same relative archive paths but content hash mismatch.
- 0 deleted files are missing a relative archive path.
- 0 deleted files require hash-only archive matching.

The M2a split remains unchanged:

- `B4.011-M2a-A`: 681 exact archive-retirement entries only.
- `B4.011-M2a-HOLD`: 18 archive drift entries.
- `B4.011-M2a-MOD`: 5 modified tracked report files.
- `B4.011-M2a-UNTRACKED`: 11 untracked report entries.

## Current Drift HOLD List

- `docs/reports/cleanup/FILE_CLEANUP_TASK.md`
- `docs/reports/cleanup/INDEX.md`
- `docs/reports/cleanup/directory-organization/legacy/PROJECT_DIRECTORY_MANAGEMENT_PLAN.md`
- `docs/reports/cleanup/index-artifacts/INDEX_root.md`
- `docs/reports/documentation-governance/2026-04-08-decision-register.md`
- `docs/reports/documentation-governance/2026-04-09-ai-tools-family-wave1.md`
- `docs/reports/documentation-governance/2026-04-09-worklogs-source-investigation.md`
- `docs/reports/misc/PROJECT_STRUCTURE.md`
- `docs/reports/plans/code-simplification-notes.md`
- `docs/reports/plans/compatibility-inventory.md`
- `docs/reports/quality/README.md`
- `docs/reports/quality/backend-audit-2026-05-14.md`
- `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md`
- `docs/reports/quality/generated/backend-fullpath-route-table.json`
- `docs/reports/quality/generated/backend-fullpath-route-table.md`
- `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md`
- `docs/reports/reviews/PHASE1_GOVERNANCE_APPROVAL.md`
- `docs/reports/tasks/2026-03-27-local-dirty-worktree-batch-plan.md`

## Current Modified Tracked Files

These remain outside M2a-A:

- `docs/reports/BACKTEST_API_DOCUMENTATION.md`
- `docs/reports/IMPLEMENT_WEB_FRONTEND_V2_NAVIGATION_STATUS_REPORT.md`
- `docs/reports/PHASE2_MENU_REFACTORING_COMPLETION_REPORT.md`
- `docs/reports/codebase-cleanup-2026-03-29.md`
- `docs/reports/frontend-optimization-implementation-status-2026-01-27.md`

## Current Untracked Entries

These remain outside M2a-A:

- `docs/reports/ARTDECO_DOCS_CODE_ALIGNMENT_AUDIT_2026-05-28-review.md`
- `docs/reports/ARTDECO_DOCS_CODE_ALIGNMENT_AUDIT_2026-05-28.md`
- `docs/reports/DASHBOARD_CRITIQUE_AUDIT.md`
- `docs/reports/FRONTEND_DATA_SOURCE_DIAGNOSIS.md`
- `docs/reports/GPU_DOCUMENTATION_INVENTORY.md`
- `docs/reports/P3-C5-HANDOFF.md`
- `docs/reports/P3-C5-exception-consolidation-progress.md`
- `docs/reports/PRODUCT_DESIGN_AUDIT.md`
- `docs/reports/architecture/data-source-service-extraction-analysis-review-2026-06-09.md`
- `docs/reports/workspace-cleanup-plan-2026-05-14-review.md`
- `docs/reports/workspace-cleanup-plan-2026-05-14.md`

## Recommendation

Proceed with `B4.011-M2a-A` only after this refresh is committed and attached to
the FUNCTION_TREE node at current HEAD.

`B4.011-M2a-A` must stage only the 681 exact active deletions and their matching
archive copies. It must exclude all 18 drift files, all 5 modified tracked
files, all 11 untracked report entries, and all files introduced by
`6f77ad17d`.
