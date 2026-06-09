# B4.007 Root Legacy View Disposition

Date: 2026-06-07
Branch: `wip/root-dirty-20260403`
HEAD at scan: `81396cbc4`
Mode: `no-source`

## Boundary

This report handles the B4.007 `RL-1 root legacy view truth` queue. It does not modify, restore, stage, commit, delete, or retire any root-level Vue page.

The root legacy queue is intentionally separated from the already committed B4.007 route/source packages because its diff is large and governance-sensitive:

- Files: `23`
- Tracked diff files: `23`
- Total diff from the B4.007 preflight: `+1457 / -7345`
- Current direct router imports among these files: `0`

Deletion or full retirement is not authorized by this report. Any file proposed for deletion must move to a separate deletion-retirement package with explicit approval.

## Canonical Route Truth Notes

- `/dashboard` is backed by `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`, not `web/frontend/src/views/Dashboard.vue`.
- `/system/config` is backed by `web/frontend/src/views/system/Settings.vue`, not `web/frontend/src/views/Settings.vue`.
- B4.004 data/market route packages and B4.005 system/risk route packages remain closed and must not be reopened through this queue.
- These root-level files are therefore route-truth evidence rows, not direct active route packages.

## Disposition Table

### Legacy Dashboard

Disposition: source-hold. Review as compatibility-wrapper or retirement candidates only after route-truth decision.

- `web/frontend/src/views/Dashboard.vue`
- `web/frontend/src/views/EnhancedDashboard.vue`
- `web/frontend/src/views/Phase4Dashboard.vue`

### Legacy Market And Analysis

Disposition: source-hold. These overlap with closed data/market route truth and must not be committed as a bulk source package.

- `web/frontend/src/views/AdvancedAnalysis.vue`
- `web/frontend/src/views/Analysis.vue`
- `web/frontend/src/views/IndicatorLibrary.vue`
- `web/frontend/src/views/IndustryConceptAnalysis.vue`
- `web/frontend/src/views/Market.vue`
- `web/frontend/src/views/MarketData.vue`
- `web/frontend/src/views/StockAnalysisDemo.vue`
- `web/frontend/src/views/StockDetail.vue`
- `web/frontend/src/views/Stocks.vue`
- `web/frontend/src/views/TdxMarket.vue`
- `web/frontend/src/views/TechnicalAnalysis.vue`
- `web/frontend/src/views/Wencai.vue`

### Legacy Risk And Monitor

Disposition: source-hold. These overlap with closed system/risk route truth and require per-file route-truth review before any source acceptance.

Note: `monitor.vue` remains lowercase and should be handled carefully in any future compatibility-wrapper decision because case-sensitive import paths can behave differently across platforms.

- `web/frontend/src/views/EnhancedRiskMonitor.vue`
- `web/frontend/src/views/monitor.vue`
- `web/frontend/src/views/RealTimeMonitor.vue`
- `web/frontend/src/views/RiskMonitor.vue`

### Legacy Portfolio

Disposition: source-hold. This should be reviewed against ArtDeco portfolio/trading route truth before any source acceptance.

- `web/frontend/src/views/PortfolioManagement.vue`

### Legacy System And Misc

Disposition: source-hold. These are root-level legacy views with no current direct router import.

- `web/frontend/src/views/Settings.vue`
- `web/frontend/src/views/TaskManagement.vue`
- `web/frontend/src/views/TestPage.vue`

## Recommended Next Packages

1. `B4.007-F1 root legacy route-truth decision table`
   - No-source only.
   - For each of the 23 files, record one of: preserve as compatibility wrapper, move to canonical route, archive-only, or deletion-retirement candidate.
   - No source/test staging.

2. `B4.007-F2 root legacy compatibility wrappers`
   - Source-authorized only after F1.
   - Split by domain group, not as a 23-file bulk package.
   - Gate: GitNexus fresh, GitNexus staged detect, OPENDOG recorded, type-check, focused root-view tests if present.

3. `B4.007-F3 root legacy deletion-retirement`
   - Separate explicit deletion-retirement approval required.
   - Must include route/import/runtime checks and recovery evidence.

## Hold Items

The following B4.007-adjacent item remains on hold because the focused node test currently requires touching a non-B4.007 source boundary:

- `web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts`

Observed failure:

- Command: `cd web/frontend && node --test src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts src/views/artdeco-pages/stock-management-tabs/__node_tests__/stockManagementRouteData.test.ts`
- Failure: Node cannot resolve `@/views` imported from `web/frontend/src/views/artdeco-pages/market-tabs/marketKlineData.ts`.
- Boundary decision: do not modify `web/frontend/src/views/artdeco-pages/market-tabs/marketKlineData.ts` inside B4.007 because it is outside the active B4.007 file list and overlaps earlier data/market support.

## Gates For Any Future RL-1 Source Package

- Do not stage all 23 root legacy views together.
- Do not stage ST-HOLD files.
- Do not touch closed B4.003-B4.006 files.
- Do not touch unrelated dirty files.
- Run GitNexus impact/staged detect for the exact package.
- Record OPENDOG test/build evidence.
- Run `cd web/frontend && npm run type-check`.
- Run focused unit/node/E2E tests based on the exact route truth being preserved.
- Ensure staged files exactly match the package list.
