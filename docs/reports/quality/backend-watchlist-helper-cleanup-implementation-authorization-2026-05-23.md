# Backend Watchlist Helper Cleanup Implementation Authorization - 2026-05-23

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for-review
- Workline: G2.13 adapter-aware watchlist helper cleanup authorization
- Parent issue: https://github.com/chengjon/mystocks/issues/79
- Parent decision issue: https://github.com/chengjon/mystocks/issues/92
- Current HEAD checked: `0ccf1fc58d531cba8f64cc1031d53875e636a766`
- Source code changed by this packet: no
- Runtime behavior changed by this packet: no
- Tests changed by this packet: no

## Governance Boundary

This document is an implementation authorization packet, not the implementation.
It records the exact scope that may be used by a future adapter-aware watchlist
helper cleanup PR if this packet is reviewed and accepted.

This PR must remain governance-only. It does not authorize backend source edits,
test edits, OpenSpec changes, route/OpenAPI contract changes, PM2 commands,
issue label movement, or movement of issue `#79` / `#92` to `ready-for-agent`.

## Current Issue State

- Issue `#79`: `OPEN`, label `needs-triage`
- Issue `#92`: `OPEN`, labels `enhancement`, `ready-for-human`,
  `ready-for-downstream`
- Issue `#92` remains parent decision context only; this packet does not change
  its disposition.

## Evidence Inputs

- `docs/reports/quality/backend-watchlist-helper-cleanup-next-lane-decision-2026-05-23.md`
- `.planning/codebase/generated/watchlist-helper-cleanup-next-lane-decision-2026-05-23.json`
- PR `#152`: https://github.com/chengjon/mystocks/pull/152
- PR `#152` merge commit:
  `0ccf1fc58d531cba8f64cc1031d53875e636a766`
- Prior route-surface implementation PR `#150`, merged at
  `b14ef8421d8ccd6dfd4a714b2a17d4e1ae971419`
- Current source inspection of:
  - `web/backend/app/services/watchlist_service.py`
  - `web/backend/app/services/data_adapters/watchlist.py`
  - `web/backend/app/services/adapters/watchlist_adapter.py`
  - `web/backend/app/api/watchlist.py`
- Current GitNexus impact snapshots for `WatchlistService`,
  `get_watchlist_service`, and `WatchlistDataSourceAdapter`

## Current-Head Helper Surface

| File | Lines | Current watchlist getter/helper state |
|---|---:|---|
| `web/backend/app/services/watchlist_service.py` | 637 | owns `get_watchlist_service()`, `install_watchlist_service()`, and `get_watchlist_service_dependency()` |
| `web/backend/app/services/data_adapters/watchlist.py` | 289 | has `_get_watchlist_service()` helper and direct getter-backed lazy cache |
| `web/backend/app/services/adapters/watchlist_adapter.py` | 290 | has `_get_watchlist_service()` helper and direct getter-backed lazy cache |
| `web/backend/app/api/watchlist.py` | 677 | route-surface DI already migrated by G2.10; no route handler calls the getter directly |

Current token counts from HEAD `0ccf1fc58d`:

| File | `get_watchlist_service` tokens | `_get_watchlist_service` tokens | `Depends(...)` tokens | provider/app-state tokens |
|---|---:|---:|---:|---:|
| `watchlist_service.py` | 3 | 0 | 0 | 8 |
| `data_adapters/watchlist.py` | 11 | 9 | 0 | 0 |
| `adapters/watchlist_adapter.py` | 11 | 9 | 0 | 0 |
| `api/watchlist.py` | 8 | 0 | 22 | 8 |

## GitNexus Pre-Edit Snapshot

### `WatchlistService`

- Target: `Class:web/backend/app/services/watchlist_service.py:WatchlistService`
- Risk: `LOW`
- Impacted count: `0`
- Affected processes: `0`

### `get_watchlist_service`

- Target: `Function:web/backend/app/services/watchlist_service.py:get_watchlist_service`
- Risk: `MEDIUM`
- Impacted count: `15`
- Direct callers: `9`
- Affected processes: `0`
- Direct affected modules:
  - `Data_adapters`
  - `Adapters`

GitNexus direct callers still include the seven route handlers from the earlier
index, but current source inspection confirms those route handlers are already
using the G2.10 dependency seam. Future implementation must refresh GitNexus
before editing and treat stale graph entries as a reconciliation item, not a
reason to edit route code.

### `WatchlistDataSourceAdapter`

