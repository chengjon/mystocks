# Backend Service Lifecycle DI Strategy Provider

## Status

- Date: 2026-06-13
- Task: G2.337
- Mode: source-authorized implementation
- Branch: `g2-337-strategy-datasourcefactory-provider-injection`
- Base: `origin/main`
- Base commit: `356f9e2f969d6f5bc59c999b9e8ee5d095e52f7b`
- OpenStock boundary: no OpenStock internals, tests, runtime, configuration, packaging, or repository files changed.

## Authorization Boundary

G2.336 selected `web/backend/app/api/strategy.py` as the next current-main service lifecycle DI candidate. G2.337 implements only that candidate.

Allowed implementation scope:

- `web/backend/app/api/strategy.py`
- `web/backend/tests/test_strategy_provider_injection.py`
- `governance/function-tree/catalog.yaml`
- `governance/compliance/unified-response-contract-legacy-baseline.json`
- `governance/mainline/task-cards/g2-337.yaml`
- `docs/reports/quality/backend-service-lifecycle-di-strategy-provider-2026-06-13.md`

Non-goals:

- No strategy route path, response envelope, parameter validation, exception mapping, or adapter request payload changes.
- No watchlist, technical_analysis, dashboard, frontend, runtime, dependency, configuration, OpenSpec implementation, or OpenStock internal changes.
- No deletion, retirement, compatibility-layer removal, or response-contract migration.

## Impact Evidence

GitNexus pre-edit impact was attempted before source modification:

- `api_impact(file=web/backend/app/api/strategy.py)`: returned no current routes for the file.
- `impact(target=get_strategy_definitions, file_path=web/backend/app/api/strategy.py)`: `not_found`.
- `impact(target=run_strategy_single, file_path=web/backend/app/api/strategy.py)`: `not_found`.
- `impact(target=run_strategy_batch, file_path=web/backend/app/api/strategy.py)`: `not_found`.
- `route_map(route=/api/v1/strategy)`: still maps strategy routes to `web/backend/app/api/strategy_management/_strategy_execution_router.py`, which is not the current-main source file.

This is treated as an index coverage limitation, not as proof of no impact. The implementation is therefore constrained by AST verification and focused strategy tests.

## Implementation Summary

`strategy.py` now follows the same provider boundary pattern already used by `technical_analysis.py`:

- Added `get_strategy_data_source()`.
- Kept the single `DataSourceFactory()` construction inside that provider boundary.
- Refreshed the function-tree catalog mapping so the current-main `strategy.py` route file and focused backend regression test map to `domain-03-node-01`.
- Registered existing `strategy.py` UnifiedResponse contract debt in the explicit legacy baseline so this DI task does not change response models or return envelopes.
- Injected `strategy_adapter: Any = Depends(get_strategy_data_source)` into:
  - `get_strategy_definitions`
  - `run_strategy_single`
  - `run_strategy_batch`
- Removed route-body `DataSourceFactory()` construction and route-body `get_data_source("strategy")` calls from those handlers.
- Preserved existing `strategy_adapter.get_data(...)` operations and payload keys:
  - `get_data("definitions")`
  - `get_data("run_single", params)`
  - `get_data("run_batch", params)`

## TDD Evidence

RED:

- Command: `pytest --no-cov web/backend/tests/test_strategy_provider_injection.py`
- Result before implementation: `2 failed`
- Expected failure:
  - three strategy routes still had inline `DataSourceFactory` calls
  - `get_strategy_data_source` provider did not exist

GREEN:

- Command: `pytest --no-cov web/backend/tests/test_strategy_provider_injection.py`
- Result after implementation: `2 passed in 8.73s`

## AST Residual Check

Post-implementation AST check:

| Target | Route-body `DataSourceFactory` | Route-body `get_data_source` | Provider arg |
| --- | ---: | ---: | --- |
| `get_strategy_definitions` | 0 | 0 | `strategy_adapter` |
| `run_strategy_single` | 0 | 0 | `strategy_adapter` |
| `run_strategy_batch` | 0 | 0 | `strategy_adapter` |

Provider boundary:

| Provider | `DataSourceFactory` | `get_data_source` | Data source |
| --- | ---: | ---: | --- |
| `get_strategy_data_source` | 1 | 1 | `strategy` |

## Validation

Focused checks run after implementation:

| Check | Result |
| --- | --- |
| `python -m py_compile web/backend/app/api/strategy.py` | pass |
| `pytest --no-cov web/backend/tests/test_strategy_provider_injection.py` | `2 passed in 19.63s` |
| `pytest --no-cov tests/api/file_tests/test_strategy_api.py` | `18 passed in 1.11s` |
| `pytest --no-cov tests/unit/api/test_strategy_api.py` | `17 passed in 1.35s` |
| `black --check web/backend/app/api/strategy.py web/backend/tests/test_strategy_provider_injection.py` | pass |
| `pytest --no-cov tests/unit/scripts/test_unified_response_contract_guard.py` | `11 passed in 2.20s` |
| `python scripts/compliance/unified_response_contract_guard.py --format json --root-dir $PWD --path web/backend/app/api/strategy.py` | pass; 0 errors; 6 legacy baseline exemptions |
| `git diff HEAD~1..HEAD --check` | clean |
| G2.337 mainline scope gate | `pass=True` |
| GitNexus `detect_changes(scope=compare, base_ref=origin/main)` | LOW risk; 5 changed files; 0 changed symbols; 0 affected processes |

PR CI remains the final merge gate.

## Rollback

Revert the G2.337 commit to restore route-body `DataSourceFactory()` construction and remove the focused provider-injection regression test, report, and task card.
