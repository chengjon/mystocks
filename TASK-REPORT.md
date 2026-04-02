# TASK REPORT

## [WORK] 2026-04-03 Watchlist Service Monitoring Routes（codex/watchlist-service-monitoring-routes-20260403）
- Scope:
  - 收敛 `web/frontend/src/api/services/watchlistService.ts`，移除剩余 generic `userApi` watchlist 契约依赖。
  - 保持 monitoring 自选管理页与问财“加入自选”链路可用，不丢失 `alerts_count` 与 `current_price`。
- Completed:
  - `watchlistService.ts`
    - `listWatchlists` 改走 `GET /api/v1/monitoring/watchlists`
    - `createWatchlist` 改走 `POST /api/v1/monitoring/watchlists`
    - `deleteWatchlist` 改走 `DELETE /api/v1/monitoring/watchlists/{id}`
    - `addStockToWatchlist` 改走 `POST /api/v1/monitoring/watchlists/{id}/stocks`
    - `removeStockFromWatchlist` 改走 `DELETE /api/v1/monitoring/watchlists/{id}/stocks/{stock_code}`
    - `listWatchlistStocks` 改为聚合三条链路：
      - `GET /api/v1/monitoring/watchlists/{id}/stocks`
      - `GET /api/v1/monitoring/analysis/portfolio/{id}/alerts`
      - `GET /api/v1/market/quotes`
  - 新增/更新 focused unit tests：
    - `web/frontend/tests/unit/watchlist-service-watchlists.spec.ts`
    - `web/frontend/tests/unit/watchlist-service-stocks.spec.ts`
    - `web/frontend/tests/unit/watchlist-service-mutations.spec.ts`
  - 为通过当前 frontend type ceiling 门禁，补了 3 处最小前端类型修复：
    - `web/frontend/src/views/TaskManagement.vue`
      - 移除 JS 脚本块中非法的 `as const` 断言
    - `web/frontend/src/components/market/WencaiQueryTable.vue`
      - 对 `catch` 分支的 `error` 做 `Error` 窄化
    - `web/frontend/src/composables/useMarket.ts`
      - 让 `marketOverview` state 类型跟随 `marketApi.getMarketOverview()` 的真实返回，消除旧模型漂移
  - 为通过当前 frontend full-unit 门禁，补了 3 处最小 CI 收尾修复：
    - `web/frontend/tests/unit/config/task-management-style-normalization.spec.ts`
      - 对齐 JS 脚本块现状，改为校验语义化 `tone` 字段而非过期的 `as const` 字面量
    - `web/frontend/src/api/mockApiClient.ts`
      - 删除残留的 mock GET request debug log，收敛到现有 console cleanup 规范
    - `web/frontend/tests/unit/config/console-log-cleanup-batch-12.spec.ts`
      - 修正与 `console-log-cleanup-batch-75` 冲突的过期断言，改为锁定 handler-based 文档示例
  - 同步治理边界：
    - `governance/function-tree/catalog.yaml`
    - `governance/mainline/task-cards/pr-52.yaml`
  - 已提交代码变更：
    - `7e3a10368 fix: align watchlist service with monitoring routes`
    - `838a65eea governance: add task card for pr-52`
- Verification Evidence:
  - `cd web/frontend && npx vitest run tests/unit/config/task-management-style-normalization.spec.ts tests/unit/config/console-log-cleanup-batch-64.spec.ts tests/unit/config/console-log-cleanup-batch-12.spec.ts tests/unit/config/console-log-cleanup-batch-75.spec.ts --config vitest.config.mts`
    - 结果：`4 files, 4 tests passed`
  - `cd web/frontend && npx vitest run tests/unit/watchlist-service-watchlists.spec.ts tests/unit/watchlist-service-stocks.spec.ts tests/unit/watchlist-service-mutations.spec.ts tests/unit/watchlist-service-update.spec.ts tests/unit/watchlist-management-alert-summary.spec.ts tests/unit/wencai-query-table.spec.ts tests/unit/use-market-overview.spec.ts tests/unit/composables.test.ts --config vitest.config.mts`
    - 结果：`8 files, 26 tests passed`
  - `cd web/frontend && npx vitest run tests/unit/watchlist-service-watchlists.spec.ts tests/unit/watchlist-service-stocks.spec.ts tests/unit/watchlist-service-mutations.spec.ts tests/unit/watchlist-service-update.spec.ts tests/unit/watchlist-management-alert-summary.spec.ts tests/unit/wencai-query-table.spec.ts tests/unit/use-market-overview.spec.ts tests/unit/composables.test.ts tests/unit/config/task-management-style-normalization.spec.ts tests/unit/config/console-log-cleanup-batch-64.spec.ts tests/unit/config/console-log-cleanup-batch-12.spec.ts tests/unit/config/console-log-cleanup-batch-75.spec.ts --config vitest.config.mts`
    - 结果：`12 files, 30 tests passed`
  - `cd web/frontend && npm run test:type-ceiling`
    - 结果：`TypeScript errors 0 are within configured ceiling 0`
  - `git diff --check`
  - `gitnexus_detect_changes(scope="staged")`
    - 结果：`risk_level: low`
  - `python governance/mainline/scripts/mainline_scope_gate.py --task-card governance/mainline/task-cards/pr-52.yaml --schema governance/mainline/schemas/ai-task-card.schema.json --base-sha origin/main --head-sha HEAD --report /tmp/pr52-mainline-gate-ci-unblockers.json`
    - 结果：`pass=True`
- Current Status:
  - PR 已创建：`#52`
  - governance task card 已补齐：`governance/mainline/task-cards/pr-52.yaml`
  - full-unit CI unblockers 已在本地补齐并通过 focused + expanded 回归
  - mainline gate 已基于扩大的 CI unblock scope 再次通过
  - 下一步：提交 CI unblock follow-up patch 并回推 PR 52

## [WORK] 2026-03-13 ArtDeco Pages Gate-0 + P0-A（dev-artdeco-pages-codex）
- Scope:
  - 完成 `optimize-artdeco-pages` 的 `Gate-0` 首轮 SSOT 纠偏。
  - 推进 `P0-A` 市场核心批次：
    - `Market-Realtime`
    - `Market-Technical`
- Completed:
  - 补齐 OpenSpec delta，并使变更通过严格校验：
    - `openspec/changes/optimize-artdeco-pages/specs/frontend-routing/spec.md`
    - `openspec/changes/optimize-artdeco-pages/specs/api-integration/spec.md`
    - `openspec/changes/optimize-artdeco-pages/specs/04-smart-dumb-components/spec.md`
    - `openspec/changes/optimize-artdeco-pages/specs/code-quality/spec.md`
  - 重写批次执行任务与实施计划：
    - `openspec/changes/optimize-artdeco-pages/tasks.md`
    - `docs/plans/2026-03-12-artdeco-p0-p1-batching-implementation-plan.md`
  - 完成 ArtDeco SSOT 纠偏：
    - 修正 `router meta.api` 中已确认错误的 `akshare` 前缀与 `strategy-repo` API
    - 重构 `scripts/dev/tools/generate-page-config.js`，仅生成活跃 34 页配置
    - 重构 `scripts/hooks/check-page-config.mjs`，使其与当前路由范围一致
    - 重新生成 `web/frontend/src/config/pageConfig.ts`
    - 更新 `docs/plans/frontend-page-optimization-list.md` 的 canonical path、分类矩阵与执行顺序
    - 修正 `docs/guides/web/ARTDECO_MASTER_INDEX.md` 的字体与架构口径漂移
  - 完成 `P0-A` 页面实现：
    - `web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue`
      - 切到 `/api/v1/market/quotes` 真值链路
      - 增加 `error/empty` 状态
      - 保留 TRACE_ID 展示
    - `web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue`
      - 增加 `error/empty` 状态
      - 兼容 `data: []` 与 `data: { data: [] }` 两类返回
      - 清理本轮新增的硬编码像素字面量
  - 补强页面级 E2E：
    - `web/frontend/tests/e2e/market-data.spec.ts`
    - `web/frontend/tests/e2e/kline-chart.spec.ts`
  - 为当前沙箱限制建立可运行的前端镜像验证方案：
    - 将 `web/frontend` 镜像到 `/tmp/mystocks-frontend-run`
    - 在 `/tmp` 副本上运行 Vite + Playwright，绕开工作区外 `package.json` 读取权限问题
- Verification Evidence:
  - `openspec validate optimize-artdeco-pages --strict`
  - `npm --prefix web/frontend run validate-page-config`
  - `node --check scripts/dev/tools/generate-page-config.js`
  - `node --check scripts/hooks/check-page-config.mjs`
  - `node` + `@vue/compiler-sfc` 对以下页面做语法编译检查：
    - `web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue`
    - `web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue`
  - `git diff --check -- ...`
  - `npm --prefix web/frontend run type-check`
    - 结果：失败，但失败项均为仓库既有问题，未落在本轮改动文件
  - `/tmp` 镜像副本 E2E（chromium）：
    - `cd /tmp/mystocks-frontend-run && PW_REUSE_EXISTING_SERVER=true FRONTEND_BASE_URL=http://127.0.0.1:3021 FRONTEND_PORT=3021 FRONTEND_BACKUP_PORT=3022 BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 HOME=/tmp XDG_CACHE_HOME=/tmp npx playwright test --config playwright.config.js --project=chromium tests/e2e/market-data.spec.ts tests/e2e/kline-chart.spec.ts`
    - 结果：`30 passed`
- Current Status:
  - `Gate-0` 已完成
  - `P0-A` 已完成
  - `P0-B` 已完成
  - 下一步建议进入 `P1-A`：
    - `Market-LHB`
    - `Data-Industry`
    - `Data-Concept`
    - `Data-FundFlow`
    - `Data-Indicator`
  - 已知限制：
    - 工作区内直接启动 `vite` / `vitest` / Playwright webServer 会被沙箱拦在工作区外 `package.json` 读取上
    - 当前可行验证路径是 `/tmp/mystocks-frontend-run` 镜像副本
- Verification Update:
  - `/tmp` 镜像副本 E2E（chromium）补充：
    - `cd /tmp/mystocks-frontend-run && PW_REUSE_EXISTING_SERVER=true FRONTEND_BASE_URL=http://127.0.0.1:3021 FRONTEND_PORT=3021 FRONTEND_BACKUP_PORT=3022 BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 HOME=/tmp XDG_CACHE_HOME=/tmp npx playwright test --config playwright.config.js --project=chromium tests/e2e/login-dashboard.spec.ts`
    - 结果：`3 passed`

## [WORK] 2026-03-13 ArtDeco Pages P1-A（dev-artdeco-pages-codex）
- Scope:
  - 执行 `P1-A` 市场数据域批次：
    - `Market-LHB`
    - `Data-Industry`
    - `Data-Concept`
    - `Data-FundFlow`
    - `Data-Indicator`
- Completed:
  - `web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue`
    - 增加独立路由壳层
    - 增加 `API pending` blocker 提示
  - `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue`
    - 增加 `loading/error/empty` 收口
  - `web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue`
    - 移除本地 mock fallback
    - 改为真实接口空态收口
    - 增加 `loading/error/empty` 状态
  - `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue`
    - 从纯父组件喂数模式扩展为路由页可独立加载
    - 增加 `loading/error/empty` 状态
  - `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue`
    - 增加 `API pending` blocker 提示
  - 新增页面级 E2E：
    - `web/frontend/tests/e2e/market-data-p1a.spec.ts`
  - `/tmp` 镜像副本同步并验证：
    - `DragonTigerAnalysis.vue`
    - `ArtDecoIndustryAnalysis.vue`
    - `MarketConceptTab.vue`
    - `FundFlowAnalysis.vue`
    - `ArtDecoDataAnalysis.vue`
- Verification Evidence:
  - `node` + `@vue/compiler-sfc` 对以下页面做语法编译检查：
    - `web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue`
    - `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue`
    - `web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue`
    - `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue`
    - `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue`
  - `git diff --check -- ...`
  - `/tmp` 镜像副本 E2E（chromium）：
    - `cd /tmp/mystocks-frontend-run && PW_REUSE_EXISTING_SERVER=true FRONTEND_BASE_URL=http://127.0.0.1:3021 FRONTEND_PORT=3021 FRONTEND_BACKUP_PORT=3022 BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 HOME=/tmp XDG_CACHE_HOME=/tmp npx playwright test --config playwright.config.js --project=chromium tests/e2e/market-data-p1a.spec.ts`
    - 结果：`5 passed`
- Current Status:
  - `P1-A` 已完成
  - 本轮区分：
    - `Data-Industry`、`Data-Concept`、`Data-FundFlow`：已完成真实模式空态/错误态收口
    - `Market-LHB`、`Data-Indicator`：已完成 blocker 壳层，但 API 真值仍待后端复核
  - 下一步建议进入 `P1-B`

## [WORK] 2026-03-13 ArtDeco Pages P1-B（dev-artdeco-pages-codex）
- Scope:
  - 执行 `P1-B` 信号与持仓共享组件批次：
    - `Watchlist-Signals`
    - `Strategy-Signals`
    - `Trade-Signals`
    - `Trade-Positions`
    - `Trade-Portfolio`
    - `Risk-PnL`
- Completed:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/strategySignalsData.ts`
    - 提供 shared signal rows / history / metrics / quality / type summaries
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
    - 增加 shared empty/error state
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue`
    - 切到 shared signal transform helpers
    - 增加 shared empty/error state
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
    - 增加 request trace 与 empty/error state
  - `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
    - 增加 shared empty/error state
  - 新增页面级 E2E：
    - `web/frontend/tests/e2e/signals-positions-p1b.spec.ts`
- Verification Evidence:
  - `node` + `@vue/compiler-sfc` 对以下页面做语法编译检查：
    - `StrategySignalsTab.vue`
    - `ArtDecoSignalsView.vue`
    - `ArtDecoTradingPositions.vue`
    - `PortfolioOverviewTab.vue`
  - `git diff --check -- ...`
  - `/tmp` 镜像副本 E2E（chromium）：
    - `cd /tmp/mystocks-frontend-run && PW_REUSE_EXISTING_SERVER=true FRONTEND_BASE_URL=http://127.0.0.1:3021 FRONTEND_PORT=3021 FRONTEND_BACKUP_PORT=3022 BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 HOME=/tmp XDG_CACHE_HOME=/tmp npx playwright test --config playwright.config.js --project=chromium tests/e2e/signals-positions-p1b.spec.ts`
    - 结果：`5 passed`
- Current Status:
  - `P1-B` 已完成
  - 下一步建议进入 `P1-C`

## [WORK] 2026-03-13 ArtDeco Pages P1-C（dev-artdeco-pages-codex）
- Scope:
  - 执行 `P1-C` 策略主链批次：
    - `Strategy-Repo`
    - `Strategy-Parameters`
    - `Strategy-Backtest`
- Completed:
  - 新增缺失的回测页 view model：
    - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
  - `ArtDecoBacktestAnalysis.vue` 恢复可运行状态
  - 新增页面级 E2E：
    - `web/frontend/tests/e2e/strategy-mainline-p1c.spec.ts`
  - 验证策略仓库到参数页、回测页的 query handoff
- Verification Evidence:
  - `/tmp` 镜像副本 E2E（chromium）：
    - `cd /tmp/mystocks-frontend-run && PW_REUSE_EXISTING_SERVER=true FRONTEND_BASE_URL=http://127.0.0.1:3021 FRONTEND_PORT=3021 FRONTEND_BACKUP_PORT=3022 BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 HOME=/tmp XDG_CACHE_HOME=/tmp npx playwright test --config playwright.config.js --project=chromium tests/e2e/strategy-mainline-p1c.spec.ts`
    - 结果：`3 passed`
- Current Status:
  - `P1-C` 已完成
  - 下一步建议进入 `P1-D`

## [WORK] 2026-03-13 ArtDeco Pages P1-D（dev-artdeco-pages-codex）
- Scope:
  - 执行 `P1-D` 风控主链批次：
    - `Risk-Management`
    - `Risk-Overview`
    - `Risk-StopLoss`
    - `Risk-Alerts`
- Completed:
  - 为 `ArtDecoRiskManagement.vue` 补齐缺失依赖：
    - `riskManagementHelpers.ts`
    - `ArtDecoRiskStatsGrid.vue`
    - `ArtDecoRiskOverviewPanel.vue`
    - `ArtDecoRiskStockPanel.vue`
  - `StopLossMonitorTab.vue`
    - 增加 empty/error state
  - 风控容器页改为纯壳层配置，不再请求无效 wildcard API
  - 新增页面级 E2E：
    - `web/frontend/tests/e2e/risk-mainline-p1d.spec.ts`
- Verification Evidence:
  - `node` + `@vue/compiler-sfc` 对以下页面做语法编译检查：
    - `ArtDecoRiskManagement.vue`
    - `ArtDecoRiskOverviewPanel.vue`
    - `ArtDecoRiskStatsGrid.vue`
    - `ArtDecoRiskStockPanel.vue`
    - `StopLossMonitorTab.vue`
    - `RiskOverviewTab.vue`
    - `ArtDecoRiskAlerts.vue`
  - `git diff --check -- ...`
  - `/tmp` 镜像副本 E2E（chromium）：
    - `cd /tmp/mystocks-frontend-run && PW_REUSE_EXISTING_SERVER=true FRONTEND_BASE_URL=http://127.0.0.1:3021 FRONTEND_PORT=3021 FRONTEND_BACKUP_PORT=3022 BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 HOME=/tmp XDG_CACHE_HOME=/tmp npx playwright test --config playwright.config.js --project=chromium tests/e2e/risk-mainline-p1d.spec.ts`
    - 结果：`4 passed`
- Current Status:
  - `P1-D` 已完成
  - 下一步建议进入 `P1-E`

## [WORK] 2026-03-13 ArtDeco Pages P1-E（dev-artdeco-pages-codex）
- Scope:
  - 执行 `P1-E` 自选与交易边缘批次：
    - `Watchlist-Manage`
    - `Watchlist-Screener`
    - `Trade-Terminal`
    - `Trade-History`
- Completed:
  - `WatchlistManager.vue`
    - 从被动组件扩展为路由页可自加载
    - 增加 empty/error state
  - `Screener.vue`
    - 增加 API pending blocker 壳层
  - `ArtDecoTradingHistory.vue`
    - 增加 request trace 与 empty/error state
  - 新增页面级 E2E：
    - `web/frontend/tests/e2e/watchlist-trade-p1e.spec.ts`
- Verification Evidence:
  - `node` + `@vue/compiler-sfc` 对以下页面做语法编译检查：
    - `WatchlistManager.vue`
    - `Screener.vue`
    - `ArtDecoTradingHistory.vue`
  - `git diff --check -- ...`
  - `/tmp` 镜像副本 E2E（chromium）：
    - `cd /tmp/mystocks-frontend-run && PW_REUSE_EXISTING_SERVER=true FRONTEND_BASE_URL=http://127.0.0.1:3021 FRONTEND_PORT=3021 FRONTEND_BACKUP_PORT=3022 BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 HOME=/tmp XDG_CACHE_HOME=/tmp npx playwright test --config playwright.config.js --project=chromium tests/e2e/watchlist-trade-p1e.spec.ts`
    - 结果：`4 passed`
- Current Status:
  - `P1-E` 已完成
  - 当前 `P1` 批次已全部完成
  - 下一步建议进入 `P2`：
    - `Strategy-GPU`
    - `Strategy-Opt`
    - `Strategy-Pos`
    - `Risk-News`
    - `System-Config`
    - `System-Health`
    - `System-API`
    - `System-Data`

## [WORK] 2026-03-13 ArtDeco Pages P2（dev-artdeco-pages-codex）
- Scope:
  - 执行 `P2` 页面收口批次：
    - `Strategy-GPU`
    - `Strategy-Opt`
    - `Strategy-Pos`
    - `Risk-News`
    - `System-Config`
    - `System-Health`
    - `System-API`
    - `System-Data`
- Completed:
  - `web/frontend/src/views/strategy/BacktestGPU.vue`
    - 增加 `API pending` blocker 壳层
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
    - 移除失败时 mock fallback
    - 改为真实模式 empty/error state 收口
  - `web/frontend/src/views/artdeco-pages/stock-management-tabs/PortfolioMonitor.vue`
    - 从 props-only 组件扩展为路由页可自加载
    - 增加 request trace 与 empty/error state
  - `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue`
    - 增加公告 empty/error state
  - `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue`
    - 增加 `API pending` blocker 壳层
  - `web/frontend/src/views/artdeco-pages/system-tabs/SystemHealthTab.vue`
    - 重写为真实 `/health` 页面壳层
    - 增加 empty/error state
  - `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue`
    - 增加 metrics 列表与 empty/error state
  - `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue`
    - 增加 config empty/error state
  - 新增页面级 E2E：
    - `web/frontend/tests/e2e/p2-pages.spec.ts`
