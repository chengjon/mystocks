# TASK

> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-historical-reference-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Historical Reference Cleanup`
- Objective: `Align historical-but-still-readable reference docs to the confirmed System-Config truth: read-only health endpoints, local-only page save semantics, and datasource backend writeback under System-Data.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `docs/plans/2026-03-12-api-availability-matrix-draft.md`
- `docs/references/artdeco-system-guide.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-historical-reference-cleanup.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-historical-reference-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check -- docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md`
- `rg -n 'localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch' docs/plans/2026-03-12-api-availability-matrix-draft.md docs/references/artdeco-system-guide.md`

## OpenSpec
- (none)

## Related Plans
- docs/plans/2026-03-12-api-availability-matrix-draft.md
- docs/references/artdeco-system-guide.md

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - The current System-Config truth is confirmed: health endpoints are read-only, the page save path is local-only, and datasource backend writeback belongs to System-Data.
  - The remaining drift sits in a historical availability draft and a reference guide section that are still easy for future contributors to quote.

## Scope Paths
- docs/plans/2026-03-12-api-availability-matrix-draft.md
- docs/references/artdeco-system-guide.md

## Next Steps
- Leave deeper design/archive cleanup for separate work if broader document modernization is needed.

## Compatibility Notes
- Mongo is the source of truth; this cleanup only aligns historical-but-still-readable reference docs to the already-confirmed System-Config truth.
- This work does not reopen frontend mainline verification or imply any new backend system-settings contract.
