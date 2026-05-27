# Backend Strategy Adapter Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.178
- State: ready for review
- Date: 2026-05-27
- Original implementation base HEAD: `3b8f95945fcb489316ddfaf919835d372122fa5f`
- Rebased stewardship base HEAD: `750fb7c797ff95f27152439ed988a7115252129e`
- Parent PR: `#330` merged, `docs(governance): authorize strategy adapter provider seam`
- Scope: path-limited canonical Strategy adapter provider implementation

## Boundary

This implementation modifies only the two files authorized by G2.177:

- `web/backend/app/services/adapters/strategy_adapter.py`
- `web/backend/tests/test_adapter_mock_fallback_controls.py`

It does not edit the legacy `data_adapters/strategy.py` wrapper, data adapter
factory, Strategy route provider fallback, backtest task resolver, public
`get_strategy_service()`, route/API behavior, OpenAPI exposure, frontend code,
PM2 workflows, OpenSpec content, config, scripts, compatibility surfaces, or
issue labels.

## Implementation

G2.178 adds an optional constructor-level Strategy service provider seam to the
canonical `StrategyDataSourceAdapter`.

Implementation details:

- `StrategyDataSourceAdapter.__init__()` now accepts
  `strategy_service_provider: Callable[[], Any] | None = None`.
- The provider is stored as `_strategy_service_provider`.
- `_get_strategy_service()` still remains the single adapter-local access point.
- `_get_strategy_service()` uses the injected provider when one is supplied.
- Without an injected provider, `_get_strategy_service()` keeps the existing
  public `get_strategy_service()` fallback path.
- Service caching remains unchanged: the provider is called only on the first
  successful service resolution.
- Existing factory and direct construction callers remain compatible because the
  new constructor parameter is optional.

## TDD Evidence

Red:

- Added `test_strategy_adapter_uses_injected_strategy_service_provider`.
- It failed before implementation with:
  `TypeError: StrategyDataSourceAdapter.__init__() got an unexpected keyword argument 'strategy_service_provider'`.

Green:

- Added the optional provider parameter and provider-aware helper branch.
- The focused test passed: `1 passed`.

## Static Guard

At base HEAD plus implementation changes:

- `strategy_adapter.py` line count: `372`
- Constructor line: `24`
- `_get_strategy_service()` line: `40`
- `Callable` import present: yes
- Optional provider parameter present: yes
- `_strategy_service_provider` is stored: yes
- `_get_strategy_service()` uses the injected provider: yes
- Public `get_strategy_service()` fallback is preserved: yes
- Provider test is present: yes
- Production `.py` `get_strategy_service` hits under `web/backend/app`: `19`

Current residual distribution remains:

| Owner | Hits |
|---|---:|
| `web/backend/app/tasks/backtest_tasks.py` | 2 |
| `web/backend/app/services/strategy_service.py` | 1 |
| `web/backend/app/services/adapters/strategy_adapter.py` | 10 |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 6 |

## GitNexus Evidence

Before editing:

- `web/backend/app/services/adapters/strategy_adapter.py`: LOW risk, `5`
  impacted symbols/files, `2` direct import dependents, `0` affected processes.
- `web/backend/tests/test_adapter_mock_fallback_controls.py`: LOW risk, `0`
  upstream dependents, `0` affected processes.

No HIGH or CRITICAL file-level warning was ignored.

## Verification

Commands were run from the G2.178 worktree with `PYTHONPATH=web/backend`.

| Check | Result |
|---|---|
| TDD red focused test | failed for expected constructor keyword reason |
| TDD green focused test | `1 passed` |
| `pytest -o addopts= web/backend/tests/test_adapter_mock_fallback_controls.py -q --no-cov --tb=short` | `8 passed` |
| `pytest -o addopts= web/backend/tests/test_logging_noise_regressions.py -q --no-cov --tb=short` | `10 passed` |
| `pytest -o addopts= web/backend/tests/test_strategy_management_route_provider.py web/backend/tests/test_backtest_tasks_regressions.py -q --no-cov --tb=short` | `8 passed` |
| `pytest -o addopts= tests/backend/test_data_adapter_regression.py -q --no-cov --tb=short` | `9 passed` |
| `ruff check web/backend/app/services/adapters/strategy_adapter.py web/backend/tests/test_adapter_mock_fallback_controls.py` | passed |
| `black --check web/backend/app/services/adapters/strategy_adapter.py web/backend/tests/test_adapter_mock_fallback_controls.py` | passed |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0` |

OpenAPI smoke used placeholder non-secret environment values and did not start
PM2 or execute stateful runtime gates.

## Steward Tree Reconciliation

After PR `#332` split the steward tree, this PR no longer writes G2.178 state
to the old root task-tree body. The implementation state is recorded in:

- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/generated/strategy-adapter-provider-implementation-2026-05-27.json`

The root entrypoint remains the PR `#332` split-navigation file.

## Risk And Rollback

The main risk is accidental expansion from a constructor seam into public getter
or factory behavior. This implementation keeps the default constructor path and
public getter fallback unchanged.

Rollback is a normal PR revert. Reverting removes the optional provider
parameter and focused test, restoring the previous canonical adapter behavior.

## Next Gate

Review this implementation package. If accepted and merged, close G2.178 in a
separate governance closeout and refresh remaining Strategy service getter
residuals before choosing any further Strategy source lane.