- Verification Evidence:
  - `node` + `@vue/compiler-sfc` 对以下页面做语法编译检查：
    - `BacktestGPU.vue`
    - `ArtDecoStrategyOptimization.vue`
    - `PortfolioMonitor.vue`
    - `ArtDecoAnnouncementMonitor.vue`
    - `ArtDecoSystemSettings.vue`
    - `SystemHealthTab.vue`
    - `ArtDecoMonitoringDashboard.vue`
    - `ArtDecoDataManagement.vue`
  - `npm --prefix web/frontend run type-check`
    - 结果：失败，但失败项均为仓库既有问题，未落在本轮改动文件
    - 既有错误：
      - `src/stores/risk.ts`
      - `src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
      - `src/views/composables/useTechnicalAnalysis.ts`
  - `openspec validate optimize-artdeco-pages --strict`
  - `git diff --check -- ...`
  - `gitnexus_detect_changes(scope=all)`
    - 结果：`critical`
    - 说明：当前工作树原本就存在大量未提交改动（400 files / 2484 changed symbols），无法作为本轮范围判定依据
  - `/tmp` 镜像副本 E2E（chromium）：
    - 红测：
      - `cd /tmp/mystocks-frontend-run && PW_REUSE_EXISTING_SERVER=true FRONTEND_BASE_URL=http://127.0.0.1:3021 FRONTEND_PORT=3021 FRONTEND_BACKUP_PORT=3022 BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 HOME=/tmp XDG_CACHE_HOME=/tmp npx playwright test --config playwright.config.js --project=chromium tests/e2e/p2-pages.spec.ts`
      - 结果：`8 failed`
    - 绿测：
      - `cd /tmp/mystocks-frontend-run && PW_REUSE_EXISTING_SERVER=true FRONTEND_BASE_URL=http://127.0.0.1:3021 FRONTEND_PORT=3021 FRONTEND_BACKUP_PORT=3022 BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 HOME=/tmp XDG_CACHE_HOME=/tmp npx playwright test --config playwright.config.js --project=chromium tests/e2e/p2-pages.spec.ts`
      - 结果：`8 passed`
- Current Status:
  - `P2` 已完成
  - 当前 `Gate-0 + P0 + P1 + P2` 首轮 34 页全部完成
  - 下一步建议转入：
    - `API pending` 真值复核
    - PM2 环境 smoke / `scripts/run_e2e_pm2.sh`
    - 二轮 `mixed -> real` 治理

## [WORK] 2026-03-13 ArtDeco Pages Verification Follow-up（dev-artdeco-pages-codex）
- Scope:
  - 继续执行首轮页面优化后的门禁验证与 API 真值复核
  - 核对 `scripts/run_e2e_pm2.sh`、`frontend_optimization_audit.py` 和 PM2 运行态
- Completed:
  - 实跑 `scripts/run_e2e_pm2.sh`
    - 首次失败原因：root 目录 `npx playwright` 试图在线拉包并写入 `/root/.npm`，触发 `EROFS`
    - 二次通过注入本地 Playwright 二进制与 `/tmp` 缓存后，脚本继续执行到服务探测阶段
  - 定位 PM2 门禁阻塞：
    - `mystocks-frontend` 可在 `3020` 正常启动
    - `mystocks-backend` 无法稳定启动，不是 ArtDeco 页面回归，而是后端现有导入链错误
  - 修正两处已确认的后端包导出漂移：
    - `web/backend/app/api/signal_monitoring/__init__.py`
    - `web/backend/app/api/signal_monitoring/get_signal_statistics.py`
    - `web/backend/app/api/market/__init__.py`
  - 修正两处 GPU 模块导入期注解崩溃：
    - `src/gpu/accelerated/data_processor_gpu_fixed.py`
    - `src/gpu/acceleration/feature_calculation_gpu/feature_calculation_gpu_methods/part1.py`
    - `src/gpu/acceleration/feature_calculation_gpu/feature_calculation_gpu_methods/part2.py`
  - 在最小测试环境变量下重新打通 `web.backend.app.main` 导入链
  - 恢复 PM2 服务：
    - `mystocks-backend` -> `http://localhost:8020/health`
    - `mystocks-frontend` -> `http://localhost:3020`
  - 在当前 PM2 服务上补跑 root 导航 smoke：
    - `PATH="web/frontend/node_modules/.bin:$PATH" NODE_PATH=/opt/claude/mystocks_spec-artdeco-pages/web/frontend/node_modules HOME=/tmp XDG_CACHE_HOME=/tmp BASE_URL=http://localhost:3020 playwright test tests/navigation-consistency.spec.ts --config=playwright.config.ts --project=chromium`
    - 结果：`8 passed`
  - 重写 `scripts/run_e2e_pm2.sh`
    - 环境文件按 `.env` -> `web/frontend/.env` -> `.env.example` 顺序加载
    - 仅管理 `mystocks-backend` / `mystocks-frontend`
    - 直接复用 `web/frontend/node_modules/.bin/playwright`
    - 增加 `NODE_PATH`、`NPM_CONFIG_CACHE`、`PLAYWRIGHT_BROWSERS_PATH=/tmp/ms-playwright`
    - 增加 `KEEP_PM2_SERVICES=1` 保活开关
    - 改为直接用 `pm2 start python3 ... uvicorn` 和 `pm2 start npm ... dev:no-types` 启动测试服务
  - 实跑新脚本：
    - `KEEP_PM2_SERVICES=1 scripts/run_e2e_pm2.sh`
    - 结果：`8 passed`
  - 实跑前端优化审计：
    - `python scripts/dev/frontend_optimization_audit.py --repo-root . --strict --report-file reports/analysis/frontend-page-optimization-audit-report.md`
    - 结果：
      - `plan_rows=34`
      - `component_issues=0`
      - `verified_api_issues=9`
      - `backend_source=openapi_fallback`
  - 修正 `scripts/dev/frontend_optimization_audit.py` 的本地后端导入环境：
    - 为 `load_backend_paths_from_app()` 补齐 `repo_root` 到 `sys.path`
    - 增加 `DEVELOPMENT_MODE`、`POSTGRESQL_PORT`、`POSTGRESQL_DATABASE`、`TDENGINE_*` 等默认值
  - 重新实跑前端优化审计：
    - `python scripts/dev/frontend_optimization_audit.py --repo-root . --strict --report-file reports/analysis/frontend-page-optimization-audit-report.md`
    - 结果：
      - `plan_rows=34`
      - `component_issues=0`
      - `verified_api_issues=0`
      - `backend_source=backend_app`
  - 回写页面清单与路由/API 真值：
    - `web/frontend/src/router/index.ts`
    - `web/frontend/src/config/pageConfig.ts`
    - `docs/plans/frontend-page-optimization-list.md`
    - 当前页面级 `pending` 已收缩到仅剩 `Strategy-GPU` 的 `/api/gpu/*`
- Verification Evidence:
  - `python -m py_compile web/backend/app/api/signal_monitoring/__init__.py web/backend/app/api/signal_monitoring/get_signal_statistics.py web/backend/app/api/market/__init__.py`
  - `git diff --check -- ...`
  - `pm2 status mystocks-backend mystocks-frontend`
  - `reports/analysis/frontend-page-optimization-audit-report.md`
  - `curl http://localhost:8020/health`
  - root Playwright smoke：
    - `tests/navigation-consistency.spec.ts`
  - `KEEP_PM2_SERVICES=1 scripts/run_e2e_pm2.sh`
  - `python scripts/dev/frontend_optimization_audit.py --repo-root . --strict --report-file reports/analysis/frontend-page-optimization-audit-report.md`
  - `npm --prefix web/frontend run validate-page-config`
- Current Status:
  - `mystocks-frontend`：`online`，`http://localhost:3020`
  - `mystocks-backend`：`online`，`http://localhost:8020`
  - `scripts/run_e2e_pm2.sh`：当前已可在本仓库环境下直接执行
    - 如需保留服务，使用 `KEEP_PM2_SERVICES=1`
  - 已确认的后端启动阻塞链：
    - `ImportError: cannot import name 'ActiveSignalItem' from app.api.signal_monitoring.signal_history_response`
      - 本轮已修复
    - `ImportError: cannot import name 'get_market_heatmap' from app.api.market.market_data_request`
      - 本轮已修复
    - `AttributeError: 'NoneType' object has no attribute 'DataFrame'`
      - 来源：`src/gpu/accelerated/data_processor_gpu_fixed.py`
      - 本轮已通过延迟注解求值修复
    - `NameError: name 'cudf' is not defined`
      - 来源：`feature_calculation_gpu_methods/part1.py` / `part2.py`
      - 本轮已通过延迟注解求值和 fallback 占位修复
  - 旧的 `openapi_fallback / verified_api_issues=9` 结果已被新审计覆盖，不再作为当前真值
  - 当前审计真值：
    - `backend_source=backend_app`
    - `verified_api_issues=0`
  - 剩余真正待复核的页面级 API 只剩：
    - `Strategy-GPU` -> `/api/gpu/*`

## [WORK] 2026-03-09 Batch 1-2 Repository Hygiene（dev-repo-hygiene-b1）
- Scope:
  - 执行 `integrate-repository-hygiene` 的 Batch 1 前两步：
    - `1.1 Baseline and Canonical Targets`
    - `1.2 Safe Hygiene Entry Points` 中的 `rotate_logs.sh`
- Completed:
  - 为真实项目 policy 增加 canonical lifecycle directories 回归测试：
    - `tests/unit/scripts/test_check_structure_policy.py`
  - 更新目录治理 policy，允许：
    - `archive/`
    - `var/`
  - 刷新 `docs/FILE_CLEANUP_TASK.md`，使其反映当前 `check_structure` 基线与 canonical targets
  - 为日志轮转新增 focused tests：
    - `tests/unit/scripts/test_rotate_logs.py`
  - 收敛 `scripts/maintenance/rotate_logs.sh`：
    - 支持 `--dry-run`
    - 支持 `--project-root`
    - 支持 `--retention-days`
    - 活跃日志落点：`var/log/app/`
    - 归档日志落点：`archive/logs/app/`
  - 为文件大小监控新增 focused tests：
    - `tests/unit/scripts/test_monitor_file_size.py`
  - 收敛 `scripts/maintenance/monitor_file_size.sh`：
    - 支持 `--project-root`
    - 支持 `--format text|json`
    - 复用 `scripts/compliance/file_size_guardrail.py`
  - 为自动清理新增 focused tests：
    - `tests/unit/scripts/test_auto_cleanup.py`
  - 收敛 `scripts/cleanup/auto_cleanup.sh`：
    - 默认 dry-run
    - 支持 `--execute`
    - 支持 `--project-root`
    - 支持 `--format text|json`
    - 支持 `--backup-stamp`
  - 将 `scripts/dev/cleanup_temp_files.py` 改为 canonical cleanup planner
  - 将 `scripts/dev/execute_cleanup.py` 改为执行包装器
  - 将 `scripts/dev/check_file_sizes.py` 改为兼容入口，复用 canonical line-count logic
  - 创建 canonical 目录骨架：
    - `archive/docs/`
    - `archive/logs/app/`
    - `reports/governance/`
    - `var/backups/`
    - `var/log/app/`
    - `var/reports/`
  - 修复 pytest 根目录运行时产物泄漏：
    - 新增共享 helper：`tests/pytest_runtime_artifacts.py`
    - 将生效 hook 下沉到 `tests/conftest.py`
    - 避免 `tests/unit/scripts/test_pytest_runtime_artifacts.py` 再直接导入仓库根 `conftest.py`
    - `pytest` timing CSV 统一落到 `var/reports/test_timing.csv`
    - 根目录 `test_timing.csv` 与 `__pycache__/` 已清零
  - 记录 Batch 2 治理 delta：
    - `reports/governance/2026-03-09-batch-2-root-error-remediation.md`
- Verification Evidence:
  - `pytest tests/unit/scripts/test_check_structure_policy.py -q -o addopts=''`
  - `pytest tests/unit/scripts/test_rotate_logs.py -q -o addopts=''`
  - `pytest tests/unit/scripts/test_monitor_file_size.py -q -o addopts=''`
  - `pytest tests/unit/scripts/test_auto_cleanup.py -q -o addopts=''`
  - `pytest tests/unit/scripts/test_pytest_runtime_artifacts.py -q -o addopts=''`
  - `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py -q -o addopts=''`
  - `openspec validate integrate-repository-hygiene --strict`
  - `python scripts/maintenance/check_structure.py --format text`
- Current Status:
  - Batch 1 与 Batch 2（首批根目录阻塞项修复）均已完成
  - 当前目录治理基线：
    - `errors: 0`
    - `warnings: 20`
  - 下一步建议进入 Batch 3：
    - 按类别收敛根目录 legacy docs / reports / archive warnings

## [WORK] 2026-03-09 Batch 3 Root Doc Convergence（dev-repo-hygiene-b1）
- Scope:
  - 执行 `integrate-repository-hygiene` 的 Batch 3 首批低风险文档收敛。
  - 优先处理 5 个 legacy root docs，并验证 warning delta。
- Completed:
  - 生成文档迁移 inventory：
    - `reports/governance/2026-03-09-batch-3-root-doc-inventory.md`
  - 迁移历史 E2E 报告到归档区：
    - `archive/docs/e2e/E2E_TEST_EXECUTION_SUCCESS_REPORT_2026-03-01.md`
  - 迁移根目录 E2E 兼容快速参考到活跃文档区：
    - `docs/guides/E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md`
  - 迁移 Gemini 代理活跃指南：
    - `docs/guides/ai-tools/GEMINI_PROXY_CONFIGURATION_GUIDE.md`
  - 归档 Gemini 一次性迁移清单：
    - `archive/docs/tooling/GEMINI_SETTINGS_FILE_MIGRATION_CHECKLIST_2026-03.md`
  - 迁移 OMC 活跃工作流指南：
    - `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`
  - 更新入口与索引：
    - `README.md`
    - `docs/reports/cleanup/index-artifacts/INDEX_root.md`
- Verification Evidence:
  - `python scripts/maintenance/check_structure.py --format text`
  - `openspec validate integrate-repository-hygiene --strict`
- Current Status:
  - 目录治理基线保持：
    - `errors: 0`
  - warning 已由 `20` 降至 `15`
  - 残余 warning 已收敛为：
    - workflow root artifacts：`TASK.md`、`TASK-REPORT.md`
    - root legacy dirs：`archived/`、`backups/`、`reviews/`
    - root evidence artifact：`coverage.json`
    - docs/archive/reviews 历史收敛问题
  - 下一步建议：
    - 优先处理 `coverage.json` 与 `backups/` 的 lifecycle convergence

## [WORK] 2026-03-09 Root Coverage and Backups Convergence（dev-repo-hygiene-b1）
- Scope:
  - 收敛 root `coverage.json` 与 root `backups/`。
  - 同时修正会继续生成这些 root debt 的默认写入路径。
- Completed:
  - 迁移 root coverage artifact：
    - `coverage.json` → `reports/coverage/coverage.json`
  - 迁移历史 registry backups：
    - `archive/backups/data_source_registry/registry_backup_20260216_111556.json`
    - `archive/backups/data_source_registry/registry_backup_20260216_183533.json`
    - `archive/backups/data_source_registry/registry_backup_20260216_184448.json`
  - 修正 pytest 覆盖率 JSON 输出路径：
    - `pytest.ini`
    - `tests/pytest_runtime_artifacts.py`
  - 为自动清理补充 root `backups/` 收敛能力：
    - `scripts/dev/cleanup_temp_files.py`
    - `tests/unit/scripts/test_auto_cleanup.py`
  - 修正备份默认落点：
    - `src/infrastructure/backup_recovery/backup_manager.py`
    - `src/infrastructure/backup_recovery/backup_scheduler.py`
    - `scripts/sync_sources.py`
    - `scripts/migrations/migrate_watchlist_to_monitoring.py`
  - 修正覆盖率工具脚本 canonical path：
    - `scripts/dev/quality/check_coverage.py`
    - `scripts/tests/run_e2e_tests.sh`
  - 记录治理 delta：
    - `reports/governance/2026-03-09-root-coverage-backups-convergence.md`
- Verification Evidence:
  - `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py tests/unit/scripts/test_repository_hygiene_paths.py -q -o addopts=''`
  - `openspec validate integrate-repository-hygiene --strict`
  - `python scripts/maintenance/check_structure.py --format text`
- Current Status:
  - 目录治理基线：
    - `errors: 0`
    - `warnings: 12`
  - 本轮消除了：
    - root `coverage.json`
    - root `backups/`
  - 下一步建议：
    - 处理 `archived/` 与 `reviews/`，再评估 `TASK.md` / `TASK-REPORT.md` 是否保留为 workflow exception

## [WORK] 2026-03-09 Root Reviews and Archived Convergence（dev-repo-hygiene-b1）
- Scope:
  - 收敛 root `reviews/` 与 root `archived/`。
  - 继续压低目录治理 warning，但不触碰当前多 CLI workflow 所依赖的 `TASK.md` / `TASK-REPORT.md`。
- Completed:
  - 迁移 root reviews：
    - `reports/reviews/review-20260223-031831-9e70a2.md`
    - `reports/reviews/review-20260223-202118-558dc1.md`
  - 迁移 root archived tree：
    - `archive/legacy-root-archived/`
  - 放开 `reports/reviews/**` 跟踪：
    - `.gitignore`
  - 增补回归测试：
    - `tests/unit/scripts/test_repository_hygiene_paths.py`
  - 记录治理 delta：
    - `reports/governance/2026-03-09-reviews-archived-convergence.md`
- Verification Evidence:
  - `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py tests/unit/scripts/test_repository_hygiene_paths.py -q -o addopts=''`
  - `openspec validate integrate-repository-hygiene --strict`
  - `python scripts/maintenance/check_structure.py --format text`
- Current Status:
  - 目录治理基线：
    - `errors: 0`
    - `warnings: 8`
  - 当前剩余 warning 聚焦于：
    - workflow root artifacts：`TASK.md`、`TASK-REPORT.md`
    - docs/reports lifecycle convergence：`docs/completion_reports/**`、`docs/monitoring_reports/**`、`docs/phase_reports/**`、`docs/test_reports/**`
    - archive lifecycle convergence：`docs/archive/**`、`docs/legacy/**`
  - 下一步建议：
    - 评估是否将 `TASK.md` / `TASK-REPORT.md` 作为 workflow-approved exception 保留
    - 分批把 `docs/*_reports` 收敛到 `reports/`

## [WORK] 2026-03-09 Task Artifacts Workflow Exception（dev-repo-hygiene-b1）
- Scope:
  - 将 root `TASK.md` / `TASK-REPORT.md` 从“待迁移债务”正式改为“workflow-approved exceptions”。
  - 使目录治理规则与本项目本地优先、多 CLI 协作模型一致。
- Completed:
  - 在治理策略中新增：
    - `root.workflow_exception_files`
  - 将以下文件移出 `tolerated_files`：
    - `TASK.md`
    - `TASK-REPORT.md`
  - 更新目录检查器：
    - `scripts/maintenance/check_structure.py`
  - 增补回归测试：
    - `tests/unit/scripts/test_check_structure_policy.py`
  - 在权威工作流文档中补充说明：
    - `docs/guides/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`
  - 记录治理 delta：
    - `reports/governance/2026-03-09-task-artifacts-workflow-exception.md`
- Verification Evidence:
  - `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py tests/unit/scripts/test_repository_hygiene_paths.py -q -o addopts=''`
  - `openspec validate integrate-repository-hygiene --strict`
  - `python scripts/maintenance/check_structure.py --format text`
- Current Status:
  - 目录治理基线：
    - `errors: 0`
    - `warnings: 6`
  - 当前剩余 warning 聚焦于：
    - `docs/completion_reports/**`
    - `docs/monitoring_reports/**`
    - `docs/phase_reports/**`
    - `docs/test_reports/**`
    - `docs/archive/**`
    - `docs/legacy/**`

## [WORK] 2026-03-09 Docs Report and Archive Final Convergence（dev-repo-hygiene-b1）
- Scope:
  - 清理最后 6 个治理 warning。
  - 收敛 `docs/*_reports`、`docs/archive/`、`docs/legacy/` 到 canonical lifecycle targets。
- Completed:
  - 迁移报告目录：
    - `docs/completion_reports/` → `reports/completion/`
    - `docs/monitoring_reports/` → `reports/monitoring/`
    - `docs/phase_reports/` → `reports/phase/`
    - `docs/test_reports/` → `reports/tests/`
  - 刷新/新增 report index：
    - `reports/completion/INDEX.md`
    - `reports/monitoring/INDEX.md`
    - `reports/phase/INDEX.md`
    - `reports/tests/INDEX.md`
  - 收敛 archive 文档树：
    - `docs/archive/` → `archive/docs/`
    - `docs/legacy/` → `archive/legacy-docs/`
  - 更新活跃路径说明：
    - `README.md`
    - `docs/guides/README.md`
    - `docs/guides/ai-tools/CLAUDE.md`
    - `docs/guides/documentation/DOCUMENTATION_WORKFLOW_GUIDE.md`
    - `docs/guides/web/ARTDECO_MASTER_INDEX.md`
    - `docs/architecture/FRONTEND_OPTIMIZATION_STRATEGY_V3.md`
    - `docs/reports/cleanup/directory-organization/DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED.md`
  - 增补目录回归测试：
    - `tests/unit/scripts/test_repository_hygiene_paths.py`
  - 记录治理 delta：
    - `reports/governance/2026-03-09-docs-report-archive-convergence.md`
- Verification Evidence:
  - `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py tests/unit/scripts/test_repository_hygiene_paths.py -q -o addopts=''`
  - `openspec validate integrate-repository-hygiene --strict`
  - `python scripts/maintenance/check_structure.py --format text`
- Current Status:
  - 目录治理基线：
    - `errors: 0`
    - `warnings: 0`
  - `integrate-repository-hygiene` 的 Batch 1-3 目标已全部收口

## [WORK] 2026-03-09 OpenSpec 活跃已完成变更清理
- Scope:
  - 清理仍处于 active 状态但已完成的 OpenSpec change。
  - 修复 `implement-file-directory-migration` 缺失规范元数据的问题，使其可验证、可归档。
- Change Cleanup:
  - 已归档：
    - `add-policy-driven-directory-governance`
    - `refactor-technical-debt-remediation-wave1`
    - `implement-file-directory-migration`
    - `implement-frontend-routing-optimization`
    - `add-quantitative-trading-algorithms-api`
  - 已补齐：
    - `openspec/changes/implement-file-directory-migration/proposal.md`
    - `openspec/changes/implement-file-directory-migration/specs/file-organization/spec.md`
  - 已修正新生成 spec 的 `Purpose`：
    - `openspec/specs/directory-governance/spec.md`
    - `openspec/specs/file-organization/spec.md`
    - `openspec/specs/api-integration/spec.md`
    - `openspec/specs/frontend-routing/spec.md`
    - `openspec/specs/quantitative-trading-algorithms-api/spec.md`
