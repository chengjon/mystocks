# Backend Service Lifecycle DI Candidate Refresh After IndicatorRegistry Provider - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Generated at: `2026-05-24T18:10:53+08:00`

Base branch: `wip/root-dirty-20260403`

Current branch: `g2-56-service-lifecycle-candidate-refresh-after-indicator-registry`

Current HEAD: `1fc4a4c7a86c`

## Status

G2.56 is a governance-only candidate refresh after the flat API
`IndicatorRegistry` route-provider implementation and closeout were merged.

This packet records current-head evidence and next-gate constraints. It does
not authorize source edits, route changes, OpenAPI changes, compatibility getter
cleanup, issue label changes, or OpenSpec implementation work.

## Upstream Merge Evidence

| Workline | PR | State | Merge commit | Notes |
| --- | --- | --- | --- | --- |
| G2.54 | `#195` | `MERGED` | `5b12a3c08cac3558c56af615ff14c05913d96f72` | Implemented the flat API `IndicatorRegistry` route provider |
| G2.55 | `#196` | `MERGED` | `1fc4a4c7a86cf464dedb742612c052b911d4ef5f` | Closed out and refreshed current-head evidence for PR `#195` |

## Current-Head Scan Summary

| Metric | Value |
| --- | ---: |
| API files scanned | `219` |
| Service files scanned | `152` |
| Backend test files scanned | `195` |
| Service provider state keys | `10` |
| Service provider functions | `20` |
| Service provider records | `30` |
| Route `Depends(...)` sites | `353` |
| Provider-style route dependency sites | `81` |
| Getter-style route dependency sites | `272` |

The provider-style count increased by `2` after the `IndicatorRegistry` route
provider landed. This matches the two converted `indicator_cache.py` read
handlers and does not indicate a new implementation backlog.

## IndicatorRegistry Closeout Check

| Check | Result |
| --- | --- |
| Direct `get_indicator_registry()` route calls under `web/backend/app/api` | `0` |
| `get_indicator_registry_dependency` route sites | `2` |
| Converted route file | `web/backend/app/api/indicators/indicator_cache.py` |
| Provider surface | `INDICATOR_REGISTRY_STATE_KEY`, `install_indicator_registry`, `get_indicator_registry_dependency` |
| Compatibility getter | Preserved |
| Package registry / `IndicatorCalculator` surfaces | Excluded from the route-provider batch |

The remaining `get_indicator_registry()` references are service/test or
compatibility-surface references. They are not route direct-getter regressions.

## Provider Dependency Groups

| Dependency | Sites | Files | Route files |
| --- | ---: | ---: | --- |
| `get_advanced_analysis_service_dependency` | `14` | `1` | `advanced_analysis_api.py` |
| `get_market_data_service_v2_dependency` | `14` | `2` | `dashboard_data_source.py`, `market_v2.py` |
| `get_announcement_service_dependency` | `11` | `1` | `announcement/routes.py` |
| `get_market_data_service_dependency` | `7` | `1` | `market/market_data_request.py` |
| `get_watchlist_service_dependency` | `7` | `1` | `watchlist.py` |
| `get_email_service_dependency` | `6` | `1` | `notification.py` |
| `get_stock_search_service_dependency` | `6` | `2` | `market/market_data_request.py`, `stock_search/stock_search_result.py` |
| `get_tradingview_service_dependency` | `6` | `1` | `tradingview.py` |
| `get_tdx_service_dependency` | `5` | `1` | `tdx.py` |
| `get_data_source_dependency` | `3` | `1` | `dashboard.py` |
| `get_indicator_registry_dependency` | `2` | `1` | `indicators/indicator_cache.py` |

Several rows are already implemented or inherited as reference evidence. This
table is a current-head inventory, not a queue of authorized edits.

## Remaining Getter / Direct-Call Surfaces

| Surface | Current evidence | Disposition |
| --- | --- | --- |
| Authentication dependencies such as `get_current_user` | Broad route use, `215` sites | Out of scope for service lifecycle DI candidate selection |
| Database/session dependencies such as `get_db` and repository getters | Route contract / persistence boundary | Requires separate route or repository governance, not ordinary service-provider migration |
| `get_postgres_async` direct calls | `22` sites across `8` API files | Infrastructure/data-access seam; not selected by this packet |
| `get_config_manager` direct calls | `17` sites across `2` API files plus historical file evidence | Needs a separate config ownership decision before any provider work |
| `get_data_source_factory` direct calls | `17` sites across `9` API files | Broad factory seam; not selected without a design/authorization packet |
| `get_technical_pattern_detection_service` | Existing DI pilot/reference surface | Do not reopen unless current-head evidence contradicts the completed pilot record |

No new low-risk implementation target is selected by G2.56.

## Runtime And Contract Evidence

Configured app/OpenAPI smoke remains stable at current HEAD:

```text
routes_total=548
openapi_paths_total=500
duplicate_operation_ids=0
warnings=0
```

Focused regression checks remain green:

```text
pytest -o addopts= web/backend/tests/test_indicator_registry_route_provider.py -q --tb=short --no-cov
2 passed in 1.62s

pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_v1_indicator_endpoints_have_examples_parameter_docs_and_descriptions -q --tb=short --no-cov
1 passed
```

## GitNexus Refresh Note

GitNexus index refresh was attempted before this packet.

The root checkout was stale/dirty relative to the remote branch, so it was not
rebased for indexing. Running `gitnexus analyze` inside this linked worktree
failed with `ENOTDIR .git/info` because linked worktrees use a `.git` file
instead of a `.git` directory.

For G2.56, current-head static scans plus runtime/OpenAPI smoke are treated as
authoritative. Do not use stale GitNexus graph output to choose the next service
lifecycle DI candidate unless the index is refreshed from a non-linked checkout
or a later review explicitly waives that limitation.

## Decision

G2.56 keeps the service lifecycle DI lane in `candidate-refresh` state.

The `IndicatorRegistry` route-provider closeout remains accepted at current
HEAD: route direct getter use is closed, provider dependency sites are present,
and app/OpenAPI behavior is stable. The wider service lifecycle lane should not
advance directly into source implementation from this packet.

## Next Gate

1. Human review this G2.56 packet / PR.
2. Refresh GitNexus from a checkout where `gitnexus analyze` can update the
   index, or explicitly record a stale-graph waiver.
3. If a next service lifecycle lane is desired, create a separate authorization
   packet with exact write scope, pre-edit GitNexus impact, TDD plan, rollback
   boundary, and focused verification.
4. Keep source edits locked until that separate authorization packet is
   approved.
