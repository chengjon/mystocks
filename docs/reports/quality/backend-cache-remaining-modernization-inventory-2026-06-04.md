# Backend Cache Remaining Modernization Inventory

## Status

- Date: `2026-06-04`
- Prepared by: `G2.345`
- Mode: no-source inventory
- Scope: tracked files under `web/backend/app`, `src`, and `tests` whose paths contain `cache` or `dashboard`
- Purpose: define remaining cache modernization surfaces after `Cache Core Batch1 Closed`
- Not authorized: source edits, deletion, consolidation, route changes, frontend changes, OpenSpec mutation

## Reading Rules

This inventory is a planning aid, not a deletion list.

Per `architecture/STANDARDS.md`, `unused` or `unreferenced` is not enough to delete a file. Any cleanup must first prove both code-path safety and function-tree status. Files below should be classified by future no-source nodes before implementation.

## Priority Groups

| Priority | Group | Handling |
|---|---|---|
| P1 | Dashboard cache helper cluster | Combine into one no-source G node; do not split one file per decision |
| P2 | Cache API route cluster | Inventory route/helper ownership and response contract behavior together |
| P3 | Core cache helper modules outside Batch1 | Decide whether these are canonical web-backend cache modules, compatibility modules, or separate subsystem helpers |
| P4 | `src/` cache subsystem | Reconcile application/core/infrastructure/GPU cache surfaces with web-backend cache lifecycle only after P1/P2 are bounded |
| P5 | Test and E2E cache/dashboard coverage | Use after source boundaries are decided; do not use test file existence as deletion evidence |

## P1 Dashboard Cache Helper Cluster

Recommended next node: `G2.346 dashboard cache helper surface inventory / no-source`.

Files:

- `web/backend/app/api/dashboard.py`
  - current status: active route module; contains route-local cache wrapper retained by G2.343/G2.344
  - handling: preserve as active route surface until a dashboard-cluster design says otherwise
- `web/backend/app/api/dashboard_cache.py`
  - current status: dashboard cache helper
  - handling: classify helper ownership, memory/cache-key policy, and relationship to dashboard route wrapper
- `web/backend/app/api/dashboard_data_source.py`
  - current status: dashboard data-source helper; contains global-like markers in the inventory scan
  - handling: classify data-source lifecycle ownership separately from cache wrapper behavior
- `web/backend/app/api/dashboard_builders.py`
  - current status: dashboard response/data builder helper
  - handling: classify as response construction helper; no cache-lifecycle source work without cluster authorization
- `web/backend/app/services/adapters/dashboard_adapter.py`
  - current status: dashboard service adapter
  - handling: include in dependency map for dashboard cache/data-source ownership
- `web/backend/app/services/data_adapters/dashboard.py`
  - current status: dashboard data adapter
  - handling: include in dependency map; do not merge with route helpers without explicit source authorization
- `web/backend/app/models/dashboard.py`
  - current status: dashboard model/schema surface
  - handling: treat as contract/model surface, not a cache implementation
- `web/backend/app/services/risk_management/risk_dashboard.py`
  - current status: risk dashboard service surface
  - handling: keep outside dashboard-cache source work unless future inventory finds direct cache ownership
- `web/backend/app/api/governance_dashboard.py`
  - current status: governance dashboard route module
  - handling: separate dashboard-named route surface; not part of the dashboard cache helper cluster by default
- `web/backend/app/api/_governance_dashboard_responses.py`
  - current status: governance dashboard response helper
  - handling: separate response-helper surface

## P2 Cache API Route Cluster

Files:

- `web/backend/app/api/cache.py`
  - current status: cache route entry; inventory scan found getter/global-like/route markers
  - handling: decide route entry ownership and relationship to split helper modules
- `web/backend/app/api/_cache_basic_routes.py`
  - current status: cache basic route helper; inventory scan found getter/global-like/route markers
  - handling: inspect route dependency injection and cache manager access together with `cache.py`
