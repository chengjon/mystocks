# Legacy Strategy Workbench Static Shell Truth Audit

## Scope
- `web/frontend/src/views/strategy/BatchScan.vue`
- `web/frontend/src/views/strategy/ResultsQuery.vue`
- `web/frontend/src/views/strategy/SingleRun.vue`
- `web/frontend/src/views/strategy/StatsAnalysis.vue`

## Finding
These four pages were high-priority secondary inventory candidates because they exposed selector-driven execution, query/export controls, auto-refresh state, and aggregate strategy metrics while not being registered as canonical routes.

The API calls they depended on were not present in the active typed frontend API surface and only appeared in the deprecated API module. Keeping those controls visible would make an unrouted secondary asset look executable without a verified route owner or current contract.

## Repair
- Replaced all four pages with honest `legacy-static-shell` handoff surfaces.
- Removed the four page-local SCSS files that only styled the retired execution/query workbench UI.
- Added owner regression coverage and a decommission guard to prevent `strategyApi.*`, `ElMessage`, and `@use "./styles/"` from returning to these pages.

## Verification
- RED: `npx vitest run src/views/strategy/__tests__/LegacyStrategyWorkbench.spec.ts` failed before repair; the old `BatchScan.vue` also exposed a structural template error.
- GREEN: owner and config regressions passed after repair.
- Inventory: high-priority secondary shortlist dropped from `5` to `1`.
