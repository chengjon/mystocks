# Backend EmailNotificationService Getter Retirement Implementation - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.108 EmailNotificationService getter-retirement implementation
Status: ready for review

## Purpose

Implement the G2.107 authorization by retiring the legacy/helper
`get_email_service` singleton surface in
`web/backend/app/services/email_notification_service.py`.

This implementation is intentionally narrow. It does not change the route-backed
email lifecycle seam in `web/backend/app/services/email_service.py`, notification
routes, OpenAPI exposure, PM2 workflows, OpenSpec changes, frontend code, or
issue labels.

## Parent Gate

| Gate | Result |
|---|---|
| Parent authorization | G2.107 accepted in PR `#260` |
| Parent merge commit | `d120d6d28d391daeb9e3d6accbd2b9ee0acfe931` |
| Current implementation base | `d120d6d28d391daeb9e3d6accbd2b9ee0acfe931` |
| Authorized target | `web/backend/app/services/email_notification_service.py` |
| Authorized removals | `_email_service`, `get_email_service` |
| Required preservation | `EmailNotificationService`, route-backed `email_service.py`, `get_email_service_dependency`, notification routes |

## Pre-Edit Evidence

| Evidence | Result |
|---|---|
| `architecture/STANDARDS.md` | Read before source edit; deletion requires explicit closure and evidence |
| GitNexus analyze | `gitnexus analyze --with-gitignore`; indexed successfully before edit |
| File-path GitNexus context | `email_notification_service.py:get_email_service` has no incoming graph callers, no outgoing graph calls, and no process participation |
| Bare GitNexus impact | `impact(get_email_service)` resolves to the separate route-backed `email_service.py:get_email_service` symbol with MEDIUM / `6`; this was treated as a disambiguation warning, not as the target symbol |
| Exact pre-change target scan | `email_notification_service.py:get_email_service` refs=`1`; `_email_service` refs present only in the target file |
| Route/API boundary | `web/backend/app/api/notification.py` has `0` `email_notification_service` refs |
| Route-backed dependency | `get_email_service_dependency` remains active in `notification.py` with `7` refs and in `email_service.py` with `1` ref |

## Change

Removed only the legacy/helper lazy singleton surface from
`web/backend/app/services/email_notification_service.py`:

- `_email_service`
- `get_email_service`

Added a focused regression test:

- `web/backend/tests/test_email_notification_service_getter_retirement.py`

The test asserts that `EmailNotificationService` remains importable while the
legacy getter and module singleton are absent.

## Verification

| Check | Command | Result |
|---|---|---|
| TDD red | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_email_notification_service_getter_retirement.py -q --no-cov --tb=short` | `1 failed`; failure was `hasattr(module, "get_email_service")` |
| Focused green | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_email_notification_service_getter_retirement.py web/backend/tests/test_email_notification_service_logging.py -q --no-cov --tb=short` | `5 passed` |
| Health route conflicts | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |
| Ruff touched files | `ruff check web/backend/app/services/email_notification_service.py web/backend/tests/test_email_notification_service_getter_retirement.py` | passed |
| Black touched files | `black --check web/backend/app/services/email_notification_service.py web/backend/tests/test_email_notification_service_getter_retirement.py` | passed |
| Exact post-change scan | scripted text scan | target getter refs=`0`; target singleton refs=`0`; route `email_notification_service` refs=`0` |

Note: an exploratory ruff run that included the unchanged
`test_email_notification_service_logging.py` surfaced existing PT018 style in
that file. The file was used for behavior verification but not modified, and
the final ruff gate was scoped to actual touched backend files.

## Post-Change Scan

| Surface | Result |
|---|---|
| `email_notification_service.py:get_email_service` | `0` refs |
| `email_notification_service.py:_email_service` | `0` refs |
| `web/backend/app/api/*` direct `email_notification_service` refs | `0` |
| `get_email_service_dependency` | unchanged: `notification.py` refs=`7`, `email_service.py` refs=`1` |
| `EmailNotificationService` app refs | retained in `email_notification_service.py` and `core/unified_email_service.py` |
| `EmailNotificationService` test refs | retained in `test_email_notification_service_getter_retirement.py` and `test_email_notification_service_logging.py` |

## Boundary

This PR does not:

- modify `web/backend/app/services/email_service.py`
- modify `web/backend/app/api/notification.py`
- alter route paths, response models, response shapes, or OpenAPI exposure
- alter frontend code
- alter PM2 workflows
- create or modify OpenSpec proposals/specs
- change GitHub issue labels or readiness state
- delete or rename `EmailNotificationService`
- consolidate email services beyond the authorized getter retirement

## Next Gate

Human review / PR merge decision for G2.108.

If accepted, create G2.109 closeout/current-head refresh before selecting
another service getter candidate.
