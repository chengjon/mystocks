# Backend MarketDataService Route Dependency Consumer Matrix - 2026-05-24

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为参考。

## Status

Status: review-ready.

Workline: G2.48 `get_market_data_service` route dependency consumer matrix and route-provider authorization candidate.

Recorded at: 2026-05-24T10:47:51+08:00.

Current HEAD: `0dce9ca97cd043f898039176394eb5076c353cf5`.

Base branch: `origin/wip/root-dirty-20260403`.

Parent PR: `#188`, merged at `0dce9ca97cd043f898039176394eb5076c353cf5`.

Parent issue: `#79`.

Parent decision issue: `#92`.

Source implementation authorized by this document alone: no.

## Governance Boundary

Boundary note: this packet records a route dependency consumer matrix and a
future implementation authorization candidate only. It does not edit backend
source, tests, route behavior, OpenAPI exposure, docs/API examples, generated
clients, frontend code, PM2/stateful gates, OpenSpec changes, issue labels, or
runtime configuration.

If a human reviewer approves this packet, a later implementation lane may use
the future write scope below. Until that explicit approval exists, this packet is
evidence and planning only.

## Parent State

| Item | State | Notes |
|---|---|---|
| PR `#188` | `MERGED` at `0dce9ca97cd043f898039176394eb5076c353cf5` | G2.47 selected `get_market_data_service` as the next consumer matrix / authorization candidate packet. |
| Issue `#79` | `OPEN`, `needs-triage` | Parent service singleton lifecycle DI issue remains open. |
| Issue `#92` | Parent decision context retained | This packet stays within the accepted downstream governance conveyor. |
| Completed provider modules | `8` | Existing route-provider seams remain closed and their compatibility getters must not be retired here. |

## Evidence Inputs

| Evidence | Path / Source | Role |
|---|---|---|
| G2.47 candidate selection | `docs/reports/quality/backend-service-lifecycle-di-candidate-selection-after-advanced-analysis-2026-05-24.md` | Selected `get_market_data_service` as the next consumer matrix target. |
| Generated G2.48 evidence | `.planning/codebase/generated/market-data-service-route-dependency-consumer-matrix-2026-05-24.json` | Machine-readable current-head consumer matrix and smoke results. |
| Route consumer file | `web/backend/app/api/market/market_data_request.py` | Contains the active `Depends(get_market_data_service)` route dependency surface. |
| Service getter package | `web/backend/app/services/market_data_service/` | Owns the package-level `MarketDataService` and `get_market_data_service()` surface. |
| Focused test base | `web/backend/tests/test_market_api_integration.py` | Already overrides `get_market_data_service` through `app.dependency_overrides`. |

## GitNexus Snapshot

GitNexus target:

| Symbol | File | Risk | Impacted count | Processes affected | Disposition |
|---|---|---:|---:|---:|---|
| `get_market_data_service` | `web/backend/app/services/market_data_service/get_market_data_service.py` | LOW | `0` | `0` | Route dependency surface still requires a route/provider authorization packet because text consumers are active. |

The indexed graph does not capture the seven FastAPI dependency call sites as
direct symbol callers, so this packet uses both GitNexus and current-head text /
route scans. This is a graph/text mismatch, not proof that the surface is unused.

## Route Dependency Consumer Matrix

The active route dependency surface is exactly seven public route handlers in
`web/backend/app/api/market/market_data_request.py`.

| Method | Full path | Handler | Handler line | Dependency line | Current dependency |
|---|---|---|---:|---:|---|
| POST | `/api/v1/market/fund-flow/refresh` | `refresh_fund_flow` | `198` | `201` | `Depends(get_market_data_service)` |
| GET | `/api/v1/market/etf/list` | `get_etf_list` | `231` | `238` | `Depends(get_market_data_service)` |
| POST | `/api/v1/market/etf/refresh` | `refresh_etf_data` | `273` | `274` | `Depends(get_market_data_service)` |
| GET | `/api/v1/market/chip-race` | `get_chip_race` | `298` | `303` | `Depends(get_market_data_service)` |
| POST | `/api/v1/market/chip-race/refresh` | `refresh_chip_race` | `328` | `331` | `Depends(get_market_data_service)` |
| GET | `/api/v1/market/lhb` | `get_lhb_detail` | `357` | `363` | `Depends(get_market_data_service)` |
| POST | `/api/v1/market/lhb/refresh` | `refresh_lhb_detail` | `389` | `391` | `Depends(get_market_data_service)` |

These routes are mounted through `VERSION_MAPPING["market"]["prefix"]` as
`/api/v1/market`. The future route-provider migration must preserve the method,
path, response model, response envelope, validation behavior, OpenAPI
operation IDs, and error behavior for each row.

## Compatibility And Package Surfaces

