# G2.348 Cache API Route Cluster Inventory

## Metadata

- Date: `2026-06-04`
- Node: `G2.348`
- Mode: cache API route cluster inventory / no-source
- `source_edit_authority`: `false`
- Branch: `wip/root-dirty-20260403`
- Evidence head: `2408edaf7`
- Parent: `G2.347 Dashboard Cache Helper Source Authorization Preflight`
- Authorized work: inventory cache API route entry, split route helpers, and adjacent indicator-cache surface in one decision table
- Not authorized: source edits, test edits, deletion, consolidation, route behavior changes, response-contract changes, frontend changes, OpenSpec mutation, or GitNexus index repair

## Source Edit Statement

No source files were edited by G2.348.

This node writes only this report:

- `docs/reports/worklogs/claude-auto/g2-348-cache-api-route-cluster-inventory-2026-06-04.md`

## Parent Gate

G2.347 directed the remaining cache modernization queue to:

`G2.348 cache API route cluster inventory / no-source`

Required properties:

- `source_edit_authority=false`
- inventory `web/backend/app/api/cache.py` and split cache route helpers together
- keep route/helper ownership and response-contract behavior in one decision table
- do not treat the dashboard cache helper cluster as merged into the cache API route cluster
- do not perform source edits during inventory

## Inventory Scope

In scope:

- `web/backend/app/api/cache.py`
- `web/backend/app/api/_cache_basic_routes.py`
- `web/backend/app/api/_cache_eviction_routes.py`
- `web/backend/app/api/_cache_prewarming_routes.py`
- `web/backend/app/api/indicators/indicator_cache.py`
- `web/backend/app/api/indicators/_indicator_cache_responses.py`
- `web/backend/tests/test_cache_api.py`
- `web/backend/tests/test_cache_prewarming.py`
- `web/backend/tests/test_cache_eviction.py`

Out of scope:

- Dashboard cache helper cluster closed by G2.346 and G2.347.
- Core cache manager/lifecycle implementation closed by Batch1 unless a later P3/P4 inventory reopens a distinct surface.
- Indicator implementation internals beyond deciding whether `indicator_cache.py` belongs inside this cache API route cluster.

## Local Evidence Summary

Measured route/helper surfaces:

| Surface | Status | Lines | Route count | Role markers |
|---|---:|---:|---:|---|
| `web/backend/app/api/cache.py` | clean | 88 | 4 | route aggregator, cache manager access, all-cache clear endpoint, includes basic/eviction/prewarming routers |
| `web/backend/app/api/_cache_basic_routes.py` | clean | 319 | 5 | cache status/read/write/symbol invalidation/freshness route helper |
| `web/backend/app/api/_cache_eviction_routes.py` | clean | 121 | 2 | manual eviction and eviction statistics route helper |
| `web/backend/app/api/_cache_prewarming_routes.py` | clean | 211 | 4 | prewarming trigger/status and cache monitoring route helper |
| `web/backend/app/api/indicators/indicator_cache.py` | clean | 687 | 6 | indicator-domain API module with its own indicator runtime cache |
| `web/backend/app/api/indicators/_indicator_cache_responses.py` | clean | 399 | 0 | indicator response spec helper |
| `web/backend/tests/test_cache_api.py` | clean | 437 | test app include | cache API route test surface |
| `web/backend/tests/test_cache_prewarming.py` | clean | 399 | none | cache prewarming core/strategy test surface |
| `web/backend/tests/test_cache_eviction.py` | clean | 524 | none | cache eviction core/strategy test surface |

Measured route registration:

- `web/backend/app/api/cache.py` defines `router = APIRouter(prefix="/cache", tags=["cache"])`.
- `web/backend/app/router_registry.py` registers `cache.router` with `prefix="/api"` and `tags=["cache"]`.
- The effective cache API route tree is therefore rooted at `/api/cache`.
- `cache.py` includes:
  - `basic_router`
  - `eviction_router`
  - `prewarming_router`
- `web/backend/app/api/indicators/indicator_cache.py` defines its own `APIRouter()` and is registered through the indicator API path, not through `cache.py`.

Measured route handlers:

| File | Route handlers |
|---|---|
| `cache.py` | `DELETE /api/cache` via `clear_all_cache`; includes basic, eviction, and prewarming routers |
| `_cache_basic_routes.py` | `GET /status`; `GET /{symbol}/{data_type}`; `POST /{symbol}/{data_type}`; `DELETE /{symbol}`; `GET /{symbol}/{data_type}/fresh` |
| `_cache_eviction_routes.py` | `POST /evict/manual`; `GET /eviction/stats` |
| `_cache_prewarming_routes.py` | `POST /prewarming/trigger`; `GET /prewarming/status`; `GET /monitoring/metrics`; `GET /monitoring/health` |
| `indicator_cache.py` | indicator registry, calculation, batch calculation, indicator cache stats, and indicator cache clear endpoints under the indicator API tree |

Reference scan highlights:

- `basic_router`, `eviction_router`, and `prewarming_router` are referenced only by `cache.py` in the tracked local scan.
- `get_cache_manager` is broad and appears across cache route tests, cache lifecycle/core modules, dashboard tests, and API helpers. It is not a route-local symbol.
- `prewarm_cache` appears in `_cache_prewarming_routes.py`, `web/backend/app/core/cache_prewarming.py`, and `web/backend/tests/test_cache_prewarming.py`.
- `indicator_cache` appears in indicator-domain files and services; it is not referenced by `cache.py`.
- `_success_response_spec` is a broad response helper naming pattern across many API modules, so local copies in cache route helpers are response-contract helpers, not standalone cleanup targets.

