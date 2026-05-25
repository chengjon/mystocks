# Backend Email Duplicate Getter Ownership Decision - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.106 email duplicate getter ownership decision
Status: ready for review

## Purpose

Resolve the ownership question exposed by G2.105: two service modules define a
function named `get_email_service`, but they do not represent the same lifecycle
surface. This packet is decision-only and does not authorize any source edit.

## Input State

| Field | Value |
|---|---|
| Parent candidate refresh PR | `#258` |
| Parent candidate refresh state | `MERGED` |
| Parent candidate refresh merge commit | `9ac90c14acd14b851bf49271f48fba30c8b10e41` |
| Current HEAD | `9ac90c14acd14b851bf49271f48fba30c8b10e41` |

## Decision

Treat the two `get_email_service` definitions as separate ownership surfaces:

| Owner | File | Service class | Disposition |
|---|---|---|---|
| Route-backed email lifecycle owner | `web/backend/app/services/email_service.py` | `EmailService` | Hold for separate future authorization because it owns `install_email_service`, `get_email_service_dependency`, and route dependency state |
| Legacy/helper notification owner | `web/backend/app/services/email_notification_service.py` | `EmailNotificationService` | Candidate for a future G2.107 authorization-only packet |

Do not collapse the duplicate function names into one source edit.

## Current-Head Reference Scan

| Signal | App refs | Route/API refs | Test refs | Relevant files |
|---|---:|---:|---:|---|
| `get_email_service` combined | `3` | `0` | `3` | `email_service.py`, `email_notification_service.py`, `test_notification_logging.py`, `test_email_service_lifecycle_di.py` |
| `_email_service` combined | `10` | `0` | `0` | `email_service.py`, `email_notification_service.py` |
| `get_email_service_dependency` | `8` | `7` | `3` | `email_service.py`, `notification.py`, focused tests |
| `install_email_service` | `2` | `0` | `0` | `email_service.py` |
| `EmailNotificationService` | `9` | `0` | `3` | `email_notification_service.py`, `unified_email_service.py`, focused tests |
| `EmailService` | `19` | `7` | `4` | `email_service.py`, `notification.py`, `unified_email_service.py`, focused tests |

`web/backend/app/api/notification.py` imports `EmailService` and
`get_email_service_dependency` from `email_service.py`; it does not directly
import either `get_email_service` function.

## GitNexus Evidence

| Symbol | File | Graph context / impact |
|---|---|---|
| `get_email_service` | `web/backend/app/services/email_service.py` | context incoming calls=`6`; impact MEDIUM, impacted count=`6`, affected processes=`0` |
| `get_email_service` | `web/backend/app/services/email_notification_service.py` | context incoming calls=`0`, affected processes=`0` |

The graph impact for `email_service.py:get_email_service` is intentionally
treated as a reason to hold route-backed email lifecycle work behind a later
authorization packet. Current text scan still shows route code using
`get_email_service_dependency`, not direct getter imports.

## Selected Next Lane

Create G2.107 as an EmailNotificationService getter-retirement authorization
packet only.

G2.107 must:

- target `web/backend/app/services/email_notification_service.py`;
- keep `web/backend/app/services/email_service.py` out of scope;
- keep notification routes and `get_email_service_dependency` out of scope;
- require a fresh GitNexus impact/context check before any source edit;
- require TDD red/green in the later implementation packet.

## Boundary

This packet does not:

- edit backend source or tests;
- delete either `get_email_service` definition;
- delete or rename `_email_service` in either module;
- migrate `EmailService` or `EmailNotificationService`;
- change notification routes, response models, response shapes, or OpenAPI
  exposure;
- change frontend files, generated clients, PM2 state, OpenSpec files, or
  GitHub issue labels;
- authorize G2.107 implementation work.

## Next Gate

Human review / PR merge decision for this G2.106 decision packet.

If accepted, create G2.107 as an EmailNotificationService getter-retirement
authorization packet before any email source edit.
