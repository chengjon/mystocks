# Backend Service Lifecycle DI Third Candidate Selection - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for-review
- Workline: G2.8 service lifecycle DI third candidate selection
- Parent issue: https://github.com/chengjon/mystocks/issues/79
- Parent decision issue: https://github.com/chengjon/mystocks/issues/92
- Current HEAD checked: `112487d96ad07ad3212c71e729395f2c8accfed1`
- Current branch: `g2-8-third-service-di-candidate-selection`
- Generated artifact: `.planning/codebase/generated/service-lifecycle-di-third-candidate-selection-2026-05-22.json`

Boundary note: This package is a candidate-selection packet only. It does not
authorize backend source edits, frontend source edits, tests, generated client
updates, docs/API edits, OpenSpec proposal creation, issue label changes, PM2
commands, runtime rollout, or movement of issue `#79` or issue `#92` to
`ready-for-agent`.

## Input State

Two service lifecycle DI source pilots are now merged and recorded:

| Pilot | PR | Merge commit | Closeout |
|---|---:|---|---|
| `email_service.py` | `#142` | `20657e6e86a3423b15c67b6a8d6e165fbaa47b72` | PR `#143` |
| `announcement_service.py` | `#146` | `517f47cb86aa32d32514d8588a653b08898f72c7` | PR `#147` |

Current GitHub state checked during this packet:

| Issue | State | Labels | Meaning for this packet |
|---|---|---|---|
| `#79` | OPEN | `needs-triage` | Parent service lifecycle DI lane remains open, but no third service source edit is authorized |
| `#92` | OPEN | `enhancement`, `ready-for-human`, `ready-for-downstream` | Downstream decision governance remains active; this packet is a review input only |

## Candidate Source

The accepted G2.1 candidate classification and G2.4 second-candidate selection
remain the source for narrowing the next choice:

- `backend-service-lifecycle-di-candidate-classification-2026-05-22.md`
- `.planning/codebase/generated/service-lifecycle-di-candidate-classification-2026-05-22.json`
- `backend-service-lifecycle-di-second-candidate-selection-2026-05-22.md`
- `.planning/codebase/generated/service-lifecycle-di-second-candidate-selection-2026-05-22.json`

After `email_service.py` and `announcement_service.py`, the remaining practical
candidate is `watchlist_service.py`, but it is not a clean single-route-surface
candidate.

## Current-HEAD Candidate Comparison

| Candidate | Getter | GitNexus risk | Direct callers | Extra impacted symbols | Direct owner surface | Selection result |
|---|---|---:|---:|---:|---|---|
| `watchlist_service.py` | `get_watchlist_service` | MEDIUM | 9 | 6 transitive adapter/data symbols | route + adapter/data helper surfaces | Candidate only for a split route-surface authorization packet |
| `tradingview_widget_service.py` | `get_tradingview_service` | LOW | 1 | 0 | already has provider/app-state pattern | Reference evidence only; no migration candidate |

## GitNexus Evidence

### `WatchlistService`

- Target: `Class:web/backend/app/services/watchlist_service.py:WatchlistService`
- Risk: LOW
- Direct callers: 0
- Processes affected: 0

### `get_watchlist_service`

- Target: `Function:web/backend/app/services/watchlist_service.py:get_watchlist_service`
- Risk: MEDIUM
- Impacted count: 15
- Direct callers: 9
- Processes affected: 0
- Modules affected: `Data_adapters`, `Adapters`

Direct caller files:

- `web/backend/app/api/watchlist.py`
- `web/backend/app/services/data_adapters/watchlist.py`
- `web/backend/app/services/adapters/watchlist_adapter.py`

The route direct callers are:

- `get_user_groups`
- `create_group`
- `update_group`
- `delete_group`
- `get_watchlist_by_group`
- `move_stock_to_group`
- `get_watchlist_with_groups`

The adapter/data-layer direct callers are helper functions named
`_get_watchlist_service` in:

- `web/backend/app/services/data_adapters/watchlist.py`
- `web/backend/app/services/adapters/watchlist_adapter.py`

## Current Shape Evidence

| File | Lines | Current direct getter surface | Existing DI signal | Disposition |
|---|---:|---:|---:|---|
| `web/backend/app/services/watchlist_service.py` | 621 | `_watchlist_service = None`; compatibility getter exists | no app-state provider yet | candidate service file |
| `web/backend/app/api/watchlist.py` | 674 | 7 route-level getter calls | 15 existing `Depends(...)` uses | route-surface candidate |
| `web/backend/app/services/data_adapters/watchlist.py` | 289 | helper uses getter | no FastAPI route DI surface | leave out of route-surface pilot |
| `web/backend/app/services/adapters/watchlist_adapter.py` | 290 | helper uses getter | no FastAPI route DI surface | leave out of route-surface pilot |
| `web/backend/app/services/tradingview_widget_service.py` | 358 | provider pattern already exists | `install_tradingview_service`, `get_tradingview_service_dependency` | reference only |

## Recommendation

Prepare a future G2.9 authorization packet for a route-surface-only
`watchlist_service.py` lifecycle DI pilot.

That packet should not claim full getter retirement. It should authorize only:

- adding app-state provider helpers to `watchlist_service.py`
- converting the 7 direct route handlers in `web/backend/app/api/watchlist.py`
  to inject `WatchlistService`
- adding focused tests for watchlist route dependency injection
- keeping adapter/data-layer `_get_watchlist_service` helper calls as
  compatibility callers

The adapter/data-layer files should remain out of scope unless a separate
adapter-aware authorization packet explicitly accepts their broader surface.

## Future G2.9 Authorization Packet Requirements

If this G2.8 selection is accepted, the next packet must define:

- exact backend source write scope
- exact test write scope
- route functions to convert from direct getter calls to dependency injection
- app-state/provider installation pattern
- compatibility getter retention rule
- adapter/data-layer compatibility-retention rule
- GitNexus pre-edit impact commands
- rollback plan
- targeted tests
- lint and import smoke commands
- forbidden scope

Minimum future write scope to evaluate, not yet authorized:

- `web/backend/app/services/watchlist_service.py`
- `web/backend/app/api/watchlist.py`
- focused tests for watchlist route dependency behavior

Explicitly out of scope for the future G2.9 packet unless separately approved:

- `web/backend/app/services/data_adapters/watchlist.py`
- `web/backend/app/services/adapters/watchlist_adapter.py`
- `email_service.py`
- `announcement_service.py`
- `tradingview_widget_service.py`
- route/OpenAPI contract rewrites
- docs/API edits
- generated clients
- PM2 commands
- issue label changes
- OpenSpec proposal/spec creation

## Next Gate

Human review of this G2.8 selection package.

If accepted, create a separate G2.9 implementation authorization package for
the route-surface-only `watchlist_service.py` pilot. Source edits remain locked
until that G2.9 packet is reviewed and explicitly approved.
