# B4.014-M1j Backtest Date Contract Normalization Repair

Date: 2026-06-28
Scope: B4.014 P0 mainline runtime usability, backtest submit/run/result persistence path.
Authorization: source-authorized repair for MyStocks runtime blockers before OpenStock interface integration.

## Boundary

- MyStocks only consumes/adapts data. No OpenStock provider/runtime code was changed.
- No frontend, route, ST-HOLD, marketKlineData, OpenSpec, or external dirty files were touched.
- The repair stayed on the backend backtest API/task/repository/runtime-schema boundary.

## Root Cause

M1i controlled smoke isolated a core backtest chain break:

- API/task dates were normalized to `%Y-%m-%d`, but the strategy history data source expects `YYYYMMDD`.
- The engine accepted only `trade_date` rows while the runtime provider can return `date`.
- The task result payload uses dict-shaped metrics/equity rows, while repository persistence expected Pydantic objects.
- Runtime PostgreSQL `backtest_results` is a legacy/standard mixed table. Several legacy non-null columns and varchar id fields blocked real API parent-task creation and lookup.
- Result conversion returned `performance_metrics`, while the API response model exposes `performance`.

## Implementation

- `BacktestEngine._load_market_data` now formats provider dates as `YYYYMMDD` and accepts either `trade_date`, `date`, or index dates.
- `BacktestRepository` now accepts dict-shaped engine metrics and equity rows, normalizes engine metric aliases such as `annualized_return -> annual_return`, and returns pending/completed API result shapes.
- `BacktestRepository.create_backtest` now fills the runtime legacy-required columns and returns a pending DTO without forcing a refresh against the varchar legacy primary key.
- `BacktestRepository.list_backtests` now uses string-compatible `strategy_id` filtering for the legacy runtime schema.
- `strategy_mgmt.ensure_strategy_runtime_schema_ready` now includes backtest detail tables and uses a no-FK compatibility path when the legacy parent key is not unique.
- `_save_backtest_results` now stops before writing detail rows when the parent result row is absent.

## Verification Evidence

Static/contract checks:

- `python -m py_compile web/backend/app/api/strategy_mgmt.py web/backend/app/backtest/backtest_engine.py web/backend/app/repositories/backtest_repository.py web/backend/app/tasks/backtest_tasks.py web/backend/app/models/strategy_schemas.py web/backend/tests/test_backtest_tasks_regressions.py web/backend/tests/test_strategy_mgmt_backtest_regressions.py`
- `pytest -q --no-cov -o addopts='' --tb=short web/backend/tests/test_backtest_tasks_regressions.py web/backend/tests/test_strategy_mgmt_backtest_regressions.py web/backend/tests/test_backtest_repository_trade_schema.py web/backend/tests/test_backtest_trade_schema_regressions.py`
  - Result: `27 passed in 4.65s`.

Runtime smoke checks with PM2 backend environment:

- PostgreSQL repository create/save/detail smoke:
  - pending task created
  - completed result saved
  - equity curve saved
  - counts before cleanup: `result_rows=1`, `equity_rows=1`, `trade_rows=0`
  - cleanup removed the test parent row and related detail rows.
- PostgreSQL repository get/list smoke:
  - `get_backtest` returned pending result with `performance`
  - `list_backtests` returned `total=1`
  - cleanup removed the test row.
- Controlled Celery task smoke with persisted parent:
  - task state: `SUCCESS`
  - result status: `completed`
  - returned equity curve length: `4`
  - persisted status: `completed`
  - persisted equity rows: `4`
  - cleanup removed the test parent row and detail rows.

Service state:

- `mystocks-backend`: PM2 online at `http://localhost:8020`
- `mystocks-frontend`: PM2 online at `http://localhost:3020`

## Result

The MyStocks minimal backtest path is now runnable through the backend mainline chain:

`create parent backtest -> run controlled task -> load strategy-history market data -> complete backtest -> save result -> save equity curve -> query result/list`

This closes the MyStocks-side blocker that had to be fixed before OpenStock interface integration.

## Next

Proceed to the OpenStock interface integration stage as a separate package:

1. No-source boundary audit for the OpenStock -> MyStocks consumer contract.
2. Confirm endpoint URLs, auth/env, symbol/date format, response schema, error shape, timeout/retry policy.
3. Add MyStocks adapter/contract smoke only after the interface truth is confirmed.
4. Keep OpenStock development out of `mystocks_spec`; this repo only consumes and adapts OpenStock responses.
