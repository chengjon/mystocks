# Backend EmailNotificationService Getter Retirement Closeout - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.109 EmailNotificationService getter-retirement closeout
Status: ready for review

## Purpose

Close out G2.108 by verifying the merged current head after PR `#261`. This
packet records that the legacy/helper `EmailNotificationService` getter surface
is retired and that route-backed email dependency injection remains outside this
lane.

This is closeout-only. It does not modify backend source, tests, routes,
OpenAPI, frontend, PM2, OpenSpec, or issue labels.

## Parent Merge

| Item | Value |
|---|---|
| Parent PR | `#261` |
| Parent state | `MERGED` |
| Parent merged at | `2026-05-25T17:56:05Z` |
| Parent merge commit | `9cb643dbcd78bae76afc8201dad65b6f431a801c` |
| Current HEAD | `9cb643dbcd78bae76afc8201dad65b6f431a801c` |

## Current-Head Scan

| Surface | Result |
|---|---|
| `email_notification_service.py:get_email_service` | refs=`0` |
| `email_notification_service.py:_email_service` | refs=`0` |
| `web/backend/app/api/*` direct `email_notification_service` refs | refs=`0` |
| `get_email_service_dependency` | retained: `notification.py` refs=`7`, `email_service.py` refs=`1` |
| `EmailNotificationService` app refs | retained in `email_notification_service.py` and `core/unified_email_service.py` |
| `EmailNotificationService` test refs | retained in `test_email_notification_service_getter_retirement.py` and `test_email_notification_service_logging.py` |

## Verification

| Check | Command | Result |
|---|---|---|
| Focused tests | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_email_notification_service_getter_retirement.py web/backend/tests/test_email_notification_service_logging.py -q --no-cov --tb=short` | `5 passed` |
| Health route conflicts | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |
| Ruff target files | `ruff check web/backend/app/services/email_notification_service.py web/backend/tests/test_email_notification_service_getter_retirement.py` | passed |
| Black target files | `black --check web/backend/app/services/email_notification_service.py web/backend/tests/test_email_notification_service_getter_retirement.py` | passed |
| Exact scan | scripted current-head text scan | target getter refs=`0`; target singleton refs=`0`; route direct refs=`0` |

## Closeout Decision

The EmailNotificationService legacy/helper getter-retirement lane is closed
pending human review and PR merge of this closeout packet.

Do not select the next service getter candidate from stale pre-#261 evidence.
After this packet is accepted, run a fresh service lifecycle candidate refresh
from the merged head.

## Boundary

This packet does not:

- modify backend source or tests
- modify `web/backend/app/services/email_service.py`
- modify `web/backend/app/api/notification.py`
- change routes, response contracts, or OpenAPI exposure
- change frontend code
- change PM2 workflows
- create or modify OpenSpec changes/specs
- change GitHub issue labels or readiness state
- delete or rename `EmailNotificationService`

## Next Gate

Human review / PR merge decision for G2.109.

If accepted, create a fresh service lifecycle candidate refresh before selecting
another service getter candidate.
