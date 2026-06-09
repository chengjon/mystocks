# B4.007-M1 Frontend Mainline Route Continuity No-Source Audit

Date: 2026-06-07
Branch: `wip/root-dirty-20260403`
HEAD: `b2a559c1741aae5619ab5083ab6ad43a18ab168b`
FUNCTION_TREE program: `.governance/programs/artdeco-web-design-governance`
FUNCTION_TREE node: `b4-frontend-mainline-route-truth`
Node title: `Frontend mainline route truth and runtime continuity`
Mode: no-source audit

## 1. Boundary

This audit freezes the remaining F3 single-file archive cleanup and treats the 11 root legacy view files as Backlog evidence only.

No source, test, router, menu, config, migration, deletion, or file move is authorized in M1. This report only records facts, route truth, test evidence, and M2 candidates.

Strictly excluded from action in this pass:

- ST-HOLD
- `marketKlineData`
- already closed ST-1 to ST-4 / B4.007 implementation packages
- external dirty files
- F3d/F3e archive-only single-file retirement

## 2. Evidence Commands And Gate Snapshot

| Gate / Evidence | Result |
|---|---|
| GitNexus freshness | `mystocks` indexed at `2026-06-07T09:54:10.588Z`; indexed `lastCommit` equals current HEAD `b2a559c1741aae5619ab5083ab6ad43a18ab168b`; no staleness reported for `mystocks`. |
| OPENDOG verification | Fresh verification available; `cleanup_blockers: []`; `failing_runs: []`; cleanup/refactor allowed with caution because advisory lint evidence is stale / historical pipeline evidence is not ideal. |
| PM2 | `mystocks-backend` online at `http://localhost:8020`; `mystocks-frontend` online at `http://localhost:3020`. |
| Type check | `cd web/frontend && npm run type-check` passed (`vue-tsc --noEmit`, exit 0). |
| Focused unit | `cd web/frontend && npm run test -- src/router/__tests__/home-route.spec.ts src/router/__tests__/utils.spec.ts src/stores/__tests__/auth-guard-route-meta.spec.ts src/stores/__tests__/auth-guard.spec.ts` passed: 4 files, 54 tests. |
| Focused E2E first run | `npm run test:e2e:business-smoke` did not execute tests because Playwright attempted to bind `http://localhost:3020` while PM2 frontend already occupied the port. |
| Focused E2E PM2-backed rerun | `PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke`; chromium, 55 tests: 39 passed, 5 failed, 11 did not run. Failures are listed in section 8. |
| Git index isolation | Pre-existing staged external file observed: `.claude/settings.json`. Left untouched. M1 generated only report/governance artifacts. |

## 3. Active Route Truth Summary

Source of truth: `web/frontend/src/router/index.ts`.

Extracted with TypeScript AST from the actual `routes` array.

| Metric | Value |
|---|---:|
| Active route records | 55 |
| Redirect records | 11 |
| Alias records | 1 |
| Missing component files | 0 |

Route count by first path segment:

| Segment | Count |
|---|---:|
| root | 1 |
| dashboard | 1 |
| market | 4 |
| data | 5 |
| watchlist | 4 |
| strategy | 8 |
| ai | 4 |
| trade | 8 |
| risk | 7 |
| system | 6 |
| detail | 3 |
| qm | 2 |
| login | 1 |
| catch-all | 1 |

## 4. Mainline Route Matrix

