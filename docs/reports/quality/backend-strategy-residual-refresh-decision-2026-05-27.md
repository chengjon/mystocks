# Backend Strategy Residual Refresh Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.176
- State: ready for review
- Date: 2026-05-27
- Current HEAD: `2718dd07ce10dbe94937ed0bb758956677b3dce4`
- Parent PR: `#328` merged, `docs(governance): close strategy adapter wrapper lane`
- Scope: Strategy getter residual refresh and next-track selection

## Boundary

This package is a decision package only. It does not edit backend source, backend
tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows,
OpenSpec content, config, scripts, compatibility surfaces, issue labels, or
service getter implementations.

This package does not authorize immediate source implementation. It only selects
the next Strategy residual design/authorization package.

## Parent State

PR `#327` converted `web/backend/app/services/data_adapters/strategy.py` into a
thin compatibility wrapper around canonical
`web/backend/app/services/adapters/strategy_adapter.py`.

PR `#328` closed that wrapper lane and recorded that the legacy direct import
path remains available without owning a direct `get_strategy_service` residual.

## Current Residual Scan

At current HEAD `2718dd07ce10dbe94937ed0bb758956677b3dce4`, production `.py`
`get_strategy_service` hits under `web/backend/app` are:

| Owner | Hits | Current disposition |
|---|---:|---|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 6 | Route provider fallback retained by prior decision |
| `web/backend/app/tasks/backtest_tasks.py` | 2 | Closed task-local provider helper; not reopened |
| `web/backend/app/services/adapters/strategy_adapter.py` | 10 | Only unresolved Strategy residual owner |
| `web/backend/app/services/strategy_service.py` | 1 | Public getter definition retained |
| `web/backend/app/services/data_adapters/strategy.py` | 0 | Closed by wrapper conversion |

The legacy wrapper state is:

- line count: `9`
- re-exports canonical `StrategyDataSourceAdapter`: yes
- defines `class StrategyDataSourceAdapter`: no
- contains direct `get_strategy_service`: no

## Canonical Adapter Residual

The remaining unresolved Strategy adapter residual is in:

```text
web/backend/app/services/adapters/strategy_adapter.py
```

Relevant helper sites:

- `_get_strategy_service()` lazily imports and calls public
  `app.services.strategy_service.get_strategy_service()`.
- `_fetch_strategy_data()` calls `_get_strategy_service()` to determine service
  availability and then uses mock fallback when configured.
- `health_check()` calls `_get_strategy_service()` to report service
  availability.

This is no longer a duplicate-path cleanup problem. It is a canonical adapter
provider seam problem.

## GitNexus Evidence

Fresh `gitnexus analyze --with-gitignore` was run before collecting graph
evidence.

File-level impact:

- `web/backend/app/services/adapters/strategy_adapter.py`: LOW risk,
  `5` impacted symbols/files, `2` direct import dependents, `0` affected
  processes.
- `web/backend/app/services/data_adapters/strategy.py`: LOW risk, `1` direct
  test import, `0` affected processes.

Public getter impact:

- `get_strategy_service` remains CRITICAL at symbol level with `13` impacted
  symbols, `6` direct callers, `0` affected processes, and `5` affected modules.

Tooling note: the symbol-level graph still reports stale legacy
`data_adapters/strategy.py` helper symbols even after a fresh analyze. The
current-head static scan above is therefore the ownership source of truth for
the legacy wrapper state; GitNexus file-level impact is still useful for the
canonical adapter file and legacy wrapper file.

## Verification

Commands were run from the G2.176 worktree with current HEAD
`2718dd07ce10dbe94937ed0bb758956677b3dce4`.

| Check | Result |
|---|---|
| `gh pr view 328 --repo chengjon/mystocks --json number,state,mergedAt,mergeCommit,title,url` | `MERGED`, merge commit `2718dd07ce10dbe94937ed0bb758956677b3dce4` |
| `pytest -o addopts= web/backend/tests/test_adapter_mock_fallback_controls.py -q --no-cov --tb=short` | `7 passed` |
| `pytest -o addopts= web/backend/tests/test_strategy_management_route_provider.py web/backend/tests/test_backtest_tasks_regressions.py -q --no-cov --tb=short` | `8 passed` |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0` |

OpenAPI smoke used placeholder non-secret environment values and did not start
PM2 or execute stateful runtime gates.

## Decision

Select the canonical Strategy adapter provider seam as the next Strategy
decision track.

The next package should be G2.177: a design/authorization package for
`web/backend/app/services/adapters/strategy_adapter.py`.

G2.177 should decide whether a later implementation may introduce an injectable
provider seam for `StrategyDataSourceAdapter` while preserving:

- public `get_strategy_service()` compatibility;
- route provider fallback behavior;
- backtest task resolver closure;
- legacy `data_adapters/strategy.py` wrapper compatibility;
- `data_adapter.py` and `data_source_factory` construction behavior;
- route/API behavior and OpenAPI exposure.

## Non-Authorization

This package does not authorize editing:

- `web/backend/app/services/adapters/strategy_adapter.py`
- `web/backend/app/services/data_adapters/strategy.py`
- `web/backend/app/services/data_adapter.py`
- `web/backend/app/services/data_source_factory/**`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py`
- `web/backend/app/tasks/backtest_tasks.py`
- `web/backend/app/services/strategy_service.py`

## Next Gate

Review G2.176. If accepted and merged, open G2.177 as a narrow
Strategy canonical adapter provider design/authorization package. Do not start a
Strategy source implementation lane before G2.177 is approved.
