# G2.350 Src Cache Subsystem Reconciliation Inventory

## Metadata

- Date: `2026-06-04`
- Node: `G2.350`
- Mode: src cache subsystem reconciliation inventory / no-source
- `source_edit_authority`: `false`
- Branch: `wip/root-dirty-20260403`
- Evidence head: `cc7bd76fe`
- Parent: `G2.349 Core Cache Helper Modules Outside Batch1 Inventory`
- Authorized work: batch inventory P4 `src/` cache subsystem surfaces and classify ownership/domain boundaries
- Not authorized: source edits, test edits, deletion, consolidation, web-backend lifecycle rewrites, mirror reconciliation, GPU cache changes, infrastructure Redis lock changes, mock data rewrites, frontend changes, OpenSpec mutation, or splitting P4 into single-file confirmation nodes

## Source Edit Statement

No source files were edited by G2.350.

This node writes only this report:

- `docs/reports/worklogs/claude-auto/g2-350-src-cache-subsystem-reconciliation-inventory-2026-06-04.md`

## Parent Gate

G2.349 directed the remaining cache modernization queue to:

`G2.350 src cache subsystem reconciliation inventory / no-source`

Required properties:

- `source_edit_authority=false`
- inventory `src/core/cache/*` as the P4 subsystem after P1-P3 are bounded
- compare `src/core/cache/decorators.py` and `src/core/cache/multi_level.py` against their web-backend near mirrors as evidence, not as immediate merge authorization
- decide whether `src/core/cache` is canonical infrastructure, compatibility mirror, GPU/support subsystem, or separate library surface
- do not perform source edits during inventory

The upstream P4 queue also lists adjacent `src/` cache surfaces outside `src/core/cache/*`. G2.350 records them together so P4 remains one batch inventory, not a sequence of single-file confirmation nodes.

## Inventory Scope

P4 `src/` cache surfaces:

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

Comparison-only web-backend near mirrors:

- `web/backend/app/core/cache/decorators.py`
- `web/backend/app/core/cache/multi_level.py`

## Local Evidence Summary

Measured P4 surface summary:

| Surface | Status | Lines | Top-level role evidence |
|---|---:|---:|---|
| `src/application/market_data/price_stream_processor_cached.py` | clean | 259 | `CachedPriceStreamProcessor`; application market-data cache wrapper/processor with async/cache/TTL markers |
| `src/core/cache/__init__.py` | clean | 40 | package export surface for `MultiLevelCache`, `MemoryCache`, `CacheConfig`, decorators, and invalidation helpers |
| `src/core/cache/decorators.py` | clean | 218 | core cache decorator/invalidation helper; near mirror of web-backend decorator helper with measured drift |
| `src/core/cache/multi_level.py` | clean | 429 | core multilevel cache library surface with `MemoryCache`, `CircuitBreaker`, `MultiLevelCache`, module getters/init/close, and `generate_cache_key` |
| `src/core/data_source/cache.py` | clean | 32 | small `LRUCache` data-source helper |
| `src/core/data_source/smart_cache.py` | clean | 314 | `SmartCache` data-source cache helper with refresh, invalidate, cleanup, stats, and shutdown behavior |
| `src/gpu/api_system/utils/_cache_manager_reporting.py` | clean | 54 | GPU cache reporting mixin |
| `src/gpu/api_system/utils/cache_optimization.py` | clean | 669 | GPU/API cache optimization stack with cache metrics, L1/L2/Redis cache layers, multilevel cache, and cache manager |
| `src/gpu/api_system/utils/cache_optimization_enhanced.py` | clean | 689 | enhanced GPU cache manager and adaptive/predictive helpers |
| `src/infrastructure/cache/__init__.py` | clean | 5 | infrastructure cache package marker |
| `src/infrastructure/cache/redis_lock.py` | clean | 101 | Redis distributed lock infrastructure helper |
| `src/mock/mock_Dashboard.py` | clean | 624 | dashboard mock data provider; cache-named only by P4 inventory context, not a cache implementation |

Measured module reference highlights:

