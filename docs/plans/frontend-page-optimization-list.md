# MyStocks 前端页面优化规划（修订版）

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**Historical Plan Version Snapshot**: V2.6（依据 2026-04-06 API status rule reconciliation 修订）
**Historical Plan Creation Date**: 2026-03-02
**Historical Plan Last Revision Snapshot**: 2026-04-06

## 0. 统计口径（先定义再统计）

### 0.1 口径 A（本清单采用）
- 优化范围: 业务主链页面 + Login
- 清单条目: **34**

### 0.2 口径 B（全路由参考）
- `router` 命名路由总数: **37**（含详情页与 404）
- 路由引用唯一页面组件: **35**（`src/views`）

### 0.3 本清单排除项（不在 34 条优化范围内）
- `/detail/graphics/:symbol`
- `/detail/news/:symbol`
- `/:pathMatch(.*)*`（NotFound）

---

## 1. 参考文档

- `docs/architecture/MENU_ARCHITECTURE_V3.2_ELITE.md`
- `docs/architecture/FRONTEND_OPTIMIZATION_IMPLEMENTATION_PLAN_V2.md`
- `docs/architecture/FRONTEND_OPTIMIZATION_STRATEGY_V3.md`（能力提取主策略）
- `reports/frontend-pages-audit-report.md`
- `reports/frontend-pages-cleanup-plan.md`
- `reports/frontend-directory-restructure-plan.md`
- `reports/frontend-pages-integration-analysis.md`

### 1.1 策略优先级
- 当 V2 清理策略与 V3 能力提取策略冲突时，**以 V3 为准**（避免误删高复用能力页）。

---

## 2. 前端现状（审计基线）

- 总扫描页面: 252
- 已接入页面: 35（路由引用 37 条，唯一组件 35）
- 未接入页面: 217
- 路由接入率: 35/252（13.9%）

---

## 3. 核心规范（修订后）

### 3.1 设计规范
- 风格: ArtDeco 精英风格
- 分辨率: **桌面优先（1280x720+），保留移动端基础可用（不追求功能完整等价）**
- 导航: 侧边栏 + 顶栏一致性
- 性能: 懒加载、分块加载、图表优化

### 3.2 路由与菜单 SSOT
- **router 是路由真值来源**（权限、组件映射、路径定义）。
- `MenuConfig` 是 UI 投影层（展示与分组）。
- router 与菜单不一致时，标记为 `navigation-debt`，单独治理。

### 3.3 API 使用规则（强制）
- 端点必须来源于后端注册路由或 OpenAPI 导出，禁止手工臆写。
- 文档中每个 API 字段应标注校验状态（`verified` / `pending`）。
- 关键端点清单必须显式区分“历史基线验证日期”和“后续 refresh 真相引用”；禁止再用单一 `last_verified_at` 同时承载首轮基线与后续刷新。
- CI/本地统一校验命令:
  `python scripts/dev/frontend_optimization_audit.py --repo-root . --strict --report-file reports/analysis/frontend-page-optimization-audit-report.md`
- 审计报告固定路径:
  `reports/analysis/frontend-page-optimization-audit-report.md`

### 3.4 端口真值来源
- `.env`（主） -> `web/PORTS.md`（规范） -> PM2 生效配置（运行时）
- 默认: 前端 `3020`，后端 `8020`

---

## 4. 测试与验收（双层门禁）

### 4.1 门禁层（阻塞）
```bash
bash scripts/run_e2e_pm2.sh
```

### 4.2 业务层（非阻塞但必报）
```bash
bash scripts/tests/test/run-comprehensive-tests.sh
```

### 4.3 结果判定
- 门禁层通过 + 结构性语法错误为 0 => 可运行
- 业务层必须报告: DOM 可见性、关键接口返回字段、前后端联动一致性
- 明确区分: 本次引入问题 vs 既有技术债

---

## 5. Phase 策略（口径 A: 34 条）

