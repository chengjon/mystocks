# Backend Watchlist Helper Cleanup Implementation - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-prepared-for-review
- Workline: G2.14 adapter-aware watchlist helper cleanup implementation
- Parent authorization PR: https://github.com/chengjon/mystocks/pull/153
- Parent authorization merge commit:
  `938682debb90a25392ca208e706d8388d06de786`
- Current implementation branch: `g2-14-watchlist-helper-cleanup-implementation`
- Implementation PR: https://github.com/chengjon/mystocks/pull/154
- PR checks at creation: Mainline Governance Gate passed; check-compliance passed
- Source code changed by this packet: yes, within authorized helper scope
- Runtime route/OpenAPI contract changed by this packet: no
- OpenSpec files changed by this packet: no

## Governance Boundary

This implementation follows the G2.13 authorization packet. It is limited to the
adapter-aware watchlist helper cleanup lane and does not authorize any fourth
service lifecycle DI candidate.

This PR must not be treated as permission to edit route code, OpenAPI contracts,
frontend code, PM2/runtime configuration, issue labels, or unrelated services.

## Implemented Scope

| Path | Change |
|---|---|
| `web/backend/app/services/data_adapters/watchlist.py` | Added constructor-configured `watchlist_service_provider` seam while preserving default lazy getter fallback |
| `web/backend/app/services/adapters/watchlist_adapter.py` | Added the same provider seam to the parallel watchlist adapter wrapper |
| `web/backend/tests/test_watchlist_helper_lifecycle_di.py` | Added focused TDD coverage for live-mode provider injection, mock-mode explicit provider behavior, and mock-mode no-provider fallback |

No changes were made to `web/backend/app/api/watchlist.py`.

## TDD Evidence

Red run before implementation:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_helper_lifecycle_di.py -q -n 0 --tb=short --no-cov
4 failed, 2 passed
```

Expected red failures:

- both adapter classes ignored `watchlist_service_provider` in live mode and
  called the global getter,
- both adapter classes returned `None` in mock mode even when an explicit
  provider was supplied.

Green run after implementation:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_helper_lifecycle_di.py -q -n 0 --tb=short --no-cov
6 passed in 1.45s
```

## Verification

| Check | Result |
|---|---|
| `black` on touched Python files | passed; one adapter file reformatted |
| `ruff check` on touched Python files | passed |
| `test_watchlist_helper_lifecycle_di.py` | 6 passed |
| `test_watchlist_service_lifecycle_di.py` | 3 passed |
| `test_watchlist_service_logging.py` | 3 passed |
| placeholder-env `app.main` / `app.openapi()` smoke | `routes=548`, `paths=500`, `operations=536`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0` |

## Current-Head Helper Surface After Implementation

| File | Lines | Provider seam |
|---|---:|---|
| `web/backend/app/services/data_adapters/watchlist.py` | 295 | `watchlist_service_provider` accepted from constructor config |
| `web/backend/app/services/adapters/watchlist_adapter.py` | 294 | `watchlist_service_provider` accepted from constructor config |
| `web/backend/app/services/watchlist_service.py` | 637 | unchanged |
| `web/backend/app/api/watchlist.py` | 677 | unchanged route-surface DI |

The adapter helper methods still preserve the compatibility fallback to
`get_watchlist_service()` when no explicit provider is supplied and the adapter
is not in mock mode.

## GitNexus Evidence

Pre-edit impact/context checks:

- `get_watchlist_service`: `MEDIUM`, impacted count `15`, affected processes `0`
- `WatchlistDataSourceAdapter` in `data_adapters/watchlist.py`: `LOW`,
  impacted count `0`, affected processes `0`
- `WatchlistDataSourceAdapter` in `adapters/watchlist_adapter.py`: context
  resolved by file path; no execution flows reported

The implementation did not edit `watchlist_service.py` and did not edit route
handlers, so the stale GitNexus route direct-caller entries remain a graph
freshness concern rather than a code change requirement.

## Rollback Plan

Revert the implementation commit to restore both adapter helper methods to the
previous direct lazy getter behavior. Then rerun:

```text
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_helper_lifecycle_di.py -q -n 0 --tb=short --no-cov
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_service_lifecycle_di.py -q -n 0 --tb=short --no-cov
```

## Next Gate

Human review of PR #154.

If accepted and merged, create a separate G2.15 closeout packet to update the
steward tree with the merge commit, final checks, and next service lifecycle DI
decision gate.
