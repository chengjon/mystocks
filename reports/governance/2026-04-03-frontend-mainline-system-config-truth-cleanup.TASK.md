# TASK

> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-truth-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Truth Cleanup`
- Objective: `Remove stale active-tree System-Config contract hints so scripts and active reference docs match the confirmed truth: no unified backend system-settings contract exists, the page save path is local-only, and datasource writeback belongs to System-Data.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `scripts/dev/tools/generate-page-config.js`
- `docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md`
- `docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-truth-cleanup.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-truth-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check -- scripts/dev/tools/generate-page-config.js docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md`
- `node --check scripts/dev/tools/generate-page-config.js`

## OpenSpec
- (none)

## Related Plans
- docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - System-Config truth is already confirmed in Mongo: no unified backend system-settings contract exists.
  - Active generators and active reference docs should not continue to advertise /api/system/settings or pending-contract wording.

## Scope Paths
- scripts/dev/tools/generate-page-config.js
- docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md
- docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md

## Next Steps
- Only revisit this area if backend introduces a real unified system-settings contract and OpenAPI changes land.

## Compatibility Notes
- Mongo is the source of truth; exported markdown is a projection for review and comparison.
- This cleanup removes stale active-tree contract hints without introducing a new backend system-settings contract.