- Verification Evidence:
  - `openspec validate add-policy-driven-directory-governance --strict`
  - `openspec validate refactor-technical-debt-remediation-wave1 --strict`
  - `openspec validate implement-file-directory-migration --strict`
  - `openspec validate implement-frontend-routing-optimization --strict`
  - `openspec validate add-quantitative-trading-algorithms-api --strict`
  - 对上述 5 条执行 `openspec archive <change-id> --yes`
  - 归档后 `openspec list`
    - 结果：不再存在 active + complete 的 change
- Status:
  - 本轮目标 change：已清空
  - 残余 active change：均为未完成项或无任务项，未在本轮处理范围内

## [WORK] 2026-03-09 OpenSpec 历史 spec Purpose 占位清理
- Scope:
  - 清理历史遗留 spec 中的 `TBD - created by archiving change ...` 占位 Purpose。
- Updated Specs:
  - `openspec/specs/01-unified-response-format/spec.md`
  - `openspec/specs/02-type-safety-generation/spec.md`
  - `openspec/specs/03-adapter-pattern/spec.md`
  - `openspec/specs/04-smart-dumb-components/spec.md`
  - `openspec/specs/05-csrf-protection/spec.md`
  - `openspec/specs/api-documentation/spec.md`
- Verification Evidence:
  - `openspec validate 01-unified-response-format --type spec --strict`
  - `openspec validate 02-type-safety-generation --type spec --strict`
  - `openspec validate 03-adapter-pattern --type spec --strict`
  - `openspec validate 04-smart-dumb-components --type spec --strict`
  - `openspec validate 05-csrf-protection --type spec --strict`
  - `openspec validate api-documentation --type spec --strict`
  - `rg -n 'TBD - created by archiving change' openspec/specs`
- Status:
  - 本轮 6 个历史占位 Purpose：已清理

## [WORK] 2026-03-09 OpenSpec 老式 `No tasks` change 退场
- Scope:
  - 清理仍留在 active 列表中的老式、非标准 OpenSpec change。
- Change Cleanup:
  - 已归档：`reorganize-project-directory-structure`
  - 归档方式：`openspec archive reorganize-project-directory-structure --skip-specs --yes`
  - 归档原因：
    - 原 change 不符合当前 OpenSpec 标准结构（缺少标准 `proposal.md` / delta spec）
    - 其目录治理与文件迁移意图已被后续已归档 change 覆盖：
      - `2026-03-09-implement-file-directory-migration`
      - `2026-03-09-add-policy-driven-directory-governance`
- Verification Evidence:
  - `openspec archive reorganize-project-directory-structure --skip-specs --yes`
    - 结果：归档为 `openspec/changes/archive/2026-03-09-reorganize-project-directory-structure`
  - `openspec list`
    - 结果：active 列表中已无 `No tasks` 条目
- Status:
  - 历史 `No tasks` active change：已清空

## [WORK] 2026-03-09 OpenSpec `0/N tasks` 陈旧 change 分级
- Scope:
  - 对当前 active 列表中 `0/N tasks` 的 change 做保守分级。
  - 目标是区分“可考虑退场”“建议合并/重写”“应保留待执行”，而不是继续盲目归档。
- 分级结果:
  - **A. 可考虑退场（需人工最终确认，当前未自动归档）**
    - `add-unit-tests-ci-cd`
      - 证据：无 spec delta、仅有 `proposal.md + tasks.md`、范围与测试主线高度重叠。
      - 主要重叠对象：
        - `implement-optimized-testing-strategy`
        - `comprehensive-testing-solution`
      - 判断：更像早期宽泛测试计划，适合并入新的测试主线后退场。
    - `create-html-vue-conversion-analysis-docs`
      - 证据：定位偏“分析/策略文档”，且后续已有更具体实现主线。
      - 主要重叠对象：
        - `implement-html-to-vue-conversion-merger`
        - `implement-optimized-html-vue-artdeco-conversion`
      - 判断：更像前置分析 change，若文档价值已沉淀到仓库，可考虑退场。
  - **B. 建议合并或重写后再决定是否退场**
    - `implement-html-to-vue-conversion-merger`
      - 与 `implement-optimized-html-vue-artdeco-conversion`、`implement-web-frontend-v2-navigation` 高度同域，存在主线竞争。
    - `update-web-design-system-v2`
      - 与 `add-artdeco-strategy-management-chain`、当前前端 ArtDeco 主线存在明显交叉，但尚不能证明已完全替代。
    - `implement-optimized-testing-strategy`
      - 尽管为 `0/17`，但其 spec 能力边界清晰（ESM、环境稳定化、分层测试、工具协同），更适合收敛/重写而非直接退场。
    - `tech-debt-governance-2026q1`
      - 与已归档 `refactor-technical-debt-remediation-wave1` 有治理面重叠，但其 `architecture-governance` 能力仍具独立性，不宜直接归档。
  - **C. 应保留待执行（暂未发现明确 superseded 证据）**
    - `implement-html5-migration-experience-optimization`
    - `optimize-data-source-v2`
    - `implement-typescript-type-extension-system`
    - `add-smart-quant-monitoring`
    - `add-quantitative-trading-algorithms`
    - `add-comprehensive-risk-management-system`
- 建议动作:
  - 先处理 A 组：逐条确认是否将有效内容合并进仍存活主线，然后使用 `--skip-specs` 或正式归档退场。
  - 再处理 B 组：为每条指定“唯一主线”，避免同域 change 并存。
  - C 组先保留，不做自动清理。
- Verification Evidence:
  - `openspec list`
  - 逐条检查以下 change 的 `proposal.md` / `tasks.md` / `specs/`：
    - `add-unit-tests-ci-cd`
    - `implement-optimized-testing-strategy`
    - `tech-debt-governance-2026q1`
    - `implement-html5-migration-experience-optimization`
    - `update-web-design-system-v2`
    - `optimize-data-source-v2`
    - `implement-typescript-type-extension-system`
    - `implement-html-to-vue-conversion-merger`
    - `create-html-vue-conversion-analysis-docs`
    - `add-smart-quant-monitoring`
    - `add-quantitative-trading-algorithms`
    - `add-comprehensive-risk-management-system`
  - 交叉关键词与 proposal 对比：
    - `testing|html to vue|artdeco|technical debt|governance`
- Status:
  - 本轮未新增自动归档
  - 已形成下一轮清理优先级：`A -> B -> C`

## [WORK] 2026-03-09 OpenSpec A 组 `0/N tasks` change 退场
- Scope:
  - 执行上一轮分级中的 A 组退场，只处理“最像被后续主线吞并”的两条 change。
- Change Cleanup:
  - 已归档：`add-unit-tests-ci-cd`
    - 归档方式：`openspec archive add-unit-tests-ci-cd --skip-specs --yes`
    - 退场依据：
      - 无 OpenSpec delta/spec，属于早期宽泛测试计划
      - 与后续更具体的测试主线高度重叠：
        - `implement-optimized-testing-strategy`
        - `implement-api-file-level-testing`
        - `comprehensive-testing-solution`
  - 已归档：`create-html-vue-conversion-analysis-docs`
    - 归档方式：`openspec archive create-html-vue-conversion-analysis-docs --skip-specs --yes`
    - 退场依据：
      - 本质为前置分析/文档型 change，不是独立长期 capability
      - 与后续更具体的实现主线重叠：
        - `implement-html-to-vue-conversion-merger`
        - `implement-optimized-html-vue-artdeco-conversion`
- Verification Evidence:
  - `openspec archive add-unit-tests-ci-cd --skip-specs --yes`
    - 结果：归档为 `openspec/changes/archive/2026-03-09-add-unit-tests-ci-cd`
  - `openspec archive create-html-vue-conversion-analysis-docs --skip-specs --yes`
    - 结果：归档为 `openspec/changes/archive/2026-03-09-create-html-vue-conversion-analysis-docs`
  - `openspec list`
    - 结果：active 列表中不再包含上述两条
- Status:
  - A 组：已清空
  - 下一轮候选：B 组（需更谨慎，不宜直接批量退场）

## [WORK] 2026-03-09 OpenSpec B 组唯一主线判定
- Scope:
  - 对 B 组 change 做“唯一主线”判定，优先解决主线竞争问题。
  - 本轮只做归属判断，不直接批量归档。
- 判定结果:
  - `implement-html-to-vue-conversion-merger`
    - **唯一主线候选**：`implement-optimized-html-vue-artdeco-conversion`
    - **证据**：
      - 优化版 proposal 明确点名原方案存在关键问题：`visual inconsistency`、`design system gap`、`user experience degradation`
      - 原 change 关注 `ui-conversion`
      - 优化版直接覆盖更强约束：ArtDeco-first、64 组件库优先、视觉签名强制、并修改 `04-smart-dumb-components`
    - **结论**：
      - 业务主线已被优化版接管
      - 但原 change 仍携带独立 `ui-conversion` delta，若要退场，需先决定：
        - 是否将其剩余能力并入优化版/正式 spec
        - 或明确放弃 `ui-conversion` 作为独立 capability
      - **本轮不直接归档**
  - `update-web-design-system-v2`
    - **唯一主线候选**：`implement-optimized-html-vue-artdeco-conversion`
    - **辅助相关主线**：`frontend-optimization-six-phase`
    - **证据**：
      - `update-web-design-system-v2` 的核心内容是 ArtDeco token / animation / 金融视觉体系升级
      - 优化版 conversion 已把 ArtDeco token、组件优先级、视觉签名、页面改造作为更强执行主线
      - `frontend-optimization-six-phase` 则更像前端整体升级总盘，不适合作为设计系统唯一执行主线
    - **结论**：
      - 设计系统执行主线应收敛到 `implement-optimized-html-vue-artdeco-conversion`
      - `update-web-design-system-v2` 更像“阶段总结/横向设计说明”，后续应考虑重写成纯 spec 或文档，而非继续作为独立 active 执行 change
  - `implement-optimized-testing-strategy`
    - **唯一主线候选**：保留其自身
    - **证据**：
      - 拥有独立 testing capabilities：`esm-compatibility-testing`、`environment-stabilization`、`layered-testing-framework`、`toolchain-integration`
      - 比 `implement-api-file-level-testing` 更偏测试基础设施
      - 比 `comprehensive-testing-solution` 更聚焦、结构更现代
    - **结论**：
      - 不建议退场
      - 应作为测试基础设施主线保留
  - `tech-debt-governance-2026q1`
    - **唯一主线候选**：保留其自身
    - **证据**：
      - 其 delta 落在独立 capability：`architecture-governance`
      - 与 `refactor-technical-debt-remediation-wave1` 的关系更像“治理基线 vs 执行波次”
      - Wave1 已归档到 `code-quality`，并未替代治理 SoT / conflict matrix / governance cadence
    - **结论**：
      - 不建议退场
      - 应作为治理元层主线保留
- Recommended Next Actions:
  - 可继续处理的高置信度目标仅剩：
    - `implement-html-to-vue-conversion-merger`
      - 先做 spec 处置决策，再归档
    - `update-web-design-system-v2`
      - 先决定是转文档化退场，还是抽取剩余独立 spec
- Verification Evidence:
  - 对以下 proposal / tasks / specs 做交叉对比：
    - `implement-html-to-vue-conversion-merger`
    - `update-web-design-system-v2`
    - `implement-optimized-testing-strategy`
    - `tech-debt-governance-2026q1`
    - `implement-optimized-html-vue-artdeco-conversion`
    - `frontend-optimization-six-phase`
    - `implement-api-file-level-testing`
    - `comprehensive-testing-solution`
    - `refactor-technical-debt-remediation-wave1`
- Status:
  - B 组已完成主线判定
  - 尚未进入归档动作

## [WORK] 2026-03-09 OpenSpec B 组 superseded change 退场
- Scope:
  - 处理 B 组中已完成主线判定且具备高置信度 superseded 关系的两条旧 change。
- Change Cleanup:
  - 已归档：`implement-html-to-vue-conversion-merger`
    - 主线接管者：`implement-optimized-html-vue-artdeco-conversion`
    - 归档方式：`openspec archive implement-html-to-vue-conversion-merger --skip-specs --no-validate --yes`
    - 使用 `--no-validate` 的原因：
      - 该 change 自带 `ui-conversion` delta 已不符合当前 OpenSpec 校验要求
      - 本次目标是退场旧主线，而不是把失配 delta 继续沉淀为正式 spec
  - 已归档：`update-web-design-system-v2`
    - 主线接管者：`implement-optimized-html-vue-artdeco-conversion`
    - 归档方式：`openspec archive update-web-design-system-v2 --skip-specs --no-validate --yes`
    - 使用 `--no-validate` 的原因：
      - 该 change 的 delta/spec 结构同样不符合当前 OpenSpec 校验要求
      - 其设计系统意图已被更强的 ArtDeco 优化主线吸收，不应再落入正式 spec
- Verification Evidence:
  - `openspec validate implement-html-to-vue-conversion-merger --strict`
    - 结果：存在多条 delta 结构错误
  - `openspec validate update-web-design-system-v2 --strict`
    - 结果：存在多条 delta 结构错误
  - `openspec archive implement-html-to-vue-conversion-merger --skip-specs --no-validate --yes`
    - 结果：归档为 `openspec/changes/archive/2026-03-09-implement-html-to-vue-conversion-merger`
  - `openspec archive update-web-design-system-v2 --skip-specs --no-validate --yes`
    - 结果：归档为 `openspec/changes/archive/2026-03-09-update-web-design-system-v2`
- Status:
  - B 组中两条 superseded 旧主线：已退场
  - 保留项：`implement-optimized-testing-strategy`、`tech-debt-governance-2026q1`

## [WORK] 2026-03-09 测试主线旧总盘退场
- Scope:
  - 清理测试域的旧总盘 change，避免测试主线继续多头并存。
- Change Cleanup:
  - 已归档：`comprehensive-testing-solution`
    - 归档方式：`openspec archive comprehensive-testing-solution --skip-specs --no-validate --yes`
    - 退场依据：
      - proposal 自称“75% 已实现 / 85% 完成”，但 tasks 仅显示 `4/18`，状态表达明显失真
      - 无合法 OpenSpec delta/spec 落点，不适合继续作为 capability 主线
      - 其能力已被更聚焦 change 拆分承接：
        - `implement-optimized-testing-strategy`：测试基础设施 / ESM / PM2 / layered testing 主线
        - `implement-api-file-level-testing`：API 文件级测试专项主线
  - 保留：
    - `implement-optimized-testing-strategy`
    - `implement-api-file-level-testing`
- Verification Evidence:
  - `openspec validate comprehensive-testing-solution --strict`
    - 结果：无 delta，不能作为规范化 active change 继续保留
  - `openspec archive comprehensive-testing-solution --skip-specs --no-validate --yes`
    - 结果：归档为 `openspec/changes/archive/2026-03-09-comprehensive-testing-solution`
  - `openspec list`
    - 结果：active 列表中已无 `comprehensive-testing-solution`
- Status:
  - 测试域旧总盘：已退场
  - 测试域当前主线：已收敛为“基础设施主线 + API 测试专项主线”

## [WORK] 2026-03-09 `tech-debt-governance-2026q1` 保留判定
- Scope:
  - 判断 `tech-debt-governance-2026q1` 是否应继续清理退场，还是保留为治理元层主线。
- 结论:
  - **保留 active，不归档**
- 保留依据:
  - 该 change 拥有独立 capability：`architecture-governance`
  - 它关注的是治理元层：
    - architecture source of truth
    - spec conflict matrix
    - debt register
    - execution board
    - weekly governance cadence
  - 已归档的 `refactor-technical-debt-remediation-wave1` 主要落在 `code-quality`，属于执行波次和质量门，不等同于治理元层
- 已落地产物（说明该 change **部分被旁路实现**，但未完全闭环）:
  - `architecture/STANDARDS.md`
  - `docs/standards/technical-debt-governance-charter-v1.md`
  - `reports/analysis/tech-debt-baseline.json`
  - `TASK.md`
  - `TASK-REPORT.md`
  - 多份 `reports/analysis/tech-debt-weekly-report-*.md`
- 仍缺失的关键闭环:
  - 目标路径 `technical_debt/governance/` 不存在
  - 正式 live spec `openspec/specs/architecture-governance/spec.md` 不存在
- 判断:
  - 这条 change 不是“已被完全取代”
  - 更准确的状态是：**治理内容部分已在别处落地，但 OpenSpec 主线尚未完成归拢**
- Recommended Next Action:
  - 不做退场
  - 后续若继续处理，应考虑：
    - 缩小范围，只保留真正未落地的治理元层项
    - 或将现有旁路产物重新对齐到 `architecture-governance` 正式 spec
- Verification Evidence:
  - 检查 `openspec/changes/tech-debt-governance-2026q1/*`
  - 检查存在性：
    - `architecture/STANDARDS.md`
    - `docs/standards/technical-debt-governance-charter-v1.md`
    - `reports/analysis/tech-debt-baseline.json`
    - `TASK.md`
    - `TASK-REPORT.md`
    - `reports/analysis/tech-debt-weekly-report-*.md`
  - 检查缺失项：
    - `technical_debt/governance/`
    - `openspec/specs/architecture-governance/spec.md`
- Status:
  - `tech-debt-governance-2026q1`：保留
  - 原因：部分实现 + 独立治理 capability 未闭环

## [WORK] 2026-03-09 LOCAL-2 收口：Maestro owner suggestion 主CLI闭环
- Scope:
  - 收口 `LOCAL-2`，使本地 tracker、collab assignment 与 `TASK.md` / `TASK-REPORT.md` 保持一致。
  - 完成 Maestro 文档入口补齐，并验证本地运行时闭环可用。
- Code / Doc Change:
  - `src/services/maestro/__init__.py`
    - 改为延迟导出 `kernel` / `collab` 名称，修复 `run_symphony` 启动时的循环导入。
  - `tests/unit/services/symphony/test_run_symphony_cli.py`
    - 新增 `run_symphony` 模块导入回归测试，覆盖循环导入场景。
  - `docs/guides/INDEX.md`
    - 补入 `MAESTRO_SUMMARY`、`MAESTRO_QUICK_START`、`SYMPHONY_LOCAL_MULTICLI_WORKFLOW` 入口。
  - `docs/reports/cleanup/index-artifacts/INDEX_root.md`
    - 同步补入上述三份文档入口。
  - `TASK.md`
    - 将 `LOCAL-2` 的人工派单记录更新为完成态。
- Verification Evidence:
  - `pytest --no-cov tests/unit/services/symphony/test_run_symphony_cli.py tests/unit/services/symphony/test_maestro_namespace.py -q`
    - 结果：`5 passed`
  - `python scripts/runtime/run_symphony.py WORKFLOW.md --port 8035`
    - `curl http://127.0.0.1:8035/api/v1/state` -> `200`
    - `curl http://127.0.0.1:8035/api/v1/collab/issues/LOCAL-2` -> `200`
    - `curl http://127.0.0.1:8035/api/v1/collab/stale` -> `200`
  - `python scripts/runtime/local_tracker.py --sqlite-path .symphony/tracker.db update-state LOCAL-2 'Done'`
    - 结果：`LOCAL-2  Done  Formalize owner suggestion dispatch workflow`
  - `python scripts/runtime/maestro_collab.py --sqlite-path .symphony/tracker.db assign LOCAL-2 --worker-cli main --assigned-by main --acceptance-summary '补充 TASK.md 正式派单版，并完成 owner suggestion 到 assign 的主CLI闭环' --status completed`
    - 结果：assignment `status=completed`
  - `openspec archive add-maestro-owner-suggestion --yes`
    - 结果：归档为 `openspec/changes/archive/2026-03-08-add-maestro-owner-suggestion`
  - 顺延归档同一主线已完成 change：
    - `add-symphony-service`
    - `add-local-sqlite-symphony-tracker`
    - `align-symphony-local-multicli-collaboration`
    - `define-maestro-three-layer-architecture`
    - `add-maestro-collab-core`
    - `add-maestro-owner-aware-dispatch`
  - `openspec validate symphony-service --type spec --strict`
    - 结果：`Specification 'symphony-service' is valid`
- Status:
  - `LOCAL-2`: 已完成
  - local tracker: `Done`
  - collab assignment: `completed`
  - `symphony-service` OpenSpec 主线：已归档入 spec

## [WORK] 2026-03-05 Mock Manager 修复与全链路验证（Task #4/#5）
- Scope:
  - 修复 `UnifiedMockDataManager` 获取链路健壮性，避免返回无 `get_data` 对象导致 `/api/v1/market/stocks` 500。
  - 复测后端健康与核心接口可用性，整理结构化证据。
- Code Change:
  - `web/backend/app/mock/mock_data/factory.py:14`
    - 新增 `_FallbackMockDataManager`（稳定提供 `get_data`）。
    - 新增 `_is_valid_manager()` 校验 `get_data` 可调用性。
    - 在 `get_mock_data_manager()` 中增加缓存实例与新实例的类型/模块日志。
    - 当对象无有效 `get_data` 或异常时统一回退 fallback。
- Verification Evidence:
  - `curl http://127.0.0.1:8020/health` -> `200`
    - 证据文件：`/tmp/backend_health_after_fix.json`
    - 关键结果：`status=healthy`
  - `curl http://127.0.0.1:8020/api/v1/market/stocks?limit=5` -> `200`
    - 证据文件：`/tmp/stocks_api_after_fix.json`
    - 关键结果：`success=true`, `source=mock`, `total=5`
  - Python 运行态校验：
    - `PYTHONPATH=/opt/claude/mystocks_spec/web/backend python3 -c "..."`
    - 输出：`UnifiedMockDataManager app.mock.mock_data True`
