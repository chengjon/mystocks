# MyStocks 前端页面优化规划（修订版）

**版本**: V2.1（依据 2026-03-02 审核意见修订）
**创建日期**: 2026-03-02
**最后更新**: 2026-03-03

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
| 1 | Login | `/login` | `Login.vue` | P0 | real | `/api/v1/auth/login` | pending | 认证入口 |
| 2 | DealingRoom | `/dealing-room` | `artdeco-pages/ArtDecoDashboard.vue` | P0 | mixed | `/api/v1/market/overview` | pending | 主仪表板 |
| 3 | Market-Realtime | `/market/realtime` | `artdeco-pages/market-tabs/MarketRealtimeTab.vue` | P0 | mixed | `/api/v1/market/quotes` | verified | 核心页面 |
| 4 | Market-Technical | `/market/technical` | `artdeco-pages/market-tabs/MarketKLineTab.vue` | P0 | mixed | `/api/v1/market/kline` | verified | 核心页面 |
| 5 | Market-LHB | `/market/lhb` | `artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` | P1 | mixed | `/api/data/lhb` | pending | 需后端路由复核 |
| 6 | Data-Industry | `/data/industry` | `artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` | P1 | mixed | `/api/akshare/market/*` | verified | 当前含 mock fallback |
| 7 | Data-Concept | `/data/concept` | `artdeco-pages/market-tabs/MarketConceptTab.vue` | P1 | mixed | `/api/akshare/market/*` | verified | 统一走 akshare 前缀 |
| 8 | Data-FundFlow | `/data/fund-flow` | `artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` | P1 | mixed | `/api/akshare/market/fund-flow/*` | verified | 需统一接口映射 |
| 9 | Data-Indicator | `/data/indicator` | `artdeco-pages/ArtDecoDataAnalysis.vue` | P1 | mixed | `/api/indicators/*` | pending | 公式编辑器升级中 |
| 10 | Watchlist-Manage | `/watchlist/manage` | `artdeco-pages/stock-management-tabs/WatchlistManager.vue` | P1 | mixed | `/api/watchlist` | verified | |
| 11 | Watchlist-Signals | `/watchlist/signals` | `artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | P1 | mock | `/api/v1/trade/signals` | pending | `mock-debt` |
| 12 | Watchlist-Screener | `/watchlist/screener` | `stocks/Screener.vue` | P1 | mixed | `/api/data/stocks` | pending | |
| 13 | Strategy-Repo | `/strategy/repo` | `artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` | P1 | mixed | `/api/v1/strategy/strategies` | verified | 含 mock fallback |
| 14 | Strategy-Parameters | `/strategy/parameters` | `artdeco-pages/strategy-tabs/StrategyParametersTab.vue` | P1 | mock | `/api/v1/strategy/strategies` | verified | `mock-debt` |
| 15 | Strategy-Signals | `/strategy/signals` | `artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | P1 | mock | `/api/v1/trade/signals` | pending | `mock-debt` |
| 16 | Strategy-Backtest | `/strategy/backtest` | `artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` | P1 | mixed | `/api/v1/strategy/backtest*` | verified | 受 `VITE_USE_MOCK_DATA` 影响 |
| 17 | Strategy-GPU | `/strategy/gpu` | `strategy/BacktestGPU.vue` | P2 | mixed | `/api/gpu/*` | pending | 后端路由暂未发现已注册前缀 |
| 18 | Strategy-Opt | `/strategy/opt` | `artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue` | P2 | mock | `/api/v1/strategy/*` | pending | `mock-debt` |
| 19 | Strategy-Pos | `/strategy/pos` | `artdeco-pages/stock-management-tabs/PortfolioMonitor.vue` | P2 | mixed | `/api/v1/trade/positions` | pending | |
| 20 | Trade-Positions | `/trade/positions` | `artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` | P1 | mixed | `/api/v1/trade/positions` | pending | |
| 21 | Trade-Terminal | `/trade/terminal` | `TradingDashboard.vue` | P1 | mixed | `/api/trade/*` | pending | |
| 22 | Trade-Signals | `/trade/signals` | `artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` | P1 | mock | `/api/v1/trade/signals` | pending | `mock-debt` |
| 23 | Trade-Portfolio | `/trade/portfolio` | `artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | P1 | mixed | `/api/v1/trade/positions` | pending | |
| 24 | Trade-History | `/trade/history` | `artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` | P1 | mixed | `/api/trade/*` | pending | |
| 25 | Risk-Management | `/risk/management` | `artdeco-pages/ArtDecoRiskManagement.vue` | P1 | mixed | `/api/v1/risk/*` | pending | |
| 26 | Risk-Overview | `/risk/overview` | `artdeco-pages/risk-tabs/RiskOverviewTab.vue` | P1 | mixed | `/api/v1/risk/*` | pending | |
| 27 | Risk-PnL | `/risk/pnl` | `artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | P1 | mixed | `/api/v1/trade/positions` | pending | 组件复用 |
| 28 | Risk-StopLoss | `/risk/stop-loss` | `artdeco-pages/risk-tabs/StopLossMonitorTab.vue` | P1 | mock | `/api/v1/monitoring/watchlists` | verified | 存在 `Math.random()` |
| 29 | Risk-Alerts | `/risk/alerts` | `artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` | P1 | placeholder | `/api/v1/risk/alerts` | pending | 页面占位 |
| 30 | Risk-News | `/risk/news` | `artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` | P2 | placeholder | `/api/v1/announcement` | verified | 页面占位 |
| 31 | System-Config | `/system/config` | `artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` | P2 | mixed | `/api/system/*` | pending | |
| 32 | System-Health | `/system/health` | `artdeco-pages/system-tabs/SystemHealthTab.vue` | P2 | mixed | `/health` | verified | |
| 33 | System-API | `/system/api` | `artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` | P2 | placeholder | `/metrics` | verified | 页面占位 |
| 34 | System-Data | `/system/data` | `artdeco-pages/system-tabs/ArtDecoDataManagement.vue` | P2 | placeholder | `/api/v1/data-sources/config` | verified | 页面占位 |

---

## 7. 已校验端点清单（自动校验）

`last_verified_at: 2026-03-03`（来源: `scripts/dev/frontend_optimization_audit.py`）

- `/api/v1/market/quotes`（`VERSION_MAPPING + market router`）
- `/api/v1/market/kline`（`VERSION_MAPPING + market router`）
- `/api/watchlist`（`main.py include_router(watchlist, prefix="/api/watchlist")`）
- `/api/v1/strategy/strategies`（`strategy_management/get_monitoring_db.py`）
- `/api/v1/strategy/backtest*`（`strategy_management/*.py`）
- `/api/v1/announcement`（`VERSION_MAPPING + announcement`）
- `/api/v1/data-sources/config`（`data_source_config.py`）
- `/health`、`/metrics`（`main.py`）

待校验（pending）:
- `/api/gpu/*`（当前后端注册路由中未发现该前缀，保留为 pending）

> 说明: 清单中标记为 `pending` 的 API，需在下一轮以 OpenAPI 导出或后端路由表完成逐条校验；已校验结果以自动脚本输出为准。

---

## 8. 当前进度

- 总清单条目: 34
- 优化中: 2（Login、DealingRoom）
- 待优化: 32
- 完成: 0
- 完成率: 0%

---

## 9. 下一步执行顺序

1. 先消除 `placeholder` 页面（#29/#30/#33/#34）。
2. 再治理 `mock-debt` 页面（#11/#14/#15/#18/#22/#28）。
3. 最后处理 `mixed` 页面的 API 对齐与可见性测试补强。
4. 每次涉及路由或 Layout 变更，先过 `scripts/run_e2e_pm2.sh`。

---

## 10. 审批备注（2026-03-03）

- 门禁命令实跑结果: `bash scripts/run_e2e_pm2.sh` -> `8 passed`（chromium，navigation-consistency）
- 审计报告路径统一为:
  `reports/analysis/frontend-page-optimization-audit-report.md`
- CI 门禁已接入:
  `.github/workflows/frontend-testing.yml` 新增 `frontend-optimization-audit` 作业（strict）
- 当前运行端口真值:
  Frontend `3020`，Backend `8020`
- 端口兼容性探测:
  `http://localhost:3020` -> `200`，`http://localhost:8020/health` -> `200`，`http://localhost:8020/health` -> `000`
