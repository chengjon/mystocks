# B4.007 ArtDeco/root legacy route truth preflight

Date: 2026-06-07
Branch: `wip/root-dirty-20260403`
HEAD: `9fddbd140e1f`
Mode: `no-source`

## Boundary

This node refreshes the B4.007 ArtDeco/root legacy route-truth boundary after B4.006 ST-5A through ST-5F were committed. It does not edit, restore, stage, or commit frontend source, tests, styles, resources, or assets.

Primary references:

- `architecture/STANDARDS.md`
- `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`
- `openspec/AGENTS.md`
- `docs/reports/worklogs/claude-auto/b4-007-artdeco-root-legacy-route-truth-preflight-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-006-strategy-trade-route-package-preflight-2026-06-06.md`
- `web/frontend/src/router/index.ts`

OpenSpec disposition:

- No new OpenSpec proposal is created for this preflight because B4.007 is route-truth cleanup of existing behavior, not a new capability.
- If a later package changes menu architecture, route patterns, or introduces a new canonical route model, stop and create/validate an OpenSpec change first.

Hard exclusions:

- Exclude all B4.002 deletion-retirement candidates from ordinary B4.007 source packages.
- Exclude closed B4.003-B4.006 packages.
- Exclude ST-HOLD deletion-coupled rows until deletion-retirement disposition is explicitly resolved.
- Exclude unrelated dirty files outside the B4.007 path list below.
- Treat `views/artdeco-pages/**` as active route truth only when `web/frontend/src/router/index.ts` imports that file directly.

Current ST-HOLD rows still dirty and excluded:

- `web/frontend/src/views/BacktestWizard.vue`
- `web/frontend/src/views/strategy/BatchScan.vue`
- `web/frontend/src/views/strategy/ResultsQuery.vue`
- `web/frontend/src/views/strategy/SingleRun.vue`
- `web/frontend/src/views/strategy/StatsAnalysis.vue`

Closed B4.006 residue inside the ST-5 exact file list: `0`.

## Evidence Snapshot

Repository evidence:

- Current branch: `wip/root-dirty-20260403`
- Current HEAD: `9fddbd140e1f`
- Worktree dirty rows: `1145`
- Frontend dirty rows: `165`
- Dirty `web/frontend/src/views/**` rows: `111`
- B4.007 active candidate files after exclusions: `40`

GitNexus evidence:

- `node .gitnexus/run.cjs status`
- Indexed commit: `9fddbd1`
- Current commit: `9fddbd1`
- Status: `up-to-date`

OPENDOG evidence:

- `opendog verification --id mystocks --json`
- Freshness: `fresh`
- Failing runs: `0`
- Cleanup blockers: `0`
- All expected kinds recorded: `true`
- Gate level: `caution`
- Caution reason is advisory evidence hygiene, not a B4.007 failure: lint evidence is stale/incomplete and some previous recorded commands have pipeline-masking caveats.

Router truth evidence:

- `web/frontend/src/router/index.ts` currently has `44` dynamic route imports.
- Among the `40` B4.007 active candidates, `3` are directly imported by the router:
  - `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue` as `stock-graphics` (`graphics/:symbol`)
  - `web/frontend/src/views/Login.vue` as `login` (`/login`)
  - `web/frontend/src/views/NotFound.vue` as `not-found` (`/:pathMatch(.*)*`)
- The other `37` active candidates are non-direct route-truth, sidecar, workbench, or legacy evidence rows.
- `/dashboard` route truth remains `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`, not root `web/frontend/src/views/Dashboard.vue`.
- `/trade/terminal` route truth remains `web/frontend/src/views/TradingDashboard.vue`; that file is not part of the active dirty B4.007 list after the ST-5 closeout.
- `/system/config` route truth remains `web/frontend/src/views/system/Settings.vue`, not root `web/frontend/src/views/Settings.vue`.

## Active Candidate File List

### AR-1 Active Route Exceptions

Risk: medium-high. These files are current router targets or active route exception support. Each source package must run GitNexus impact before accepting/staging the file.

Files:

- `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`
- `web/frontend/src/views/Login.vue`
- `web/frontend/src/views/NotFound.vue`

Diff scale:

- Files: `3`
- Tracked diff files: `3`
- Untracked files: `0`
- Total diff: `+699 / -470`

Focused test scope:

- `cd web/frontend && npm run test -- src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts tests/unit/config/shell-route-runtime-guardrails.spec.ts`
- `cd web/frontend && npm run type-check`
- For `Login.vue`, add or run a focused Playwright login route smoke before commit. Existing test candidate: `tests/authenticated-page-validation.spec.ts --grep "Login should succeed"`.
- Any package that changes visible route behavior must also run a focused Chromium route smoke with `PLAYWRIGHT_EXTERNAL_FRONTEND=1`.

### AR-2 ArtDeco Noncanonical Workbench Truth

Risk: medium. These files live under ArtDeco workbench/support paths but are not direct router truth in the current router.

Files:

- `web/frontend/src/views/artdeco-pages/ArtDecoMarketQuotes.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue`
- `web/frontend/src/views/artdeco-pages/components/ArtDecoSignalHistory.vue`
- `web/frontend/src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts`
- `web/frontend/src/views/artdeco-pages/stock-management-tabs/__node_tests__/stockManagementRouteData.test.ts`
- `web/frontend/src/views/artdeco-pages/stock-management-tabs/stockManagementRouteData.ts`

Diff scale:

- Files: `6`
- Tracked diff files: `6`
- Untracked files: `0`
- Total diff: `+112 / -178`

Focused test scope:

- `cd web/frontend && npm run test -- tests/unit/config/console-log-cleanup-batch-1.spec.ts tests/unit/config/artdeco-technical-analysis-static-shell.spec.ts tests/unit/config/domain-body-migration-ownership.spec.ts`
- `cd web/frontend && node --test src/views/artdeco-pages/market-tabs/__node_tests__/marketKlineData.test.ts src/views/artdeco-pages/stock-management-tabs/__node_tests__/stockManagementRouteData.test.ts`
- `cd web/frontend && npm run type-check`

### RL-1 Root Legacy View Truth

Risk: medium-high governance risk. These root-level Vue pages are dirty but not current canonical router imports after B4.002-B4.006 exclusions. Do not accept them as one source package. Do not delete or retire them in an ordinary B4.007 source package.

Files:

- `web/frontend/src/views/AdvancedAnalysis.vue`
- `web/frontend/src/views/Analysis.vue`
- `web/frontend/src/views/Dashboard.vue`
- `web/frontend/src/views/EnhancedDashboard.vue`
- `web/frontend/src/views/EnhancedRiskMonitor.vue`
- `web/frontend/src/views/IndicatorLibrary.vue`
- `web/frontend/src/views/IndustryConceptAnalysis.vue`
- `web/frontend/src/views/Market.vue`
- `web/frontend/src/views/MarketData.vue`
- `web/frontend/src/views/monitor.vue`
- `web/frontend/src/views/Phase4Dashboard.vue`
- `web/frontend/src/views/PortfolioManagement.vue`
- `web/frontend/src/views/RealTimeMonitor.vue`
- `web/frontend/src/views/RiskMonitor.vue`
- `web/frontend/src/views/Settings.vue`
- `web/frontend/src/views/StockAnalysisDemo.vue`
- `web/frontend/src/views/StockDetail.vue`
- `web/frontend/src/views/Stocks.vue`
- `web/frontend/src/views/TaskManagement.vue`
- `web/frontend/src/views/TdxMarket.vue`
- `web/frontend/src/views/TechnicalAnalysis.vue`
- `web/frontend/src/views/TestPage.vue`
- `web/frontend/src/views/Wencai.vue`

Diff scale:

- Files: `23`
- Tracked diff files: `23`
- Untracked files: `0`
- Total diff: `+1457 / -7345`

Focused test scope:

- First package must be a no-source disposition table that marks each file as preserve, compatibility wrapper, move-to-canonical, archive-only, or deletion-retirement candidate.
- Any later source package must be split by domain and must run `cd web/frontend && npm run type-check`.
- If a root legacy file is kept as a compatibility wrapper, pair it with its exact root-view test if present and run that Vitest spec.
- If a root legacy file is proposed for deletion or retirement, stop and route it to a separate deletion-retirement authorization.

### SR-1 Strategy/Trade Sidecar Route Truth

Risk: medium. This is the B4.006 ST-6 handoff: sidecar/noncanonical strategy/trade/trading/trade-management rows not closed by ST-5.

Files:

