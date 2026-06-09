# G2.343 Dashboard-Local Cache Lifecycle Surface Inventory

## Metadata

- Date: `2026-06-04`
- Node: `G2.343`
- Mode: no-source dashboard-local lifecycle inventory
- `source_edit_authority`: `false`
- Parent: `G2.342 stats-health module-level getter repair closeout`
- Target: `web/backend/app/api/dashboard.py`
- Authorized work: dashboard-local cache lifecycle fact audit, usage classification, GitNexus impact review, and next-gate recommendation only
- Not authorized: source edits, test edits, route changes, cache lifecycle rewrites, deletion, frontend changes, OpenSpec mutation, or compatibility cleanup

## Source Edit Statement

No source or test files are edited by this node.

This report is a no-source governance artifact. It does not authorize implementation.

## Parent Context

G2.338 classified three cache lifecycle-like surfaces after G2.337 established `CacheLifecycleProvider` as the canonical cache lifecycle owner:

- `web/backend/app/core/cache/factory.py`: duplicate/dormant sync lifecycle owner candidate
- `web/backend/app/core/cache/stats_health.py`: separate legacy/dormant async lifecycle implementation candidate
- `web/backend/app/api/dashboard.py`: route-local memoization wrapper over canonical async provider

G2.339 and G2.340 handled the cache factory surface.

G2.341 and G2.342 handled the stats-health module-level getter tail.

This node handles only the remaining dashboard-local cache lifecycle surface.

## Live Source Facts

`web/backend/app/api/dashboard.py` imports the canonical cache manager API:

- `from app.core.cache_manager import CacheManager, get_cache_manager_async`

It keeps route-local module state:

- `_cache_manager: Optional[CacheManager] = None`
- `_cache_manager_initialized: Optional[bool] = None`

It defines local wrapper:

- `async def get_cache_manager() -> CacheManager`

The local wrapper:

- uses the module globals `_cache_manager` and `_cache_manager_initialized`
- attempts optional Redis cache discovery through `src.core.cache.multi_level.get_cache`
- calls canonical `get_cache_manager_async(redis_cache=redis_cache)`
- memoizes the returned manager in `_cache_manager`
- marks `_cache_manager_initialized = True`

The dashboard summary route uses this wrapper:

- route: `GET /api/dashboard/summary`
- handler: `get_dashboard_summary(...)`
- call: `cache_manager = await get_cache_manager()`

The handler then uses the returned manager for:

- `try_get_cached_dashboard(...)`
- `cache_dashboard_data(...)`

Related helper facts:

- `web/backend/app/api/dashboard_cache.py` accepts `CacheManager` and performs `fetch_from_cache(...)` / `write_to_cache(...)`
- `web/backend/app/api/dashboard_data_source.py` has its own market-data snapshot caches (`_TDX_MARKET_SNAPSHOT_CACHE`, `_MAJOR_INDEX_QUOTES_CACHE`) that are domain-data caches, not cache-manager lifecycle owners

## GitNexus Evidence

`context(name="get_cache_manager", file_path="web/backend/app/api/dashboard.py")`:

- symbol found: `Function:web/backend/app/api/dashboard.py:get_cache_manager`
- direct incoming caller: `get_dashboard_summary`
- outgoing call: `web/backend/app/core/cache_manager.py:get_cache_manager_async`
- processes listed directly on local getter: none

`impact(target="get_cache_manager", file_path="web/backend/app/api/dashboard.py", direction="upstream")`:

- risk: `LOW`
- impacted count: `1`
- direct callers: `1`
- processes affected: `1`
- affected module: `Api`
- affected process target: `get_dashboard_summary`
- affected process count reported for `get_dashboard_summary`: `3`

`context(name="get_dashboard_summary", file_path="web/backend/app/api/dashboard.py")`:

- symbol found: `Function:web/backend/app/api/dashboard.py:get_dashboard_summary`
- outgoing call includes local `get_cache_manager`
- outgoing calls also include dashboard builders, dashboard cache helpers, and dashboard data source
- indexed processes:
  - `Get_dashboard_summary -> Get_cache_key`
  - `Get_dashboard_summary -> _is_cache_expired`
  - `Get_dashboard_summary -> _evict_memory_cache`

