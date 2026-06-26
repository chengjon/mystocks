# B4.014-M1e-A Strategy Runtime Schema Readiness Implementation Closeout

Date: 2026-06-26

## Mainline Target

Restore strategy management runtime usability for the B4.014 A-share quant mainline.

This package fixes the P0 runtime blocker found in M1e:

- `/api/strategy-mgmt/health` was HTTP 200 but body `unhealthy`.
- `/api/strategy-mgmt/strategies?user_id=1001` returned HTTP 500.
- `/api/strategy-mgmt/backtest/results?user_id=1001` returned HTTP 500.

Root cause: strategy/backtest ORM expectations drifted from the live PostgreSQL runtime schema.

## Implementation

Changed files:

- `web/backend/app/api/strategy_mgmt.py`
- `web/backend/tests/test_strategy_mgmt_backtest_regressions.py`

Implementation details:

- Added `ensure_strategy_runtime_schema_ready(db)`.
- The helper uses current ORM table metadata for `user_strategies` and `backtest_results`.
- It is additive only:
  - missing table -> `table.create(bind=bind, checkfirst=True)`
  - missing column on existing table -> `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...`
  - no table drops
  - no column drops
  - no table rewrites
  - no destructive migration
- Strategy and backtest repository dependencies call readiness before constructing repositories, so direct list endpoints do not depend on `/health` being called first.
- Strategy health calls readiness before table counts.

## TDD Evidence

RED:

- `test_strategy_runtime_schema_readiness_is_additive_and_idempotent` failed because `ensure_strategy_runtime_schema_ready` did not exist.
- `test_strategy_health_runs_schema_readiness_before_table_counts` failed because `health_check` did not call readiness.
- `test_strategy_repository_dependencies_prepare_runtime_schema` failed because repository dependencies did not call readiness.

GREEN:

- Focused regression file passed:
  - `pytest -q --no-cov -o addopts='' --tb=short web/backend/tests/test_strategy_mgmt_backtest_regressions.py`
  - Result: 8 passed.
- Syntax passed:
  - `python -m py_compile web/backend/app/api/strategy_mgmt.py web/backend/tests/test_strategy_mgmt_backtest_regressions.py`

## Runtime Evidence

After PM2 backend restart:

- `mystocks-backend`: online, `http://localhost:8020`
- `mystocks-frontend`: online, `http://localhost:3020`

Runtime probes:

- `GET /health`: HTTP 200
- `GET /api/strategy-mgmt/health`: HTTP 200, body `status=healthy`, `database=connected`
- `GET /api/strategy-mgmt/strategies?user_id=1001`: HTTP 200, empty list
- `GET /api/strategy-mgmt/backtest/results?user_id=1001`: HTTP 200, empty list

Runtime schema after readiness:

- `user_strategies` exists with the current ORM columns.
- `backtest_results` retained existing columns and gained additive ORM-required columns including `user_id`, `symbols`, `start_date`, `end_date`, `commission_rate`, `slippage_rate`, `benchmark`, `performance_metrics`, `status`, `error_message`, `started_at`, and `completed_at`.

## Boundaries

No OpenStock provider/runtime development, frontend changes, B4.012 cleanup, repository hygiene, broad migration framework rewrite, table drop, column drop, or route redesign was performed.

Remaining known boundary:

- `data_source.dependencies.timeseries_source.status` is still `unhealthy` inside the strategy health payload, while the strategy management endpoint itself is `healthy`. This is a separate data source/runtime dependency issue and should be handled in a later B4.014 P0 package only if it blocks a real user path.