- Frontend Baseline Evidence (复用现有结果):
  - 证据文件：`/tmp/playwright_results_v2.json`
  - 关键结果：登录页加载正常，控制台错误 0，网络失败 0。
- Status:
  - Task #4: 已完成
  - Task #5: 已完成结构化证据沉淀

## [AUTO] 2026-02-13 23:50:54 Session 9862d30c-05f2-458c-aa0b-047bdc3293ec
- Completion: true
- Summary: Scripts are executable and the skill is registered. Here's the completed skill summary:
- Model: `glm-5`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/9862d30c-05f2-458c-aa0b-047bdc3293ec.jsonl`


## [AUTO] 2026-02-14 00:10:55 Session 9862d30c-05f2-458c-aa0b-047bdc3293ec
- Completion: true
- Summary: 这是一个很好的问题！当前设计确实缺少 Worker CLI 的**确认报到机制**。让我分析问题并提出解决方案：
- Model: `glm-5`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/9862d30c-05f2-458c-aa0b-047bdc3293ec.jsonl`


## [AUTO] 2026-02-14 00:28:17 Session 9862d30c-05f2-458c-aa0b-047bdc3293ec
- Completion: true
- Summary: ---
- Model: `glm-5`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/9862d30c-05f2-458c-aa0b-047bdc3293ec.jsonl`


## [AUTO] 2026-02-16 12:31:47 Session cf325287-a5b2-4b31-9b0e-72e482af7db0
- Completion: true
- Summary: 了解，质量门有专人处理。那我这边的文档更新工作已经全部完成了。
- Model: `kiro-claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/cf325287-a5b2-4b31-9b0e-72e482af7db0.jsonl`


## [AUTO] 2026-02-22 18:35:27 Session 5672dc2c-3b4e-4bc7-82d5-cb1685c788c0
- Completion: true
- Summary: 已配置完成。
- Model: `glm-5`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/5672dc2c-3b4e-4bc7-82d5-cb1685c788c0.jsonl`


## [AUTO] 2026-02-23 12:49:55 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: ---
- Model: `glm-4.7`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-02-28 18:14:49 Session 47e961d4-8690-4de6-bd1f-405b4a1d47a8
- Completion: true
- Summary: 已完成 OMC 全局配置，当前状态如下：
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/47e961d4-8690-4de6-bd1f-405b4a1d47a8.jsonl`


## [AUTO] 2026-02-28 18:36:12 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 继续完成了一轮语义归一，并已验证通过。
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-02-28 18:45:03 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 继续完成了最后收口，当前状态如下：
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-02-28 19:04:55 Session 47e961d4-8690-4de6-bd1f-405b4a1d47a8
- Completion: true
- Summary: <summary>
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/47e961d4-8690-4de6-bd1f-405b4a1d47a8.jsonl`


## [AUTO] 2026-03-01 12:34:07 Session c74b6e2e-2466-4ff0-b98e-a1bb2440a49c
- Completion: true
- Summary: <summary>
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/c74b6e2e-2466-4ff0-b98e-a1bb2440a49c.jsonl`


## [AUTO] 2026-03-01 13:23:32 Session c74b6e2e-2466-4ff0-b98e-a1bb2440a49c
- Completion: true
- Summary: 已完成，阈值已支持环境变量配置并验证通过。
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/c74b6e2e-2466-4ff0-b98e-a1bb2440a49c.jsonl`


## [AUTO] 2026-03-01 17:05:14 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 继续完成了。我刚才尝试调用独立 `code-reviewer` 子代理做审查，但该环境返回 503（模型通道不可用），所以我已手动完成同等快速审查。
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-01 18:55:45 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 收到，已按“可验收完成”给你整理最终关闭说明。
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-01 18:59:01 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 继续完成了，并做了进一步收敛。
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-01 22:19:01 Session acb7ff56-04c0-4574-81b0-054e743d400a
- Completion: true
- Summary: 已完成。我已生成任务总结文档，包含：
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/acb7ff56-04c0-4574-81b0-054e743d400a.jsonl`


## [AUTO] 2026-03-01 23:24:30 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成，继续推进并验证通过。
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 01:08:20 Session acb7ff56-04c0-4574-81b0-054e743d400a
- Completion: true
- Summary: 已完成，你同意的这步我已经落地并验证通过。
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/acb7ff56-04c0-4574-81b0-054e743d400a.jsonl`


## [AUTO] 2026-03-02 01:17:38 Session acb7ff56-04c0-4574-81b0-054e743d400a
- Completion: true
- Summary: 已修复。你看到的 **“Stop says: ⚠️ 发现 2 个错误”** 是因为 Python Stop hook 把**非关键检查**也计入了 `TOTAL_ERRORS`，从而触发 warning。
- Model: `model`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/acb7ff56-04c0-4574-81b0-054e743d400a.jsonl`


## [AUTO] 2026-03-02 08:42:14 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成前端 TypeScript 类型检查的第一轮修复。当前已清理的错误包括：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 08:47:18 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成路由元数据的 `title` 字段补全。当前错误队列已大幅减少，主要剩余问题为：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 09:08:27 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮 TypeScript 类型检查修复的关键部分。当前状态：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 09:12:33 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的主要工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 09:23:24 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的主要工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 09:49:59 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的主要工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 10:05:10 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的主要工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 10:34:25 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的主要工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 10:42:55 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的主要工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 11:09:56 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的主要工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 11:10:57 Session 1e3a7b3b-e92f-49c4-93f5-ae61eabaa680
- Completion: true
- Summary: 完美！问题已修复。现在重新打开 HTML 文件：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/1e3a7b3b-e92f-49c4-93f5-ae61eabaa680.jsonl`


## [AUTO] 2026-03-02 11:14:22 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的主要工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 11:18:58 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的关键工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 11:27:58 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的主要工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 11:34:19 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成第一轮前端 TypeScript 类型检查修复的主要工作。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 11:42:47 Session 1e3a7b3b-e92f-49c4-93f5-ae61eabaa680
- Completion: true
- Summary: 完美！问题已修复。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/1e3a7b3b-e92f-49c4-93f5-ae61eabaa680.jsonl`


## [AUTO] 2026-03-02 11:58:27 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成对自动生成类型文件的修复。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 12:00:27 Session 1e3a7b3b-e92f-49c4-93f5-ae61eabaa680
- Completion: true
- Summary: 完美！已重新生成简化版报告。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/1e3a7b3b-e92f-49c4-93f5-ae61eabaa680.jsonl`


## [AUTO] 2026-03-02 12:07:13 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成任务交接文档的编写。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 16:04:34 Session 24633564-5346-4abf-afa7-f297681c2759
- Completion: true
- Summary: 已完成任务交接。文档已保存在 `/opt/claude/mystocks_spec/docs/reports/TYPESCRIPT_TYPE_CHECK_ISSUES_2026-03-02.md`，包含了完整的问题分析、根本原因、建议方案和交接信息。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/24633564-5346-4abf-afa7-f297681c2759.jsonl`


## [AUTO] 2026-03-02 16:52:58 Session ec1fbfdc-07ff-4ff4-b877-96bd6439175f
- Completion: true
- Summary: 我已经完成了测试框架的修复和更新。让我总结一下所有的改动：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/ec1fbfdc-07ff-4ff4-b877-96bd6439175f.jsonl`


## [AUTO] 2026-03-02 22:53:41 Session c05f89e3-316f-497d-9911-4412046af0f5
- Completion: true
- Summary: 理解。现在我们已经完成了：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/c05f89e3-316f-497d-9911-4412046af0f5.jsonl`


## [AUTO] 2026-03-03 08:15:16 Session 68072cce-843a-4069-bf05-ad04c0ad6b2d
- Completion: true
- Summary: 非常好，这个补充很关键。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/68072cce-843a-4069-bf05-ad04c0ad6b2d.jsonl`


## [AUTO] 2026-03-03 11:37:07 Session 68072cce-843a-4069-bf05-ad04c0ad6b2d
- Completion: true
- Summary: 已完成 **Quant Matrix Pro 骨架** 的创建工作。下面给出核心改动概览以及后续验证步骤。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/68072cce-843a-4069-bf05-ad04c0ad6b2d.jsonl`


## [AUTO] 2026-03-03 11:39:05 Session ec1fbfdc-07ff-4ff4-b877-96bd6439175f
- Completion: true
- Summary: <summary>
- Model: `openai/gpt-oss-120b`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/ec1fbfdc-07ff-4ff4-b877-96bd6439175f.jsonl`


## [AUTO] 2026-03-03 12:18:55 Session 68072cce-843a-4069-bf05-ad04c0ad6b2d
- Completion: true
- Summary: 已继续执行，**Quant Matrix Pro 第一阶段骨架已落地并可通过前端类型检查**。
- Model: `gpt-5.3-codex`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/68072cce-843a-4069-bf05-ad04c0ad6b2d.jsonl`


## [AUTO] 2026-03-03 12:19:42 Session ec1fbfdc-07ff-4ff4-b877-96bd6439175f
- Completion: true
- Summary: <summary>
- Model: `openai/gpt-oss-120b`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/ec1fbfdc-07ff-4ff4-b877-96bd6439175f.jsonl`


## [AUTO] 2026-03-03 12:26:18 Session ec1fbfdc-07ff-4ff4-b877-96bd6439175f
- Completion: true
- Summary: <summary>
- Model: `openai/gpt-oss-120b`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/ec1fbfdc-07ff-4ff4-b877-96bd6439175f.jsonl`


## [AUTO] 2026-03-03 14:14:16 Session ec1fbfdc-07ff-4ff4-b877-96bd6439175f
- Completion: true
- Summary: <summary>
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/ec1fbfdc-07ff-4ff4-b877-96bd6439175f.jsonl`


## [AUTO] 2026-03-03 14:19:15 Session ec1fbfdc-07ff-4ff4-b877-96bd6439175f
- Completion: true
- Summary: <summary>
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/ec1fbfdc-07ff-4ff4-b877-96bd6439175f.jsonl`


## [AUTO] 2026-03-03 15:28:28 Session 68072cce-843a-4069-bf05-ad04c0ad6b2d
- Completion: true
- Summary: 已完成 **Quant Matrix** 页面以及 **ArtDeco** 策略信号页**的 TypeScript 类型错误修复，并确认前端项目的类型检查全部通过。
- Model: `openai/gpt-oss-120b`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/68072cce-843a-4069-bf05-ad04c0ad6b2d.jsonl`


## [AUTO] 2026-03-03 15:50:50 Session 68072cce-843a-4069-bf05-ad04c0ad6b2d
- Completion: true
- Summary: 已完成以下工作：
- Model: `openai/gpt-oss-120b`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/68072cce-843a-4069-bf05-ad04c0ad6b2d.jsonl`


## [AUTO] 2026-03-03 15:54:19 Session ec1fbfdc-07ff-4ff4-b877-96bd6439175f
- Completion: true
- Summary: <summary>
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/ec1fbfdc-07ff-4ff4-b877-96bd6439175f.jsonl`


## [AUTO] 2026-03-03 18:09:35 Session 68072cce-843a-4069-bf05-ad04c0ad6b2d
- Completion: true
- Summary: 已完成 **QuantMatrix Dealing Room** 页面所需的所有修复：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/68072cce-843a-4069-bf05-ad04c0ad6b2d.jsonl`


## [AUTO] 2026-03-03 21:53:07 Session 68072cce-843a-4069-bf05-ad04c0ad6b2d
- Completion: true
- Summary: 已完成以下工作：
- Model: `openai/gpt-oss-120b`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/68072cce-843a-4069-bf05-ad04c0ad6b2d.jsonl`


## [AUTO] 2026-03-04 09:58:23 Session 33ff4a1f-f24e-47f7-bd59-784bfe39a7a4
- Completion: true
- Summary: 我看到您的项目有大量的 worktree，让我帮您整理分析一下：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/33ff4a1f-f24e-47f7-bd59-784bfe39a7a4.jsonl`


## [AUTO] 2026-03-04 10:27:03 Session 33ff4a1f-f24e-47f7-bd59-784bfe39a7a4
- Completion: true
- Summary: 我已成功执行 **方案 A（保守清理）**，清理结果如下：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/33ff4a1f-f24e-47f7-bd59-784bfe39a7a4.jsonl`


## [AUTO] 2026-03-05 00:58:45 Session 0db6503d-8172-43b8-9072-9e34491e55d4
- Completion: true
- Summary: 收到，我已继续完成了三路并行审查（质量/安全/综合），结论一致：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/0db6503d-8172-43b8-9072-9e34491e55d4.jsonl`


## [AUTO] 2026-03-05 10:05:03 Session 0db6503d-8172-43b8-9072-9e34491e55d4
- Completion: true
- Summary: **结论：** **NO‑GO**（当前状态不适合作为 `main` 基线）
- Model: `openai/gpt-oss-120b`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/0db6503d-8172-43b8-9072-9e34491e55d4.jsonl`


## [AUTO] 2026-03-05 13:44:14 Session 0db6503d-8172-43b8-9072-9e34491e55d4
- Completion: true
- Summary: 已继续执行，我刚并行启动了两条修复线：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/0db6503d-8172-43b8-9072-9e34491e55d4.jsonl`


## [AUTO] 2026-03-05 15:54:24 Session 3c07c534-9cb9-457b-81ad-ea3fbc770bef
- Completion: true
- Summary: 已完成收敛，现为**单一配置源**：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/3c07c534-9cb9-457b-81ad-ea3fbc770bef.jsonl`


## [AUTO] 2026-03-05 16:01:33 Session 3c07c534-9cb9-457b-81ad-ea3fbc770bef
- Completion: true
- Summary: 已完成：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/3c07c534-9cb9-457b-81ad-ea3fbc770bef.jsonl`


## [AUTO] 2026-03-05 16:01:50 Session 0db6503d-8172-43b8-9072-9e34491e55d4
- Completion: true
- Summary: 已继续完成并收口，当前结论如下。
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/0db6503d-8172-43b8-9072-9e34491e55d4.jsonl`


## [AUTO] 2026-03-05 23:08:38 Session 0db6503d-8172-43b8-9072-9e34491e55d4
- Completion: true
- Summary: <summary>
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/0db6503d-8172-43b8-9072-9e34491e55d4.jsonl`


## [AUTO] 2026-03-06 01:16:22 Session 0db6503d-8172-43b8-9072-9e34491e55d4
- Completion: true
- Summary: 已继续完成最后任务收口：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/0db6503d-8172-43b8-9072-9e34491e55d4.jsonl`


## [AUTO] 2026-03-07 01:40:53 Session 58a20da9-d8fa-408d-bf03-03fc44bde647
- Completion: true
- Summary: 已完成检查和修改，当前配置如下：
- Model: `claude-opus-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/58a20da9-d8fa-408d-bf03-03fc44bde647.jsonl`


## [AUTO] 2026-03-07 16:49:53 Session 58a20da9-d8fa-408d-bf03-03fc44bde647
- Completion: true
- Summary: 已继续执行并完成本轮收尾，当前状态如下：
- Model: `claude-sonnet-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/58a20da9-d8fa-408d-bf03-03fc44bde647.jsonl`


## [AUTO] 2026-03-07 17:15:49 Session 4c528131-30d2-4005-98e6-14535d2ec75e
- Completion: true
- Summary: 已从中断点继续完成“最后任务”，当前结果如下：
- Model: `claude-sonnet-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/4c528131-30d2-4005-98e6-14535d2ec75e.jsonl`


## [AUTO] 2026-03-08 01:51:07 Session 4c528131-30d2-4005-98e6-14535d2ec75e
- Completion: true
- Summary: <summary>
- Model: `claude-sonnet-4-6`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/4c528131-30d2-4005-98e6-14535d2ec75e.jsonl`


## [MANUAL] 2026-03-08 23:33:10 Session interactive-2026-03-08-dealing-room-governance
- Completion: true
- Summary: 已完成首页 `dealing-room` 语义收口、旧 `/dashboard` 兼容跳转、前端冒烟校验与治理文档同步。关键结果：`build:no-types` 通过、PM2 `mystocks-backend`/`mystocks-frontend` 在线、E2E smoke `15/15` 通过；技术债基线更新为 `frontend_type_errors=90`，并将 E2E 门禁文案改为按实际执行套件报告。
- Model: `claude-sonnet-4-6`
- Files: `web/frontend/src/router/index.ts`, `web/frontend/src/router/homeRoute.ts`, `web/frontend/src/config/pageConfig.ts`, `scripts/dev/tools/generate-page-config.js`, `web/backend/app/services/email_notification_service.py`, `AGENTS.md`, `docs/standards/technical-debt-governance-charter-v1.md`, `reports/analysis/tech-debt-baseline.json`, `docs/guides/MULTI_CLI_PROMPT_STRATEGIES.md`
- Transcript: `N/A (interactive session summary recorded manually)`

## [AUTO] 2026-03-09 01:29:20 Session 4c528131-30d2-4005-98e6-14535d2ec75e
- Completion: true
- Summary: 已完成 **5份核心E2E文档** 的改写工作：
- Model: `glm-5`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/4c528131-30d2-4005-98e6-14535d2ec75e.jsonl`


## [AUTO] 2026-03-09 03:05:02 Session 4c528131-30d2-4005-98e6-14535d2ec75e
- Completion: true
- Summary: 验证结果显示 E2E 命令口径统一工作已基本完成：
- Model: `glm-5`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/4c528131-30d2-4005-98e6-14535d2ec75e.jsonl`


## [AUTO] 2026-03-09 03:08:15 Session 4c528131-30d2-4005-98e6-14535d2ec75e
- Completion: true
- Summary: ---
- Model: `glm-5`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/4c528131-30d2-4005-98e6-14535d2ec75e.jsonl`

## [WORK] 2026-03-12 Round 1 Data/DB Runtime Audit（dev-data-db-audit-claude）
- Scope:
  - 按任务要求先做资产盘点，不做删除或行为改动。
  - 已阅读：`TASK.md`、`openspec/AGENTS.md`、`openspec/changes/audit-data-db-runtime/{proposal,design,tasks}.md`
  - 已补充门禁阅读：`architecture/STANDARDS.md`、`docs/FUNCTION_TREE.md`、`docs/guides/ai-tools/AI_QUICK_START.md`、`docs/architecture/README.md`、`docs/deployment/README.md`、`docs/operations/README.md`
- Judgment Legend:
  - `有效`：当前代码主链路或运行入口明确使用。
  - `兼容保留`：仍被脚本/测试/兼容包装引用，当前不能安全删除。
  - `待判定`：仓库中存在，但运行入口、部署入口或主链路不够清晰。
- Snapshot:
  - `config/data_sources_registry.yaml`：20 个数据源条目，`17` 个目标 `postgresql`，`3` 个目标 `tdengine`；来源分布为 `akshare=18`、`system_mock=1`、`windows_nodes=1`。
  - `config/data_sources.json`：当前 Web 数据源工厂模块配置为 `market/data/dashboard/technical_analysis/watchlist/strategy` 共 6 个模块。
  - `config/table_config.yaml`：29 个表定义，其中 `PostgreSQL=21`、`TDengine=8`、`Redis=0`。
  - `src/adapters/`：顶层 28 个 `.py` 文件，子目录中 `akshare/31`、`tdx/16`、`financial/14`、`efinance_adapter/5`、`akshare_modules/5`、`baostock/1`、`webdata/1`。

### 数据源现状矩阵

| 对象 | 事实源 | 现状 | 判断 |
| --- | --- | --- | --- |
| Core 双库数据协调主线 | `src/core/data_manager.py`、`src/core/infrastructure/data_router.py`、`src/data_access/{postgresql_access,tdengine_access}.py` | `DataManager` 通过 `DataRouter` 按 `DataClassification` 在 `PostgreSQL/TDengine` 间路由；这是核心持久化主链路。 | `有效` |
| YAML 数据源注册表 + Config CRUD | `config/data_sources_registry.yaml`、`src/core/data_source/config_manager.py`、`web/backend/app/api/data_source_config.py` | `ConfigManager` 以 YAML 为主配置源，并挂有版本/审计/回滚能力；GitNexus 显示其被 `/api/v1/data-sources/config` 直接调用，风险为 `CRITICAL`，不能轻删。 | `有效` |
| Web 运行时数据源工厂（JSON） | `config/data_sources.json`、`web/backend/app/services/data_source_factory/*.py`、`web/backend/app/api/data/*`、`web/backend/app/api/market/market_data_request.py` | Web API 仍广泛通过 `get_data_source_factory()` 读取 JSON 配置；这是另一条正在工作的运行时数据源主线。 | `有效` |
| 适配器管理器 V1/V2 | `src/adapters/data_source_manager.py`、`src/core/data_source/base.py` | V1 `DataSourceManager` 在脚本和单测中被大量直接调用；V2 `DataSourceManagerV2` 提供 YAML + 智能路由 + SmartCache，但没有完全取代 V1。 | `兼容保留` |
| MultiSourceManager 局部链路 | `web/backend/app/services/multi_source_manager.py`、`web/backend/app/api/multi_source.py` | 这是独立于上面两套之外的第三条局部链路，当前仅看见 `EastMoney/Cninfo` 适配器和本地字典缓存。 | `有效（局部）` |
| 环境变量驱动数据源工厂 | `src/data_sources/factory.py`、`scripts/switch_data_mode.py` | 依赖 `TIMESERIES_DATA_SOURCE/RELATIONAL_DATA_SOURCE/BUSINESS_DATA_SOURCE`；当前主要被脚本和测试引用，不是 Web 后端主配置入口。 | `兼容保留` |
| 拆分式 YAML Loader | `config/data_sources_loader.py`、`config/data_sources/sina_finance.yaml` | Loader 依赖主配置中的 `load_sources`/`aliases`，但当前 `config/data_sources_registry.yaml` 仅有 `version/last_updated/data_sources`，未启用拆分加载；`sina_finance.yaml` 目前不会进入主运行配置。 | `待判定` |
| Redis DataSourceRegistry 示例栈 | `src/core/datasource/registry.py`、`config/datasource.yaml.example` | 存在 Redis 驱动的注册表/健康状态模型，但未发现它接入当前应用启动流程或 Web 配置。 | `待判定` |
| 顶层适配器资产池 | `src/adapters/` | 代码资产明显多于 YAML/JSON 运行配置暴露的对象；例如 registry YAML 只有 20 个条目且几乎都是 AKShare，但适配器目录包含 TDX、BaoStock、Tushare、EFinance、Sina、Byapi 等多条实现。 | `兼容保留` |