GitNexus status:

- `route_map("/api/cache")` returned no matching routes and reported stale index status.
- `shape_check("/api/cache")` returned no matching route shapes and reported stale index status.
- Later symbol context calls failed with LadybugDB unavailable / not initialized errors.
- G2.348 therefore does not derive any source authorization from GitNexus.
- Any later source node touching route handlers must first restore a usable fresh GitNexus index and rerun API impact/context checks.

## Decision Table

| Surface | Current role | Route/helper ownership decision | Response-contract decision | Source authorization decision |
|---|---|---|---|---|
| `web/backend/app/api/cache.py` | Primary cache API route entry and router aggregator. Defines `/cache`, owns the all-cache clear endpoint, and includes the basic, eviction, and prewarming helper routers. | Keep as the active cache API route aggregator and entry surface. Do not fold split helpers back into this file from inventory alone. | Keep route-level response specs tied to this route entry. Any response contract change must follow API contract rules and OpenAPI synchronization. | No source work authorized. |
| `web/backend/app/api/_cache_basic_routes.py` | Split helper for basic cache status/read/write/symbol invalidation/freshness endpoints. | Keep as an active route helper owned by the cache API route cluster. It is not an orphan and should not be deleted because `cache.py` imports and includes it. | Keep local response specs as part of basic cache route contract. Do not consolidate `_success_response_spec` naming without a response-contract source node. | No source work authorized. |
| `web/backend/app/api/_cache_eviction_routes.py` | Split helper for manual eviction and eviction statistics endpoints. | Keep as an active route helper owned by the cache API route cluster. Its lifecycle effects are eviction-specific and should remain grouped with eviction tests if edited later. | Keep eviction response specs with the eviction route helper until a broader response helper consolidation is authorized. | No source work authorized. |
| `web/backend/app/api/_cache_prewarming_routes.py` | Split helper for prewarming trigger/status and cache monitoring metrics/health endpoints. | Keep as an active route helper owned by the cache API route cluster. Its lifecycle effects are prewarming/monitoring-specific and should remain grouped with prewarming tests if edited later. | Keep prewarming and monitoring response specs local to this helper until a broader response helper consolidation is authorized. | No source work authorized. |
| `web/backend/app/api/indicators/indicator_cache.py` | Indicator-domain API module with registry/calculation endpoints and its own indicator runtime cache operations. | Keep outside the cache API route cluster. It is cache-named but belongs to the indicator API tree, not the `/api/cache` route tree. | Keep indicator response behavior with indicator-domain contract surfaces. | No source work authorized from this node. |
| `web/backend/app/api/indicators/_indicator_cache_responses.py` | Indicator-domain response spec helper. | Keep outside the cache API route cluster. It supports `indicator_cache.py`, not `cache.py`. | Keep as indicator response-contract helper. | No source work authorized from this node. |
| `web/backend/tests/test_cache_api.py` | Route-level test surface for cache API read/write/delete/freshness/response format behavior. | Treat as the primary verification surface if the `/api/cache` route cluster is edited later. | Response format tests make it relevant for any future response-contract change. | No test work authorized from this node. |
| `web/backend/tests/test_cache_prewarming.py` | Core/strategy test surface for cache prewarming behavior. | Treat as adjacent verification if prewarming route behavior is changed later. | Not a route response-contract source by itself. | No test work authorized from this node. |
| `web/backend/tests/test_cache_eviction.py` | Core/strategy test surface for eviction behavior. | Treat as adjacent verification if eviction route behavior is changed later. | Not a route response-contract source by itself. | No test work authorized from this node. |

## Cluster Decision

The cache API route cluster is active and should remain grouped as:

- route aggregator: `web/backend/app/api/cache.py`
- split route helpers:
  - `web/backend/app/api/_cache_basic_routes.py`
  - `web/backend/app/api/_cache_eviction_routes.py`
  - `web/backend/app/api/_cache_prewarming_routes.py`
- primary route verification:
  - `web/backend/tests/test_cache_api.py`
- adjacent lifecycle verification:
  - `web/backend/tests/test_cache_prewarming.py`
  - `web/backend/tests/test_cache_eviction.py`

The indicator cache files are explicitly adjacent but separate:

- `web/backend/app/api/indicators/indicator_cache.py`
- `web/backend/app/api/indicators/_indicator_cache_responses.py`

No deletion, consolidation, route rewrite, response-contract rewrite, or test edit is authorized by G2.348.

## Source Authorization Finding

G2.348 does not open a source node.

Reasons:

1. The P2 route cluster has a clear active ownership model: `cache.py` is the aggregator, and the split helper modules are active included routers.
2. Indicator cache is cache-named but indicator-owned; merging it into the cache API route cluster would create a false route ownership boundary.
3. Response helper duplication is a broad API pattern, not a cache-route-only cleanup target.
4. GitNexus route/API evidence is unavailable or stale, so this inventory cannot satisfy any future source-edit impact gate.
5. The local evidence does not show a defect or explicit behavior change requirement.

## Recommended Next Gate

Continue the remaining cache modernization queue with:

`G2.349 core cache helper modules outside Batch1 inventory / no-source`

Required properties:

- `source_edit_authority=false`
- inventory core cache helper modules outside the already-closed Batch1 lifecycle surfaces
- decide whether each surface is canonical web-backend cache infrastructure, compatibility helper, or separate subsystem helper
- do not merge the cache API route cluster into core helper ownership
- do not perform source edits during inventory
