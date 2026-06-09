# G2.349 Core Cache Helper Modules Outside Batch1 Inventory

## Metadata

- Date: `2026-06-04`
- Node: `G2.349`
- Mode: core cache helper modules outside Batch1 inventory / no-source
- `source_edit_authority`: `false`
- Branch: `wip/root-dirty-20260403`
- Evidence head: `cc7bd76fe`
- Parent: `G2.348 Cache API Route Cluster Inventory`
- Authorized work: batch inventory remaining core cache helper modules outside already-closed Batch1 lifecycle surfaces
- Not authorized: source edits, test edits, deletion, consolidation, route behavior changes, cache lifecycle rewrites, compatibility export changes, frontend changes, OpenSpec mutation, or splitting helper files into one-file confirmation nodes

## Source Edit Statement

No source files were edited by G2.349.

This node writes only this report:

- `docs/reports/worklogs/claude-auto/g2-349-core-cache-helper-modules-outside-batch1-inventory-2026-06-04.md`

## Parent Gate

G2.348 directed the remaining cache modernization queue to:

`G2.349 core cache helper modules outside Batch1 inventory / no-source`

Required properties:

- `source_edit_authority=false`
- inventory core cache helper modules outside the already-closed Batch1 lifecycle surfaces
- decide whether each surface is canonical web-backend cache infrastructure, compatibility helper, or separate subsystem helper
- do not merge the cache API route cluster into core helper ownership
- do not perform source edits during inventory

## Inventory Scope

Primary P3 scope from the remaining cache modernization inventory:

- `web/backend/app/core/cache/__init__.py`
- `web/backend/app/core/cache/core.py`
- `web/backend/app/core/cache/batch_ops.py`
- `web/backend/app/core/cache/decorators.py`
- `web/backend/app/core/cache/fetch_write.py`
- `web/backend/app/core/cache/multi_level.py`

Additional Batch1-outside adjacent core cache helpers found in the tracked-file scan:

- `web/backend/app/core/cache_eviction.py`
- `web/backend/app/core/cache_integration.py`
- `web/backend/app/core/cache_prewarming.py`
- `web/backend/app/core/cache_utils.py`

Closed Batch1 boundary, not reopened by G2.349:

- `web/backend/app/core/cache_lifecycle.py`
- `web/backend/app/core/cache_manager.py`
- `web/backend/app/core/cache/factory.py`
- `web/backend/app/core/cache/stats_health.py`

Deferred to P4 `src/` cache subsystem inventory:

- `src/core/cache/__init__.py`
- `src/core/cache/decorators.py`
- `src/core/cache/multi_level.py`

## Local Evidence Summary

Measured primary P3 helper surfaces:

| Surface | Status | Lines | Top-level role evidence |
|---|---:|---:|---|
| `web/backend/app/core/cache/__init__.py` | clean | 14 | package export facade; defines `CacheManager` from `CacheCoreInit`, `CacheFetchWriteMixin`, `CacheBatchMixin`, and closed Batch1 `CacheStatsHealthMixin`; `__all__ = ["CacheManager"]` |
| `web/backend/app/core/cache/core.py` | clean | 233 | `CacheCoreInit` mixin/helper; imports `MultiLevelCache`; has global-like, async, TTL, and multilevel markers |
| `web/backend/app/core/cache/batch_ops.py` | clean | 217 | `CacheBatchMixin`; batch operation helper with TTL/multilevel/error-handling markers |
| `web/backend/app/core/cache/decorators.py` | clean | 218 | decorator/runtime helper; exposes `cached`, `cached_sync`, `CacheInvalidator`, invalidation helpers, and middleware helper |
| `web/backend/app/core/cache/fetch_write.py` | clean | 262 | `CacheFetchWriteMixin`; fetch/write operation helper with async, freshness, multilevel, and cleanup markers |
| `web/backend/app/core/cache/multi_level.py` | clean | 429 | standalone multilevel cache subsystem helper; exposes `MemoryCache`, `CircuitBreaker`, `MultiLevelCache`, `get_cache`, `init_cache`, `close_cache`, and `generate_cache_key` |

Measured adjacent Batch1-outside root helpers:

