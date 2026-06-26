# B4.014-M1g Backtest Status Identifier Compatibility Implementation Closeout

Date: 2026-06-27

## Scope

Source-authorized implementation for:

- `web/backend/app/repositories/backtest_repository.py`
- `web/backend/tests/test_strategy_mgmt_backtest_regressions.py`

No changes were made to OpenStock provider/runtime code, data-source runtime behavior, strategy core execution, backtest engine logic, frontend, API paths, or B4.012 governance debt.

## Runtime Problem

Before this repair:

```text
GET /api/strategy-mgmt/backtest/status/1 -> HTTP 500
operator does not exist: character varying = integer
```

The live runtime table keeps legacy string identifiers:

- `backtest_results.backtest_id`: `character varying`
- `backtest_results.strategy_id`: `character varying`

The status endpoint passed an integer route parameter to the repository, which produced a PostgreSQL `varchar = integer` comparison before reaching any backtest engine or data-source path.

## Change

Added repository-local identifier normalization:

- `BacktestRepository.get_backtest()`
- `BacktestRepository.update_backtest_status()`
- `BacktestRepository.save_backtest_results()`

The lookup value is normalized to string before comparing against `BacktestResultModel.backtest_id`, preserving compatibility with the current live `varchar` schema without destructive migration or table rewrite.

## Regression Coverage

Added:

```text
test_backtest_repository_uses_string_compatible_id_lookup_for_legacy_runtime_schema
```

The test captures the SQLAlchemy filter expression and verifies that the lookup compiles to:

```text
backtest_results.backtest_id = '1'
```

instead of:

```text
backtest_results.backtest_id = 1
```

## Verification

Commands executed:

```bash
pytest -q --no-cov -o addopts='' --tb=short web/backend/tests/test_strategy_mgmt_backtest_regressions.py::test_backtest_repository_uses_string_compatible_id_lookup_for_legacy_runtime_schema
python -m py_compile web/backend/app/api/strategy_mgmt.py web/backend/app/repositories/backtest_repository.py web/backend/tests/test_strategy_mgmt_backtest_regressions.py
pytest -q --no-cov -o addopts='' --tb=short web/backend/tests/test_strategy_mgmt_backtest_regressions.py
pm2 restart mystocks-backend
```

Results:

- focused red/green test: `1 passed`
- py_compile: passed
- focused regression file: `9 passed`
- PM2 backend: restarted and online on port `8020`

Runtime smoke after backend reload:

| Endpoint | Result |
| --- | --- |
| `GET /health` | HTTP 200 |
| `GET /api/strategy-mgmt/health` | HTTP 200, `status=healthy`, `database=connected` |
| `GET /api/strategy-mgmt/strategies?user_id=1001` | HTTP 200 |
| `GET /api/strategy-mgmt/backtest/results?user_id=1001` | HTTP 200 |
| `GET /api/strategy-mgmt/backtest/status/1` | HTTP 404 domain not found; no varchar/int SQL operator error |

The status endpoint no longer emits the previous SQL 500. Returning a 404 for a missing `backtest_id=1` is acceptable and expected because the current runtime table has no matching row.

## Remaining Boundary

`/api/strategy-mgmt/health` still reports the lower-level `timeseries_source` as `unhealthy` and aggregate `data_source.status=degraded`. That remains outside M1g because the proven runtime blocker here was the backtest status ID comparison. The next OpenStock/data-source investigation should only start when a write-authorized minimal backtest execution smoke proves an actual user-path blockage.
