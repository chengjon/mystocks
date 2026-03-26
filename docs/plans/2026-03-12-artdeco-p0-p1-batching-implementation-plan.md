# ArtDeco P0/P1 Batching Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 ArtDeco 页面优化首轮范围从“34 页优先级清单”收敛为符合治理基线的 `Gate-0 + P0/P1` 可执行批次，明确每批的页面范围、共享文件、验证入口和阻塞边界。

**Architecture:** 先执行 `Gate-0` 治理校对，统一 `Container-Tab`、`Base/Domain`、`router/menu/API/tokens` 的单一事实源，再按共享组件和共享 API 聚合页面批次推进。对 `API pending` 页面采取“状态收口 + 空态/错误态 + 阻塞登记”的执行策略；对 `API verified` 页面要求完成真实数据链路和 E2E 断言。

**Tech Stack:** Markdown, OpenSpec, Vue 3, TypeScript, SCSS tokens, Playwright, PM2

---

## Batch Matrix

| Batch | Pages | Shared focus | API posture | Primary verification |
|------|------|------|------|------|
| `Gate-0` | All `P0/P1` | `Container-Tab`, `components/[domain]`, tokens, route/API metadata | mixed | page-config, token audit, optimization audit |
| `P0-A` | `Market-Realtime`, `Market-Technical` | market core tabs | verified | market-data, kline-chart, PM2 smoke |
| `P0-B` | `Login`, `DealingRoom` | auth entry + dashboard container | pending | auth/login, dashboard, PM2 smoke |
| `P1-A` | `Market-LHB`, `Data-Industry`, `Data-Concept`, `Data-FundFlow`, `Data-Indicator` | market-data tabs + shared analysis blocks | mixed | market-data, comprehensive pages |
| `P1-B` | `Watchlist-Signals`, `Strategy-Signals`, `Trade-Signals`, `Trade-Positions`, `Trade-Portfolio`, `Risk-PnL` | shared signals/positions models | mixed | strategy-management, trade-management, comprehensive pages |
| `P1-C` | `Strategy-Repo`, `Strategy-Parameters`, `Strategy-Backtest` | strategy tabs + backtest workbench | verified | strategy-management, strategy-backtest |
| `P1-D` | `Risk-Management`, `Risk-Overview`, `Risk-StopLoss`, `Risk-Alerts` | risk container + alert/stop-loss tabs | mixed | risk-monitor, comprehensive pages |
| `P1-E` | `Watchlist-Manage`, `Watchlist-Screener`, `Trade-Terminal`, `Trade-History` | watchlist management + trading shell/history | mixed | trade-management, comprehensive pages |

### Execution Rules

- `API verified` batch: 必须完成真实接口渲染、错误态/空态收口、REQ_ID 展示位和批次级 E2E 断言。
- `API pending` batch: 禁止臆造字段契约，先完成容器壳层、加载/错误/空态、令牌清理和 blocker 登记。
- 任何涉及页面块分拆时，优先复用 `views/artdeco-pages/components/*`；仅页面专属逻辑允许留在 `*-tabs/`。
- 任何样式调整必须回到 `web/frontend/src/styles/artdeco-tokens.scss`，不得新增硬编码颜色或间距。

### Task 1: Gate-0 ArtDeco 治理校对

