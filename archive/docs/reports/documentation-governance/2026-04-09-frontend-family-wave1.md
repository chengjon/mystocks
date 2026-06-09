# Frontend Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/frontend/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/frontend/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/frontend/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把 hygiene、PR gate、dashboard integration、deployment、样式修复、routing task、dayjs、UI enhancement 与多份历史任务/总结材料全部平铺暴露
- 这会让当前高频 runbook 与历史任务/专题材料处于同一优先级，增加根导航噪音

## Changes

- 将 `docs/guides/frontend/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Frontend family 的根导航
- 根导航现在优先保留：
  - `guides/frontend/INDEX.md`
  - `guides/frontend/frontend-change-hygiene-and-micro-commit-guide.md`
  - `guides/frontend/PR_GATE_QUICK_REFERENCE.md`
  - `guides/frontend/DASHBOARD_API_INTEGRATION_GUIDE.md`
  - `guides/frontend/DASHBOARD_API_ENRICHMENT_GUIDE.md`
  - `guides/frontend/history-mode-deployment-guide.md`
  - `guides/frontend/SASS_DEPRECATION_FIX.md`
  - `guides/frontend/css-scss-development-guide.md`
  - `Supporting Guides` -> `guides/frontend/INDEX.md`
- 将 routing task、dayjs、service adapter、UI enhancement 和其余历史任务/总结材料收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - 无新增 canonical trunk；该 family 继续保持 `supporting`
- family transition index:
  - `docs/guides/frontend/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 routing task、dayjs、service adapter 与其他历史任务 leaf docs 的直接暴露
- retention duty:
  - `SERVICE_ADAPTER_GUIDE.md`
  - `FRONTEND_ROUTING_OPTIMIZATION_GUIDE.md`
  - `HTML5_MIGRATION_WEB_WORKERS_SUMMARY.md`
  - `api-data-fetching-pattern-standardization-task.md`
  - `data-visualization-enhancement-task.md`
  - `dayjs修复指南.md`
  - `dayjs新手指南.md`
  - `enhanced-ui-ux-guide.md`
  - `error-handling-implementation-task.md`
  - `frontend-auth-guard-enablement-task.md`
  - `frontend-routing-history-migration-task.md`
  - `frontend_optimization_next_steps.md`
  - `mystocks-artdeco-integration-fix.md`
  - `page-title-management-dynamic-options-task.md`
  - `router_analysis_report_corrected.md`
  - 以上文档继续保留为 specialized/reference docs

## Expected Effect

- 根导航优先展示当前仍有较高现实入链的 hygiene、gate、dashboard integration、deployment 与样式规范入口
- 历史任务、专题方案和 dayjs/service adapter/UI enhancement 材料不再与高频入口平级暴露，但仍可通过 family index 进入
- 后续若这些 specialized references 的实际入链继续下降，可继续逐份评估 archive/delete
