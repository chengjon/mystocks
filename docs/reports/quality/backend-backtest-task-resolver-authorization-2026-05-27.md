# Backend Backtest Task Resolver Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.169
- State: ready for review
- Date: 2026-05-27
- Current HEAD: `9994a89c73e38a11b907060bb11663df35eff6e6`
- Parent PR: `#321` merged, `docs(governance): split strategy service residual tracks`
- Scope: authorization-only package for `web/backend/app/tasks/backtest_tasks.py::_resolve_backtest_data_source`

## Boundary

This package does not edit backend source, tests, runtime behavior, route behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec content, scripts, config, or issue labels.

The only decision made here is whether a future G2.170 source lane may be opened for the backtest task resolver seam. Source implementation remains frozen until this package is reviewed and accepted.

## Parent Decision

G2.168 split the remaining Strategy service getter residual into three separately governed tracks:

| Track | Disposition |
|---|---|
| Strategy route provider fallback | Retain as intentional compatibility/provider fallback. |
| Backtest task data-source resolver | Select as next narrow authorization candidate. |
| Strategy adapter/provider duplication | Defer to a separate adapter design track. |

PR `#321` merged that split into `wip/root-dirty-20260403` at `9994a89c73e38a11b907060bb11663df35eff6e6`.

## Current Resolver State

Target file: `web/backend/app/tasks/backtest_tasks.py`

Current resolver facts:

- `_resolve_backtest_data_source` spans lines `18-34`.
- `run_backtest_task` spans lines `35-128`.
- `run_backtest_task` calls `_resolve_backtest_data_source` once.
- `_resolve_backtest_data_source` accepts `data_source_mode` values `strategy_service` and `auto`.
- `_resolve_backtest_data_source` imports and calls public `get_strategy_service()` internally.
- Unsupported mode still raises `ValueError` with the existing Chinese message.

Current resolver body excerpt:

```python
def _resolve_backtest_data_source(backtest_config: dict):
    data_source_mode = backtest_config.get("data_source_mode", "strategy_service")
    if data_source_mode not in {"strategy_service", "auto"}:
        raise ValueError(f"不支持的回测数据源策略: {data_source_mode}")

    from app.services.strategy_service import get_strategy_service

    return get_strategy_service()
```

## GitNexus Evidence

`_resolve_backtest_data_source`:

- Risk: LOW
- Direct impacted caller: `1`
- Affected processes: `0`
- Affected modules: `1`
- Direct caller: `web/backend/app/tasks/backtest_tasks.py::run_backtest_task`
- Outgoing call: `web/backend/app/services/strategy_service.py::get_strategy_service`

`run_backtest_task`:

- Located at `web/backend/app/tasks/backtest_tasks.py:35-128`
- Calls `_resolve_backtest_data_source`, `_save_backtest_results`, and `_update_backtest_status`
- No GitNexus execution process was attached to this task symbol in the current index

The target is a narrow task-local seam. The broader public `get_strategy_service` getter remains CRITICAL from prior G2.168 evidence and must not be treated as mechanically safe to remove.

## Verification

Commands executed at current HEAD `9994a89c73e38a11b907060bb11663df35eff6e6`:

| Check | Result |
|---|---|
| Parent PR state | `#321` is `MERGED`; merge commit `9994a89c73e38a11b907060bb11663df35eff6e6` |
| GitNexus impact | `_resolve_backtest_data_source` LOW, direct caller `run_backtest_task` |
| Static scan | resolver still owns direct internal `get_strategy_service()` fallback |
| Backtest regression test | `web/backend/tests/test_backtest_tasks_regressions.py`: `2 passed` |
| Strategy route provider regression | `web/backend/tests/test_strategy_management_route_provider.py`: `5 passed` |

No OpenAPI smoke was required for this authorization package because no route, response model, OpenAPI schema, or runtime endpoint file is edited. Future G2.170 may include OpenAPI smoke only as a no-drift sanity check if the implementer decides it is useful.

## Authorization Decision

Approve a future G2.170 source-capable lane only if it stays within the scope below.

Allowed future source/test scope:

| Path | Future role |
|---|---|
| `web/backend/app/tasks/backtest_tasks.py` | Introduce a narrow backtest task resolver/provider seam while preserving current data-source behavior. |
| `web/backend/tests/test_backtest_tasks_regressions.py` | Add or update focused regression coverage for the resolver seam and existing mode behavior. |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Record completion and review state. |
| `.planning/codebase/generated/*backtest-task-resolver*2026-05-27.json` | Record machine-readable evidence. |
| `docs/reports/quality/*backtest-task-resolver*2026-05-27.md` | Record implementation or closeout evidence. |
| `governance/mainline/task-cards/pr-*.yaml` | Record mainline scope gate metadata. |

Required future implementation properties:

- Preserve `data_source_mode` compatibility for `strategy_service` and `auto`.
- Preserve the existing unsupported-mode `ValueError` behavior.
- Keep public `get_strategy_service()` available and unchanged.
- Avoid editing Strategy route provider fallback from G2.166.
- Avoid editing Strategy adapter/provider helpers from the separate adapter design track.
- Use TDD red/green before source implementation.
- Run GitNexus impact before editing `_resolve_backtest_data_source` or any other modified symbol.
- Run staged GitNexus `detect_changes` before commit.

Expected future implementation outcome:

- `run_backtest_task` behavior remains unchanged.
- The resolver gains a testable dependency seam for the Strategy data-source provider.
- Direct Strategy service acquisition remains available as a compatibility fallback, but the task resolver becomes easier to override in tests and future lifecycle-DI migration.

## Non-Goals

G2.170 must not:

- Edit `web/backend/app/services/strategy_service.py`.
- Edit `web/backend/app/api/strategy_management/_strategy_execution_router.py`.
- Edit `web/backend/app/services/adapters/strategy_adapter.py`.
- Edit `web/backend/app/services/data_adapters/strategy.py`.
- Delete, privatize, rename, or change public `get_strategy_service()`.
- Change Celery app configuration, task queue semantics, retry behavior, status persistence, or result persistence.
- Change route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec changes, scripts, config, or issue-label state.
- Treat the broader Strategy service getter seam as solved by the backtest task resolver lane.

## Review Gate

Before opening G2.170, a reviewer must confirm:

1. G2.169 is accepted as authorization-only.
2. The future source scope remains limited to `backtest_tasks.py` plus focused regression tests.
3. Strategy adapter/provider duplication is still deferred to its own design track.
4. Route provider fallback remains intentionally retained.
5. No implementation work is performed from this G2.169 package.

## Rollback

If this authorization is rejected or superseded, revert only the G2.169 governance PR. That removes this report, the generated JSON artifact, the PR task card, and the steward-tree entry. No backend runtime behavior is affected because no source or test file is edited here.

