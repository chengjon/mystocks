# Backend Service Lifecycle DI Candidate Classification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

Date: 2026-05-22
Status: candidate-classification-prepared-for-review
Branch: `g2-issue79-candidate-classification`
HEAD checked: `ecc391393dbbba8b961fb351c94cc4a1ad82be95`
Generated at: 2026-05-22T12:04:41+08:00
Primary issue: `#79`
Parent issue: `#92`

## Purpose

This report classifies issue `#79` service lifecycle DI candidates after the G2
design/triage packet and selects the next candidate for a future implementation
authorization packet.

This is still governance and design evidence only. It does not create an
implementation issue, does not create or modify an OpenSpec proposal, does not
change issue labels, and does not authorize backend source, tests, route,
OpenAPI, docs/API, runtime, PM2, script, config, or generated-client changes.

## Input State

| Input | State | Evidence |
|---|---|---|
| Issue `#78` | `CLOSED` | Adapter lifecycle DI prerequisite closed as reconciled governance evidence |
| Issue `#79` | `OPEN`, `needs-triage` | Service lifecycle DI lane |
| Issue `#92` | `OPEN`, `ready-for-downstream`, `ready-for-human` | Parent downstream decision index |
| G2 design/triage | Merged | PR `#139`, `ecc391393dbbba8b961fb351c94cc4a1ad82be95` |

## Corrected Candidate Inventory

The previous G2 design/triage packet intentionally used narrow signals but
counted only `_instance = None`. G2.1 adds a broader and more accurate
module-level singleton variable pattern:

`_[name]_(service|manager|registry|client|provider|instance|adapter)* = None`

Current corrected count:

- service files scanned: 152
- module-level singleton variable files: 21
- service getter files from the prior packet: 16
- existing provider/app-state pattern: 1
- completed route-level DI pilot: 1

The 21 module-level singleton variable files are classification input, not an
implementation backlog.

## Candidate Classification

| Class | Candidate files | Disposition |
|---|---:|---|
| Already has provider/app-state pattern | `tradingview_widget_service.py` | Reference evidence; do not reopen as first new implementation pilot |
| Completed route-level DI pilot | `technical_pattern_detection_service.py` | Completed D2.1a evidence; do not reopen without current-head contradiction |
| Recommended first future pilot | `email_service.py` | Suitable for a separate implementation authorization packet |
| Name-collision / disambiguation required | `email_notification_service.py` | Do not include in the first pilot unless explicitly scoped; it also defines `get_email_service` |
| Critical or broad route impact | `strategy_service.py`, `tdx_service.py`, `stock_search_service.py` | Exclude from first pilot |
| Large or cross-cutting stateful service | `monitoring_service.py`, `technical_analysis_service.py` | Exclude from first pilot |
| Domain-heavy medium candidates | `announcement_service.py`, `watchlist_service.py` | Defer until after a smaller pilot proves the pattern |
| Real-time / room / streaming state | `realtime_streaming_service.py`, `room_socketio_adapter.py`, `room_management.py`, `room_permission_service.py` | Requires separate lifecycle/connection-state design |
| Central data/integration services | `data_service.py`, `data_service_enhanced.py`, `market_data_service_v2.py`, `unified_data_service.py`, `multi_source_manager.py` | Requires separate data-boundary design before DI migration |

## GitNexus Impact Evidence

| Symbol | File | Risk | Direct callers | Processes affected | Disposition |
|---|---|---:|---:|---:|---|
| `TradingViewWidgetService` | `tradingview_widget_service.py` | LOW | 0 | 0 | Reference only; pattern already exists |
| `get_tradingview_service` | `tradingview_widget_service.py` | LOW | 1 | 0 | Reference only; route already uses dependency provider |
| `get_tradingview_service_dependency` | `tradingview_widget_service.py` | LOW | 0 | 0 | Reference provider pattern |
| `EmailService` | `email_service.py` | LOW | 0 | 0 | Candidate service class |
| `get_email_service` | `email_service.py` | MEDIUM | 6 | 0 | Recommended first future pilot with exact scope |
| `get_announcement_service` | `announcement_service.py` | MEDIUM | 11 | 0 | Defer; broader domain route surface |
| `get_watchlist_service` | `watchlist_service.py` | MEDIUM | 9 | 0 | Defer; adapter and route consumers |
| `get_strategy_service` | `strategy_service.py` | CRITICAL | 6 | 0 | Exclude from first pilot |
| `get_tdx_service` | `tdx_service.py` | CRITICAL | 2 | 5 | Exclude from first pilot |
| `get_stock_search_service` | `stock_search_service.py` | CRITICAL | 6 | 11 | Exclude from first pilot |

## Recommended First Future Pilot

Select `web/backend/app/services/email_service.py` as the first future service
lifecycle implementation candidate, but do not implement it in this packet.

Reasons:

- `EmailService` class impact is LOW with 0 affected symbols/processes.
- `get_email_service` impact is MEDIUM with 6 direct route callers and 0
  affected processes.
- Direct route surface is concentrated in `web/backend/app/api/notification.py`.
- Existing notification logging tests already patch `get_email_service`, which
  gives a concrete test seam for dependency override conversion.
- The service is small enough to review as a pilot and is less cross-cutting
  than strategy, market data, watchlist, announcement, monitoring, or technical
  analysis services.

Important disambiguation:

- `web/backend/app/services/email_service.py` and
  `web/backend/app/services/email_notification_service.py` both define
  `get_email_service`.
- A future implementation packet must target the `email_service.py` symbol by
  file path and must not modify `email_notification_service.py` unless that file
  is explicitly added to scope.

## Future Implementation Authorization Scope

If this classification is accepted, the next packet may request a separate
G2.2 implementation authorization with this exact proposed write scope:

- `web/backend/app/services/email_service.py`
- `web/backend/app/api/notification.py`
- `web/backend/tests/test_notification_logging.py`
- `web/backend/tests/test_email_service_lifecycle_di.py`
- one future `governance/mainline/task-cards/pr-*.yaml`
- one future implementation report under `docs/reports/quality/`

Expected implementation shape for that future packet:

- retain `get_email_service()` as a compatibility getter
- add a FastAPI dependency provider for route injection
- route notification endpoints through `Depends(...)`
- keep SMTP behavior unchanged
- use dependency override or monkeypatch tests with a fake email service
- avoid `email_notification_service.py`
- avoid PM2, OpenAPI, generated-client, frontend, docs/API, and broader route
  changes

## Required Future Gates

Before source edits in any G2.2 packet:

- run GitNexus impact for `EmailService` and the exact `get_email_service`
  symbol in `web/backend/app/services/email_service.py`
- prove the write scope is still current at HEAD
- include a route consumer matrix for `notification.py`
- include a dependency override test plan
- include rollback instructions that restore direct `get_email_service()` calls
- run staged `gitnexus_detect_changes(scope="staged")` before commit

## Non-Authorization

This packet does not authorize:

- backend source, frontend source, test, generated client, docs/API, route,
  OpenAPI, probe URL, script, config, runtime, or PM2 changes
- issue label changes
- creating implementation issues
- moving issue `#79` or `#92` to `ready-for-agent`
- creating or modifying OpenSpec proposals
- migrating service singletons

## Evidence Artifact

Structured candidate classification evidence is recorded in:

`.planning/codebase/generated/service-lifecycle-di-candidate-classification-2026-05-22.json`
