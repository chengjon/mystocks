# Backend MarketDataService Route Provider Closeout - 2026-05-24

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为参考。

## Status

Status: closeout packet prepared.

Workline: G2.50 `MarketDataService` route-provider closeout after PR `#190`
merge.

This is a governance and evidence closeout packet only. It records the
post-merge state of the G2.49 implementation and does not authorize another
source implementation lane.

## Governance Boundary

Allowed scope:

- record PR `#190` merge status
- record current-head route dependency and OpenAPI evidence
- update the steward tree and evidence ledger
- create a path-limited mainline task card for this closeout packet

Out of scope:

- backend source changes
- route path or response model changes
- `market_data_adapter.py` fallback changes
- `web/backend/app/services/__init__.py` IntegratedServices changes
- `MarketDataServiceV2` consolidation
- frontend, docs/API, PM2, OpenSpec task, or issue-label changes
- selecting or authorizing the next service lifecycle implementation target

## Parent State

| Item | State | Notes |
|---|---|---|
| PR `#189` | `MERGED` at `7daf74ce0c3210defc2ad283583a335037daa500` | G2.48 consumer matrix and implementation authorization candidate. |
| PR `#190` | `MERGED` at `33163197b59893372d5d1d68af53acbfbbb0f613` | G2.49 route-provider implementation merged on `2026-05-24T04:13:57Z`. |
| Implementation commit | `f9a945b624a2f6915b5ea60acf6dbad6f1f61403` | Adds the provider seam and converts the authorized route dependencies. |
| Closeout HEAD | `33163197b59893372d5d1d68af53acbfbbb0f613` | Current `origin/wip/root-dirty-20260403` at closeout preparation. |

## Evidence Inputs

| Evidence | Path / Source | Notes |
|---|---|---|
| G2.48 authorization | `docs/reports/quality/backend-market-data-service-route-dependency-consumer-matrix-2026-05-24.md` | Identified exactly seven `/api/v1/market` route dependencies as the authorized migration surface. |
| G2.49 implementation report | `docs/reports/quality/backend-market-data-service-route-provider-implementation-2026-05-24.md` | Records TDD, implementation scope, GitNexus review signal, and local verification. |
| G2.49 generated evidence | `.planning/codebase/generated/market-data-service-route-provider-implementation-2026-05-24.json` | Machine-readable implementation evidence. |
| G2.49 task card | `governance/mainline/task-cards/pr-190.yaml` | Mainline scope and acceptance gates for PR `#190`. |
| PR merge metadata | GitHub PR `#190` | `state=MERGED`, merge commit `33163197b59893372d5d1d68af53acbfbbb0f613`. |

## Closeout Findings

The G2.49 implementation is now part of the target branch. Current-head checks
confirm the authorized route dependency surface is closed:

| Check | Value |
|---|---:|
| `Depends(get_market_data_service)` in `market_data_request.py` | `0` |
| `Depends(get_market_data_service_dependency)` in `market_data_request.py` | `7` |
| Provider import present in `market_data_request.py` | `true` |
| Service provider files under `web/backend/app/services` | `8` |
| Provider dependency functions under `web/backend/app/services` | `8` |
| API files with provider dependency usage | `11` |
| API provider dependency sites | `79` |

Current provider dependency functions:

- `get_announcement_service_dependency`
- `get_email_service_dependency`
- `get_market_data_service_dependency`
- `get_market_data_service_v2_dependency`
- `get_stock_search_service_dependency`
- `get_tdx_service_dependency`
- `get_tradingview_service_dependency`
- `get_watchlist_service_dependency`

## Compatibility Boundary

The following surfaces remain intentionally preserved:

- `get_market_data_service()` remains public compatibility fallback.
- `app.services.market_data_service` package exports the compatibility getter
  and provider dependency.
- `market_data_adapter.py` fallback surface remains unchanged.
- `web/backend/app/services/__init__.py` IntegratedServices accessor remains
  unchanged.
- `MarketDataServiceV2` remains a separate service lane.

Residual non-route references to `get_market_data_service()` are not deletion
candidates in this closeout:

- `web/backend/app/services/market_data_service/get_market_data_service.py`
- `web/backend/app/services/__init__.py`
- `web/backend/app/services/market_data_adapter.py`
- `web/backend/app/api/dashboard_data_source.py`

These references are either compatibility surfaces or separate route/helper
lanes. They must not be collapsed into the G2.49/G2.50 route-provider closure.

## Verification

| Gate | Result |
|---|---|
| PR `#190` metadata | `state=MERGED`, merge commit `33163197b59893372d5d1d68af53acbfbbb0f613`. |
| PR `#190` checks before merge | No failed check; checks were `pass` or `skipping`. |
| Focused lifecycle DI test | `5 passed in 2.35s`. |
| Market API integration test | `18 passed in 16.52s`. |
| Route dependency guard | `old_depends=0`, `new_depends=7`, `provider_import=true`. |
| Configured app/OpenAPI smoke | `app_import=ok`, routes=`548`, paths=`500`, duplicate operation IDs=`0`, selected `/api/v1/market` schema paths=`13`. |

The OpenAPI smoke used non-sensitive placeholder environment variables. It
captures the current schema exposure snapshot and must not be treated as a
permanent path-count baseline.

## GitNexus Review Signal

G2.49 staged `gitnexus_detect_changes(scope=staged)` returned `HIGH`
(`changed_files=9`, `changed_count=39`, `affected_count=6`). That signal was
kept in the implementation report and PR body for reviewer attention.

The HIGH signal is closed as reviewed evidence for this route-provider lane, not
as a suppressed warning. It came from `market_data_request.py` file-level flow
mapping while the accepted diff remained limited to the authorized provider
import and seven route dependency parameter changes.

## Decision

G2.49 is closed as merged and verified for the authorized `/api/v1/market`
route-provider surface.

This closeout does not authorize the next source implementation. The next
service lifecycle step should be a current-head candidate refresh / selection
packet, starting from merge commit
`33163197b59893372d5d1d68af53acbfbbb0f613`.

## Next Gate

Prepare a new current-head candidate refresh before selecting another service
lifecycle DI lane. That packet must:

- start from the post-PR `#190` head
- keep already preserved compatibility surfaces out of deletion scope
- distinguish route-provider candidates from dashboard/helper/fallback callers
- avoid broad external-client, DB/session-backed, cache/task-running, and
  process-level singleton seams unless explicitly authorized
- require a separate implementation authorization before any source edits
