# MyStocks 前端页面优化规划（修订版）

**版本**: V2.1（依据 2026-03-02 审核意见修订）
**创建日期**: 2026-03-02
**最后更新**: 2026-03-13

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
- 关键端点清单须包含 `last_verified_at`。
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
- Login、DealingRoom、Market-Realtime、Market-Technical、Market-LHB、Data-Industry

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
- `API状态`: `verified` / `pending`

| # | 页面 | 路径 | 组件路径（router 真值） | 优先级 | 数据状态 | API（当前） | API状态 | 备注 |
|---|---|---|---|---|---|---|---|---|
| 1 | Login | `/login` | `Login.vue` | P0 | real | `/api/v1/auth/login` | verified | 认证入口；2026-03-13 已重写 ArtDeco 壳层，补齐可见错误区与 chromium E2E |
| 2 | DealingRoom | `/dashboard` | `artdeco-pages/ArtDecoDashboard.vue` | P0 | real | `/api/v1/market/*` | verified | 主仪表板（保留 `/dealing-room` -> `/dashboard` 兼容跳转）；2026-03-13 已补 header 指标加载链路与 chromium E2E；当前页为多接口聚合容器 |
| 3 | Market-Realtime | `/market/realtime` | `artdeco-pages/market-tabs/MarketRealtimeTab.vue` | P0 | real | `/api/v1/market/quotes` | verified | 核心页面；2026-03-13 已切 quotes 真值链路，补齐 empty/error state 与 chromium E2E |
| 4 | Market-Technical | `/market/technical` | `artdeco-pages/market-tabs/MarketKLineTab.vue` | P0 | real | `/api/v1/market/kline` | verified | 核心页面；2026-03-13 已补 K 线 empty/error state、数组 payload 兼容与 chromium E2E |
| 5 | Market-LHB | `/market/lhb` | `artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` | P1 | mixed | `/api/v1/market/lhb` | verified | 2026-03-13 已补 blocker 壳层与 chromium E2E；live backend 已存在 `/api/v1/market/lhb`，后续只需接通页面实现 |
| 6 | Data-Industry | `/data/industry` | `artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` | P1 | real | `/api/akshare/market/*` | verified | 2026-03-03 已移除 mock 回退；2026-03-13 已补 empty/error state 与 chromium E2E |
| 7 | Data-Concept | `/data/concept` | `artdeco-pages/market-tabs/MarketConceptTab.vue` | P1 | real | `/api/akshare/market/*` | verified | 2026-03-13 已移除 mock fallback，改为真实接口空态收口与 chromium E2E |
| 8 | Data-FundFlow | `/data/fund-flow` | `artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` | P1 | real | `/api/akshare/market/fund-flow/*` | verified | 2026-03-13 已补路由级自加载、empty state 与 chromium E2E |
| 9 | Data-Indicator | `/data/indicator` | `artdeco-pages/ArtDecoDataAnalysis.vue` | P1 | mixed | `/api/v1/indicators/*` | verified | 公式编辑器升级中；2026-03-13 已补 blocker 壳层与 chromium E2E；live backend 已存在指标前缀 |
| 10 | Watchlist-Manage | `/watchlist/manage` | `artdeco-pages/stock-management-tabs/WatchlistManager.vue` | P1 | real | `/api/watchlist` | verified | 2026-03-13 已补路由级自加载与 empty/error state，并通过 chromium E2E |
| 11 | Watchlist-Signals | `/watchlist/signals` | `artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | P1 | real | `/api/v1/trade/signals` | verified | 2026-03-03 已移除 mock 回退；2026-03-13 已补 shared empty/error state 与 chromium E2E |
| 12 | Watchlist-Screener | `/watchlist/screener` | `stocks/Screener.vue` | P1 | mixed | `/api/v1/data/stocks/*` | verified | 当前仍保留 blocker 壳层；live backend 已存在数据选股前缀 |
| 13 | Strategy-Repo | `/strategy/repo` | `artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` | P1 | real | `/api/v1/strategy/strategies` | verified | 2026-03-03 已移除 mock 回退，失败转空态；2026-03-13 已补 chromium E2E 主链验证 |
| 14 | Strategy-Parameters | `/strategy/parameters` | `artdeco-pages/strategy-tabs/StrategyParametersTab.vue` | P1 | real | `/api/v1/strategy/strategies` | verified | 2026-03-03 已移除 mock 回退；2026-03-13 已补 chromium E2E 主链验证 |
| 15 | Strategy-Signals | `/strategy/signals` | `artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | P1 | real | `/api/v1/trade/signals` | verified | 2026-03-03 已移除 mock 回退；2026-03-13 已补 shared empty/error state 与 chromium E2E |
| 16 | Strategy-Backtest | `/strategy/backtest` | `artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` | P1 | real | `/api/v1/strategy/backtest*` | verified | 2026-03-03 已移除 mock 基线依赖；2026-03-13 已补 backtest workbench view model 与 chromium E2E |
| 17 | Strategy-GPU | `/strategy/gpu` | `strategy/BacktestGPU.vue` | P2 | mixed | `/api/gpu/*` | pending | 2026-03-13 已补 API pending blocker 壳层与 chromium E2E；live backend 仍未发现该前缀 |
| 18 | Strategy-Opt | `/strategy/opt` | `artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue` | P2 | real | `/api/v1/strategy/*` | verified | 2026-03-13 已移除失败时 mock 回退，改为空态/错误态收口并通过 chromium E2E |
| 19 | Strategy-Pos | `/strategy/pos` | `artdeco-pages/stock-management-tabs/PortfolioMonitor.vue` | P2 | real | `/api/v1/trade/positions` | verified | 2026-03-13 已补路由级自加载与 empty/error state，并通过 chromium E2E |
| 20 | Trade-Positions | `/trade/positions` | `artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` | P1 | real | `/api/v1/trade/positions` | verified | 2026-03-03 已接入 REAL API 持仓映射；2026-03-13 已补 empty/error state 与 chromium E2E |
| 21 | Trade-Terminal | `/trade/terminal` | `TradingDashboard.vue` | P1 | mixed | `/api/trading/*` | verified | 2026-03-13 已完成壳层可用性验证，并通过 chromium E2E；live backend 已存在交易运行时前缀 |
| 22 | Trade-Signals | `/trade/signals` | `artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` | P1 | real | `/api/v1/trade/signals` | verified | 2026-03-03 已移除 mock 回退；2026-03-13 已切 shared signal transform 与 chromium E2E |
| 23 | Trade-Portfolio | `/trade/portfolio` | `artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | P1 | real | `/api/v1/trade/positions` | verified | 2026-03-03 已移除组件内模拟注入；2026-03-13 已补 shared empty/error state 与 chromium E2E |
| 24 | Trade-History | `/trade/history` | `artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` | P1 | real | `/api/v1/trade/trades` | verified | 2026-03-03 已接入 REAL API 历史映射；2026-03-13 已补 empty/error state 与 chromium E2E |
| 25 | Risk-Management | `/risk/management` | `artdeco-pages/ArtDecoRiskManagement.vue` | P1 | mixed | `/api/v1/risk/*` | verified | 2026-03-13 已补容器 helpers / panels 并通过 chromium E2E |
| 26 | Risk-Overview | `/risk/overview` | `artdeco-pages/risk-tabs/RiskOverviewTab.vue` | P1 | mixed | `/api/v1/risk/*` | verified | 2026-03-13 已完成壳层可用性验证，并通过 chromium E2E |
| 27 | Risk-PnL | `/risk/pnl` | `artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | P1 | real | `/api/v1/trade/positions` | verified | 组件复用，2026-03-03 已切 REAL API + 空态；2026-03-13 已补 shared empty/error state 与 chromium E2E |
| 28 | Risk-StopLoss | `/risk/stop-loss` | `artdeco-pages/risk-tabs/StopLossMonitorTab.vue` | P1 | real | `/api/v1/monitoring/watchlists` | verified | 2026-03-03 已移除 `Math.random()` 伪数据；2026-03-13 已补 empty/error state 与 chromium E2E |
| 29 | Risk-Alerts | `/risk/alerts` | `artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` | P1 | mixed | `/api/v1/risk/alerts` | verified | 2026-03-03 已去占位并接入告警规则/记录；2026-03-13 已完成壳层可用性验证并通过 chromium E2E |
| 30 | Risk-News | `/risk/news` | `artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` | P2 | real | `/api/v1/announcement` | verified | 2026-03-13 已补 empty/error state 与 chromium E2E |
| 31 | System-Config | `/system/config` | `artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` | P2 | mixed | `/api/v1/system/*` | verified | 2026-03-13 已补 blocker 壳层，保留本地设置持久化与 chromium E2E；live backend 已存在系统配置前缀 |
| 32 | System-Health | `/system/health` | `artdeco-pages/system-tabs/SystemHealthTab.vue` | P2 | real | `/health` | verified | 2026-03-13 已补 health empty/error state 与 chromium E2E |
| 33 | System-API | `/system/api` | `artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` | P2 | real | `/metrics` | verified | 2026-03-13 已补 metrics empty/error state 与 chromium E2E |
| 34 | System-Data | `/system/data` | `artdeco-pages/system-tabs/ArtDecoDataManagement.vue` | P2 | real | `/api/v1/data-sources/config` | verified | 2026-03-13 已补 config empty/error state 与 chromium E2E |

---

## 7. 已校验端点清单（自动校验）

`last_verified_at: 2026-03-13`（来源: `scripts/dev/frontend_optimization_audit.py --strict`, `backend_source=backend_app`, `verified_api_issues=0`）

- `/api/v1/auth/login`（`auth router`）
- `/api/v1/market/*`（`market router`; 仪表板页为多接口聚合容器）
- `/api/v1/market/quotes`（`VERSION_MAPPING + market router`）
- `/api/v1/market/kline`（`VERSION_MAPPING + market router`）
- `/api/v1/market/lhb`（`market router`）
- `/api/watchlist`（`main.py include_router(watchlist, prefix="/api/watchlist")`）
- `/api/v1/data/stocks/*`（`data router`）
- `/api/v1/strategy/strategies`（`strategy_management/get_monitoring_db.py`）
- `/api/v1/strategy/backtest*`（`strategy_management/*.py`）
- `/api/v1/indicators/*`（`indicators router`）
- `/api/v1/trade/signals`（`trade router`）
- `/api/v1/trade/positions`（`trade router`）
- `/api/v1/trade/trades`（`trade router`）
- `/api/trading/*`（`trading runtime router`）
- `/api/v1/risk/*`、`/api/v1/risk/alerts`（`risk router`）
- `/api/v1/announcement`（`VERSION_MAPPING + announcement`）
- `/api/announcement/list`（`announcement compatibility route`）
- `/api/v1/system/*`（`system router`）
- `/api/v1/data-sources/config`（`data_source_config.py`）
- `/health`、`/metrics`（`main.py`）

待校验（pending）:
- `/api/gpu/*`（当前后端注册路由中未发现该前缀，保留为 pending）

> 说明: 2026-03-13 已在可导入 `backend_app` 的环境下重跑审计，`verified_api_issues=0`。当前真正未证实的页面级 API 只剩 `/api/gpu/*`。

---

## 8. 当前进度

- 总清单条目: 34
- 优化中: 0
- 待优化: 0
- 完成: 34（Login、DealingRoom、Market-Realtime、Market-Technical、Market-LHB、Data-Industry、Data-Concept、Data-FundFlow、Data-Indicator、Watchlist-Manage、Watchlist-Signals、Watchlist-Screener、Strategy-Repo、Strategy-Parameters、Strategy-Signals、Strategy-Backtest、Strategy-GPU、Strategy-Opt、Strategy-Pos、Trade-Positions、Trade-Terminal、Trade-Signals、Trade-Portfolio、Trade-History、Risk-Management、Risk-Overview、Risk-PnL、Risk-StopLoss、Risk-Alerts、Risk-News、System-Config、System-Health、System-API、System-Data）
- 完成率: 100%

## 8.1 Gate-0 P0/P1 分类矩阵（2026-03-12）

| 页面 | 批次 | 分类标记 | 说明 |
|---|---|---|---|
| Login | P0-B | `container-only`, `needs-token-cleanup`, `api-pending-blocked` | 登录入口页，保留独立壳层与错误态 |
| DealingRoom | P0-B | `container-only`, `needs-domain-component-extraction`, `needs-token-cleanup`, `api-pending-blocked` | 规范路径已切到 `/dashboard`，`/dealing-room` 仅保留兼容跳转 |
| Market-Realtime | P0-A | `tab-only`, `needs-token-cleanup` | 核心实时行情页，优先补 E2E 可见性与状态断言 |
| Market-Technical | P0-A | `tab-only`, `needs-token-cleanup` | 核心 K 线分析页，优先补图表与空态收口 |
| Market-LHB | P1-A | `tab-only`, `needs-token-cleanup`, `api-pending-blocked` | 后端路由仍需复核 |
| Data-Industry | P1-A | `tab-only` | 已切真实数据，保持空态/失败态一致性 |
| Data-Concept | P1-A | `tab-only`, `needs-domain-component-extraction`, `needs-token-cleanup` | 与行业/资金流共享分析块 |
| Data-FundFlow | P1-A | `tab-only`, `needs-domain-component-extraction`, `needs-token-cleanup` | 统一 akshare 资金流映射 |
| Data-Indicator | P1-A | `container-only`, `needs-domain-component-extraction`, `api-pending-blocked` | 指标分析页仍受接口真值阻塞 |
| Watchlist-Manage | P1-E | `tab-only`, `needs-token-cleanup` | 自选管理页优先补交互一致性 |
| Watchlist-Signals | P1-B | `tab-only`, `needs-domain-component-extraction`, `api-pending-blocked` | 与策略/交易信号页共组件 |
| Watchlist-Screener | P1-E | `container-only`, `needs-domain-component-extraction`, `needs-token-cleanup`, `api-pending-blocked` | 当前仍是独立 `stocks/Screener.vue` |
| Strategy-Repo | P1-C | `tab-only` | 路由 API 真值已收口到 `/api/v1/strategy/strategies` |
| Strategy-Parameters | P1-C | `tab-only` | 保持真实接口驱动 |
| Strategy-Signals | P1-B | `tab-only`, `needs-domain-component-extraction`, `api-pending-blocked` | 与 watchlist/trade signals 共组件 |
| Strategy-Backtest | P1-C | `tab-only`, `needs-domain-component-extraction` | 回测工作台需继续沉淀复用块 |
| Trade-Positions | P1-B | `tab-only`, `needs-domain-component-extraction`, `api-pending-blocked` | 与组合/风险页共享持仓模型 |
| Trade-Terminal | P1-E | `container-only`, `needs-token-cleanup`, `api-pending-blocked` | 交易壳层页，先保流程可达 |
| Trade-Signals | P1-B | `tab-only`, `needs-domain-component-extraction`, `api-pending-blocked` | 与另外两个信号页共组件 |
| Trade-Portfolio | P1-B | `tab-only`, `needs-domain-component-extraction`, `api-pending-blocked` | 与 `Risk-PnL` 共用 `PortfolioOverviewTab.vue` |
| Trade-History | P1-E | `tab-only`, `needs-domain-component-extraction`, `api-pending-blocked` | 历史对账与交易控制块可抽复用组件 |
| Risk-Management | P1-D | `container-only`, `needs-domain-component-extraction`, `api-pending-blocked` | 风控父容器，需统一路由/API 壳层 |
| Risk-Overview | P1-D | `tab-only`, `api-pending-blocked` | 保持风险摘要与空态一致性 |
| Risk-PnL | P1-B | `tab-only`, `needs-domain-component-extraction`, `api-pending-blocked` | 与 Trade-Portfolio 共组件 |
| Risk-StopLoss | P1-D | `tab-only`, `needs-token-cleanup` | 已去伪数据，继续做视觉和状态口径统一 |
| Risk-Alerts | P1-D | `tab-only`, `api-pending-blocked` | 告警中心先保结构与 blocker 登记 |

## 8.2 P2 验证补充（2026-03-13）

- `/tmp` 镜像副本 `chromium`：
  `cd /tmp/mystocks-frontend-run && PW_REUSE_EXISTING_SERVER=true FRONTEND_BASE_URL=http://127.0.0.1:3021 FRONTEND_PORT=3021 FRONTEND_BACKUP_PORT=3022 BACKEND_PORT=8020 BACKEND_BACKUP_PORT=8021 HOME=/tmp XDG_CACHE_HOME=/tmp npx playwright test --config playwright.config.js --project=chromium tests/e2e/p2-pages.spec.ts`
- 结果：`8 passed`

---

## 9. 下一步执行顺序

1. `Gate-0` 到 `P2` 首轮页面收口已完成，34 页已全部进入可执行状态。
2. 下一步优先补 `API pending` 真值复核：当前仅剩 `Strategy-GPU` 的 `/api/gpu/*`。
3. 持续使用 `scripts/run_e2e_pm2.sh` 做 PM2 smoke，避免回退到手工环境绕过。
4. 对仍为 `mixed` 的页面继续做二轮治理，目标是把 blocker 页推进到真实接口模式，而不是继续扩散页面内临时壳层。

---

## 10. 审批备注（2026-03-03）

- 门禁命令实跑结果: `KEEP_PM2_SERVICES=1 scripts/run_e2e_pm2.sh` -> `8 passed`（chromium，navigation-consistency）
- 审计报告路径统一为:
  `reports/analysis/frontend-page-optimization-audit-report.md`
- CI 门禁已接入:
  `.github/workflows/frontend-testing.yml` 新增 `frontend-optimization-audit` 作业（strict）
- 当前运行端口真值:
  Frontend `3020`，Backend `8020`
- 端口兼容性探测:
  `http://localhost:3020` -> `200`，`http://localhost:8020/health` -> `200`，`http://localhost:8000/health` -> `000`
- 本轮进展（2026-03-13）:
  `scripts/run_e2e_pm2.sh` 已修复环境依赖问题，可直接复用本地前端 Playwright 和 `/tmp/ms-playwright` 浏览器缓存
- 本轮进展（2026-03-13，审计真值恢复）:
  `frontend_optimization_audit.py --strict` 已回到 `backend_app` 模式，`verified_api_issues=0`
- 本轮进展（2026-03-13，pending 收口）:
  页面级 `pending` 已收缩到仅剩 `Strategy-GPU` 的 `/api/gpu/*`
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
- 本轮进展（2026-03-12，Gate-0）:
  `router/pageConfig/优化清单` 已完成首轮 SSOT 纠偏；`/dashboard` 取代清单中的旧 `/dealing-room` 作为主路径，`/qm/*`、详情页和 `not-found` 不再进入活跃 `pageConfig` 生成范围
- 本轮校验限制（2026-03-13）:
  `frontend_optimization_audit.py --strict` 在当前会话环境缺少完整数据库相关变量时会退回 `openapi_fallback`；该模式下仍报告 `verified_api_issues=9`，只能视为“待带完整环境复核”的校验提示，不能直接判定为后端真值回归
- 本轮进展（2026-03-13，P0-A）:
  `#3/#4` 已完成状态收口与页面级回归；在 `/tmp/mystocks-frontend-run` 镜像副本上使用 `chromium` 实测 `market-data.spec.ts + kline-chart.spec.ts` 共 30 条用例，结果 `30 passed`
- 本轮进展（2026-03-13，P0-B）:
  `#1/#2` 已完成登录页壳层与仪表板容器首轮收口；在 `/tmp/mystocks-frontend-run` 镜像副本上使用 `chromium` 实测 `login-dashboard.spec.ts` 共 3 条用例，结果 `3 passed`
- 本轮进展（2026-03-13，P1-A）:
  `#5/#6/#7/#8/#9` 已完成首轮页面收口；在 `/tmp/mystocks-frontend-run` 镜像副本上使用 `chromium` 实测 `market-data-p1a.spec.ts` 共 5 条用例，结果 `5 passed`
- 本轮进展（2026-03-13，P1-B）:
  `#11/#15/#20/#22/#23/#27` 已完成 shared signals / positions 首轮收口；在 `/tmp/mystocks-frontend-run` 镜像副本上使用 `chromium` 实测 `signals-positions-p1b.spec.ts` 共 5 条用例，结果 `5 passed`
- 本轮进展（2026-03-13，P1-C）:
  `#13/#14/#16` 已完成策略主链首轮收口；在 `/tmp/mystocks-frontend-run` 镜像副本上使用 `chromium` 实测 `strategy-mainline-p1c.spec.ts` 共 3 条用例，结果 `3 passed`
- 本轮进展（2026-03-13，P1-D）:
  `#25/#26/#28/#29` 已完成风控主链首轮收口；在 `/tmp/mystocks-frontend-run` 镜像副本上使用 `chromium` 实测 `risk-mainline-p1d.spec.ts` 共 4 条用例，结果 `4 passed`
- 本轮进展（2026-03-13，P1-E）:
  `#10/#12/#21/#24` 已完成自选与交易边缘页首轮收口；在 `/tmp/mystocks-frontend-run` 镜像副本上使用 `chromium` 实测 `watchlist-trade-p1e.spec.ts` 共 4 条用例，结果 `4 passed`
