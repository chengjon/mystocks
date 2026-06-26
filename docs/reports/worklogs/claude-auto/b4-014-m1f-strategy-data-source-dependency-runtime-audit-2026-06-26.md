# B4.014-M1f Strategy Data-Source Dependency Runtime Audit

Date: 2026-06-26

Scope: no-source runtime audit only.

## Boundary

- No source, test, runtime configuration, frontend, OpenSpec, or external dirty files were modified.
- No write endpoints were called. Strategy creation and backtest execution remained out of scope because they can create database/task state.
- MyStocks remains a consumer/adaptation layer for OpenStock data. This audit did not add or change provider/data-source runtime behavior.

## Runtime Context

- Branch: `wip/root-dirty-20260403`
- Baseline commit: `d57ffa3f3`
- PM2:
  - `mystocks-backend`: online, port `8020`
  - `mystocks-frontend`: online
- Staged index before audit: empty.

## Read-Only Probe Results

| Endpoint | Result | Runtime meaning |
| --- | --- | --- |
| `GET /health` | HTTP 200 | Backend service is reachable and reports healthy. |
| `GET /api/strategy-mgmt/health` | HTTP 200 | Strategy management service now reports `status=healthy`, `database=connected`. |
| `GET /api/strategy-mgmt/strategies?user_id=1001` | HTTP 200 | Strategy list path is readable; returned an empty paged result. |
| `GET /api/strategy-mgmt/backtest/results?user_id=1001` | HTTP 200 | Backtest result list path is readable; returned an empty paged result. |
| `GET /api/strategy-mgmt/backtest/status/1` | HTTP 500 | Backtest status path still fails before any backtest engine/data-source execution. |

The strategy health payload still contains a degraded data-source dependency:

- `data_source.status=degraded`
- `timeseries_source.status=unhealthy`
- `timeseries_source.error=""`
- `relational_source.status=healthy`

This degraded dependency does not currently block the read-only strategy list or backtest result list paths.

## Backtest Status Blocker

The status endpoint fails with:

```text
operator does not exist: character varying = integer
WHERE backtest_results.backtest_id = 1
```

Runtime schema evidence from `information_schema.columns`:

| Column | Runtime type |
| --- | --- |
| `backtest_results.backtest_id` | `character varying` |
| `backtest_results.strategy_id` | `character varying` |
| `backtest_results.user_id` | `integer` |
| `backtest_results.status` | `character varying` |

The repository model currently treats `backtest_id` and `strategy_id` as integer columns. The live table retained a legacy string identifier shape, and the HTTP route accepts `backtest_id: int`. The immediate 500 is therefore an ID/schema compatibility issue, not an OpenStock or timeseries-source failure.

## Data Dependency Finding

The async backtest task resolves its data source through `get_strategy_service()` and injects it into `BacktestEngine`. That means actual backtest execution can later exercise the strategy service data path, but the observed `GET /backtest/status/1` 500 occurs earlier in the repository lookup and never reaches the engine or data-source layer.

## Decision

M1f should not proceed to data-source runtime repair yet.

The next mainline-safe repair should target the concrete user-visible 500:

- Normalize backtest status/result identifier handling against the live schema.
- Preserve existing data and avoid destructive schema rewrites.
- Keep the repair limited to strategy management API/repository compatibility and direct regression tests.
- Defer the degraded `timeseries_source` investigation until a write-authorized minimal backtest execution smoke proves it blocks an actual user path.

## Proposed Next Node

`B4.014-M1g backtest status identifier compatibility repair`

Recommended authorization boundary:

- Allowed source candidates:
  - `web/backend/app/api/strategy_mgmt.py`
  - `web/backend/app/repositories/backtest_repository.py`
- Allowed tests:
  - direct strategy/backtest regression tests only.
- Non-goals:
  - no OpenStock provider work
  - no strategy core rewrite
  - no destructive database migration
  - no frontend work
  - no unrelated governance cleanup

## Closeout Criteria For The Next Repair

- `GET /api/strategy-mgmt/backtest/status/1` no longer returns 500 due to varchar/int comparison.
- Strategy health/list/result-list endpoints remain HTTP 200.
- Regression tests cover legacy string IDs or route/repository normalization.
- Runtime smoke confirms no new strategy management 500s.
