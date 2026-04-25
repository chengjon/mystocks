# Closeout Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-25

## What Landed

- Removed service-level `VITE_APP_MODE` branching from `web/frontend/src/api/services/strategyService.ts`
- Kept `VITE_USE_MOCK_DATA` + shared `apiClient` as the active frontend mock-mode execution truth
- Removed adapter-layer silent mock fallback from:
  - `web/frontend/src/api/adapters/strategyAdapter.ts`
  - `web/frontend/src/api/adapters/marketAdapter.ts`
- Updated strategy detail consumer handling in `web/frontend/src/composables/useStrategy.ts`
- Added explicit mock support for `/v1/strategy/*` routes in `web/frontend/src/api/mockApiClient.ts`
- Updated environment/mock governance docs and added:
  - `docs/guides/mock-data/MOCK_GOVERNANCE_AUDIT_LEDGER.md`

## Verified Inventory / Layer Audit

| Surface | Page status | Client layer | Service layer | Adapter layer | Result |
|--------|-------------|--------------|---------------|---------------|--------|
| Strategy list/detail paths via `useStrategy.ts` | verified | explicit `VITE_USE_MOCK_DATA` gate | `VITE_APP_MODE` branch removed | silent fallback removed | aligned |
| Strategy backtest paths via `useStrategy.backtest.ts` / backtest VM | verified | explicit `VITE_USE_MOCK_DATA` gate | `VITE_APP_MODE` branch removed | backtest adapter already returned explicit `null` failure | aligned |
| Market overview / fund flow / kline adapter paths | verified | explicit `VITE_USE_MOCK_DATA` gate | no dual-truth service branch in this batch | silent fallback removed | aligned |
| App readiness | controlled fallback only | explicit `VITE_USE_MOCK_DATA` gate | n/a | n/a | confirmed compliant, no behavior change required |

## Validation

### OpenSpec

```bash
openspec validate align-mock-data-governance-with-verified-pages --strict
```

Result: passed

### Frontend targeted tests

```bash
npm run test -- src/api/__tests__/strategy.test.ts src/api/adapters/marketAdapter.spec.ts src/api/services/__tests__/strategyService.msw.spec.ts src/composables/__tests__/useStrategy.spec.ts tests/unit/use-strategy.spec.ts tests/unit/config/console-log-cleanup-batch-21.spec.ts
```

Result:

- Test files: 6 passed
- Tests: 38 passed

### Explicit mock strategy-route validation

```bash
npm run test -- tests/unit/mockApiClient-strategy-routes.spec.ts
```

Result:

- Test files: 1 passed
- Tests: 2 passed

## Mock Acceptance vs Real Verification

- `mock acceptance`:
  - still supported through `VITE_USE_MOCK_DATA=true`
  - now uses `/v1/strategy/*` through shared `apiClient` + `mockApiClient`
- `real mainline verified`:
  - no longer depends on service-level `VITE_APP_MODE`
  - no longer silently substitutes adapter mock payloads on request failure

## Remaining Follow-up

- Historical reports outside the execution-facing docs still mention `VITE_APP_MODE` or old fallback models; those remain documentation cleanup work, not a blocker for current runtime alignment.

## Archive Readiness

- OpenSpec implementation status: complete
- OpenSpec validation status: passed (`openspec validate align-mock-data-governance-with-verified-pages --strict`)
- Runtime/test evidence status: passed for the targeted frontend test batch recorded above
- Archive status: not yet archived

This change is implementation-complete and archive-ready from a spec/task perspective, but it should only be archived after the corresponding runtime change is merged/deployed according to the normal OpenSpec archive flow.

Explicit non-goals for this closeout:

- It does not claim that every historical mock-related document in the repository has been cleaned up.
- It does not claim that all unrelated frontend auth/routing work in the current worktree is part of this change.
- It does not convert archive readiness into deployment completion.