| Surface | Status | Lines | Top-level role evidence |
|---|---:|---:|---|
| `web/backend/app/core/cache_eviction.py` | clean | 393 | eviction subsystem helper; exposes `AccessFrequencyTracker`, `TimeWindowEvictionStrategy`, `EvictionScheduler`, and singleton getters/resets |
| `web/backend/app/core/cache_integration.py` | clean | 600 | service-cache integration helper; exposes `CacheIntegration`, integration singleton/reset, and read/write/invalidate decorators |
| `web/backend/app/core/cache_prewarming.py` | clean | 334 | prewarming/monitoring subsystem helper; exposes `CacheMonitor`, `CachePrewarmingStrategy`, and singleton getters/resets |
| `web/backend/app/core/cache_utils.py` | clean | 212 | API/market-facing cache utility helper; exposes `cache_response`, `clear_api_cache`, and `get_cache_stats` |

Reference scan highlights:

- No tracked local import of `from app.core.cache import CacheManager` or `app.core.cache.CacheManager` was found.
- `app.core.cache.multi_level` is imported by `web/backend/app/core/cache/core.py`.
- `app.core.cache_eviction` is imported by the cache eviction API helper, cache prewarming helper, and eviction/prewarming tests.
- `app.core.cache_integration` is imported by data services, market-data service part1, cache API tests, and cache integration tests.
- `app.core.cache_prewarming` is imported by the cache prewarming API helper and prewarming tests.
- `app.core.cache_utils.cache_response` is imported by market API route files.
- The scan skipped 3 tracked Python paths missing from the local worktree. No decision in this report depends solely on those missing paths.

Mirror/drift observations:

- `web/backend/app/core/cache/decorators.py` and `src/core/cache/decorators.py` are near mirrors but not byte-identical: 4 differing lines were measured.
- `web/backend/app/core/cache/multi_level.py` and `src/core/cache/multi_level.py` are near mirrors but not byte-identical: 16 differing lines were measured.
- This is enough to keep `src/core/cache` as a separate P4 subsystem inventory. G2.349 must not collapse `web/backend` and `src` cache subsystems.

GitNexus status:

- `CacheCoreInit` in `web/backend/app/core/cache/core.py` was not found by GitNexus.
- `MultiLevelCache` in `web/backend/app/core/cache/multi_level.py` was not found by GitNexus.
- `CacheIntegration` in `web/backend/app/core/cache_integration.py` resolved, with incoming imports from data services, market-data service part1, cache API tests, and cache integration tests; index status was still `stale: true`.
- `cache_response` in `web/backend/app/core/cache_utils.py` resolved, with incoming calls from market route files; index status was still `stale: true`.
- G2.349 therefore does not derive any source authorization from GitNexus. Any later source node must first restore a fresh index and rerun targeted context/impact.

## Decision Table

