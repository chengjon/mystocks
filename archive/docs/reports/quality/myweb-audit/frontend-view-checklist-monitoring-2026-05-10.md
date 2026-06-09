# Frontend View Checklist: `views/monitoring/*`

日期：2026-05-10

范围：`web/frontend/src/views/monitoring/*`

本批次目的：复核旧监控目录中的未路由页面、页面私有 composable、样式资产和测试守护，避免把仍有功能资产或 guard 约束的历史页面直接删除。本批次只做生命周期分类，不移动文件。

## 1. Truth Inputs

路由 / 菜单真相：

- `web/frontend/src/router/index.ts` 当前没有导入 `@/views/monitoring/*`。
- `web/frontend/src/layouts/MenuConfig.ts` 当前主菜单不包含 `/monitoring/*`。
- 当前监控相关的正式入口已经分散到 canonical 主域：
- `/watchlist/manage` -> `views/watchlist/Manage.vue`，覆盖自选组合管理。
- `/risk/overview` -> `views/risk/Overview.vue`，覆盖风险概览与 alert-rules 读链。
- `/risk/alerts` -> `views/risk/Alerts.vue`，覆盖告警中心。
- `/risk/stop-loss` -> `views/risk/StopLoss.vue`，覆盖止损监控。
- `/system/health`、`/system/api`、`/system/resources` 覆盖系统健康与资源监控。

历史 / 规格证据：

- `openspec/specs/file-organization/spec.md` 明确要求评估 `src/views/monitoring/` 时先分类为 canonical runtime truth、historical route target、test-guarded artifact 或其他明确 lifecycle role；不能仅凭 live router 缺失删除。
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/monitoring-dashboard-static-shell-truth-audit.md` 已将 `MonitoringDashboard.vue` 降级为 honest static legacy shell。
- `docs/reports/quality/myweb-audit/audit-20260426-02/secondary-line-progress-summary.md` 将 `monitoring/{AlertRulesManagement,RiskDashboard,WatchlistManagement}.vue` 仍列为后续候选，因为它们组合了 selector、stats strip、fallback literals 和 shared composables 等启发式风险。

测试 / guard 证据：

- `web/frontend/src/views/monitoring/__tests__/MonitoringDashboard.spec.ts` 守护 `MonitoringDashboard.vue` 已降级为静态壳，且不得继续展示伪实时摘要、伪告警或伪龙虎榜数据。
- `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts` 守护 `AlertRulesManagement.scss` 与 `MonitoringDashboard.scss` 的 ArtDeco token 引用。
- `web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts` 守护 `RiskDashboard.scss`、`WatchlistManagement.scss` 的 fintech -> ArtDeco token bridge。
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts` 守护四个 monitoring Vue 页面不回退到旧 `@import` 样式入口。
- `web/frontend/tests/unit/config/console-log-cleanup-batch-1.spec.ts` 仍把 `MonitoringDashboard.vue` 纳入 console cleanup guard。

## 2. Page Classification

