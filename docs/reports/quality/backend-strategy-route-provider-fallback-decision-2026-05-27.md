# Backend Strategy Route Provider Fallback Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.182
- State: ready for review
- Date: 2026-05-27
- Base HEAD: `0398eb81259bba5c7d8c8ba6479056554e13d064`
- Parent decision: G2.181, PR `#334`, merge commit `0398eb81259bba5c7d8c8ba6479056554e13d064`
- Scope: governance decision package only

Boundary note: this report does not authorize backend source edits, frontend
source edits, tests, generated client updates, docs/API edits, OpenSpec proposal
creation, issue label changes, PM2 commands, runtime rollout, compatibility
deletion, adapter-local cleanup implementation, backtest task helper
implementation, route behavior changes, or OpenAPI exposure changes.

## Purpose

G2.181 selected the Strategy route/provider fallback residual as the next
governance target. This package checks whether that residual should become a
source implementation lane or be retained as an intentional route-local provider
fallback.

## Route Evidence

At HEAD `0398eb81259bba5c7d8c8ba6479056554e13d064`,
`web/backend/app/api/strategy_management/_strategy_execution_router.py` has
`6` `get_strategy_service` hits:

| Class | Lines | Current meaning |
|---|---|---|
| Import | `20` | Imports `StrategyService` and the public getter fallback. |
| Route-local provider | `33`, `34` | Defines `get_strategy_service_dependency()` and returns the public fallback. |
| Endpoint dependency usages | `388`, `454`, `499` | Three handlers receive `StrategyService` through `Depends(get_strategy_service_dependency)`. |

The three endpoint dependency usages are:

| Method | Path | Function |
|---|---|---|
| GET | `/results` | `query_strategy_results` |
| GET | `/matched-stocks` | `get_matched_stocks` |
| GET | `/stats/summary` | `get_strategy_summary` |

The route handlers do not call `get_strategy_service()` directly. They depend
on a route-local provider through FastAPI `Depends`.

## Existing Test Evidence

Focused test executed in this branch:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_strategy_management_route_provider.py -q --no-cov --tb=short
```

Result:

```text
5 passed in 4.79s
```

The test file verifies that:

- the route module exposes `get_strategy_service_dependency()`
- the affected handlers depend on the route-local provider
- injected fake strategy services are used by the three affected handlers

## Comparison Evidence

A repository scan found `21` backend API files using `Depends(get_*_dependency)`
style route dependency providers. This means the Strategy execution router is
not an isolated pattern outlier; the remaining fallback is a route-local
provider fallback, not a direct handler body call.

## Decision

Retain the current route-local provider fallback. Do not open a source
implementation lane from this residual.

Rationale:

- The route already has an explicit provider boundary at the handler signature.
- The only direct getter call is inside the provider helper.
- Focused tests verify the provider seam and injected-service behavior.
- Replacing the fallback would be a broader route dependency-provider policy
  change, not a narrow Strategy getter cleanup.

## Deferred Work

This package does not change the remaining Strategy getter residual classes:

- `strategy_adapter.py`: still a future adapter-local lifecycle cleanup
  candidate only.
- `backtest_tasks.py`: no-op unless fresh current-HEAD evidence contradicts the
  closed resolver-seam handling.
- `strategy_service.py`: retained public getter definition.

## Next Gate

Review G2.182. If accepted, prepare G2.183 to decide whether the remaining
Strategy getter work is:

- track closeout with retained residuals, or
- a separate adapter-local lifecycle cleanup authorization package.

No source lane is opened by G2.182.
