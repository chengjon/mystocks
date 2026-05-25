# Backend Service Lifecycle Candidate Refresh After EnhancedDataService - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.101 service lifecycle candidate refresh after EnhancedDataService
Status: ready for review

## Purpose

Refresh service lifecycle getter candidates after the EnhancedDataService public
compatibility getter lane was closed through PR `#253`.

This packet is candidate-refresh only. It does not authorize source edits,
getter deletion, route/API changes, OpenAPI exposure changes, PM2 execution,
OpenSpec changes, frontend edits, or issue-label changes.

## Input State

G2.100 was accepted through PR `#253`, merged at
`d7be7e6e8bb0ad3bcf62b9420bc5da5d7941054e`.

Current HEAD for this packet:
`d7be7e6e8bb0ad3bcf62b9420bc5da5d7941054e`.

## Current-Head Scan Summary

| Metric | Value |
|---|---:|
| Service files scanned | `152` |
| Backend app files scanned | `575` |
| API files scanned | `219` |
| Test files scanned | `1008` |
| Getter definitions | `18` |
| Candidate-like definitions | `4` |
| Holds | `14` |

`get_enhanced_data_service` is no longer present as a service getter definition.

## Candidate Rows

| Symbol | File | Line | App refs | Route/API refs | Test refs | Package export refs | Disposition |
|---|---|---:|---:|---:|---:|---:|---|
| `get_email_service` | `web/backend/app/services/email_notification_service.py` | `324` | `3` | `0` | `3` | `0` | hold duplicate logical getter name; prior email lane requires separate decision |
| `get_announcement_service` | `web/backend/app/services/announcement_service.py` | `526` | `2` | `0` | `1` | `0` | hold completed announcement DI lane; do not reopen here |
| `get_email_service` | `web/backend/app/services/email_service.py` | `325` | `3` | `0` | `3` | `0` | hold duplicate logical getter name; prior email lane requires separate decision |
| `get_tradingview_service` | `web/backend/app/services/tradingview_widget_service.py` | `322` | `2` | `0` | `2` | `0` | select future authorization candidate only |

## Selected Next Lane

Select `get_tradingview_service` as the next future authorization candidate.

Rationale:

- The getter has no route/API references.
- It has no package export references.
- GitNexus impact is LOW with impacted count `1` and affected processes `0`.
- The only direct graph caller is `install_tradingview_service`, so the future
  authorization packet can define a narrow implementation boundary around the
  module-local fallback singleton without touching route registration.

Boundary:

- This selection does not authorize deleting `TradingViewWidgetService`.
- This selection does not authorize changing TradingView routes, response
  models, response shapes, OpenAPI exposure, frontend code, PM2 state, or issue
  labels.
- A future G2.102 packet must be authorization-only first and must distinguish
  getter retirement from the active TradingView service class, install helper,
  and dependency provider.

## Verification Evidence

| Check | Result |
|---|---|
| GitNexus index | Refreshed with `gitnexus analyze --with-gitignore`; graph contains `62,761` nodes, `145,913` edges, `3,287` clusters, and `300` flows |
| Getter candidate scan | `152` service files, `575` app files, `219` API files, `1008` test files, `18` getter definitions, `4` candidate-like definitions, `14` holds |
| Selected candidate impact | `get_tradingview_service`: LOW, impacted count `1`, affected processes `0` |
| Selected candidate context | getter lazily initializes `_tradingview_service`; direct graph caller is `install_tradingview_service`; no process participation |

## Boundary

This packet makes no source, test, route/API, OpenAPI, PM2, frontend, OpenSpec,
or issue-label changes.

## Next Gate

Human review / PR merge decision for this G2.101 governance packet.

If accepted, create G2.102 as a TradingView getter-retirement authorization
packet before any source edit.