| Path | Name | Component / Redirect | Menu Truth | Notes |
|---|---|---|---|---|
| `/` | n/a | `layouts/ArtDecoLayoutEnhanced.vue`; redirects to `HOME_ROUTE_PATH` | app shell | Root layout shell. |
| `/dashboard` | n/a | `views/artdeco-pages/ArtDecoDashboard.vue` | active | Canonical dashboard exception remains ArtDeco page. |
| `/market` | n/a | redirects to `/market/realtime` | active parent | Parent only. |
| `/market/realtime` | `market-realtime` | `views/market/Realtime.vue` | active | Canonical market realtime. |
| `/market/technical` | `market-technical` | `views/market/Technical.vue` | active | Canonical technical market view. |
| `/market/lhb` | `market-lhb` | `views/market/LHB.vue` | active | Canonical LHB view. |
| `/data` | n/a | redirects to `/data/industry` | active parent | Parent only. |
| `/data/industry` | `data-industry` | `views/data/Industry.vue` | active | Canonical data industry. |
| `/data/concept` | `data-concept` | `views/data/Concepts.vue` | active | Canonical concepts. |
| `/data/fund-flow` | `data-fund-flow` | `views/data/FundFlow.vue` | active | Canonical fund flow. |
| `/data/indicator` | `data-indicator` | `views/data/Advanced.vue` | active | Canonical indicator/advanced data. |
| `/watchlist` | n/a | redirects to `/watchlist/manage` | active parent | Parent only. |
| `/watchlist/manage` | `watchlist-manage` | `views/watchlist/Manage.vue` | active | Canonical watchlist management. |
| `/watchlist/signals` | `watchlist-signals` | `views/watchlist/Signals.vue` | active | Canonical watchlist signals. |
| `/watchlist/screener` | `watchlist-screener` | `views/watchlist/Screener.vue` | active | Canonical screener. |
| `/strategy` | n/a | redirects to `/strategy/repo` | active parent | Parent only. |
| `/strategy/repo` | `strategy-repo` | `views/strategy/List.vue` | active | Canonical strategy list. |
| `/strategy/parameters` | `strategy-parameters` | `views/strategy/Parameters.vue` | active | Canonical strategy parameters. |
| `/strategy/signals` | `strategy-signals` | `views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | active | Active ArtDeco tab component remains in mainline. |
| `/strategy/backtest` | `strategy-backtest` | `views/strategy/Backtest.vue` | active | Canonical backtest. |
| `/strategy/gpu` | `strategy-gpu` | `views/strategy/BacktestGPU.vue` | active | Canonical GPU backtest. |
| `/strategy/opt` | `strategy-opt` | `views/strategy/Optimization.vue` | active | Canonical optimization. |
| `/strategy/pos` | `strategy-pos` | `views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` | active | Cross-domain ArtDeco position tab remains active under strategy. |
| `/trade` | n/a | redirects to `/trade/terminal` | active parent | Parent only. |
| `/trade/positions` | `trade-positions` | `views/trade/Center.vue` | active | Canonical trade positions. |
| `/trade/terminal` | `trade-terminal` | `views/TradingDashboard.vue` | active | Current explicit route-truth exception. |
| `/trade/execution` | `trade-execution` | `views/trade/Execution.vue` | active | Canonical execution. |
| `/trade/signals` | `trade-signals` | `views/trade/Signals.vue` | active | Canonical trade signals. |
| `/trade/portfolio` | `trade-portfolio` | `views/trade/Portfolio.vue` | active | Canonical portfolio trade view. |
| `/trade/history` | `trade-history` | `views/trade/History.vue` | active | Canonical trade history. |
| `/trade/reconciliation` | `trade-reconciliation` | `views/trade/Reconciliation.vue` | active | Canonical reconciliation. |
| `/risk` | n/a | redirects to `/risk/overview` | active parent | Parent only. |
| `/risk/management` | `risk-management` | `views/risk/Center.vue` | active; alias `/risk-management` | Only active alias found. |
| `/risk/overview` | `risk-overview` | `views/risk/Overview.vue` | active | Canonical risk overview. |
| `/risk/pnl` | `risk-pnl` | `views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | active | ArtDeco portfolio tab remains active under risk. |
| `/risk/stop-loss` | `risk-stop-loss` | `views/risk/StopLoss.vue` | active | Canonical stop-loss. |
| `/risk/alerts` | `risk-alerts` | `views/risk/Alerts.vue` | active | Canonical risk alerts. |
| `/risk/news` | `risk-news` | `views/risk/News.vue` | active | Current route for announcement/news function. |
| `/system` | n/a | redirects to `/system/config` | active parent | Parent only. |
| `/system/config` | `system-config` | `views/system/Settings.vue` | active | Canonical settings/config. |
| `/system/health` | `system-health` | `views/system/Health.vue` | active | Canonical health. |
| `/system/api` | `system-api` | `views/system/API.vue` | active | Canonical API view. |
| `/system/resources` | `system-resources` | `views/system/Resources.vue` | active | Canonical resources. |
| `/system/data` | `system-data` | `views/system/DataSource.vue` | active | Canonical data source view. |

## 5. Utility / Compatibility Routes