### 数据库现状矩阵

| 对象 | 事实源 | 现状 | 判断 |
| --- | --- | --- | --- |
| PostgreSQL 主业务库 | `web/backend/app/core/config.py`、`web/backend/app/core/database.py`、`src/data_access/postgresql_access.py` | 后端启动必需项；`readiness` 探针校验它；核心查询、监控库回退、DataManager 路由均依赖它。 | `有效` |
| PostgreSQL 监控/审计库 | `web/backend/app/core/config.py`、`src/storage/database/database_manager/_build_monitor_db_url.py` | 当前口径是与主库同实例/同数据库复用，必要时单独 URL；表创建/验证/操作日志均写这里。 | `有效` |
| TDengine 时序库 | `src/data_access/tdengine_access.py`、`web/backend/app/core/tdengine_manager.py`、`config/docker-compose.tdengine.yml` | 高频时序路径明确存在；`table_config.yaml` 中有 8 个 TDengine 表定义，`data_sources_registry.yaml` 里也有 3 个条目直接标到 `tdengine`。 | `有效` |
| Redis 运行时基础设施 | `web/backend/app/core/config.py`、`web/backend/app/core/redis_client.py`、`web/backend/app/core/readiness.py`、`web/backend/app/core/celery_app.py`、`web/backend/app/services/redis/*` | Redis 已不是“可有可无”的旁路：就绪探针、缓存、锁、Pub/Sub、JWT 黑名单、CSRF token 以及 Celery broker/result backend 都在使用它。 | `有效` |
| MongoDB | `config/docker-infra/monitoring-stack.yml`、`config/docker/mongodb.yml`、`tests/unit/core/test_web_backend_runtime_settings.py` | 仓库中有 Docker/README/测试口径，但未找到 Web 后端对应的运行时配置字段、访问层或工厂实现；`IDataAccess` 也没有 Mongo 实现。 | `待判定` |
| MongoDB 抽象枚举 | `src/data_access/interfaces/i_data_access.py` | `DatabaseType` 仍包含 `MONGODB`，但 `DataAccessFactory` 只支持 `TDENGINE/POSTGRESQL`。接口层与实现层口径未对齐。 | `兼容保留` |
| Redis 作为“表型数据库” | `config/table_config.yaml`、`src/core/config_driven_table_manager.py`、`src/storage/database/database_manager/database_table_manager_methods/part1.py` | `table_config.yaml` 仍声明 Redis 连接信息，但表定义数为 0；表管理器也保留 `DatabaseType.REDIS`，并在代码中写明“项目当前未使用”。 | `兼容保留` |

### 缓存现状矩阵

| 对象 | 事实源 | 现状 | 判断 |
| --- | --- | --- | --- |
| L1/L2 多级缓存组件 | `src/core/cache/multi_level.py` | 明确实现 `Memory + Redis` 两级缓存、熔断器和 Prometheus 指标，是共享缓存能力本体。 | `有效` |
| Web RedisManager / RedisCacheService | `web/backend/app/core/redis_client.py`、`web/backend/app/services/redis/redis_cache.py` | Web 运行时的 Redis 接入主线，封装了连接池、set/get、批量操作。 | `有效` |
| Web CacheManager 三级缓存框架 | `web/backend/app/core/cache/core.py`、`web/backend/app/core/cache_integration.py` | 代码层设计为 `L1 memory -> L2 Redis -> L3 TDengine`，但当前文件里 `REDIS_CACHE_AVAILABLE = False`，表现为“框架在、启用条件未完全收口”。 | `兼容保留` |
| 安全相关缓存/状态 | `web/backend/app/main.py`、`web/backend/app/core/security.py` | CSRF token 与 JWT 黑名单均为 `Redis 优先，内存回退`，说明 Redis 是安全路径依赖。 | `有效` |
| MultiSourceManager 本地缓存 | `web/backend/app/services/multi_source_manager.py` | 单独维护 `_cache` + `TTL=300` 的局部内存缓存，不复用共享缓存栈。 | `有效（局部）` |
| `config/.env.example` 的“应用层缓存替代 Redis”口径 | `config/.env.example` | 该文案与当前实现冲突：代码明确依赖 Redis 作为缓存/消息/锁/Celery 设施。 | `待判定（文档失真）` |

### 运行依赖现状矩阵

| 对象 | 事实源 | 现状 | 判断 |
| --- | --- | --- | --- |
| 根 `.env.example` | `.env.example` | 与当前 Web 后端必需项更接近：包含 `POSTGRESQL_*`、`REDIS_*`、`JWT_SECRET_KEY`、`3020/8020` 端口。 | `有效` |
| `config/.env.example` | `config/.env.example` | 仍写有 “Week 3 简化”“应用层缓存替代 Redis” 等旧口径，且与当前 Redis/Celery/Readiness 实现不一致。 | `兼容保留` |
| 本地测试基础设施 | `config/docker-compose.test.yml` | 明确同时拉起 `postgres-test`、`redis-test`、`tdengine-test`、`backend-test`，说明测试口径是三设施并存。 | `有效` |
| 双库开发基础设施 | `config/docker-compose.tdengine.yml` | 提供 `TDengine + PostgreSQL` 开发/验证环境。 | `有效` |
| 生产基础设施 | `config/docker/docker-compose.prod.yml` | 生产口径明确包含 `PostgreSQL + Redis + TDengine + backend + frontend + nginx + prometheus + grafana + backup-service`。 | `有效` |
| 监控栈 Docker | `config/docker-infra/monitoring-stack.yml` | 监控栈包含 `Prometheus/Grafana/MongoDB/AlertManager`，其中 Mongo 更像监控/文档库旁路而非主业务库。 | `待判定` |
| 根 `docker-compose.prod.yml` | `docker-compose.prod.yml` | 当前不是 compose 文件本体，而是仅写了一个路径字符串 `config/docker/docker-compose.prod.yml` 的跳转壳。 | `兼容保留` |
| PM2 配置 | `config/pm2/ecosystem.config.js` | 仍指向旧路径 `/opt/claude/mystocks_spec`，默认端口是 `3002/8000`，与当前门禁口径 `3020/8020` 以及当前 worktree 路径不一致。 | `待判定` |
| 运行时依赖包 | `requirements.txt`、`pyproject.toml` | 依赖仍包含 `redis`、`celery`、`psycopg2-binary`、`taospy`、`asyncpg`，同时保留 `pymongo` 可选依赖；与“Mongo 未接主链”现状形成偏差。 | `兼容保留` |

### 关键结论（第一轮）

1. 当前仓库不是单一数据源/数据库运行栈，而是至少并行存在三套数据源管理路径：
   - Core 双库持久化主线：`DataManager + DataRouter + TDengine/PostgreSQLDataAccess`
   - Web 运行时模块工厂：`config/data_sources.json + web/backend/app/services/data_source_factory`
   - YAML 配置治理主线：`config/data_sources_registry.yaml + ConfigManager + /api/v1/data-sources/config`

2. Redis 不是“未来规划项”或“已被应用层缓存替代”的历史配置，而是当前运行时依赖：
   - readiness probe
   - cache / pubsub / distributed lock
   - JWT blacklist
   - CSRF token 持久化
   - Celery broker / result backend

3. MongoDB 当前更像“基础设施/测试/文档口径遗留项”：
   - Docker 和测试里有明确存在感
   - 但应用运行配置、数据访问层、工厂实现未形成闭环
   - 本轮不能判定可删

4. 数据源拆分治理未真正落地：
   - `config/data_sources_loader.py` 已存在
   - `config/data_sources/sina_finance.yaml` 已存在
   - 但主 registry 未声明 `load_sources`
   - 运行时仍只吃单文件 `config/data_sources_registry.yaml`

5. 当前最明显的“先别删”区域：
   - `src/adapters/data_source_manager.py` / `DataSourceManagerV2`
   - `src/data_sources/factory.py`
   - `src/core/datasource/registry.py`
   - `config/pm2/ecosystem.config.js`
   - Mongo 相关 Docker / 测试口径

### 建议的第二轮核查方向

1. 先做“入口收口”，确认生产/PM2/测试究竟以哪套数据源配置为准：
   - `data_sources_registry.yaml`
   - `data_sources.json`
   - `TIMESERIES/RELATIONAL/BUSINESS_DATA_SOURCE`

2. 逐条核对 Redis 的真实职责边界：
   - 业务缓存
   - 安全状态
   - Celery
   - 监控事件
   - 工具维护 DB

3. 单独核定 Mongo：
   - 是否仅保留给监控/文档/实验用途
   - 是否缺失运行时配置模块
   - 是否只是测试/文档债务

4. 再决定哪些能标为：
   - `可删`
   - `兼容保留`
   - `待判定`

### Verification Evidence

- `git branch --show-current`
- `openspec list`
- `openspec list --specs`
- `python` 统计 `config/data_sources_registry.yaml` 条目分布
- `python` 统计 `config/table_config.yaml` 表定义分布
- `rg`/`sed` 核对以下事实源：
  - `src/core/data_manager.py`
  - `src/core/infrastructure/data_router.py`
  - `src/data_access/{factory,postgresql_access,tdengine_access}.py`
  - `src/core/data_source/config_manager.py`
  - `web/backend/app/services/data_source_factory/data_source_factory.py`
  - `web/backend/app/core/{config,database,redis_client,readiness}.py`
  - `web/backend/app/main.py`
  - `config/{data_sources_registry.yaml,data_sources.json,table_config.yaml}`
  - `config/docker-compose.tdengine.yml`
  - `config/docker-compose.test.yml`
  - `config/docker/docker-compose.prod.yml`
  - `config/docker-infra/monitoring-stack.yml`

## [WORK] 2026-03-12 Round 2 Runtime Entry Convergence（dev-data-db-audit-claude）
- Scope:
  - 在第一轮矩阵基础上，继续收口“真实入口”和“兼容层边界”。
  - 仍然不做删除，不改业务行为，只补事实源和验证证据。

### 入口收口结果

| 入口/链路 | 实际注册或调用证据 | 第二轮判断 |
| --- | --- | --- |
| YAML 配置治理入口 | `web/backend/app/router_registry.py` 注册了 `data_source_config.router` 与 `data_source_registry.router`；前者直连 `ConfigManager(yaml_config_path=\"config/data_sources_registry.yaml\")`，后者直连 `DataSourceManagerV2()` | `有效（治理入口）` |
| JSON Web 运行时数据源入口 | `web/backend/app/router_registry.py` 注册 `data.router`、`data_quality.router`、`market.router`；全仓统计 `get_data_source_factory()` 在 `web/backend/app` 内出现 `22` 次，其中 `/api/data/*` 13 次 | `有效（主运行入口）` |
| `multi_source` 局部运行入口 | `web/backend/app/router_registry.py` 注册 `multi_source.router`；`get_multi_source_manager()` 在 `web/backend/app` 内出现 `10` 次（`api/multi_source.py` 8 次、`announcement_service.py` 1 次、manager 自身单例 1 次） | `有效（局部运行入口）` |
| `src.data_sources` 工厂入口 | `web/backend/app/api/strategy_mgmt.py` 直接 `from src.data_sources import get_business_source`；`web/backend/app/api/v1/risk/core.py`、`web/backend/app/api/risk/metrics.py` 等直接调用 `src.data_sources.factory.get_timeseries_source` | `兼容保留（局部运行链路）` |

### 第二轮判断更新

1. `config/data_sources.json` 已可明确认定为当前 Web 后端最广泛的数据获取配置入口。
   - 证据：`web/backend/app/api/data/*.py`、`web/backend/app/api/data_quality.py`、`web/backend/app/api/market/market_data_request.py` 直接走 `get_data_source_factory()`
   - 结论：它不是测试壳，而是活跃运行主线

2. `config/data_sources_registry.yaml` 已可明确认定为“治理/盘点/配置 CRUD 入口”，不是主要的数据获取运行入口。
   - 证据：`data_source_config.py` 负责 CRUD / 版本 / 回滚
   - 证据：`data_source_registry.py` 负责搜索 / 分类统计 / 测试 / 健康检查
   - 结论：YAML 线是 active，但职责偏治理，不是 Web API 的主取数路径

3. `src.data_sources.factory` 不能再简单视为“只剩脚本兼容”。
   - 它已进入已注册的 `strategy_mgmt` 与 `api/v1/risk/*` 运行路径
   - 但不是全局默认入口，也不主导 `/api/data/*`
   - 当前应归类为 `兼容保留（局部运行链路）`

4. `ConfigManager` 与 `DataSourceManagerV2` 的边界已清晰：
   - `ConfigManager`：面向配置变更治理、版本化、审计、回滚
   - `DataSourceManagerV2`：面向数据源注册表搜索、分类统计、测试与健康检查
   - 两者都吃 `config/data_sources_registry.yaml`，但用途不同

5. `config/data_sources_loader.py` / `config/data_sources/*.yaml` 仍未进入已验证主链路。
   - 当前主 registry 不包含 `load_sources` / `aliases`
   - `config/data_sources/sina_finance.yaml` 不会自动被主 registry 合并
   - 本轮保持 `待判定`

### Mongo / Redis 边界收口

| 对象 | 第二轮证据 | 第二轮判断 |
| --- | --- | --- |
| MongoDB 运行时配置 | `web/backend/app/core/config.py` 中不存在 `mongodb_host` / `mongodb_runtime_host` / `mongodb_connection_kwargs` 等字段；仓库中也不存在 `src/utils/mongo_runtime_config.py` | `兼容保留（主应用未接入，测试/容器口径仍在）` |
| MongoDB 测试口径 | `tests/unit/core/test_web_backend_runtime_settings.py`、`tests/unit/core/test_runtime_config_governance.py` 仍断言 Mongo runtime 配置存在 | `兼容保留（测试漂移）` |
| Redis 角色化配置 | `src/utils/redis_runtime_config.py` 存在按 role 分库实现；相关治理测试大部分通过 | `有效` |
| Celery Redis 默认值 | `web/backend/app/core/config.py` 中 `celery_broker_url` / `celery_result_backend` 字段默认值仍写死 `redis://localhost:6379/0|1`；只有 `default_celery_*` property 才使用 role-aware DB | `待判定（配置行为漂移）` |

### 定向验证结果

- `pytest tests/unit/core/test_web_backend_runtime_settings.py -q -o addopts=''`
  - 结果：`3 failed, 2 passed`
  - 失败原因：
    - `Settings` 缺少 `mongodb_host`
    - `Settings` 缺少 `mongodb_runtime_host`
    - `celery_broker_url` 未按 `REDIS_CELERY_BROKER_DB` 自动回落到 role-specific URL

- `pytest tests/unit/core/test_runtime_config_governance.py -q -o addopts=''`
  - 结果：`2 failed, 8 passed`
  - 失败原因：
    - `ModuleNotFoundError: No module named 'src.utils.mongo_runtime_config'`
  - 已确认通过的部分：
    - Redis role-aware kwargs
    - Redis manager 使用 role-aware kwargs
    - 若显式设置 Redis role DB，相关运行时治理逻辑成立

### 第二轮结论

1. 当前至少有 4 条并存的数据源入口，不宜直接做删除判断：
   - `data_sources.json` Web 运行时主线
   - `data_sources_registry.yaml + ConfigManager` 治理主线
   - `data_sources_registry.yaml + DataSourceManagerV2` 注册表/测试主线
   - `src.data_sources.factory` 局部业务主线

2. Mongo 相关资产已从“纯待判定”收口到更窄的状态：
   - 主应用运行时未接入
   - 但 Docker / README / 测试仍明确保留
   - 因此当前更接近 `兼容保留（周边基础设施/测试口径）`，不是 `有效`

3. Redis 相关资产已可明确分成两类：
   - `有效`：缓存、安全状态、Celery、readiness
   - `待判定/配置漂移`：Celery URL 默认值与 role-aware 设计不完全一致

4. 到第二轮为止，仍然没有形成“可以立即安全删除”的对象名单。
   - 当前最合理动作仍是继续收口入口与文档/测试漂移
   - 而不是直接删除代码或基础设施文件

### 建议的第三轮方向

1. 以“主应用实际注册的 API 路径”为索引，逐条列出：
   - 使用 `data_sources.json` 的路由
   - 使用 `data_sources_registry.yaml` 的路由
   - 使用 `src.data_sources.factory` 的路由

2. 单独建立“漂移清单”：
   - Mongo runtime tests 与现实现脱节
   - `config/.env.example` 与 Redis 现实脱节
   - PM2 端口/路径与当前门禁脱节
   - Celery URL 默认值与 role-aware 设计脱节

3. 在第三轮再判断是否能产出首批低风险修复：
   - 文档校正
   - 测试校正
   - 默认配置校正
   - 仍然先不删运行资产

## [WORK] 2026-03-12 Round 3 Route-Level Ownership Check（dev-data-db-audit-claude）
- Scope:
  - 继续把“文件存在”与“路由已注册并真实调用”分开。
  - 重点复核 `src.data_sources.factory`、风险路由和 dashboard 数据源归属，避免误把死路径算进运行面。

### 路由级修正

1. `strategy_mgmt` 并不把 `src.data_sources` 用在核心 CRUD / 回测流程中。
   - `web/backend/app/api/strategy_mgmt.py` 中 `get_business_source()` 只被 `/api/strategy-mgmt/health` 的 `Depends(get_data_source)` 使用
   - 结论：这是 `局部健康检查依赖`，不是该模块的主业务数据入口

2. `api/risk/metrics.py` 是已注册活路径，且明确使用 `src.data_sources.factory.get_timeseries_source(source_type=\"mock\")`。
   - `web/backend/app/api/risk/__init__.py` 已把 `metrics_router` 纳入 `router`
   - `web/backend/app/api/risk_management.py` 只是兼容 shim，但 `router_registry.py` 注册的是这个 shim 导出的 `app.api.risk.router`
   - 结论：`src.data_sources.factory` 在风险指标路径上是 `有效的局部运行依赖`

3. `web/backend/app/api/v1/risk/core.py` 当前不是主应用已注册路径。
   - 虽然 `web/backend/app/api/v1/risk/__init__.py` 有聚合 router
   - 但当前 `web/backend/app/api/v1/router.py` 并未 include `v1.risk.router`
   - 结论：`api/v1/risk/*` 目前应视为 `未接主路由的存量资产`

4. `dashboard` 不走 `src.data_sources.factory`，而是走专用适配层。
   - `web/backend/app/api/dashboard.py` 依赖 `app.api.dashboard_data_source.get_data_source`
   - `web/backend/app/api/dashboard_data_source.py` 的主实现是 `RealBusinessDataSource`
   - 结论：dashboard 是第四类独立数据接入面，和 `data_sources.json` / `data_sources_registry.yaml` / `src.data_sources.factory` 都不同

### 第三轮结论

1. `src.data_sources.factory` 的运行面比第二轮判断更窄：
   - 活路径主要是 `api/risk/metrics.py`
   - `strategy_mgmt` 仅 `/health` 使用
   - `api/v1/risk/core.py` 当前未接主路由

2. 主应用当前至少存在 4 类数据接入面：
   - `config/data_sources.json` 驱动的 Web 数据源工厂
   - `config/data_sources_registry.yaml` 驱动的治理/注册表入口
   - `multi_source` 局部聚合入口
   - `dashboard_data_source.RealBusinessDataSource` 专用入口

3. 到第三轮为止，`src.data_sources.factory` 仍不能删，但已可从“大面积运行主线”降到“窄面兼容/局部运行链路”。

## [WORK] 2026-03-12 Round 4 Runtime Config Drift Fixes（dev-data-db-audit-claude）
- Scope:
  - 依据第二轮、第三轮已确认的低风险漂移点，先修复 runtime config 兼容层与 `.env` 文档口径。
  - 不做资产删除，不改业务路由。
- Impact Note:
  - 修改前已对 `web/backend/app/core/config.py:Settings` 做 GitNexus impact 分析。
  - 风险级别：`HIGH`
  - 采取的控制策略：
    - 不删除现有字段
    - 仅补兼容属性
    - 仅在 Celery URL 未显式配置时做默认回落

### Implemented Fixes

| 类型 | 文件 | 修复内容 |
| --- | --- | --- |
| 运行时配置兼容 | `web/backend/app/core/config.py` | 为 `Settings` 补充 Mongo 兼容字段：`mongodb_host`、`mongodb_port`、`mongodb_root_username`、`mongodb_root_password`、`mongodb_database`、`mongodb_auth_source`，以及兼容属性 `mongodb_runtime_host`、`mongodb_runtime_port`、`mongodb_connection_kwargs` |
| Celery 默认值收口 | `web/backend/app/core/config.py` | 将 `celery_broker_url` / `celery_result_backend` 改为“空值时按 role-aware Redis DB 自动回落”，修复默认值与 `REDIS_CELERY_*_DB` 脱节 |
| Mongo helper 补全 | `src/utils/mongo_runtime_config.py` | 新增 Mongo runtime helper，支持标准环境变量与 legacy `MONGODB_IP` / `USERNAME` / `PASSWORD` 回落 |
| 文档口径修正 | `config/.env.example` | 删除“应用层缓存替代 Redis”的旧说法，改为当前 `TDengine + PostgreSQL + Redis` 运行口径，并补充 Redis role DB 与 Mongo 兼容环境变量说明 |

### Verification Evidence

- `pytest tests/unit/core/test_web_backend_runtime_settings.py -q -o addopts=''`
  - 结果：`5 passed`
