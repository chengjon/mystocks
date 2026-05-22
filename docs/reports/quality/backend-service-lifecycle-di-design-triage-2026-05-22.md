# Backend Service Lifecycle DI Design Triage

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

Date: 2026-05-22
Status: design-triage-prepared-for-review
Branch: `g2-issue79-service-lifecycle-triage`
HEAD checked: `9be035fd895dac1d28cbb5d3c7195e81da8d87a1`
Generated at: 2026-05-22T11:47:21+08:00
Primary issue: `#79`
Closed prerequisite issue: `#78`
Parent issue: `#92`

## Purpose

This report starts issue `#79` service lifecycle DI design/triage after issue
`#78` was closed as reconciled governance evidence.

This is a design and triage packet only. It does not create an implementation
issue, does not create or modify an OpenSpec proposal, does not change issue
labels, and does not authorize backend source, tests, route, OpenAPI, docs/API,
runtime, PM2, script, config, or generated-client changes.

## Current Issue State

| Issue | State | Labels | Role |
|---|---|---|---|
| `#78` | `CLOSED` | `needs-triage` | Adapter lifecycle DI prerequisite reconciled and closed |
| `#79` | `OPEN` | `needs-triage` | Service lifecycle DI design/triage lane |
| `#92` | `OPEN` | `enhancement`, `ready-for-downstream`, `ready-for-human` | Parent downstream decision index |

## Current-HEAD Scan Summary

Current scan scope:

- Directory: `web/backend/app/services`
- Service files scanned: 152
- HEAD: `9be035fd895dac1d28cbb5d3c7195e81da8d87a1`

The broad singleton/getter heuristic matched 104 files, but that is not an
implementation backlog. It intentionally overcounts ordinary business getters,
factory helpers, external-client wrappers, cache/task services, and
DB/session-backed services. Use the narrower signals below for decision-making.

| Signal | Count | Notes |
|---|---:|---|
| `_instance = None` | 4 | Strongest legacy singleton signal |
| `def get_*service(...)` | 16 | Candidate service getter or compatibility accessor |
| `def get_*_dependency(...)` | 1 | Existing FastAPI dependency-provider pattern |
| `app.state` / `request.app.state` | 1 | Existing app-state lifecycle pattern |
| `@lru_cache` / cache decorator | 4 | Needs per-file statefulness review |
| Current route-level DI pilot | 1 | `TechnicalPatternDetectionService` from D2.1a |

The old `module_service_singleton` broad rule is rejected for this packet as a
decision signal because it overmatched every service file in the current scan.

## Narrow Candidate Inventory

### `_instance = None` Targets

| File | Initial classification | Disposition |
|---|---|---|
| `web/backend/app/services/strategy_service.py` | external-client / DB-session backed / process-level singleton signals | Do not migrate without impact analysis and route/service owner selection |
| `web/backend/app/services/tdx_service.py` | external-client / process-level singleton signals | Do not migrate without adapter/client ownership review |
| `web/backend/app/services/monitoring_service.py` | DB/session, cache/task, process-level singleton signals; large file | Exclude from first pilot; needs separate monitoring lifecycle design |
| `web/backend/app/services/technical_analysis_service.py` | external-client, cache/task, analytics, process-level signals; large file | Exclude from first pilot; needs data-source and cache boundary review |

### Existing Provider/App-State Pattern

| File | Evidence | Disposition |
|---|---|---|
| `web/backend/app/services/tradingview_widget_service.py` | `get_tradingview_service`, `get_tradingview_service_dependency`, app-state signal | Treat as reference evidence for service lifecycle pattern, not as proof that all service lifecycle work is complete |

### Completed Route-Level Pilot

| File | Evidence | Disposition |
|---|---|---|
| `web/backend/app/services/technical_pattern_detection_service.py` | D2.1a route-level DI pilot exists; service file uses cache decorator | Treat as completed pilot evidence; do not reopen unless current-head tests contradict the D2.1a report |

### Service Getter Surface

The current scan found 16 files with `get_*service(...)` functions:

- `web/backend/app/services/__init__.py`
- `web/backend/app/services/advanced_analysis_service.py`
- `web/backend/app/services/announcement_service.py`
- `web/backend/app/services/data_service.py`
- `web/backend/app/services/data_service_enhanced.py`
- `web/backend/app/services/email_notification_service.py`
- `web/backend/app/services/email_service.py`
- `web/backend/app/services/market_data_service/get_market_data_service.py`
- `web/backend/app/services/realtime_streaming_service.py`
- `web/backend/app/services/stock_search_service/stock_search_service.py`
- `web/backend/app/services/strategy_service.py`
- `web/backend/app/services/tdx_service.py`
- `web/backend/app/services/tradingview_widget_service.py`
- `web/backend/app/services/unified_data_service.py`
- `web/backend/app/services/watchlist_service.py`
- `web/backend/app/services/wencai_service.py`

These files must be classified before implementation as:

- existing compatibility getter retained
- route-level provider candidate
- app-level lifecycle provider candidate
- factory/integration point that should remain centralized
- DB/session-backed service requiring session injection design
- external-client wrapper requiring client ownership design
- cache/task/process singleton intentionally retained
- false positive or out-of-scope

## Recommended G2 Decision

Recommended review outcome for this packet:

1. Accept that issue `#78` is closed and issue `#79` may begin design/triage.
2. Keep issue `#79` in `needs-triage`; do not move it to `ready-for-agent`.
3. Do not open implementation from the broad 104-file heuristic.
4. Use a narrower candidate classification packet before any code edits.
5. Treat `tradingview_widget_service.py` and
   `technical_pattern_detection_service.py` as reference evidence, not automatic
   next implementation targets.
6. Exclude `monitoring_service.py` and `technical_analysis_service.py` from the
   first service lifecycle implementation pilot because they are large,
   stateful, and cross-cutting.

## Required Next Packet

The next packet should be a service lifecycle candidate classification and
pilot authorization packet. It must include:

- selected candidate or explicit no-pilot decision
- exact write scope
- caller and route consumer matrix
- interface/test-double strategy
- dependency override plan
- app-state or route-level lifecycle choice
- rollback plan
- GitNexus impact before source edits
- focused test plan

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

Structured design/triage evidence is recorded in:

`.planning/codebase/generated/service-lifecycle-di-design-triage-2026-05-22.json`