| Path | Component / Redirect | Mainline Status |
|---|---|---|
| `/ai` | redirects to `/ai/sentiment` | Active but not in current mainline menu path set. |
| `/ai/sentiment` | `views/ai/Sentiment.vue` | Hidden/secondary route. |
| `/ai/ml` | `views/ai/MlWorkbench.vue` | Hidden/secondary route. |
| `/ai/batch` | `views/ai/BatchAnalysis.vue` | Hidden/secondary route. |
| `/detail` | parent detail shell | Hidden detail parent. |
| `/detail/graphics/:symbol` | `views/artdeco-pages/analysis-tabs/KLineAnalysis.vue` | Active detail graphics route. |
| `/detail/news/:symbol` | `views/announcement/AnnouncementMonitor.vue` | Active detail news route. |
| `/qm` | redirects to `HOME_ROUTE_PATH` | Compatibility route. |
| `/qm/:pathMatch(.*)*` | normalizes compatibility paths | Compatibility route. |
| `/login` | `views/Login.vue` | Auth utility route. |
| `/:pathMatch(.*)*` | `views/NotFound.vue` | Catch-all. |

## 6. Menu / Router Inconsistency Matrix

Active menu/config path sources checked:

- `web/frontend/src/layouts/MenuConfig.ts`: 43 path entries
- `web/frontend/src/config/menu.config.js`: 26 path entries
- `web/frontend/src/stores/menuStore.ts`: no literal path entries

Menu paths with no active route and no alias:

| Menu Path | Current Router Truth | M2 Candidate |
|---|---|---|
| `/market/wencai` | no active route; root `views/Wencai.vue` exists but is not routed | Decide whether to add route/alias or remove menu entry. |
| `/technical/indicators` | no active route; current equivalent appears to be `/data/indicator` | Align menu or add alias if backwards compatibility is required. |
| `/technical/analysis` | no active route; current equivalent appears to be `/market/technical` | Align menu or add alias if backwards compatibility is required. |
| `/strategy/management` | no active route; current equivalent appears to be `/strategy/repo` | Align menu path or alias. |
| `/strategy/risk` | no active route; risk is now under `/risk/*` | Remove or intentionally redirect. |
| `/monitoring/watchlists` | no active route; current equivalent appears to be `/watchlist/manage` | Align menu path or alias. |
| `/risk/announcement` | no active route; current route is `/risk/news` | Align menu path or alias. |
| `/stocks/management` | no active route; current equivalent appears to be `/watchlist/manage` or stock-management ArtDeco tabs | Needs product decision. |
| `/stocks/portfolio` | no active route; current equivalent appears to be `/trade/portfolio` or `/risk/pnl` depending semantics | Needs product decision. |
| `/system/architecture` | no active route | Remove, alias, or create route in M2 only if still product-relevant. |
| `/system/database-monitor` | no active route | Remove, alias, or create route in M2 only if still product-relevant. |
| `/system/monitoring` | no active route | Current system routes are `/system/health`, `/system/resources`, `/system/data`. |
| `/system/logs` | no active route | Remove, alias, or create route in M2 only if still product-relevant. |
| `/system/settings` | no active route; current route is `/system/config` | Align menu path or alias. |
| `/data/import` | no active route | Remove, alias, or create route in M2 only if still product-relevant. |

Active routes absent from current menu path set:

| Route | Interpretation |
|---|---|
| `/ai`, `/ai/sentiment`, `/ai/ml`, `/ai/batch` | Hidden/secondary AI routes unless product wants them in main navigation. |
| `/detail`, `/detail/graphics/:symbol`, `/detail/news/:symbol` | Detail routes are expected to be deep links, not menu entries. |
| `/qm`, `/qm/:pathMatch(.*)*` | Compatibility routes; expected to remain hidden. |
| `/login` | Auth route; expected to remain hidden. |

## 7. Domain Dependency Summary

Direct imports from active route components, grouped by mainline domain:

| Domain | Route Components | Store Imports | API Imports | Composable Imports |
|---|---:|---|---|---|
| dashboard | 1 | none | none | `views/artdeco-pages/composables/useArtDecoDashboard` |
| data | 4 | none | `api/apiClient`, `api/types/common` | `composables/artdeco/useArtDecoApi`, `composables/market/useDataAnalysis` |
| market | 3 | none | `api/apiClient`, `api/index` | `composables/artdeco/useArtDecoApi` |
| watchlist | 3 | none | none | none |
| strategy | 7 | `stores/apiStores` | none | `composables/strategy/useStrategyCrossTabContext`, `views/strategy/composables/useBacktestGPU` |
| trade | 7 | `stores/apiStores` | `api/apiClient`, `api/trade`, `api/tradeExecutionTracking.ts` | `composables/artdeco/useArtDecoApi`, `views/composables/useTradingDashboard`, `composables/attribution/useAttributionAnalysis.ts`, `views/trade/composables/useTradeReconciliation` |
| risk | 6 | none | `api/index`, `api/types/common`, `api/apiClient` | `composables/artdeco/useArtDecoApi`, `views/ai/composables/useAiSentimentWorkbench` |
| system | 5 | `stores/apiStores`, `stores/storePolicies` | `api/apiClient`, `api/index` | `composables/artdeco/useArtDecoApi`, `composables/useBackendReadiness`, `views/system/composables/useSystemResourcesPage` |

No missing active route component file was found.

## 8. Focused Test Findings

The focused E2E command covered:

- `tests/e2e/auth-login.spec.ts`
- `tests/e2e/critical/menu-navigation-fixed.spec.ts`
- `tests/e2e/market-data.spec.ts`
- `tests/e2e/risk-overview.spec.ts`
- `tests/e2e/risk-pnl.spec.ts`
- `tests/e2e/trade-terminal.spec.ts`
- `tests/e2e/strategy-management-chain.spec.ts`
- `tests/e2e/strategy-backtest.spec.ts`
- `tests/e2e/kline-chart.spec.ts`

Actual result with PM2-backed frontend:

| Browser Project | Total | Passed | Failed | Did Not Run |
|---|---:|---:|---:|---:|
| chromium | 55 | 39 | 5 | 11 |

Failures:

| Test | Failure |
|---|---|
| `tests/e2e/critical/menu-navigation-fixed.spec.ts:74` | Expected H1 `QUANTIX` not found after main shell becomes visible. |
| `tests/e2e/critical/menu-navigation-fixed.spec.ts:81` | Same H1 `QUANTIX` missing while navigating to market realtime via sidebar. |
| `tests/e2e/critical/menu-navigation-fixed.spec.ts:89` | Same H1 `QUANTIX` missing in market API failure scenario. |
| `tests/e2e/kline-chart.spec.ts:149` | Critical console error: `vue-i18n` reports `Need to install with app.use function`, from `src/composables/useI18n.ts` via `ArtDecoSkipLink.vue`. |
| `tests/e2e/market-data.spec.ts:241` | Playwright strict locator conflict: `PRESET: 核心蓝筹样本` appears in both `market-realtime-header` and `market-realtime-control-row`. |

Unit guard coverage passed:

| Unit Scope | Files | Tests | Result |
|---|---:|---:|---|
| router utils, home route, auth guard route meta, auth guard store | 4 | 54 | passed |

## 9. F2a / F2b Thin Wrapper Status

Exact route component matching shows none of these wrappers is directly mounted by `router/index.ts`.

| Wrapper | Canonical / Target Import | Exact Active Route Component? | Mainline Verdict |
|---|---|---|---|
| `views/Dashboard.vue` | `views/artdeco-pages/ArtDecoDashboard.vue` | no | Thin compatibility shell; not active route truth. |
| `views/EnhancedDashboard.vue` | `views/artdeco-pages/ArtDecoDashboard.vue` | no | Thin compatibility shell; not active route truth. |
| `views/Phase4Dashboard.vue` | `views/artdeco-pages/ArtDecoDashboard.vue` | no | Thin compatibility shell; not active route truth. |
| `views/Settings.vue` | `views/system/Settings.vue` | no | Thin compatibility shell; not active route truth. |
| `views/EnhancedRiskMonitor.vue` | `views/risk/Center.vue` | no | Thin compatibility shell; not active route truth. |
| `views/RiskMonitor.vue` | `views/risk/Center.vue` | no | Thin compatibility shell; not active route truth. |
| `views/IndicatorLibrary.vue` | `views/data/Advanced.vue` | no | Thin compatibility shell; not active route truth. |
| `views/Market.vue` | `views/trade/Portfolio.vue` | no | Thin compatibility shell; imported target looks semantically suspicious, but it is not in active route truth. |
| `views/Wencai.vue` | `components/market/WencaiPanel.vue` | no | Shell exists; `/market/wencai` menu path has no active route. |