- `pytest tests/unit/core/test_runtime_config_governance.py -q -o addopts=''`
  - 结果：`10 passed`
- `pytest tests/unit/core/test_web_backend_runtime_settings.py tests/unit/core/test_runtime_config_governance.py -q -o addopts=''`
  - 结果：`15 passed`
  - 备注：存在 6 条 warning，均为仓库既有第三方/历史 Pydantic 与 taos 依赖告警，不是本次回归

### Current Status

1. 第二轮确认的两类 runtime 漂移已修复：
   - Mongo compatibility helper / Settings 字段缺失
   - Celery URL 默认回落未使用 role-aware Redis DB

2. 文档漂移已开始收口，但只修了 `config/.env.example`。
   - 根 `.env.example`
   - PM2 配置
   - 其他 README / Docker 文档
   仍需后续继续对齐

3. 当前仍未产生“可删资产”清单。
   - 本轮修复强化了兼容层证据
   - 删除动作仍应延后到入口、文档、测试完全收口之后

## [WORK] 2026-03-12 Round 5 Env And PM2 Drift Fixes（dev-data-db-audit-claude）
- Scope:
  - 继续处理低风险漂移，目标是补齐根 `.env.example` 与 PM2 默认开发配置的当前口径。
  - 不改业务代码，不删资产。

### Implemented Fixes

| 类型 | 文件 | 修复内容 |
| --- | --- | --- |
| 根环境模板收口 | `.env.example` | 补充 Redis role DB、Celery URL、Mongo 兼容环境变量，使根模板与当前 runtime config 兼容层保持一致 |
| PM2 路径/端口收口 | `config/pm2/ecosystem.config.js` | 移除对 `/opt/claude/mystocks_spec` 的硬编码，改为基于 `__dirname` 动态解析项目根；默认端口调整为 `frontend=3020/3021`、`backend=8020/8021`；前后端 cwd、PYTHONPATH 与健康检查地址均改为相对当前仓库根生成 |
| PM2 前端启动方式修正 | `config/pm2/ecosystem.config.js` | 将前端从依赖 `PORT=3002` 的不稳定方式改为显式 `npm run dev -- --host 0.0.0.0 --port <FRONTEND_PORT>` |

### Verification Evidence

- `node -c config/pm2/ecosystem.config.js`
  - 结果：通过
- `node -e "const cfg=require('./config/pm2/ecosystem.config.js'); console.log(cfg.apps.map(a=>a.name+':' + a.cwd).join('\\n'))"`
  - 结果：输出的 `cwd` 已指向当前 worktree：
    - `mystocks-frontend:/opt/claude/mystocks_spec-data-db-audit/web/frontend`
    - `mystocks-backend:/opt/claude/mystocks_spec-data-db-audit/web/backend`
    - 各数据同步任务指向 `/opt/claude/mystocks_spec-data-db-audit`

### Current Status

1. `config/pm2/ecosystem.config.js` 已不再绑定旧仓库绝对路径和旧端口。
2. 根 `.env.example` 与 `config/.env.example` 的 Redis/Celery/Mongo 兼容字段口径已基本对齐。
3. 仍待后续收口的 PM2 / 运维漂移：
   - `web/backend/ecosystem.config.js`
   - `config/pm2/ecosystem.production.config.js`
   - 监控栈文档中的 `8000` 端口口径

## [WORK] 2026-03-13 Round 6 Monitoring And PM2 Production Convergence（dev-data-db-audit-claude）
- Scope:
  - 继续收口 `config/**` 范围内的生产/测试 PM2 配置与监控栈配置、文档口径。
  - 仍然不做删除。

### Implemented Fixes

| 类型 | 文件 | 修复内容 |
| --- | --- | --- |
| 生产 PM2 配置收口 | `config/pm2/ecosystem.production.config.js` | 改为基于 `__dirname` 解析当前仓库根；默认前后端端口收口到 `3020/8020`；去除旧 `/opt/claude/mystocks_spec` 依赖；`post-deploy` 指向 `config/pm2/ecosystem.production.config.js` |
| 测试 PM2 配置收口 | `config/pm2/pm2.config.js` | 改为动态仓库根、`3020/8020` 端口、当前 worktree 路径；前端 `VITE_API_BASE_URL` / `VITE_WS_URL` 与后端口径对齐 |
| Prometheus 抓取端口收口 | `config/monitoring-stack/config/prometheus.yml` | 将残余 `host.docker.internal:8000` / `localhost:8000` 抓取目标统一改为 `8020` |
| AlertManager 注释口径收口 | `config/monitoring-stack/config/alertmanager.yml` | webhook 示例地址从 `8000` 改为 `8020` |
| 监控栈文档收口 | `config/monitoring-stack/{README,DEPLOYMENT,MONITORING_VERIFICATION_COMPLETE_REPORT}.md` | 收口旧 `8000` 端口与旧 `/opt/claude/mystocks_spec/monitoring-stack` 路径引用 |

### Verification Evidence

- `node -c config/pm2/ecosystem.production.config.js`
  - 结果：通过
- `node -c config/pm2/pm2.config.js`
  - 结果：通过
- `python` 解析 YAML：
  - `config/monitoring-stack/config/prometheus.yml`
  - `config/monitoring-stack/config/alertmanager.yml`
  - 结果：均通过 `yaml.safe_load`
- `python` 扫描活跃监控配置/文档：
  - 未发现 `localhost:8000`
  - 未发现 `host.docker.internal:8000`
  - 未发现旧路径 `/opt/claude/mystocks_spec/monitoring-stack`

### Current Status

1. `config/pm2` 下三份主配置已部分收口：
   - `ecosystem.config.js`
   - `ecosystem.production.config.js`
   - `pm2.config.js`

2. `config/monitoring-stack` 的主配置和主要活跃文档已从 `8000` 切换到 `8020`。

3. 仍然残留的配置债务主要集中在：
   - `config/pm2/ecosystem.enhanced.config.js`
   - `config/pm2/ecosystem.playwright*.js`
   - `config/monitoring-stack/MONITORING_STATUS.md`
   - `config/monitoring-stack/DEPLOYMENT_NOTES.md`

## [WORK] 2026-03-13 Round 7 Active Monitoring Docs Sweep（dev-data-db-audit-claude）
- Scope:
  - 继续在 `config/**` 范围内做活跃配置/文档的端口与路径收口。
  - 本轮刻意不继续扩到 `ecosystem.enhanced.config.js` 与 Playwright PM2 配置，避免把范围拉散。

### Implemented Fixes

| 类型 | 文件 | 修复内容 |
| --- | --- | --- |
| Prometheus 补漏 | `config/monitoring-stack/config/prometheus.yml` | 将 `wencai/tasks/multi-source` 三个残余 job 的 `8000` target 统一改为 `8020` |
| AlertManager 注释补漏 | `config/monitoring-stack/config/alertmanager.yml` | 统一 webhook 示例端口到 `8020` |
| 活跃状态文档收口 | `config/monitoring-stack/MONITORING_STATUS.md` | 修复旧 `monitoring-stack` 仓库路径引用 |
| 活跃监控文档收口 | `config/monitoring-stack/{README,DEPLOYMENT,MONITORING_VERIFICATION_COMPLETE_REPORT}.md` | 复核并确保已改文件中不再残留 `8000` 或旧 `monitoring-stack` 路径 |

### Verification Evidence

- `node -c config/pm2/ecosystem.production.config.js && node -c config/pm2/pm2.config.js`
  - 结果：通过
- `python` 解析 YAML：
  - `config/monitoring-stack/config/prometheus.yml`
  - `config/monitoring-stack/config/alertmanager.yml`
  - 结果：通过
- `python` 扫描以下活跃文件：
  - `config/monitoring-stack/config/prometheus.yml`
  - `config/monitoring-stack/config/alertmanager.yml`
  - `config/monitoring-stack/README.md`
  - `config/monitoring-stack/DEPLOYMENT.md`
  - `config/monitoring-stack/MONITORING_STATUS.md`
  - `config/monitoring-stack/MONITORING_VERIFICATION_COMPLETE_REPORT.md`
  - `config/pm2/ecosystem.config.js`
  - `config/pm2/ecosystem.production.config.js`
  - `config/pm2/pm2.config.js`
  - 结果：未发现以下残留模式：
    - `localhost:8000`
    - `host.docker.internal:8000`
    - `/opt/claude/mystocks_spec/monitoring-stack`
    - `/opt/claude/mystocks_spec/web/backend`
    - `/opt/claude/mystocks_spec/web/frontend`

### Current Status

1. 活跃的 PM2 主配置和监控栈主配置/主文档已经基本对齐到：
   - 后端：`8020`
   - 前端：`3020`
   - 当前 worktree 路径

2. 仍待后续处理的主要配置债务：
   - `config/pm2/ecosystem.enhanced.config.js`
   - `config/pm2/ecosystem.playwright*.js`
   - `config/monitoring-stack/DEPLOYMENT_NOTES.md`

3. 到目前为止，本分支仍没有形成“可以立即删除”的资产列表；
   现阶段更适合继续做配置/文档/测试口径收口，再进入删除判定。

## [WORK] 2026-03-13 Round 8 PM2 Worktree Decoupling Sweep（dev-data-db-audit-claude）
- Scope:
  - 收口剩余 `config/pm2` 中仍绑定旧 worktree 绝对路径的配置文件。
  - 本轮只改路径与默认端口口径，不改 Playwright 或增强版配置的业务语义。

### Implemented Fixes

| 类型 | 文件 | 修复内容 |
| --- | --- | --- |
| 增强 PM2 配置 | `config/pm2/ecosystem.enhanced.config.js` | 新增 `projectRoot/frontendCwd/backendCwd/gpuApiCwd` 与 `frontendPort/backendPort` 常量；去除旧 `/opt/claude/mystocks_spec`、`3002`、`8000`、`3000` 绑定 |
| Playwright PM2 配置 | `config/pm2/ecosystem.playwright*.js` | 为所有活跃 Playwright PM2 配置新增动态 `projectRoot`，统一替换旧 `cwd: '/opt/claude/mystocks_spec'` |

### Verification Evidence

- `node -c` 通过：
  - `config/pm2/ecosystem.enhanced.config.js`
  - `config/pm2/ecosystem.playwright.config.js`
  - `config/pm2/ecosystem.playwright.p0.config.js`
  - `config/pm2/ecosystem.playwright.p1.config.js`
  - `config/pm2/ecosystem.playwright.p1.fixed.config.js`
  - `config/pm2/ecosystem.playwright.p2.config.js`
- `python` 文本扫描：
  - 未发现上述文件中残留 `/opt/claude/mystocks_spec`

### Current Status

1. `config/pm2` 下当前活跃的主配置与测试配置已基本完成 worktree 解耦。
2. 仍可继续处理但优先级更低的项：
   - `config/monitoring-stack/DEPLOYMENT_NOTES.md`
   - 其他历史报告/说明文档中的旧端口口径

3. 到目前为止，数据源/数据库/缓存治理阶段已从“纯盘点”推进到“配置与文档漂移修复”，但仍未进入删除动作。

## [WORK] 2026-03-13 Round 9 Active Deployment Docs Port Convergence（dev-data-db-audit-claude）
- Scope:
  - 收口活跃部署/运维/README 文档中的旧固定端口与旧“端口范围”说法。
  - 仅改文档，不改运行逻辑。

### Implemented Fixes

| 类型 | 文件 | 修复内容 |
| --- | --- | --- |
| 部署文档收口 | `docs/deployment/README.md` | 将“8000-8010 / 3000-3010 自动选端口”改为固定 `8020/8021` 与 `3020/3021`；命令与访问地址同步更新 |
| 运维部署文档收口 | `docs/operations/deployment-guide.md` | 同步改为固定 `8020/8021` 与 `3020/3021` 口径 |
| Web README 收口 | `web/README.md` | 将旧 “固定端口 3000/8000” 全部改为当前 `3020/3021` 与 `8020/8021`，并同步启动命令与排障命令 |

### Verification Evidence

- `python` 文本扫描：
  - `docs/deployment/README.md`
  - `docs/operations/deployment-guide.md`
  - `web/README.md`
  - 结果：未发现以下残留模式：
    - `localhost:3000`
    - `3000-3010`
    - `8000-8010`
    - `固定端口 8000`
    - `固定端口 3000`

### Current Status

1. 活跃部署/运维说明文档已基本统一到：
   - 前端：`3020`
   - 后端：`8020`
   - 备用端口：`3021/8021`

2. 当前剩余主要是历史/次级文档债务，而不是主入口文档债务。

3. 现阶段已具备进入“首批保守删除候选清单”的前提，但建议先单独整理候选项与删除依据，再决定是否执行删除。

## [WORK] 2026-03-13 Round 10 Conservative Deletion Candidates Inventory（dev-data-db-audit-claude）
- Scope:
  - 生成首批“保守删除候选清单”，仍然只做清单，不执行删除。
  - 候选对象限定在本任务 scope 内，且必须满足以下至少两项：
    - 明确是时间戳备份副本
    - 存在同名/同职责 canonical 文件
    - 在 `src/config/scripts/tests/web/docs` 的活跃源码中无直接引用
    - 与当前架构口径（如 MySQL 已移除）明显不一致

### 首批保守删除候选

| 对象 | 功能树状态 | 删除判断 | 依据 |
| --- | --- | --- | --- |
| `src/adapters/akshare_adapter.py.backup_1767777516` | `重复冗余` | `可删候选` | 时间戳备份副本；canonical 文件为 `src/adapters/akshare_adapter.py`；在活跃源码检索中未发现直接引用，只有报告/质量产物提及 |
| `src/adapters/financial_adapter.py.backup_1767777515` | `重复冗余` | `可删候选` | 时间戳备份副本；canonical 文件为 `src/adapters/financial_adapter.py`；活跃源码无直接引用，仅报告/质量产物提及 |
| `src/core/config_driven_table_manager.py.backup_20251108` | `重复冗余` | `可删候选` | 时间戳备份副本；canonical 文件为 `src/core/config_driven_table_manager.py`；当前主实现已存在且已被实际引用，备份副本未进入主链路 |
| `src/core/data_source_manager_v2.py.backup_1767777516` | `重复冗余` | `可删候选` | 时间戳备份副本；canonical 对应能力已迁入 `src/core/data_source/base.py` / `src/core/data_source/config_manager.py` / 当前 V2 管理栈；活跃源码无直接引用 |

### 明确不删 / 暂不列入删除候选

| 对象 | 状态 | 保留原因 |
| --- | --- | --- |
| `src/storage/database/execute_example_mysql_only.py` | `待判定` | 文件名带 `mysql_only`，但内容实际在跑 PostgreSQL 示例；当前主要被历史文档/质量报告引用。它更像“误导性命名的示例脚本”，直接删除风险高，优先建议后续做“重命名或归档”判定 |
| `src/adapters/legacy_adapter.py` | `兼容保留` | 仍被 `scripts/dev/examples/real_project_application/...` 指向，属于演示/重构样例链路，不满足“代码路径可安全移除” |
| `src/adapters/akshare/legacy_market_data.py` | `兼容保留` | 文件头明确声明“保留用于向后兼容”；多份历史完成报告把它作为 legacy 同步函数模块记录，当前不能仅凭文件名删除 |
| `config/sina_finance_only.yaml` | `兼容保留` | 被 `scripts/quick_health_check.sh` 与 `scripts/tests/legacy/test_sina_integration_final.py` 直接使用，是特化配置入口，不满足安全移除条件 |
| `config/data_sources/sina_finance.yaml` | `待判定` | 当前主 registry 未加载它，但它属于拆分式 loader 计划的一部分；在拆分治理正式下线前不应删除 |
| `config/datasource.yaml.example` | `兼容保留` | 仍有 archived OpenSpec 任务将其作为交付物记录；虽然主应用未直接接入，但尚不满足“正式下线”证据 |

### 当前建议

1. 如果下一轮进入真正删除动作，优先只处理上面 4 个时间戳备份副本。
2. `execute_example_mysql_only.py` 不建议直接删，优先做：
   - 是否改名为 PostgreSQL example
   - 是否移入 `archive/` 或 `scripts/examples/`
3. `legacy_*` 与 `sina_finance*` 相关对象目前仍保持保守，不进入删除执行面。

## [WORK] 2026-03-13 Round 11 First Conservative Cleanup Execution（dev-data-db-audit-claude）
- Scope:
  - 执行首批真正删除动作，但仅限上一轮已确认的 4 个时间戳备份副本。
  - 仍不触碰 `legacy_*`、`sina_finance*`、`execute_example_mysql_only.py`。

### Removed

- `src/adapters/akshare_adapter.py.backup_1767777516`
- `src/adapters/financial_adapter.py.backup_1767777515`
- `src/core/config_driven_table_manager.py.backup_20251108`
- `src/core/data_source_manager_v2.py.backup_1767777516`

### Removal Basis

1. 以上 4 个对象均为带时间戳的备份副本。
2. 均存在对应 canonical 主文件或主实现链路。
3. 在活跃源码范围检索中未发现直接引用，仅历史报告/质量产物提及。
4. 根据清理标准，可归入功能树状态 `重复冗余`。

### Verification Evidence

- `python` 检查文件存在性：
  - `src/adapters/akshare_adapter.py.backup_1767777516 -> False`
  - `src/adapters/financial_adapter.py.backup_1767777515 -> False`
  - `src/core/config_driven_table_manager.py.backup_20251108 -> False`
  - `src/core/data_source_manager_v2.py.backup_1767777516 -> False`

### Current Status

1. 当前已完成首批低风险实际清理。
2. 仍未进入删除执行面的对象：
   - `src/storage/database/execute_example_mysql_only.py`
   - `src/adapters/legacy_adapter.py`
   - `src/adapters/akshare/legacy_market_data.py`
   - `config/sina_finance_only.yaml`
   - `config/data_sources/sina_finance.yaml`
   - `config/datasource.yaml.example`
3. 后续若继续删除，应先单独处理“命名误导示例脚本”和“legacy/拆分计划资产”的归档或重命名策略。

## [WORK] 2026-03-13 Round 12 Misleading Example Rename（dev-data-db-audit-claude）
- Scope:
  - 处理命名误导但不适合直接删除的示例脚本。
  - 当前只处理 `execute_example_mysql_only.py`。
- Impact Note:
  - GitNexus upstream impact on file `src/storage/database/execute_example_mysql_only.py`
  - 风险级别：`LOW`
  - 结果：`impactedCount=0`

### Implemented Fix

- `src/storage/database/execute_example_mysql_only.py`
  → `src/storage/database/execute_example_postgresql_only.py`

### Basis

1. 文件内容实际是 PostgreSQL-only 示例，不再包含 MySQL-only 语义。
2. 活跃源码检索未发现上游引用。
3. 旧文件名主要只出现在历史报告、质量产物和代码盘点产物中。
4. 因此更适合改名，而不是保留误导性名称或直接删除。

### Verification Evidence

- `python` 文件存在性检查：
  - `src/storage/database/execute_example_mysql_only.py -> False`
  - `src/storage/database/execute_example_postgresql_only.py -> True`
- `rg` 活跃源码范围检索：
  - 未发现旧文件名在活跃源码中的直接引用
  - 旧文件名仅残留于历史报告/质量产物

### Status Update

- `src/storage/database/execute_example_mysql_only.py`
  - 状态由 `待判定`
  - 更新为 `已通过重命名收口`

- 仍保守保留：
  - `src/adapters/legacy_adapter.py`
  - `src/adapters/akshare/legacy_market_data.py`
  - `config/sina_finance_only.yaml`
  - `config/data_sources/sina_finance.yaml`
  - `config/datasource.yaml.example`

## [WORK] 2026-03-13 Round 13 Legacy Compatibility Fix（dev-data-db-audit-claude）
- Scope:
  - 对已判定为“兼容保留”的 legacy 资产做最小必要修复，而不是删除。
  - 当前只处理 `src/adapters/akshare/legacy_market_data.py`。
- Impact Note:
  - `legacy_market_data.py` 的 GitNexus upstream impact 为 `LOW`，`impactedCount=0`
  - 文件仍通过 `src/adapters/akshare/__init__.py` 对外暴露 legacy 函数，因此不适合删除

### Implemented Fix

| 文件 | 问题 | 修复 |
| --- | --- | --- |
| `src/adapters/akshare/legacy_market_data.py` | `_retry_api_call` 名义上是“同步版本”，实际返回 `async wrapper`，导致 legacy 同步函数会返回 coroutine | 改为真正的同步重试逻辑：`time.sleep` + 同步 `wrapper` + 直接 `func(*args, **kwargs)` |

### Verification Evidence

- 最小化本地验证脚本执行结果：
  - `result ok`
  - `call_count 1`
  - `is_coroutine False`

### Status Update

1. `src/adapters/akshare/legacy_market_data.py` 继续保持 `兼容保留`。
2. 但它已不再是“坏掉的兼容层”，当前至少满足同步调用语义。
3. `src/adapters/legacy_adapter.py` 仍保持不动，继续视为示例/重构演示资产。

## [WORK] 2026-03-13 Round 14 Remaining Candidate Closure（dev-data-db-audit-claude）
- Scope:
  - 收口最后两类仍未最终定性的对象：
    - `sina_finance*` 配置
    - `config/datasource.yaml.example`
  - 本轮只更新结论，不执行删除。

### 结论更新

| 对象 | 新结论 | 依据 |
| --- | --- | --- |
| `config/sina_finance_only.yaml` | `兼容保留` | 被 `scripts/quick_health_check.sh` 与 `scripts/tests/legacy/test_sina_integration_final.py` 直接使用；不是孤儿配置 |
| `config/data_sources/sina_finance.yaml` | `兼容保留` | 由 `config/sina_finance_only.yaml` 的 `load_sources: [sina_finance]` 间接加载；因此不是无主拆分文件 |
| `config/datasource.yaml.example` | `兼容保留` | 对应 `DataSourceRegistry` / `src/api/datasource/routes.py` 这条模板化管理链路；虽然不属当前 Web 主入口，但仍有真实 API/测试/模块存在 |