- `src.core.cache.multi_level` is imported by async cache integration scripts, legacy scripts, `tests/unit/test_cache.py`, dashboard file tests, and `web/backend/app/api/dashboard.py`.
- `src.core.data_source.cache.LRUCache` is exported through `src/core/data_source/__init__.py` and referenced by performance cache benchmark tests.
- `src.core.data_source.smart_cache.SmartCache` is imported by efinance adapter core and several smart-cache/data-source tests.
- `src.infrastructure.cache.redis_lock.RedisDistributedLock` is imported by application bootstrap, the non-cached price stream processor, and runtime-config governance tests.
- GPU cache optimization modules are imported by integrated GPU API services, GPU cache tests, and GPU verification scripts.
- `src/mock/mock_Dashboard.py` is imported by mock-data scripts/tests and web-backend mock data support.

Measured core-cache test surface:

- `tests/unit/test_cache.py` imports from `src.core.cache.multi_level`.
- It covers `MemoryCache`, `CacheConfig`, `generate_cache_key`, and `MultiLevelCache` behavior.
- Dedicated runtime-config tests exist for both `src/core/cache/multi_level.py` and `web/backend/app/core/cache/multi_level.py`, which is evidence that the two surfaces are tracked separately.

Mirror/drift observations:

| `src` surface | Web-backend near mirror | Measured drift |
|---|---|---:|
| `src/core/cache/decorators.py` | `web/backend/app/core/cache/decorators.py` | 4 differing lines, same line count |
| `src/core/cache/multi_level.py` | `web/backend/app/core/cache/multi_level.py` | 16 differing lines, same line count |

The drift is small but real. It is evidence for a later reconciliation discussion, not source authorization to merge, delete, or normalize either side.

## GitNexus Status

GitNexus evidence is partial and stale:

- `MultiLevelCache` in `src/core/cache/multi_level.py` was not found.
- `cached` in `src/core/cache/decorators.py` was not found.
- `RedisDistributedLock` in `src/infrastructure/cache/redis_lock.py` was not found.
- `SmartCache` in `src/core/data_source/smart_cache.py` resolved and showed imports from data-source base, efinance adapter core, smart-cache tests, data-source metrics tests, and performance benchmarks.
- `EnhancedCacheManager` in `src/gpu/api_system/utils/cache_optimization_enhanced.py` resolved and showed imports from GPU docs/tests/scripts.
- `CachedPriceStreamProcessor` in `src/application/market_data/price_stream_processor_cached.py` resolved and showed a runtime demo import.
- All successful GitNexus results still reported `stale: true`.

G2.350 does not derive any source authorization from GitNexus. Any later source node must first restore a fresh index and rerun context/impact for the specific domain cluster.

## Decision Table

