# Backend Next High-Risk Service Getter Track Selection

Date: 2026-05-26  
Task: G2.155 next high-risk service getter track selection  
Branch: `g2-155-next-high-risk-getter-track-selection`  
Base HEAD: `3beee4c192dd060dd5f54022cf30f0d3ea1d7294`  
Parent: G2.154, merged by PR `#307`

> **历史决策说明**: This report records a G2.155 governance decision only. It does not authorize backend source changes, backend test changes, route/API changes, OpenAPI exposure changes, frontend changes, PM2 workflow changes, OpenSpec changes, issue-state changes, compatibility wrapper deletion, or the G2.156 source implementation lane.

## Purpose

G2.154 closed the realtime/socket subtrack and returned control to the broader G2 high-risk service getter queue. G2.155 selects the next track from the remaining G2.143 tracks without opening a source implementation lane.

## Inputs

- `docs/reports/quality/backend-high-risk-service-getter-strategy-decision-2026-05-26.md`
- `docs/reports/quality/backend-realtime-socket-subtrack-closeout-2026-05-26.md`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- OpenSpec active list and spec list, checked on 2026-05-26; PostHog `ECONNREFUSED` remains telemetry noise

## Refreshed Track Evidence

| Track | Primary surface | Risk | Impact | Current disposition |
|---|---|---:|---:|---|
| Dashboard/TDX | `get_tdx_service` | CRITICAL | impacted 4, direct 2, processes 5 | Select next design/authorization track |
| Indicator/Data | `get_data_service` | CRITICAL | impacted 4, direct 3, processes 7 | Defer to later dedicated package |
| Strategy adapter | `get_strategy_service` | CRITICAL | impacted 11, direct 6, processes 0 | Defer to later dedicated package |
| Root facade compatibility | `web/backend/app/services/__init__.py` | locked | active compatibility surface | Keep locked; not a cleanup candidate |
| Route dependency/provider governance | FastAPI provider getters | locked | active route dependency contracts | Keep locked; not a singleton-retirement candidate |

Dashboard/TDX currently has the smallest direct caller count among the remaining CRITICAL implementation families. Its d=1 callers are concentrated in `web/backend/app/api/dashboard_data_source.py`:

- `_get_major_index_quotes`
- `_get_tdx_live_market_snapshot`

Current token scan:

| Token | Files | Hits | Main surfaces |
|---|---:|---:|---|
| `get_tdx_service` | 3 | 14 | `api/tdx.py`, `api/dashboard_data_source.py`, `services/tdx_service.py` |
| `get_data_service` | 5 | 10 | indicator cache, strategy indicators, system health, service provider |
| `get_strategy_service` | 5 | 27 | strategy adapters, strategy execution router, backtest task, service provider |

Route-provider surfaces remain active contracts:

- `get_market_data_service_v2_dependency`: 17 hits across 3 files
- `get_tdx_service_dependency`: 7 hits across 2 files
- `get_indicator_registry_dependency`: 4 hits across 2 files

## Decision

Select the Dashboard/TDX runtime seam as the next high-risk service getter track.

This selection is narrower than Indicator/Data and Strategy adapter:

- Dashboard/TDX has two direct callers, both dashboard helper functions.
- Prior TDX route/provider work exists, so the next package can focus on dashboard consumer contracts and fallback behavior.
- Indicator/Data crosses indicator cache, strategy indicators, system health, and strategy runtime helpers.
- Strategy adapter crosses adapter wrappers, strategy execution routes, and backtest task resolution.

## G2.156 Gate

The next package should be G2.156 Dashboard/TDX design and authorization.

Minimum requirements for G2.156:

- Refresh GitNexus impact for `get_tdx_service` and the dashboard helper callers.
- Produce a Dashboard/TDX consumer contract matrix for `_get_major_index_quotes`, `_get_tdx_live_market_snapshot`, and their dashboard summary callers.
- Document TDX unavailable/fallback behavior and the test-double strategy.
- Define allowed source and test paths before any implementation lane starts.
- Require focused dashboard/TDX route tests or import-safe smoke tests.
- Require route/OpenAPI drift check if the approved implementation touches route-level dependency contracts.
- Explicitly exclude Indicator/Data, Strategy adapter, root facade compatibility, and route dependency/provider governance from the first Dashboard/TDX implementation lane.

## Non-Goals

- No backend source or test edit.
- No route/API or OpenAPI change.
- No provider, getter, or compatibility wrapper deletion.
- No implementation authorization for G2.156 source changes.
- No GitHub issue label or state change.

## Next Gate

Review and merge this G2.155 decision package. If accepted, start G2.156 as a Dashboard/TDX design and authorization package before any Dashboard/TDX source implementation begins.
