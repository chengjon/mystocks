# Backend Email Service Lifecycle DI Implementation - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-ready-for-review
- Workline: G2.3 service lifecycle DI implementation
- Candidate: `web/backend/app/services/email_service.py`
- Base HEAD: `6e92dd2942057b2763a4074abc102b761c2b2d76`
- Branch: `g2-3-email-service-di-implementation`
- Prepared at: `2026-05-22T16:05:40+08:00`

This implementation executes the G2.2 authorization package accepted through PR
`#141`. It keeps the scope limited to `email_service.py`, its six
`notification.py` consumers, focused tests, this report, and the PR task card.

## Authorization Boundary

Authorized by:

- PR `#141`: `docs: prepare email service DI authorization`
- `docs/reports/quality/backend-email-service-lifecycle-di-implementation-authorization-2026-05-22.md`

This implementation does not modify:

- `web/backend/app/services/email_notification_service.py`
- strategy, tdx, stock-search, monitoring, or technical-analysis services
- frontend source
- generated clients
- `docs/api/`
- OpenSpec changes/specs
- route paths, HTTP methods, response contracts, or OpenAPI exposure behavior
- PM2/runtime scripts or process state

## GitNexus Pre-Edit Gate

Fresh impact checks before source edits:

| Symbol | File | Risk | Direct callers | Affected processes |
|---|---|---:|---:|---:|
| `EmailService` | `web/backend/app/services/email_service.py` | LOW | 0 | 0 |
| `get_email_service` | `web/backend/app/services/email_service.py` | MEDIUM | 6 | 0 |

The six direct callers were all in `web/backend/app/api/notification.py` and
were the only route consumers migrated in this batch.

## Implementation Summary

`web/backend/app/services/email_service.py`:

- adds `EMAIL_SERVICE_STATE_KEY`
- keeps `get_email_service()` as the compatibility getter
- adds `install_email_service(app, service=None)`
- adds `get_email_service_dependency(request)`
- uses `app.state` as the FastAPI lifecycle holder and lazily installs the
  compatibility singleton when no app-state service exists

`web/backend/app/api/notification.py`:

- imports `EmailService` and `get_email_service_dependency`
- injects `email_service: EmailService = Depends(get_email_service_dependency)`
  into all six email routes
- removes route-body calls to `get_email_service()`
- preserves existing route paths, request bodies, response payload shapes,
  permission checks, and background task behavior

Tests:

- adds `web/backend/tests/test_email_service_lifecycle_di.py`
- updates `web/backend/tests/test_notification_logging.py` to pass fake service
  instances through the route function parameter instead of monkeypatching the
  compatibility getter

## Route Consumer Closure

| Route-local path | Function | New access path | Notes |
|---|---|---|---|
| `GET /status` | `get_email_service_status` | injected `EmailService` | status behavior unchanged |
| `POST /email/send` | `send_email` | injected `EmailService` | background task captures injected service |
| `POST /email/welcome` | `send_welcome_email` | injected `EmailService` | background task captures injected service |
| `POST /email/newsletter` | `send_daily_newsletter` | injected `EmailService` | logging assertions retained |
| `POST /email/price-alert` | `send_price_alert` | injected `EmailService` | logging assertions retained |
| `POST /test-email` | `send_test_email` | injected `EmailService` | immediate send behavior unchanged |

## TDD Evidence

Red run:

```text
python -m pytest web/backend/tests/test_email_service_lifecycle_di.py -q -n 0 --tb=short --no-cov
3 failed
```

Expected failures:

- `get_email_service_dependency` did not exist
- notification route signatures did not accept `email_service`
- `send_test_email(..., email_service=fake)` rejected the injected service

Green run:

```text
python -m pytest web/backend/tests/test_email_service_lifecycle_di.py web/backend/tests/test_notification_logging.py -q -n 0 --tb=short --no-cov
6 passed in 1.35s
```

## Verification

| Gate | Result | Notes |
|---|---|---|
| Focused pytest | passed | `6 passed in 1.35s` |
| Ruff touched files | passed | `All checks passed!` |
| `app.main` import smoke | passed | placeholder env produced `app.main import ok` |
| OpenSpec changes | not touched | no proposal/spec/task edits |
| PM2/runtime | not touched | no service start/stop/recreate |

The first `app.main` import smoke failed only because placeholder environment
variables were incomplete. After adding required placeholder values for
`POSTGRESQL_HOST`, `POSTGRESQL_USER`, `POSTGRESQL_PASSWORD`, `BACKEND_PORT`, and
`BACKEND_BACKUP_PORT`, import returned status `0` and printed
`app.main import ok`. Existing noisy import-time warnings included mock-data
fallback and GPU dependency version warnings; they are not introduced by this
batch.

## Rollback

Rollback is path-limited:

1. Restore direct `get_email_service()` calls inside the six notification route
   bodies.
2. Remove `EMAIL_SERVICE_STATE_KEY`, `install_email_service`, and
   `get_email_service_dependency` as one unit.
3. Remove `test_email_service_lifecycle_di.py`.
4. Restore `test_notification_logging.py` monkeypatches if the route functions
   no longer accept injected services.
5. Do not modify `email_notification_service.py`.

## Next Gate

Review this implementation PR. If accepted, merge as the first `email_service.py`
service lifecycle DI implementation batch under issue `#79`. Do not generalize
this pattern to additional service files until a separate candidate packet and
approval exist.