| Surface | Current evidence | Future disposition |
|---|---|---|
| `web/backend/app/services/market_data_service/get_market_data_service.py` | Defines module-level `_market_data_service` and `get_market_data_service()` only. No app-state installer/provider exists. | Add provider seam here in a later approved implementation lane. Preserve `get_market_data_service()` as compatibility fallback. |
| `web/backend/app/services/market_data_service/__init__.py` | Re-exports `MarketDataService` and `get_market_data_service`. | Re-export the future installer/provider/state key if implementation is approved. |
| `web/backend/app/services/__init__.py` | Defines a separate IntegratedServices accessor also named `get_market_data_service()`. | Do not modify in this lane; it is not the route import target. |
| `web/backend/app/services/market_data_adapter.py` | Imports `get_market_data_service` from the package and uses it as a fallback. | Keep out of the route-provider migration; the compatibility getter must remain. |
| `web/backend/tests/test_market_api_integration.py` | Uses `app.dependency_overrides[get_market_data_service]` in the `client` fixture. | Use as focused route override base; future implementation should update/extend tests for the provider dependency. |
| `MarketDataServiceV2` lane | Already has `install_market_data_service_v2()` and `get_market_data_service_v2_dependency()`. | Keep separate; do not consolidate V1 package service and V2 service in this lane. |

## Candidate Decision

This packet recommends approving a separate implementation branch that migrates
only the seven `market/market_data_request.py` route dependency parameters from
the compatibility getter to an app-state provider dependency.

The compatibility getter should remain public because non-route fallback
surfaces and tests still depend on it.

## Future Allowed Write Scope

If this packet is approved, the next implementation branch should be limited to:

| Path | Future allowed change |
|---|---|
| `web/backend/app/services/market_data_service/get_market_data_service.py` | Add a stable state key, `install_market_data_service(app, service=None)`, and `get_market_data_service_dependency(request)` while preserving `get_market_data_service()`. |
| `web/backend/app/services/market_data_service/__init__.py` | Re-export the future provider, installer, and state key. |
| `web/backend/app/api/market/market_data_request.py` | Convert only the seven route dependency parameters listed in the matrix to `Depends(get_market_data_service_dependency)`. |
| `web/backend/tests/test_market_data_service_lifecycle_di.py` or equivalent focused test file | Cover provider install, app-state override, fallback behavior, dependency override, and representative market route behavior. |
| `web/backend/tests/test_market_api_integration.py` | Update only if needed to keep the existing route override fixture aligned with the new provider dependency. |
| future implementation evidence report | Record implementation evidence and verification results. |
| future PR task card | Bind the implementation PR to the authorized source/test/report paths. |

## Future Implementation Shape

The future implementation should follow the established app-state provider plus
compatibility fallback pattern:

- keep `get_market_data_service()` as the compatibility getter
- add a stable state key, for example `MARKET_DATA_SERVICE_STATE_KEY`
- add `install_market_data_service(app, service=None)` that stores the selected
  service on `app.state`
- add `get_market_data_service_dependency(request: Request)` that reads from
  `app.state` and falls back to installer/getter when absent
- inject `MarketDataService` into the seven listed route handlers with
  `Depends(get_market_data_service_dependency)`
- preserve existing route paths, HTTP methods, response envelopes, OpenAPI
  operation IDs, validation behavior, and exception behavior

## Explicit Non-Goals

This packet and the future implementation lane must not:

- modify `web/backend/app/services/market_data_adapter.py`
- modify `web/backend/app/services/__init__.py`
- consolidate `MarketDataService` and `MarketDataServiceV2`
- remove, rename, or deprecate `get_market_data_service()`
- change route paths, HTTP methods, response models, response envelopes, or
  OpenAPI schema exposure
- change docs/API examples, generated clients, frontend code, PM2 scripts,
  runtime configuration, OpenSpec changes/specs, or GitHub issue labels
- expand into dashboard, V2 market data, data-service, strategy-service, or
  external-client seams
- authorize compatibility getter cleanup

## Required Future Gates

Before any future source implementation commit:

1. Run GitNexus impact/context for `get_market_data_service` and the selected
   route handlers.
2. Add failing focused tests for provider install/app-state override/fallback and
   at least one route dependency override path.
3. Implement the smallest provider seam that satisfies those tests.
4. Run the focused lifecycle DI test and `web/backend/tests/test_market_api_integration.py`.
5. Run `ruff check` on touched backend source/test files.
6. Run configured app/OpenAPI smoke and confirm route count, OpenAPI path count,
   duplicate operation IDs, and the seven selected market route paths.
7. Stage only the authorized paths and run GitNexus `detect_changes` on staged
   scope before committing.

## Rollback Plan For Future Implementation

If the future implementation causes regressions:

- revert the implementation PR
- keep this consumer matrix packet as historical evidence
- preserve `get_market_data_service()` compatibility behavior
- do not delete route consumers, tests, or package re-exports during rollback

## Verification Notes

Fresh current-head evidence used for this packet:

```text
current_head=0dce9ca97cd043f898039176394eb5076c353cf5
route_dependency_sites=7
reference_files=14
reference_count=52
gitnexus_get_market_data_service_risk=LOW
gitnexus_impacted_count=0
configured_app_import=ok
configured_route_count=548
configured_openapi_paths=500
configured_duplicate_operation_ids=0
selected_market_routes=7
test_market_api_integration_collect_only=18 collected
test_market_api_integration=18 passed
```

The configured app/OpenAPI smoke used non-sensitive placeholder environment
variables only. It did not read production secrets, run PM2, connect to a live
database intentionally, or authorize runtime promotion.
