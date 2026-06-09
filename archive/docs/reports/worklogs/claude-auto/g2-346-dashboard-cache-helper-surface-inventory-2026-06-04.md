# G2.346 Dashboard Cache Helper Surface Inventory

## Metadata

- Date: `2026-06-04`
- Node: `G2.346`
- Mode: dashboard cache helper surface inventory / no-source
- `source_edit_authority`: `false`
- Branch: `wip/root-dirty-20260403`
- Evidence head: `711623ca9`
- Parent: `G2.345 Cache Core Batch1 stage closeout and remaining inventory`
- Authorized work: inspect the dashboard cache helper surface as one group and produce one decision table
- Not authorized: source edits, test edits, deletion, consolidation, route behavior changes, frontend changes, OpenSpec mutation, or splitting the dashboard cache helper surface into multiple fine-grained confirmation nodes

## Source Edit Statement

No source files were edited by G2.346.

This node writes only this report:

- `docs/reports/worklogs/claude-auto/g2-346-dashboard-cache-helper-surface-inventory-2026-06-04.md`

## Parent Gate

G2.345 classified the dashboard cache helper cluster as the next P1 cache modernization inventory surface:

| Priority | Group | Handling |
|---|---|---|
| P1 | Dashboard cache helper cluster | Combine into one no-source G node; do not split one file per decision |

This report follows that gate. It is an inventory and decision table, not a deletion list and not a source authorization.

## Inventory Scope

In scope for this surface pass:

- `web/backend/app/api/dashboard.py`
- `web/backend/app/api/dashboard_cache.py`
- `web/backend/app/api/dashboard_data_source.py`
- `web/backend/app/api/dashboard_builders.py`
- `web/backend/app/models/dashboard.py`
- `web/backend/app/services/adapters/dashboard_adapter.py`
- `web/backend/app/services/data_adapters/dashboard.py`
- `web/backend/app/services/risk_management/risk_dashboard.py`
- `web/backend/app/api/governance_dashboard.py`
- `web/backend/app/api/_governance_dashboard_responses.py`

The last two files are dashboard-named governance surfaces. They are included to prevent accidental conflation with the dashboard cache helper cluster, not because they are cache-helper targets.

## Evidence Summary

Measured local static inventory:

| Surface | Status at scan | Lines | Top-level role evidence |
|---|---:|---:|---|
| `web/backend/app/api/dashboard.py` | clean | 436 | route module; imports `dashboard_cache`, `dashboard_data_source`, `dashboard_builders`, dashboard models, and `CacheManager` |
| `web/backend/app/api/dashboard_cache.py` | clean | 84 | helper module with `generate_cache_key`, `try_get_cached_dashboard`, and `cache_dashboard_data` |
| `web/backend/app/api/dashboard_data_source.py` | clean | 701 | provider module with `RealBusinessDataSource`, `get_data_source`, and dashboard market-overview prewarm entry |
| `web/backend/app/api/dashboard_builders.py` | clean | 164 | response builder module with four dashboard summary builders |
| `web/backend/app/models/dashboard.py` | clean | 245 | Pydantic response/request contract models |
| `web/backend/app/services/adapters/dashboard_adapter.py` | clean | 312 | service adapter class `DashboardDataSourceAdapter` |
| `web/backend/app/services/data_adapters/dashboard.py` | clean | 299 | parallel data adapter class `DashboardDataSourceAdapter` |
| `web/backend/app/services/risk_management/risk_dashboard.py` | clean | 634 | risk-management dashboard service and chart/value objects |
| `web/backend/app/api/governance_dashboard.py` | dirty before G2.346, untouched | 699 | governance dashboard route module; separate `get_dashboard_summary` name |
| `web/backend/app/api/_governance_dashboard_responses.py` | clean | 217 | governance dashboard response spec helper |

Reference scan highlights:

- `try_get_cached_dashboard` appears in `dashboard.py`, `dashboard_cache.py`, and `tests/api/file_tests/test_dashboard_api.py`.
- `cache_dashboard_data` appears in `dashboard.py`, `dashboard_cache.py`, and `tests/api/file_tests/test_dashboard_api.py`.
- `dashboard.py` is the only tracked non-test caller/importer of the dashboard cache helper functions found in this scan.
- `generate_cache_key` is not a unique project-wide symbol name; it also appears in core cache utilities and tests. Any future source work must disambiguate by file path.
- `get_data_source` is broad: it appears in 25 tracked Python files. It should not be treated as a dashboard-cache-local helper.
- `DashboardDataSourceAdapter` appears in both `services/adapters/dashboard_adapter.py` and `services/data_adapters/dashboard.py`, plus factory/tests. This is an adapter-surface concern, not a dashboard cache helper decision.
- `governance_dashboard.py` does not reference `try_get_cached_dashboard` or `cache_dashboard_data` in this scan.

GitNexus status:

- Fresh GitNexus context/impact evidence could not be used for this node.
- The tool reported LadybugDB unavailable because `.gitnexus/lbug.wal` did not match the current database, with stale index status.
- No source authorization is derived from GitNexus for G2.346.
- Any later source-edit node touching these symbols must first restore a fresh GitNexus index and rerun impact analysis.

## Decision Table