- `web/backend/app/api/_cache_eviction_routes.py`
  - current status: cache eviction route helper
  - handling: classify route helper boundary and response contract
- `web/backend/app/api/_cache_prewarming_routes.py`
  - current status: cache prewarming route helper
  - handling: classify route helper boundary and lifecycle effects
- `web/backend/app/api/indicators/indicator_cache.py`
  - current status: indicator cache route/helper surface
  - handling: keep in indicator domain unless future cache API inventory proves shared ownership
- `web/backend/app/api/indicators/_indicator_cache_responses.py`
  - current status: indicator cache response helper
  - handling: response contract surface, not lifecycle owner by default

## P3 Core Cache Helper Modules Outside Batch1

Files:

- `web/backend/app/core/cache/__init__.py`
  - current status: package export surface
  - handling: do not add/remove exports without compatibility review
- `web/backend/app/core/cache/core.py`
  - current status: core cache helper; inventory scan found global-like markers
  - handling: ownership decision required before lifecycle edits
- `web/backend/app/core/cache/batch_ops.py`
  - current status: batch operations helper
  - handling: classify as operation helper; no lifecycle edits yet
- `web/backend/app/core/cache/decorators.py`
  - current status: decorator helper
  - handling: classify runtime side effects and import paths before edits
- `web/backend/app/core/cache/fetch_write.py`
  - current status: fetch/write helper
  - handling: classify data access/cache write responsibility before edits
- `web/backend/app/core/cache/multi_level.py`
  - current status: multi-level cache implementation; inventory scan found global-like markers
  - handling: separate high-risk ownership decision required

Already closed in Batch1:

- `web/backend/app/core/cache_lifecycle.py`
- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache/factory.py`
- `web/backend/app/core/cache/stats_health.py`

## P4 `src/` Cache Subsystem

Files:

- `src/application/market_data/price_stream_processor_cached.py`
- `src/core/cache/__init__.py`
- `src/core/cache/decorators.py`
- `src/core/cache/multi_level.py`
- `src/core/data_source/cache.py`
- `src/core/data_source/smart_cache.py`
- `src/gpu/api_system/utils/_cache_manager_reporting.py`
- `src/gpu/api_system/utils/cache_optimization.py`
- `src/gpu/api_system/utils/cache_optimization_enhanced.py`
- `src/infrastructure/cache/__init__.py`
- `src/infrastructure/cache/redis_lock.py`
- `src/mock/mock_Dashboard.py`

Handling:

- do not fold these into the web-backend cache lifecycle track by name alone
- separate application cache, data-source cache, GPU cache, infrastructure Redis lock, and mock dashboard concerns
- future source work should start with no-source ownership classification per domain cluster

## P5 Test And E2E Surfaces

Representative cache/dashboard test files remain broad and should be used as verification surfaces after ownership decisions:

- `web/backend/tests/test_cache_lifecycle.py`
- `tests/api/file_tests/test_cache_api.py`
- `tests/api/file_tests/test_dashboard_api.py`
- `tests/api/test_cache_file.py`
- `tests/integration/test_dashboard_api.py`
- `tests/performance/test_cache_strategy.py`
- `tests/performance/test_smart_cache_benchmark.py`
- `tests/unit/core/test_web_backend_multilevel_cache_runtime.py`
- `tests/unit/core/test_src_core_multilevel_cache_runtime.py`
- `tests/e2e/dashboard.spec.ts`
- `tests/e2e/dashboard-page.spec.ts`
- `tests/e2e/specs/dashboard.spec.ts`

## Next Gate

Start with `G2.346 dashboard cache helper surface inventory / no-source`.

The next gate should produce:

- one dashboard-cache cluster map
- one explicit list of active route/helper/model/service responsibilities
- one decision about whether a later source node should edit route wrapper behavior, helper module ownership, tests only, or nothing
- no source edits during inventory
