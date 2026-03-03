# `frontend-page-optimization-list.md` 审核意见（结合当前 `web/` 现状）

## 1. 审核范围与依据
- 审核对象：`docs/plans/frontend-page-optimization-list.md`
- 代码事实来源：
  - `web/frontend/src/router/index.ts`
  - `web/frontend/src/layouts/MenuConfig.ts`
  - `web/frontend/src/views/artdeco-pages/**`
  - `scripts/tests/test/run-comprehensive-tests.sh`
  - `scripts/run_e2e_pm2.sh`
  - `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
  - `web/PORTS.md`、`.env`
- 补充参考（你新增建议）：`docs/architecture/FRONTEND_OPTIMIZATION_STRATEGY_V3.md`

## 2. 审核结论
建议“**有条件通过**”：当前规划方向正确，但存在会直接影响执行落地的口径冲突与映射偏差。建议先完成下列 `P0/P1` 修订，再进入批量页面优化。

## 3. 关键问题与修改建议

### P0-1 页面总量与 Phase 分组口径不一致
**问题证据**
- 文档声明“总页面数 35”（第 12、321 行），但清单仅编号到 `34`（第 183-233 行）。
- 文档写 `Phase 2: 市场&数据（8 页）`（第 101 行），实际表格是 6 页（#7-#12）。
- 文档写 `Phase 4: 风险&系统（9 页）`（第 103 行），实际表格是 10 页（#25-#34）。
- 路由当前有 37 个命名路由（含详情页和 404），去掉 layout 后 35 个唯一页面组件。

**建议修改**
- 先明确统计口径并写入文档首页：
  - 口径 A（推荐）：优化范围=“业务主链 + 登录”，即当前 34 条（与现有表一致）。
  - 口径 B：优化范围=“路由全量页面”，需补充 `stock-graphics`、`stock-news`、`not-found`。
- 同步修正所有统计字段（总数、待优化数、完成率、Phase 页数）。

---

### P0-2 页面组件映射与实际路由不一致（会导致错改）
**问题证据**
以下条目在规划文档与路由真实组件不一致：

| 路由 | 规划文档写法 | 当前路由实际组件 |
|---|---|---|
| `/market/technical` | `KLineAnalysis.vue` | `market-tabs/MarketKLineTab.vue` |
| `/data/industry` | `IndustryAnalysis.vue` | `market-data-tabs/ArtDecoIndustryAnalysis.vue` |
| `/data/concept` | `ConceptAnalysis.vue` | `market-tabs/MarketConceptTab.vue` |
| `/strategy/repo` | `StrategyManagement.vue` | `strategy-tabs/ArtDecoStrategyManagement.vue` |
| `/strategy/backtest` | `BacktestAnalysis.vue` | `strategy-tabs/ArtDecoBacktestAnalysis.vue` |
| `/strategy/opt` | `StrategyOptimization.vue` | `strategy-tabs/ArtDecoStrategyOptimization.vue` |
| `/trade/positions` | `TradingPositions.vue` | `trading-tabs/ArtDecoTradingPositions.vue` |
| `/trade/signals` | `SignalsView.vue` | `trading-tabs/ArtDecoSignalsView.vue` |
| `/trade/portfolio` | `PortfolioOverview.vue` | `portfolio-tabs/PortfolioOverviewTab.vue` |
| `/trade/history` | `TradingHistory.vue` | `trading-tabs/ArtDecoTradingHistory.vue` |
| `/risk/news` | `AnnouncementMonitor.vue` | `risk-tabs/ArtDecoAnnouncementMonitor.vue` |
| `/system/api` | `APIHealth.vue` | `system-tabs/ArtDecoMonitoringDashboard.vue` |
| `/system/data` | `DataSourceSettings.vue` | `system-tabs/ArtDecoDataManagement.vue` |

**建议修改**
- 规划表格中的“当前组件”列改为“**router 实际组件路径**（相对 `src/views/`）”。
- 每次更新清单前，先以 `router/index.ts` 自动导出当前路由映射，避免手填漂移。

---

### P0-3 “禁止 mock”与当前页面实现冲突
**问题证据**
- 文档要求“禁止任何 mock/demo 数据”（第 117 行）。
- 但当前路由页中存在：
  - `ArtDecoBacktestAnalysis.vue` 直接依赖 `@/mock/backtestWorkbenchMock`，并按 `VITE_USE_MOCK_DATA` 切换。
  - `StopLossMonitorTab.vue` 存在 `Math.random()` 生成数据与 fallback 假数据。
  - `ArtDecoRiskAlerts.vue`、`ArtDecoAnnouncementMonitor.vue`、`ArtDecoMonitoringDashboard.vue`、`ArtDecoDataManagement.vue` 为占位/重构中页面。

**建议修改**
- 把“禁止 mock”拆成两级约束：
  - `P0 页面`：必须真实 API + 无随机数据。
  - `P1/P2 页面`：允许短期 fallback，但必须打标 `mock-debt` 并给出消债截止时间。
- 在清单中新增列：`数据状态（real/mixed/mock/placeholder）`。

---

### P0-4 API 端点口径需回归“后端路由真值”
**问题证据（示例）**
- 规划写 `/api/akshare_market/boards`、`/api/akshare_market/fund_flow`，后端前缀为 `/api/akshare/market`。
- 规划写 `/api/data_source_config`，后端为 `/api/v1/data-sources/config`。
- 规划写 `/api/risk_v31/stop_loss`，而 V3.1 风险端点实际是 `/stop-loss/...` 风格（需以后端注册路由核定最终完整前缀）。
- 部分文档端点（如 `/api/v1/strategy/list`）与当前策略路由主形态 `/strategies` 体系存在不一致风险。

**建议修改**
- 在文档中新增“API 校验规则”：
  - 路由行内端点必须来自后端注册路由或 OpenAPI 导出，而非手工维护。
- 将“关键 API 端点参考”改为“**已校验端点清单** + `last_verified_at` 时间戳”。

---

### P0-5 测试流程与项目强制门禁不一致
**问题证据**
- 文档流程用 `scripts/tests/test/run-comprehensive-tests.sh`（第 270 行）。
- 架构红线要求路由/Layout改动必须走 `scripts/run_e2e_pm2.sh`。
- 现有 `comprehensive-all-pages.spec.ts` 仍以 `HTTP >= 200` 为主，未覆盖文档宣称的“元素可见 + 数据一致性”标准；且登录成功判断仍含 `/dashboard` 旧口径。

**建议修改**
- 将文档“默认验收命令”改为：
  - `bash scripts/run_e2e_pm2.sh`（门禁）
  - 补充 `comprehensive-all-pages.spec.ts`（扩展场景）
- 把“通过标准”分两层：
  - 门禁层（阻塞）：脚本通过、无结构性语法错误。
  - 业务层（非阻塞但必报）：核心 DOM 可见性、关键接口数据一致性。

---

### P1-1 端口与 PM2 口径建议统一为 `.env` 驱动
**问题证据**
- 当前 `.env` 与 `web/PORTS.md` 主端口为 `3020/8020`。
- 仓库内存在多套 PM2 配置与历史端口写法（如 3002/8000），容易引发执行偏差。

**建议修改**
- 文档中将“后端地址固定值”改为“读取 `.env`（默认 8020）”。
- 新增“端口真值来源”：`web/PORTS.md` + `.env` + PM2 生效配置文件。

---

### P1-2 菜单与路由的 SSOT 关系需补充说明
**问题证据**
- `MenuConfig.ts` 的策略域未包含 `/strategy/parameters`、`/strategy/signals`，但路由已有。

**建议修改**
- 在清单“路由配置规范”中补一条：
  - “优化范围以 router 为准，菜单可见性以 MenuConfig 为准；二者不一致时需记录为导航债务并单独治理”。

---

### P1-3 “禁止移动端适配”建议改为“桌面优先 + 移动端可用”
**问题证据**
- 文档写“禁止移动端适配”（第 111 行）。
- 现有多个 ArtDeco 页面已存在 `@media (width <= 768px)` 的响应式样式。

**建议修改**
- 文案改为：
  - “桌面优先（1280x720+），保留移动端基础可用（不追求完整功能等价）”。

---

### P1-4 纳入你新增的 V3 策略文档作为上位参考
**你新增的建议文件**
- `docs/architecture/FRONTEND_OPTIMIZATION_STRATEGY_V3.md`

**建议修改（可直接加入原文）**
- 在“参考文档”增加：
  - `docs/architecture/FRONTEND_OPTIMIZATION_STRATEGY_V3.md`（能力提取主策略，V3）
- 在“策略优先级”增加：
  - 当 V2 清理策略与 V3“能力提取”冲突时，以 V3 为准，避免误删高复用能力页。

## 4. 建议的最小修订清单（可审批执行）
1. 修正页面总数与 Phase 分组口径（统一为 34 或补全到 35/37）。
2. 全量替换“当前组件”列为 router 实际组件路径。
3. 新增 `数据状态` 列，显式标记 `placeholder/mock` 页面。
4. 将 API 列改为“已校验端点”，并写入校验时间。
5. 验收命令切换到 `scripts/run_e2e_pm2.sh`，扩展测试保持并行。
6. 参考文档纳入 `FRONTEND_OPTIMIZATION_STRATEGY_V3.md`，并声明 V3 优先级。

## 5. 审批建议
- 建议审批结论：**“按以上 P0/P1 修订后通过”**。
- 若你同意，我下一步可以直接基于以上清单改写 `docs/plans/frontend-page-optimization-list.md`（保留原结构，仅做最小必要修订）。

## 6. 收口动作结果（2026-03-03）
- 门禁实跑：
  - 执行：`bash scripts/run_e2e_pm2.sh`
  - 结果：`exit 0`，`8 passed (4.5s)`（chromium，`navigation-consistency.spec.ts`）
- 报告路径统一：
  - 固定为 `reports/analysis/frontend-page-optimization-audit-report.md`
- 端口事实（审批备注）：
  - 运行真值：Frontend `3020`、Backend `8020`
  - 当前兼容地址校验：`http://localhost:8020/health` 不通（`000`）

## 7. 继续收口（2026-03-03）
- CI 自动门禁补齐：
  - `.github/workflows/frontend-testing.yml` 新增 `frontend-optimization-audit` 作业
  - 执行命令：
    `python scripts/dev/frontend_optimization_audit.py --repo-root . --strict --report-file reports/analysis/frontend-page-optimization-audit-report.md`
- 说明：
  - `scripts/run_e2e_pm2.sh` 末尾会执行 `pm2 delete all` 清理测试服务
  - 为审批状态确认，已额外执行 `pm2 start ecosystem.test.config.js` 并复核：
    - `http://localhost:3020` -> `200`
    - `http://localhost:8020/health` -> `200`
    - `http://localhost:8020/health` -> `000`
