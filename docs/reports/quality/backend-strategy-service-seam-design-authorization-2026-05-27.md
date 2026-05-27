# Backend Strategy Service Seam Design Authorization

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Task: G2.165 Strategy service seam design and authorization  
Branch: `g2-165-strategy-service-seam-design-authorization`  
Base: `wip/root-dirty-20260403`  
Current HEAD: `3355c50c5a0c9cf5b20dd9d33300a695e5a3807b`  
Created: 2026-05-27

Scope: G2.165 authorization package only. No backend source, backend test, route/API behavior, OpenAPI exposure, frontend, PM2, OpenSpec, config, script, issue-label, or runtime behavior change is performed in this package.

Boundary: this is a source-implementation authorization package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not perform implementation.

## Decision

Authorize the next gate as G2.166: Strategy route provider injection implementation lane.

G2.166 may only address the three direct `get_strategy_service()` body calls in `web/backend/app/api/strategy_management/_strategy_execution_router.py`.

G2.166 must not edit adapter/provider duplication or task/backtest data-source resolution. Those are separate surfaces with different runtime contracts and must remain deferred until a later decision package explicitly selects them.

## Parent State

| Input | State |
|---|---|
| Parent package | G2.164 next high-risk service getter track selection after Indicator/Data |
| Parent PR | `#317`, merged |
| Parent merge commit | `3355c50c5a0c9cf5b20dd9d33300a695e5a3807b` |
| Parent evidence | `docs/reports/quality/backend-next-high-risk-service-getter-track-selection-after-indicator-data-2026-05-27.md` |
| Parent generated artifact | `.planning/codebase/generated/next-high-risk-service-getter-track-selection-after-indicator-data-2026-05-27.json` |

G2.164 selected the Strategy adapter / strategy-management seam as the next high-risk service getter track, but did not authorize source implementation. G2.165 narrows that selected track into a single implementable slice.

## GitNexus Evidence

`get_strategy_service` remains a high-risk shared getter:

| Target | Risk | Impacted | Direct callers | Affected processes | Affected modules |
|---|---:|---:|---:|---:|---|
| `get_strategy_service` | CRITICAL | `13` | `6` | `0` | `Data_adapters`, `Adapters`, `Strategy_management`, `Cdp`, `Tasks` |

Direct caller matrix:

| Direct caller | File | Surface | G2.165 disposition |
|---|---|---|---|
| `_get_strategy_service` | `web/backend/app/services/data_adapters/strategy.py` | Adapter/provider duplication | Defer. Do not touch in G2.166. |
| `_get_strategy_service` | `web/backend/app/services/adapters/strategy_adapter.py` | Adapter/provider duplication | Defer. Do not touch in G2.166. |
| `query_strategy_results` | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | Strategy-management route handler | Authorize for G2.166 provider injection. |
| `get_matched_stocks` | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | Strategy-management route handler | Authorize for G2.166 provider injection. |
| `get_strategy_summary` | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | Strategy-management route handler | Authorize for G2.166 provider injection. |
| `_resolve_backtest_data_source` | `web/backend/app/tasks/backtest_tasks.py` | Task/backtest resolution | Defer. Do not touch in G2.166. |

Focused caller impact:

| Target | Risk | Impact |
|---|---:|---|
| `query_strategy_results` | LOW | impacted `0`, direct `0`, processes `0` |
| `_resolve_backtest_data_source` | LOW | impacted `1`, direct `1`, processes `0`; direct caller is `run_backtest_task` |

This split shows that the route-handler body-call slice is the smallest safe first implementation lane. The shared getter itself remains CRITICAL, so the implementation must be narrow and preserve the public fallback.

## Current-Head Hit Classification

Scope: `web/backend/app/api`, `web/backend/app/services`, `web/backend/app/tasks`, and `web/backend/tests` at HEAD `3355c50c5a0c9cf5b20dd9d33300a695e5a3807b`.

| Category | Count | Notes |
|---|---:|---|
| Definition | `1` | `web/backend/app/services/strategy_service.py:455` |
| Import | `4` | route module, two adapter modules, backtest task module |
| FastAPI `Depends(get_strategy_service...)` | `0` | no provider injection exists yet |
| Application body calls | `6` | three route calls, two adapter lazy calls, one backtest task call |
| Backend test references | `1` | `test_backtest_tasks_regressions.py` monkeypatches the service getter module |

Application body calls:

