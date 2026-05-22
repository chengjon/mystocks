# Backend Watchlist Service Lifecycle DI Closeout - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: completed-and-recorded
- Workline: G2.11 service lifecycle DI implementation closeout
- Completed pilot: `web/backend/app/services/watchlist_service.py`
- Implementation PR: https://github.com/chengjon/mystocks/pull/150
- Implementation merge commit: `b14ef8421d8ccd6dfd4a714b2a17d4e1ae971419`
- Implementation commit: `480c7aad9da84b058a05025c1304a94556780aef`
- Authorization PR: https://github.com/chengjon/mystocks/pull/149
- Authorization merge commit: `bddb764c79355e6c0c366fdd9a28d64a685700bf`
- Closeout branch: `g2-11-watchlist-service-di-closeout`
- Recorded at: `2026-05-23T01:50:00+08:00`

## Governance Boundary

This closeout is governance bookkeeping only. It records that the G2.10
watchlist route-surface DI implementation was reviewed through PR checks and
merged. It does not authorize a fourth service DI candidate, adapter/data-layer
migration, OpenSpec changes, issue label movement, PM2/runtime work, frontend
work, route/OpenAPI contract changes, or additional source edits.

## Completed Scope

PR `#150` implemented the G2.9-authorized route-surface-only scope:

- `web/backend/app/services/watchlist_service.py`
  - added `WATCHLIST_SERVICE_STATE_KEY`
  - added `install_watchlist_service(app, service=None)`
  - added `get_watchlist_service_dependency(request)`
  - retained `get_watchlist_service()` as the compatibility getter
- `web/backend/app/api/watchlist.py`
  - injected `WatchlistService` into seven watchlist group route handlers
  - removed route-body direct `get_watchlist_service()` calls from those seven
    handlers
- `web/backend/tests/test_watchlist_service_lifecycle_di.py`
  - added focused TDD coverage for provider installation, route signatures, and
    fake-service injection
- `docs/reports/quality/backend-watchlist-service-lifecycle-di-implementation-2026-05-22.md`
  - recorded implementation evidence and rollback boundaries
- `governance/mainline/task-cards/pr-150.yaml`
  - recorded implementation scope and gates
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
  - recorded G2.10 as implementation prepared for review

## Preserved Compatibility Boundary

The implementation did not edit:

- `web/backend/app/services/data_adapters/watchlist.py`
- `web/backend/app/services/adapters/watchlist_adapter.py`

Those adapter/data helper callers continue to use `get_watchlist_service()` as a
compatibility surface. Any future adapter-aware cleanup must be created as a
separate child packet with its own impact evidence, exact write scope, tests,
rollback plan, and review gate.

## Verification Recorded Before Merge

Local verification from the implementation packet:

| Check | Result |
|---|---|
| TDD red run | 3 expected failures before implementation |
| `ruff check web/backend/app/services/watchlist_service.py web/backend/app/api/watchlist.py web/backend/tests/test_watchlist_service_lifecycle_di.py` | passed |
| `black --check web/backend/app/services/watchlist_service.py web/backend/app/api/watchlist.py web/backend/tests/test_watchlist_service_lifecycle_di.py` | passed |
| focused + existing watchlist tests | 42 passed |
| `app.main` / `app.openapi()` smoke with required placeholder env | routes=548, paths=500, operations=536, duplicate_operation_ids=0 |
| Markdown governance | checked_files=2, errors=0 |
| Mainline scope gate | pass=True, violations=[] |
| GitNexus staged/compare checks | low risk, affected_processes=0 |

GitHub PR `#150` checks:

| Check | Result |
|---|---|
| `Validate API Contracts` | pass |
| `Generate TypeScript Types` | pass |
| `Detect Breaking Changes` | pass |
| `Generate Contract Validation Report` | pass |
| `Mainline Governance Gate` | pass |
| `check-compliance` | pass |
| weekly/notify jobs | skipped as expected |

## Current State After Merge

- `watchlist_service.py` is now the third merged route-surface service lifecycle
  DI source pilot after `email_service.py` and `announcement_service.py`.
- `get_watchlist_service()` remains the legacy compatibility getter.
- Seven watchlist group route handlers use injected `WatchlistService`.
- Watchlist adapter/data helper callers remain intentionally unmigrated.
- Issue `#79` remains the parent service lifecycle DI issue and should not be
  moved to implementation-ready state by this closeout.

## Next Gate

Human review of this closeout packet.

If accepted, decide in a separate packet whether to:

1. select a fourth route-surface service DI candidate,
2. create an adapter-aware watchlist helper cleanup packet, or
3. pause the service lifecycle DI sequence and return to another architecture
   workline.

This closeout does not itself authorize any of those follow-up actions.
