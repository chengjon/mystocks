## 1. OpenSpec

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Finalize the `system-resource-usage-monitoring` capability delta for single-node snapshots, trends, dependency summaries, and backend-defined thresholds.
- [x] 1.2 Finalize the `frontend-routing` delta for `/system/resources` and the system navigation label.
- [x] 1.3 Run `openspec validate add-system-resource-usage-monitoring --strict`.

## 2. Backend
- [x] 2.1 Add a dedicated backend resource-metrics contract under the system API surface.
- [x] 2.2 Implement single-node host metrics, process metrics for `mystocks-backend` and `mystocks-frontend`, and dependency summaries for PostgreSQL, TDengine, and Redis.
- [x] 2.3 Return backend-defined thresholds and `normal / warning / critical` state semantics in the same response.
- [x] 2.4 Add targeted backend tests for contract shape, trend windows, and threshold-state mapping.

## 3. Frontend
- [x] 3.1 Add a dedicated `/system/resources` route, menu entry, and page-config truth entry.
- [x] 3.2 Add a frontend resource-usage API surface that consumes the unified backend contract.
- [x] 3.3 Implement the standalone system resource page with snapshot cards, trend charts, dependency panels, and polling pause/resume controls.
- [x] 3.4 Add targeted frontend tests for rendering, polling controls, and threshold-state presentation.

## 4. Validation And Closeout
- [x] 4.1 Run targeted backend tests.
- [x] 4.2 Run targeted frontend unit tests and lint checks.
- [x] 4.3 Run at least one page-level E2E or smoke verification for `/system/resources`.
- [x] 4.4 Update `docs/FUNCTION_TREE.md` to close `6.1 资源使用` only if the independent page, unified contract, and verification evidence are complete.
- [x] 4.5 Commit the implementation in focused batches.
  - [x] Repo-truth（2026-05-07）：这条 change 的实现已按 focused batches 收口，而不是单次大提交。后端 unified contract / aggregation / route / backend tests 已由 `86f0f7514` `feat(system): add resource usage backend contract` 落地；当前 batch 补齐并提交剩余的前端 `/system/resources` 路由入口与 `Resources.vue` 工作台、前端 targeted tests、`monitoringApi` 资源契约接线，以及 `docs/FUNCTION_TREE.md` 中 `6.1 资源使用` 的闭环更新。验证命令为 `pytest web/backend/tests/test_system_resource_metrics_service.py web/backend/tests/test_system_resources_route.py -q --no-cov`、`cd web/frontend && npm run test -- src/api/__tests__/monitoringApi.spec.ts src/views/system/__tests__/Resources.spec.ts`、`cd web/frontend && env PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium tests/e2e/system-resources.spec.ts`，均已通过。
- [x] 4.6 Archive `add-system-resource-usage-monitoring` after the implementation and validations are complete.
