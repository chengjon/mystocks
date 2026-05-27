# Backend Data Quality / Adapter Cross-Cutting Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review candidate
- Prepared at: `2026-05-28T00:38:03+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `5565e2b0967958c406a4115dc840a9e90a0b2aab`
- Worktree branch: `g2-190-data-quality-adapter-decision`
- Scope: data-quality / adapter cross-cutting decision package
- Source edit authority: none

Boundary note: this package is a design and authorization input only. It does
not authorize backend source edits, frontend edits, test edits, OpenSpec
proposal creation, GitHub issue label changes, adapter constructor migration,
singleton wrapper deletion, or data-quality source implementation.

## Parent State

| Item | State | Evidence |
|---|---|---|
| G2.189 stop-loss provider closeout / candidate refresh | Merged | PR `#342`, merge commit `5565e2b0967958c406a4115dc840a9e90a0b2aab` |
| G2.190 data-quality / adapter cross-cutting decision | For review | This report plus `.planning/codebase/generated/data-quality-adapter-cross-cutting-decision-2026-05-28.json` |

## Why This Is Not A Direct Implementation Lane

`get_data_quality_monitor` is a cross-cutting service singleton surface, not a
small route-local getter.

GitNexus impact for
`web/backend/app/services/_data_quality_monitor_singleton.py:get_data_quality_monitor`
records:

| Metric | Value |
|---|---:|
| Risk | `CRITICAL` |
| Impacted symbols | 24 |
| Direct callers | 20 |
| Affected processes | 7 |
| Affected modules | 4 |

The affected modules span Services, Data_adapters, Api, and Adapters. That means
this surface must be split into owner-specific lanes before source
implementation. G2.190 therefore does not open a source lane.

## Static Inventory

Static inventory at HEAD `5565e2b0967958c406a4115dc840a9e90a0b2aab` found 16
files touching the data-quality monitor surface, with 21
`get_data_quality_monitor()` calls and 2 `monitor_data_quality()` calls.

| Bucket | Files | Getter calls | Monitor calls | Handling |
|---|---:|---:|---:|---|
| Route surface | 1 | 6 | 1 | Candidate for the next route-only authorization package |
| Split adapter constructors | 8 | 8 | 0 | Requires interface / test-double design before source edits |
| Legacy adapter compatibility | 5 | 5 | 0 | Requires separate compatibility ownership decision |
| Service wrapper / export | 2 | 2 | 1 | Retain until consumers are migrated and current HEAD proves no runtime consumers remain |

## Route Surface

`web/backend/app/api/data_quality.py` has 9 routes. Seven route handlers touch
the monitor surface directly or through `monitor_data_quality()`.

| Method | Path | Function | Getter calls | Monitor calls |
|---|---|---|---:|---:|
| `GET` | `/health` | `get_sources_health` | 0 | 0 |
| `GET` | `/metrics` | `get_data_quality_metrics` | 1 | 0 |
| `GET` | `/alerts` | `get_active_alerts` | 1 | 0 |
| `POST` | `/alerts/{alert_id}/acknowledge` | `acknowledge_alert` | 1 | 0 |
| `POST` | `/alerts/{alert_id}/resolve` | `resolve_alert` | 1 | 0 |
| `GET` | `/config/mode` | `get_data_source_mode` | 0 | 0 |
| `GET` | `/status/overview` | `get_system_status_overview` | 1 | 0 |
| `POST` | `/test/quality` | `test_data_quality` | 0 | 1 |
| `GET` | `/metrics/trends` | `get_quality_trends` | 1 | 0 |

## Decision

G2.190 classifies the data-quality monitor surface as a critical cross-cutting
surface and rejects a single-batch implementation.

The next gate should be:

`G2.191 data-quality route provider authorization package`

G2.191 should remain authorization-only. It should define the exact future
source/test surface for a route-only provider migration before any backend source
changes happen.

## Track Split

| Track | Surface | Sequence | Next gate |
|---|---|---:|---|
| Route provider | `web/backend/app/api/data_quality.py` | 1 | Prepare G2.191 route-only authorization package |
| Split adapter constructor | `web/backend/app/services/adapters_split/*.py` | 2 | Interface / test-double design before adapter constructor source edits |
| Legacy adapter compatibility | `web/backend/app/services/adapters/*.py`, `web/backend/app/services/data_adapters/*.py`, `web/backend/app/services/market_data_adapter.py` | 3 | Compatibility ownership decision before source edits |
| Singleton wrapper retention | `web/backend/app/services/_data_quality_monitor_singleton.py` | 4 | Retain until route and adapter consumers are migrated and verified |

## G2.191 Suggested Authorization Shape

G2.191 may authorize a future source lane only after review. The suggested future
implementation surface should be limited to:

- `web/backend/app/api/data_quality.py`
- focused data-quality route/provider regression tests
- OpenAPI dependency leak smoke
- `app.main` import / data-quality route registration smoke

G2.191 must preserve:

- route paths
- HTTP methods
- response models
- OpenAPI examples
- error response contract
- data-source factory behavior
- `DataQualityMonitor` backing singleton behavior

G2.191 must not include:

- adapter constructor migration
- legacy adapter compatibility cleanup
- `DataQualityMonitor` implementation rewrite
- singleton wrapper deletion

## Explicit Non-Goals

- Do not edit backend source from G2.190.
- Do not edit frontend source from G2.190.
- Do not edit tests from G2.190.
- Do not create or change OpenSpec proposals from G2.190.
- Do not change GitHub issue or PR labels from G2.190.
- Do not migrate adapter constructors from G2.190.
- Do not delete `_data_quality_monitor_singleton.py`.
- Do not start data-quality source implementation before a separate accepted
  authorization package exists.

## Evidence Artifacts

| Artifact | Role |
|---|---|
| `.planning/codebase/generated/data-quality-adapter-cross-cutting-decision-2026-05-28.json` | G2.190 machine-readable decision evidence |
| `docs/reports/quality/backend-data-quality-adapter-cross-cutting-decision-2026-05-28.md` | G2.190 human-readable decision package |
| `governance/mainline/task-cards/pr-343.yaml` | G2.190 governance-only PR scope card |
