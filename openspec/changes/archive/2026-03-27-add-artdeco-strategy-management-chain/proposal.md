# Change: Add ArtDeco StrategyManagement Chain

> **历史计划说明**:
> 本文件记录某次历史提案、计划或分工设想，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前 `openspec/specs/`、已归档结论或实际实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际实现为准，并将已归档结论仅视为历史背景。


## Why

当前 `ArtDecoStrategyManagement` 页面仍是占位态，缺少策略管理核心能力：
- 页面未接入真实 API / REAL-MOCK 回退链路；
- 与 `useStrategy`、`StrategyApiService`、`StrategyAdapter` 现有能力未打通；
- 与策略参数、策略信号、回测分析 Tab 的上下游联动不完整。

这导致策略管理域无法形成“可配置 -> 可执行 -> 可回测 -> 可观测”的闭环，也不满足 `architecture/STANDARDS.md` 中的 `Proposal-First Rule`、`Mock 驱动开发`、`TRACE_ID 显化` 要求。

## What Changes

1. 新增 `strategy-management-chain` 能力规范，定义 StrategyManagement 的业务闭环要求：
   - 列表/筛选/分页与请求追踪展示；
   - REAL 优先、MOCK 可降级的链路行为；
   - 策略生命周期操作（启动/停止/暂停/恢复）；
   - 策略 CRUD（创建/编辑/删除）和参数可视化；
   - 与回测分析、策略参数、策略信号 Tab 的联动入口与状态一致性。

2. 明确接口优先级与迁移策略：
   - MVP 阶段优先复用前端已接好的 `/api/v1/strategy` 链路（`useStrategy` + `StrategyApiService`）；
   - 预留向 `/api/strategy-mgmt` 收敛的适配层，不在本次提案引入破坏性切换。

3. 给出分阶段实现任务（MVP + Phase2），覆盖前端改造、类型适配、测试与门禁验证。

## Impact

- **Affected specs**: `strategy-management-chain`（新增）
- **Affected code (planned)**:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
  - `web/frontend/src/composables/useStrategy.ts`
  - `web/frontend/src/api/services/strategyService.ts`
  - `web/frontend/src/utils/strategy-adapters.ts`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
  - `web/frontend/tests/e2e/strategy-management.spec.ts`

- **Breaking changes**: 无（通过兼容适配方式推进）
- **Primary risks**:
  - 后端响应结构不统一（`/api/v1/strategy` vs `/api/strategy-mgmt`）；
  - 现有 Tab 使用的 `strategyApi` 与 `useStrategy` 并行，需避免字段分裂。
