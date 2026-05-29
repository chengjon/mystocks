# Backend Unified Data Service Ownership Decision - 2026-05-29

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2: `G2.223`
- Status: ownership decision package for review
- Prepared at: `2026-05-29T08:19:43+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `e7402fffe29bee5f7f2a4ada5a60a4bf26876969`
- Parent: G2.222 / PR `#375`, merged at `e7402fffe29bee5f7f2a4ada5a60a4bf26876969`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source edit authority: no

Boundary note: this package is a no-source ownership decision. It does not
authorize backend source edits, tests, route/OpenAPI changes, frontend work,
issue label changes, OpenSpec proposal creation, PM2 commands, or PR merges.

## Target

| Item | Value |
|---|---|
| Symbol | `get_unified_data_service` |
| File | `web/backend/app/services/unified_data_service.py` |
| Definition line | `576` |
| Current shape | lazy module singleton provider plus same-file facade helpers |
| Classification | root facade / compatibility service surface |

G2.222 selected this candidate after closing the execution tracking provider
seam. This package decides ownership only; it intentionally stops before source
authorization.

## Current-HEAD Evidence

GitNexus impact:

| Metric | Value |
|---|---:|
| Risk | MEDIUM |
| Impacted symbols | 5 |
| Direct callers | 5 |
| Processes affected | 0 |
| Modules affected | 1 (`Services`) |

Direct graph callers:

| Caller | File | Interpretation |
|---|---|---|
| `get_stocks_basic` | `web/backend/app/services/unified_data_service.py` | same-file facade wrapper |
| `get_stocks_industries` | `web/backend/app/services/unified_data_service.py` | same-file facade wrapper |
| `get_stocks_concepts` | `web/backend/app/services/unified_data_service.py` | same-file facade wrapper |
| `get_market_overview` | `web/backend/app/services/unified_data_service.py` | same-file facade wrapper |
| `search_stocks` | `web/backend/app/services/unified_data_service.py` | same-file facade wrapper |

Static source scan:

| Scan item | Value |
|---|---:|
| `get_unified_data_service` / `UnifiedDataService` text hits in `web/backend/app` | 12 |
| Files with hits | 2 |
| Route-body direct `get_unified_data_service()` calls | 0 |
| Direct imports of `UnifiedDataService` from the route layer | 1 |
| Direct `UnifiedDataService()` instantiations in route code | 2 |

Route-layer direct instantiations:

| File | Line | Shape |
|---|---:|---|
| `web/backend/app/api/industry_concept_analysis.py` | 224 | `UnifiedDataService()` result is not assigned |
| `web/backend/app/api/industry_concept_analysis.py` | 277 | `UnifiedDataService()` result is not assigned |

These route-layer instantiations are not the same seam as the same-file
`get_unified_data_service` facade. They should not be fixed inside this
ownership decision package.

## Ownership Classification

`web/backend/app/services/unified_data_service.py` owns the lazy singleton
provider and five same-file facade wrappers. Current graph evidence does not
show route bodies calling `get_unified_data_service()` directly.

`web/backend/app/api/industry_concept_analysis.py` owns a separate route cleanup
candidate: two unassigned `UnifiedDataService()` calls inside industry/concept
list endpoints. That candidate touches route behavior and therefore needs its
own authorization package before any source edit.

This package does not authorize:

- deleting or renaming `get_unified_data_service`
- changing `UnifiedDataService` constructor behavior
- changing industry/concept route response contracts
- changing route/OpenAPI exposure
- batching cache prewarming provider work
- frontend or data-source behavior changes

## Decision

G2.223 does not select a direct implementation lane for
`get_unified_data_service`.

Reason: the GitNexus impact is MEDIUM, but all direct graph callers are
same-file facade helpers. The only route-level evidence is direct class
instantiation in `industry_concept_analysis.py`, and that is a route
ownership/cleanup concern, not a same-file facade edit.

The selected follow-up is G2.224: a no-source authorization package for the
`industry_concept_analysis.py` direct `UnifiedDataService()` instantiation
cleanup candidate.

## G2.224 Candidate Boundary

G2.224 may decide whether a future path-limited source lane can remove or
replace the two unassigned `UnifiedDataService()` instantiations while
preserving route contracts.

Candidate source paths if a later package authorizes implementation:

- `web/backend/app/api/industry_concept_analysis.py`
- a focused existing or new route test for the industry/concept list endpoints

G2.224 must not batch:

- `get_unified_data_service` deletion
- `UnifiedDataService` constructor refactor
- cache prewarming provider work
- route/OpenAPI contract changes
- frontend changes
- data source behavior changes

`get_prewarming_strategy` remains deferred behind the G2.224 route cleanup
authorization decision.

## Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/unified-data-service-ownership-decision-2026-05-29.json` | Machine-readable G2.223 ownership decision evidence |
| `docs/reports/quality/backend-unified-data-service-ownership-decision-2026-05-29.md` | Human-readable G2.223 decision package |
| `governance/mainline/task-cards/pr-376.yaml` | Mainline governance task card |

## Verification Plan

This no-source package should be verified with:

- JSON parse for the generated evidence and steward index
- Markdown governance gate for changed markdown files
- mainline scope gate for the PR task card
- `git diff --check`
- OpenSpec strict validate for `migrate-backend-singletons-to-lifecycle-di`
- GitNexus staged/compare change detection to confirm no code symbols or
  execution flows changed
