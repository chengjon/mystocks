# Backend Strategy Adapter Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.177
- State: ready for review
- Date: 2026-05-27
- Current HEAD: `46cf4b25da6cb29852663206fa815dd5b37f9787`
- Parent PR: `#329` merged, `docs(governance): refresh strategy residual decision`
- Scope: Strategy canonical adapter provider seam design/authorization

## Boundary

This package is design/authorization only. It does not edit backend source,
backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2
workflows, OpenSpec content, config, scripts, compatibility surfaces, issue
labels, or service getter implementations.

This package authorizes only a future G2.178 implementation lane after review.
No source implementation is performed here.

## Parent State

G2.176 refreshed current Strategy residual ownership after the legacy
`data_adapters/strategy.py` wrapper closeout.

Current production `.py` `get_strategy_service` hits under `web/backend/app`
remain `19`:

| Owner | Hits | Current disposition |
|---|---:|---|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 6 | Route provider fallback retained |
| `web/backend/app/tasks/backtest_tasks.py` | 2 | Closed task-local helper |
| `web/backend/app/services/adapters/strategy_adapter.py` | 10 | Selected canonical adapter provider seam |
| `web/backend/app/services/strategy_service.py` | 1 | Public getter definition retained |
| `web/backend/app/services/data_adapters/strategy.py` | 0 | Closed legacy wrapper lane |

## Current Source Facts

Target file:

```text
web/backend/app/services/adapters/strategy_adapter.py
```

Current facts at HEAD `46cf4b25da6cb29852663206fa815dd5b37f9787`:

- File line count: `368`
- Class starts at line `21`: `StrategyDataSourceAdapter`
- Constructor starts at line `24`: `def __init__(self, config: Dict[str, Any]):`
- `_get_strategy_service()` starts at line `39`
- `_fetch_strategy_data()` starts at line `99`
- `health_check()` starts at line `322`
- `get_strategy_service` mentions in file: `10`
- `_get_strategy_service` mentions in file: `8`
- Constructor provider/factory/callable mentions: `0`
- Mock fallback helper remains present: yes
- Mock fallback guard remains present: yes

Current behavior:

- The constructor accepts only `config`.
- `_get_strategy_service()` lazily imports public
  `app.services.strategy_service.get_strategy_service`.
- `_fetch_strategy_data()` and `health_check()` call `_get_strategy_service()`.
- Factory construction and legacy wrapper imports resolve to the canonical class
  without passing a provider.

## GitNexus Evidence

- `web/backend/app/services/adapters/strategy_adapter.py` file impact: LOW,
  `5` impacted symbols/files, `2` direct import dependents, `0` affected
  processes.
- Public `get_strategy_service` symbol impact remains CRITICAL, `13` impacted
  symbols, `6` direct callers, `0` affected processes, `5` affected modules.

Tooling note: symbol-level impact still reports stale legacy
`data_adapters/strategy.py` helper symbols. The current static scan remains the
ownership source of truth for the closed legacy wrapper path.

## Authorization

If this package is approved, future G2.178 may implement only a constructor-level
provider seam inside the canonical Strategy adapter.

Allowed future source/test paths:

- `web/backend/app/services/adapters/strategy_adapter.py`
- `web/backend/tests/test_adapter_mock_fallback_controls.py`

Allowed future implementation shape:

- Add an optional constructor parameter to `StrategyDataSourceAdapter`, for
  example a `strategy_service_provider` callable.
- Preserve current default constructor behavior for existing factory and direct
  class construction callers.
- Keep `_get_strategy_service()` as the single adapter-local access point.
- Make `_get_strategy_service()` use the injected provider when one is supplied,
  otherwise fall back to public `get_strategy_service()`.
- Preserve existing service caching, exception behavior, mock fallback behavior,
  metrics behavior, and response shapes.
- Add a focused test proving the injected provider is used and the default
  constructor remains compatible.

Forbidden future changes in G2.178:

- Do not edit `web/backend/app/services/data_adapters/strategy.py`.
- Do not edit `web/backend/app/services/data_adapter.py`.
- Do not edit `web/backend/app/services/data_source_factory/**`.
- Do not edit `web/backend/app/api/strategy_management/_strategy_execution_router.py`.
- Do not edit `web/backend/app/tasks/backtest_tasks.py`.
- Do not edit `web/backend/app/services/strategy_service.py`.
- Do not delete, rename, privatize, or behaviorally change public
  `get_strategy_service()`.
- Do not change route/API behavior, OpenAPI exposure, frontend code, PM2
  workflows, OpenSpec content, config, scripts, compatibility surfaces, or issue
  labels.

## Required G2.178 Verification

Future G2.178 must use TDD:

1. Add a failing focused test for injected provider behavior.
2. Implement the minimal constructor/provider seam.
3. Rerun the focused and regression checks below.

Required checks:

- `pytest -o addopts= web/backend/tests/test_adapter_mock_fallback_controls.py -q --no-cov --tb=short`
- `pytest -o addopts= web/backend/tests/test_logging_noise_regressions.py -q --no-cov --tb=short`
- `pytest -o addopts= web/backend/tests/test_strategy_management_route_provider.py web/backend/tests/test_backtest_tasks_regressions.py -q --no-cov --tb=short`
- `pytest -o addopts= tests/backend/test_data_adapter_regression.py -q --no-cov --tb=short`
- `ruff check web/backend/app/services/adapters/strategy_adapter.py web/backend/tests/test_adapter_mock_fallback_controls.py`
- `black --check web/backend/app/services/adapters/strategy_adapter.py web/backend/tests/test_adapter_mock_fallback_controls.py`
- OpenAPI smoke with `routes=548`, `paths=500`, and zero duplicate operation IDs.
- GitNexus staged detect-changes before commit.
- Mainline scope gate after commit.

## Verification For This Package

Commands were run from the G2.177 worktree with current HEAD
`46cf4b25da6cb29852663206fa815dd5b37f9787`.

| Check | Result |
|---|---|
| `gh pr view 329 --repo chengjon/mystocks --json number,state,mergedAt,mergeCommit,title,url` | `MERGED`, merge commit `46cf4b25da6cb29852663206fa815dd5b37f9787` |
| `pytest -o addopts= web/backend/tests/test_adapter_mock_fallback_controls.py -q --no-cov --tb=short` | `7 passed` |
| `pytest -o addopts= web/backend/tests/test_logging_noise_regressions.py -q --no-cov --tb=short` | `10 passed` |
| `pytest -o addopts= web/backend/tests/test_strategy_management_route_provider.py web/backend/tests/test_backtest_tasks_regressions.py -q --no-cov --tb=short` | `8 passed` |
| `pytest -o addopts= tests/backend/test_data_adapter_regression.py -q --no-cov --tb=short` | `9 passed` |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0` |

OpenAPI smoke used placeholder non-secret environment values and did not start
PM2 or execute stateful runtime gates.

## Next Gate

Review G2.177. If accepted and merged, start G2.178 as a path-limited
implementation lane for the canonical Strategy adapter provider seam. Do not
start G2.178 before this authorization package is accepted.
