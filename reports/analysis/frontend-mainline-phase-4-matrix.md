# MyStocks Frontend Mainline Phase 4 Matrix

> Generated at: `2026-04-05T17:42:40+08:00`
> Source plan: `docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md`
> Overall plan: `docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md`
> Scope: `10` pages

## 1. Runtime Baseline

- Verification date: `2026-04-05`
- `mystocks-backend`: `http://localhost:8020`
- `mystocks-frontend`: `http://localhost:3020`
- Backend health:
  - `/health` -> `200 OK`
  - `/health/ready` -> `200 OK`
- Frontend proxy health:
  - `/api/health/ready` -> `200 OK`
- Verification frontend runtime:
  - live PM2 preview shell: `mystocks-frontend`
  - `http://localhost:3020`
  - `VITE_API_BASE_URL=http://localhost:8020`

## 2. Page Matrix

| Page | Domain | Route | Component | Mock | Real | Issue Category | Current Conclusion | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Risk-Management | 风险管理 / 主工作流 | `/risk/management` | `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue` | PASS | PASS | none | 风险工作流壳层、派生预警列表与真实 positions 映射稳定 | 后续补导出 / 设置动作的真实行为闭环 |
| Risk-Overview | 风险管理 / 规则总览 | `/risk/overview` | `web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue` | PASS | PASS | none | 规则清单、预警消息与真实规则读链稳定 | 后续补 rules / alerts 更深层联动边界 |
| Risk-PnL | 风险管理 / 盈亏透视 | `/risk/pnl` | `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | PASS | PASS | none | 组合资产、绩效归因与真实持仓映射稳定 | 后续补零持仓与极端权重场景 |
| Risk-StopLoss | 风险管理 / 止损雷达 | `/risk/stop-loss` | `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue` | PASS | PASS | none | watchlist -> stocks -> quotes 链路稳定，mock 轨已覆盖 triggered / critical 两类状态 | 后续补更大 watchlist 与空链回退边界 |
| Risk-Alerts | 风险管理 / 告警中心 | `/risk/alerts` | `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` | PASS | PASS | none | 告警记录和规则列表双表格稳定消费真实接口 | 后续补部分失败下的分链降级提示 |
| Risk-News | 风险管理 / 公告舆情 | `/risk/news` | `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` | PASS | PASS | none | 公告统计、表格与原文入口稳定，真实公告路由可达 | 后续补空公告与原文打开失败提示 |
| System-Config | 系统管理 / 配置中心 | `/system/config` | `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` | PASS | PASS | backend contract/runtime gap | 监控视图、页签与本地持久化稳定；统一系统配置后端契约确认不存在，当前 `保存本地设置` 仅写入 `localStorage`，数据源真实写回归属 `System-Data` | 仅在后端引入统一 system-settings 契约时再补非破坏式 real-write smoke |
| System-Health | 系统管理 / 健康矩阵 | `/system/health` | `web/frontend/src/views/artdeco-pages/system-tabs/SystemHealthTab.vue` | PASS | PASS | none | 健康探针、服务状态与中间件面板稳定消费真实 `/health` | 后续补非 healthy 状态的显式回退断言 |
| System-API | 系统管理 / 可观测面板 | `/system/api` | `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` | PASS | PASS | none | 系统监控工作台和导出报告动作在 mock 轨闭环，real 子集路由稳定通过 | 后续补基于真实 `/health/detailed` 的导出链 smoke |
| System-Data | 系统管理 / 数据源治理 | `/system/data` | `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue` | PASS | PASS | none | 配置表、启停切换与 mock batch 写回链稳定，real 子集页面读链通过 | 后续补受控测试租户下的 real-write smoke |

## 3. Execution Evidence

### Mock Track

- Browser project: `chromium`
- Important note:
  - This suite uses Playwright route stubs against the live PM2 frontend shell.
- Command:
  - `cd web/frontend && PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --config playwright.config.js --project chromium`
    - Result: `10 passed, 0 failed, 0 skipped` (`15.0s`)

### Real Track

- Browser project: `chromium`
- Command:
  - `cd web/frontend && PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test tests/e2e/comprehensive-all-pages.spec.ts --config playwright.config.js --project chromium --grep 'Risk-Management|Risk-Overview|Risk-PnL|Risk-StopLoss|Risk-Alerts|Risk-News|System-Config|System-Health|System-API|System-Data'`
    - Result: `10 passed, 0 failed, 0 skipped` (`4.4m`)
- Real subset HTTP evidence:
  - `Risk-Management`: `HTTP 200`
  - `Risk-Overview`: `HTTP 200`
  - `Risk-PnL`: `HTTP 200`
  - `Risk-StopLoss`: `HTTP 200`
  - `Risk-Alerts`: `HTTP 200`
  - `Risk-News`: `HTTP 200`
  - `System-Config`: `HTTP 200`
  - `System-Health`: `HTTP 200`
  - `System-API`: `HTTP 200`
  - `System-Data`: `HTTP 200`

## 4. Classification Summary

- `route/config drift`: `0`
- `frontend render gap`: `0`
- `backend contract/runtime gap`: `1`

Resolved during Phase 4:

- 新增 `phase4-mainline-matrix.spec.ts`，为 Risk / System 十页建立统一 mock 矩阵
- Mock 轨继续统一为 `VITE_USE_MOCK_DATA=false`，由 Playwright route stubs 接管请求路径
- `System-Data` 的批量写回请求构造已在 mock 轨被显式验证
- live PM2 frontend 在本次 refresh 中已从陈旧 `BACKEND_PORT=8888` 代理漂移纠正回 `BACKEND_PORT=8020`，`/api/health/ready` 已恢复 `200`

Known Phase 4 gap:

- `System-Config` 的真值已明确为“缺少统一 system-settings 后端契约”；当前 `保存本地设置` 仅写入本地 `localStorage`，不构成已验证的真实后端配置写链

## 5. Quality Gate

- Structural syntax errors: `0`
- Frontend type baseline: `reports/analysis/tech-debt-baseline.json` -> `frontend_type_errors = 0`
- Type-check execution in this closeout:
  - `cd web/frontend && npx vue-tsc --noEmit --pretty false`
  - Result: `exit 0`, no output
- Type regression verdict:
  - No evidence of regression above baseline in this refresh batch
  - This refresh batch changed Phase 4 / overall analysis artifacts only
- PM2 services:
  - `mystocks-backend`: `online`
  - `mystocks-frontend`: `online`
- Service addresses:
  - `http://localhost:8020`
  - `http://localhost:3020`

## 6. Final Conclusion

Phase 4 remains in a usable closeout state after the `2026-04-05` refresh:

- All ten target pages pass the dedicated mock matrix.
- All ten target pages pass the real-read subset in `comprehensive-all-pages.spec.ts`.
- One known gap remains explicitly documented:
  - `System-Config` has no unified backend config write contract; current save behavior is local-only degrade, not real-write closure.
- Outside that documented gap, this refresh did not require production source edits; the only runtime action was reloading the live PM2 frontend shell with the correct backend port environment.