| 页面 / 资产 | 当前分类 | 路由状态 | 资产状态 | 守护状态 | 结论 |
| --- | --- | --- | --- | --- | --- |
| `views/monitoring/MonitoringDashboard.vue` | `candidate-review/legacy-static-shell` | dead route | 已降级为诚实静态 legacy shell | direct spec + style/cleanup guards | 不归档，需先退役/迁移 guard |
| `views/monitoring/AlertRulesManagement.vue` | `candidate-review/legacy-functional-page` | dead route | 告警规则管理旧页面，仍有 API/composable/表格资产 | style normalization guard | 不归档，需先吸收或确认 successor |
| `views/monitoring/RiskDashboard.vue` | `candidate-review/legacy-functional-page` | dead route | 风险 dashboard 旧页面，仍含指标卡、selector/summary 逻辑、`|| 0` 兜底 | fintech bridge style guard | 不归档，需先吸收或降级 |
| `views/monitoring/WatchlistManagement.vue` | `candidate-review/legacy-functional-page` | dead route | 自选组合旧页面，仍含组合/股票管理交互与统计逻辑 | fintech bridge style guard | 不归档，需先吸收或确认 successor |
| `views/monitoring/composables/useAlertRulesManagement.ts` | `candidate-support-asset` | helper | `AlertRulesManagement.vue` 页面私有 composable | tied to candidate page | 随候选页处理 |
| `views/monitoring/composables/useRiskDashboard.ts` | `candidate-support-asset` | helper | `RiskDashboard.vue` 页面私有 composable，含旧随机趋势/兜底逻辑 | tied to candidate page | 随候选页处理 |
| `views/monitoring/composables/useWatchlistManagement.ts` | `candidate-support-asset` | helper | `WatchlistManagement.vue` 页面私有 composable，含 watchlistService 交互与派生统计 | tied to candidate page | 随候选页处理 |
| `views/monitoring/styles/AlertRulesManagement.scss` | `candidate-support-asset` | style | 旧告警规则页样式，已接入 ArtDeco token | style guard | 随候选页处理 |
| `views/monitoring/styles/MonitoringDashboard.scss` | `candidate-support-asset/orphan-style` | style | 当前静态壳未直接引用，但仍被 style guard 覆盖 | style guard | 不直接删除，需先修正 guard |
| `views/monitoring/styles/RiskDashboard.scss` | `candidate-support-asset` | style | 旧 risk dashboard fintech token bridge | style guard | 随候选页处理 |
| `views/monitoring/styles/WatchlistManagement.scss` | `candidate-support-asset` | style | 旧 watchlist management fintech token bridge | style guard | 随候选页处理 |

## 3. Redundant-Page Checklist

本批次未发现可直接归档页面。

已经降级但仍需保留的页面：

- `MonitoringDashboard.vue` 已按历史 myweb-audit 结论降级为 honest static legacy shell，不再展示伪实时行情、伪告警统计或伪龙虎榜数据。
- 该页面仍有直接 spec 与多项配置型 guard，因此不能直接移动或删除；后续若归档，必须先迁移或退役对应测试。

仍需资产拆解的候选页面：

- `AlertRulesManagement.vue` 与 `useAlertRulesManagement.ts` 仍有告警规则表格、编辑、新建、删除和 `/monitoring` API 交互逻辑；需要对比当前 `/risk/alerts`、`/risk/overview` 的 canonical 规则/告警能力后再决定吸收或降级。
- `RiskDashboard.vue` 与 `useRiskDashboard.ts` 仍包含 portfolio health、risk score、position、alerts、建议等旧 dashboard 结构，但页面内存在大量 `|| 0` 兜底和随机趋势逻辑，不能作为 live truth 保留。
- `WatchlistManagement.vue` 与 `useWatchlistManagement.ts` 仍包含 watchlistService 的创建、编辑、删除、股票管理、派生统计逻辑；需要与当前 `/watchlist/manage` canonical 页面逐项对账后再决定吸收或归档。

禁止误判项：

- 不能仅凭 `router/index.ts` 无导入就删除 `views/monitoring/*`；`file-organization` 规格明确禁止这种做法。
- 不能把 `MonitoringDashboard.vue` 的 static-shell 状态扩展到整个目录；其他三个页面仍是 legacy functional pages，尚未完成资产拆解。
- 不能把旧 monitoring 页面作为新的 canonical 页面复活；如果需要恢复能力，必须先声明目标 route truth，并优先并入当前 `watchlist`、`risk`、`system` 主域。

## 4. Batch Conclusion

`views/monitoring/*` 当前应拆成三类治理：

- `candidate-review/legacy-static-shell`：`MonitoringDashboard.vue`，已关闭伪实时风险，但仍被 guard 守护。
- `candidate-review/legacy-functional-page`：`AlertRulesManagement.vue`、`RiskDashboard.vue`、`WatchlistManagement.vue`，均不是 active route owner，但仍需功能资产拆解与 successor 对账。
- `candidate-support-asset`：对应 composables 与 styles，随页面候选一起处理；其中 `MonitoringDashboard.scss` 当前更像 orphan-style guard artifact，需先修正 guard 再处理。

本批次没有 `archive-approved` 页面。后续建议先做 `monitoring` 资产吸收矩阵：逐项映射到 `/watchlist/manage`、`/risk/overview`、`/risk/alerts`、`/risk/stop-loss`、`/system/*`，能吸收的下沉到 canonical 页面或共享服务，无法复用且 guard 已退役后才进入 archive move。