- `web/frontend/src/views/artdeco-pages/ArtDecoTradingManagement.vue`
- `web/frontend/src/views/artdeco-pages/portfolio-tabs/portfolioOverviewData.ts`
- `web/frontend/src/views/artdeco-pages/portfolio-tabs/__tests__/portfolioOverviewData.spec.ts`
- `web/frontend/src/views/trading/Positions.vue`
- `web/frontend/src/views/TradeManagement.vue`

Diff scale:

- Files: `5`
- Tracked diff files: `5`
- Untracked files: `0`
- Total diff: `+134 / -542`

Focused test scope:

- `cd web/frontend && npm run test -- src/views/__tests__/TradeManagement.spec.ts src/views/artdeco-pages/portfolio-tabs/__tests__/portfolioOverviewData.spec.ts tests/unit/config/trade-management-style-entrypoint.spec.ts`
- `cd web/frontend && npm run type-check`
- If `ArtDecoTradingManagement.vue` route behavior is accepted, add/run its focused component spec before commit.

### SR-2 Shared/Static Governance Tests

Risk: low-medium. This is the B4.006 ST-7 handoff: static governance tests only. It must not be mixed with source changes.

Files:

- `web/frontend/tests/unit/config/legacy-strategy-workbench-decommission.spec.ts`
- `web/frontend/tests/unit/config/trade-management-components-normalization.spec.ts`
- `web/frontend/tests/unit/config/trade-management-style-entrypoint.spec.ts`

Diff scale:

- Files: `3`
- Tracked diff files: `2`
- Untracked files: `1`
- Total tracked diff: `+30 / -22`

Focused test scope:

- `cd web/frontend && npm run test -- tests/unit/config/legacy-strategy-workbench-decommission.spec.ts tests/unit/config/trade-management-components-normalization.spec.ts tests/unit/config/trade-management-style-entrypoint.spec.ts`
- `cd web/frontend && npm run type-check`

## Empty Or Resolved From The 2026-06-06 B4.007 Preflight

Root legacy test evidence is no longer active dirty in the refreshed scan:

- Count: `0`
- Previous 23 root legacy test evidence paths are currently clean or no longer in the active dirty set.

The previous 2026-06-06 B4.007 preflight report remains untracked and was not modified by this refresh.

## Recommended Commit Queue

1. `B4.007-A no-source route-truth preflight`
   - File: this report only.
   - Gate: staged-only report path; GitNexus fresh; OPENDOG fresh.
   - No frontend type-check or E2E required because this is a no-source evidence artifact.

2. `B4.007-B SR-2 shared/static governance tests`
   - Test-only package.
   - Gate: focused Vitest, type-check, GitNexus staged detect, OPENDOG recorded, staged-only exact 3 files.

3. `B4.007-C AR-2 ArtDeco noncanonical workbench truth`
   - Non-direct route ArtDeco support package.
   - Gate: focused Vitest/node tests, type-check, GitNexus staged detect, OPENDOG recorded, staged-only exact files.

4. `B4.007-D SR-1 strategy/trade sidecar route truth`
   - Sidecar route-truth package.
   - Gate: focused Vitest, type-check, GitNexus staged detect, OPENDOG recorded, staged-only exact files.

5. `B4.007-E AR-1 active route exceptions`
   - Split further if impact is not low after GitNexus staged detect:
     - `KLineAnalysis.vue`
     - `Login.vue` and `NotFound.vue`
   - Gate: GitNexus impact before accepting each directly routed symbol/file; focused unit; type-check; focused Chromium route smoke; OPENDOG recorded.

6. `B4.007-F RL-1 root legacy disposition`
   - No-source decision table before source acceptance.
   - Split source implementation by domain only after each file has a route-truth disposition.
   - Deletion or full retirement remains outside ordinary B4.007 source authorization.

## Commit-Time Gates For Source/Test Packages

Each later source/test package must satisfy all of the following before commit:

- GitNexus index fresh at current HEAD.
- GitNexus impact before editing/accepting symbols.
- GitNexus staged detect reports expected files/symbols and no unexpected high-risk blast radius.
- OPENDOG verification evidence recorded for focused tests/build.
- `cd web/frontend && npm run type-check` exits `0`.
- Focused unit/node tests pass for the target files.
- Focused Chromium E2E route smoke runs for active route packages.
- `git diff --check --cached` exits `0`.
- Staged files exactly match the package file list.
- Target files have no unstaged residue.
- ST-HOLD, closed B4.003-B4.006, and unrelated dirty files stay untouched.
