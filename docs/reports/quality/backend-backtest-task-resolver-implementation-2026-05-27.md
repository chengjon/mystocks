# Backend Backtest Task Resolver Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.170
- State: ready for review
- Date: 2026-05-27
- Base HEAD: `bc2c0b8e102c455c09ba718b3eff982bf0f6e5e7`
- Parent PR: `#322` merged, `docs(governance): authorize backtest task resolver seam`
- Scope: path-limited source implementation for `web/backend/app/tasks/backtest_tasks.py::_resolve_backtest_data_source`

## Boundary

This implementation stays inside the G2.169 authorization boundary.

Source/test files changed:

- `web/backend/app/tasks/backtest_tasks.py`
- `web/backend/tests/test_backtest_tasks_regressions.py`

Governance artifacts changed:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/backtest-task-resolver-implementation-2026-05-27.json`
- `docs/reports/quality/backend-backtest-task-resolver-implementation-2026-05-27.md`
- `governance/mainline/task-cards/pr-323.yaml`

Out of scope and untouched:

- `web/backend/app/services/strategy_service.py`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py`
- `web/backend/app/services/adapters/strategy_adapter.py`
- `web/backend/app/services/data_adapters/strategy.py`
- Route/API behavior
- OpenAPI exposure
- Frontend
- PM2 workflows
- OpenSpec changes/specs
- Config/scripts
- Issue labels

## Implementation

The backtest task resolver now has a task-local Strategy data-source provider seam:

```python
def _get_strategy_data_source():
    from app.services.strategy_service import get_strategy_service

    return get_strategy_service()
```

`_resolve_backtest_data_source()` now validates `data_source_mode` and delegates acquisition to `_get_strategy_data_source()`:

```python
return _get_strategy_data_source()
```

This keeps the public `get_strategy_service()` compatibility fallback intact while moving the resolver away from an inline direct getter call. Tests can now override the task-local provider seam without patching the service module directly.

## Static Result

Post-change scan:

| Metric | Result |
|---|---:|
| `_get_strategy_data_source` lines | `18-23` |
| `_resolve_backtest_data_source` lines | `24-38` |
| `run_backtest_task` lines | `39-132` |
| Resolver direct `get_strategy_service` mentions | `0` |
| Resolver `_get_strategy_data_source` mentions | `1` |
| Helper `get_strategy_service` mentions | `2` |
| `run_backtest_task` resolver calls | `1` |
| Provider seam test present | `true` |
| Unsupported-mode test uses `pytest.raises` | `true` |

## GitNexus Evidence

Pre-edit impact for `_resolve_backtest_data_source`:

- Risk: LOW
- Direct impacted caller: `1`
- Direct caller: `web/backend/app/tasks/backtest_tasks.py::run_backtest_task`
- Affected processes: `0`
- Affected modules: `1`

No HIGH or CRITICAL warning was returned for the edited resolver symbol.

## TDD Evidence

Red test:

```text
web/backend/tests/test_backtest_tasks_regressions.py::test_resolve_backtest_data_source_uses_task_local_provider
1 failed in 2.66s
```

Expected failure:

```text
AssertionError: assert <fallback object> is <fake provider object>
```

Green test:

```text
web/backend/tests/test_backtest_tasks_regressions.py
3 passed in 2.60s
```

After ruff/format refactor, the final focused test remained green:

```text
web/backend/tests/test_backtest_tasks_regressions.py
3 passed in 3.18s
```

## Verification

| Check | Result |
|---|---|
| Backtest task regressions | `3 passed in 3.18s` |
| Strategy route provider regressions | `5 passed in 6.29s` |
| Ruff touched backend files | `All checks passed!` |
| Black touched backend files | `2 files would be left unchanged` |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0`, `total_warnings_captured=121` |

OpenAPI smoke used minimal non-secret placeholder environment values because the application import gate requires runtime configuration variables. This implementation does not edit route registration or OpenAPI schema files.

## Behavior Compatibility

Preserved behavior:

- `data_source_mode` default remains `strategy_service`.
- `data_source_mode="strategy_service"` remains supported.
- `data_source_mode="auto"` remains supported.
- Unsupported mode still raises `ValueError` before engine construction.
- `run_backtest_task` still calls `_resolve_backtest_data_source()` once.
- Public `get_strategy_service()` remains available and unchanged.
- Strategy route provider fallback remains unchanged.
- Strategy adapter/provider helper duplication remains deferred to its own design track.

## Review Gate

Before accepting this PR, verify:

1. The changed source/test paths match the G2.169 authorization boundary.
2. The new task-local provider seam is enough for the intended future lifecycle-DI migration step.
3. The public Strategy service getter is still retained.
4. The Strategy adapter/provider track remains separate.
5. The TDD red/green evidence and focused regressions are acceptable.

## Rollback

Revert this PR to restore the previous inline resolver behavior. The rollback removes only the task-local provider seam, the provider-seam regression test, and the governance artifacts for G2.170.

