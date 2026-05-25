# Backend Service Lifecycle Candidate Refresh After TradingView - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.105 service lifecycle candidate refresh after TradingView
Status: ready for review

## Purpose

Refresh the service lifecycle getter candidate inventory after G2.104 closed the
TradingView getter-retirement lane. This packet selects no source implementation
lane. It records that the remaining candidate-like rows require a duplicate
email getter ownership decision before any email getter source edit.

## Input State

| Field | Value |
|---|---|
| Parent closeout PR | `#257` |
| Parent closeout state | `MERGED` |
| Parent closeout merge commit | `750fa311eb716ff54c577748e5658329736632b4` |
| Current HEAD | `750fa311eb716ff54c577748e5658329736632b4` |

## Current-Head Scan Summary

| Metric | Value |
|---|---:|
| Service files scanned | `152` |
| Backend app files scanned | `575` |
| API files scanned | `219` |
| Test files scanned | `1008` |
| Getter definitions | `17` |
| Candidate-like definitions | `3` |
| Holds | `14` |

`get_tradingview_service` is no longer present as a service getter definition.

## Candidate Rows

| Symbol | File | Line | App refs | Route/API refs | Test refs | Package export refs | Disposition |
|---|---|---:|---:|---:|---:|---:|---|
| `get_announcement_service` | `web/backend/app/services/announcement_service.py` | `526` | `2` | `0` | `1` | `0` | hold completed announcement DI lane; do not reopen here |
| `get_email_service` | `web/backend/app/services/email_notification_service.py` | `324` | `3` | `0` | `3` | `0` | hold duplicate logical getter name; requires email ownership decision |
| `get_email_service` | `web/backend/app/services/email_service.py` | `325` | `3` | `0` | `3` | `0` | hold duplicate logical getter name; requires email ownership decision |

## Selected Next Lane

Do not select a direct source implementation lane from this refresh.

Prepare G2.106 as an email duplicate getter ownership decision packet only.

Rationale:

- The only remaining candidate-like non-completed service area is email.
- Email has duplicate logical getter names in
  `web/backend/app/services/email_service.py` and
  `web/backend/app/services/email_notification_service.py`.
- `web/backend/app/services/email_service.py` also owns the active
  `get_email_service_dependency` route dependency seam, so getter retirement
  must not be inferred from name-only counts.
- GitNexus reports `get_email_service` in `email_service.py` as MEDIUM impact
  with impacted count `6` and affected processes `0`, while the
  `email_notification_service.py` getter has no incoming graph callers.
- The next packet must decide ownership and implementation boundaries before
  any source edit.

Boundary:

- This selection does not authorize editing email services or notification
  routes.
- This selection does not authorize deleting either `get_email_service`
  definition.
- This selection does not authorize changing routes, response models, response
  shapes, OpenAPI exposure, frontend code, PM2 state, OpenSpec files, or issue
  labels.

## Verification Evidence

| Check | Result |
|---|---|
| GitNexus index | Refreshed with `gitnexus analyze --with-gitignore`; graph size is non-gating for this doc-only packet because added governance artifacts can alter index counts between amendments |
| Getter candidate scan | `152` service files, `575` app files, `219` API files, `1008` test files, `17` getter definitions, `3` candidate-like definitions, `14` holds |
| Email service getter impact | `get_email_service` in `email_service.py`: MEDIUM, impacted count `6`, affected processes `0` |
| Email notification getter context | `get_email_service` in `email_notification_service.py`: incoming graph callers `0`, affected processes `0` |

## Boundary

This packet does not:

- edit backend source or tests;
- delete, rename, or migrate any email service symbol;
- change routes, response models, response shapes, or OpenAPI exposure;
- change frontend files, generated clients, PM2 state, OpenSpec files, or
  GitHub issue labels;
- authorize G2.106 implementation work.

## Next Gate

Human review / PR merge decision for this G2.105 governance packet.

If accepted, create G2.106 as an email duplicate getter ownership decision
packet before any email getter source edit.
