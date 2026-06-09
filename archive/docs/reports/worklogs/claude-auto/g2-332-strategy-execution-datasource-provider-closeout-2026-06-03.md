# G2.332 Strategy Execution DataSource Provider Closeout

Date: 2026-06-03

## Gate

- Node: `G2.332`
- Mode: source implementation after G2.331 ownership approval
- `source_edit_authority`: `true`
- Design direction: route-local provider dependency
- Scope: `web/backend/app/api/strategy_management/_strategy_execution_router.py` execution handlers only

## Source Changes

Changed files:

- `web/backend/app/api/strategy_management/_strategy_execution_router.py`
- `tests/api/file_tests/test_strategy_management_api.py`

Implementation summary:

- Added `get_strategy_data_source() -> Any` as a narrow provider seam in `_strategy_execution_router.py`.
- Replaced the three execution handler body-local `DataSourceFactory()` constructions with `await get_strategy_data_source()`.
- Left route paths, response envelopes, response keys, status/error handling branches, and the later direct `get_strategy_service()` handlers unchanged.

Handlers changed:

- `get_strategy_definitions`
- `run_strategy_single`
- `run_strategy_batch`

Handlers intentionally unchanged:

- `query_strategy_results`
- `get_matched_stocks`
- `get_strategy_summary`

## TDD Evidence

RED:

- Command:
  - `pytest tests/api/file_tests/test_strategy_management_api.py::TestStrategyManagementAPIFile::test_strategy_execution_handlers_use_overridable_strategy_data_source -q -n 0 --tb=short --no-cov`
- Result before implementation:
  - failed as expected
  - failure reason: the handler still instantiated `DataSourceFactory`, triggering the sentinel `AssertionError`

GREEN:

- Command:
  - `pytest tests/api/file_tests/test_strategy_management_api.py::TestStrategyManagementAPIFile::test_strategy_execution_handlers_use_overridable_strategy_data_source -q -n 0 --tb=short --no-cov`
- Result after implementation:
  - `1 passed, 1 warning`

The new test verifies that:

- a fake strategy data-source provider can drive all three execution handlers
- a sentinel `DataSourceFactory` is not instantiated by those handlers
- `definitions`, `run_single`, and `run_batch` adapter calls preserve expected endpoint names and parameter payloads
- response data envelopes for the three handlers remain stable

## Impact Evidence

Pre-change GitNexus evidence:

- `api_impact` for `web/backend/app/api/strategy_management/_strategy_execution_router.py` identified 6 routes.
- All 6 routes reported `LOW` risk, 0 direct consumers, and 0 affected execution flows.
- Upstream impact for `get_strategy_definitions`, `run_strategy_single`, and `run_strategy_batch` each reported:
  - risk: `LOW`
  - impacted count: `0`
  - affected processes: `0`

Post-change GitNexus evidence:

- `detect_changes(scope="all")` reported high risk because the current worktree already contains a large unrelated dirty set: 844 changed files.
- This result is not suitable as this micro-batch's scoped risk conclusion.
- Exact scoped file status after this node shows only the two intended source/test files changed for G2.332, plus previously created G2.330/G2.331 reports.

## Verification

Passed:

- `pytest tests/api/file_tests/test_strategy_management_api.py::TestStrategyManagementAPIFile::test_strategy_execution_handlers_use_overridable_strategy_data_source -q -n 0 --tb=short --no-cov`
  - `1 passed, 1 warning`
- `python -m py_compile web/backend/app/api/strategy_management/_strategy_execution_router.py tests/api/file_tests/test_strategy_management_api.py`
  - exit `0`
- `git diff --check -- web/backend/app/api/strategy_management/_strategy_execution_router.py tests/api/file_tests/test_strategy_management_api.py`
  - exit `0`

Known unrelated/older route-surface drift observed:

- Command:
  - `pytest tests/api/file_tests/test_strategy_management_api.py -q -n 0 --tb=short --no-cov`
- Result:
  - `3 failed, 8 passed, 1 warning`
- Failed assertions:
  - `strategy_module.router.prefix` is currently `""`, while the test expects `/api/v1/strategy`
  - route-method pair count is currently `23`, while the test expects `16`
  - `/api/v1/strategy/backtest/results/{backtest_id}/chart-data` is currently wired, while the test expects it not to be wired
- These failures are outside the G2.332 source boundary and existed independently of the provider-seam behavior under test.

## Scope Control

No changes were made to:

- `web/backend/app/api/strategy_management/__init__.py`
- `web/backend/app/services/data_source_factory.py`
- `web/backend/app/services/data_source_factory/data_source_factory.py`
- `web/backend/app/services/adapters/strategy_adapter.py`
- `web/backend/app/services/strategy_service.py`
- `web/backend/app/api/technical_analysis.py`
- `web/backend/app/api/watchlist.py`
- frontend API config or consumers
- legacy strategy router compatibility surfaces

## Next Gate Recommendation

Recommended next governance node:

`G2.333 strategy_management route-surface test drift triage`

Reason:

- Full `test_strategy_management_api.py` currently encodes stale route-surface expectations unrelated to this provider-seam change.
- Before broadening verification for future strategy route changes, the package route prefix/count/chart-data expectations need a no-source fact audit and then an explicit source authorization if the tests should be updated.

## Closeout

G2.332 completed the route-local provider seam for the three strategy execution handlers within the approved source boundary. Focused behavior verification passed; broader package route tests still contain unrelated route-surface drift and remain unresolved.
