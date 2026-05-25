# Backend AnnouncementService Getter Retirement Authorization - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.117 AnnouncementService getter-retirement authorization
Status: ready for review

## Purpose

Authorize a future implementation branch for retiring the module-level
`AnnouncementService` lazy singleton getter in
`web/backend/app/services/announcement_service.py`.

This authorization does not modify backend source, tests, routes, OpenAPI,
frontend code, PM2 workflows, OpenSpec changes, GitHub issue labels, or service
implementation logic.

## Parent Gate

| Gate | Result |
|---|---|
| Parent consumer matrix | G2.116 accepted in PR `#269` |
| Parent merge commit | `618820c89888887a7352999e32ec4285ccad836a` |
| Current authorization base | `618820c89888887a7352999e32ec4285ccad836a` |

## Target

| Surface | Status |
|---|---|
| `AnnouncementService` | preserve |
| `_announcement_service` | authorized for future removal |
| `get_announcement_service` | authorized for future removal |
| `install_announcement_service` | preserve |
| `get_announcement_service_dependency` | preserve |
| Announcement routes / OpenAPI exposure | preserve |

## Evidence

| Evidence | Result |
|---|---|
| Exact direct getter scan | `3 refs / 2 files`: service definition, installer fallback, lifecycle test monkeypatch |
| Exact API direct getter refs | `0` |
| Exact adapter direct getter refs | `0` |
| Dependency refs | `14 refs / 3 files`; 11 announcement route handlers use `Depends(get_announcement_service_dependency)` |
| GitNexus context | graph reports 11 route callers for `get_announcement_service` |
| GitNexus impact | MEDIUM / `11`, affected processes=`0` |

The GitNexus route callers are treated as a graph-level dependency-injection
signal, not as direct text consumers. A future implementation must verify this
with focused tests and exact post-change scans.

## Authorized Future Scope

Future G2.118 may modify only:

- `web/backend/app/services/announcement_service.py`
- `web/backend/tests/test_announcement_service_lifecycle_di.py`
- a focused getter-retirement regression test if needed
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/announcement-service-getter-retirement-implementation-2026-05-26.json`
- `docs/reports/quality/backend-announcement-service-getter-retirement-implementation-2026-05-26.md`
- a future task card, expected `governance/mainline/task-cards/pr-271.yaml`

Future G2.118 must preserve:

- `AnnouncementService`
- `install_announcement_service`
- `get_announcement_service_dependency`
- announcement route contracts and OpenAPI exposure
- frontend, PM2, OpenSpec, and issue-label state

## Boundary

This PR does not:

- modify backend source or tests
- delete any getter
- modify route paths, response models, response shapes, or OpenAPI exposure
- modify frontend code
- modify PM2 workflows
- create or modify OpenSpec proposals/specs
- change GitHub issue labels or readiness state
- authorize any implementation beyond future G2.118

## Next Gate

Human review / PR merge decision for G2.117.

If accepted, create G2.118 AnnouncementService getter-retirement implementation
before any announcement service source edit.