**Files:**
- Modify: `openspec/changes/optimize-artdeco-pages/tasks.md`
- Modify: `docs/plans/frontend-page-optimization-list.md`
- Review/Modify: `web/frontend/src/router/index.ts`
- Review/Modify: `web/frontend/src/config/pageConfig.ts`
- Review/Modify: `docs/guides/web/ARTDECO_MASTER_INDEX.md`
- Review/Modify: `docs/api/ArtDeco_System_Architecture_Summary.md`
- Review: `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
- Review: `web/frontend/src/styles/artdeco-tokens.scss`

**Step 1: 建立 P0/P1 页面分类矩阵**

将 26 个页面逐一标记：
- `container-only`
- `tab-only`
- `needs-domain-component-extraction`
- `needs-token-cleanup`
- `api-pending-blocked`

**Step 2: 校对治理真值漂移**

至少核对以下几类漂移：
- `router` 与 `frontend-page-optimization-list` 的 API 标注是否一致
- `ARTDECO_MASTER_INDEX` 与 `artdeco-tokens.scss` 的字体/令牌描述是否一致
- 页面是否违反 `components/[domain]` 与 `*-tabs/` 边界

**Step 3: 锁定批次验证入口**

为每个批次指明要跑的 `vitest`、`playwright` 和 `PM2 smoke` 入口，避免执行时临时找测试。

**Step 4: 自检**

Run: `npm --prefix web/frontend run validate-page-config`

Expected: `pageConfig` 结构合法，无新增配置漂移。

Run: `npm --prefix web/frontend run lint:artdeco`

Expected: 无新增设计令牌违规。

Run: `python scripts/dev/frontend_optimization_audit.py --repo-root . --strict --report-file reports/analysis/frontend-page-optimization-audit-report.md`

Expected: 审计报告生成，新增漂移或 pending 页面被明确记录。

### Task 2: 执行 P0-A 市场核心批次

**Files:**
- Modify: `web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue`
- Modify: `web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoRealtimeMonitor.vue`
- Review/Modify: `web/frontend/src/composables/artdeco/useArtDecoApi.ts`
- Review/Modify: `web/frontend/src/config/pageConfig.ts`
- Test: `web/frontend/tests/e2e/market-data.spec.ts`
- Test: `web/frontend/tests/e2e/kline-chart.spec.ts`
- Verify: `tests/navigation-consistency.spec.ts`

**Step 1: 先补失败断言**

为实时行情和 K 线页增加以下断言：
- 页面核心区可见
- `loading/error/empty` 状态切换
- REQ_ID 展示位存在
- 真值接口返回后至少一组关键数据可见

**Step 2: 收口 mixed 状态**

移除页面内零散的 mock/mixed 分支，统一走 `useArtDecoApi` 和 `pageConfig` 配置，保证失败时转空态或错误态，而不是静默回退。

**Step 3: 清理视觉债**

检查是否存在硬编码颜色、间距、涨跌语义错误，统一回到 `artdeco-tokens.scss`。

**Step 4: 批次验证**

Run: `npm --prefix web/frontend run type-check`

Expected: 不高于技术债基线。

Run: `cd web/frontend && npx playwright test --config playwright.config.js --project=chromium tests/e2e/market-data.spec.ts tests/e2e/kline-chart.spec.ts`

Expected: `chromium` 项目通过，失败用例只允许是既有技术债并需记录。

Run: `bash scripts/run_e2e_pm2.sh`

Expected: `tests/navigation-consistency.spec.ts` 在 PM2 环境通过。

### Task 3: 执行 P0-B 入口壳层批次

**Files:**
- Modify: `web/frontend/src/views/Login.vue`
- Modify: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- Review/Modify: `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.chart-options.ts`
- Review/Modify: `web/frontend/src/router/guards.ts`
- Review/Modify: `web/frontend/src/router/index.ts`
- Test: `tests/e2e/login.spec.js`
- Test: `tests/e2e/specs/auth.spec.ts`
- Test: `tests/e2e/dashboard.spec.ts`
- Test: `web/frontend/tests/artdeco-dashboard.spec.ts`

**Step 1: 明确入口页目标**

`Login` 与 `DealingRoom` 先保证：
- 登录壳层完整
- 仪表板骨架可用
- `loading/error/empty` 和 REQ_ID 展示位齐全
- 不在 API `pending` 状态下臆造字段

**Step 2: 统一容器职责**

父容器负责：
- 路由接入
- 顶层状态
- API/Tab 配置

专属业务块留在页面或 `*-tabs/`，可复用块抽到 `components/`。

**Step 3: 批次验证**

Run: `npm --prefix web/frontend run type-check`

Expected: 不高于技术债基线。

Run: `BASE_URL=http://localhost:3020 npx playwright test tests/e2e/login.spec.js tests/e2e/specs/auth.spec.ts tests/e2e/dashboard.spec.ts --config playwright.config.ts --project=chromium`

Expected: 登录与仪表板基础链路通过或阻塞被明确记录。

