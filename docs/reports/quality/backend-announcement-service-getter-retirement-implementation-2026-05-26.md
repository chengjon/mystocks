# Backend AnnouncementService Getter Retirement Implementation - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Ready for review.

## Parent Gate

| Field | Value |
|---|---|
| Parent node | G2.117 AnnouncementService getter-retirement authorization |
| Parent PR | `#270` |
| Parent state | `MERGED` |
| Parent merge commit | `ca1ad8da694f0174b5a80d414cc624d05865ec8f` |
| Parent merged at | `2026-05-25T19:34:08Z` |
| Implementation branch | `g2-118-announcement-service-getter-retirement-implementation` |
| Implementation base HEAD | `ca1ad8da694f0174b5a80d414cc624d05865ec8f` |

G2.117 authorized one narrow source-capable implementation branch:
retire `web/backend/app/services/announcement_service.py`
`_announcement_service` and `get_announcement_service`, while preserving
`AnnouncementService`, `install_announcement_service`,
`get_announcement_service_dependency`, announcement route behavior, and OpenAPI
exposure.

## Scope

Changed files:

- `web/backend/app/services/announcement_service.py`
- `web/backend/tests/test_announcement_service_lifecycle_di.py`
- `web/backend/tests/test_announcement_service_getter_retirement.py`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/announcement-service-getter-retirement-implementation-2026-05-26.json`
- `governance/mainline/task-cards/pr-271.yaml`

No route/API files, OpenAPI artifacts, frontend files, PM2 workflows,
OpenSpec changes/specs, or issue-label state were changed.

## Pre-Edit Evidence

| Gate | Result |
|---|---|
| `architecture/STANDARDS.md` | read before source edit |
| GitNexus analyze | completed before source edit |
| GitNexus context | `get_announcement_service` located in `web/backend/app/services/announcement_service.py`; graph still reports 11 route callers |
| GitNexus impact | `MEDIUM`, impacted count `11`, affected processes `0` |

The graph callers were treated as the route-dependency seam to verify, not as
permission to edit route handlers.

## Implementation

`web/backend/app/services/announcement_service.py`:

- removed the module-level `_announcement_service`
- removed `get_announcement_service`
- changed `install_announcement_service` to construct `AnnouncementService()`
  directly when no explicit service is supplied

`web/backend/tests/test_announcement_service_lifecycle_di.py`:

- changed the app-state fallback test to monkeypatch `AnnouncementService`
  rather than the retired getter

`web/backend/tests/test_announcement_service_getter_retirement.py`:

- added focused regression coverage proving the legacy getter and singleton are
  absent while the app-state installer and dependency remain importable

## Verification

| Check | Command | Result |
|---|---|---|
| TDD red | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_announcement_service_getter_retirement.py -q --no-cov --tb=short` | `1 failed`; failure proved `get_announcement_service` still existed before implementation |
| Focused green | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_announcement_service_getter_retirement.py web/backend/tests/test_announcement_service_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| Health route conflicts | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed` |
| Ruff touched files | `ruff check web/backend/app/services/announcement_service.py web/backend/tests/test_announcement_service_lifecycle_di.py web/backend/tests/test_announcement_service_getter_retirement.py` | passed |
| Black touched files | `black --check web/backend/app/services/announcement_service.py web/backend/tests/test_announcement_service_lifecycle_di.py web/backend/tests/test_announcement_service_getter_retirement.py` | passed |
| Exact post-change scan | scripted text scan over backend app/tests | target getter definitions=`0`; target singleton tokens in service=`0`; API direct getter refs=`0`; dependency refs=`15`; route dependency handlers=`11`; install refs=`3`; files scanned=`776` |
| GitNexus staged detect changes | `detect_changes(scope="staged")` | risk=`low`; changed count=`15`; changed files=`7`; affected count=`0`; affected processes=`0` |

## Boundary Confirmation

Preserved:

- `AnnouncementService`
- `install_announcement_service`
- `get_announcement_service_dependency`
- `ANNOUNCEMENT_SERVICE_STATE_KEY`
- announcement route dependency injection
- OpenAPI exposure

Retired:

- `web/backend/app/services/announcement_service.py:_announcement_service`
- `web/backend/app/services/announcement_service.py:get_announcement_service`

Not changed:

- announcement route handlers
- route paths, response models, response shapes, or OpenAPI exposure
- frontend code
- PM2 workflows
- OpenSpec proposals/specs
- GitHub issue labels or readiness state
- broader announcement service behavior

## Next Gate

Human review and PR merge decision for G2.118.

If accepted, create G2.119 as a closeout/current-head verification packet before
selecting the next medium route-backed getter lane.
