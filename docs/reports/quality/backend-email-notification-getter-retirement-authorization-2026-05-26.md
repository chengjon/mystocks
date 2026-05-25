# Backend EmailNotificationService Getter Retirement Authorization - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- State: ready for review
- Governance node: G2.107
- Scope: authorization-only
- Created at: 2026-05-26T01:29:37+08:00
- Current HEAD: `6e10c496a4e3c68c21b93a2ddfec09ef74f1aa30`
- Parent decision: G2.106 accepted in PR `#259`

This packet does not edit backend source, tests, route contracts, OpenAPI
exposure, PM2 workflows, OpenSpec changes, or issue labels. It only records
the gate for a future implementation branch.

## Purpose

G2.106 separated two same-named email getters:

- `web/backend/app/services/email_service.py:get_email_service` is part of
  the route-backed `EmailService` lifecycle seam.
- `web/backend/app/services/email_notification_service.py:get_email_service`
  is a legacy/helper lazy getter around `EmailNotificationService`.

This packet authorizes only the next step: a future G2.108 implementation
branch may retire the `email_notification_service.py` module-level
`_email_service` singleton and `get_email_service` helper after it completes
the required pre-edit impact and TDD gates.

## Current Evidence

| Evidence | Result |
|---|---|
| Current checkout | `6e10c496a4e3c68c21b93a2ddfec09ef74f1aa30` |
| Parent PR | `#259`, merged as `6e10c496a4e3c68c21b93a2ddfec09ef74f1aa30` |
| Target file | `web/backend/app/services/email_notification_service.py` |
| Target singleton | `_email_service` at line `321` |
| Target getter | `get_email_service` at line `324` |
| Preserved class | `EmailNotificationService` at line `23` |
| GitNexus context | `email_notification_service.py:get_email_service` has no incoming graph callers, no outgoing graph calls, and no process participation |
| GitNexus disambiguation warning | Bare `impact(get_email_service)` resolves to the separate route-backed `email_service.py:get_email_service` symbol with MEDIUM / `6`; future implementation must use file-path context plus text scan |
| Route/API boundary | `web/backend/app/api/notification.py` imports `EmailService` and `get_email_service_dependency` from `app.services.email_service`; it has no `email_notification_service` refs |
| Active route-backed dependency | `get_email_service_dependency` exact refs: `notification.py` has `7`, `email_service.py` has `1` |
| Class usage retained | `web/backend/app/core/unified_email_service.py` imports `EmailNotificationService`; `test_email_notification_service_logging.py` instantiates the class directly |

## Authorized Future G2.108 Scope

If this packet is accepted, G2.108 may modify only the minimum source and test
surface needed to remove the legacy/helper lazy getter:

- `web/backend/app/services/email_notification_service.py`
- A focused backend test proving the getter and module singleton are retired,
  for example `web/backend/tests/test_email_notification_service_getter_retirement.py`
- Steward-tree update
- Generated G2.108 evidence JSON
- G2.108 implementation report
- G2.108 mainline task card

The future implementation may remove:

- `email_notification_service.py:_email_service`
- `email_notification_service.py:get_email_service`

The future implementation must preserve:

- `EmailNotificationService`
- Existing `EmailNotificationService` constructor behavior
- Existing logging behavior covered by `test_email_notification_service_logging.py`
- `web/backend/app/core/unified_email_service.py` class import behavior unless
  a separate authorization packet approves that change

## Forbidden Future G2.108 Scope

The authorization does not allow changes to:

- `web/backend/app/services/email_service.py`
- `web/backend/app/api/notification.py`
- `get_email_service_dependency`
- `install_email_service`
- notification route paths, response models, response shapes, or OpenAPI
  exposure
- frontend code
- PM2 workflows
- OpenSpec proposals or specs
- GitHub issue labels or readiness states
- deletion or rename of `EmailNotificationService`
- broader email service consolidation

## Required Future G2.108 Verification

G2.108 must run fresh checks in its own isolated worktree before source edits:

1. Re-read `architecture/STANDARDS.md`.
2. Run GitNexus file-path context for
   `web/backend/app/services/email_notification_service.py:get_email_service`.
3. Treat bare `impact(get_email_service)` as ambiguous because it resolves to
   the route-backed `email_service.py` symbol.
4. Re-run an exact text scan for `email_notification_service.py` getter refs,
   route/API refs, and `EmailNotificationService` class refs.
5. Write the focused absence test first and capture the red result.
6. Remove only the authorized getter and singleton.
7. Run the focused green test and existing
   `test_email_notification_service_logging.py`.
8. Run ruff/black checks on touched backend files.
9. Stage only authorized paths and run GitNexus `detect_changes` with
   `scope="staged"`.
10. Run the mainline scope gate and markdown / JSON / YAML governance checks.

## Boundary

This is not implementation approval for this branch. G2.107 makes no runtime
change. It only creates the review gate for G2.108.

If this packet is rejected, keep G2.106 as the latest accepted email getter
ownership decision and do not edit either email getter.

## Next Gate

Human review / PR merge decision for G2.107.

If accepted, create G2.108 as the EmailNotificationService getter-retirement
implementation branch before any email notification source edit.
