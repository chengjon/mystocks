# G2.334 Strategy Management Route Surface Test Alignment Closeout

Date: 2026-06-04

## Gate

- Node: `G2.334`
- Mode: source implementation after G2.333 triage approval
- `source_edit_authority`: `true`
- Target: `tests/api/file_tests/test_strategy_management_api.py`
- Non-goal: no backend route mutation, no frontend path changes, no compatibility route cleanup

## Source Changes

Changed file:

- `tests/api/file_tests/test_strategy_management_api.py`

Changes made:

- Updated `test_router_registers_expected_strategy_routes` to reflect current composed-router behavior:
  - root package router prefix is `""`
  - full route paths still carry `/api/v1/strategy`
  - added assertions for the 6 execution routes and 1 chart-data route that are part of the current package router surface
- Updated route-method pair count from `16` to `23`.
- Replaced the stale chart-data exclusion assertion with a positive wired-route assertion.
- Renamed the chart-data test from `test_chart_data_function_is_exported_but_not_wired_into_package_router` to `test_chart_data_function_is_exported_and_wired_into_package_router`.

No backend route files were edited in this node.

## TDD / Baseline Evidence

RED baseline:

- Command:
  - `pytest tests/api/file_tests/test_strategy_management_api.py -q -n 0 --tb=short --no-cov`
- Result before test alignment:
  - `3 failed, 8 passed, 1 warning`
- Failing assertions:
  - expected `strategy_module.router.prefix == "/api/v1/strategy"` but current value is `""`
  - expected route count `16` but current count is `23`
  - expected chart-data route not wired, but current router includes `/api/v1/strategy/backtest/results/{backtest_id}/chart-data`

GREEN result:

- Command:
  - `pytest tests/api/file_tests/test_strategy_management_api.py -q -n 0 --tb=short --no-cov`
- Result after test alignment:
  - `11 passed, 1 warning`

## Verification

Passed:

- `pytest tests/api/file_tests/test_strategy_management_api.py -q -n 0 --tb=short --no-cov`
  - `11 passed, 1 warning`
- `python -m py_compile tests/api/file_tests/test_strategy_management_api.py`
  - exit `0`
- `git diff --check -- tests/api/file_tests/test_strategy_management_api.py`
  - exit `0`

## Impact Evidence

Pre-change GitNexus impact was run for the three edited test methods:

- `test_router_registers_expected_strategy_routes`
- `test_router_contains_expected_number_of_route_method_pairs`
- `test_chart_data_function_is_exported_but_not_wired_into_package_router`

Each returned:

- risk: `LOW`
- impacted count: `0`
- affected processes: `0`

GitNexus index noted stale status because the working tree contains uncommitted changes, but these are test-only edits and current verification is based on live test execution.

## Scope Control

No changes were made to:

- `web/backend/app/api/strategy_management/__init__.py`
- `web/backend/app/api/strategy_management/_chart_data_router.py`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py`
- frontend API config or consumers
- legacy strategy route compatibility surfaces
- OpenSpec tasks or archived change files

## Closeout

G2.334 completed the strategy management route-surface test alignment. The targeted file-level suite now passes against the current 23-route package surface.
