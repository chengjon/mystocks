# Backend Strategy Service Route Provider Injection Implementation

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Task: G2.166 Strategy route provider injection implementation  
Branch: `g2-166-strategy-route-provider-injection`  
Base: `wip/root-dirty-20260403`  
Current HEAD before this commit: `e5f8a4a2a53bc707a57732ac5c6e14d1f63a5444`  
Created: 2026-05-27

Scope: G2.166 narrow source implementation lane authorized by G2.165. This implementation only changes the strategy execution route module, a focused route-provider test, the steward tree, this report, its generated JSON artifact, and the mainline task card.

Boundary: this PR does not edit `web/backend/app/services/strategy_service.py`, adapter/provider duplication, task/backtest resolution, route paths, response models, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, config, or scripts. Public `get_strategy_service()` fallback compatibility is preserved.

## Summary

G2.166 replaced the three direct route-handler body calls to `get_strategy_service()` in `_strategy_execution_router.py` with a route-local FastAPI dependency provider.

The new provider is:

- `get_strategy_service_dependency() -> StrategyService`

It delegates to the existing public `get_strategy_service()` fallback. The three route handlers now receive `strategy_service: StrategyService = Depends(get_strategy_service_dependency)` and use that injected object.

## Parent Authorization

| Input | State |
|---|---|
| Parent package | G2.165 Strategy service seam design and authorization |
| Parent PR | `#318`, merged |
| Parent merge commit | `e5f8a4a2a53bc707a57732ac5c6e14d1f63a5444` |
| Parent evidence | `docs/reports/quality/backend-strategy-service-seam-design-authorization-2026-05-27.md` |
| Parent generated artifact | `.planning/codebase/generated/strategy-service-seam-design-authorization-2026-05-27.json` |

G2.165 authorized only this source slice:

- application source: `web/backend/app/api/strategy_management/_strategy_execution_router.py`
- focused test: `web/backend/tests/test_strategy_management_route_provider.py`

## GitNexus Evidence Before Edits

| Target | Risk | Impact |
|---|---:|---|
| `get_strategy_service` | CRITICAL | impacted `13`, direct `6`, processes `0` |
| `query_strategy_results` | LOW | impacted `0`, direct `0`, processes `0` |
| `get_matched_stocks` | LOW | impacted `1`, direct `1`, processes `0`; direct caller is `get_strategy_summary` |
| `get_strategy_summary` | LOW | impacted `0`, direct `0`, processes `0` |

The shared getter remains CRITICAL because it is still a public fallback used by adapter and task surfaces. The actual G2.166 edit target is the LOW-risk route-handler slice authorized by G2.165.

## TDD Record

Red test:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_strategy_management_route_provider.py -q --no-cov
5 failed in 4.57s
```

Expected failures:

- missing `get_strategy_service_dependency()`;
- missing `strategy_service` handler parameters;
- direct function calls could not pass an injected fake strategy service.

Green test:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_strategy_management_route_provider.py -q --no-cov
5 passed in 4.36s
```

The direct-call test had to pass explicit plain parameter values because direct invocation of FastAPI handlers otherwise passes `Query(...)` default objects into business logic. This is test-call hygiene only; it does not change runtime route behavior.

## Implementation Details

Changed source file:

- `web/backend/app/api/strategy_management/_strategy_execution_router.py`

Changes:

- import `Depends`;
- import `StrategyService` for dependency parameter typing;
- add route-local provider `get_strategy_service_dependency()`;
- inject `strategy_service` into:
  - `query_strategy_results`;
  - `get_matched_stocks`;
  - `get_strategy_summary`;
- replace each route handler's body-local `service = get_strategy_service()` with `service = strategy_service`.

Changed focused test file:

- `web/backend/tests/test_strategy_management_route_provider.py`

Test coverage added:

- provider delegates to public fallback;
- all three handlers expose a `Depends(get_strategy_service_dependency)` parameter;
- direct handler calls can use a fake injected service without calling the public singleton getter.

## Closure Metrics

| Metric | Before | After | Notes |
|---|---:|---:|---|
| Route-handler body calls to `get_strategy_service()` in `_strategy_execution_router.py` | `3` | `0` | Target met. |
| `Depends(get_strategy_service_dependency)` sites in `_strategy_execution_router.py` | `0` | `3` | One per authorized handler. |
| Route-local provider fallback call | `0` | `1` | Expected; preserves public fallback compatibility. |
| Adapter lazy getter calls | unchanged | unchanged | Deferred by G2.165. |
| Backtest task resolver call | unchanged | unchanged | Deferred by G2.165. |

Static scan after implementation:

```json
{
  "route_file_body_get_strategy_service_calls": 1,
  "route_handler_body_get_strategy_service_calls": 0,
  "provider_fallback_calls": 1,
  "depends_sites": 3
}
```

The remaining route-file call is the provider fallback itself: `return get_strategy_service()`.

## Verification

| Check | Result |
|---|---|
| Parent PR state | PR `#318` merged; merge commit `e5f8a4a2a53bc707a57732ac5c6e14d1f63a5444` |
| TDD red | `5 failed in 4.57s` before implementation |
| TDD green | `5 passed in 4.36s` after implementation |
| Strategy route OpenAPI docs focused test | `1 passed in 13.62s` |
| Backtest task regressions | `2 passed in 1.94s` |
| Ruff touched backend files | `All checks passed!` |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `warnings=0` |
| Static closure scan | route handler body calls `3 -> 0`, provider fallback preserved |

## Rollback

If this implementation changes route behavior, OpenAPI exposure, response shape, adapter behavior, task/backtest resolution, or public `get_strategy_service()` compatibility, revert this PR. Rollback is a normal source/test/governance revert of this PR only.

## Next Gate

Review this implementation package. If accepted and merged, start G2.167 as a governance-only service getter inventory refresh after Strategy route provider injection.
