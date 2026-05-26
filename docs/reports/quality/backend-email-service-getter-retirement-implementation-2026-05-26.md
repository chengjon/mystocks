# Backend EmailService Getter Retirement Implementation - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Ready for review.

## Parent Gate

| Field | Value |
|---|---|
| Parent node | G2.121 EmailService getter-retirement authorization |
| Parent PR | `#274` |
| Parent state | `MERGED` |
| Parent merge commit | `5b944a53a8a6f960ec1420cfd2a885c364d97bf3` |
| Parent merged at | `2026-05-26T00:33:28Z` |
| Implementation branch | `g2-122-email-service-getter-retirement-implementation` |
| Implementation base HEAD | `5b944a53a8a6f960ec1420cfd2a885c364d97bf3` |

## Scope

Changed files:

- `web/backend/app/services/email_service.py`
- `web/backend/tests/test_email_service_lifecycle_di.py`
- `web/backend/tests/test_notification_logging.py`
- `web/backend/tests/test_email_service_getter_retirement.py`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/email-service-getter-retirement-implementation-2026-05-26.json`
- `governance/mainline/task-cards/pr-275.yaml`

No route/API files, OpenAPI artifacts, frontend files, PM2 workflows,
OpenSpec changes/specs, or issue-label state were changed.

## Pre-Edit Evidence

| Gate | Result |
|---|---|
| `architecture/STANDARDS.md` | read before source edit |
| Parent PR `#274` | `MERGED` |
| GitNexus context | `get_email_service` located in `web/backend/app/services/email_service.py`; graph reports 6 notification route callers |
| GitNexus impact | `MEDIUM`, impacted count `6`, affected processes `0` |

Exact text scan before implementation showed API direct getter refs=`0` and
routes using `get_email_service_dependency`.

## Implementation

`web/backend/app/services/email_service.py`:

- removed the module-level `_email_service`
- removed `get_email_service`
- changed `install_email_service` to construct `EmailService()` directly when no
  explicit service is supplied

`web/backend/tests/test_email_service_lifecycle_di.py`:

- removed obsolete fake module `get_email_service` exposure
- changed the app-state fallback test to monkeypatch `EmailService` rather than
  the retired getter

`web/backend/tests/test_notification_logging.py`:

- removed obsolete fake module `get_email_service` exposure

`web/backend/tests/test_email_service_getter_retirement.py`:

- added focused regression coverage proving the legacy getter and singleton are
  absent while the app-state installer and dependency remain importable

## Verification

| Check | Command | Result |
|---|---|---|
| TDD red | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_email_service_getter_retirement.py -q --no-cov --tb=short` | `1 failed`; failure proved `get_email_service` still existed before implementation |
| Focused green | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_email_service_getter_retirement.py web/backend/tests/test_email_service_lifecycle_di.py web/backend/tests/test_notification_logging.py -q --no-cov --tb=short` | `7 passed` |
| Health route conflicts | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |
| Ruff touched files | `ruff check web/backend/app/services/email_service.py web/backend/tests/test_email_service_lifecycle_di.py web/backend/tests/test_notification_logging.py web/backend/tests/test_email_service_getter_retirement.py` | passed |
| Black touched files | `black --check web/backend/app/services/email_service.py web/backend/tests/test_email_service_lifecycle_di.py web/backend/tests/test_notification_logging.py web/backend/tests/test_email_service_getter_retirement.py` | passed |
| Exact post-change scan | scripted text scan over backend app/tests | target getter definitions=`0`; target singleton tokens in service=`0`; app/API direct getter refs=`0`; test direct getter refs=`2` in absence assertions; dependency refs=`8`; route dependency handlers=`6`; install refs=`2`; files scanned=`777` |
| GitNexus staged detect changes | `detect_changes(scope="staged")` | risk=`low`; changed count=`18`; changed files=`8`; affected count=`0`; affected processes=`0` |

## Boundary Confirmation

Preserved:

- `EmailService`
- `install_email_service`
- `get_email_service_dependency`
- `EMAIL_SERVICE_STATE_KEY`
- notification route dependency injection
- OpenAPI exposure

Retired:

- `web/backend/app/services/email_service.py:_email_service`
- `web/backend/app/services/email_service.py:get_email_service`

Not changed:

- notification route handlers
- route paths, response models, response shapes, or OpenAPI exposure
- frontend code
- PM2 workflows
- OpenSpec proposals/specs
- GitHub issue labels or readiness state
- broader email service behavior

## Next Gate

Human review and PR merge decision for G2.122.

If accepted, create G2.123 as a closeout/current-head verification packet before
selecting the next service lifecycle getter lane.
