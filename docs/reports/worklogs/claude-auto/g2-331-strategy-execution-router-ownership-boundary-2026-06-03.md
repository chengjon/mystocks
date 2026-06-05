# G2.331 Strategy Execution Router Ownership Boundary

Date: 2026-06-03

## Gate

- Node: `G2.331`
- Mode: `planned_no_source`
- `source_edit_authority`: `false`
- Target: `web/backend/app/api/strategy_management/_strategy_execution_router.py`
- Authorized work: ownership determination and follow-on refactor boundary definition only
- Not authorized: source edits, route mutation, dependency injection implementation, frontend path changes, compatibility cleanup, deletion, or OpenSpec task mutation

## Source Edit Statement

No business source files were edited in this node. This node only produced this report under `docs/reports/worklogs/claude-auto/`.

## Starting Point From G2.330

G2.330 classified `web/backend/app/api/strategy_management/_strategy_execution_router.py` as a route direct-constructor residual:

- `DataSourceFactory()` x3
- `get_data_source("strategy")` x3
- Candidate disposition: secondary route provider-injection candidate
- Required next step: separate no-source ownership / authorization, or inclusion in an approved DataSourceFactory route-residual batch

Current file status check for this node:

- `web/backend/app/api/strategy_management/_strategy_execution_router.py` is tracked and not dirty.
- Existing dirty files noted from G2.330 remain outside this node: `web/backend/app/api/technical_analysis.py` and `web/backend/app/api/watchlist.py`.

## Ownership Determination

### Decision

Ownership belongs to the `strategy_management` route package execution slice, not to the global DataSourceFactory lifecycle track and not to the generic strategy service singleton track.

Primary owner module:

- `web/backend/app/api/strategy_management/_strategy_execution_router.py`

Owning package / route surface:

- `web/backend/app/api/strategy_management/__init__.py`
- Canonical package router prefix: `/api/v1/strategy`

Supporting implementation modules that may be referenced by a future authorized design, but are not owned by this node:

- `web/backend/app/services/data_source_factory/data_source_factory.py`
- `web/backend/app/services/adapters/strategy_adapter.py`
- `web/backend/app/services/strategy_service.py`

### Rationale

The residual is route-local and isolated to three handlers in `_strategy_execution_router.py`. The file already mixes two strategy access paths:

- First path: route -> `DataSourceFactory()` -> `get_data_source("strategy")` -> `StrategyDataSourceAdapter.get_data(...)` -> lazy `get_strategy_service()`
- Second path: route -> direct `get_strategy_service()` -> `StrategyService` methods

Because both paths converge on strategy-domain behavior, the residual is best classified as an execution-router seam inconsistency. It is not a request to redesign `DataSourceFactory`, retire the compatibility import, or eliminate the `StrategyService` singleton.

## Route And Dependency Evidence

Package mounting evidence:

| File | Evidence |
|---|---|
| `web/backend/app/api/strategy_management/__init__.py` | imports `execution_router` from `._strategy_execution_router` |
| `web/backend/app/api/strategy_management/__init__.py` | includes `execution_router` with `prefix="/api/v1/strategy"` |
| `tests/api/file_tests/test_strategy_management_api.py` | asserts `strategy_module.router.prefix == "/api/v1/strategy"` and locks 16 route-method pairs |

Handler-level matrix:

| Handler | Route path hint | Current strategy access path | Residual classification |
|---|---|---|---|
| `get_strategy_definitions` | `GET /definitions` under `/api/v1/strategy` | `DataSourceFactory()` then `get_data_source("strategy")` then `strategy_adapter.get_data("definitions")` | in scope for future provider-boundary change |
| `run_strategy_single` | `POST /run/single` under `/api/v1/strategy` | `DataSourceFactory()` then `get_data_source("strategy")` then `strategy_adapter.get_data("run_single", params)` | in scope for future provider-boundary change |
| `run_strategy_batch` | `POST /run/batch` under `/api/v1/strategy` | `DataSourceFactory()` then `get_data_source("strategy")` then `strategy_adapter.get_data("run_batch", params)` | in scope for future provider-boundary change |
| `query_strategy_results` | `GET /results` under `/api/v1/strategy` | direct `get_strategy_service()` then `service.query_strategy_results(...)` | out of source-change scope unless explicitly authorized |
| `get_matched_stocks` | `GET /matched-stocks` under `/api/v1/strategy` | direct `get_strategy_service()` then `service.get_matched_stocks(...)` | out of source-change scope unless explicitly authorized |
| `get_strategy_summary` | `GET /stats/summary` under `/api/v1/strategy` | direct `get_strategy_service()` then `service.get_strategy_definitions()` / `service.get_matched_stocks(...)` | out of source-change scope unless explicitly authorized |

DataSourceFactory implementation evidence:

- `web/backend/app/services/data_source_factory.py` is a backward-compatible entrypoint.
- The implementation lives under `web/backend/app/services/data_source_factory/data_source_factory.py`.
- `DataSourceFactory._create_single_data_source(...)` maps `source_type == "strategy"` to `StrategyDataSourceAdapter(...)`.
- `DataSourceFactory.get_data_source(source_name)` returns from the factory's `_data_sources` registry.
- The same implementation contains a module-global `_global_factory` and async `get_data_source_factory()`, but the current route residual does not use that provider; it directly constructs `DataSourceFactory()`.

Strategy adapter evidence:

- `web/backend/app/services/adapters/strategy_adapter.py` defines `StrategyDataSourceAdapter`.
- `StrategyDataSourceAdapter._get_strategy_service()` lazily imports and caches `get_strategy_service()`.
- `StrategyDataSourceAdapter.get_data(...)` handles `definitions`, `run_single`, and `run_batch` behavior.

