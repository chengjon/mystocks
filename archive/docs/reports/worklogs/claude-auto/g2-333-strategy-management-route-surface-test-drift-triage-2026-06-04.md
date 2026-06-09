# G2.333 Strategy Management Route Surface Test Drift Triage

Date: 2026-06-04

## Gate

- Node: `G2.333`
- Mode: `planned_no_source`
- `source_edit_authority`: `false`
- Target: `tests/api/file_tests/test_strategy_management_api.py`
- Authorized work: route-surface fact audit and test-drift boundary recommendation only
- Not authorized: source edits, test edits, route mutation, compatibility cleanup, frontend path changes, or OpenSpec task mutation

## Source Edit Statement

No source or test files were edited in this node. This node only produced this report under `docs/reports/worklogs/claude-auto/`.

## Trigger

G2.332 completed the route-local provider seam for the three strategy execution handlers and recorded unrelated package route-surface drift in `tests/api/file_tests/test_strategy_management_api.py`:

- `strategy_module.router.prefix` is currently `""`, while the test expects `/api/v1/strategy`.
- route-method pair count is currently `23`, while the test expects `16`.
- `/api/v1/strategy/backtest/results/{backtest_id}/chart-data` is currently wired, while the test expects it not to be wired.

## Current Router Surface

Current live import of `app.api.strategy_management` reports:

| Fact | Current value |
|---|---:|
| `strategy_module.router.prefix` | `""` |
| route-method pair count | `23` |
| all route paths start with `/api/v1/strategy` | yes |
| chart-data route wired | yes |

Current route list:

| Path | Method | Name |
|---|---|---|
| `/api/v1/strategy/strategies` | `GET` | `list_strategies` |
| `/api/v1/strategy/strategies` | `POST` | `create_strategy` |
| `/api/v1/strategy/strategies/{strategy_id}` | `GET` | `get_strategy` |
| `/api/v1/strategy/strategies/{strategy_id}` | `PUT` | `update_strategy` |
| `/api/v1/strategy/strategies/{strategy_id}` | `DELETE` | `delete_strategy` |
| `/api/v1/strategy/{strategy_id}/start` | `POST` | `start_strategy` |
| `/api/v1/strategy/{strategy_id}/pause` | `POST` | `pause_strategy` |
| `/api/v1/strategy/{strategy_id}/resume` | `POST` | `resume_strategy` |
| `/api/v1/strategy/{strategy_id}/stop` | `POST` | `stop_strategy` |
| `/api/v1/strategy/models/train` | `POST` | `train_model` |
| `/api/v1/strategy/models/training/{task_id}/status` | `GET` | `get_training_status` |
| `/api/v1/strategy/models` | `GET` | `list_models` |
| `/api/v1/strategy/backtest/run` | `POST` | `run_backtest` |
| `/api/v1/strategy/backtest/results` | `GET` | `list_backtest_results` |
| `/api/v1/strategy/backtest/results/{backtest_id}` | `GET` | `get_backtest_result` |
| `/api/v1/strategy/backtest/status/{backtest_id}` | `GET` | `get_backtest_status` |
| `/api/v1/strategy/definitions` | `GET` | `get_strategy_definitions` |
| `/api/v1/strategy/run/single` | `POST` | `run_strategy_single` |
| `/api/v1/strategy/run/batch` | `POST` | `run_strategy_batch` |
| `/api/v1/strategy/results` | `GET` | `query_strategy_results` |
| `/api/v1/strategy/matched-stocks` | `GET` | `get_matched_stocks` |
| `/api/v1/strategy/stats/summary` | `GET` | `get_strategy_summary` |
| `/api/v1/strategy/backtest/results/{backtest_id}/chart-data` | `GET` | `get_backtest_chart_data` |

## Code Evidence

Package router composition:

- `web/backend/app/api/strategy_management/__init__.py` creates `router = APIRouter(tags=["strategy"])`.
- It includes `management_router` without a prefix.
- It includes `execution_router` with `prefix="/api/v1/strategy"`.
- It includes `chart_data_router` with `prefix="/api/v1/strategy"`.
- It exports `get_backtest_chart_data` in `__all__`.

Chart-data route:

- `web/backend/app/api/strategy_management/_chart_data_router.py` describes itself as `Backtest chart-data route (migrated from deleted get_backtest_result.py)`.
- It registers `GET /backtest/results/{backtest_id}/chart-data`.
- Because `__init__.py` includes it with `/api/v1/strategy`, its effective package route is `/api/v1/strategy/backtest/results/{backtest_id}/chart-data`.

## Test Drift Findings

| Finding | Current test assertion | Current code fact | Triage verdict |
|---|---|---|---|
| Router prefix assertion is stale | `strategy_module.router.prefix == "/api/v1/strategy"` | package router prefix is `""`; included child routes already carry full `/api/v1/strategy` paths | update test to assert full-path route surface rather than root router prefix |
| Route count assertion is stale | `len(route_pairs) == 16` | package route count is `23` | update expected count to `23` or assert expected subsets by domain slice |
| Chart-data exclusion assertion is stale | chart-data path should not be in route paths | chart-data router is explicitly included and exported | replace exclusion assertion with positive wired-route assertion |

## Current Test Result

Command:

`pytest tests/api/file_tests/test_strategy_management_api.py -q -n 0 --tb=short --no-cov`

Result:

- `3 failed, 8 passed, 1 warning`

Failing tests:

- `test_router_registers_expected_strategy_routes`
- `test_router_contains_expected_number_of_route_method_pairs`
- `test_chart_data_function_is_exported_but_not_wired_into_package_router`

Passing tests still confirm:

- exported symbols remain callable
- core route names remain stable for strategy list/model/backtest operations
- every route path starts with `/api/v1/strategy`
- backtest and model route subsets exist
- G2.332 provider-seam focused test passes

## Boundary Decision

The observed drift is test expectation drift, not evidence that the current `strategy_management` route composition should be rolled back.

Reasoning:

- Current code explicitly includes the chart-data router.
- The chart-data route file documents migration from deleted `get_backtest_result.py`.
- Full route paths consistently start with `/api/v1/strategy`.
- The package root router prefix being `""` is consistent with a composed router whose children include full prefixes.
- The current 23-route surface includes the original 16 base routes plus 6 execution routes and 1 chart-data route.

## Recommended Next Gate

Recommended next node:

`G2.334 strategy_management route-surface test alignment authorization`

Required declarations before editing tests:

- `source_edit_authority=true`
- exact target: `tests/api/file_tests/test_strategy_management_api.py`
- explicit non-goal: no backend route mutation
- expected route count: `23`
- expected chart-data route status: wired
- expected root router prefix behavior: `""`, with full-path route assertions retained
- verification command:
  - `pytest tests/api/file_tests/test_strategy_management_api.py -q -n 0 --tb=short --no-cov`
- rollback rule: restore previous test assertions if route surface audit evidence is invalidated

## Closeout

G2.333 no-source route-surface drift triage is complete. It recommends test alignment, not route rollback, but does not authorize any file edits.