Run: `bash scripts/run_e2e_pm2.sh`

Expected: 导航一致性门禁通过。

### Task 4: 执行 P1-A 市场数据域批次

**Files:**
- Modify: `web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue`
- Modify: `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue`
- Modify: `web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue`
- Modify: `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue`
- Modify: `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/components/MarketFundFlow.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/components/MarketConcepts.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/components/AnalysisIndicators.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/market-data-tabs/industryAnalysisData.ts`
- Test: `web/frontend/tests/e2e/market-data.spec.ts`
- Test: `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
- Test: `web/frontend/src/views/artdeco-pages/market-data-tabs/__tests__/industryAnalysisData.spec.ts`
- Test: `web/frontend/src/views/artdeco-pages/market-data-tabs/__tests__/FundFlowAnalysis.spec.ts`

**Step 1: 先按 shared component 收口**

对概念、行业、资金流、指标页优先抽共用的表格/图表/筛选块，避免在单页重复修状态逻辑。

**Step 2: 对 pending 接口只做壳层收口**

`Market-LHB`、`Data-Indicator` 等 `pending` 页面，只做：
- loading/error/empty
- token cleanup
- REQ_ID 位
- 阻塞登记

不做字段臆断和假接口拼装。

**Step 3: 批次验证**

Run: `npm --prefix web/frontend run type-check`

Expected: 不高于技术债基线。

Run: `cd web/frontend && npx playwright test --config playwright.config.js --project=chromium tests/e2e/market-data.spec.ts tests/e2e/comprehensive-all-pages.spec.ts`

Expected: 市场数据相关页面可见性通过。

### Task 5: 执行 P1-B 信号与持仓共享组件批次

**Files:**
- Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- Modify: `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue`
- Modify: `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
- Modify: `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/strategySignalsData.ts`
- Review/Modify: `web/frontend/src/views/artdeco-pages/portfolio-tabs/portfolioOverviewData.ts`
- Review/Modify: `web/frontend/src/views/artdeco-pages/trading-tabs/tradingDataTransform.ts`
- Review/Modify: `web/frontend/src/views/artdeco-pages/components/ArtDecoSignalMonitoringOverview.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/components/ArtDecoSignalMonitoringMetrics.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/components/ArtDecoTradingSignalsControls.vue`
- Test: `web/frontend/tests/e2e/strategy-management.spec.ts`
- Test: `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
- Verify: `tests/e2e/trade-management.spec.ts`

**Step 1: 先统一共享模型**

统一以下共享对象的字段映射和状态语义：
- `/api/v1/trade/signals`
- `/api/v1/trade/positions`

避免三个信号页、三个持仓页各自维护不同映射。

**Step 2: 抽离共享块**

能复用的筛选栏、统计卡、信号汇总块、持仓透视块，优先落到 `components/`，不要把跨页逻辑继续堆在 `*-tabs/`。

**Step 3: 批次验证**

Run: `npm --prefix web/frontend run type-check`

Expected: 不高于技术债基线。

Run: `cd web/frontend && npx playwright test --config playwright.config.js --project=chromium tests/e2e/strategy-management.spec.ts tests/e2e/comprehensive-all-pages.spec.ts`

Expected: shared signals/positions 页面可见性通过。

Run: `BASE_URL=http://localhost:3020 npx playwright test tests/e2e/trade-management.spec.ts --config playwright.config.ts --project=chromium`

Expected: 交易管理主链通过或阻塞被记录。

### Task 6: 执行 P1-C 策略主链批次

**Files:**
- Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
- Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestQuickRun.ts`
- Review/Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyParametersData.ts`
- Review/Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/strategyCrossTabNavigation.ts`
- Review/Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestHeader.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestWorkbenchTabs.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue`
- Test: `web/frontend/tests/e2e/strategy-management.spec.ts`
- Test: `web/frontend/tests/e2e/strategy-backtest.spec.ts`

**Step 1: 先保真实接口链路**

因为本批次接口已相对稳定，优先保证列表、参数、回测工作台都使用真实接口，不再回退 mock。

**Step 2: 再做页签块治理**

将回测头部、工作台、KPI 网格等稳定复用区块留在 `components/`，避免回到大单页。

