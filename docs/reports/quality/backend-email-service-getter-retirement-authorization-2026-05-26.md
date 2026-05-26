# Backend EmailService Getter Retirement Authorization - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Ready for review.

## Parent Gate

| Field | Value |
|---|---|
| Parent node | G2.120 Service lifecycle candidate refresh after AnnouncementService |
| Parent PR | `#273` |
| Parent state | `MERGED` |
| Parent merge commit | `1f117e1c7aa0333b6c0de272d697043f59f56bc9` |
| Parent merged at | `2026-05-26T00:21:15Z` |
| Current HEAD | `1f117e1c7aa0333b6c0de272d697043f59f56bc9` |

## Authorization Decision

Authorize only a future G2.122 implementation branch to retire the
`EmailService` module-level getter:

- `web/backend/app/services/email_service.py:_email_service`
- `web/backend/app/services/email_service.py:get_email_service`

The future implementation must preserve:

- `EmailService`
- `install_email_service`
- `get_email_service_dependency`
- `EMAIL_SERVICE_STATE_KEY`
- notification route paths, response contracts, and OpenAPI exposure

## Current Evidence

| Check | Value |
|---|---:|
| `get_email_service` definitions in `email_service.py` | 1 |
| `_email_service` tokens in `email_service.py` | 5 |
| Exact direct getter refs in API files | 0 |
| Exact direct getter refs in adapter files | 0 |
| Exact direct getter refs in backend tests | 4 across 3 files |
| `get_email_service_dependency` refs in API | 7 |
| `Depends(get_email_service_dependency)` route refs | 6 |
| API files scanned | 219 |
| Backend test files scanned | 201 |

GitNexus impact for `get_email_service`:

- risk: MEDIUM
- impacted count: 6
- affected processes: 0
- modules affected: 1

GitNexus reports notification route callers. Exact text scan shows those routes
import and use `get_email_service_dependency`, not the getter itself.

GitNexus staged detect changes for this authorization packet is low risk with
changed count `0`, changed files `4`, affected count `0`, and affected
processes `0`.

## Future G2.122 Maximum Scope

If this packet is reviewed and accepted, G2.122 may be created with this maximum
source/test scope:

| Path | Future allowed action |
|---|---|
| `web/backend/app/services/email_service.py` | Remove `_email_service` and `get_email_service`; change `install_email_service` fallback to construct `EmailService()` directly |
| `web/backend/tests/test_email_service_lifecycle_di.py` | Update fallback installation coverage to patch `EmailService` rather than the retired getter |
| `web/backend/tests/test_notification_logging.py` | Remove obsolete fake getter exposure if required by focused tests |
| `web/backend/tests/test_email_service_getter_retirement.py` | Add focused absence/preservation regression coverage |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Record implementation status after the branch runs |
| `.planning/codebase/generated/email-service-getter-retirement-implementation-2026-05-26.json` | Record generated implementation evidence |
| `docs/reports/quality/backend-email-service-getter-retirement-implementation-2026-05-26.md` | Record implementation evidence |
| `governance/mainline/task-cards/pr-274.yaml` | Record implementation task-card gate |

## Future G2.122 Required Gates

Before any source edit:

- read `architecture/STANDARDS.md`
- run GitNexus context/impact for `get_email_service`
- write a failing TDD test proving the getter/singleton still exist

Before commit:

- focused EmailService getter-retirement tests pass
- `test_email_service_lifecycle_di.py` passes
- `test_notification_logging.py` passes if touched
- `test_health_route_conflicts.py` passes
- ruff and black pass on touched files
- exact post-change scan shows target getter definitions=`0`, target singleton
  tokens=`0`, direct API getter refs=`0`
- GitNexus staged detect changes is low/expected
- mainline scope gate passes after commit

## Boundary Confirmation

This is an authorization-only packet.

No backend source files, backend tests, route/API files, OpenAPI artifacts,
frontend files, PM2 workflows, OpenSpec changes/specs, or GitHub issue labels
are changed here.

This packet does not perform the getter retirement. It only authorizes the
future G2.122 implementation boundary.
