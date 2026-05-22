# Backend Announcement Service Lifecycle DI Implementation - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-prepared-for-review
- Workline: G2.6 announcement service lifecycle DI implementation
- Authorization packet: `backend-announcement-service-lifecycle-di-implementation-authorization-2026-05-22.md`
- Authorization merge: PR `#145`, `e9d674c01edc5e701a0b3eca80b05f62dfc4986f`
- Implementation branch: `g2-6-announcement-service-di-implementation`
- Current HEAD before implementation: `e9d674c01edc5e701a0b3eca80b05f62dfc4986f`

## Authorization Boundary

This implementation stays inside the G2.5 allowed write scope:

- `web/backend/app/services/announcement_service.py`
- `web/backend/app/api/announcement/routes.py`
- `web/backend/tests/test_announcement_service_lifecycle_di.py`
- `docs/reports/quality/backend-announcement-service-lifecycle-di-implementation-2026-05-22.md`
- `governance/mainline/task-cards/pr-146.yaml`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`

No `watchlist_service.py`, adapter/data-layer file, frontend file, `docs/api/`
file, generated client, OpenSpec proposal/spec, PM2 script, runtime process
configuration, or issue label was changed.

## GitNexus Pre-Edit Gate

Pre-edit impact was run before source changes:

| Symbol | Risk | Direct callers | Processes affected | Result |
|---|---:|---:|---:|---|
| `AnnouncementService` | LOW | 0 | 0 | safe to proceed |
| `get_announcement_service` | MEDIUM | 11 | 0 | allowed by G2.5; all direct callers are announcement routes |

No HIGH or CRITICAL risk was reported.

## TDD Evidence

RED command:

```bash
env PYTHONPATH=web/backend pytest -q -n 0 --tb=short --no-cov \
  web/backend/tests/test_announcement_service_lifecycle_di.py
```

Expected and observed RED failures:

- `get_announcement_service_dependency` did not exist
- announcement route signatures did not include `service`
- `fetch_announcements(..., service=fake_service)` rejected the injected service

GREEN command:

```bash
env PYTHONPATH=web/backend pytest -q -n 0 --tb=short --no-cov \
  web/backend/tests/test_announcement_service_lifecycle_di.py
```

Observed result: `3 passed`.

## Implementation Summary

### `announcement_service.py`

The service now keeps the compatibility singleton getter and adds the app-state
provider seam:

- `ANNOUNCEMENT_SERVICE_STATE_KEY`
- `install_announcement_service(app, service=None)`
- `get_announcement_service_dependency(request)`

The existing `get_announcement_service()` compatibility getter remains in place
for non-route callers.

### `announcement/routes.py`

The route module now imports:

- `Depends`
- `AnnouncementService`
- `get_announcement_service_dependency`

The 11 direct route callers now accept injected `AnnouncementService`:

- `fetch_announcements`
- `get_announcements`
- `get_today_announcements`
- `get_important_announcements`
- `get_announcement_stats`
- `get_monitor_rules`
- `create_monitor_rule`
- `update_monitor_rule`
- `delete_monitor_rule`
- `get_triggered_records`
- `evaluate_monitor_rules`

Implementation shape check:

- Direct `get_announcement_service()` calls left in `announcement/routes.py`: `0`
- Route dependency parameters added: `11`
- Compatibility getter retained in service: yes

### Tests

`web/backend/tests/test_announcement_service_lifecycle_di.py` verifies:

- app-state installation through `get_announcement_service_dependency`
- every converted route exposes a `service` parameter
- `fetch_announcements` uses an injected fake service

Existing `web/backend/tests/test_announcement_routes_regressions.py` remains
unchanged and passing.

## Verification

Focused pytest:

```bash
env PYTHONPATH=web/backend pytest -q -n 0 --tb=short --no-cov \
  web/backend/tests/test_announcement_service_lifecycle_di.py \
  web/backend/tests/test_announcement_routes_regressions.py
```

Result: `4 passed`.

Ruff:

```bash
ruff check \
  web/backend/app/services/announcement_service.py \
  web/backend/app/api/announcement/routes.py \
  web/backend/tests/test_announcement_service_lifecycle_di.py \
  web/backend/tests/test_announcement_routes_regressions.py
```

Result: `All checks passed!`

Import smoke:

```bash
env PYTHONPATH=web/backend python - <<'PY'
from app.services.announcement_service import (
    AnnouncementService,
    get_announcement_service,
    get_announcement_service_dependency,
    install_announcement_service,
)
from app.api.announcement import routes

print("announcement service DI import smoke passed")
PY
```

Result: `announcement service DI import smoke passed`.

Staged GitNexus scope check:

```text
scope=staged, risk_level=low, changed_files=6, changed_count=30,
affected_count=0, affected_processes=[]
```

## Not Executed

The following broader gates were not executed because this is a narrow
route-level service lifecycle DI implementation:

- full backend pytest
- PM2 stateful workflow
- route/OpenAPI drift generation
- generated client rebuild
- frontend tests

## Rollback

Rollback is straightforward:

1. Remove `ANNOUNCEMENT_SERVICE_STATE_KEY`, `install_announcement_service`, and
   `get_announcement_service_dependency`.
2. Restore the 11 route-body `get_announcement_service()` calls.
3. Remove `service: AnnouncementService = Depends(...)` route parameters.
4. Remove `test_announcement_service_lifecycle_di.py`.

The compatibility getter was not removed, so non-route rollback risk is low.

## Next Gate

Human review of this implementation PR.

If merged, create a separate closeout record that updates the steward tree from
`announcement-service-di-implementation-prepared-for-review` to merged and
recorded. Do not start a third service lifecycle DI candidate until that closeout
is accepted.
