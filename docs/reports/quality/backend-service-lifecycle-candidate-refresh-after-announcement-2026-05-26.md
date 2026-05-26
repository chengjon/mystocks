# Backend Service Lifecycle Candidate Refresh After AnnouncementService - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Ready for review.

## Parent Gate

| Field | Value |
|---|---|
| Parent node | G2.119 AnnouncementService getter-retirement closeout |
| Parent PR | `#272` |
| Parent state | `MERGED` |
| Parent merge commit | `550ce654219385afa65fc4fbfaf6129b2d2a4ca3` |
| Parent merged at | `2026-05-26T00:07:41Z` |
| Current HEAD | `550ce654219385afa65fc4fbfaf6129b2d2a4ca3` |

## Scan Summary

| Metric | Value |
|---|---:|
| Service Python files | 152 |
| Backend app Python files | 575 |
| API Python files | 219 |
| Backend test Python files | 201 |
| `get_*service` definitions found in services | 14 |
| Module-lazy candidates | 7 |
| `get_announcement_service` definitions | 0 |
| `_announcement_service` tokens in `announcement_service.py` | 0 |

`get_announcement_service` is removed from the active candidate pool by exact
current-head text scan.

## Candidate Matrix

| Candidate | File | Risk | Impact | Exact API refs | Exact adapter refs | Disposition |
|---|---|---:|---:|---:|---:|---|
| `get_streaming_service` | `web/backend/app/services/realtime_streaming_service.py:424` | HIGH | 9 | 0 | n/a | hold: Socket.IO / streaming seam |
| `get_tdx_service` | `web/backend/app/services/tdx_service.py:275` | CRITICAL | 6 | 2 | n/a | hold: dashboard route process seam |
| `get_email_service` | `web/backend/app/services/email_service.py:325` | MEDIUM | 6 | 0 | 0 | select next authorization candidate |
| `get_watchlist_service` | `web/backend/app/services/watchlist_service.py:613` | MEDIUM | 15 | 0 | 4 across 2 adapter files | hold: route + adapter seam |
| `get_data_service` | `web/backend/app/services/data_service.py:466` | CRITICAL | 5 | 5 | n/a | hold: indicator / strategy route process seam |
| `get_strategy_service` | `web/backend/app/services/strategy_service.py:455` | CRITICAL | 13 | 4 | n/a | hold: strategy task / adapter seam |
| `get_stock_search_service` | `web/backend/app/services/stock_search_service/stock_search_service.py:171` | CRITICAL | 6 | 0 | n/a | hold: stock-search route process seam |

## Email Candidate Detail

Exact text scan:

- direct `get_email_service` refs in API files: `0`
- direct `get_email_service` refs in adapter files: `0`
- `get_email_service_dependency` refs in backend app: `8`
- `get_email_service_dependency` refs in API: `7`
- `Depends(get_email_service_dependency)` route refs: `6`
- backend test direct getter refs: `4` across `3` files

GitNexus impact reports `MEDIUM`, impacted count `6`, affected processes `0`.
Its direct API caller list corresponds to notification route dependency
consumers, while exact text scan shows those routes no longer directly reference
the getter.

## Watchlist Hold Detail

`get_watchlist_service` remains behind EmailService because exact text scan still
finds `4` direct getter refs across:

- `web/backend/app/services/adapters/watchlist_adapter.py`
- `web/backend/app/services/data_adapters/watchlist.py`

Watchlist routes also have `7` `Depends(get_watchlist_service_dependency)` refs,
but the adapter seam must be resolved before a simple getter-retirement
authorization packet.

## GitNexus Stale Note

After `gitnexus analyze --with-gitignore` in this worktree, GitNexus MCP still
resolved the retired `get_announcement_service` symbol and its historical route
callers. Exact current-head text scan reports:

- `get_announcement_service` definitions: `0`
- `_announcement_service` tokens in `announcement_service.py`: `0`
- API direct getter refs: `0`

Do not reopen the AnnouncementService lane from this stale graph result.

## Decision

Select `get_email_service` as the next authorization candidate.

This packet does not authorize source edits. If G2.120 is accepted, create
G2.121 as an authorization-only packet before any EmailService source edit.

## Verification

| Check | Result |
|---|---|
| Parent PR `#272` state | `MERGED`, merge commit `550ce654219385afa65fc4fbfaf6129b2d2a4ca3` |
| `gitnexus analyze --with-gitignore` | completed in this worktree |
| GitNexus staged detect changes | risk=`low`; changed count=`0`; changed files=`4`; affected count=`0`; affected processes=`0` |
| Markdown governance | errors=`0` |
| JSON / YAML parse | passed |
| Cached diff check | passed |

## Boundary Confirmation

This is a candidate-refresh-only packet.

No backend source files, backend tests, route/API files, OpenAPI artifacts,
frontend files, PM2 workflows, OpenSpec changes/specs, or GitHub issue labels
are changed here.
