# G2.351 Cache Dashboard Test And E2E Coverage Inventory

## Metadata

- Date: `2026-06-05`
- Node: `G2.351`
- Mode: cache/dashboard test and E2E coverage inventory / no-source
- `source_edit_authority`: `false`
- Branch: `wip/root-dirty-20260403`
- Evidence head: `f707c67db`
- Parent: `G2.350 Src Cache Subsystem Reconciliation Inventory`
- Authorized work: inventory cache/dashboard test and E2E coverage surfaces after P1-P4 boundaries were classified
- Not authorized: source edits, test edits, fixture edits, E2E rewrites, deletion, consolidation, test quarantine changes, coverage threshold changes, frontend changes, OpenSpec mutation, or splitting coverage files into one-file confirmation nodes

## Source Edit Statement

No source files or test files were edited by G2.351.

This node writes only this report:

- `docs/reports/worklogs/claude-auto/g2-351-cache-dashboard-test-and-e2e-coverage-inventory-2026-06-05.md`

## Parent Gate

G2.350 directed the remaining cache modernization queue to:

`G2.351 cache/dashboard test and E2E coverage inventory / no-source`

Required properties:

- `source_edit_authority=false`
- inventory cache/dashboard tests as coverage surfaces after P1-P4 are bounded
- separate route tests, core cache tests, data-source cache tests, GPU cache tests, and mock/dashboard tests
- do not use test existence as deletion evidence
- do not perform source or test edits during inventory

## Reading Rules

This report is a coverage-surface inventory, not a test plan and not a cleanup list.

Per `architecture/STANDARDS.md`, test existence, test absence, unused-looking tests, or duplicated-looking coverage is not deletion evidence. Any later source or test cleanup must first prove code-path safety, function-tree status, and route/runtime impact.

Counts below are measured scan values. They are not quality targets and are not coverage percentages.

## Representative P5 Evidence

The upstream P5 queue listed representative cache/dashboard test files. G2.351 verified them as follows:

| Representative file | Status at scan | Test count | Coverage domain |
|---|---:|---:|---|
| `web/backend/tests/test_cache_lifecycle.py` | clean | 10 | core cache lifecycle/runtime |
| `tests/api/file_tests/test_cache_api.py` | clean | 10 | cache API route file tests |
| `tests/api/file_tests/test_dashboard_api.py` | clean | 17 | dashboard API route/cache/data-source/mock integration |
| `tests/api/test_cache_file.py` | dirty before G2.351, untouched | 19 | cache API route contract/performance-style file tests |
| `tests/integration/test_dashboard_api.py` | clean | 11 | dashboard API integration |
| `tests/performance/test_cache_strategy.py` | clean | 0 test functions found by static scan | data-source/cache strategy benchmark surface |
| `tests/performance/test_smart_cache_benchmark.py` | clean | 1 | smart-cache benchmark |
| `tests/unit/core/test_web_backend_multilevel_cache_runtime.py` | clean | 3 | web-backend multilevel cache runtime config |
| `tests/unit/core/test_src_core_multilevel_cache_runtime.py` | clean | 2 | `src` multilevel cache runtime config |
| `tests/e2e/dashboard.spec.ts` | clean | 4 | frontend dashboard E2E |
| `tests/e2e/dashboard-page.spec.ts` | clean | 16 | frontend dashboard page E2E |
| `tests/e2e/specs/dashboard.spec.ts` | dirty before G2.351, untouched | 14 | frontend dashboard E2E spec |

Representative P5 scan total:

- 12 representative files.
- 107 detected test functions/cases.
- 2 representative files were already dirty before this node and were not touched by G2.351.

## Extended Scan Summary

Tracked-file keyword scan for cache/dashboard test-like files found:

| Coverage group | Files | Detected test functions/cases | Reading |
|---|---:|---:|---|
| Cache API route | 6 | 63 | route/file/API tests for cache endpoints plus runtime-config probes |
| Core cache | 8 | 119 | cache manager, lifecycle, integration, eviction, prewarming, multilevel, async integration |
| Data-source cache | 6 | 73 | dashboard file route/data-source cache, smart cache, cache strategy/performance surfaces |
| GPU cache | 3 | 44 | GPU cache optimization and GPU cache-key/runtime surfaces |
| Dashboard API route | 3 | 26 | dashboard API, governance dashboard API, dashboard data source |
| Frontend/dashboard E2E and specs | 25 | 156 | dashboard Playwright/spec/unit-style frontend coverage and page objects |
| Dashboard general | 6 | 10 | dashboard service/composable/config/template tests |
| Cache general | 2 | 2 | database cache serialization and alert-rule cache surfaces |
| Performance/dashboard-cache general | 1 | 0 | dashboard widget type/performance-style surface |

Extended scan total:

- 60 tracked cache/dashboard test-like files.
- 493 detected test functions/cases.

## Coverage Domain Decision Table