- Target resolved by GitNexus:
  `Class:web/backend/app/services/data_adapters/watchlist.py:WatchlistDataSourceAdapter`
- Risk: `LOW`
- Impacted count: `0`
- Affected processes: `0`

The same class name also exists in
`web/backend/app/services/adapters/watchlist_adapter.py`; future implementation
must use file-disambiguated GitNexus context/impact or direct file-path evidence
before editing either adapter.

## Future Allowed Write Scope

If this authorization packet is accepted, a future implementation PR may edit
only the following paths:

| Path | Allowed purpose |
|---|---|
| `web/backend/app/services/data_adapters/watchlist.py` | Replace direct singleton getter dependency with an adapter-aware provider/factory seam while preserving current behavior by default |
| `web/backend/app/services/adapters/watchlist_adapter.py` | Apply the same adapter-aware provider/factory seam to the parallel adapter wrapper |
| `web/backend/app/services/watchlist_service.py` | Inspect only by default; edit only if a tiny typed provider alias or helper is strictly needed |
| `web/backend/tests/test_watchlist_helper_lifecycle_di.py` | Add focused TDD coverage for adapter/helper provider injection and fallback behavior |
| `docs/reports/quality/backend-watchlist-helper-cleanup-implementation-2026-05-23.md` | Record future implementation evidence |
| `governance/mainline/task-cards/pr-154.yaml` | Record future implementation PR scope |

## Explicitly Forbidden Scope

The future implementation PR must not edit:

- `web/backend/app/api/watchlist.py`
- `web/backend/app/services/email_service.py`
- `web/backend/app/services/announcement_service.py`
- `web/backend/app/services/tradingview_widget_service.py`
- unrelated service lifecycle DI candidates
- OpenSpec change/spec files
- frontend files
- docs/API route contract files
- PM2, Docker, CI, deployment, or runtime configuration

If the future implementation discovers that route code must change, stop and
return for a new authorization packet instead of expanding this scope.

## Future Implementation Shape

The intended implementation is adapter-aware cleanup, not a route-surface DI
rewrite.

The preferred minimal shape is:

1. Preserve `get_watchlist_service()` in `watchlist_service.py` as a compatibility
   getter.
2. In both adapter files, introduce an injectable provider/factory seam sourced
   from constructor config, for example `watchlist_service_provider`.
3. Keep current lazy default behavior by using `get_watchlist_service` as the
   default provider when no explicit provider is supplied and `mode != "mock"`.
4. Keep mock mode returning `None` for the real service unless an explicit test
   provider is supplied.
5. Avoid touching route handlers because G2.10 already completed the route
   dependency seam.

The implementation should prefer a small local seam over a new abstraction unless
the future diff proves both adapter files can share a helper without widening
scope.

## Required Future TDD Tests

Future implementation must be test-first. Suggested initial failing tests:

1. `data_adapters/watchlist.py` adapter uses an injected fake provider in live
   mode and does not call the global getter.
2. `adapters/watchlist_adapter.py` adapter uses an injected fake provider in live
   mode and does not call the global getter.
3. Both adapters preserve mock-mode fallback behavior when no provider is
   supplied.
4. Existing watchlist route dependency-injection tests still pass unchanged.

Suggested future commands:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_helper_lifecycle_di.py -q -n 0 --tb=short --no-cov
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist_service_lifecycle_di.py -q -n 0 --tb=short --no-cov
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_watchlist.py -q -n 0 --tb=short --no-cov
```

## Required Future Quality Gates

Before future source edits:

- read `architecture/STANDARDS.md`
- refresh current branch/HEAD state
- run GitNexus context/impact for:
  - `get_watchlist_service`
  - `WatchlistDataSourceAdapter` in each adapter file
  - any concrete helper symbol selected for edit
- if any impact is `HIGH` or `CRITICAL`, stop and return for review

After future source edits:

- run the focused TDD commands above
- run ruff on touched backend files
- run app import/OpenAPI smoke if the future diff touches imports broadly
- run GitNexus `detect_changes(scope="staged")`
- run mainline scope gate against the future PR task card

## Rollback Plan

The future implementation rollback is straightforward:

1. revert the future implementation commit,
2. restore both adapter helper methods to direct `get_watchlist_service()` lazy
   getter behavior,
3. rerun the focused watchlist helper and route DI tests,
4. record rollback evidence in the future implementation report.

## Next Gate

Human review of this G2.13 authorization packet.

If accepted, create a separate G2.14 implementation branch limited to this
packet's allowed paths. Until then, backend source edits remain locked.
