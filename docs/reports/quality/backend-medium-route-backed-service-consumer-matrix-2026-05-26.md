# Backend Medium Route-Backed Service Consumer Matrix - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.116 medium route-backed exact consumer matrix
Status: ready for review

## Purpose

Build the exact consumer matrix requested by G2.115 for the remaining medium
route-backed service getter candidates:

- `get_announcement_service`
- `get_email_service`
- `get_watchlist_service`

This is an evidence-only matrix. It does not modify backend source, tests,
route/API contracts, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec
changes, GitHub issue labels, or service implementation logic.

## Parent Gate

| Gate | Result |
|---|---|
| Parent strategy packet | G2.115 accepted in PR `#268` |
| Parent merge commit | `dabe473f5d2616cfeda6c41ceeecee1bc5c57fb6` |
| Current matrix base | `dabe473f5d2616cfeda6c41ceeecee1bc5c57fb6` |

## Matrix

| Candidate | Direct getter refs | Dependency refs | Adapter refs | Tests | Decision |
|---|---:|---:|---:|---:|---|
| `get_announcement_service` | `3 refs / 2 files`: service definition, installer fallback, lifecycle test monkeypatch | `14 refs / 3 files`; 11 route handlers in `announcement/routes.py` use `Depends(get_announcement_service_dependency)` | `0` | `test_announcement_service_lifecycle_di.py` | Select as next authorization-candidate packet only |
| `get_email_service` | `6 refs / 4 files`: service definition, installer fallback, tests / fake modules | `11 refs / 4 files`; 6 notification endpoints use `Depends(get_email_service_dependency)` | `0` | `test_email_service_lifecycle_di.py`, `test_notification_logging.py`, email-notification retirement assertion | Hold behind announcement to avoid overlapping email-service lane churn |
| `get_watchlist_service` | `8 refs / 5 files`: service definition, installer fallback, adapters, tests | `10 refs / 3 files`; 7 watchlist handlers use `Depends(get_watchlist_service_dependency)` | `4 refs / 2 files`: `services/adapters/watchlist_adapter.py`, `services/data_adapters/watchlist.py` | `test_watchlist_service_lifecycle_di.py`, `test_watchlist_helper_lifecycle_di.py` | Hold until adapter consumer ownership is planned |

## Decision

Select `web/backend/app/services/announcement_service.py:get_announcement_service`
as the next authorization-candidate packet.

This matrix does not authorize implementation. The next packet should be a
G2.117 authorization-only packet that explicitly preserves:

- `AnnouncementService`
- `install_announcement_service`
- `get_announcement_service_dependency`
- announcement route contracts and OpenAPI exposure
- existing announcement route dependency injection

The future implementation, if separately approved, should be limited to retiring
the service module singleton/getter fallback surface and updating focused tests.

## Boundary

This PR does not:

- modify backend source or tests
- authorize source edits
- delete any getter
- modify route paths, response models, response shapes, or OpenAPI exposure
- modify frontend code
- modify PM2 workflows
- create or modify OpenSpec proposals/specs
- change GitHub issue labels or readiness state

## Next Gate

Human review / PR merge decision for G2.116.

If accepted, create G2.117 AnnouncementService getter-retirement authorization
before any announcement service source edit.
