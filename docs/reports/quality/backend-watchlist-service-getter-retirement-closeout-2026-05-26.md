# Backend WatchlistService Getter Retirement Closeout - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Decision

G2.132 records the G2.131 WatchlistService getter-retirement implementation as merged and closes the WatchlistService getter-retirement lane.

This closeout is governance-only. It does not modify runtime code, tests, API routes, OpenAPI exposure, PM2 workflow, OpenSpec changes, GitHub issue labels, or product behavior.

## Parent Merge

| Field | Value |
|---|---|
| Parent PR | `#284` |
| State | `MERGED` |
| Merged at | `2026-05-26T03:30:49Z` |
| Merge commit | `ccadd5e0560c4fa1fab7fae130a8b64e624352bc` |
| Title | `G2.131 Retire WatchlistService getter singleton` |
| URL | `https://github.com/chengjon/mystocks/pull/284` |

Current branch HEAD for this closeout is `ccadd5e0560c4fa1fab7fae130a8b64e624352bc`.

## Current-Head Scan

The current-head scan confirms the intended retired symbols remain absent and the app-state dependency seam remains present.

| Check | Result |
|---|---:|
| `watchlist_service.py` `get_watchlist_service` definitions | `0` |
| `watchlist_service.py` `_watchlist_service` assignments | `0` |
| `WatchlistService` class preserved | `true` |
| `install_watchlist_service` preserved | `true` |
| `get_watchlist_service_dependency` preserved | `true` |
| Adapter fallback imports | `0` |
| Adapter public getter calls | `0` |
| App/API public getter calls | `0` |
| Watchlist route dependency references | `8` |
| Watchlist route dependency handlers | `7` |

## Verification

| Gate | Command | Result |
|---|---|---|
| Parent PR state | `gh pr view 284 --json number,state,mergedAt,mergeCommit,title,url` | `MERGED` at `2026-05-26T03:30:49Z` |
| Current-head scan | Scripted scan over `watchlist_service.py`, watchlist adapters, and `app/api/watchlist.py` | Getter definitions `0`, singleton assignments `0`, adapter fallback imports `0`, route dependency handlers `7` |
| Focused watchlist tests | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_service_getter_retirement.py web/backend/tests/test_watchlist_service_lifecycle_di.py web/backend/tests/test_watchlist_helper_lifecycle_di.py web/backend/tests/test_adapter_mock_fallback_controls.py web/backend/tests/test_logging_noise_regressions.py -q --no-cov --tb=short` | `28 passed in 3.29s` |
| Health route conflicts | `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `120 passed in 73.83s` |

## Scope Boundary

Allowed closeout paths:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/watchlist-service-getter-retirement-closeout-2026-05-26.json`
- `docs/reports/quality/backend-watchlist-service-getter-retirement-closeout-2026-05-26.md`
- `governance/mainline/task-cards/pr-285.yaml`

Forbidden paths remain locked for this closeout:

- `web/backend/**`
- `web/frontend/**`
- `src/**`
- `tests/**`
- `docs/api/**`
- `docs/guides/**`
- `config/**`
- `scripts/**`
- `openspec/changes/**`
- `openspec/specs/**`

## Closeout Result

The WatchlistService getter-retirement lane is ready to close after this governance PR is reviewed and merged.

The next steward-tree gate is a fresh remaining-candidate scan before selecting another service lifecycle implementation lane. The next scan must treat `WatchlistService` as a completed retired-getter case and must not reopen the already accepted route dependency seam unless a current-head contradiction appears.
