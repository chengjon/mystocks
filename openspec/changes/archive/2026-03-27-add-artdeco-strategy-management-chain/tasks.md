## 1. Baseline & Contract Alignment

> **历史任务说明**:
> 本文件用于保留某次历史任务拆解、执行清单或阶段性待办，不代表当前仍需按原样执行。
> 其中的勾选状态、优先级和实施顺序仅对应当时上下文；继续沿用前应先对照 `architecture/STANDARDS.md`、当前需求、现行 specs 与实际仓库状态重新校准。


- [x] 1.1 Confirm API source priority for StrategyManagement MVP (`/api/v1/strategy` first, `/api/strategy-mgmt` compatibility path)
- [x] 1.2 Define canonical frontend ViewModel fields for strategy list/detail/lifecycle state
- [x] 1.3 Document request/response mapping table in design doc and sync with frontend team

## 2. StrategyManagement MVP (ArtDeco)

- [x] 2.1 Replace placeholder UI in `ArtDecoStrategyManagement.vue` with table/list + filter + pagination + empty state
- [x] 2.2 Integrate `useStrategy` data loading and bind loading/error states
- [x] 2.3 Surface Request ID / process time in StrategyManagement UI (TRACE_ID requirement)
- [x] 2.4 Add REAL-MOCK fallback behavior and explicit source indicator in UI

## 3. StrategyManagement MVP Actions (Execution Scope Locked)

- [x] 3.1 Implement row-level lifecycle actions: start, stop, pause, resume

## 4. Phase2 - CRUD & Feedback Enhancements

- [x] 4.1 Implement create/edit/delete flows with optimistic update and rollback on failure
- [x] 4.2 Ensure operation-level feedback (toast + inline status update + retry affordance)

## 5. Phase2 - Cross-Tab Integration

- [x] 5.1 Add navigation handoff from StrategyManagement to Parameters/Signals/Backtest tabs with `strategyId`
- [x] 5.2 Keep strategy status and parameter snapshots consistent across tabs after mutation
- [x] 5.3 Add backtest quick action entry from strategy row and backtest status polling handoff

## 6. Phase2 - Strategy Optimization Chain (Same Owner, Deferred Execution)

- [x] 6.1 Replace `ArtDecoStrategyOptimization.vue` placeholder with functional ArtDeco shell and data source indicator
- [x] 6.2 Reuse StrategyManagement canonical strategy context (`strategyId`, status, parameter snapshot) as optimization input contract
- [x] 6.3 Define optimization result write-back points to management/parameters/backtest views (without duplicating adapters)

## 7. Testing & Quality Gates

- [x] 7.1 Add/update unit tests for adapters/composables (`useStrategy`, `StrategyAdapter`)
- [x] 7.2 Add/update E2E scenarios for strategy list, lifecycle actions, CRUD, and fallback behavior
- [x] 7.3 Run frontend quality checks: syntax errors must be 0, type inference errors must not exceed baseline (100)
- [x] 7.4 Verify PM2 services and E2E baseline reporting in completion report

## 8. Delivery & Governance

- [x] 8.1 Produce implementation report distinguishing new regressions vs pre-existing technical debt
- [ ] 8.2 Update OpenSpec tasks status and archive only after deployment acceptance

## Scope Guard

- [x] SG.1 MVP implementation scope is strictly `2.x + 3.1`; all 4.x/5.x items are Phase2 and MUST NOT block MVP delivery
- [x] SG.2 Strategy Optimization chain (`6.x`) is executed by the same owner after MVP completion to avoid contract divergence