### Phase 0（前置治理）
- 低复用页面: 清理/归档
- 高复用页面: 能力提取（按 V3）

### Phase 1（6 页，P0/P1）
- Login、Dashboard、Market-Realtime、Market-Technical、Market-LHB、Data-Industry

### Phase 2（6 页）
- Data-Concept、Data-FundFlow、Data-Indicator、Watchlist-Manage、Watchlist-Signals、Watchlist-Screener

### Phase 3（12 页）
- Strategy 全域 + Trade 全域

### Phase 4（10 页）
- Risk 全域 + System 全域

---

## 6. 34 页优化清单（以 router 实际组件为准）

字段说明:
- `组件路径`: 相对 `src/views/`
- `数据状态`: `real` / `mixed` / `mock` / `placeholder`
- `API状态`: `verified` / `pending`；`docs/plans/2026-03-12-api-availability-matrix-draft.md` 只作为首轮历史基线来源，若后续 refresh artifact 更新当前真相，以更新日期更晚的 artifact 为准
- `备注`: 行内出现的 `127.0.0.1:81xx`、`localhost:8888` 等端口，均是带日期的历史验证证据，不是当前运行时端口真值；当前仓库默认端口真值仍以第 3.4 节为准，即 frontend `3020` / backend `8020`

| # | 页面 | 路径 | 组件路径（router 真值） | 优先级 | 数据状态 | API（当前） | API状态 | 备注 |
|---|---|---|---|---|---|---|---|---|
| 1 | Login | `/login` | `Login.vue` | P0 | real | `/api/v1/auth/login` | verified | 2026-03-13 已在当前 worktree backend `127.0.0.1:8124` 验证 form login 成功，返回 `data.token/token_type/user` 与 `authStore` 消费契约一致 |
| 2 | Dashboard | `/dashboard` | `artdeco-pages/ArtDecoDashboard.vue` | P0 | mixed | `primary-family: /api/v1/market/quotes + /api/akshare/market/fund-flow/hsgt-summary + /api/akshare/market/fund-flow/big-deal + /api/v1/market/kline + /api/v2/market/sector/fund-flow ; stats-family: /health + /api/v1/strategy/strategies + /api/v1/trade/positions` | verified | 2026-03-13 当前 worktree backend `127.0.0.1:8126` 已验证主链与 stats 链均可达；`sector/fund-flow` 从 `500` 收口到 `200`，前端现有 industry mapper 可提取 12 条热区行；AKShare 资金流家族在登录态 Bearer token 下返回 `200`。`DealingRoom` 仅保留为历史兼容别名，当前 canonical route truth 为 `/dashboard`。 |
| 3 | Market-Realtime | `/market/realtime` | `artdeco-pages/market-tabs/MarketRealtimeTab.vue` | P0 | mixed | `/api/v1/market/quotes` | verified | 2026-03-13 已在当前 worktree backend `127.0.0.1:8120` 验证真实返回与字段映射 |
| 4 | Market-Technical | `/market/technical` | `artdeco-pages/market-tabs/MarketKLineTab.vue` | P0 | mixed | `/api/v1/market/kline` | verified | 2026-03-13 页级请求、实时返回与字段映射已核 |
| 5 | Market-LHB | `/market/lhb` | `artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` | P1 | mixed | `/api/v2/market/lhb` | verified | 2026-03-13 组件自取数链、实时返回与字段映射已核 |
| 6 | Data-Industry | `/data/industry` | `artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` | P1 | real | `/api/v2/market/sector/fund-flow` | verified | 2026-03-13 页级请求、实时返回与字段映射已核 |
| 7 | Data-Concept | `/data/concept` | `artdeco-pages/market-tabs/MarketConceptTab.vue` | P1 | mixed | `/api/v2/market/sector/fund-flow?sector_type=概念` | verified | 2026-03-13 页级请求、实时返回与字段映射已核 |
| 8 | Data-FundFlow | `/data/fund-flow` | `artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` | P1 | mixed | `/api/akshare/market/fund-flow/hsgt-summary` + `/api/akshare/market/fund-flow/big-deal` | verified | 2026-03-13 已在当前 worktree backend `127.0.0.1:8121` 验证真实返回与字段映射 |
| 9 | Data-Indicator | `/data/indicator` | `artdeco-pages/ArtDecoDataAnalysis.vue` | P1 | mixed | `read-family: /api/v1/indicators/registry + /api/v1/data/stocks/basic` | verified | 2026-03-14 当前 worktree backend `127.0.0.1:8132` 已验证指标注册表与选股股票池读链均返回 `200`；页面 composable 已切到真实注册表/股票池数据，公式编辑器仍为占位但不阻塞主链 |
| 10 | Watchlist-Manage | `/watchlist/manage` | `artdeco-pages/stock-management-tabs/WatchlistManager.vue` | P1 | mixed | `read-family: /api/v1/monitoring/watchlists + /api/v1/monitoring/watchlists/{id}/stocks ; write-family: /api/v1/monitoring/watchlists + /api/v1/monitoring/watchlists/{id}/stocks + /api/v1/monitoring/watchlists/{id}/stocks/{code}` | verified | 2026-03-14 当前 worktree backend `127.0.0.1:8130` 已验证 create/read/add/remove 全链返回 `200`；路由直连页已补本地读链与 create/remove 动作，import/export 保留本地 JSON 工具但不再阻塞主链 |
| 11 | Watchlist-Signals | `/watchlist/signals` | `artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | P1 | real | `/api/v1/trade/signals` | verified | 2026-03-12 runtime probe + 页面字段映射已核 |
| 12 | Watchlist-Screener | `/watchlist/screener` | `stocks/Screener.vue` | P1 | mixed | `/api/v1/data/stocks/basic` | verified | 2026-03-14 当前 worktree backend `127.0.0.1:8132` 已验证股票池读链返回 `200`；页面已改为消费真实 `price/change_pct/volume/turnover/pe/market_cap` payload |
| 13 | Strategy-Repo | `/strategy/repo` | `artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` | P1 | real | `/api/v1/strategy/strategies` | verified | 2026-03-13 已在当前 worktree backend `127.0.0.1:8122` 验证 list/create/update/delete 闭环；生命周期按钮继续本地禁用 |
| 14 | Strategy-Parameters | `/strategy/parameters` | `artdeco-pages/strategy-tabs/StrategyParametersTab.vue` | P1 | real | `/api/v1/strategy/strategies` | verified | 2026-03-12 runtime probe + 页面字段映射已核 |
| 15 | Strategy-Signals | `/strategy/signals` | `artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | P1 | real | `/api/v1/trade/signals` | verified | 2026-03-12 runtime probe + 页面字段映射已核 |
| 16 | Strategy-Backtest | `/strategy/backtest` | `artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` | P1 | real | `read/write-family: /api/v1/strategy/backtest/run + /api/v1/strategy/backtest/status/{id} + /api/v1/strategy/backtest/results/{id}` | verified | 2026-03-13 当前 worktree backend `127.0.0.1:8128` 已验证 run/status/result 主链均返回 `200`；前端缺失的 backtest view model/helpers 已补齐，页面消费所需 `backtest_id/status/performance/start_date/end_date` 已可提取 |
| 17 | Strategy-GPU | `/strategy/gpu` | `strategy/BacktestGPU.vue` | P2 | mixed | `read-family: /api/gpu/status + /api/gpu/performance` | verified | 2026-03-14 当前 worktree backend `127.0.0.1:8131` 已验证 GPU 状态与性能读链返回 `200`；页面 composable 已优先读取真实 GPU payload，benchmark/reset 仍为本地模拟动作但不阻塞主读链 |
| 18 | Strategy-Opt | `/strategy/opt` | `artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue` | P2 | real | `/api/v1/strategy/strategies` | verified | 2026-03-14 已确认页面主链只读策略列表；PM2 backend `http://localhost:8888` 返回 `200` 且 `items=[]` 时，页面保持 `REAL` 数据源并显示空态，不回退 mock |
| 19 | Strategy-Pos | `/strategy/pos` | `artdeco-pages/stock-management-tabs/PortfolioMonitor.vue` | P2 | mixed | `/api/v1/trade/positions` | verified | 2026-03-14 路由直连页已补本地自取数；PM2 backend `http://localhost:8888` 的真实持仓 payload 可映射到持仓行与统计卡片 |
| 20 | Trade-Positions | `/trade/positions` | `artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` | P1 | real | `/api/v1/trade/positions` | verified | 2026-03-12 runtime probe + 持仓字段映射已核 |
| 21 | Trade-Terminal | `/trade/terminal` | `TradingDashboard.vue` | P1 | mixed | `read-family: /api/trading/status + /api/trading/strategies/performance + /api/trading/market/snapshot + /api/trading/risk/metrics ; write-family: /api/trading/start + /api/trading/stop + /api/trading/strategies/add + /api/trading/strategies/{name}` | verified | 2026-03-14 PM2 backend `http://localhost:8888` 已验证四条读链与四条写链均可达；页面写动作已接入 fresh CSRF helper，不再因为裸 axios 缺 token 而失败 |
| 22 | Trade-Signals | `/trade/signals` | `artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` | P1 | real | `/api/v1/trade/signals` | verified | 2026-03-12 runtime probe + 页面字段映射已核 |
| 23 | Trade-Portfolio | `/trade/portfolio` | `artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | P1 | real | `/api/v1/trade/positions` | verified | 2026-03-14 已用 PM2 backend `http://localhost:8888` 的真实持仓 payload 验证 `PortfolioOverviewTab` 映射；`total_assets/today_pnl/positions[]` 可消费，派生的绩效归因与再平衡建议可生成 |
| 24 | Trade-History | `/trade/history` | `artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` | P1 | real | `/api/v1/trade/trades` | verified | 2026-03-14 已用 PM2 backend `http://localhost:8888` 的真实成交记录 payload 验证 `tradingDataTransform.ts` 映射；`trade_id/trade_time/symbol/direction/price/quantity/amount/commission` 可消费 |
| 25 | Risk-Management | `/risk/management` | `artdeco-pages/ArtDecoRiskManagement.vue` | P1 | mixed | `/api/v1/trade/positions` | verified | 2026-03-14 页面已接入 `ArtDecoPageTemplate` 的真实 positions 读链；`riskManagementData.ts` 可把 live payload 映射为头部风险指标与风险预警列表 |
| 26 | Risk-Overview | `/risk/overview` | `artdeco-pages/risk-tabs/RiskOverviewTab.vue` | P1 | mixed | `/api/v1/monitoring/alert-rules` | verified | 2026-03-13 当前 worktree backend `127.0.0.1:8128` 已验证规则读链返回 `200`；页面规则表对 `rule_name/rule_type/symbol/is_active/priority` 的消费口径成立，其他 tab 仍保留静态展示但不阻塞主读链 |
| 27 | Risk-PnL | `/risk/pnl` | `artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | P1 | real | `/api/v1/trade/positions` | verified | 与 `Trade-Portfolio` 复用同一 `PortfolioOverviewTab` 和同一 live payload 映射；2026-03-14 已验证真实持仓数据可消费 |
| 28 | Risk-StopLoss | `/risk/stop-loss` | `artdeco-pages/risk-tabs/StopLossMonitorTab.vue` | P1 | mixed | `read-family: /api/v1/monitoring/watchlists + /api/v1/monitoring/watchlists/{id}/stocks + /api/v1/market/quotes` | verified | 2026-03-13 当前 worktree backend `127.0.0.1:8125` 已验证三段读链均可达；页面已改为 watchlist -> stocks -> quotes 组合映射，监控库不可用时在 `TESTING/DEVELOPMENT_MODE` 下走 runtime fallback |
| 29 | Risk-Alerts | `/risk/alerts` | `artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` | P1 | mixed | `read-family: /api/v1/monitoring/alert-rules + /api/v1/monitoring/alerts` | verified | 2026-03-13 当前 worktree backend `127.0.0.1:8127` 已验证两条读链均返回 `200`；`alert-rules` 已对齐 `UnifiedResponse`，监控库不可用时在 `TESTING/DEVELOPMENT_MODE` 下走 runtime fallback |
| 30 | Risk-News | `/risk/news` | `artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` | P2 | mixed | `/api/announcement/list` | verified | 2026-03-12 页面真实请求已核，旧 `/api/v1/announcement` 口径作废 |
| 31 | System-Config | `/system/config` | `views/system/Settings.vue` | P2 | mixed | `read/write-family: general /api/v1/system/settings/general ; monitor-family: /api/health/detailed + /api/health ; routed section owners: security /api/v1/system/settings/security ; datasource /api/v1/data-sources/config/* ; notification /api/notification/preferences` | verified | 2026-04-06 活跃路由已切到 canonical `Settings.vue`；页面“保存系统设置”直接写入 general section 后端真相，`ArtDecoSystemSettings.vue` 仅保留为薄包装层；整体设置真相保持按 section owner 拆分，不引入单体统一 settings 存储 |
| 32 | System-Health | `/system/health` | `artdeco-pages/system-tabs/SystemHealthTab.vue` | P2 | mixed | `/health` | verified | |
| 33 | System-API | `/system/api` | `artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` | P2 | mixed | `primary: /health ; export: /api/health/detailed` | verified | 2026-03-13 已在当前 worktree backend `127.0.0.1:8124` 验证主加载与导出链均可消费；导出链以 `warning` 状态返回非阻塞脚本告警 |
| 34 | System-Data | `/system/data` | `artdeco-pages/system-tabs/ArtDecoDataManagement.vue` | P2 | mixed | `read: /api/v1/data-sources/config/ ; write-family: /api/v1/data-sources/config/batch` | verified | 2026-03-13 前端已对齐 `endpoints[]` 读模型与 `batch.operations[].updates.status` 写模型；启用/禁用分别映射到 `active` / `maintenance` |

---

## 7. 首轮核验证据清单（多源证据）

`historical first-round baseline verified_at: 2026-03-13`

说明:
- 本节是首轮核验历史基线，不是当前主线的统一“最新验证时间”。
- 2026-04-05 的 PM2/proxy refresh 与 2026-04-06 的 System-Config sectioned contract closeout，已在 `reports/analysis/frontend-mainline-overall-closeout.md` 与 `reports/analysis/frontend-mainline-overall-status.json` 单独更新为当前真相。
- 读取本清单时，应把本节视为“首轮 verified 来源说明”，而不是覆盖后续 refresh 的最新口径。

页面级 `verified` 已支撑的主接口:
- `/api/v1/market/quotes`
  - 支撑页面：`Market-Realtime`、`Risk-StopLoss`
- `/api/akshare/market/fund-flow/hsgt-summary` + `/api/akshare/market/fund-flow/big-deal`
  - 支撑页面：`Data-FundFlow`
- `/api/v2/market/lhb`
  - 支撑页面：`Market-LHB`
- `/api/v1/market/kline`
  - 支撑页面：`Market-Technical`
- `/api/v2/market/sector/fund-flow`
  - 支撑页面：`Data-Industry`
- `/api/v2/market/sector/fund-flow?sector_type=概念`
  - 支撑页面：`Data-Concept`
- `/api/v1/trade/signals`
  - 支撑页面：`Watchlist-Signals`、`Strategy-Signals`、`Trade-Signals`
- `/api/v1/strategy/strategies`
  - 支撑页面：`Strategy-Repo`、`Strategy-Parameters`
- `/api/v1/strategy/backtest/run` + `/api/v1/strategy/backtest/status/{id}` + `/api/v1/strategy/backtest/results/{id}`
  - 支撑页面：`Strategy-Backtest`
- `/api/v1/monitoring/watchlists` + `/api/v1/monitoring/watchlists/{id}/stocks`
  - 支撑页面：`Watchlist-Manage`
- `/api/v1/monitoring/watchlists` + `/api/v1/monitoring/watchlists/{id}/stocks` + `/api/v1/monitoring/watchlists/{id}/stocks/{code}`
  - 支撑页面：`Watchlist-Manage`
- `/api/health/detailed` + `/api/health`
  - 支撑页面：`System-Config`
- `/api/v1/data-sources/config/` + `/api/v1/data-sources/config/batch`
  - 支撑页面：`System-Data`
- `/health` + `/api/health/detailed`
  - 支撑页面：`System-API`
- `/api/v1/trade/positions`
  - 支撑页面：`Trade-Positions`、`Trade-Portfolio`、`Risk-PnL`、`Strategy-Pos`、`Risk-Management`
- `/api/v1/trade/trades`
  - 支撑页面：`Trade-History`
- `/api/announcement/list`
  - 支撑页面：`Risk-News`
- `/api/v1/monitoring/alert-rules` + `/api/v1/monitoring/alerts`
  - 支撑页面：`Risk-Alerts`
- `/api/v1/monitoring/alert-rules`
  - 支撑页面：`Risk-Overview`
- `/api/v1/monitoring/watchlists` + `/api/v1/monitoring/watchlists/{id}/stocks` + `/api/v1/market/quotes`
  - 支撑页面：`Risk-StopLoss`
- `/health`
  - 支撑页面：`System-Health`

活跃清单中当前已无“路径已证实存在但页面仍保持 `pending`”的接口。
旧 `/api/v1/risk/alerts` 仅作为已证伪旧口径保留在下方历史纠偏章节，不能再视为当前 pending 项。

已证伪或需修正的旧口径:
- `Market-Realtime`
  - 旧错误页面口径：`/api/v1/data/markets/overview`
  - 当前页面口径：`/api/v1/market/quotes`
  - 当前状态：已在当前 worktree backend `127.0.0.1:8120` 验证通过
- `Risk-News`
  - 旧口径：`/api/v1/announcement`
  - 页面真实请求：`/api/announcement/list`
- `Market-LHB`
  - 旧口径：`/api/data/lhb`
  - 当前已核实：`/api/v2/market/lhb`
- `Data-Industry` / `Data-Concept` / `Data-FundFlow`
  - 旧口径混用：`/api/akshare/market/*`、`/api/akshare_market/*`
  - 当前真实页面口径已分化：
    - `Data-Industry` -> `/api/v2/market/sector/fund-flow`
    - `Data-Concept` -> 当前错误路径 `/api/v1/market/concept`，候选替代 `/api/v2/market/sector/fund-flow?sector_type=概念`
    - `Data-FundFlow` -> `/api/akshare/market/fund-flow/hsgt-summary` + `/api/akshare/market/fund-flow/big-deal`
- `System-Data`
  - 读路径已证实：`/api/v1/data-sources/config/`
  - 写路径家族已证实：`/api/v1/data-sources/config/batch`
  - 当前页面语义：
    - `启用` -> batch `updates.status = active`
    - `禁用` -> batch `updates.status = maintenance`
- `Risk-StopLoss`
  - 旧错误口径：只读取 `/api/v1/monitoring/watchlists`
  - 当前页面真实链路：
    - `/api/v1/monitoring/watchlists`
    - `/api/v1/monitoring/watchlists/{id}/stocks`
    - `/api/v1/market/quotes`
- `Risk-Alerts`
  - 旧错误口径：`/api/v1/risk/alerts`
  - 当前页面真实链路：
    - `/api/v1/monitoring/alert-rules`
    - `/api/v1/monitoring/alerts`
- `Risk-Overview`
  - 旧错误口径：`/api/v1/risk/*`
  - 当前页面真实链路：
    - `/api/v1/monitoring/alert-rules`
- `System-Config`
  - 旧错误口径：`/api/system/*`
  - 当前页面真实链路：
    - `/api/health/detailed`
    - `/api/health`

> 说明: 自 2026-03-12 起，本清单不再仅依赖 `scripts/dev/frontend_optimization_audit.py` 的路径匹配结果；`verified` 必须同时满足“页面真实请求可定位 + 路径存在/可达 + 字段可消费”。
> `Strategy-Repo` 的本轮验证口径补充：在 `TESTING=true` + `DEVELOPMENT_MODE=true` 的当前 worktree backend 上，`/api/v1/strategy/strategies` 已通过 runtime fallback 证明 CRUD 与 `UnifiedResponse` 契约闭环；缺失的 lifecycle 路径仍保持 UI 侧禁用，不再阻塞主 CRUD 流。
> `Strategy-Backtest` 的本轮验证口径补充：在 `TESTING=true` + `DEVELOPMENT_MODE=true` 的当前 worktree backend 上，`/api/v1/strategy/backtest/run`、`/status/{id}`、`/results/{id}` 已通过 runtime fallback 闭环；前端本地缺失的 `backtestAnalysisViewModel.ts`、`backtestAnalysisHelpers.ts`、`backtestContract.ts` 也已补回，因此当前页面不再卡在缺模块或后端环境门禁。
> `System-Config` 的本轮验证口径补充：活跃路由当前落在 `web/frontend/src/views/system/Settings.vue`，并通过 `/api/v1/system/settings/general` 读取与写入 general section；健康监控仍读取 `/api/health/detailed` 和 `/api/health`。更宽口径的系统设置真相仍按 section owner 拆分：security -> `/api/v1/system/settings/security`，datasource -> `/api/v1/data-sources/config/*`，notification -> `/api/notification/preferences`。本轮收口的结论不是“补出一个单体统一 `/api/system/settings`”，而是把页面从本地草稿退化态切换到受治理的分段后端契约。
> `Risk-Overview` 的本轮验证口径补充：页面真实请求只有 `/api/v1/monitoring/alert-rules`；规则表页签的字段消费已在当前 worktree backend 上核证，其余 overview/alerts 页签保持静态展示，不构成主读链 blocker。
> `Risk-Alerts` 的本轮验证口径补充：在 `TESTING=true` + `DEVELOPMENT_MODE=true` 的当前 worktree backend 上，`/api/v1/monitoring/alert-rules` 与 `/api/v1/monitoring/alerts` 会在监控 DB 不可用时降级到 runtime fallback；其中 `alert-rules` 已补齐 `UnifiedResponse` 契约，与 `useArtDecoApi()` 的读链一致。
> `Risk-StopLoss` 的本轮验证口径补充：在 `TESTING=true` + `DEVELOPMENT_MODE=true` 的当前 worktree backend 上，watchlist 读接口会在监控 DB 不可用时降级到 runtime fallback；页面再使用 `/api/v1/market/quotes` 补全 `current_price`，从而闭环 `symbol/current_price/stop_price/distance`。
>
> 运行时备注（2026-03-13）: `localhost:8020` 当前由 PM2 主仓库实例 `/opt/claude/mystocks_spec/web/backend` 提供，不是本 worktree `/opt/claude/mystocks_spec-api-availability/web/backend`。本轮 `Market-Realtime` 的后端改动是通过当前 worktree backend `127.0.0.1:8120` + `DEVELOPMENT_MODE=true` 单独验证的。

---

## 8. 历史进度快照（2026-03-03 计划基线）

> 以下计数是 2026-03-03 这份执行清单的历史计划快照，不是 2026-04-06 当前 frontend mainline 的实时完成率；当前收口真相以 `reports/analysis/frontend-mainline-overall-closeout.md` 与 `reports/analysis/frontend-mainline-overall-status.json` 为准。

- 总清单条目: 34
- 优化中: 2（Login、Dashboard）
- 待优化: 32
- 完成: 0
- 完成率: 0%

---

## 9. 历史下一步执行顺序（2026-03-03 计划快照）

> 以下顺序是 2026-03-03 这份计划文档的历史执行建议，不是当前 frontend mainline 的实时排期；当前主线锚点以 `docs/plans/2026-04-02-frontend-mainline-phase-1-execution-matrix.md` 为准，任务状态以 Mongo `coordctl.py work` 记录为准。

1. `placeholder` 与 `mock-debt` 页面收口已完成，继续按 V3 策略推进 `mixed` 页面能力提取与聚合。
2. 优先处理 P0/P1 的 `mixed` 页面，补齐 API 对齐与字段一致性验证。
3. 同步扩展 E2E 对关键页面的可见性与数据一致性断言（保留 PM2 门禁链路）。
4. 每次涉及路由或 Layout 变更，先过 `scripts/run_e2e_pm2.sh`。

---

## 10. 历史审批备注快照（2026-03-03）

- 历史门禁命令实跑结果（2026-03-03）: `bash scripts/run_e2e_pm2.sh` -> `8 passed`（chromium，navigation-consistency）
- 审计报告路径统一为:
  `reports/analysis/frontend-page-optimization-audit-report.md`
- CI 门禁已接入:
  `.github/workflows/frontend-testing.yml` 新增 `frontend-optimization-audit` 作业（strict）
- 当时运行端口真值（2026-03-03 审批记录）:
  Frontend `3020`，Backend `8020`
- 当时端口兼容性探测（2026-03-03）:
  `http://localhost:3020` -> `200`，`http://localhost:8020/health` -> `200`，`http://localhost:8000/health` -> `000`
- 本轮进展（2026-03-03）:
  `#29/#30` 风险告警与公告监控页面完成去占位并接入数据加载；`#33/#34` 状态修正为 `mixed`
- 本轮进展（2026-03-03，V3 第二批）:
  `#11/#14/#15` 已移除 mock 回退，统一切换到 REAL API 驱动
- 本轮进展（2026-03-03，V3 第三批）:
  `#22/#28` 已移除 mock 依赖（信号页不再回退 MOCK；止损页移除 `Math.random`）
- 本轮进展（2026-03-03，V3 第四批）:
  `#18` 已移除 mock 回退（Strategy-Opt 改为 REAL API + 空态收口，`mock-debt` 清零）
- 本轮进展（2026-03-03，V3 第五批）:
  `#13` 已移除 mock 回退（Strategy-Repo 保持 REAL 数据源，写操作不再因 mock 状态被禁用）
- 本轮进展（2026-03-03，V3 第六批）:
  `#16` 已移除 `VITE_USE_MOCK_DATA` 触发的 mock 基线（Strategy-Backtest 切到 REAL 空态基线）
- 本轮进展（2026-03-03，V3 第七批）:
  `#6` 已移除 mock 回退（Data-Industry 改为 REAL 数据解析 + 空态收口）
- 本轮进展（2026-03-03，V3 第八批）:
  `#23/#27` 已移除组件内模拟持仓注入（Trade-Portfolio/Risk-PnL 切到 REAL API + 空态收口）
- 本轮进展（2026-03-03，V3 第九批）:
  `#20/#24` 已完成路由页直连 REAL API（Trade-Positions/Trade-History 去外部喂数依赖，失败转空态）
