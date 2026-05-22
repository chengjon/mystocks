# Backend Watchlist Helper Cleanup Closeout - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: completed-and-recorded
- Workline: G2.15 adapter-aware watchlist helper cleanup closeout
- Implementation PR: https://github.com/chengjon/mystocks/pull/154
- Implementation merge commit:
  `1dcb394a49a9d95e939b2119acc431b825954036`
- Implementation commit:
  `fad638f636060237845ca893dbd16420c4ef92af`
- Parent authorization PR: https://github.com/chengjon/mystocks/pull/153
- Parent authorization merge commit:
  `938682debb90a25392ca208e706d8388d06de786`
- Closeout branch: `g2-15-watchlist-helper-cleanup-closeout`
- Closeout PR: https://github.com/chengjon/mystocks/pull/155
- Closeout PR checks at creation: Mainline Governance Gate passed;
  check-compliance passed
- Recorded at: `2026-05-23T03:05:02+08:00`

## Governance Boundary

This closeout is governance bookkeeping only. It records that the G2.14
adapter-aware watchlist helper cleanup implementation was reviewed through PR
checks and merged. It does not authorize another service lifecycle DI candidate,
OpenSpec changes, issue label movement, PM2/runtime work, frontend work,
route/OpenAPI contract changes, or additional source edits.

## Completed Scope

PR `#154` implemented the G2.13-authorized helper cleanup scope:

- `web/backend/app/services/data_adapters/watchlist.py`
  - added constructor-configured `watchlist_service_provider` support
  - preserved lazy default `get_watchlist_service()` fallback
  - preserved mock fallback behavior while allowing explicit provider injection
- `web/backend/app/services/adapters/watchlist_adapter.py`
  - added the same provider seam and compatibility fallback behavior
- `web/backend/tests/test_watchlist_helper_lifecycle_di.py`
  - covers provider injection in live mode for both helper adapter classes
  - covers explicit provider support in mock mode
  - covers unchanged mock mode behavior when no provider is configured

No route handler, OpenAPI schema, frontend, config, script, OpenSpec, PM2, or
runtime process-state files were changed by PR `#154`.

## Verification Recorded Before Merge

Local verification from the implementation packet:

| Check | Result |
|---|---|
| TDD red run | `4 failed, 2 passed` before implementation |
| focused helper tests | `6 passed` |
| route DI regression tests | `3 passed` |
| watchlist logging regression tests | `3 passed` |
| touched-file `ruff check` | passed |
| touched-file `black --check` | passed |
| Markdown governance | checked_files=2, errors=0 |
| `app.main` / `app.openapi()` smoke with required placeholder env | routes=548, paths=500, operations=536, duplicate_operation_ids=0, duplicate_operation_id_warnings=0 |
| Mainline scope gate | pass=True |
| GitNexus compare against `origin/wip/root-dirty-20260403` | low risk, changed_files=6, affected_processes=0 |

GitHub PR `#154` checks:

| Check | Result |
|---|---|
| Mainline Governance Gate | pass |
| `check-compliance` | pass |
| `weekly-full-scan` | skipped as expected |

## Current-Head Verification After Merge

The closeout branch is based on the PR `#154` merge commit:

```text
1dcb394a4 Merge pull request #154 from chengjon/g2-14-watchlist-helper-cleanup-implementation
```

Verification rerun on this merged HEAD:

| Check | Result |
|---|---|
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_helper_lifecycle_di.py -q -n 0 --tb=short --no-cov` | 6 passed |
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_service_lifecycle_di.py -q -n 0 --tb=short --no-cov` | 3 passed |
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_service_logging.py -q -n 0 --tb=short --no-cov` | 3 passed |
| `ruff check web/backend/app/services/data_adapters/watchlist.py web/backend/app/services/adapters/watchlist_adapter.py web/backend/tests/test_watchlist_helper_lifecycle_di.py` | passed |
| `app.main` / `app.openapi()` smoke with required placeholder env | routes=548, paths=500, operations=536, duplicate_operation_ids=0, duplicate_operation_id_warnings=0 |

## Current State After Merge

- Both watchlist helper adapter files now support constructor-configured
  `watchlist_service_provider` injection.
- Default `get_watchlist_service()` compatibility fallback remains available.
- `watchlist_service.py` remains the route-surface app-state provider source from
  the earlier G2.10/G2.11 lane.
- Watchlist route handlers remain unchanged by this helper cleanup.
- Issue `#79` remains `OPEN` with `needs-triage`.
- Issue `#92` remains `OPEN` with `enhancement`, `ready-for-human`, and
  `ready-for-downstream`.

## Next Gate

Human review of this G2.15 closeout packet.

If accepted, create a separate G2.16 decision packet before any further service
lifecycle DI source edits. That packet should decide whether to select another
route-surface service candidate, run another adapter-aware cleanup, or pause the
service lifecycle DI sequence and return to another architecture workline.
