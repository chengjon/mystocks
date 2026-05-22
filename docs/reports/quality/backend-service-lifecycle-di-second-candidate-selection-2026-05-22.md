# Backend Service Lifecycle DI Second Candidate Selection - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for-review
- Workline: G2.4 service lifecycle DI second candidate selection
- Parent issue: https://github.com/chengjon/mystocks/issues/79
- Parent decision issue: https://github.com/chengjon/mystocks/issues/92
- Current HEAD checked: `68da82084266ca7f9b7be9f5b55da7ac5e64fbd7`
- Current branch: `g2-4-steward-tree-retrospective-next-candidate`
- Generated artifact: `.planning/codebase/generated/service-lifecycle-di-second-candidate-selection-2026-05-22.json`

Boundary note: This package is a candidate-selection packet only. It does not
authorize backend source edits, frontend source edits, tests, generated client
updates, docs/API edits, OpenSpec proposal creation, issue label changes, PM2
commands, runtime rollout, or movement of issue `#79` or issue `#92` to
`ready-for-agent`.

## Input State

The first service lifecycle DI implementation pilot is complete:

- PR `#140`: candidate classification accepted
- PR `#141`: `email_service.py` implementation authorization accepted
- PR `#142`: `email_service.py` lifecycle DI implementation merged at
  `20657e6e86a3423b15c67b6a8d6e165fbaa47b72`
- PR `#143`: closeout recorded at
  `68da82084266ca7f9b7be9f5b55da7ac5e64fbd7`

Current GitHub state checked during this packet:

| Issue | State | Labels | Meaning for this packet |
|---|---|---|---|
| `#79` | OPEN | `needs-triage` | Parent service lifecycle DI lane remains open, but no second service source edit is authorized |
| `#92` | OPEN | `enhancement`, `ready-for-human`, `ready-for-downstream` | Downstream decision governance remains active; this packet is a review input only |

## Candidate Source

The current candidate source is the accepted G2.1 classification:

- `backend-service-lifecycle-di-candidate-classification-2026-05-22.md`
- `.planning/codebase/generated/service-lifecycle-di-candidate-classification-2026-05-22.json`

That packet deferred two medium candidates after `email_service.py`:

- `web/backend/app/services/announcement_service.py`
- `web/backend/app/services/watchlist_service.py`

This packet rechecks those two candidates at current HEAD after the first pilot
was merged and recorded.

## Current-HEAD Candidate Comparison

| Candidate | Getter | GitNexus risk | Direct callers | Extra impacted symbols | Direct owner surface | Selection result |
|---|---|---:|---:|---:|---|---|
| `web/backend/app/services/announcement_service.py` | `get_announcement_service` | MEDIUM | 11 | 0 transitive symbols reported | `web/backend/app/api/announcement/routes.py` | Recommended next authorization candidate |
| `web/backend/app/services/watchlist_service.py` | `get_watchlist_service` | MEDIUM | 9 | 6 transitive symbols through adapter/data layers | `web/backend/app/api/watchlist.py`, `web/backend/app/services/data_adapters/watchlist.py`, `web/backend/app/services/adapters/watchlist_adapter.py` | Defer |

## GitNexus Evidence

### `get_announcement_service`

- Target: `Function:web/backend/app/services/announcement_service.py:get_announcement_service`
- Risk: MEDIUM
- Impacted count: 11
- Direct callers: 11
- Processes affected: 0
- Modules affected: 1 (`Announcement`)
- Direct caller file: `web/backend/app/api/announcement/routes.py`

Direct caller functions:

- `fetch_announcements`
- `get_announcements`
- `get_today_announcements`
- `get_important_announcements`
- `get_announcement_stats`
- `get_monitor_rules`
- `create_monitor_rule`
- `update_monitor_rule`
- `delete_monitor_rule`
- `get_triggered_records`
- `evaluate_monitor_rules`

### `get_watchlist_service`

- Target: `Function:web/backend/app/services/watchlist_service.py:get_watchlist_service`
- Risk: MEDIUM
- Impacted count: 15
- Direct callers: 9
- Processes affected: 0
- Modules affected: 2 (`Data_adapters`, `Adapters`)
- Direct caller files:
  - `web/backend/app/api/watchlist.py`
  - `web/backend/app/services/data_adapters/watchlist.py`
  - `web/backend/app/services/adapters/watchlist_adapter.py`

`watchlist_service.py` remains a valid future candidate, but it is not the best
second pilot because it crosses route and adapter/data-layer helper surfaces.

## Local Shape Evidence

| File | Lines | Singleton pattern | Getter calls in file | Route decorators | Notes |
|---|---:|---|---:|---:|---|
| `web/backend/app/services/announcement_service.py` | 530 | `_announcement_service = None` | 1 | 0 | Service file only |
| `web/backend/app/api/announcement/routes.py` | 595 | none | 11 | 14 | Single direct route owner surface |
| `web/backend/app/services/watchlist_service.py` | 621 | `_watchlist_service = None` | 1 | 0 | Service file only |
| `web/backend/app/api/watchlist.py` | 674 | none | 7 | 15 | Existing route-level dependency use exists, but service getter remains direct |
| `web/backend/app/services/data_adapters/watchlist.py` | 289 | none | 10 | 0 | Adapter/data layer coupling |
| `web/backend/app/services/adapters/watchlist_adapter.py` | 290 | none | 10 | 0 | Adapter/data layer coupling |

## Recommendation

Select `web/backend/app/services/announcement_service.py` as the next service
lifecycle DI implementation authorization candidate.

This is not an approval to edit source. It only means the next package, if the
human maintainer accepts this selection, should be a G2.5 implementation
authorization packet for `announcement_service.py`.

## Required Future G2.5 Authorization Packet

If this selection is accepted, the next packet must define:

- exact backend source write scope
- exact test write scope
- route functions to convert from direct getter calls to dependency injection
- app-state/provider installation pattern
- compatibility getter retention rule
- GitNexus pre-edit impact commands
- rollback plan
- targeted tests
- lint and import smoke commands
- forbidden scope

Minimum future write scope to evaluate, not yet authorized:

- `web/backend/app/services/announcement_service.py`
- `web/backend/app/api/announcement/routes.py`
- focused tests for announcement service lifecycle dependency behavior

Explicitly out of scope for the next authorization packet unless separately
approved:

- `watchlist_service.py`
- `email_service.py`
- `email_notification_service.py`
- adapter/data-layer services
- route/OpenAPI contract rewrites
- docs/API edits
- generated clients
- PM2 commands
- issue label changes
- OpenSpec proposal/spec creation

## Next Gate

Human review of this G2.4 selection package.

If accepted, create a separate G2.5 implementation authorization package for
`announcement_service.py`. Source edits remain locked until that G2.5 packet is
reviewed and explicitly approved.