Strategy service evidence:

- `web/backend/app/services/strategy_service.py` defines `StrategyService`.
- The same file defines module-global `_strategy_service_instance` and `get_strategy_service()`.
- Later handlers in `_strategy_execution_router.py` already call `get_strategy_service()` directly.

## GitNexus / API Impact Evidence

GitNexus route-level `api_impact` identified 6 routes for the target file:

- `/api/v1/strategy/definitions`
- `/api/v1/strategy/run/single`
- `/api/v1/strategy/run/batch`
- `/api/v1/strategy/results`
- `/api/v1/strategy/matched-stocks`
- `/api/v1/strategy/stats/summary`

GitNexus reported `LOW` risk for each route, with 0 direct consumers and 0 execution flows. Treat this as supplemental evidence only. Current-source and file-level route tests remain the stronger evidence for route surface stability.

## External Consumer / Compatibility Notes

Observed consumer evidence:

- `tests/api/file_tests/test_strategy_management_api.py` locks package route prefix and expected route-method pairs.
- `web/frontend/src/config/api.js` contains active strategy endpoint constants using `/api/strategy/...`, not `/api/v1/strategy/...`.
- `web/frontend/src/api/index.js.deprecated` contains deprecated strategy calls using `/v1/strategy/...`.
- No direct active frontend caller was confirmed for `runSingle`, `runBatch`, `matchedStocks`, or `stats` in this node's active-source grep, but this is not proof of absence.

Boundary implication:

- G2.331 does not authorize frontend path reconciliation.
- Any future source node that changes response shape or route exposure must include backend route tests and at least a targeted frontend/API path smoke.

## Existing Governance Constraints

Relevant prior decisions and constraints:

- `strategy_management/` is the canonical strategy route package.
- `backend-domain-router-reconciliation-2026-05-18.md` records strategy route compatibility as active and cautions that canonical path decisions must not be bundled with broad compatibility deletion.
- `openspec/changes/migrate-backend-singletons-to-lifecycle-di/tasks.md` records that lifecycle DI work should preserve compatibility getters and avoid expanding to unrelated singleton/getter candidates in the same batch.
- `architecture/STANDARDS.md` requires architecture convergence, compatibility-layer retirement, route mutation, and DI lifecycle work to pass explicit governance.

## Follow-On Source Boundary

If a later node sets `source_edit_authority=true`, the permitted source boundary should be narrow:

Allowed candidate files:

- `web/backend/app/api/strategy_management/_strategy_execution_router.py`
- Focused tests that directly prove the changed route behavior and injection/override behavior, likely under `tests/api/file_tests/` or `web/backend/tests/`

Conditionally allowed only if the authorized design explicitly chooses a shared provider seam:

- `web/backend/app/api/strategy_management/__init__.py`
- `web/backend/app/services/data_source_factory/data_source_factory.py`
- `web/backend/app/services/adapters/strategy_adapter.py`
- `web/backend/app/services/strategy_service.py`
- `web/backend/app/app_factory.py`

Out of scope unless separately authorized:

- `web/backend/app/api/technical_analysis.py`
- `web/backend/app/api/watchlist.py`
- `web/backend/app/services/data_source_factory.py` compatibility entrypoint cleanup
- global `_global_factory` lifecycle redesign
- `StrategyService` singleton redesign
- route prefix changes
- frontend API path changes
- legacy `strategy_mgmt` / compatibility route retirement
- OpenSpec archive or task checklist edits

## Acceptable Future Design Directions

This node does not choose an implementation. It only bounds acceptable directions for a future authorized node.

Potential direction A: route-local provider dependency

- Introduce a small dependency seam for the strategy data-source adapter used by the three execution handlers.
- Keep route paths, response envelopes, error codes, and payload keys stable.
- Tests should override the dependency and assert the three DataSourceFactory route paths no longer construct a new factory per request.

Potential direction B: unify execution handlers on `get_strategy_service()`

- Replace the adapter detour only if the future design proves endpoint behavior remains equivalent for `definitions`, `run_single`, and `run_batch`.
- This direction touches behavior more directly because it bypasses `StrategyDataSourceAdapter` fallback/mock behavior. It requires stronger tests than direction A.

Potential direction C: reuse global `get_data_source_factory()`

- This reduces direct factory construction but keeps the factory/adapter path.
- It does not solve full lifecycle ownership unless paired with app lifecycle install/teardown semantics.
- It may be acceptable as a smaller interim step only if explicit acceptance criteria say so.

## Recommended Next Gate

Recommended next node:

`G2.332 strategy execution DataSourceFactory provider authorization`

Required declarations before source work:

- `source_edit_authority=true`
- exact chosen design direction
- explicit route list in scope: `/api/v1/strategy/definitions`, `/api/v1/strategy/run/single`, `/api/v1/strategy/run/batch`
- explicit non-goals for `/results`, `/matched-stocks`, `/stats/summary`
- GitNexus impact for edited handler symbols before edits
- dirty-worktree handling rule
- tests to run
- rollback rule

Recommended verification for a future source node:

- `pytest tests/api/file_tests/test_strategy_management_api.py -q -n 0 --tb=short --no-cov`
- focused backend behavior tests for the three execution handlers with provider override/fake adapter
- route/API smoke for `/api/v1/strategy/definitions`, `/api/v1/strategy/run/single`, and `/api/v1/strategy/run/batch`
- if frontend path behavior is touched, targeted frontend API/path tests must be added to that source node

## Closeout

G2.331 ownership determination is complete as a pure governance node. The target is eligible for a later authorization node, but this report does not grant source edit authority.