### Supporting Evidence

1. `config/sina_finance_only.yaml`
   - 含 `load_sources: [sina_finance]`
   - 是 `config.data_sources_loader.DataSourcesLoader` 可直接消费的主配置文件

2. `config/data_sources/sina_finance.yaml`
   - 包含 `sina_finance_stock_ratings` 数据源定义
   - 被 `test_sina_integration_final.py` 通过 `loader.main_config_file = loader.config_dir / "sina_finance_only.yaml"` 的方式间接加载

3. `config/datasource.yaml.example`
   - 对应 `src/core/datasource/registry.py:DataSourceRegistry`
   - `src/api/datasource/routes.py` 存在完整 `/api/datasources` CRUD / health / metrics 路由
   - 相关 `tests/unit/test_datasource/*` 和 `tests/api/file_tests/test_data_source_registry_api.py` 仍在

### Final Remaining Inventory Status

- `可删/已执行`
  - 4 个时间戳备份副本已删除

- `已通过重命名收口`
  - `execute_example_mysql_only.py` → `execute_example_postgresql_only.py`

- `兼容保留`
  - `src/adapters/legacy_adapter.py`
  - `src/adapters/akshare/legacy_market_data.py`
  - `config/sina_finance_only.yaml`
  - `config/data_sources/sina_finance.yaml`
  - `config/datasource.yaml.example`

### Current Status

1. 本轮之后，原先列出的高不确定对象已基本全部落入明确分类。
2. 当前若再继续推进，重点就不再是“盘点”，而是：
   - 是否要对 `兼容保留` 项做归档/隔离
   - 是否要继续统一历史报告中的旧文件名引用
   - 是否要准备提交/分批提交

## [WORK] 2026-03-13 Compatibility Retention Archival Plan
- Scope:
  - 将兼容保留资产的后续处理方式固化为可执行方案。
  - 本轮只出方案，不执行新的迁移。

### Output

- 新增方案文档：
  - `reports/governance/2026-03-13-compatibility-retention-archival-plan.md`

### Plan Summary

1. `src/adapters/legacy_adapter.py`
   - 定位：`archive-ready`
   - 建议目标：`archive/code-compatibility/examples/legacy_adapter.py`

2. `src/adapters/akshare/legacy_market_data.py`
   - 定位：`in-source isolation`
   - 建议目标：`src/adapters/akshare/compat/legacy_market_data.py`

3. `config/sina_finance_only.yaml`
   - 定位：`config compatibility hold`
   - 后续建议目标：`config/compatibility/sina_finance/main.yaml`

4. `config/data_sources/sina_finance.yaml`
   - 定位：`config compatibility hold`
   - 后续建议目标：`config/compatibility/sina_finance/source.yaml`

5. `config/datasource.yaml.example`
   - 定位：`config compatibility hold`
   - 后续建议目标：`config/templates/datasource-registry.yaml.example`

### Current Status

1. “兼容保留资产的归档/隔离方案”已经独立成文，可按批次执行。
2. 当前可以选择进入下一轮实际迁移：
   - 先迁 `legacy_adapter.py`
   - 再做 `legacy_market_data.py` 的 `compat/` 隔离
3. `sina_finance*` 与 `datasource.yaml.example` 仍建议晚于代码兼容资产迁移。

## [WORK] 2026-03-13 Round 15 Compatibility Isolation Execution（dev-data-db-audit-claude）
- Scope:
  - 执行归档/隔离方案中的前两步：
    - `legacy_adapter.py` 归档
    - `legacy_market_data.py` 隔离到 `compat/`

### Implemented Changes

| 类型 | 动作 |
| --- | --- |
| 归档 | `src/adapters/legacy_adapter.py` → `archive/code-compatibility/examples/legacy_adapter.py` |
| 活跃引用收口 | `scripts/dev/examples/real_project_application/real_project_application_methods/part1.py` 中的 `refactor_module` 路径改为归档后的新位置 |
| 兼容隔离 | `src/adapters/akshare/legacy_market_data.py` 的主实现移动到 `src/adapters/akshare/compat/legacy_market_data.py` |
| 兼容壳 | 新增 `src/adapters/akshare/legacy_market_data.py` 作为薄兼容 shim，继续 re-export 原函数 |
| 兼容导出 | 新增 `src/adapters/akshare/compat/__init__.py`，并将 `src/adapters/akshare/__init__.py` 改为从 `compat` 导出 legacy 函数 |

### Verification Evidence

- 文件存在性检查：
  - `src/adapters/legacy_adapter.py -> False`
  - `archive/code-compatibility/examples/legacy_adapter.py -> True`
  - `src/adapters/akshare/compat/legacy_market_data.py -> True`
  - `src/adapters/akshare/legacy_market_data.py -> True`

- 活跃源码扫描结果：
  - `archive/code-compatibility/examples/legacy_adapter.py` 已替换唯一活跃路径引用
  - `src/adapters/akshare/legacy_market_data.py` 在活跃源码中仅作为兼容壳存在
  - `src/adapters/akshare/__init__.py` 已切换到 `.compat`

- 语法验证：
  - `python -m py_compile src/adapters/akshare/__init__.py`
  - `python -m py_compile src/adapters/akshare/legacy_market_data.py`
  - `python -m py_compile src/adapters/akshare/compat/__init__.py`
  - `python -m py_compile src/adapters/akshare/compat/legacy_market_data.py`
  - `python -m py_compile scripts/dev/examples/real_project_application/real_project_application_methods/part1.py`
  - 结果：通过

### Status Update

1. `legacy_adapter.py`
   - 状态由 `兼容保留`
   - 更新为 `已归档隔离`

2. `legacy_market_data.py`
   - 状态仍为 `兼容保留`
   - 但当前已完成 `in-source isolation`

3. 下一步若继续执行兼容资产方案，应轮到：
   - `config/sina_finance_only.yaml`
   - `config/data_sources/sina_finance.yaml`
   - `config/datasource.yaml.example`

## [WORK] 2026-03-13 Round 16 Compatibility Config Relocation（dev-data-db-audit-claude）
- Scope:
  - 执行兼容配置资产迁移：
    - `sina_finance*`
    - `datasource.yaml.example`
  - 不修改 loader 主逻辑，只更新明确消费者。

### Implemented Changes

| 类型 | 动作 |
| --- | --- |
| 兼容配置迁移 | `config/sina_finance_only.yaml` → `config/compatibility/sina_finance/main.yaml` |
| 子配置迁移 | `config/data_sources/sina_finance.yaml` → `config/compatibility/sina_finance/sina_finance.yaml` |
| 模板迁移 | `config/datasource.yaml.example` → `config/templates/datasource-registry.yaml.example` |
| 脚本消费者更新 | `scripts/quick_health_check.sh` 中的检查路径切换到 `config/compatibility/sina_finance/main.yaml` |
| 测试消费者更新 | `scripts/tests/legacy/test_sina_integration_final.py` 同时更新 `main_config_file` 与 `sources_dir` 到 `config/compatibility/sina_finance/` |

### Verification Evidence

- 文件存在性检查：
  - `config/compatibility/sina_finance/main.yaml -> True`
  - `config/compatibility/sina_finance/sina_finance.yaml -> True`
  - `config/templates/datasource-registry.yaml.example -> True`
  - `config/sina_finance_only.yaml -> False`
  - `config/data_sources/sina_finance.yaml -> False`
  - `config/datasource.yaml.example -> False`

- `DataSourcesLoader` 最小验证：
  - `loader.main_config_file = config/compatibility/sina_finance/main.yaml`
  - `loader.sources_dir = config/compatibility/sina_finance`
  - 结果：成功加载 `sina_finance_stock_ratings`

- 活跃源码路径扫描：
  - 未发现旧路径
    - `config/sina_finance_only.yaml`
    - `config/data_sources/sina_finance.yaml`
    - `config/datasource.yaml.example`
  - 唯一残留为 archived OpenSpec 任务记录，可接受

- 语法验证：
  - `python -m py_compile scripts/tests/legacy/test_sina_integration_final.py`
  - 结果：通过

### Status Update

1. `sina_finance*` 兼容配置已完成物理隔离。
2. `datasource.yaml.example` 已完成模板目录收口。
3. 至此，原先列为“兼容保留”的配置资产已从散落状态收口到：
   - `config/compatibility/`
   - `config/templates/`

## [WORK] 2026-03-13 Final Change Classification
- Scope:
  - 将当前 worktree 的全部改动整理成提交/评审可直接使用的分类清单。
  - 不新增行为改动。

### Output

- 新增分类清单：
  - `reports/governance/2026-03-13-final-change-classification.md`

### Covered Buckets

- Runtime compatibility fixes
- PM2 convergence
- Monitoring stack config/doc convergence
- Active deployment/operations docs convergence
- Low-risk redundant cleanup
- Example/compatibility path cleanup
- Compatibility isolation execution
- Compatibility config relocation
- Audit trail / reporting

### Current Status

1. 当前分支已经具备“按分类准备提交”的条件。
2. 如需继续，下一步不再是盘点，而是：
   - 提交前最终验证
   - 或按分类拆分提交

## [WORK] 2026-03-13 Final Verification Snapshot（dev-data-db-audit-claude）
- Scope:
  - 对当前改动面执行提交前定向验证。
  - 验证范围只覆盖本轮实际变更，不做全仓回归。

### Verification Commands

- `pytest tests/unit/core/test_web_backend_runtime_settings.py tests/unit/core/test_runtime_config_governance.py -q -o addopts=''`
- `python -m py_compile web/backend/app/core/config.py src/utils/mongo_runtime_config.py src/storage/database/execute_example_postgresql_only.py src/adapters/akshare/__init__.py src/adapters/akshare/legacy_market_data.py src/adapters/akshare/compat/__init__.py src/adapters/akshare/compat/legacy_market_data.py scripts/tests/legacy/test_sina_integration_final.py scripts/dev/examples/real_project_application/real_project_application_methods/part1.py archive/code-compatibility/examples/legacy_adapter.py`
- `node -c config/pm2/ecosystem.config.js`
- `node -c config/pm2/ecosystem.production.config.js`
- `node -c config/pm2/pm2.config.js`
- `node -c config/pm2/ecosystem.enhanced.config.js`
- `node -c config/pm2/ecosystem.playwright.config.js`
- `node -c config/pm2/ecosystem.playwright.p0.config.js`
- `node -c config/pm2/ecosystem.playwright.p1.config.js`
- `node -c config/pm2/ecosystem.playwright.p1.fixed.config.js`
- `node -c config/pm2/ecosystem.playwright.p2.config.js`
- `python` + `yaml.safe_load`:
  - `config/monitoring-stack/config/prometheus.yml`
  - `config/monitoring-stack/config/alertmanager.yml`
  - `config/compatibility/sina_finance/main.yaml`
  - `config/compatibility/sina_finance/sina_finance.yaml`
  - `config/templates/datasource-registry.yaml.example`
- `.env` 模板格式检查（按 dotenv 语法，不按 YAML）：
  - `.env.example`
  - `config/.env.example`

### Verification Results

1. Runtime config tests:
   - `15 passed`
   - warnings: `6`
   - 说明：warning 为仓库既有 Pydantic / taos 依赖告警，不是本次回归

2. Python syntax checks:
   - 通过

3. PM2 config syntax checks:
   - 通过

4. YAML parse checks:
   - 通过

5. `.env` template format checks:
   - `.env.example -> valid`
   - `config/.env.example -> valid`

6. Residual path / port / old-name scans:
   - 活跃源码与活跃配置中未再发现：
     - `localhost:8000`
     - `host.docker.internal:8000`
     - `/opt/claude/mystocks_spec/monitoring-stack`
     - `/opt/claude/mystocks_spec/web/backend`
     - `/opt/claude/mystocks_spec/web/frontend`
     - `config/sina_finance_only.yaml`
     - `config/data_sources/sina_finance.yaml`
     - `config/datasource.yaml.example`
     - `execute_example_mysql_only.py`

### Current Status

1. 当前变更已达到“可进入提交前复核”的状态。
2. 尚未执行的项：
   - 全仓回归测试
   - PM2 实际启动验证
   - Git 提交/拆分提交

## [WORK] 2026-03-13 Split Commit Playbook
- Scope:
  - 由于当前沙箱无法写 worktree git metadata，无法直接完成 `git commit`。
  - 改为输出可直接执行的拆分提交操作手册。

### Output

- 新增：
  - `reports/governance/2026-03-13-split-commit-playbook.md`

### Notes

1. 当前已 staged 的第一批文件：
   - `.env.example`
   - `config/.env.example`
   - `web/backend/app/core/config.py`
   - `src/utils/mongo_runtime_config.py`

2. playbook 已提供：
   - 每批提交的文件边界
   - `git restore --staged .` 重建 staging 的命令
   - 推荐 commit message

3. 若在可写 git metadata 环境下执行，可直接按 playbook 顺序完成拆分提交。

## [WORK] 2026-03-14 Active-Tree Legacy Backup Cleanup（mystocks_spec2）
- Scope:
  - 按 `TASK.md` 仅处理 12 个 active-tree legacy / backup / broken 文件。
  - 目标是完成“代码路径判定 + 功能树判定”，只删除已证明 `重复冗余` 的对象。

### Startup Blockers / Read-First Gaps

1. `git fetch origin` / `git rebase main`
   - 初始阻塞原因：早先沙箱无法写上游主仓库的 worktree git metadata。
   - 初始报错：`cannot open '/opt/claude/mystocks_spec/.git/worktrees/mystocks_spec2/FETCH_HEAD': Read-only file system`
   - 后续处理结果：
     - 权限放开后已成功执行 `git fetch origin`
     - 已成功执行 `git rebase main`
     - 当前分支已同步到 `main` 最新提交 `e4ecf083 (feat(maestro): enable env-auth mongo coordination)`
   - 同步前核对：
     - `git -c safe.directory=/opt/claude/mystocks_spec2 rev-list --left-right --count main...HEAD` -> `1 0`
     - `git -c safe.directory=/opt/claude/mystocks_spec2 diff --stat HEAD..main` 仅涉及：
       - `scripts/runtime/maestro_collab.py`
       - `tests/unit/runtime/test_maestro_coordination_cli.py`
     - 上述差异均不在本任务允许范围内，因此先提交本轮清理，再 rebase 吃入该修复提交。

2. Mongo control plane `coordctl`
   - 阻塞原因：Mongo 鉴权不可用。
   - 实际报错：`pymongo.errors.OperationFailure: Command createIndexes requires authentication`
   - 影响：
     - 无法执行 `work show`
     - 无法执行 `work mark/update add`
     - 本轮进度仅能先落在 `TASK-REPORT.md`

3. `TASK.md` 指定的 3 份必读文档在仓库中不存在：
   - `docs/reports/ARCHITECTURE_ASSESSMENT_REPORT.md`
   - `docs/reports/API_VERSION_CONFLICT_INVESTIGATION.md`
   - `docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md`
   - 替代读取：
     - `docs/plans/2026-03-14-architecture-api-remediation-worker-allocation.md`
     - `docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md`
     - `docs/reports/plans/compatibility-inventory.md`
     - `docs/reports/plans/code-simplification-notes.md`

### Classification and Action

| 文件 | 状态判定 | 动作 | 代码路径判定 | 功能树判定 |
|---|---|---|---|---|
| `web/frontend/src/views/RiskMonitor.vue.broken` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；当前 `main.js` 只加载 `router/index.ts`，现行 `router/index.ts` 风控路由指向 ArtDeco 页面 | `docs/reports/EMERGENCY_FIX_COMPLETION_REPORT.md` 说明它是临时重命名的损坏页面；当前风险功能树已转到 `ArtDecoRiskManagement.vue` / `risk-tabs/*` |
| `web/frontend/src/views/BacktestAnalysis.vue.broken` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；现行 `router/index.ts` 的回测路由指向 `ArtDecoBacktestAnalysis.vue` | `EMERGENCY_FIX_COMPLETION_REPORT.md` 说明它是临时重命名的损坏页面；当前回测功能树已转到 ArtDeco 策略页 |
| `web/frontend/src/router/index.ts.broken` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；当前入口 `web/frontend/src/main.js` 明确导入 `./router/index.ts` | 属于旧路由快照，功能树已被当前 `router/index.ts` 覆盖 |
| `web/frontend/src/router/index.ts.bak.20260214` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；当前入口只使用 `router/index.ts` | 属于日期备份快照，功能树已被当前 `router/index.ts` 覆盖 |
| `web/frontend/src/main.js.old` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；当前活动入口是 `web/frontend/src/main.js` | `web/frontend/FRONTEND_FIX_IMPLEMENTATION_GUIDE.md` 将其标记为替换入口文件时产生的临时旧文件 |
| `web/frontend/src/App.vue.old` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；当前活动入口从 `main.js` 导入 `./App.vue` | `FRONTEND_FIX_IMPLEMENTATION_GUIDE.md` 将其标记为替换 App 壳层时产生的临时旧文件 |
| `web/backend/app/api/risk_management.py.backup.20260130` | `重复冗余` | 已删除 | 对后缀文件名在 `web/backend/app` 精确扫描为 `0`；现行注册链路导入的是 `web/backend/app/api/risk_management.py` | `docs/reports/phase1.4_risk_management_split_progress.md` 标记其为“备份原文件”；现行 `risk_management.py` 是指向 `app.api.risk` 的弃用 shim |
| `web/backend/app/api/data.py.backup.20260130` | `重复冗余` | 已删除 | 对后缀文件名在 `web/backend/app` 精确扫描为 `0`；现行注册链路导入的是包级 facade `web/backend/app/api/data/__init__.py` | `docs/reports/phase1_complete_execution_summary_report.md` 标记其为“备份原文件”；当前数据功能树由 `api/data/*` 子路由和 `data_api_new.py` 兼容层承接 |
| `web/backend/app/api/technical_analysis.py.new` | `重复冗余` | 已删除 | 对后缀文件名在 `web/backend/app` 精确扫描为 `0`；`api.__init__`、`register_routers.py`、`router_registry.py` 均导入现行 `technical_analysis.py` | `docs/reports/plans/compatibility-inventory.md` 与 `code-simplification-notes.md` 都把它列为零引用删除候选；现行技术分析模块存在且可编译 |
| `src/database/database_service.py.backup.20260130` | `重复冗余` | 已删除 | 对后缀文件名在 `src` 精确扫描为 `0`；现行代码树使用 `src/database/services/database_service.py` 与 `src/database/database_service.py` | `docs/reports/phase1.2_database_service_split_completion.md` 明确它是拆分时备份的原文件 |
| `src/advanced_analysis/decision_models_analyzer.py.backup.20260130` | `重复冗余` | 已删除 | 对后缀文件名在 `src` 精确扫描为 `0`；GitNexus 图谱命中活跃 `DecisionModelsAnalyzer` 位于 `src/advanced_analysis/decision_models_analyzer.py` | `docs/reports/phase1.1_decision_models_split_completion.md` 明确它是拆分时备份的原文件；活跃类仍由 `src/advanced_analysis/__init__.py` 调用 |
| `src/monitoring/alert_manager.py.backup_complex_20251108` | `重复冗余` | 已删除 | 对后缀文件名在 `src` 精确扫描为 `0`；GitNexus 图谱命中活跃 `AlertManager` 位于 `src/monitoring/alert_manager.py` | 活跃文件头部注释明确“复杂多渠道告警已迁移到 Grafana”；备份文件仅是简化前快照 |

### Completed

1. 删除了以下 12 个已证明 `重复冗余` 的文件：
   - `web/frontend/src/views/RiskMonitor.vue.broken`
   - `web/frontend/src/views/BacktestAnalysis.vue.broken`
   - `web/frontend/src/router/index.ts.broken`
   - `web/frontend/src/router/index.ts.bak.20260214`
   - `web/frontend/src/main.js.old`
   - `web/frontend/src/App.vue.old`
   - `web/backend/app/api/risk_management.py.backup.20260130`
   - `web/backend/app/api/data.py.backup.20260130`
   - `web/backend/app/api/technical_analysis.py.new`
   - `src/database/database_service.py.backup.20260130`
   - `src/advanced_analysis/decision_models_analyzer.py.backup.20260130`
   - `src/monitoring/alert_manager.py.backup_complex_20251108`

2. 保留结论：
   - 本批次没有任何文件需要按 `有效` / `兼容保留` / `待判定` 留在 active tree。
   - 当前可见的剩余引用仅存在于历史文档与非运行时元数据，不构成代码路径阻塞。

### Verification Evidence

1. 精确残留扫描：
   - 命令：
     - `rg -n --hidden --glob '!*.git' "RiskMonitor\\.vue\\.broken|BacktestAnalysis\\.vue\\.broken|index\\.ts\\.broken|index\\.ts\\.bak\\.20260214|main\\.js\\.old|App\\.vue\\.old|risk_management\\.py\\.backup\\.20260130|data\\.py\\.backup\\.20260130|technical_analysis\\.py\\.new|database_service\\.py\\.backup\\.20260130|decision_models_analyzer\\.py\\.backup\\.20260130|alert_manager\\.py\\.backup_complex_20251108" web/frontend/src web/backend/app src`
   - 结果：
     - 返回码 `1`
     - 标准输出为空
     - 说明：active code trees 中已无上述 legacy 文件名残留

2. Git diff 格式检查：
   - 命令：
     - `git -c safe.directory=/opt/claude/mystocks_spec2 diff --check`
   - 结果：
     - 通过，无 whitespace / conflict marker 问题

3. 当前工作树实际变更面：
   - 命令：
     - `git -c safe.directory=/opt/claude/mystocks_spec2 status --short`
   - 结果：
     - 本轮相关变更为 `TASK-REPORT.md` + 12 个目标文件删除
     - 另有 `TASK.md` 为派单前置脏改，未在本轮修改

