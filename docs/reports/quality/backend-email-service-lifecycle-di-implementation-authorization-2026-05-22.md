# Backend Email Service Lifecycle DI Implementation Authorization - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-authorization-prepared-for-review
- Workline: G2.2 service lifecycle DI authorization
- Candidate: `web/backend/app/services/email_service.py`
- Current HEAD: `0b5e393e2ff1e5da465d26b338d083a6023faf9b`
- Prepared at: `2026-05-22T15:33:04+08:00`
- Source edits in this package: none

This package converts the accepted G2.1 candidate classification into a
reviewable implementation authorization packet for `email_service.py`. It does
not execute the implementation and does not move issue `#79` or `#92` into an
implementation-ready state.

## Governance Boundary

The human maintainer approved PR `#140` and accepted `email_service.py` as the
first service lifecycle DI implementation candidate. This G2.2 package only
defines the future implementation scope, tests, rollback plan, and pre-edit risk
checks.

This package does not authorize:

- backend source edits
- frontend source edits
- test edits
- generated client edits
- `docs/api/` edits
- OpenSpec proposal or spec creation
- issue label changes
- moving issue `#79` or `#92` to `ready-for-agent`
- PM2 command execution, service restart, process deletion, or process
  recreation

## Current Issue State

| Issue | State | Labels | Role |
|---|---|---|---|
| `#78` | closed | `needs-triage` | adapter lifecycle DI prerequisite, reconciled by PR `#138` |
| `#79` | open | `needs-triage` | service lifecycle DI parent lane |
| `#92` | open | `enhancement`, `ready-for-downstream`, `ready-for-human` | downstream decision audit trail |

## Evidence Inputs

| Evidence | Role |
|---|---|
| `docs/reports/quality/backend-adapter-lifecycle-di-closeout-acceptance-2026-05-22.md` | confirms adapter prerequisite `#78` is closed |
| `docs/reports/quality/backend-service-lifecycle-di-design-triage-2026-05-22.md` | defines service lifecycle DI triage and candidate strategy |
| `docs/reports/quality/backend-service-lifecycle-di-candidate-classification-2026-05-22.md` | selects `email_service.py` as first future implementation candidate |
| `.planning/codebase/generated/service-lifecycle-di-candidate-classification-2026-05-22.json` | machine-readable G2.1 candidate classification |
| `web/backend/app/services/tradingview_widget_service.py` | reference provider/app-state pattern from completed pilot evidence |

## Candidate Facts

`web/backend/app/services/email_service.py` contains the candidate singleton:

- `class EmailService` starts at line `18`
- module-level `_email_service = None` at line `319`
- compatibility getter `get_email_service()` starts at line `322`
- the getter lazily creates `EmailService()` and returns the cached instance
- `EmailService.__init__` reads SMTP environment configuration and logs when
  `SMTP_USERNAME` / `SMTP_PASSWORD` are absent

Path disambiguation is mandatory because
`web/backend/app/services/email_notification_service.py` also defines a separate
`_email_service` and `get_email_service()` for `EmailNotificationService`.

## GitNexus Risk Snapshot

| Symbol | File | Risk | Direct callers | Processes affected | Disposition |
|---|---|---:|---:|---:|---|
| `EmailService` | `web/backend/app/services/email_service.py` | LOW | 0 | 0 | service class candidate |
| `get_email_service` | `web/backend/app/services/email_service.py` | MEDIUM | 6 | 0 | compatibility getter and route seam |

The six direct callers of the file-disambiguated `get_email_service` are all in
`web/backend/app/api/notification.py`:

- `get_email_service_status`
- `send_email`
- `send_welcome_email`
- `send_daily_newsletter`
- `send_price_alert`
- `send_test_email`

Future implementation must rerun GitNexus impact on `EmailService` and the
file-disambiguated `get_email_service` before editing any source file. If either
impact becomes HIGH or CRITICAL, implementation must stop and return to review.

## Future Allowed Write Scope

If this authorization package is explicitly accepted in a later review, the
future implementation PR may modify only:

- `web/backend/app/services/email_service.py`
- `web/backend/app/api/notification.py`
- `web/backend/tests/test_notification_logging.py`
- `web/backend/tests/test_email_service_lifecycle_di.py`
- `docs/reports/quality/backend-email-service-lifecycle-di-implementation-*.md`
- `governance/mainline/task-cards/pr-*.yaml`

## Explicitly Forbidden Scope

Future implementation must not modify:

