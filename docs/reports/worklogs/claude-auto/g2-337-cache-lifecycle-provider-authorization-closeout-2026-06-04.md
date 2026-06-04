# G2.337 Cache Lifecycle Provider Authorization Closeout

## Metadata

- Date: `2026-06-04`
- Node: `G2.337`
- Mode: source implementation after G2.336 design preflight
- `source_edit_authority`: `true`
- Parent: `G2.336 cache manager lifecycle design preflight`
- Scope: first-lane cache lifecycle provider implementation only
- Non-goals: no API route rewrite, no dashboard lifecycle rewrite, no `cache/factory.py` consolidation, no `stats_health.py` consolidation, no response schema changes, no cache invalidation behavior changes, no compatibility getter deletion, no frontend changes, no OpenSpec mutation

## Source Changes

Changed files:

- `web/backend/app/core/cache_lifecycle.py`
- `web/backend/app/core/cache_manager.py`
- `web/backend/tests/test_cache_lifecycle.py`

Implementation summary:

- Added `CacheLifecycleProvider` as the explicit canonical owner for cache manager lifecycle state.
- Moved lifecycle ownership out of module-level `_manager` / `_async_manager` slots and into the provider instance.
- Kept public compatibility getters in `cache_manager.py`:
  - `get_cache_manager()`
  - `get_cache_manager_async(...)`
  - `reset_cache_manager()`
- Kept `CacheManager` and `AsyncCacheManager` importable from `cache_manager.py`.
- Preserved reset behavior:
  - async wrapper closes backing sync manager through `AsyncCacheManager.close()`
  - sync manager closes directly when no async wrapper exists

## TDD Evidence

RED command:

- `pytest web/backend/tests/test_cache_lifecycle.py -q -n 0 --tb=short --no-cov`

RED result before implementation:

- `5 failed`
- expected failures:
  - `ModuleNotFoundError: No module named 'app.core.cache_lifecycle'`
  - existing public getters did not delegate to a lifecycle provider

GREEN command:

- `pytest web/backend/tests/test_cache_lifecycle.py -q -n 0 --tb=short --no-cov`

GREEN result after implementation and test-double correction:

- `5 passed`

Debug note:

- Initial GREEN run exposed that the dummy async manager did not model production `AsyncCacheManager.close()` semantics.
- The test double was corrected so async close also closes its backing sync manager, matching production behavior.
- Production reset behavior was not widened beyond the existing close contract.

## GitNexus Impact Evidence

Pre-change impact was run before source edits.

`get_cache_manager`:

- risk: `HIGH`
- impacted count: `10`
- direct callers: `10`
- affected processes: `2`
- affected modules: `3`
- affected processes include:
  - `get_cached_data`
  - `get_cache_status`

`get_cache_manager_async`:

- risk: `LOW`
- impacted count: `2`
- direct callers: `1`
- affected processes: `1`
- affected process:
  - `get_dashboard_summary`

`reset_cache_manager`:

- risk: `LOW`
- impacted count: `0`
- direct callers/processes/modules reported: `0`

Index status:

- GitNexus index was stale because current commit differs from indexed commit.
- Impact was used as required blast-radius screening, and live pytest verification is the runtime evidence for this source lane.

## Verification

Passed:

- `pytest web/backend/tests/test_cache_lifecycle.py -q -n 0 --tb=short --no-cov`
  - `5 passed`
- `pytest web/backend/tests/test_cache_manager.py web/backend/tests/test_cache_api.py web/backend/tests/test_cache_eviction.py web/backend/tests/test_cache_integration.py web/backend/tests/test_cache_prewarming.py -q -n 0 --tb=short --no-cov`
  - `108 passed, 29 skipped`
  - skipped tests are TDengine-dependent cache manager tests in the existing suite
- `pytest tests/api/file_tests/test_cache_api.py tests/api/file_tests/test_dashboard_api.py -q -n 0 --tb=short --no-cov`
  - `25 passed, 1 warning`
  - warning: existing ddtrace deprecation warning for `HTTP_422_UNPROCESSABLE_ENTITY`
- `python -m py_compile web/backend/app/core/cache_manager.py web/backend/app/core/cache_lifecycle.py web/backend/tests/test_cache_lifecycle.py`
  - exit `0`
- `git diff --check -- web/backend/app/core/cache_manager.py web/backend/app/core/cache_lifecycle.py web/backend/tests/test_cache_lifecycle.py`
  - exit `0`

## Detect Changes Caveat

`gitnexus detect_changes(scope="all")` was run after implementation.

Result:

- changed files: `840`
- changed symbols: `3167`
- affected processes: `12`
- risk level: `high`

This is not suitable as this micro-batch's scoped risk conclusion because the current `main` worktree already contains a large unrelated dirty set.

Scoped status for this node's implementation files shows:

- modified: `web/backend/app/core/cache_manager.py`
- added: `web/backend/app/core/cache_lifecycle.py`
- added: `web/backend/tests/test_cache_lifecycle.py`

The G2.335/G2.336/G2.337 worklogs are also new governance artifacts from this continuation.

## Scope Control

No changes were made to:

- `web/backend/app/api/_cache_basic_routes.py`
- `web/backend/app/api/cache.py`
- `web/backend/app/api/dashboard.py`
- `web/backend/app/core/cache/factory.py`
- `web/backend/app/core/cache/stats_health.py`
- `web/backend/app/core/cache_eviction.py`
- `web/backend/app/core/cache_integration.py`
- `web/backend/app/core/cache_prewarming.py`
- `tests/api/file_tests/test_cache_api.py`
- `tests/api/file_tests/test_dashboard_api.py`
- any frontend file
- any OpenSpec file

## Remaining Boundaries

This node does not retire old public getter surfaces. They remain compatibility wrappers by design.

This node does not consolidate the separate lifecycle-like surfaces in:

- `web/backend/app/core/cache/factory.py`
- `web/backend/app/core/cache/stats_health.py`
- `web/backend/app/api/dashboard.py`

Those surfaces need a separate no-source inventory or authorization node before any consolidation.

## Recommended Next Gate

Recommended next node:

`G2.338 cache lifecycle parallel-surface inventory / no-source`

Required properties:

- `source_edit_authority=false`
- inventory `cache/factory.py`, `stats_health.py`, and dashboard-local cache globals
- classify each as compatibility wrapper, duplicate lifecycle owner, or separate domain surface
- do not edit source
- decide whether a later consolidation lane is warranted

## Closeout

G2.337 completed the first-lane cache lifecycle provider implementation within the approved source boundary.

The cache lifecycle owner is now explicit via `CacheLifecycleProvider`, and the existing public getter API remains intact as a compatibility wrapper surface.
