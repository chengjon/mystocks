# G2.338 Cache Lifecycle Parallel-Surface Inventory

## Metadata

- Date: `2026-06-04`
- Node: `G2.338`
- Mode: no-source parallel-surface inventory
- `source_edit_authority`: `false`
- Parent: `G2.337 cache lifecycle provider authorization closeout`
- Authorized work: inventory and classify cache lifecycle-like surfaces only
- Not authorized: Python source edits, test edits, route behavior changes, dashboard lifecycle rewrites, compatibility cleanup, deletion, OpenSpec mutation, or frontend changes

## Source Edit Statement

No source files were edited by this node.

This node writes only this governance worklog and does not authorize implementation.

## Parent Context

G2.337 introduced `CacheLifecycleProvider` as the explicit canonical owner for the main cache manager lifecycle:

- canonical provider module: `web/backend/app/core/cache_lifecycle.py`
- compatibility surface: `web/backend/app/core/cache_manager.py`
- preserved public wrappers:
  - `get_cache_manager()`
  - `get_cache_manager_async(...)`
  - `reset_cache_manager()`

G2.337 explicitly did not consolidate:

- `web/backend/app/core/cache/factory.py`
- `web/backend/app/core/cache/stats_health.py`
- `web/backend/app/api/dashboard.py`

This node inventories those remaining lifecycle-like surfaces.

## Inventory Summary

| Surface | Live lifecycle facts | Text-call evidence | GitNexus evidence | Classification | Disposition |
|---|---|---:|---|---|---|
| `web/backend/app/core/cache/factory.py` | local `_cache_manager`; sync `get_cache_manager(...)`; local `reset_cache_manager()` | `0` imports for `app.core.cache.factory`; `0` exact imports of `from app.core.cache.factory import get_cache_manager` in scanned backend/tests/src/scripts paths | symbol not resolved by current GitNexus index | duplicate lifecycle owner / dormant compatibility candidate | do not edit in this node; candidate for later deprecation or delegation preflight |
| `web/backend/app/core/cache/stats_health.py` | local `_cache_manager`; async `get_cache_manager_async(...)`; Redis initialization side effects; own `CacheManager` class | `0` imports for `app.core.cache.stats_health` in scanned backend/tests/src/scripts paths | symbol not resolved by current GitNexus index | separate legacy/dormant lifecycle implementation, not a thin wrapper | no first-lane consolidation; requires deeper ownership decision before any edit |
| `web/backend/app/api/dashboard.py` | route-local `_cache_manager`; `_cache_manager_initialized`; local async `get_cache_manager()` wraps canonical `app.core.cache_manager.get_cache_manager_async(...)` | dashboard summary route uses local getter; broader grep for dashboard summary showed route/test references | GitNexus found local getter; direct caller is `get_dashboard_summary`; outgoing call is canonical `cache_manager.get_cache_manager_async`; `get_dashboard_summary` participates in 3 indexed processes | route-local memoization wrapper over canonical provider | retain for now; any cleanup needs dashboard-specific authorization and tests |

## Surface Details

### `web/backend/app/core/cache/factory.py`

Live facts:

- module-level `_cache_manager`
- sync `get_cache_manager(tdengine_manager=...)`
- `CacheManager(tdengine_manager)` construction
- warning that Redis support is unavailable and callers should use async cache manager for Redis support
- local `reset_cache_manager()`

Caller facts:

- no direct import usage was found in scanned backend/tests/src/scripts paths

Classification:

- duplicate lifecycle owner / dormant compatibility candidate

Reasoning:

- Its interface overlaps the canonical sync getter responsibility.
- It owns independent lifecycle state, so it is not a thin wrapper.
- Current call evidence suggests it may be unused, but deletion is not authorized because runtime string imports, external scripts, or documentation references were not exhaustively proven absent.

Recommended future gate:

- no-source deprecation/delegation preflight for `cache/factory.py`
- prove import absence more broadly before any deletion
- if retained, convert to a thin wrapper over canonical `app.core.cache_manager.get_cache_manager`

### `web/backend/app/core/cache/stats_health.py`

Live facts:

- module-level `_cache_manager`
- async `get_cache_manager_async(tdengine_manager=..., redis_cache=...)`
- Redis availability initialization and health-check behavior
- own cache manager implementation details and async TDengine methods

Caller facts:

- no direct import usage was found in scanned backend/tests/src/scripts paths

Classification:

- separate legacy/dormant lifecycle implementation, not a thin wrapper

Reasoning:

- It has more implementation depth than a compatibility wrapper.
- Its Redis initialization behavior may not be semantically identical to the new `CacheLifecycleProvider` lane.
- Even if currently unused, it should not be collapsed mechanically into the canonical provider without proving whether it owns a separate stats/health domain responsibility.

Recommended future gate:

- no-source ownership decision for `stats_health.py`
- classify it as one of:
  - obsolete duplicate implementation
  - separate stats-health domain surface
  - compatibility wrapper candidate
