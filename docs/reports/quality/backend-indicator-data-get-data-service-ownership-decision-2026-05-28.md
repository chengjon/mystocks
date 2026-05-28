# Backend Indicator/Data `get_data_service` Ownership Decision - 2026-05-28

> **历史文档说明**: 本文件是 G2.215 执行证据快照，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Branch: `g2-215-indicator-data-get-data-service-decision`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `a508fb263173b2014d307c4baec3b1eca0f42340`
- Prepared at: `2026-05-28T23:51:14+08:00`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source authority: none

This package is a no-source ownership decision. It does not authorize backend
source edits, tests, route/OpenAPI changes, frontend work, issue label changes,
or OpenSpec proposal creation.

## Inputs

G2.214 selected `get_data_service` for this decision because fresh current-HEAD
GitNexus evidence reported a `CRITICAL` impact, contradicting older LOW/retained
wording for Indicator/Data provider candidates.

Accepted parent state:

| Input | State |
|---|---|
| PR `#367` | Merged at `a508fb263173b2014d307c4baec3b1eca0f42340` |
| G2.214 report | `docs/reports/quality/backend-nonstrategy-provider-queue-refresh-2026-05-28.md` |
| G2.214 evidence | `.planning/codebase/generated/nonstrategy-provider-queue-refresh-2026-05-28.json` |

## Current-HEAD Evidence

GitNexus impact for `get_data_service`:

| Metric | Value |
|---|---:|
| Risk | `CRITICAL` |
| Direct callers | 3 |
| Impacted symbols | 5 |
| Affected processes | 7 |
| Affected modules | 2 |

Direct graph participants:

| Symbol | File | Classification |
|---|---|---|
| `calculate_indicators` | `web/backend/app/api/indicators/indicator_cache.py` | Indicator route handler using `DataService` dependency |
| `_calculate_single_indicator` | `web/backend/app/api/indicators/indicator_cache.py` | Indicator helper receiving injected `data_service` |
| `get_technical_indicators` | `web/backend/app/api/v1/strategy/indicators.py` | Strategy technical-indicator route handler using `DataService` dependency |

Static source scan:

| File | Line | Evidence |
|---|---:|---|
| `web/backend/app/services/data_service.py` | 466 | `get_data_service()` is the `DataService` singleton/backing API |
| `web/backend/app/api/indicators/indicator_cache.py` | 49 | `get_indicator_data_service()` returns `get_data_service()` |
| `web/backend/app/api/v1/strategy/indicators.py` | 30 | `get_strategy_indicator_data_service()` returns `get_data_service()` |

The important nuance: the current source has two provider-wrapper calls to
`get_data_service`. Route handlers consume `DataService` through FastAPI
`Depends(...)` provider parameters. This is still high-risk because the backing
service fans into route/process flows, but it is not a direct route-body
singleton-call cleanup.

## Ownership Classification

| Surface | Current state | Decision |
|---|---|---|
| `web/backend/app/services/data_service.py` singleton/backing API | Active global singleton fallback | Retain; source changes require a separate authorization package |
| `web/backend/app/api/indicators/indicator_cache.py` route dependency provider | `calculate_indicators` and batch calculation receive `DataService` from `Depends(get_indicator_data_service)` | Active route provider surface; do not treat as direct route-body singleton debt |
| `web/backend/app/api/v1/strategy/indicators.py` route dependency provider | `get_technical_indicators` receives `DataService` from `Depends(get_strategy_indicator_data_service)` | Route/provider surface only; do not reopen closed Strategy getter residual work |
| `_calculate_single_indicator` helper chain | Receives `data_service` as a parameter from the route path | Graph participant; not a separate direct `get_data_service` call site |

## Decision

G2.215 resolves the contradiction as follows:

- The older LOW/retained wording is superseded for `get_data_service`.
- The current graph impact is correctly high because active Indicator and
  Strategy technical-indicator routes depend on the shared `DataService` backing
  API.
- The current source shape is provider-wrapper based, so this should not be
  handled as a direct route-body singleton migration.
- No source lane is selected or authorized by this package.

## Next Gate

Start G2.216 only as an authorization package:

`G2.216 indicator/data DataService singleton provider authorization package`

G2.216 should decide whether a future source lane may add a `DataService`
provider/reset seam while preserving `get_data_service()` as the default
singleton fallback and keeping the route providers compatible.

G2.216 must not batch:

- Strategy getter residual reopen
- route/OpenAPI contract changes
- trade evidence provider work
- cache prewarming provider work
- data-quality monitor source reopen
- realtime streaming/socket work

## Evidence Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/indicator-data-get-data-service-ownership-decision-2026-05-28.json` | Machine-readable G2.215 ownership decision evidence |
| `docs/reports/quality/backend-indicator-data-get-data-service-ownership-decision-2026-05-28.md` | Human-readable G2.215 decision package |
| `governance/mainline/task-cards/pr-368.yaml` | Mainline governance task card |