| Surface | Current role | Classification | Decision | Source authorization |
|---|---|---|---|---|
| `src/application/market_data/price_stream_processor_cached.py` | Cached application market-data processor/wrapper. | Application market-data cache surface. | Keep separate from web-backend cache lifecycle and `src/core/cache`. It is application workflow cache behavior, not canonical cache infrastructure. | Not authorized. |
| `src/core/cache/__init__.py` | Package export surface for core cache library helpers. | `src` core cache package facade. | Keep. Do not add/remove exports or align with web-backend package exports without a dedicated source preflight. | Not authorized. |
| `src/core/cache/decorators.py` | Core decorator/invalidation helper imported through `src.core.cache.multi_level`. | `src` core cache library helper; near mirror of web-backend decorator helper. | Keep as separate `src` core helper. Measured mirror drift prevents treating it as a byte-identical compatibility copy. | Not authorized. |
| `src/core/cache/multi_level.py` | Core multilevel cache implementation with memory cache, circuit breaker, module lifecycle helpers, and key generator. | `src` core cache library surface. | Keep as a separate library-like cache surface. Do not fold into web-backend `multi_level.py` or Batch1 cache manager from inventory alone. | Not authorized. |
| `src/core/data_source/cache.py` | Small data-source `LRUCache` helper. | Data-source cache helper. | Keep in the data-source domain. It is not part of web-backend lifecycle or `src/core/cache` mirror reconciliation. | Not authorized. |
| `src/core/data_source/smart_cache.py` | Data-source smart cache helper used by adapters and data-source tests. | Data-source cache subsystem. | Keep as active data-source infrastructure. Any future change must include adapter/data-source tests and performance benchmark implications. | Not authorized. |
| `src/gpu/api_system/utils/_cache_manager_reporting.py` | GPU cache reporting mixin. | GPU support cache helper. | Keep within GPU API system ownership. Do not reconcile with web-backend cache manager by name alone. | Not authorized. |
| `src/gpu/api_system/utils/cache_optimization.py` | GPU/API cache optimization stack with L1/L2/Redis/multilevel/cache manager concepts. | GPU support cache subsystem. | Keep as GPU-specific cache infrastructure. It is not a duplicate of web-backend `CacheManager` despite overlapping class names. | Not authorized. |
| `src/gpu/api_system/utils/cache_optimization_enhanced.py` | Enhanced GPU cache manager with adaptive/predictive helpers. | GPU support cache subsystem. | Keep as GPU-specific cache optimization surface. | Not authorized. |
| `src/infrastructure/cache/__init__.py` | Infrastructure cache package marker. | Infrastructure package boundary. | Keep with Redis lock infrastructure. No standalone cleanup action. | Not authorized. |
| `src/infrastructure/cache/redis_lock.py` | Redis distributed lock infrastructure helper. | Infrastructure Redis lock surface. | Keep separate from cache storage/lifecycle concerns. This is locking infrastructure, not cache data lifecycle. | Not authorized. |
| `src/mock/mock_Dashboard.py` | Mock dashboard data provider used by mock scripts/tests and web-backend mock support. | Mock dashboard data surface, not cache infrastructure. | Keep out of cache modernization source work. Its P4 inclusion is name/context adjacency, not ownership evidence. | Not authorized. |
| `web/backend/app/core/cache/decorators.py` | Web-backend decorator helper near mirror. | Comparison-only P3 web-backend helper. | Do not edit in G2.350. Use only as drift evidence. | Not authorized. |
| `web/backend/app/core/cache/multi_level.py` | Web-backend multilevel cache helper near mirror. | Comparison-only P3 web-backend helper. | Do not edit in G2.350. Use only as drift evidence. | Not authorized. |

## Cluster Decision

G2.350 classifies the P4 `src` cache subsystem into six domain clusters:

1. Application market-data cache:
   - `src/application/market_data/price_stream_processor_cached.py`

2. `src` core cache library:
   - `src/core/cache/__init__.py`
   - `src/core/cache/decorators.py`
   - `src/core/cache/multi_level.py`

3. Data-source cache:
   - `src/core/data_source/cache.py`
   - `src/core/data_source/smart_cache.py`

4. GPU cache optimization/support:
   - `src/gpu/api_system/utils/_cache_manager_reporting.py`
   - `src/gpu/api_system/utils/cache_optimization.py`
   - `src/gpu/api_system/utils/cache_optimization_enhanced.py`

5. Infrastructure Redis lock:
   - `src/infrastructure/cache/__init__.py`
   - `src/infrastructure/cache/redis_lock.py`

6. Mock dashboard data:
   - `src/mock/mock_Dashboard.py`

These clusters are not one interchangeable cache implementation. They must not be collapsed into web-backend cache lifecycle ownership by filename similarity.

## Source Authorization Finding

G2.350 does not open a source node.

Reasons:

1. The P4 list is multi-domain: application workflow, core library, data-source, GPU, infrastructure lock, and mock-data surfaces.
2. `src/core/cache` and web-backend cache helper files have measured near-mirror drift, so reconciliation requires a dedicated design/source preflight, not inventory-time edits.
3. GPU cache surfaces have independent service/test imports and must remain under GPU ownership until explicitly authorized.
4. Data-source cache helpers are active adapter/data-source infrastructure.
5. Redis lock is infrastructure synchronization, not cache lifecycle.
6. GitNexus evidence is partial and stale.
7. `architecture/STANDARDS.md` forbids deletion or consolidation based only on static naming, unused-looking surfaces, or near-duplicate files.

## Recommended Next Gate

Continue the remaining cache modernization queue with:

`G2.351 cache/dashboard test and E2E coverage inventory / no-source`

Required properties:

- `source_edit_authority=false`
- inventory cache/dashboard tests as coverage surfaces after P1-P4 are bounded
- separate route tests, core cache tests, data-source cache tests, GPU cache tests, and mock/dashboard tests
- do not use test existence as deletion evidence
- do not perform source or test edits during inventory