| Domain | Representative surfaces | Current role | Decision | Source/test authorization |
|---|---|---|---|---|
| Cache API route coverage | `tests/api/file_tests/test_cache_api.py`, `tests/api/test_cache_file.py`, `web/backend/tests/test_cache_api.py` | Verifies `/api/cache` route behavior, response format, read/write/delete/freshness behavior, and app-router include surfaces. | Keep as primary P2 verification surface for any future cache API route source node. Dirty status in `tests/api/test_cache_file.py` is pre-existing and not touched. | Not authorized. |
| Dashboard API route coverage | `tests/api/file_tests/test_dashboard_api.py`, `tests/integration/test_dashboard_api.py`, `web/backend/tests/test_dashboard_data_source.py` | Verifies dashboard route/cache wrapper/data-source/builder behavior. | Keep as P1 dashboard helper verification surface. Do not merge with cache API route tests by name alone. | Not authorized. |
| Governance dashboard route coverage | `tests/api/file_tests/test_governance_dashboard_api.py` | Verifies separate governance dashboard route behavior. | Keep separate from dashboard cache helper coverage. Existing dirty status is outside G2.351. | Not authorized. |
| Core cache lifecycle/runtime coverage | `web/backend/tests/test_cache_lifecycle.py`, `web/backend/tests/test_cache_manager.py`, `web/backend/tests/test_cache_integration.py`, `tests/unit/test_cache.py`, runtime config cache tests | Verifies Batch1 cache manager/lifecycle, integration wrappers, multilevel cache, and runtime config behavior. | Keep as P3/P4 core verification surface. Do not use overlap to remove either web-backend or `src` cache tests. | Not authorized. |
| Eviction/prewarming coverage | `web/backend/tests/test_cache_eviction.py`, `web/backend/tests/test_cache_prewarming.py` | Verifies cache eviction and prewarming subsystems used by route helpers. | Keep as subsystem verification for future P2/P3 source work involving eviction or prewarming. | Not authorized. |
| Data-source cache coverage | `tests/unit/test_smart_cache.py`, `tests/performance/test_smart_cache_benchmark.py`, `tests/performance/test_phase1_datasource_benchmark.py`, `tests/unit/test_data_source_metrics_integration.py` | Verifies `SmartCache`, `LRUCache`, adapter/data-source cache behavior, and benchmark surfaces. | Keep under data-source cache ownership from P4. Do not fold into web-backend cache lifecycle coverage. | Not authorized. |
| GPU cache coverage | `src/gpu/api_system/tests/unit/test_cache/test_cache_optimization.py`, `src/gpu/api_system/tests/unit/test_cache/test_cache_optimization_enhanced.py`, `tests/unit/gpu/test_feature_calculation_gpu_cache_key.py` | Verifies GPU cache optimization/cache key behavior. | Keep under GPU cache ownership from P4. Do not interpret `CacheManager` names as web-backend cache coverage. | Not authorized. |
| Frontend dashboard E2E/spec coverage | `tests/e2e/dashboard.spec.ts`, `tests/e2e/dashboard-page.spec.ts`, `tests/e2e/specs/dashboard.spec.ts`, `web/frontend/tests/**/dashboard*.spec.ts`, dashboard page objects | Verifies dashboard frontend routes, page objects, visual/style/config behavior, and ArtDeco dashboard assumptions. | Keep as frontend/dashboard coverage. It is not evidence for backend cache helper deletion or source changes. | Not authorized. |
| Mock dashboard coverage | `src/mock/mock_Dashboard.py` consumers, mock data tests/scripts, dashboard file tests with mock markers | Verifies mock dashboard data support and test fixtures. | Keep as mock/dashboard verification surface. Do not treat mock data coverage as cache infrastructure coverage. | Not authorized. |
| Performance/cache coverage | cache performance/benchmark files | Verifies performance-sensitive cache behavior. | Keep as benchmark/performance evidence. Do not convert benchmark presence into pass/fail gate without a later explicit performance node. | Not authorized. |

## Dirty Worktree Note

The broad `tests/`, `web/backend/tests`, and frontend test directories contain many pre-existing dirty entries in this worktree. G2.351 did not edit any of them.

Representative dirty cache/dashboard-related files observed in this scan include:

- `tests/api/test_cache_file.py`
- `tests/e2e/specs/dashboard.spec.ts`
- `tests/api/file_tests/test_governance_dashboard_api.py`
- `tests/test_cache_performance.py`
- `src/gpu/api_system/tests/unit/test_cache/test_cache_optimization.py`
- `web/frontend/src/views/composables/__tests__/useTradingDashboard.spec.ts`
- `web/frontend/tests/unit/config/dashboard-route-canonical-truth.spec.ts`

These are status observations only. They do not authorize cleanup, revert, staging, or edits.

## Source Authorization Finding

G2.351 does not open a source node and does not open a test-edit node.

Reasons:

1. P1-P4 established multiple cache/dashboard ownership domains; the tests reflect those domains and should remain verification surfaces.
2. Test overlap is expected across route, core, data-source, GPU, mock, and frontend dashboard behavior.
3. Test existence is not deletion evidence.
4. Dirty test files predate this node and were not changed here.
5. No failing test output or defect was introduced by this report-only inventory.

## Recommended Next Gate

The P1-P5 cache modernization inventory queue is now bounded.

Recommended next node:

`G2.352 cache modernization inventory queue closeout / no-source`

Required properties:

- `source_edit_authority=false`
- summarize G2.346-G2.351 boundaries and decisions
- list which surfaces remain active verification surfaces
- identify whether any future source authorization preflight is needed, and only if backed by a concrete defect or behavior-change request
- do not perform source or test edits during closeout
