# Backend Watchlist Service Lifecycle DI Implementation Authorization - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for-review
- Workline: G2.9 service lifecycle DI watchlist route-surface authorization
- Parent issue: https://github.com/chengjon/mystocks/issues/79
- Parent decision issue: https://github.com/chengjon/mystocks/issues/92
- Current HEAD checked: `ccc4982cd11b47996c6534f087b0c9cb3783877a`
- Source code changed by this packet: no
- Runtime behavior changed by this packet: no
- Tests changed by this packet: no

## Governance Boundary

This document is an implementation authorization packet, not the implementation.
It records the exact scope that may be used by a future watchlist route-surface
DI implementation PR if this packet is reviewed and accepted.

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

- `docs/reports/quality/backend-service-lifecycle-di-third-candidate-selection-2026-05-22.md`
- `.planning/codebase/generated/service-lifecycle-di-third-candidate-selection-2026-05-22.json`
- PR `#148`: https://github.com/chengjon/mystocks/pull/148
- PR `#148` merge commit: `ccc4982cd11b47996c6534f087b0c9cb3783877a`
- Current-head GitNexus impact checks for `WatchlistService` and
  `get_watchlist_service`
- Current source inspection of:
  - `web/backend/app/services/watchlist_service.py`
  - `web/backend/app/api/watchlist.py`
  - `web/backend/app/services/data_adapters/watchlist.py`
  - `web/backend/app/services/adapters/watchlist_adapter.py`

## Candidate Decision

`watchlist_service.py` is approved only as a route-surface DI authorization
candidate.

The adapter and data-layer helper callers of `get_watchlist_service` are not
part of this authorization. They remain compatibility surfaces unless a future
adapter-aware packet names them explicitly and supplies separate impact,
verification, and rollback gates.

## GitNexus Pre-Edit Snapshot

### `WatchlistService`

- Target: `Class:web/backend/app/services/watchlist_service.py:WatchlistService`
- Direction: upstream
- Risk: LOW
- Impacted symbols: 0
- Direct callers: 0
- Affected processes: 0
- Affected modules: 0

### `get_watchlist_service`

- Target:
  `Function:web/backend/app/services/watchlist_service.py:get_watchlist_service`
- Direction: upstream
- Risk: MEDIUM
- Impacted symbols: 15
- Direct callers: 9
- Affected processes: 0
- Affected modules: 2
- Direct affected modules:
  - `Data_adapters`
  - `Adapters`

Direct callers:

| File | Symbol | Future disposition |
|---|---|---|
| `web/backend/app/api/watchlist.py` | `get_user_groups` | route-surface DI candidate |
| `web/backend/app/api/watchlist.py` | `create_group` | route-surface DI candidate |
| `web/backend/app/api/watchlist.py` | `update_group` | route-surface DI candidate |
| `web/backend/app/api/watchlist.py` | `delete_group` | route-surface DI candidate |
| `web/backend/app/api/watchlist.py` | `get_watchlist_by_group` | route-surface DI candidate |
| `web/backend/app/api/watchlist.py` | `move_stock_to_group` | route-surface DI candidate |
| `web/backend/app/api/watchlist.py` | `get_watchlist_with_groups` | route-surface DI candidate |
| `web/backend/app/services/data_adapters/watchlist.py` | `_get_watchlist_service` | retain as compatibility caller |
| `web/backend/app/services/adapters/watchlist_adapter.py` | `_get_watchlist_service` | retain as compatibility caller |

Transitive adapter/data symbols:

| Depth | File | Symbol | Future disposition |
|---:|---|---|---|
| 2 | `web/backend/app/services/data_adapters/watchlist.py` | `_fetch_watchlist_data` | out of scope |
| 2 | `web/backend/app/services/data_adapters/watchlist.py` | `health_check` | out of scope |
| 2 | `web/backend/app/services/adapters/watchlist_adapter.py` | `_fetch_watchlist_data` | out of scope |
| 2 | `web/backend/app/services/adapters/watchlist_adapter.py` | `health_check` | out of scope |
| 3 | `web/backend/app/services/data_adapters/watchlist.py` | `get_data` | out of scope |
| 3 | `web/backend/app/services/adapters/watchlist_adapter.py` | `get_data` | out of scope |

## Current Route Surface

Current source facts at HEAD `ccc4982cd11b47996c6534f087b0c9cb3783877a`:

| File | Lines | Current direct getter surface | Existing DI signal |
|---|---:|---:|---|
| `web/backend/app/services/watchlist_service.py` | 621 | one singleton getter and `_watchlist_service = None` | no app-state provider |
| `web/backend/app/api/watchlist.py` | 674 | seven direct route-body calls to `get_watchlist_service()` | existing FastAPI `Depends(...)` usage for auth and request dependencies |
| `web/backend/app/services/data_adapters/watchlist.py` | 289 | adapter helper uses `get_watchlist_service` | out of scope |
| `web/backend/app/services/adapters/watchlist_adapter.py` | 290 | adapter helper uses `get_watchlist_service` | out of scope |

Route-surface functions that may be migrated by a future implementation:

| Function | Route surface | Current getter line | Future allowed action |
|---|---|---:|---|
| `get_user_groups` | `GET /groups` | 497 | inject `WatchlistService` through route dependency |
| `create_group` | `POST /groups` | 520 | inject `WatchlistService` through route dependency |
| `update_group` | `PUT /groups/{group_id}` | 555 | inject `WatchlistService` through route dependency |
| `delete_group` | `DELETE /groups/{group_id}` | 584 | inject `WatchlistService` through route dependency |
| `get_watchlist_by_group` | `GET /group/{group_id}` | 609 | inject `WatchlistService` through route dependency |
| `move_stock_to_group` | `PUT /move` | 632 | inject `WatchlistService` through route dependency |
| `get_watchlist_with_groups` | `GET /with-groups` | 667 | inject `WatchlistService` through route dependency |

## Future Allowed Write Scope

If this packet is accepted, a separate future implementation PR may edit only:

- `web/backend/app/services/watchlist_service.py`
- `web/backend/app/api/watchlist.py`
- one focused watchlist lifecycle DI test file, preferably under
  `web/backend/tests/`
- one implementation report under `docs/reports/quality/`
- one future implementation task card under `governance/mainline/task-cards/`
- this steward tree, only to record implementation evidence after that future
  implementation is complete

The future implementation PR must remain route-surface-only. It may not treat
this packet as permission to migrate adapter/data-layer helpers.

## Explicitly Forbidden Scope

The future implementation PR must not edit:

- `web/backend/app/services/data_adapters/watchlist.py`
- `web/backend/app/services/adapters/watchlist_adapter.py`
- `web/backend/app/services/email_service.py`
- `web/backend/app/services/email_notification_service.py`
- `web/backend/app/services/announcement_service.py`
- `web/backend/app/services/tradingview_widget_service.py`
- `web/backend/app/services/strategy_service.py`
- `web/backend/app/services/tdx_service.py`
- `web/backend/app/services/stock_search_service/`
- `web/backend/app/services/monitoring_service.py`
- `web/backend/app/services/technical_analysis_service.py`
- frontend source
- `docs/api/`
- generated clients
- OpenSpec proposal, task, or spec files
- PM2 scripts or runtime process configuration
- route paths, methods, response models, request models, or OpenAPI exposure
  policy

## Future Implementation Shape

### Service Provider Pattern

The future source implementation may follow the already proven email and
announcement service pattern:

1. Add a watchlist app-state key in `watchlist_service.py`.
2. Add `install_watchlist_service(app, service=None)` to install or reuse the
   service from `app.state`.
3. Add `get_watchlist_service_dependency(request)` for FastAPI route
   injection.
4. Retain `get_watchlist_service()` as the compatibility singleton getter for
   adapter/data-layer helper callers.
5. Do not change `WatchlistService` business behavior.

### Route Injection Pattern

The future source implementation may update only the seven route handlers listed
above so they receive:

```python
service: WatchlistService = Depends(get_watchlist_service_dependency)
```

The future implementation must not change route path, method, request shape,
response shape, response model, OpenAPI examples, error contract, or auth
dependency behavior.

## Required Future Tests

A future implementation PR must use TDD and include a red/green test proving the
route dependency can be overridden without touching the module-level singleton.

Minimum test expectations:

- a focused watchlist lifecycle DI test with a fake `WatchlistService`
- proof that at least one migrated route uses `app.dependency_overrides` for the
  watchlist dependency
- proof that the route response contract remains unchanged for the exercised
  route
- regression coverage that the compatibility `get_watchlist_service()` getter
  still returns a service for non-route callers

Suggested future verification commands:

```bash
ruff check web/backend/app/services/watchlist_service.py web/backend/app/api/watchlist.py
pytest -o addopts= web/backend/tests/test_watchlist_service_lifecycle_di.py -q --no-cov
pytest -o addopts= web/backend/tests/test_watchlist_service_logging.py -q --no-cov
```

If the future implementation touches a currently covered route test, it should
also run the smallest existing watchlist route suite that exercises that path.

## Required Future Quality Gates

Before the future source implementation edits any symbol, it must run GitNexus
impact on:

- `WatchlistService`
- `get_watchlist_service`
- any route function that will be modified

Before future commit, it must stage only the intended files and run:

- `gitnexus_detect_changes(scope="staged")`
- path-limited `git diff --cached --check`
- markdown governance for any changed report/task card
- JSON validity for any generated evidence artifact
- mainline scope gate for the future task card

If GitNexus reports HIGH or CRITICAL risk for the staged implementation, the
future PR must stop and return to review instead of widening the batch.

## Rollback Plan

Rollback of the future implementation should be a path-limited revert that:

1. Restores the seven route functions to direct `get_watchlist_service()` calls.
2. Removes the new watchlist route dependency test file.
3. Removes the provider functions as a single unit if they are not retained.
4. Leaves adapter/data-layer helper callers unchanged.
5. Leaves route paths, request models, response bodies, error contracts, and
   OpenAPI behavior unchanged.

Because this packet performs no source edits, rollback for this PR is simply to
revert this authorization report, JSON artifact, steward tree update, and task
card.

## Next Gate

Human review of this G2.9 authorization packet.

If accepted, create a separate implementation worktree and PR. That future PR
may edit only the allowed write scope above and must produce an implementation
report before closeout. No source implementation is authorized by this packet
until that review acceptance is explicit.
