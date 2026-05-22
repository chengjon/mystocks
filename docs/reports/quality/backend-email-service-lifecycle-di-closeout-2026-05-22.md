# Backend Email Service Lifecycle DI Closeout - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: completed-and-recorded
- Workline: G2.3 service lifecycle DI implementation closeout
- Completed pilot: `web/backend/app/services/email_service.py`
- Merge commit: `20657e6e86a3423b15c67b6a8d6e165fbaa47b72`
- PR: https://github.com/chengjon/mystocks/pull/142
- Recorded at: `2026-05-22`

## Decision

The human maintainer approved PR `#142` after the G2.2 authorization package
was merged by PR `#141`. PR `#142` was merged and is now the completed first
service lifecycle DI source pilot under issue `#79`.

This closeout records completion only. It does not authorize another service
lifecycle migration, OpenSpec proposal, issue label change, or movement of issue
`#79` / `#92` to `ready-for-agent`.

## Completed Scope

Merged files from PR `#142`:

- `web/backend/app/services/email_service.py`
- `web/backend/app/api/notification.py`
- `web/backend/tests/test_email_service_lifecycle_di.py`
- `web/backend/tests/test_notification_logging.py`
- `docs/reports/quality/backend-email-service-lifecycle-di-implementation-2026-05-22.md`
- `governance/mainline/task-cards/pr-142.yaml`

## Functional Result

`email_service.py` now provides:

- retained compatibility getter: `get_email_service()`
- app-state key: `EMAIL_SERVICE_STATE_KEY`
- installer: `install_email_service(app, service=None)`
- FastAPI dependency provider: `get_email_service_dependency(request)`

The six notification email routes now receive an injected `EmailService`:

- `get_email_service_status`
- `send_email`
- `send_welcome_email`
- `send_daily_newsletter`
- `send_price_alert`
- `send_test_email`

The implementation intentionally preserved route paths, HTTP methods, request
models, response payload shape, OpenAPI exposure, and background-task behavior.

## Preserved Boundaries

The following remained untouched:

- `web/backend/app/services/email_notification_service.py`
- other service singleton candidates
- frontend source
- generated clients
- `docs/api/`
- OpenSpec changes/specs
- PM2/runtime scripts or process state

## Verification Summary

Local verification before PR publication:

| Gate | Result |
|---|---|
| TDD red | observed missing provider/signature/injection failures before implementation |
| Focused pytest | `6 passed` |
| Ruff touched files | passed |
| Markdown governance | `checked_files=1`, `errors=0` |
| Mainline scope gate | `pass=True` |
| GitNexus staged detect_changes | `risk_level=medium`; hunk review confirmed authorized scope |
| `app.main` import smoke | status `0`, `app.main import ok` with placeholder env |

GitHub PR checks before merge:

- `check-compliance`: success
- `Mainline Governance Gate`: success
- `Validate API Contracts`: success
- `Generate TypeScript Types`: success
- `Detect Breaking Changes`: success or skipped duplicate
- contract validation report: success

## Current Issue State

At closeout recording time:

- issue `#79`: `OPEN`, labels `needs-triage`
- issue `#92`: `OPEN`, labels `enhancement`, `ready-for-downstream`,
  `ready-for-human`

This closeout does not change either issue's label or state.

## Next Gate

Before any second service lifecycle DI candidate is selected, create a separate
candidate/authorization packet with:

- candidate file path and same-name collision review
- current-head GitNexus impact
- exact write scope
- tests and rollback plan
- explicit human approval

Do not generalize the `email_service.py` implementation to additional services
from this closeout alone.