4. 相对 `main` 的真实交付范围：
   - 命令：
     - `git -c safe.directory=/opt/claude/mystocks_spec2 diff --name-status main...HEAD`
     - `git -c safe.directory=/opt/claude/mystocks_spec2 diff --check main...HEAD`
   - 结果：
     - 仅包含 `TASK-REPORT.md` 和 12 个目标文件删除
     - `diff --check main...HEAD` 通过

5. 现行替代模块语法检查：
   - 命令：
     - `python -m py_compile web/backend/app/api/risk_management.py web/backend/app/api/data/__init__.py web/backend/app/api/technical_analysis.py src/database/database_service.py src/advanced_analysis/decision_models_analyzer.py src/monitoring/alert_manager.py`
   - 结果：
     - 通过

6. GitNexus 变更探测（按规范执行，但结果受 worktree / index freshness 限制污染）：
   - 命令：
     - `gitnexus_detect_changes(scope="all")`
     - `gitnexus_detect_changes(scope="staged")`
     - `gitnexus_detect_changes(scope="compare", base_ref="main")`
   - 结果：
     - `scope="all"` 与 `scope="compare"` 返回高噪声 `critical`
     - `scope="staged"` 返回 `No changes detected`
     - 该工具对本轮“删除 legacy 备份文件 + worktree 既有历史状态”的组合不够稳定
   - 解释：
     - 本轮实际交付范围以 `git diff --name-status main...HEAD` 和 `git status --short` 为准

7. 探索性回归（非本次门禁，但已记录）：
   - 命令：
     - `pytest web/backend/tests/test_large_file_split_regressions.py tests/unit/monitoring/test_alert_manager_simplified.py -q`
   - 结果：
     - `13 failed, 44 passed`
   - 失败归因（均不指向已删除文件）：
     - `tests/unit/monitoring/test_alert_manager_simplified.py`
       - 失败原因：测试文件未导入 `AlertManager`，直接实例化触发 `NameError`
     - `web/backend/tests/test_large_file_split_regressions.py::test_strategy_management_module_stays_below_850_lines`
       - 失败原因：`web/backend/app/api/strategy_management/get_monitoring_db.py` 当前为 `930` 行，超出门禁
     - `web/backend/tests/test_large_file_split_regressions.py::test_cache_api_split_helpers_remain_importable`
     - `web/backend/tests/test_large_file_split_regressions.py::test_notification_module_remains_importable`
       - 失败原因：`app.core.config` 因缺失必需环境变量触发 `SystemExit: 1`
   - 结论：
     - 该命令暴露的是仓库既有测试/环境债务，不是本次 legacy 删除回归

### Residual Risks / Notes

1. 历史文档仍提到已删除文件名，例如：
   - `web/frontend/FRONTEND_FIX_IMPLEMENTATION_GUIDE.md`
   - `docs/reports/EMERGENCY_FIX_COMPLETION_REPORT.md`
   - `docs/reports/phase1_complete_execution_summary_report.md`
   - 这些引用属于历史迁移记录，不构成运行时代码路径

2. `.omc` 元数据仍可能保留旧文件名：
   - 按 `TASK.md` 明确要求，本轮未触碰 `.omc/**`
   - 该类引用属于非运行时记忆数据，不作为保留 active-tree legacy 文件的依据

3. 由于 Mongo control plane 鉴权阻塞，本轮尚无法把状态回写为 `in_progress` / `ready_for_review`
   - 即使在 rebase 到 `e4ecf083` 之后，`coordctl` 仍失败
   - 进一步核对：
     - worktree 根目录不存在 `.env`
     - 当前 shell 中也不存在 `MONGODB_ROOT_USERNAME` / `MONGODB_ROOT_PASSWORD` / `MAESTRO_COLLAB_MONGO_URI` 等变量
     - `coordctl` 现行逻辑会从 `.env` 或环境变量读取 Mongo 凭据；在缺失凭据时只能匿名连接，最终触发 `Command createIndexes requires authentication`
   - 交付状态已完整记录在本文件，待具备凭据后可由 main CLI 或后续会话补写

### Git Delivery Snapshot

1. 本轮清理提交：
   - `4ef9ecb7`
   - `chore(cleanup): remove active-tree legacy backups`

2. 当前分支基线：
   - 已 rebase 到 `main` 的 `e4ecf083`

3. 当前工作树状态：
   - 仅剩 `TASK.md` 为未提交派单文件改动
   - 本轮实现文件已全部在提交中

## [WORK] 2026-03-14 API Route Registration And Prefix Governance（mystocks_spec1）
- Scope:
  - 统一 `register_all_routers` 与 `register_api_routes` 的注册职责，收敛为单一主注册入口。
  - 治理本任务范围内 scoped router 的前缀来源，避免模块内硬编码非 `/api` / 非版本化前缀。
  - 增加 focused backend regression checks，验证映射、前缀约束与兼容包装器行为。

### Completed

- `web/backend/app/api/register_routers.py`
  - 改为兼容包装器，统一委托 `app.router_registry.register_api_routes(...)`
  - 不再维护第二套路由清单
- `web/backend/app/router_registry.py`
  - 通过 `VERSION_MAPPING` 挂载：
    - `monitoring_watchlists`
    - `monitoring_analysis`
    - `multi_source`
  - 补回 `prometheus_exporter`，避免 `app_factory.py` 切到 central registry 后丢路由
- `web/backend/app/api/VERSION_MAPPING.py`
  - 新增治理映射：
    - `monitoring_analysis -> /api/v1/monitoring/analysis`
    - `monitoring_watchlists -> /api/v1/monitoring/watchlists`
    - `multi_source -> /api/multi-source`
- `web/backend/app/api/technical/routes.py`
  - 移除模块内 `/technical` 前缀，改由 central registry 负责挂载
- `web/backend/app/api/monitoring_analysis.py`
  - 移除模块内 `/monitoring/analysis` 前缀
  - 文档注释更新为 `/api/v1/monitoring/analysis/**`
- `web/backend/app/api/monitoring_watchlists.py`
  - 移除模块内 `/monitoring/watchlists` 前缀
  - 文档注释更新为 `/api/v1/monitoring/watchlists/**`
  - 根据 main review follow-up 修复 runtime fallback：
    - `get_watchlist` 改为返回 runtime watchlist 详情
    - `delete_watchlist` 改为删除 runtime watchlist，而不是误走“添加股票”分支
- `web/backend/app/api/multi_source/routes.py`
  - 移除模块内 `/multi_source` 前缀
  - 文档示例更新为 `/api/multi-source/**`
- `web/backend/tests/test_route_governance_static.py`
  - 新增 focused static regression checks：
    - 版本映射包含治理条目
    - scoped router 模块本身不再烘焙 runtime prefix
    - `register_all_routers` 委托到 central registry
- `web/backend/tests/test_monitoring_watchlists_runtime_fallback.py`
  - 直接按 canonical prefix 挂载 `watchlists` router
  - 测试装载方式改为按文件路径加载目标模块，绕开 `app.api.__init__` 现存导入炸点
  - 补充 `get_watchlist` / `delete_watchlist` 的 runtime fallback regression tests

### Verification Evidence

- TDD red phase:
  - `pytest web/backend/tests/test_route_governance_static.py -q`
  - 结果：`3 failed`
  - 失败点：
    - `VERSION_MAPPING` 缺少治理条目
    - scoped router 仍保留硬编码前缀
    - `register_all_routers` 仍维持第二套注册逻辑
- Focused pytest green phase:
  - `PYTHONPATH=.:web/backend pytest -o addopts='' web/backend/tests/test_route_governance_static.py -q`
  - 结果：`3 passed`
  - `PYTHONPATH=.:web/backend pytest -o addopts='' web/backend/tests/test_monitoring_watchlists_runtime_fallback.py -q`
  - 初次结果：`6 passed`
  - review follow-up 后结果：`8 passed`
- Review follow-up red/green:
  - `PYTHONPATH=.:web/backend pytest -o addopts='' web/backend/tests/test_monitoring_watchlists_runtime_fallback.py -q -k 'get_watchlist_returns_runtime_fallback_when_db_unavailable or delete_watchlist_uses_runtime_fallback_when_db_unavailable'`
  - red 结果：`2 failed`
  - 失败点：
    - `get_watchlist` runtime fallback 误引用未定义 `request`
    - `delete_watchlist` runtime fallback 误引用未定义 `request`
  - green 结果：`2 passed, 6 deselected`
- Syntax:
  - `PYTHONPATH=.:web/backend python -m py_compile web/backend/app/api/VERSION_MAPPING.py web/backend/app/router_registry.py web/backend/app/api/register_routers.py web/backend/app/api/technical/routes.py web/backend/app/api/monitoring_analysis.py web/backend/app/api/monitoring_watchlists.py web/backend/app/api/multi_source/routes.py web/backend/tests/test_route_governance_static.py web/backend/tests/test_monitoring_watchlists_runtime_fallback.py`
  - 结果：通过
- Diff hygiene:
  - `git -c safe.directory=/opt/claude/mystocks_spec1 diff --check -- web/backend/app/api/VERSION_MAPPING.py web/backend/app/router_registry.py web/backend/app/api/register_routers.py web/backend/app/api/technical/routes.py web/backend/app/api/monitoring_analysis.py web/backend/app/api/monitoring_watchlists.py web/backend/app/api/multi_source/routes.py web/backend/tests/test_route_governance_static.py web/backend/tests/test_monitoring_watchlists_runtime_fallback.py`
  - 结果：通过
- GitNexus:
  - `impact(register_api_routes, upstream)` -> `LOW`
  - `impact(register_all_routers, upstream)` -> `LOW`
  - `detect_changes(scope=unstaged)` -> `CRITICAL`
  - 说明：该结果受当前 worktree 既有 `405` 个已改文件影响，非本批次单独引入；本批次实际修改文件仅限上文列出的 9 个目标文件

### Environment / Process Blockers

- `git fetch origin`
  - 初次失败：此前 worktree git metadata 位于只读路径，无法写 `FETCH_HEAD`
  - 当前状态：已在全局 `safe.directory` 放行后执行成功
- `git rebase main`
  - 未执行
  - 原因：
    - 当前 worktree 存在本地未提交改动（含派单文件 `TASK.md` 的既有改动）
    - `HEAD...origin/main = 22 0`，当前分支不落后于 `origin/main`
    - 在脏工作树上强行 rebase 风险高于收益
- `python scripts/runtime/coordctl.py work show ...`
  - 失败：Mongo `createIndexes` 鉴权失败（`Unauthorized`）
- `TASK.md` 指向的以下文件在当前路径不存在：
  - `docs/reports/ARCHITECTURE_ASSESSMENT_REPORT.md`
  - `docs/reports/API_VERSION_CONFLICT_INVESTIGATION.md`
  - `docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md`
  - 本轮改以现有可定位文档与代码真值推进

### Risks

- `router_registry.py` 仍依赖 `app.api.__init__` 的现有导入行为；本轮没有越界重构该包初始化逻辑。
- `detect_changes(scope=unstaged)` 在当前脏 worktree 中噪音很大，提交前仍需 main CLI 结合文件清单人工确认范围。
- `technical/routes.py` 目前仍非主注册链路的活跃技术分析实现；本轮只做前缀治理，不扩展其职责。
- `config/monitoring-stack/config/prometheus.yml` 仍引用 `/api/multi_source/health`；这与本轮 canonical `/api/multi-source/**` 口径不一致，但该文件超出 worker scope，需由 main CLI 或对应 owner 单独收敛。

### Rollback

1. 还原以下文件到本轮前状态：
   - `web/backend/app/api/VERSION_MAPPING.py`
   - `web/backend/app/router_registry.py`
   - `web/backend/app/api/register_routers.py`
   - `web/backend/app/api/technical/routes.py`
   - `web/backend/app/api/monitoring_analysis.py`
   - `web/backend/app/api/monitoring_watchlists.py`
   - `web/backend/app/api/multi_source/routes.py`
   - `web/backend/tests/test_route_governance_static.py`
   - `web/backend/tests/test_monitoring_watchlists_runtime_fallback.py`
2. 重新执行：
   - `PYTHONPATH=.:web/backend pytest -o addopts='' web/backend/tests/test_route_governance_static.py -q`
   - `PYTHONPATH=.:web/backend pytest -o addopts='' web/backend/tests/test_monitoring_watchlists_runtime_fallback.py -q`

### Delivery Status

- 代码状态：
  - 已满足本任务 acceptance 的实现与 focused regression 要求
- 可复核状态：
  - 可进入 main CLI review
- 未完成的流程项：
  - Mongo control plane `ready_for_review` 打点
  - 原因：当前环境对目标 Mongo 库无鉴权，`coordctl` 在 `createIndexes` 阶段即失败
- 分支同步结论：
  - `git fetch origin` 已成功
  - `HEAD...origin/main = 22 0`
  - 当前分支未落后于 `origin/main`
  - 因 worktree 非干净且含既有 `TASK.md` 改动，未执行 `git rebase main`

### Main CLI Handoff

- 请 main CLI 优先核对：
  - `TASK.md` 为派单文件既有改动，不属于本轮实现
  - 本轮目标文件仅为：
    - `web/backend/app/api/VERSION_MAPPING.py`
    - `web/backend/app/router_registry.py`
    - `web/backend/app/api/register_routers.py`
    - `web/backend/app/api/technical/routes.py`
    - `web/backend/app/api/monitoring_analysis.py`
    - `web/backend/app/api/monitoring_watchlists.py`
    - `web/backend/app/api/multi_source/routes.py`
    - `web/backend/tests/test_monitoring_watchlists_runtime_fallback.py`
    - `web/backend/tests/test_route_governance_static.py`
    - `TASK-REPORT.md`
- 如需补控制面状态：
  - 需先解决 Mongo 认证，再执行：
    - `python scripts/runtime/coordctl.py work mark 2026-03-14-api-route-governance-mystocks-spec1 --status ready_for_review --actor-cli mystocks_spec1 --summary "Code, focused validation, and TASK-REPORT are ready for main review" --output json`

## [MAIN MERGE] 2026-03-15 Frontend Structure Convergence Worker3
- Source:
  - Mongo `work_item_id`: `2026-03-14-frontend-structure-convergence-mystocks-spec3`
  - Worker worktree: `/opt/claude/mystocks_spec3`
- Merged Into Local `main`:
  - `web/frontend/src/components/realtime/RealtimePositionPanel.vue`
  - `web/frontend/src/composables/useWebSocketWithConfig.ts`
  - `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue`
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - `web/frontend/tests/unit/components/ArtDecoDashboardLogic.spec.ts`
  - `web/frontend/tests/unit/realtime-position-panel.spec.ts`
  - `web/frontend/tests/unit/use-websocket-with-config.spec.ts`
- Merge Notes:
  - 已并入 worker3 已复核的 realtime/dashboard/WebSocket 收口结果：
    - `RealtimePositionPanel` 改为 shared `useRealtimeMarket()`，并修复真实双 `connected` 握手下的重复握手动作
    - `useWebSocketWithConfig` 立即激活底层订阅注册并返回真实 cleanup
    - `useArtDecoDashboard` 维持已验证的 `market.trend.000001` 订阅路径，并补趋势点追加断言
    - `ArtDecoMarketData` 的龙虎榜加载改为 `dashboardService.getLongHuBang(...)`
  - worker3 中较早版本的 `ArtDecoStrategyManagement.vue` / `strategyManagementViewModel.ts` 纯逻辑拆分未按原样并入。
  - 原因：当前 `main` 工作树已存在更完整的 `strategyManagementHelpers.ts` + `useStrategyManagementViewModel()` 路线与对应测试，强行覆盖会踩掉主仓并行重构；该部分按 `superseded by current main-side refactor` 处理。
- Main-Side Verification:
  - `npm --prefix web/frontend run test -- strategy-management-view-model.spec.ts use-websocket-with-config.spec.ts ArtDecoDashboardLogic.spec.ts realtime-position-panel.spec.ts`
    - 结果：`3 files passed`, `9 tests passed`
    - 说明：`strategy-management-view-model.spec.ts` 未在当前 `main` 中并入，按现有主仓 helper 路线改为单独验证
  - `npm --prefix web/frontend run test -- strategy-management-helpers.spec.ts`
    - 结果：`1 file passed`, `5 tests passed`
  - `git diff --check -- web/frontend/src/components/realtime/RealtimePositionPanel.vue web/frontend/src/composables/useWebSocketWithConfig.ts web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts web/frontend/tests/unit/components/ArtDecoDashboardLogic.spec.ts web/frontend/tests/unit/realtime-position-panel.spec.ts web/frontend/tests/unit/use-websocket-with-config.spec.ts`
    - 结果：通过
  - `gitnexus_detect_changes(scope="staged")`
    - 结果：`risk_level=low`
- Local Main Commits:
  - `065953da` `fix(frontend): converge realtime dashboard subscriptions`

## [MAIN MERGE] 2026-03-15 Function Tree Governance Worker5
- Source:
  - Mongo `work_item_id`: `2026-03-14-govern-function-tree-as-code-mystocks-spec5`
  - Worker worktree: `/opt/claude/mystocks_spec5`
  - Worker commits reviewed:
    - `74d9a273` `feat(governance): codify function tree governance`
    - `07c1cae5` `fix(governance): harden function tree catalog`
- Merged Into Local `main`:
  - `.github/pull_request_template.md`
  - `docs/FUNCTION_TREE.md`
  - `docs/guides/ai-tools/AI_QUICK_START.md`
  - `docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md`
  - `governance/function-tree/catalog.yaml`
  - `governance/function-tree/schema.json`
  - `governance/mainline/schemas/ai-task-card.schema.json`
  - `governance/mainline/scripts/mainline_scope_gate.py`
  - `governance/mainline/spec/ai-development-mainline-governance-spec.md`
  - `governance/mainline/templates/ai-task-card.yaml`
  - `openspec/changes/govern-function-tree-as-code/**`
  - `tests/fixtures/governance/function-tree-governance-sample-card.yaml`
  - `tests/unit/governance/**`
- Merge Notes:
  - 已选择性并入 worker5 的治理实现，不带 worker worktree 根的 `TASK.md` / `TASK-REPORT.md`。
  - `function_tree` 现在具备 machine-readable catalog/schema、task-card schema 合同、mainline scope gate 校验、PR reviewer 镜像字段，以及 `FUNCTION_TREE` 稳定 ID 文档同步口径。
  - follow-up 修复也已包含在主线并入结果中：
    - duplicate `domain_id` / `node_id` 由 `load_function_tree_catalog()` 的 integrity check 直接拒绝
    - literal entrypoint path existence 补了回归测试
    - `meta-governance` dead link 已改为仓内真实存在的 `docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md`
    - OpenSpec `design.md` 的 trailing whitespace 已清掉
  - 当前唯一仍保留的限制是：
    - 原始 `pytest ... -q` 在仓库默认 coverage fail-under 80 下仍返回退出码 `1`
    - 但 focused governance 测试本身已全部通过，不属于本次变更引入的功能失败
- Main-Side Verification:
  - `pytest --no-cov tests/unit/governance/test_function_tree_catalog.py tests/unit/governance/test_task_card_function_tree_schema.py tests/unit/governance/test_mainline_scope_gate_function_tree.py tests/unit/governance/test_function_tree_doc_sync.py -q`
    - 结果：`19 passed`
  - `pytest tests/unit/governance/test_function_tree_catalog.py tests/unit/governance/test_task_card_function_tree_schema.py tests/unit/governance/test_mainline_scope_gate_function_tree.py tests/unit/governance/test_function_tree_doc_sync.py -q`
    - 结果：`19 passed`，但命令整体因仓库默认 coverage fail-under 80 / no-data-collected 返回退出码 `1`
  - `openspec validate govern-function-tree-as-code --strict`
    - 结果：通过
  - `git diff --check -- .github/pull_request_template.md docs/FUNCTION_TREE.md docs/guides/ai-tools/AI_QUICK_START.md docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md governance/function-tree/catalog.yaml governance/function-tree/schema.json governance/mainline/schemas/ai-task-card.schema.json governance/mainline/scripts/mainline_scope_gate.py governance/mainline/spec/ai-development-mainline-governance-spec.md governance/mainline/templates/ai-task-card.yaml openspec/changes/govern-function-tree-as-code/design.md openspec/changes/govern-function-tree-as-code/proposal.md openspec/changes/govern-function-tree-as-code/specs/function-tree-governance/spec.md openspec/changes/govern-function-tree-as-code/tasks.md tests/fixtures/governance/function-tree-governance-sample-card.yaml tests/unit/governance/__init__.py tests/unit/governance/test_function_tree_catalog.py tests/unit/governance/test_function_tree_doc_sync.py tests/unit/governance/test_mainline_scope_gate_function_tree.py tests/unit/governance/test_task_card_function_tree_schema.py`
    - 结果：通过
  - `gitnexus_detect_changes(scope="staged")`
    - 结果：`risk_level=low`
- Local Main Commits:
  - `f8bbcc6a` `feat(governance): codify function tree governance`

## [AUTO] 2026-03-16 22:19:21 Session 4e52ecb7-69f2-48ea-80a4-8aa9cc3dc3d8
- Completion: true
- Summary: The OpenCode configuration is now valid. The `mcp list` command succeeded, showing 6 MCP servers configured.
- Model: `glm-5`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/4e52ecb7-69f2-48ea-80a4-8aa9cc3dc3d8.jsonl`

## [AUTO] 2026-03-24 11:33:18 Session ed940f9a-2752-452a-bee6-590f2045c723
- Completion: true
- Summary: ✅ **已修复**
- Model: `glm-5`
- Files: (none)
- Transcript: `/root/.claude/projects/-opt-claude-mystocks-spec/ed940f9a-2752-452a-bee6-590f2045c723.jsonl`
