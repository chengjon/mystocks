# Backend Strategy Adapter Wrapper Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.174
- State: ready for review
- Date: 2026-05-27
- Base HEAD: `1fca532a056549f1869773c7dcd9ae3be5170425`
- Parent PR: `#326` merged, `docs(governance): design strategy adapter wrapper lane`
- Scope: path-limited Strategy legacy adapter wrapper implementation

## Boundary

This implementation changes only the legacy direct import path and its focused
adapter fallback test:

- `web/backend/app/services/data_adapters/strategy.py`
- `web/backend/tests/test_adapter_mock_fallback_controls.py`

It does not edit the canonical Strategy adapter implementation, data adapter
factory, Strategy route provider fallback, backtest task resolver, public
`get_strategy_service()`, route/API behavior, OpenAPI exposure, frontend code,
PM2 workflows, OpenSpec content, config, scripts, compatibility deletion, or
issue labels.

## Implementation

G2.173 selected `web/backend/app/services/adapters/strategy_adapter.py` as the
canonical `StrategyDataSourceAdapter` implementation and identified
`web/backend/app/services/data_adapters/strategy.py` as the legacy direct import
path.

G2.174 converts that legacy path into a thin compatibility wrapper:

- It re-exports canonical `StrategyDataSourceAdapter` from
  `app.services.adapters.strategy_adapter`.
- It defines `__all__ = ["StrategyDataSourceAdapter"]`.
- It removes the duplicate legacy class body and the duplicate private
  `_get_strategy_service()` helper from the legacy file.
- It adds a focused identity test proving the legacy direct import resolves to
  the canonical class object.

## GitNexus Evidence

- `web/backend/app/services/data_adapters/strategy.py`: LOW risk, `1` direct
  upstream test import, `0` affected processes.
- `web/backend/tests/test_adapter_mock_fallback_controls.py`: LOW risk, `0`
  upstream dependents, `0` affected processes.

No HIGH or CRITICAL impact warning was ignored.

## TDD Evidence

- Red: `test_legacy_strategy_adapter_import_reexports_canonical_class` failed
  with `assert StrategyAdapter is CanonicalStrategyAdapter`.
- Green: the same test passed after converting the legacy file to the wrapper.

## Verification

Commands were run from the G2.174 worktree with `PYTHONPATH=web/backend`.

| Check | Result |
|---|---|
| `pytest -o addopts= web/backend/tests/test_adapter_mock_fallback_controls.py -q --no-cov --tb=short` | `7 passed` |
| `pytest -o addopts= web/backend/tests/test_logging_noise_regressions.py -q --no-cov --tb=short` | `10 passed` |
| `pytest -o addopts= web/backend/tests/test_strategy_management_route_provider.py web/backend/tests/test_backtest_tasks_regressions.py -q --no-cov --tb=short` | `8 passed` |
| `ruff check web/backend/app/services/data_adapters/strategy.py web/backend/tests/test_adapter_mock_fallback_controls.py` | passed |
| `black --check web/backend/app/services/data_adapters/strategy.py web/backend/tests/test_adapter_mock_fallback_controls.py` | passed |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0` |

OpenAPI smoke used placeholder non-secret environment values and did not start
PM2 or perform stateful runtime gates.

## Static Guard

- Legacy wrapper line count: `9`.
- `web/backend/app/services/data_adapters/strategy.py` no longer defines
  `class StrategyDataSourceAdapter`.
- `web/backend/app/services/data_adapters/strategy.py` no longer contains a
  direct `get_strategy_service` reference.
- The focused test contains `assert StrategyAdapter is CanonicalStrategyAdapter`.

## Risk And Rollback

The primary risk is accidental expansion from a wrapper conversion into broader
Strategy service lifecycle work. This PR keeps the canonical adapter, factory,
route provider, backtest task resolver, and public getter unchanged.

Rollback is a normal PR revert. Reverting restores the previous duplicate legacy
implementation and removes only the identity test plus the G2.174 governance
artifacts.

## Next Gate

Review this implementation package. If accepted and merged, close G2.174 in the
steward tree and refresh the remaining Strategy service getter residuals before
selecting any next Strategy or high-risk getter lane.
