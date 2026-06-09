# Backend Cache Core Batch1 Stage Summary

## Status

- Date: `2026-06-04`
- Stage marker: `Cache Core Batch1 Closed`
- Scope: backend cache lifecycle ownership, core compatibility wrappers, stats-health module-level getter tail, and dashboard-local cache wrapper classification/test pinning
- Closeout node: `G2.345`
- Source authority for this report: none; documentation-only summary

## What Closed

Cache Core Batch1 closed the first backend cache lifecycle convergence slice.

The closed stage establishes `web/backend/app/core/cache_lifecycle.py` as the canonical lifecycle provider used by `web/backend/app/core/cache_manager.py`. Public cache manager getter/reset surfaces remain available, but they delegate through the canonical provider rather than owning separate module-global lifecycle state.

The stage also repaired the two first compatibility-wrapper surfaces identified by G2.338:

- `web/backend/app/core/cache/factory.py` is retained as a thin compatibility wrapper over canonical cache manager lifecycle state.
- `web/backend/app/core/cache/stats_health.py` keeps `CacheStatsHealthMixin` intact while its module-level `get_cache_manager_async(...)` tail delegates to canonical async cache lifecycle state.

Dashboard-local cache handling is not deleted. G2.343/G2.344 classify the dashboard wrapper as active route-local memoization over the canonical async getter and add file-level tests to pin delegation, Redis forwarding, memoization, and `bypass_cache=True` behavior.

## Evidence Chain

| Node | Role | Result |
|---|---|---|
| G2.335 | Cache manager lifecycle ownership boundary | Classified `cache_manager.py` as high-risk shared lifecycle candidate; required design before implementation |
| G2.336 | Lifecycle design preflight | Selected explicit `CacheLifecycleProvider` with compatibility getters |
| G2.337 | Provider implementation closeout | Added canonical lifecycle provider path and regression coverage |
| G2.338 | Parallel-surface inventory | Split remaining surfaces into `factory.py`, `stats_health.py`, and dashboard-local handling |
| G2.339 | Factory preflight | Classified `factory.py` as dormant compatibility wrapper |
| G2.340 | Factory wrapper repair | Converted `factory.py` to a thin canonical wrapper |
| G2.341 | Stats-health ownership decision | Split active mixin from broken dormant module-level getter tail |
| G2.342 | Stats-health getter repair | Converted module-level getter tail to canonical async delegation |
| G2.343 | Dashboard-local inventory | Classified dashboard-local wrapper as active route-local memoization |
| G2.344 | Dashboard wrapper closeout | Retained wrapper, normalized dashboard exceptions, and added focused dashboard cache tests |
| G2.345 | Stage closeout | Marks Batch1 closed and moves remaining work into grouped inventories |

## Focused Verification Evidence

Current focused rerun for the Batch1 closeout:

- `pytest web/backend/tests/test_cache_lifecycle.py -q -n 0 --tb=short --no-cov`
  - result: `10 passed`
- `pytest web/backend/tests/test_cache_manager.py web/backend/tests/test_cache_api.py web/backend/tests/test_cache_eviction.py web/backend/tests/test_cache_integration.py web/backend/tests/test_cache_prewarming.py -q -n 0 --tb=short --no-cov`
  - result: `108 passed, 29 skipped`
  - skipped cases were existing TDengine-dependent cache manager tests
- `pytest tests/api/file_tests/test_cache_api.py tests/api/file_tests/test_dashboard_api.py -q -n 0 --tb=short --no-cov`
  - result: `27 passed, 1 warning`
  - warning was the existing ddtrace deprecation warning for `HTTP_422_UNPROCESSABLE_ENTITY`

This report does not convert those focused results into full-repository quality claims. Whole-worktree status remains dirty and must be evaluated separately.

## Closed Files

Batch1 source/test closeout applies to the following focused files:

- `web/backend/app/core/cache_lifecycle.py`
- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache/factory.py`
- `web/backend/app/core/cache/stats_health.py`
- `web/backend/tests/test_cache_lifecycle.py`
- `web/backend/app/api/dashboard.py`
- `tests/api/file_tests/test_dashboard_api.py`

## Remaining Boundaries

Batch1 does not authorize deletion or consolidation of the wider cache subsystem.

The following remain open by design:

- dashboard cache helpers and data-source modules
- cache API route modules
- `web/backend/app/core/cache/*` helper modules outside the lifecycle wrapper path
- `src/core/cache`, `src/core/data_source/*cache*`, and GPU cache utilities
- Redis service/cache-service ownership and lifecycle decisions
- all frontend/dashboard E2E cache behavior

## Next Recommended Node

`G2.346 dashboard cache helper surface inventory / no-source`

This next node should inspect dashboard cache files as a cluster, not one file at a time, and should produce one future authorization boundary if source work is required.
