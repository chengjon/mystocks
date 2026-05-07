# Frontend Guide Family

> **导航说明**:
> 本文件是 `docs/guides/frontend/` 的 transition index，不是仓库共享规则、当前前端实现边界或唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及具体执行入口，再结合根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与验证结果核对。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于保留前端集成、PR gate、变更卫生、部署与历史任务资料，不承担仓库级 trunk。推荐阅读顺序：

1. [`frontend-change-hygiene-and-micro-commit-guide.md`](./frontend-change-hygiene-and-micro-commit-guide.md)
2. [`PR_GATE_QUICK_REFERENCE.md`](./PR_GATE_QUICK_REFERENCE.md)
3. [`DASHBOARD_API_INTEGRATION_GUIDE.md`](./DASHBOARD_API_INTEGRATION_GUIDE.md)
4. [`pinia-api-standardization-guide.md`](./pinia-api-standardization-guide.md)
5. [`DASHBOARD_API_ENRICHMENT_GUIDE.md`](./DASHBOARD_API_ENRICHMENT_GUIDE.md)
6. [`HTML5_RUNTIME_CAPABILITY_GUIDE.md`](./HTML5_RUNTIME_CAPABILITY_GUIDE.md)
7. [`HTML5_RUNTIME_OPERATIONS_GUIDE.md`](./HTML5_RUNTIME_OPERATIONS_GUIDE.md)
8. [`history-mode-deployment-guide.md`](./history-mode-deployment-guide.md)
9. [`SASS_DEPRECATION_FIX.md`](./SASS_DEPRECATION_FIX.md)
10. [`css-scss-development-guide.md`](./css-scss-development-guide.md)
11. 再按需进入 service adapter、routing optimization、dayjs 与其他历史任务/总结材料

## Active Supporting Guides

- [`frontend-change-hygiene-and-micro-commit-guide.md`](./frontend-change-hygiene-and-micro-commit-guide.md)
  - 前端变更卫生与微提交规范
- [`PR_GATE_QUICK_REFERENCE.md`](./PR_GATE_QUICK_REFERENCE.md)
  - reviewer 与执行者的前端门禁速查表
- [`DASHBOARD_API_INTEGRATION_GUIDE.md`](./DASHBOARD_API_INTEGRATION_GUIDE.md)
  - Dashboard API 集成实施指南
- [`pinia-api-standardization-guide.md`](./pinia-api-standardization-guide.md)
  - Pinia API 标准化模式、迁移步骤与验证要求
- [`DASHBOARD_API_ENRICHMENT_GUIDE.md`](./DASHBOARD_API_ENRICHMENT_GUIDE.md)
  - Dashboard API 丰富化说明
- [`HTML5_RUNTIME_CAPABILITY_GUIDE.md`](./HTML5_RUNTIME_CAPABILITY_GUIDE.md)
  - HTML5 runtime 当前能力面：PWA/IndexedDB/Web Workers 真相源与边界说明
- [`HTML5_RUNTIME_OPERATIONS_GUIDE.md`](./HTML5_RUNTIME_OPERATIONS_GUIDE.md)
  - HTML5 runtime 当前运维观察面、最小检查命令与故障排查入口
- [`history-mode-deployment-guide.md`](./history-mode-deployment-guide.md)
  - History mode 部署与故障排查指南
- [`SASS_DEPRECATION_FIX.md`](./SASS_DEPRECATION_FIX.md)
  - Sass 弃用警告修复说明
- [`css-scss-development-guide.md`](./css-scss-development-guide.md)
  - CSS/SCSS 开发规范入口

## Retained Specialized References

- [`SERVICE_ADAPTER_GUIDE.md`](./SERVICE_ADAPTER_GUIDE.md)
  - Service 适配器层使用指南
- [`FRONTEND_ROUTING_OPTIMIZATION_GUIDE.md`](./FRONTEND_ROUTING_OPTIMIZATION_GUIDE.md)
  - Frontend routing 优化实施指南
- [`HTML5_MIGRATION_WEB_WORKERS_SUMMARY.md`](./HTML5_MIGRATION_WEB_WORKERS_SUMMARY.md)
  - HTML5/Web Workers 历史总结
- [`api-data-fetching-pattern-standardization-task.md`](./api-data-fetching-pattern-standardization-task.md)
  - API 数据获取模式标准化任务方案
- [`data-visualization-enhancement-task.md`](./data-visualization-enhancement-task.md)
  - 数据可视化增强任务方案
- [`dayjs修复指南.md`](./dayjs修复指南.md)
  - dayjs 修复指南
- [`dayjs新手指南.md`](./dayjs新手指南.md)
  - dayjs 新手指南
- [`enhanced-ui-ux-guide.md`](./enhanced-ui-ux-guide.md)
  - UI/UX 增强界面使用指南
- [`error-handling-implementation-task.md`](./error-handling-implementation-task.md)
  - Error handling 实现任务方案
- [`frontend-auth-guard-enablement-task.md`](./frontend-auth-guard-enablement-task.md)
  - Authentication guard 启用任务方案
- [`frontend-routing-history-migration-task.md`](./frontend-routing-history-migration-task.md)
  - History mode 迁移任务方案
- [`frontend_optimization_next_steps.md`](./frontend_optimization_next_steps.md)
  - 前端优化下一步安排
- [`mystocks-artdeco-integration-fix.md`](./mystocks-artdeco-integration-fix.md)
  - ArtDeco 集成修复实施计划
- [`page-title-management-dynamic-options-task.md`](./page-title-management-dynamic-options-task.md)
  - Page title 动态选项任务方案
- [`router_analysis_report_corrected.md`](./router_analysis_report_corrected.md)
  - Router 分析修正版

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只保留当前仍有较高直接使用价值的 hygiene、gate、integration、deployment 与样式修复入口，其余任务/总结材料统一通过本 index 进入
- 若后续这些 specialized references 的实际入链继续下降，可继续按 bounded batch 单独评估 archive/delete