| Body call | G2.166 disposition |
|---|---|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py:399` | Replace through route provider injection. |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py:461` | Replace through route provider injection. |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py:503` | Replace through route provider injection. |
| `web/backend/app/services/adapters/strategy_adapter.py:45` | Defer adapter/provider duplication. |
| `web/backend/app/services/data_adapters/strategy.py:42` | Defer adapter/provider duplication. |
| `web/backend/app/tasks/backtest_tasks.py:31` | Defer task/backtest resolution. |

## Consumer Contract Matrix

| Consumer | Current behavior | Contract to preserve in G2.166 |
|---|---|---|
| `query_strategy_results` | Builds optional date filter, calls `service.query_strategy_results(...)`, returns `UnifiedResponse[Dict[str, Any]]` success payload, raises `BusinessException` on failure. | Same route path, method, query parameters, response model, response body shape, error handling, tags, summaries, and examples. |
| `get_matched_stocks` | Builds optional date filter, calls `service.query_strategy_results(...)`, filters matched stocks, returns `UnifiedResponse[Dict[str, Any]]`. | Same route contract and filtered payload shape. |
| `get_strategy_summary` | Builds date filter, calls `service.get_strategy_definitions()` and `service.query_strategy_results(...)`, returns per-strategy summary. | Same route contract and summary payload shape. |
| Strategy adapters | Lazy `_get_strategy_service()` caches public singleton fallback. | No change in G2.166. |
| Backtest task | `_resolve_backtest_data_source()` uses public singleton fallback for `strategy_service` / `auto` modes. | No change in G2.166. |

## G2.166 Authorized Scope

Allowed application source paths:

- `web/backend/app/api/strategy_management/_strategy_execution_router.py`

Allowed focused test paths:

- `web/backend/tests/test_strategy_management_route_provider.py` (new or existing if already present)
- `web/backend/tests/test_health_route_conflicts.py`, only for import/collection verification or a reviewed route-contract assertion update caused by the authorized route file

Allowed governance paths:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/strategy-service-route-provider-injection-implementation-2026-05-27.json`
- `docs/reports/quality/backend-strategy-service-route-provider-injection-implementation-2026-05-27.md`
- `governance/mainline/task-cards/pr-319.yaml`

Recommended implementation direction:

1. Add a local FastAPI provider wrapper in `_strategy_execution_router.py`, for example `get_strategy_service_dependency() -> StrategyService`, which delegates to the existing public `get_strategy_service()` fallback.
2. Inject that provider into `query_strategy_results`, `get_matched_stocks`, and `get_strategy_summary` with `Depends(...)`.
3. Remove the three route-handler body calls to `get_strategy_service()`.
4. Preserve the public `get_strategy_service()` function, singleton behavior, import compatibility, route paths, OpenAPI exposure, response models, operation IDs, examples, and frontend contract.

Target closure metric:

- direct body calls to `get_strategy_service()` in `_strategy_execution_router.py`: `3 -> 0`
- direct body calls to `get_strategy_service()` outside `_strategy_execution_router.py`: unchanged in G2.166
- public `get_strategy_service()` definition: unchanged

## G2.166 Forbidden Scope

G2.166 must not:

- edit `web/backend/app/services/strategy_service.py`;
- delete, privatize, rename, or change `get_strategy_service()`;
- edit `web/backend/app/services/data_adapters/strategy.py`;
- edit `web/backend/app/services/adapters/strategy_adapter.py`;
- edit `web/backend/app/tasks/backtest_tasks.py`;
- edit broad strategy-management routers outside `_strategy_execution_router.py`;
- change route paths, methods, response models, operation IDs, tags, summaries, descriptions, examples, OpenAPI exposure, or response body shapes;
- change frontend callers, PM2 workflows, config, scripts, OpenSpec state, or GitHub issue labels;
- fold realtime/socket, Dashboard/TDX, Indicator/Data residual, root facade compatibility, adapter/provider duplication, or task/backtest resolution into the route provider implementation.

## Required G2.166 Gates

Before implementation:

1. Confirm the G2.166 worktree contains PR `#318` after it is merged.
2. Re-run GitNexus impact for `get_strategy_service` and the three route handlers.
3. Stop and return to review if new HIGH or CRITICAL dependencies appear outside the route-handler scope recorded here.

During implementation:

1. Use TDD. Add a failing focused test that proves `_strategy_execution_router.py` exposes a route-local strategy service provider and that the three route handlers no longer call the public getter in their bodies.
2. Add or update direct function tests with a fake strategy service when practical, so the route handlers are proven to consume the injected service.
3. Keep route behavior and response contract unchanged.

Before PR:

1. `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_strategy_management_route_provider.py -q --no-cov`
2. `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_v1_strategy_management_endpoints_have_success_examples_and_parameter_docs -q --no-cov`
3. `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_backtest_tasks_regressions.py -q --no-cov`
4. Ruff check for touched backend files.
5. OpenAPI smoke: `routes=548`, `paths=500`, `duplicate_operation_ids=0` expected unless a later current-head baseline changes.
6. Staged GitNexus detect changes.
7. Mainline scope gate for the future PR task card.
8. `gitnexus analyze --with-gitignore` after commit.

## Baseline Verification

| Check | Result |
|---|---|
| Parent PR state | PR `#317` merged; merge commit `3355c50c5a0c9cf5b20dd9d33300a695e5a3807b` |
| Current HEAD | `3355c50c5a0c9cf5b20dd9d33300a695e5a3807b` |
| GitNexus impact: `get_strategy_service` | CRITICAL, impacted `13`, direct `6`, processes `0` |
| GitNexus context: `get_strategy_service` | incoming calls match the six direct callers listed above |
| Static hit classification | completed; `6` application body calls, `3` authorized in G2.166 |
| Strategy route OpenAPI docs focused test | `1 passed in 18.87s` |
| Backtest task regressions | `2 passed in 3.14s` |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `warnings=0` |

## Rollback

If G2.166 changes route behavior, OpenAPI exposure, response shape, or service lifecycle beyond the authorized route provider injection, revert the implementation PR. The public `get_strategy_service()` function and the adapter/backtest consumers must remain available, so rollback should be a normal source revert rather than a compatibility-restoration project.

## Next Gate

Review this package. If accepted and merged, start G2.166 as the narrow Strategy route provider injection source implementation lane. Do not start source edits from G2.165 itself.
