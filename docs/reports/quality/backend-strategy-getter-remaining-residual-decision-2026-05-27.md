# Backend Strategy Getter Remaining Residual Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.183
- State: ready for review
- Date: 2026-05-27
- Base HEAD: `597f8186092b4ad3d0704326e292c5e4fa075f15`
- Parent decision: G2.182, PR `#335`, merge commit `597f8186092b4ad3d0704326e292c5e4fa075f15`
- Scope: governance decision package only

Boundary note: this report does not authorize backend source edits, frontend
source edits, tests, generated client updates, docs/API edits, OpenSpec proposal
creation, issue label changes, PM2 commands, runtime rollout, compatibility
deletion, adapter-local cleanup implementation, backtest task helper
implementation, route behavior changes, or OpenAPI exposure changes.

## Purpose

G2.182 retained the Strategy route/provider fallback as an intentional
route-local provider seam. This package decides whether the remaining Strategy
getter residuals justify a new adapter-local lifecycle cleanup authorization
package or whether the Strategy getter track can close with retained residuals.

## Residual Scan

At HEAD `597f8186092b4ad3d0704326e292c5e4fa075f15`, production `.py`
`get_strategy_service` hits under `web/backend/app` remain `19`:

| File | Hits | Lines | Decision |
|---|---:|---|---|
| `web/backend/app/services/adapters/strategy_adapter.py` | 10 | `40`, `47`, `49`, `106`, `120`, `136`, `153`, `183`, `332`, `344` | Retain as adapter-local helper/provider seam. Do not open adapter-local cleanup authorization from this package. |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 6 | `20`, `33`, `34`, `388`, `454`, `499` | Retained by G2.182 as route-local provider fallback. |
| `web/backend/app/tasks/backtest_tasks.py` | 2 | `19`, `21` | Retain as backtest task resolver fallback unless fresh current-HEAD evidence contradicts resolver-seam tests. |
| `web/backend/app/services/strategy_service.py` | 1 | `455` | Retain as public compatibility getter definition. |

## Focused Test Evidence

Focused residual tests executed in this branch:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_adapter_mock_fallback_controls.py web/backend/tests/test_backtest_tasks_regressions.py web/backend/tests/test_strategy_management_route_provider.py -q --no-cov --tb=short
```

Result:

```text
16 passed in 4.52s
```

The test set covers:

- `StrategyDataSourceAdapter` provider/fallback controls
- backtest task resolver fallback
- Strategy route provider fallback

## Decision

Close the current Strategy getter residual track with retained residuals. Do
not open an adapter-local lifecycle cleanup authorization package from this
decision.

Rationale:

- The route/provider fallback is already retained by G2.182.
- The adapter-local residuals are internal helper/provider seam calls after the
  approved constructor provider seam.
- The backtest residual is a resolver fallback covered by focused regression
  tests.
- The public getter definition remains the compatibility entrypoint.
- Focused tests covering all remaining Strategy residual surfaces passed.

## Closure Boundary

This closeout is not a statement that every `get_strategy_service` token should
disappear. It means the remaining tokens have classified ownership and should
not be used to reopen a generic Strategy getter source lane.

Future changes may still propose a broader service dependency-provider policy,
but that must be a separate proposal or authorization package with fresh
evidence, impact analysis, tests, and review.

## Next Gate

Review G2.183. If accepted, return the service lifecycle DI queue to selecting
the next non-Strategy getter candidate through a separate decision package.

No source lane is opened by G2.183.