- `web/backend/app/services/email_notification_service.py`
- `web/backend/app/services/strategy_service.py`
- `web/backend/app/services/tdx_service.py`
- `web/backend/app/services/stock_search_service/stock_search_service.py`
- `web/backend/app/services/monitoring_service.py`
- `web/backend/app/services/technical_analysis_service.py`
- other service files unless a new authorization packet names them
- frontend source
- `docs/api/`
- generated clients
- OpenAPI schema behavior
- route paths, methods, or response contracts
- PM2/runtime scripts or process state

## Future Implementation Shape

The future implementation should follow the completed
`TradingViewWidgetService` provider shape while keeping email behavior stable:

1. Keep `get_email_service()` as the compatibility getter.
2. Add an app-state provider in `email_service.py`, for example:
   `install_email_service(app, service=None)` and
   `get_email_service_dependency(request)`.
3. Use a stable app-state key dedicated to `EmailService`.
4. Update `notification.py` routes to receive `EmailService` through
   `Depends(get_email_service_dependency)`.
5. Preserve background task behavior by capturing the injected service before
   scheduling any task.
6. Preserve SMTP configuration, logging, request bodies, response shapes, and
   route paths.
7. Keep tests using dependency override or provider injection rather than
   monkeypatching the compatibility getter where feasible.

The implementation should not introduce lifespan shutdown logic unless a
current-head review finds that `EmailService` owns a closeable resource. The
current service reads configuration and creates SMTP connections per send path,
so the first pass should stay narrow.

## Route Consumer Matrix

| Route-local path | Function | Current service access | Future access target | Notes |
|---|---|---|---|---|
| `GET /status` | `get_email_service_status` | direct `get_email_service()` call | injected `EmailService` | status behavior unchanged |
| `POST /email/send` | `send_email` | direct `get_email_service()` call | injected `EmailService` | capture injected service before background task |
| `POST /email/welcome` | `send_welcome_email` | direct `get_email_service()` call | injected `EmailService` | capture injected service before background task |
| `POST /email/newsletter` | `send_daily_newsletter` | direct `get_email_service()` call | injected `EmailService` | capture injected service before background task |
| `POST /email/price-alert` | `send_price_alert` | direct `get_email_service()` call | injected `EmailService` | capture injected service before background task |
| `POST /test-email` | `send_test_email` | direct `get_email_service()` call | injected `EmailService` | test mail behavior unchanged |

## Required Future Tests

Future implementation must include focused tests before commit:

```bash
python -m pytest \
  web/backend/tests/test_notification_logging.py \
  web/backend/tests/test_email_service_lifecycle_di.py \
  -q -n 0 --tb=short --no-cov
```

The new lifecycle test file should verify at minimum:

- dependency override can inject a fake `EmailService`
- notification routes use the injected service rather than the module-level
  singleton
- background task paths retain the injected fake service instance
- `get_email_service()` compatibility getter still returns an `EmailService`
  instance for legacy callers
- `email_notification_service.py` remains untouched

The existing `test_notification_logging.py` currently monkeypatches
`module.get_email_service`; future edits should adapt it to the dependency
provider without weakening log assertions.

## Required Future Quality Gates

Future implementation PR must run and record:

1. GitNexus context and upstream impact for:
   - `EmailService` in `web/backend/app/services/email_service.py`
   - file-disambiguated `get_email_service` in
     `web/backend/app/services/email_service.py`
2. Current-head write-scope check that confirms no forbidden path changed.
3. Focused pytest command listed above.
4. Ruff on touched backend files.
5. `app.main` import smoke under the repo's accepted placeholder-env pattern, if
   the branch policy requires runtime import checks.
6. Staged GitNexus `detect_changes(scope="staged")` before commit.
7. Mainline scope gate using the future PR task card.

## Rollback Plan

Rollback of the future implementation should be a path-limited revert that:

- restores direct `get_email_service()` route-body calls in `notification.py`
- leaves route paths, request models, response bodies, and OpenAPI behavior
  unchanged
- keeps or removes the new provider functions as a single unit; do not leave
  half-wired provider state
- removes `test_email_service_lifecycle_di.py` if the provider is reverted
- does not touch `email_notification_service.py`

Because this package performs no source edits, rollback for this PR is simply to
revert the authorization report, JSON artifact, steward tree update, and task
card.

## Review Decision Needed

Reviewer should decide whether this authorization package is sufficient to open
a separate future implementation lane for `email_service.py`.

Until that decision is explicitly recorded, G2.2 remains
`implementation-authorization-prepared-for-review` and no source edit is
authorized.
