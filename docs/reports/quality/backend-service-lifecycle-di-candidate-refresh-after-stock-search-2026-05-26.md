# Backend Service Lifecycle DI Candidate Refresh After StockSearch - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: candidate-refresh-prepared-for-review
- Workline: G2.129 service lifecycle DI candidate refresh after StockSearchService getter retirement
- Current HEAD: `dbef525d9b539674d69f75fde59b372d52298913`
- Parent PR: `#281` merged at `dbef525d9b539674d69f75fde59b372d52298913`
- Generated artifact: `.planning/codebase/generated/service-lifecycle-di-candidate-refresh-after-stock-search-2026-05-26.json`

This is a governance and evidence packet only. It does not edit backend source,
tests, route handlers, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec
changes, or GitHub issue labels.

## Input State

G2.128 closed the StockSearchService getter-retirement lane after PR `#280`
merged and current-head closeout evidence confirmed:

- `get_stock_search_service` definitions: `0`
- `_stock_search_service` tokens: `0`
- package re-export: absent
- app/API/test direct getter calls: `0`
- route dependency handlers: `6`

This packet refreshes the remaining service getter pool before choosing any
next lane.

## Current-Head Scan

| Metric | Count |
|---|---:|
| Service files scanned | 152 |
| Backend app files scanned | 575 |
| Backend API files scanned | 219 |
| Backend test files scanned | 203 |
| Service getter definitions found | 12 |
| `get_announcement_service` definitions | 0 |
| `get_email_service` definitions | 0 |
| `get_stock_search_service` definitions | 0 |
| `_announcement_service` tokens | 0 |
| `_email_service` tokens | 0 |
| `_stock_search_service` tokens | 0 |

## Candidate Inventory

| Candidate | Definition | Text-scan surface | GitNexus risk | Disposition |
|---|---|---:|---|---|
| `get_watchlist_service` | `web/backend/app/services/watchlist_service.py:613` | API direct `0`, app direct `6`, tests `2`, dependency refs `18`, route dependency handlers `7` | MEDIUM, impacted `15`, direct `9`, processes `0` | Next authorization candidate only |
| `get_market_data_service` | `web/backend/app/services/__init__.py:260` | API direct `0`, app direct `2`, tests `16`, dependency refs `24` | LOW, impacted `0`, but graph resolves to `web/backend/app/services/market_data_service/get_market_data_service.py` | Hold for graph/text symbol disambiguation |
| `get_tdx_service` | `web/backend/app/services/tdx_service.py:275` | API direct `2`, app direct `4`, tests `2`, dependency refs `15` | CRITICAL, impacted `6`, processes `5` | Hold: dashboard live-market seam |
| `get_data_service` | `web/backend/app/services/data_service.py:466` | API direct `5`, app direct `6`, tests `6`, dependency refs `0` | CRITICAL, impacted `5`, processes `7` | Hold: indicators/strategy data seam |
| `get_strategy_service` | `web/backend/app/services/strategy_service.py:455` | API direct `4`, app direct `11`, tests `1`, dependency refs `0` | CRITICAL, impacted `13`, modules `5` | Hold: strategy route/adapter/task seam |
| `get_streaming_service` | `web/backend/app/services/realtime_streaming_service.py:424` | API direct `0`, app direct `12`, tests `19`, dependency refs `0` | HIGH, impacted `9`, direct `9` | Hold: streaming/Socket.IO lifecycle seam |

## Watchlist Candidate Boundary

`get_watchlist_service` is the only sampled candidate that is not HIGH or
CRITICAL, and it has no affected execution processes in GitNexus. It is still
not an implementation-ready change because direct d=1 callers include both
adapter fallback helpers and route handlers:

| Surface | Required future handling |
|---|---|
| `web/backend/app/services/data_adapters/watchlist.py:_get_watchlist_service` | Must be included in authorization scope or explicitly retained |
| `web/backend/app/services/adapters/watchlist_adapter.py:_get_watchlist_service` | Must be included in authorization scope or explicitly retained |
| `web/backend/app/api/watchlist.py:get_user_groups` | Route dependency acceptance required |
| `web/backend/app/api/watchlist.py:create_group` | Route dependency acceptance required |
| `web/backend/app/api/watchlist.py:update_group` | Route dependency acceptance required |
| `web/backend/app/api/watchlist.py:delete_group` | Route dependency acceptance required |
| `web/backend/app/api/watchlist.py:get_watchlist_by_group` | Route dependency acceptance required |
| `web/backend/app/api/watchlist.py:move_stock_to_group` | Route dependency acceptance required |
| `web/backend/app/api/watchlist.py:get_watchlist_with_groups` | Route dependency acceptance required |

The next packet may prepare a WatchlistService getter-retirement authorization,
but this report does not authorize source edits.

## Decision

No direct implementation candidate is selected by G2.129.

Selected next gate:

1. Create G2.130 WatchlistService getter-retirement authorization packet.
2. Include adapter fallback seams, seven route dependency handlers, focused
   tests, GitNexus d=1 acceptance, and rollback criteria.
3. Keep `get_market_data_service` on hold until package-helper text evidence
   and GitNexus graph symbol resolution are reconciled.
4. Keep TDX, data, strategy, and streaming getters on their existing high-risk
   design tracks.

## Verification

- Parent PR `#281`: `MERGED`, merge commit
  `dbef525d9b539674d69f75fde59b372d52298913`
- Candidate scan: fresh current-head scan at
  `dbef525d9b539674d69f75fde59b372d52298913`
- GitNexus impact sampling:
  - `get_watchlist_service`: MEDIUM, impacted `15`, direct `9`, processes `0`
  - `get_market_data_service`: LOW, impacted `0`, graph/text symbol mismatch
  - `get_tdx_service`: CRITICAL, impacted `6`, processes `5`
  - `get_data_service`: CRITICAL, impacted `5`, processes `7`
  - `get_strategy_service`: CRITICAL, impacted `13`, modules `5`
  - `get_streaming_service`: HIGH, impacted `9`, direct `9`
- Staged GitNexus detect changes: low risk, changed files `4`, changed symbols
  `0`, affected symbols `0`, affected processes `0`

## Non-Goals

- No backend source or test edits
- No route handler edits
- No service getter deletion or rewrite
- No route path, response model, response shape, or OpenAPI exposure changes
- No frontend, PM2, or runtime workflow changes
- No OpenSpec change/spec creation or modification
- No GitHub issue label or readiness change
- No implementation authorization

## Next Gate

Human review / PR merge decision for G2.129. If accepted, prepare G2.130 as a
separate WatchlistService getter-retirement authorization packet before any
source branch is opened.