- only after that, authorize either retirement, delegation, or separation under a clearer module name

### `web/backend/app/api/dashboard.py`

Live facts:

- route-local `_cache_manager`
- route-local `_cache_manager_initialized`
- local async `get_cache_manager()` imports Redis multi-level cache
- local getter calls canonical `app.core.cache_manager.get_cache_manager_async(redis_cache=redis_cache)`
- `get_dashboard_summary()` awaits the local getter and then uses dashboard cache helpers

GitNexus facts:

- local dashboard `get_cache_manager` found
- incoming caller: dashboard `get_dashboard_summary`
- outgoing call: canonical `web/backend/app/core/cache_manager.py:get_cache_manager_async`
- `get_dashboard_summary` participates in 3 indexed processes:
  - `Get_dashboard_summary -> Get_cache_key`
  - `Get_dashboard_summary -> _is_cache_expired`
  - `Get_dashboard_summary -> _evict_memory_cache`

Classification:

- route-local memoization wrapper over canonical provider

Reasoning:

- Unlike `cache/factory.py` and `stats_health.py`, dashboard does not construct its own `CacheManager`; it wraps the canonical async getter.
- Its local state caches the dashboard route's resolved async manager and Redis initialization path.
- It is lifecycle-like, but it is not currently a duplicate lifecycle owner for `CacheManager`.

Recommended future gate:

- keep dashboard local wrapper unchanged unless a dashboard-specific source node is authorized
- if cleanup is desired, first prove whether `_cache_manager_initialized` still adds value after G2.337 provider memoization
- required tests for any future dashboard edit:
  - `pytest tests/api/file_tests/test_dashboard_api.py -q -n 0 --tb=short --no-cov`
  - dashboard async cache operation tests
  - cache route file tests if canonical cache manager import behavior changes

## Boundary Decision

Only one canonical lifecycle owner is recognized after G2.337:

- `web/backend/app/core/cache_lifecycle.py::CacheLifecycleProvider`

Current compatibility surface:

- `web/backend/app/core/cache_manager.py`

Parallel or lifecycle-like surfaces:

- `cache/factory.py`: duplicate/dormant sync lifecycle owner candidate
- `stats_health.py`: separate legacy/dormant lifecycle implementation candidate
- `dashboard.py`: route-local memoization wrapper over canonical async provider

Do not consolidate these three surfaces in one implementation batch.

## Risk Notes

- `cache/factory.py` and `stats_health.py` have no direct imports in the scanned backend/tests/src/scripts paths, but absence from text search is not enough for deletion under `architecture/STANDARDS.md`.
- `stats_health.py` may contain domain behavior beyond lifecycle ownership and therefore needs ownership classification before any rewrite.
- `dashboard.py` participates in indexed dashboard summary processes; changes there are route behavior changes and require separate source authority.
- GitNexus index is stale and did not resolve the `cache/factory.py` / `stats_health.py` getter symbols; live source and text-call evidence are used for this no-source inventory.

## Recommended Next Gate

Recommended next node:

`G2.339 cache factory dormant lifecycle preflight / no-source`

Required properties:

- `source_edit_authority=false`
- focus only on `web/backend/app/core/cache/factory.py`
- prove whether the module has live callers beyond the scanned backend/tests/src/scripts paths
- decide whether it should become a thin compatibility wrapper over canonical `cache_manager.py`
- no deletion unless code-path and function-tree status both support removal

Alternate next node:

`G2.339 cache stats-health ownership decision / no-source`

Use the alternate if maintainers prefer to resolve the deeper `stats_health.py` implementation before the smaller dormant factory surface.

## Verification Performed

Evidence gathered:

- reviewed G2.337 closeout and next-gate constraints
- reviewed `architecture/STANDARDS.md` migration closure and single-truth-source rules
- collected live source facts for:
  - `web/backend/app/core/cache/factory.py`
  - `web/backend/app/core/cache/stats_health.py`
  - `web/backend/app/api/dashboard.py`
  - `web/backend/app/core/cache_manager.py`
  - `web/backend/app/core/cache_lifecycle.py`
- ran text-call scans for direct imports/usages of cache factory, stats-health, dashboard, and lifecycle provider surfaces
- ran GitNexus context for dashboard local `get_cache_manager` and `get_dashboard_summary`
- attempted GitNexus context for `stats_health.py:get_cache_manager_async` and `cache/factory.py:get_cache_manager`; current index did not resolve those symbols

No tests were run because this node made no source or test changes.

## Scope Control

No changes were made to:

- `web/backend/app/core/cache/factory.py`
- `web/backend/app/core/cache/stats_health.py`
- `web/backend/app/api/dashboard.py`
- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache_lifecycle.py`
- any test file
- any OpenSpec file
- any frontend file

## Closeout

G2.338 is complete as a no-source inventory node.

It confirms that the new canonical cache lifecycle owner should remain `CacheLifecycleProvider`, while `cache/factory.py`, `stats_health.py`, and dashboard-local cache state each require separate handling decisions before any consolidation.