| Surface | Current role | Classification | Decision | Source authorization |
|---|---|---|---|---|
| `web/backend/app/core/cache/__init__.py` | Package export facade that constructs a `CacheManager` class from mixins, including the Batch1-closed stats/health mixin. | Compatibility/export facade; not the canonical lifecycle owner. | Keep. Do not add or remove exports from inventory alone. Treat it as a compatibility-sensitive package boundary. | Not authorized. |
| `web/backend/app/core/cache/core.py` | Core init mixin/helper coupled to `MultiLevelCache` and manager-style initialization state. | Web-backend cache package mixin helper; not standalone canonical manager. | Keep as part of the package helper group. Any future change must compare behavior against the Batch1-closed `cache_manager.py` lifecycle boundary. | Not authorized. |
| `web/backend/app/core/cache/batch_ops.py` | Batch operation mixin helper. | Web-backend package operation helper. | Keep. Do not edit as a standalone file; it belongs with the package facade/mixin group. | Not authorized. |
| `web/backend/app/core/cache/decorators.py` | Decorator and invalidation helper using the web-backend multilevel cache import path. | Runtime decorator helper and web-backend mirror variant of `src/core/cache/decorators.py`. | Keep. Do not consolidate with `src/core/cache/decorators.py` in this node because the mirror has measured drift and belongs to P4 reconciliation. | Not authorized. |
| `web/backend/app/core/cache/fetch_write.py` | Fetch/write mixin helper with async, freshness, and cleanup behavior markers. | Web-backend package data access/cache write helper. | Keep as part of the package helper group. Do not treat it as lifecycle owner independent of the facade and Batch1 manager boundary. | Not authorized. |
| `web/backend/app/core/cache/multi_level.py` | Multilevel cache implementation/helper with memory/cache/Redis/circuit-breaker style responsibilities and module-level getters. | Separate high-risk web-backend cache subsystem helper. | Keep. Do not fold into `cache_manager.py`, API route helpers, or `src/core/cache/multi_level.py` from inventory alone. | Not authorized; requires separate high-risk source preflight if later touched. |
| `web/backend/app/core/cache_eviction.py` | Eviction subsystem helper used by cache eviction API, prewarming, and tests. | Canonical web-backend eviction subsystem helper adjacent to, but outside, Batch1 lifecycle closure. | Keep. It is active infrastructure, not cleanup residue. Future changes must include eviction route and eviction tests. | Not authorized. |
| `web/backend/app/core/cache_integration.py` | Service-cache integration helper used by data services, market-data service part1, and tests. | Canonical service integration helper; broad service-facing cache integration surface. | Keep. Do not merge into route cluster or Batch1 manager lifecycle without a dedicated service-integration preflight. | Not authorized. |
| `web/backend/app/core/cache_prewarming.py` | Prewarming and monitoring helper used by cache prewarming API and tests. | Canonical web-backend prewarming subsystem helper. | Keep. It belongs with prewarming API/test verification if edited later. | Not authorized. |
| `web/backend/app/core/cache_utils.py` | API/market-facing cache utility decorator/helper used by market route files. | API utility/compatibility helper; not canonical cache lifecycle owner. | Keep. Do not delete or consolidate because market route imports are active. Future source work must include market route behavior checks. | Not authorized. |
| `web/backend/app/core/cache_lifecycle.py` | Batch1-closed lifecycle provider. | Closed Batch1 canonical lifecycle boundary. | Do not reopen in G2.349. | Not authorized. |
| `web/backend/app/core/cache_manager.py` | Batch1-closed canonical cache manager surface. | Closed Batch1 canonical manager/lifecycle surface. | Do not reopen in G2.349. Use as comparison boundary only. | Not authorized. |
| `web/backend/app/core/cache/factory.py` | Batch1-closed package factory bridge. | Closed Batch1 compatibility/factory boundary. | Do not reopen in G2.349. | Not authorized. |
| `web/backend/app/core/cache/stats_health.py` | Batch1-closed stats/health mixin surface. | Closed Batch1 stats/health helper boundary. | Do not reopen in G2.349, even though `cache/__init__.py` imports it. | Not authorized. |
| `src/core/cache/*` | Separate `src` cache subsystem with near-mirror files and measured drift from web-backend cache helpers. | Deferred P4 subsystem. | Do not reconcile in G2.349. | Not authorized. |

## Cluster Decision

G2.349 keeps the Batch1-outside cache helper surface grouped into three bands:

1. Web-backend package helper/facade band:
   - `web/backend/app/core/cache/__init__.py`
   - `web/backend/app/core/cache/core.py`
   - `web/backend/app/core/cache/batch_ops.py`
   - `web/backend/app/core/cache/decorators.py`
   - `web/backend/app/core/cache/fetch_write.py`
   - `web/backend/app/core/cache/multi_level.py`

2. Web-backend adjacent subsystem/helper band:
   - `web/backend/app/core/cache_eviction.py`
   - `web/backend/app/core/cache_integration.py`
   - `web/backend/app/core/cache_prewarming.py`
   - `web/backend/app/core/cache_utils.py`

3. Deferred `src` subsystem band:
   - `src/core/cache/__init__.py`
   - `src/core/cache/decorators.py`
   - `src/core/cache/multi_level.py`

No deletion, consolidation, compatibility export change, source rewrite, or test edit is authorized by G2.349.

## Source Authorization Finding

G2.349 does not open a source node.

Reasons:

1. The primary P3 files are helper/facade/mixin/multilevel surfaces, not an isolated defect or behavior-change target.
2. Several adjacent root helpers are active service/API/test infrastructure, not cleanup residue.
3. `src/core/cache` mirror drift is measurable and requires a later P4 reconciliation, not a P3 shortcut.
4. GitNexus evidence is partial and stale, so it cannot satisfy any future source-edit impact gate.
5. `architecture/STANDARDS.md` forbids deletion or consolidation based only on static unused/unreferenced signals.

## Recommended Next Gate

Continue the remaining cache modernization queue with:

`G2.350 src cache subsystem reconciliation inventory / no-source`

Required properties:

- `source_edit_authority=false`
- inventory `src/core/cache/*` as the P4 subsystem after P1-P3 are bounded
- compare `src/core/cache/decorators.py` and `src/core/cache/multi_level.py` against their web-backend near mirrors as evidence, not as immediate merge authorization
- decide whether `src/core/cache` is canonical infrastructure, compatibility mirror, GPU/support subsystem, or separate library surface
- do not perform source edits during inventory