`impact(target="get_dashboard_summary", file_path="web/backend/app/api/dashboard.py", direction="upstream")`:

- risk: `LOW`
- direct upstream count: `0`
- process/module affected count in upstream walk: `0`

GitNexus caveat:

- Index status still reports stale warning because the current commit differs from the indexed commit in this dirty worktree.
- The relevant dashboard symbols resolved and returned process evidence after the long `npx gitnexus analyze` refresh in G2.342.

## Classification

Classification:

`web/backend/app/api/dashboard.py` has an active route-local memoization wrapper over the canonical async cache lifecycle provider.

It is not currently classified as:

- obsolete dead code
- a deletion candidate
- an independent canonical lifecycle owner
- a broken compatibility wrapper

The dashboard-local globals are route-local memoization state around the canonical `cache_manager.get_cache_manager_async(...)` path. Because `get_dashboard_summary(...)` directly depends on the wrapper and participates in three indexed dashboard cache processes, this surface should not be removed or rewritten without an explicit source authorization node and dashboard-specific tests.

## Decision

Retain the dashboard-local wrapper for now.

Do not consolidate it in the same lane as cache factory or stats-health repairs.

Any future source edit must be a dashboard-specific authorization that decides one of:

- keep current route-local memoization and only add tests/documentation
- replace route-local memoization with direct canonical provider usage
- move dashboard cache lifecycle acquisition into a FastAPI dependency
- remove `_cache_manager_initialized` only if tests prove canonical provider memoization preserves behavior

## Required Tests For Future Source Work

Any future dashboard-local source change should include, at minimum:

```bash
pytest tests/api/file_tests/test_dashboard_api.py -q -n 0 --tb=short --no-cov
```

Focused behavioral coverage should prove:

- `GET /api/dashboard/summary` still uses cache read/write helpers when `bypass_cache=false`
- `bypass_cache=true` still skips cache reads
- route-local cache acquisition still passes optional Redis cache into canonical async lifecycle acquisition, or deliberately stops doing so with an approved design
- dashboard helper cache-key behavior remains unchanged

## Verification Performed

Evidence collected for this no-source node:

- reviewed G2.338 parallel-surface inventory
- reviewed G2.342 closeout and remaining surface recommendation
- scanned live `web/backend/app/api/dashboard.py` cache wrapper and route handler facts
- scanned dashboard cache helper modules
- scanned dashboard file tests and dashboard route entries
- ran GitNexus context/impact on dashboard-local `get_cache_manager`
- ran GitNexus context/impact on `get_dashboard_summary`

No tests were run for G2.343 because this node made no source or test changes.

## Scope Control

No changes were made to:

- `web/backend/app/api/dashboard.py`
- `web/backend/app/api/dashboard_cache.py`
- `web/backend/app/api/dashboard_data_source.py`
- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache_lifecycle.py`
- any test file
- any frontend file
- any OpenSpec file

## Recommended Next Gate

Recommended next node:

`G2.344 dashboard-local cache wrapper authorization`

Required properties:

- `source_edit_authority=true`
- target only `web/backend/app/api/dashboard.py` and dashboard-specific tests
- choose one explicit design outcome before editing:
  - retain wrapper with test coverage only
  - direct canonical provider call
  - FastAPI dependency handoff
  - `_cache_manager_initialized` simplification
- must run GitNexus impact before edits on `get_cache_manager` and `get_dashboard_summary`
- must include `tests/api/file_tests/test_dashboard_api.py` verification

Alternative:

If maintainers prefer no source change, mark dashboard-local wrapper as retained compatibility / route-local optimization and return to the broader G2 service-lifecycle residual queue.

## Closeout

G2.343 is complete as a no-source inventory node. It classifies `web/backend/app/api/dashboard.py` as an active route-local memoization wrapper over the canonical async cache lifecycle provider. The wrapper has one direct caller (`get_dashboard_summary`) and is connected to three indexed dashboard cache processes, so future changes require explicit dashboard-specific source authorization rather than opportunistic cleanup.
