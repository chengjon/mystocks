# Backend AnnouncementService Getter Retirement Closeout - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Ready for review.

## Parent Merge

| Field | Value |
|---|---|
| Parent node | G2.118 AnnouncementService getter-retirement implementation |
| Parent PR | `#271` |
| Parent state | `MERGED` |
| Parent merge commit | `4a2a21272deff876bc9fb5f1058c0682a7f4b5de` |
| Parent merged at | `2026-05-25T23:56:18Z` |
| Closeout branch | `g2-119-announcement-service-getter-retirement-closeout` |
| Current HEAD | `4a2a21272deff876bc9fb5f1058c0682a7f4b5de` |

## Closeout Decision

The AnnouncementService getter-retirement implementation lane is closed at
current HEAD.

This closeout records that PR `#271` merged the narrow implementation that
removed only:

- `web/backend/app/services/announcement_service.py:_announcement_service`
- `web/backend/app/services/announcement_service.py:get_announcement_service`

It also confirms that the following surfaces remain present:

- `AnnouncementService`
- `install_announcement_service`
- `get_announcement_service_dependency`
- announcement route dependency injection

## Current-Head Evidence

| Check | Result |
|---|---|
| Target getter definitions | `0` |
| Target singleton tokens in `announcement_service.py` | `0` |
| API direct getter refs | `0` |
| Dependency refs | `15` |
| Route dependency handlers | `11` |
| Installer refs | `3` |
| Backend app/test Python files scanned | `776` |

## Verification

| Check | Command | Result |
|---|---|---|
| Parent PR state | `gh pr view 271 --repo chengjon/mystocks --json number,state,mergedAt,mergeCommit,url` | `MERGED`, merge commit `4a2a21272deff876bc9fb5f1058c0682a7f4b5de` |
| Focused tests | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_announcement_service_getter_retirement.py web/backend/tests/test_announcement_service_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| Health route conflicts | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |
| Current-head scan | scripted text scan | getter=`0`, singleton=`0`, API direct refs=`0`, route dependency handlers=`11` |
| GitNexus staged detect changes | `detect_changes(scope="staged")` | risk=`low`; changed count=`0`; changed files=`4`; affected count=`0`; affected processes=`0` |

## Boundary Confirmation

This is a closeout-only packet.

No backend source files, backend tests, route/API files, OpenAPI artifacts,
frontend files, PM2 workflows, OpenSpec changes/specs, or GitHub issue labels
are changed here.

This packet does not authorize the next implementation lane. It only records
that G2.118 is merged and verified at current HEAD.

## Next Gate

Create G2.120 as a service lifecycle candidate refresh after AnnouncementService
before selecting the next medium route-backed getter lane.
