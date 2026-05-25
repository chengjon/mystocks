# Backend Service Lifecycle Candidate Refresh After EmailNotificationService - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.110 service lifecycle candidate refresh
Status: ready for review

## Purpose

Refresh the service lifecycle getter candidate set after G2.109 closed the
EmailNotificationService legacy getter-retirement lane. This packet selects the
next authorization candidate only; it does not authorize source edits.

## Parent State

| Item | Value |
|---|---|
| Parent closeout | G2.109 |
| Parent PR | `#262` |
| Parent merge commit | `ae6d2f287ddb8d71119ce52ef4ebaf00d64dc7b5` |
| Current HEAD | `ae6d2f287ddb8d71119ce52ef4ebaf00d64dc7b5` |

## Scan Scope

| Scope | Count |
|---|---:|
| Service files | `152` |
| Backend app files | `575` |
| API files | `219` |
| Backend test files | `199` |
| All repository test files | `1211` |
| Service getter definitions | `16` |
| Candidate-like module-lazy definitions | `9` |

The retired `web/backend/app/services/email_notification_service.py:get_email_service`
no longer appears in the candidate set.

## Candidate Rows

| Candidate | File | Kind | App refs/files | API refs/files | Backend test refs/files | GitNexus | Disposition |
|---|---|---|---:|---:|---:|---|---|
| `get_market_data_service` | `web/backend/app/services/market_data_service/get_market_data_service.py:28` | module-lazy | `8/4` | `0/0` | `13/4` | LOW / `0` | selected for next authorization packet |
| `get_streaming_service` | `web/backend/app/services/realtime_streaming_service.py:424` | module-lazy | `12/3` | `0/0` | `19/2` | HIGH / `9` | hold; Socket.IO / streaming seam |
| `get_tdx_service` | `web/backend/app/services/tdx_service.py:275` | module-lazy | `4/2` | `2/1` | `2/2` | CRITICAL / `4`, affected processes=`5` | hold; dashboard route process seam |
| `get_announcement_service` | `web/backend/app/services/announcement_service.py:526` | module-lazy | `2/1` | `0/0` | `1/1` | MEDIUM / `11` | completed/route-backed hold, not selected |
| `get_email_service` | `web/backend/app/services/email_service.py:325` | module-lazy | `2/1` | `0/0` | `4/3` | MEDIUM / `6` | route-backed EmailService seam hold |
| `get_watchlist_service` | `web/backend/app/services/watchlist_service.py:613` | module-lazy | `6/3` | `0/0` | `2/2` | MEDIUM / `13` | adapter/route seam hold |
| `get_data_service` | `web/backend/app/services/data_service.py:466` | module-lazy | `6/3` | `5/2` | `6/2` | CRITICAL / `4`, affected processes=`7` | indicator/strategy route hold |
| `get_strategy_service` | `web/backend/app/services/strategy_service.py:455` | module-lazy | `11/5` | `4/1` | `1/1` | CRITICAL / `11` | strategy/task/adapter hold |
| `get_stock_search_service` | `web/backend/app/services/stock_search_service/stock_search_service.py:171` | module-lazy | `4/2` | `0/0` | `6/4` | CRITICAL / `6`, affected processes=`11` | stock-search route hold |

## Decision

Select `web/backend/app/services/market_data_service/get_market_data_service.py`
`get_market_data_service` as the next authorization candidate only.

Rationale:

- GitNexus impact is LOW with impacted count `0`.
- Direct API refs are `0`.
- Focused lifecycle and dashboard tests already reference the surface, giving a
  natural test gate for a future authorization/implementation lane.
- Higher-risk candidates have route, adapter, streaming, or process seams that
  should not be mixed into the next small batch.

## Boundary

This packet does not:

- edit backend source or tests
- delete or migrate any getter
- change route/API behavior or OpenAPI exposure
- change frontend code
- change PM2 workflows
- create or modify OpenSpec changes/specs
- change GitHub issue labels or readiness state
- authorize G2.111 implementation work

## Next Gate

Human review / PR merge decision for G2.110.

If accepted, create G2.111 as a MarketDataService getter-retirement
authorization packet before any market-data service source edit.
