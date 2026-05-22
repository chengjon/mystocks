# Backend Announcement Service Lifecycle DI Closeout - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: completed-and-recorded
- Workline: G2.7 service lifecycle DI implementation closeout
- Completed pilot: `web/backend/app/services/announcement_service.py`
- Implementation PR: https://github.com/chengjon/mystocks/pull/146
- Implementation merge commit: `517f47cb86aa32d32514d8588a653b08898f72c7`
- Closeout branch: `g2-7-announcement-service-di-closeout`
- Recorded at: `2026-05-22T19:23:37+08:00`

## Decision

The human maintainer approved PR `#146` after the G2.6 implementation review.
PR `#146` was merged into `wip/root-dirty-20260403` at
`517f47cb86aa32d32514d8588a653b08898f72c7`.

This closeout records the completed second service lifecycle DI pilot. It does
not authorize a third service lifecycle DI candidate.

## Completed Scope

PR `#146` completed the exact G2.5 authorized implementation scope:

- `web/backend/app/services/announcement_service.py`
- `web/backend/app/api/announcement/routes.py`
- `web/backend/tests/test_announcement_service_lifecycle_di.py`
- `docs/reports/quality/backend-announcement-service-lifecycle-di-implementation-2026-05-22.md`
- `governance/mainline/task-cards/pr-146.yaml`

## Functional Result

`announcement_service.py` now follows the same lifecycle DI pattern as the
earlier `email_service.py` pilot:

- `get_announcement_service()` remains as the compatibility getter.
- `ANNOUNCEMENT_SERVICE_STATE_KEY` is defined.
- `install_announcement_service(...)` installs an `AnnouncementService` into
  `app.state`.
- `get_announcement_service_dependency(...)` reads from `app.state` and lazily
  installs the compatibility singleton when needed.

The 11 announcement route handlers now receive `AnnouncementService` through
FastAPI dependency injection:

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

Post-merge shape check:

| Check | Result |
|---|---:|
| Direct `get_announcement_service()` calls in `announcement/routes.py` | 0 |
| Route dependency parameters | 11 |
| Compatibility getter retained | yes |
| `ANNOUNCEMENT_SERVICE_STATE_KEY` present | yes |
| `install_announcement_service` present | yes |
| `get_announcement_service_dependency` present | yes |

## Preserved Boundaries

PR `#146` did not modify:

- `web/backend/app/services/watchlist_service.py`
- `web/backend/app/services/data_adapters/watchlist.py`
- `web/backend/app/services/adapters/watchlist_adapter.py`
- `web/backend/app/services/email_service.py`
- `web/backend/app/services/email_notification_service.py`
- `docs/api/`
- generated clients
- OpenSpec proposal/spec files
- frontend files
- PM2 scripts or runtime process configuration
- issue labels

## Verification Summary

Post-merge focused pytest:

```bash
env PYTHONPATH=web/backend pytest -q -n 0 --tb=short --no-cov \
  web/backend/tests/test_announcement_service_lifecycle_di.py \
  web/backend/tests/test_announcement_routes_regressions.py
```

Result: `4 passed`.

Post-merge ruff:

```bash
ruff check \
  web/backend/app/services/announcement_service.py \
  web/backend/app/api/announcement/routes.py \
  web/backend/tests/test_announcement_service_lifecycle_di.py \
  web/backend/tests/test_announcement_routes_regressions.py
```

Result: `All checks passed!`

Post-merge import smoke:

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

PR `#146` implementation verification also recorded:

- Pre-edit GitNexus: `AnnouncementService` LOW, `get_announcement_service`
  MEDIUM with 11 direct route callers and 0 affected processes.
- TDD RED observed before implementation.
- Focused pytest passed.
- Ruff passed.
- Import smoke passed.
- Markdown governance passed.
- Mainline scope gate passed.
- GitNexus staged `detect_changes` reported low risk and no affected
  processes.

## Remaining Gate

Do not start a third service lifecycle DI candidate from issue `#79` until this
closeout PR is reviewed and accepted.

If accepted, the next service lifecycle lane should begin again at candidate
selection or authorization, not implementation.