| Surface | Current role | Cache-helper classification | Decision | Future authorization condition |
|---|---|---|---|---|
| `web/backend/app/api/dashboard.py` | Active dashboard API route orchestrator. It wires cache manager access, helper cache read/write, data source access, builders, response envelopes, and exception handling. | Dashboard cache entry surface, but not a reusable cache lifecycle owner. | Keep as the active dashboard route boundary. Do not delete, consolidate, or split decisions by endpoint during this no-source node. | A future source node must be route-scoped and must include route contract tests plus fresh GitNexus impact if changing route behavior, cache lookup/write behavior, exception mapping, or response shape. |
| `web/backend/app/api/dashboard_cache.py` | Small dashboard-local helper module for cache key generation, cache read, and cache write. | Primary dashboard cache helper file. It is route-owned by `dashboard.py`; it is not the canonical cache manager implementation. | Keep as a dashboard-owned helper. Do not delete solely because its production caller set is small. Do not merge into `dashboard.py` without a source authorization node. | If source work is later authorized, handle this together with `dashboard.py` and `tests/api/file_tests/test_dashboard_api.py`; do not create separate one-file confirmation nodes for each helper. |
| `web/backend/app/api/dashboard_data_source.py` | Dashboard data provider surface containing `RealBusinessDataSource`, business-source access, market overview prewarm, and `get_data_source`. | Adjacent dashboard data-source surface, not the cache helper itself. | Keep separate from the cache helper classification. Do not treat `get_data_source` as dashboard-cache-local because the symbol has broad project references. | A future source node must be data-source scoped and must prove route/data-source blast radius separately from cache helper cleanup. |
| `web/backend/app/api/dashboard_builders.py` | Dashboard response builder surface for market overview, watchlist, portfolio, and risk alert summaries. | Response-shaping helper, not cache owner. | Keep as a builder/helper module. It should remain grouped with dashboard route contract reasoning, not cache lifecycle cleanup. | Future source work must include response model/fixture coverage if builder output shape changes. |
| `web/backend/app/models/dashboard.py` | Dashboard request/response Pydantic contract surface. | Contract model surface, not cache owner. | Keep as dashboard contract truth for the route cluster. No cache cleanup decision should mutate it. | Any source change requires explicit schema/contract authorization and tests that pin API response compatibility. |
| `web/backend/app/services/adapters/dashboard_adapter.py` | Service adapter class named `DashboardDataSourceAdapter`, tied to data quality monitor and data source interface. | Dashboard data adapter surface outside the route-local cache helper. | Keep outside the dashboard cache helper target. Inventory notes it only to avoid accidental merge with `dashboard_cache.py`. | Future work should be an adapter-consolidation or data-source-factory node, not a cache helper node. |
| `web/backend/app/services/data_adapters/dashboard.py` | Parallel service data adapter class also named `DashboardDataSourceAdapter`. | Dashboard data adapter surface outside the route-local cache helper. | Keep outside the dashboard cache helper target. The duplicate class name needs its own adapter-surface inventory before any consolidation. | Future source work must compare both adapter files, factories, and tests in one adapter-focused no-source authorization pass. |
| `web/backend/app/services/risk_management/risk_dashboard.py` | Risk-management dashboard service with risk overview, portfolio risk summary, chart data, and dashboard service class. | Dashboard-named but not part of the dashboard API cache helper path. | Defer. Do not include in dashboard cache helper cleanup. | Future work should be risk-dashboard scoped and should not inherit decisions from dashboard API cache helper inventory. |
| `web/backend/app/api/governance_dashboard.py` | Governance dashboard API route module with separate response models and its own `get_dashboard_summary` name. It was already dirty at scan time and was not touched by G2.346. | Separate governance dashboard route; not a dashboard cache helper surface. | Defer and keep out of this cache-helper decision. Do not use same-name `get_dashboard_summary` as evidence of coupling to dashboard cache. | Any future source work must first account for the pre-existing dirty state and run route-specific impact/contract checks. |
| `web/backend/app/api/_governance_dashboard_responses.py` | Governance dashboard response spec helper. | Separate governance response helper; not cache-related. | Defer. It exists only as adjacency evidence for the governance dashboard route. | Future work belongs with governance dashboard response-contract maintenance. |

## Cluster Decision

The dashboard cache helper cluster remains a coherent route-local surface:

- The source-facing cluster is `dashboard.py` + `dashboard_cache.py` + dashboard route file tests.
- `dashboard_data_source.py`, `dashboard_builders.py`, and `models/dashboard.py` are adjacent route/data/contract surfaces that must be considered if behavior or response shape changes, but they are not cache helper cleanup targets by themselves.
- Dashboard-named risk and governance files are explicitly out of the cache helper cluster.
- No deletion, consolidation, or source rewrite is authorized by G2.346.
- This node closes the inventory as one table. It should not be decomposed into additional one-file confirmation nodes.

## Recommended Next Gate

No immediate source node is authorized by G2.346.

If dashboard cache helper work continues, the next gate should be one combined no-source source-authorization preflight, for example:

`G2.347 dashboard cache helper source authorization preflight / no-source`

Required properties:

- `source_edit_authority=false`
- restore fresh GitNexus index before any source authorization
- evaluate `dashboard.py`, `dashboard_cache.py`, and `tests/api/file_tests/test_dashboard_api.py` together
- explicitly decide whether source work is needed at all
- continue to exclude governance dashboard, risk dashboard, and data-adapter consolidation from the dashboard cache helper scope
