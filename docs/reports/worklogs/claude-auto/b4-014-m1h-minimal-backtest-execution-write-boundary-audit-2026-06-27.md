# B4.014-M1h Minimal Backtest Execution Write-Boundary Audit

Date: 2026-06-27

Scope: no-source, no-write audit only.

## Boundary

- No source, test, runtime config, frontend, OpenSpec, OpenStock, or external dirty files were modified.
- No write endpoint was called.
- `POST /api/strategy-mgmt/backtest/execute` was not executed because it creates a backtest row and enqueues a Celery task.
- MyStocks remains a consumer/adaptation layer. This audit did not add or repair data-source provider/runtime behavior.

## Current Runtime Baseline

| Check | Result |
| --- | --- |
| `mystocks-backend` | PM2 online, port `8020` |
| `mystocks-frontend` | PM2 online, port `3020` |
| Redis `127.0.0.1:6379` | reachable |
| Celery broker | `redis://localhost:6379/1` |
| Celery result backend | `redis://localhost:6379/1` |
| Celery worker process | not found in PM2 or process list |

Read-only strategy endpoints:

| Endpoint | Result |
| --- | --- |
| `GET /health` | HTTP 200 |
| `GET /api/strategy-mgmt/health` | HTTP 200, `status=healthy`, `database=connected` |
| `GET /api/strategy-mgmt/strategies?user_id=1001` | HTTP 200, empty list |
| `GET /api/strategy-mgmt/backtest/results?user_id=1001` | HTTP 200, empty list |
| `GET /api/strategy-mgmt/backtest/status/1` | HTTP 404 domain not found; no SQL operator error |

The data-source dependency still reports:

- `data_source.status=degraded`
- `timeseries_source.status=unhealthy`
- `relational_source.status=healthy`

## Write Endpoint Boundary

`POST /api/strategy-mgmt/backtest/execute` is a true write path:

1. `_require_write_auth(authorization)` gates writes.
2. It checks the strategy via `strategy_repo.get_strategy(backtest_req.strategy_id)`.
3. It creates a backtest row through `backtest_repo.create_backtest(execute_request)`.
4. It enqueues `run_backtest_task.delay(...)`.
5. It registers `backtest_id -> celery task_id` in process memory.

In test mode, `_require_write_auth()` allows writes. In non-test mode, a valid Bearer token is required.

## Execution Chain Boundary

The queued task is:

```text
app.tasks.backtest_tasks.run_backtest
```

Task path:

1. `_resolve_backtest_data_source(backtest_config)` accepts only `strategy_service` or `auto`.
2. It returns `get_strategy_service()`.
3. `BacktestEngine(..., data_source=data_source)` receives the strategy service.
4. `web/backend/app/backtest/backtest_engine.py` calls `self.data_source.get_stock_history(...)`.
5. `web/backend/app/services/strategy_service.py` currently uses `akshare` for strategy history fetches.

Important implication: a successful API `202` only proves database insertion plus Celery enqueue. It does not prove the backtest engine actually executes unless a worker is running or the task is executed synchronously under a controlled smoke.

## Decision

Do not directly call `POST /api/strategy-mgmt/backtest/execute` as an unaudited continuation.

The next useful mainline validation must explicitly authorize one of these two options:

1. **API enqueue smoke only**
   - Start from an existing or seeded strategy.
   - Call the write endpoint.
   - Validate HTTP 202, DB row creation, task id registration or Redis enqueue.
   - This does not prove BacktestEngine/data-source execution while no Celery worker is running.

2. **Controlled execution smoke**
   - Start or authorize a Celery worker for this repo, or invoke the task synchronously in a controlled test harness.
   - Use a minimal short-date/single-symbol request.
   - Validate whether `BacktestEngine` reaches `strategy_service.get_stock_history`.
   - If it fails due to history fetch/data provider behavior, classify the blocker as a MyStocks consumer/adaptation issue or an OpenStock boundary issue before any source fix.

## Recommended Next Node

`B4.014-M1i controlled minimal backtest execution smoke`

Recommended authorization:

- Allow exactly one minimal write smoke against runtime `8020`, or a controlled synchronous task smoke.
- Permit cleanup of only the smoke-created backtest row/task evidence if explicitly included.
- Do not authorize source edits yet.
- Do not authorize OpenStock provider/runtime development.
- Do not authorize broad data-source repair.

## Non-Goals

- No OpenStock provider/runtime development.
- No source fix.
- No frontend work.
- No B4.012 cleanup.
- No broad Celery deployment redesign.
- No strategy or backtest engine rewrite.
