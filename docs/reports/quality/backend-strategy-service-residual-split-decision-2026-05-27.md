# Backend Strategy Service Residual Split Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: Ready for review

Scope: G2.168 decision-only Strategy residual split after G2.167.

Boundary: this is a decision and routing package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not authorize implementation.

Parent: G2.167, PR `#320`, merged as `8f3cc0c15ec80b5e9acdbdf83f407abee44a6bd2`.

Current HEAD: `8f3cc0c15ec80b5e9acdbdf83f407abee44a6bd2`.

Prepared at: `2026-05-27T09:47:49+08:00`.

## Purpose

Split the remaining `get_strategy_service()` residual after the Strategy route provider injection and candidate refresh.

This package prevents the next agent from treating the remaining Strategy residual as one mechanical replacement. The remaining calls have different runtime surfaces, tests, and rollback boundaries.

## Parent Verification

| Check | Result |
|---|---|
| PR `#320` state | `MERGED`, merge commit `8f3cc0c15ec80b5e9acdbdf83f407abee44a6bd2` |
| G2.167 conclusion | no source implementation authorized |
| G2.167 next gate | split Strategy residual into adapter/provider duplication vs backtest task resolution |

## Current Residual Map

| Track | File | Line | Function | Current role | Disposition |
|---|---|---:|---|---|---|
| Route provider fallback | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 34 | `get_strategy_service_dependency` | FastAPI provider fallback introduced by G2.166 | Retain; not a debt target. |
| Strategy adapter/provider duplication | `web/backend/app/services/adapters/strategy_adapter.py` | 45 | `_get_strategy_service` | lazy service resolver for one adapter package | Separate adapter design track. |
| Strategy adapter/provider duplication | `web/backend/app/services/data_adapters/strategy.py` | 42 | `_get_strategy_service` | lazy service resolver for the parallel adapter package | Separate adapter design track. |
| Backtest task data-source resolution | `web/backend/app/tasks/backtest_tasks.py` | 31 | `_resolve_backtest_data_source` | Celery task data-source resolver | Next authorization candidate. |

Static route status remains closed:

| Route metric | Count |
|---|---:|
| Strategy route-handler body calls to `get_strategy_service()` | 0 |
| Route provider fallback calls | 1 |
| `Depends(get_strategy_service_dependency)` sites | 3 |

## GitNexus Evidence

| Symbol | Risk | Impacted | Direct | Processes | Interpretation |
|---|---:|---:|---:|---:|---|
| `get_strategy_service` | CRITICAL | 13 | 6 | 0 | Overall Strategy residual remains high-risk because adapter, route-provider, and task surfaces still converge on the public getter. |
| `_resolve_backtest_data_source` | LOW | 1 | 1 | 0 | The backtest resolver itself has one direct caller, `run_backtest_task`; it is the narrowest remaining source candidate. |

Adapter helper contexts:

| Helper | Incoming callers | Outgoing getter |
|---|---:|---|
| `web/backend/app/services/adapters/strategy_adapter.py::_get_strategy_service` | 2, `_fetch_strategy_data` and `health_check` | `get_strategy_service` |
| `web/backend/app/services/data_adapters/strategy.py::_get_strategy_service` | 2, `_fetch_strategy_data` and `health_check` | `get_strategy_service` |

The adapter helpers are structurally duplicated but not low-risk cleanup. They sit in two adapter package topologies and should be governed through an adapter-specific design packet before source work.

## Verification Snapshot

| Check | Result |
|---|---|
| `test_strategy_management_route_provider.py` | `5 passed in 4.07s` |
| `test_backtest_tasks_regressions.py` | `2 passed in 2.33s` |
| `test_adapter_mock_fallback_controls.py` | `6 passed in 0.23s` |
| OpenAPI smoke with non-secret minimal env | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0`, `total_warnings_captured=121` |

The OpenAPI smoke is included as a current-head sanity check. G2.168 does not modify route/OpenAPI code.

## Decision

Split the remaining Strategy residual into three tracks:

1. Route provider fallback: retain as intentional compatibility and dependency-injection fallback.
2. Backtest task data-source resolution: select as the next authorization candidate because its direct blast radius is LOW and it already has focused regression coverage.
3. Strategy adapter/provider duplication: defer to a separate adapter design package because it spans two parallel adapter packages and should not be mixed with task runtime resolution.

No source implementation is authorized by this package.

## Next Gate

Start G2.169 as an authorization-only package for `web/backend/app/tasks/backtest_tasks.py::_resolve_backtest_data_source`.

G2.169 must define:

- exact permitted source and test paths;
- whether the task resolver receives an injectable resolver/provider or another narrow seam;
- how `data_source_mode` behavior remains compatible for `strategy_service` and `auto`;
- required red/green test expansion in `web/backend/tests/test_backtest_tasks_regressions.py`;
- rollback condition that preserves public `get_strategy_service()` fallback compatibility;
- explicit non-goals for Strategy adapter modules, Strategy route modules, `strategy_service.py`, route/OpenAPI contracts, frontend, PM2, OpenSpec, config, scripts, and issue labels.

Only after G2.169 is reviewed and accepted should a source implementation lane be opened.
