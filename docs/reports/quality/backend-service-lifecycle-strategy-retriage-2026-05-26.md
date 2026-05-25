# Backend Service Lifecycle Strategy Re-Triage - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.115 service lifecycle strategy re-triage
Status: ready for review

## Purpose

Route the remaining service lifecycle getter candidates after G2.114 confirmed
that no LOW-risk direct implementation candidate remains.

This is a governance-only strategy packet. It does not modify backend source,
tests, route/API contracts, OpenAPI exposure, frontend code, PM2 workflows,
OpenSpec changes, GitHub issue labels, or service implementation logic.

## Parent Gate

| Gate | Result |
|---|---|
| Parent refresh | G2.114 accepted in PR `#267` |
| Parent merge commit | `3d0b72b68114effc9ba76aa3bea2d64edca15216` |
| Current strategy base | `3d0b72b68114effc9ba76aa3bea2d64edca15216` |

## Re-Triage Decision

G2.114 left 8 module-lazy candidates and selected no LOW-risk direct
implementation candidate. The next step is not another source edit. The next
step is an exact consumer matrix for medium-risk route-backed candidates.

| Lane | Candidates | Decision |
|---|---|---|
| Medium route-backed exact matrix | `get_announcement_service`, `get_email_service`, `get_watchlist_service` | Create G2.116 consumer matrix before choosing one authorization target |
| Socket.IO / streaming | `get_streaming_service` | Hold until Socket.IO manager and streaming bridge runtime ownership are modeled |
| Dashboard process | `get_tdx_service` | Hold until dashboard route/process evidence exists |
| Indicator / strategy route process | `get_data_service` | Hold until indicator and strategy route ownership evidence exists |
| Strategy task / adapter | `get_strategy_service` | Hold until task and adapter ownership evidence exists |
| Stock-search route/process | `get_stock_search_service` | Hold until stock-search route/process evidence exists |

## G2.116 Scope

The next packet should collect exact consumer evidence for:

- `web/backend/app/services/announcement_service.py:get_announcement_service`
- `web/backend/app/services/email_service.py:get_email_service`
- `web/backend/app/services/watchlist_service.py:get_watchlist_service`

It should record:

- direct text refs and GitNexus graph refs
- API route consumers
- adapter consumers
- existing route-provider or dependency seams
- test coverage currently proving the seam
- whether the candidate is already completed, should remain retained, or needs
  a future route-provider authorization packet

G2.116 must not edit source, delete getters, or authorize implementation.

## Boundary

This PR does not:

- modify backend source or tests
- authorize source edits for any candidate
- delete any getter
- select a concrete implementation candidate
- modify route paths, response models, response shapes, or OpenAPI exposure
- modify frontend code
- modify PM2 workflows
- create or modify OpenSpec proposals/specs
- change GitHub issue labels or readiness state

## Next Gate

Human review / PR merge decision for G2.115.

If accepted, create G2.116 medium route-backed exact consumer matrix before
selecting another service getter implementation candidate.
