# Backend Service Lifecycle Candidate Refresh After MarketDataService - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.114 service lifecycle candidate refresh after MarketDataService
Status: ready for review

## Purpose

Refresh the service lifecycle getter candidate pool after the G2.112
MarketDataService package-level getter retirement and G2.113 closeout were
merged.

This is a governance-only scan and routing packet. It does not modify backend
source, tests, route/API contracts, OpenAPI exposure, frontend code, PM2
workflows, OpenSpec changes, GitHub issue labels, or service implementation
logic.

## Parent Gate

| Gate | Result |
|---|---|
| Parent closeout | G2.113 accepted in PR `#266` |
| Parent merge commit | `18af895af5fd09c1dff832b6f8bc968227711a28` |
| Current refresh base | `18af895af5fd09c1dff832b6f8bc968227711a28` |

## Inventory

| Metric | Count |
|---|---:|
| Service files scanned | `152` |
| Backend app Python files scanned | `575` |
| API Python files scanned | `219` |
| Backend test Python files scanned | `200` |
| Service getter definitions | `15` |
| Candidate-like module-lazy definitions | `8` |

The retired package-level
`web/backend/app/services/market_data_service/get_market_data_service.py:get_market_data_service`
no longer appears in the candidate pool.

## Candidate Matrix

| Candidate | File | App refs | API refs | Test refs | GitNexus | Disposition |
|---|---|---:|---:|---:|---|---|
| `get_streaming_service` | `web/backend/app/services/realtime_streaming_service.py:424` | `12 / 3 files` | `0 / 0 files` | `19 / 2 files` | HIGH / `9` | hold: Socket.IO / streaming bridge seam |
| `get_tdx_service` | `web/backend/app/services/tdx_service.py:275` | `4 / 2 files` | `2 / 1 file` | `2 / 2 files` | CRITICAL / `6`, affected processes=`5` | hold: dashboard route process seam |
| `get_announcement_service` | `web/backend/app/services/announcement_service.py:526` | `2 / 1 file` | `0 / 0 files` | `1 / 1 file` | MEDIUM / `11` | hold: completed route-backed seam; do not reopen without new evidence |
| `get_email_service` | `web/backend/app/services/email_service.py:325` | `2 / 1 file` | `0 / 0 files` | `4 / 3 files` | MEDIUM / `6` | hold: route-backed email service seam |
| `get_watchlist_service` | `web/backend/app/services/watchlist_service.py:613` | `6 / 3 files` | `0 / 0 files` | `2 / 2 files` | MEDIUM / `15` | hold: route + adapter seam |
| `get_data_service` | `web/backend/app/services/data_service.py:466` | `6 / 3 files` | `5 / 2 files` | `6 / 2 files` | CRITICAL / `5`, affected processes=`7` | hold: indicator / strategy route process seam |
| `get_strategy_service` | `web/backend/app/services/strategy_service.py:455` | `11 / 5 files` | `4 / 1 file` | `1 / 1 file` | CRITICAL / `13` | hold: strategy task / adapter seam |
| `get_stock_search_service` | `web/backend/app/services/stock_search_service/stock_search_service.py:171` | `4 / 2 files` | `0 / 0 files` | `6 / 4 files` | CRITICAL / `6`, affected processes=`11` | hold: stock search route/process seam |

## Decision

No LOW-risk direct implementation candidate is selected from this refresh.

The remaining candidates are route-backed, adapter-backed, Socket.IO-backed,
dashboard-backed, task-backed, or process-affected. The next step should be a
strategy re-triage packet that decides whether to:

- split route-backed medium-risk candidates into explicit route-provider
  authorization lanes,
- build consumer matrices for adapter-backed candidates before authorizing code,
- keep Socket.IO / dashboard / task-backed candidates on hold until dedicated
  runtime evidence exists.

## Boundary

This PR does not:

- modify backend source or tests
- authorize source edits for any candidate
- delete any getter
- select the next implementation candidate
- modify route paths, response models, response shapes, or OpenAPI exposure
- modify frontend code
- modify PM2 workflows
- create or modify OpenSpec proposals/specs
- change GitHub issue labels or readiness state

## Next Gate

Human review / PR merge decision for G2.114.

If accepted, create a service lifecycle strategy re-triage packet before
selecting another service getter implementation candidate.
