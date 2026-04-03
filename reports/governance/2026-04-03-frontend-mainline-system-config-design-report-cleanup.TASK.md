# TASK

> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-design-report-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Design Report Cleanup`
- Objective: `Align the remaining stale System-Config backend contract wording in the historical phase-2 design report to the confirmed current truth without implying a unified backend system-settings API exists.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-design-report-cleanup.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-design-report-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check -- docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`
- `rg -n 'localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch' docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`

## OpenSpec
- (none)

## Related Plans
- docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - The current System-Config truth is already confirmed in active codepaths and governance snapshots.
  - The remaining stale backend config contract wording sits in a historical design completion report that is still easy to quote out of context.

## Scope Paths
- docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md

## Next Steps
- Leave broader design-report modernization for separate work if needed.

## Compatibility Notes
- Mongo is the source of truth; this is a narrow design-report wording cleanup only.
- This cleanup does not claim the old phase-2 design was implemented verbatim; it only prevents the report from advertising a backend contract that the active codepath does not provide.
