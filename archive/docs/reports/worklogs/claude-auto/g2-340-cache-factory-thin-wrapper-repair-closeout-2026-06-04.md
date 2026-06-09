# G2.340 Cache Factory Thin-Wrapper Repair Closeout

## Metadata

- Date: `2026-06-04`
- Node: `G2.340`
- Mode: source implementation after G2.339 preflight
- `source_edit_authority`: `true`
- Parent: `G2.339 cache factory dormant lifecycle preflight`
- Target: `web/backend/app/core/cache/factory.py`
- Scope: repair the import-broken dormant factory surface by converting it to a thin compatibility wrapper
- Non-goals: no deletion, no route changes, no dashboard changes, no `stats_health.py` changes, no `cache_manager.py` API changes, no `cache_lifecycle.py` API changes, no frontend changes, no OpenSpec mutation

## Source Changes

Changed files:

- `web/backend/app/core/cache/factory.py`
- `web/backend/tests/test_cache_lifecycle.py`

Implementation summary:

- Replaced missing `from .manager import CacheManager` with canonical `app.core.cache_manager` delegation.
- Removed local `_cache_manager` lifecycle state from `cache/factory.py`.
- Preserved `CacheManager` as a compatibility alias to `canonical_cache_manager.CacheManager`.
- Kept `get_cache_manager(tdengine_manager=...)` as a compatibility wrapper.
- Kept `reset_cache_manager()` as a compatibility wrapper.
- `get_cache_manager(tdengine_manager=...)` delegates to the canonical lifecycle provider so callers can still pass an explicit TDengine manager before first construction.

## TDD Evidence

RED command:

- `pytest web/backend/tests/test_cache_lifecycle.py -q -n 0 --tb=short --no-cov`

RED result before implementation:

- `3 failed, 5 passed`
- expected failures:
  - `ModuleNotFoundError: No module named 'app.core.cache.manager'`
  - failures came from importing `app.core.cache.factory`

GREEN command:

- `pytest web/backend/tests/test_cache_lifecycle.py -q -n 0 --tb=short --no-cov`

GREEN result after implementation:

- `8 passed`

Test coverage added:

- `app.core.cache.factory` imports successfully
- `factory.get_cache_manager(tdengine_manager=...)` delegates to canonical lifecycle provider
- `factory.reset_cache_manager()` delegates to canonical `cache_manager.reset_cache_manager`

## GitNexus Evidence

Pre-edit GitNexus impact was attempted for:

- `web/backend/app/core/cache/factory.py:get_cache_manager`
- `web/backend/app/core/cache/factory.py:reset_cache_manager`

Result:

- both returned `not_found`
- risk: `UNKNOWN`
- index status: stale

This matches G2.339's prior finding that the dormant factory symbols are not resolved by the current GitNexus index. The edit was therefore kept to the explicitly authorized narrow file and validated with live import/tests.

## Verification

Passed:

- `pytest web/backend/tests/test_cache_lifecycle.py -q -n 0 --tb=short --no-cov`
  - `8 passed`
- `pytest web/backend/tests/test_cache_manager.py web/backend/tests/test_cache_api.py web/backend/tests/test_cache_eviction.py web/backend/tests/test_cache_integration.py web/backend/tests/test_cache_prewarming.py -q -n 0 --tb=short --no-cov`
  - `108 passed, 29 skipped`
  - skipped tests are existing TDengine-dependent cache manager tests
- `pytest tests/api/file_tests/test_cache_api.py tests/api/file_tests/test_dashboard_api.py -q -n 0 --tb=short --no-cov`
  - `25 passed, 1 warning`
  - warning: existing ddtrace deprecation warning for `HTTP_422_UNPROCESSABLE_ENTITY`
- `python -m py_compile web/backend/app/core/cache/factory.py web/backend/app/core/cache_manager.py web/backend/app/core/cache_lifecycle.py web/backend/tests/test_cache_lifecycle.py`
  - exit `0`
- `git diff --check -- web/backend/app/core/cache/factory.py web/backend/app/core/cache_manager.py web/backend/app/core/cache_lifecycle.py web/backend/tests/test_cache_lifecycle.py`
  - exit `0`
- direct import check for `app.core.cache.factory`
  - printed `app.core.cache.factory`
  - `hasattr(f, "get_cache_manager") == True`
  - `hasattr(f, "reset_cache_manager") == True`

## Detect Changes Caveat

`gitnexus detect_changes(scope="all")` was run after implementation.

Result:

- changed files: `841`
- changed symbols: `3204`
- affected processes: `12`
- risk level: `high`

This remains unsuitable as this micro-batch's scoped risk conclusion because the current `main` worktree already contains a large unrelated dirty set.

Scoped source changes for this node are limited to:

- `web/backend/app/core/cache/factory.py`
- `web/backend/tests/test_cache_lifecycle.py`

The pre-existing G2.337 cache lifecycle source changes remain in the worktree:

- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache_lifecycle.py`

## Scope Control

No changes were made to:

- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache_lifecycle.py`
- `web/backend/app/core/cache/stats_health.py`
- `web/backend/app/api/dashboard.py`
- route modules
- frontend files
- OpenSpec files

## Remaining Boundaries

This node did not delete `cache/factory.py`.

This node did not expose `get_cache_manager` from `app.core.cache.__init__`.

This node did not consolidate `stats_health.py` or dashboard-local cache lifecycle state.

## Recommended Next Gate

Recommended next node:

`G2.341 cache stats-health ownership decision / no-source`

Required properties:

- `source_edit_authority=false`
- focus only on `web/backend/app/core/cache/stats_health.py`
- decide whether it is obsolete duplicate implementation, separate stats-health domain surface, or compatibility-wrapper candidate
- do not edit source

Alternate next node:

`G2.341 cache factory export policy / no-source`

Use the alternate only if maintainers want to decide whether `app.core.cache.__init__` should expose the repaired factory compatibility wrappers.

## Closeout

G2.340 completed the narrow cache factory thin-wrapper repair.

`app.core.cache.factory` is importable again, no longer owns local cache lifecycle state, and delegates through the canonical cache lifecycle provider path.