**Step 3: 批次验证**

Run: `npm --prefix web/frontend run type-check`

Expected: 不高于技术债基线。

Run: `cd web/frontend && npx playwright test --config playwright.config.js --project=chromium tests/e2e/strategy-management.spec.ts tests/e2e/strategy-backtest.spec.ts`

Expected: `chromium` 通过策略管理与回测链路。

### Task 7: 执行 P1-D 风控主链批次

**Files:**
- Modify: `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue`
- Modify: `web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue`
- Modify: `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue`
- Modify: `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskMonitor.vue`
- Test: `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
- Verify: `tests/e2e/risk-monitor.spec.ts`

**Step 1: 先统一风险页状态口径**

所有风控页统一：
- 风险摘要
- 告警/止损状态
- 空态/错误态
- REQ_ID 展示位

**Step 2: 区分 verified 与 pending**

`Risk-StopLoss` 可优先收口真实数据；
`Risk-Management`、`Risk-Overview`、`Risk-Alerts` 若字段真值仍未确认，仅做容器和展示一致性，不臆造契约。

**Step 3: 批次验证**

Run: `npm --prefix web/frontend run type-check`

Expected: 不高于技术债基线。

Run: `BASE_URL=http://localhost:3020 npx playwright test tests/e2e/risk-monitor.spec.ts --config playwright.config.ts --project=chromium`

Expected: 风控主链通过或阻塞被明确记录。

Run: `cd web/frontend && npx playwright test --config playwright.config.js --project=chromium tests/e2e/comprehensive-all-pages.spec.ts`

Expected: 风险页面可见性通过。

### Task 8: 执行 P1-E 自选与交易边缘批次

**Files:**
- Modify: `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
- Modify: `web/frontend/src/views/stocks/Screener.vue`
- Modify: `web/frontend/src/views/TradingDashboard.vue`
- Modify: `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/components/AnalysisScreener.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/components/ArtDecoTradingHistoryControls.vue`
- Review/Modify: `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoHistoryView.vue`
- Test: `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
- Verify: `tests/e2e/trade-management.spec.ts`

**Step 1: 先保交易壳层和历史视图**

`Trade-Terminal` 与 `Trade-History` 优先保证流程可达、错误态和空态完整。

**Step 2: 再补自选管理**

`Watchlist-Manage` 可走真实接口；
`Watchlist-Screener` 若 API 仍 `pending`，仅做页面结构、状态和 blocker 登记。

**Step 3: 批次验证**

Run: `npm --prefix web/frontend run type-check`

Expected: 不高于技术债基线。

Run: `cd web/frontend && npx playwright test --config playwright.config.js --project=chromium tests/e2e/comprehensive-all-pages.spec.ts`

Expected: 边缘页面的可见性和导航链路通过。

Run: `BASE_URL=http://localhost:3020 npx playwright test tests/e2e/trade-management.spec.ts --config playwright.config.ts --project=chromium`

Expected: 交易主链无新增回归。

### Task 9: 全量回写与门禁验证

**Files:**
- Modify: `docs/plans/frontend-page-optimization-list.md`
- Modify: `openspec/changes/optimize-artdeco-pages/tasks.md`
- Modify: `TASK-REPORT.md`

**Step 1: 回写清单状态**

按批次更新：
- 页面数据状态
- API 状态
- `last_verified_at`
- 已知阻塞和保留原因

**Step 2: 跑统一门禁**

Run: `npm --prefix web/frontend run type-check`

Expected: 结构性语法错误为 `0`，类型错误不高于基线。

Run: `bash scripts/run_e2e_pm2.sh`

Expected: PM2 环境下的导航门禁通过。

Run: `pm2 list`

Expected: 报告 `mystocks-backend` 与 `mystocks-frontend` 状态。

Run: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3020`

Expected: 返回 `200`。

Run: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8020/health`

Expected: 返回 `200`。

**Step 3: 输出本轮报告**

在 `TASK-REPORT.md` 中必须区分：
- 本次引入问题
- 仓库既有技术债
- `API pending` 阻塞
- 实际执行的命令、浏览器项目、通过/失败/跳过数量