## 10. Frozen F3 Backlog Legacy Files

Exact active route component matching: all 11 are not active route components.

Exact active source module imports: none.

Each file still has a direct local unit test import under `web/frontend/src/views/__tests__/`, so deletion or relocation requires a separately authorized Backlog batch that handles test disposition.

| Backlog File | Active Route? | Active Source Import? | Remaining Test Anchor |
|---|---|---|---|
| `views/Analysis.vue` | no | no | `views/__tests__/Analysis.spec.ts` |
| `views/IndustryConceptAnalysis.vue` | no | no | `views/__tests__/IndustryConceptAnalysis.spec.ts` |
| `views/MarketData.vue` | no | no | `views/__tests__/MarketData.spec.ts` |
| `views/monitor.vue` | no | no | `views/__tests__/monitor.spec.ts` |
| `views/PortfolioManagement.vue` | no | no | `views/__tests__/PortfolioManagement.spec.ts` |
| `views/RealTimeMonitor.vue` | no | no | `views/__tests__/RealTimeMonitor.spec.ts` |
| `views/StockDetail.vue` | no | no | `views/__tests__/StockDetail.spec.ts` |
| `views/Stocks.vue` | no | no | `views/__tests__/Stocks.spec.ts` |
| `views/TaskManagement.vue` | no | no | `views/__tests__/TaskManagement.spec.ts` |
| `views/TdxMarket.vue` | no | no | `views/__tests__/TdxMarket.spec.ts` |
| `views/TechnicalAnalysis.vue` | no | no | `views/__tests__/TechnicalAnalysis.spec.ts` |

M1 conclusion: the 11 files are decoupled from active mainline routing, but not free to delete. Their remaining test anchors and historical report references belong in the frozen Backlog batch.

## 11. Mainline Breakpoints And Risks

### Blocking / High-Priority For M2

1. Menu config contains 15 paths without active route or alias. These are visible navigation-risk candidates because menu clicks can land on missing routes unless another runtime layer rewrites them.
2. Business smoke E2E has a critical menu/navigation failure: dashboard shell no longer exposes H1 `QUANTIX`, while the critical menu test still treats it as route continuity evidence.
3. K-line E2E catches a global runtime error from `vue-i18n` installation state through `ArtDecoSkipLink.vue`.
4. Market realtime E2E has a strict locator conflict from duplicated `PRESET: 核心蓝筹样本` text.

### Medium Priority / Decision Needed

1. `/market/wencai` is present in menu/config but no active route exists. Root `views/Wencai.vue` exists as a non-routed wrapper around `components/market/WencaiPanel.vue`.
2. System menu paths appear older than router truth (`/system/settings`, `/system/monitoring`, `/system/logs`, `/system/database-monitor`, `/system/architecture` versus `/system/config`, `/system/health`, `/system/api`, `/system/resources`, `/system/data`).
3. Stock/technical legacy menu semantics still point outside the current canonical route tree.
4. Active ArtDeco tab components remain intentionally mounted in strategy/risk/detail paths; these are not archive candidates while route truth depends on them.

### Backlog Only

1. F2a/F2b thin wrappers are not active route truth.
2. The 11 F3 legacy files are route/source decoupled but have unit test anchors.
3. Archive-only deletion/retirement remains frozen until after M1 to M3 mainline closure.

## 12. Recommended Next Step

Proceed to B4.007-M2 with a small, source-authorized mainline continuity repair package. Suggested order:

1. Fix or explicitly retire the 15 menu paths that have no active router equivalent, prioritizing visible menu entries.
2. Decide whether the E2E H1 `QUANTIX` assertion should follow the new ArtDeco shell truth or whether the shell should restore that accessible heading.
3. Fix the `vue-i18n` runtime installation path affecting `ArtDecoSkipLink.vue`.
4. Fix market realtime duplicated locator text or test selector scope.
5. Rerun type-check, focused unit, and the same PM2-backed business smoke E2E until the mainline route continuity gate is green.

Do not resume F3 archive-only backlog until M2 and M3 mainline route continuity are closed.
