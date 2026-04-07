# MyStocks Frontend Mainline Phase 4 Matrix

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> Generated at: `2026-04-06T13:32:02+08:00`
> Source plan: `docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md`
> Overall plan: `docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md`
> Scope: `10` pages

## 1. Runtime Baseline

- Verification date: `2026-04-06`
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
| System-Config | 系统管理 / 配置中心 | `/system/config` | `web/frontend/src/views/system/Settings.vue` | PASS | PASS | none | 活跃路由已切到 canonical `Settings.vue`；健康监控继续消费 `/api/health/detailed` 与 `/api/health`，系统设置表单直接读写 `/api/v1/system/settings/general`，整体配置真相保持按 section owner 拆分而非伪造单体统一存储 | 若后续页面显式暴露 security / datasource / notification 编辑器，再补各 section owner 的非破坏式 live-browser smoke |
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
- Supplemental sectioned-contract checks:
  - `curl -sS -o /tmp/system-settings-general.json -w '%{http_code}' http://localhost:8020/api/v1/system/settings/general`
    - Result: `200`
  - `curl -sS -o /tmp/system-settings-security.json -w '%{http_code}' http://localhost:8020/api/v1/system/settings/security`
    - Result: `200`
  - `cd web/backend && PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_system_settings_contract.py tests/test_health_route_conflicts.py -q -o addopts="" -k system_settings`
    - Result: `passed`
  - `cd web/frontend && npx vitest run src/views/system/__tests__/Settings.spec.ts src/services/__tests__/systemSettingsContract.spec.ts src/services/__tests__/TradingApiManager.system-settings.spec.ts`
    - Result: `passed`
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
- `backend contract/runtime gap`: `0`

Resolved during Phase 4:

- 新增 `phase4-mainline-matrix.spec.ts`，为 Risk / System 十页建立统一 mock 矩阵
- Mock 轨继续统一为 `VITE_USE_MOCK_DATA=false`，由 Playwright route stubs 接管请求路径
- `System-Data` 的批量写回请求构造已在 mock 轨被显式验证
- live PM2 frontend 在本次 refresh 中已从陈旧 `BACKEND_PORT=8888` 代理漂移纠正回 `BACKEND_PORT=8020`，`/api/health/ready` 已恢复 `200`
- `/system/config` 当前已落到 canonical `web/frontend/src/views/system/Settings.vue`，general section 读写链接入 `/api/v1/system/settings/general`，旧 `ArtDecoSystemSettings.vue` 仅保留为薄包装兼容层
- approved `add-sectioned-system-config-contract` 已为 general / security 落地 canonical backend routes，并保持 datasource / notification 继续由各自 owner 契约负责，避免引入单体统一假真相

Known Phase 4 note:

- `System-Config` 已从 “无后端契约的本地退化页” 收口为 “分段后端契约页”；本轮没有执行共享 PM2 环境下的破坏式 live write mutation，因此写闭环证据以 targeted backend/frontend tests 为准，不把它误写成 live runtime mutation 结果

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

Phase 4 remains in a usable closeout state after the `2026-04-06` refresh:

- All ten target pages pass the dedicated mock matrix.
- All ten target pages pass the real-read subset in `comprehensive-all-pages.spec.ts`.
- No unresolved `backend contract/runtime gap` remains inside the Phase 4 page matrix.
- `System-Config` is now closed under the approved sectioned contract:
  - active route entry is `web/frontend/src/views/system/Settings.vue`
  - live runtime GET checks for `/api/v1/system/settings/general` and `/api/v1/system/settings/security` returned `200`
  - general-section write closure is verified by targeted backend/frontend tests rather than destructive PM2 write mutation
- The governance rule stays unchanged:
  - do not reintroduce a fake monolithic unified settings API
  - keep section ownership explicit for general / security / datasource / notification
