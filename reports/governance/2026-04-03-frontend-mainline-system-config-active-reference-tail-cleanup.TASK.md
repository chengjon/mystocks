# TASK

> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-active-reference-tail-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Active Reference Tail Cleanup`
- Objective: `Align the remaining active reference docs to the confirmed System-Config truth: the page save path is local-only, the visible CTA is 保存本地设置, and datasource backend writeback belongs to System-Data.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `reports/analysis/frontend-mainline-overall-closeout.md`
- `docs/plans/frontend-page-optimization-list.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-active-reference-tail-cleanup.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-active-reference-tail-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check -- reports/analysis/frontend-mainline-overall-closeout.md docs/plans/frontend-page-optimization-list.md`
- `rg -n '保存本地设置|local-only|System-Data|/api/health/detailed|/api/health' reports/analysis/frontend-mainline-overall-closeout.md docs/plans/frontend-page-optimization-list.md`

## OpenSpec
- (none)

## Related Plans
- docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md
- docs/plans/frontend-page-optimization-list.md

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - System-Config truth is already confirmed: the page save path is local-only and the datasource backend write path belongs to System-Data.
  - A few active reference docs still use stale wording that can mislead future follow-up work even though runtime and governance snapshots are already aligned.

## Scope Paths
- reports/analysis/frontend-mainline-overall-closeout.md
- docs/plans/frontend-page-optimization-list.md

## Next Steps
- Treat remaining mentions in historical design/reference documents as archival debt unless they are promoted back into active guidance.

## Compatibility Notes
- Mongo is the source of truth; exported markdown remains a projection for review and comparison.
- This cleanup only aligns active reference wording to the already-confirmed System-Config truth and does not reopen frontend mainline phase verdicts.
