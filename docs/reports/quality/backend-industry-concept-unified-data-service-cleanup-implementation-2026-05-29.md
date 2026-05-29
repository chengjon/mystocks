# Backend Industry/Concept UnifiedDataService Cleanup Implementation - 2026-05-29

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2: `G2.225`
- Status: implementation for review
- Prepared at: `2026-05-29T09:38:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `36c38fbf233945b7e45ed67b50591665942d4b32`
- Parent: G2.224 / PR `#377`, merged at `36c38fbf233945b7e45ed67b50591665942d4b32`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source edit authority: yes, path-limited by G2.224

Boundary note: this implementation only removes two unassigned
`UnifiedDataService()` constructor calls and the now-unused import from
`web/backend/app/api/industry_concept_analysis.py`. It does not change route
paths, response models, OpenAPI exposure, SQL text, database access path,
`get_postgresql_engine`, error contracts, `UnifiedDataService`,
`get_unified_data_service`, cache prewarming, frontend behavior, runtime
configuration, or OpenSpec specs.

## Change Summary

| Area | Before | After |
|---|---:|---:|
| Direct `UnifiedDataService()` calls in `industry_concept_analysis.py` | 2 | 0 |
| `UnifiedDataService` import in `industry_concept_analysis.py` | present | removed |
| `get_unified_data_service` route-body calls | 0 | 0 |
| Target route paths changed | no | no |
| Target response models changed | no | no |
| SQL query text changed | no | no |
| `web/backend/app` text hits for `get_unified_data_service` / `UnifiedDataService` | 12 | 9 |

Target endpoints:

| Route | Handler | Response model | Preserved behavior |
|---|---|---|---|
| `GET /api/analysis/industry/list` | `get_industry_list` | `IndustryListResponse` | PostgreSQL query path through `get_postgresql_engine()` |
| `GET /api/analysis/concept/list` | `get_concept_list` | `ConceptListResponse` | PostgreSQL query path through `get_postgresql_engine()` |

## GitNexus Evidence

Exact GitNexus context for `web/backend/app/api/industry_concept_analysis.py`:

| Function | Start line before edit | Incoming graph callers | Outgoing calls | Processes |
|---|---:|---:|---|---:|
| `get_industry_list` | 215 | 0 | `get_postgresql_engine` | 0 |
| `get_concept_list` | 268 | 0 | `get_postgresql_engine` | 0 |

File-level GitNexus upstream impact for
`web/backend/app/api/industry_concept_analysis.py`:

| Risk | Direct callers | Processes affected | Modules affected |
|---|---:|---:|---:|
| LOW | 0 | 0 | 0 |

Exact incoming caller Cypher over the two route functions returned 2 target rows
and no caller values.

## TDD Evidence

Added focused regression test:

- `web/backend/tests/test_health_route_conflicts.py::test_industry_concept_list_endpoints_do_not_instantiate_unified_data_service_directly`

Red:

- Command: `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_industry_concept_list_endpoints_do_not_instantiate_unified_data_service_directly -q --no-cov --tb=short`
- Result: failed before source edit because `UnifiedDataService()` was present.

Green:

- Command: same as above
- Result: `1 passed`

## Verification

| Check | Result |
|---|---|
| Focused endpoint metadata + direct-constructor regression tests | `2 passed` |
| Ruff target check | `All checks passed` |
| app.main / OpenAPI smoke | `routes=548`, `paths=500`, industry and concept paths present |
| OpenSpec strict validate | `migrate-backend-singletons-to-lifecycle-di` valid; PostHog telemetry ECONNREFUSED noise only |

The app.main / OpenAPI smoke used transient non-secret placeholders for values
that are not required to validate import and schema generation. No environment
configuration or secret values were written to disk.

## Invariants

G2.225 preserved:

- `/api/analysis/industry/list`
- `/api/analysis/concept/list`
- `IndustryListResponse`
- `ConceptListResponse`
- OpenAPI exposure for both routes
- SQL query text
- `get_postgresql_engine()` access path
- `HTTPException(status_code=500, ...)` error behavior
- `UnifiedDataService` constructor implementation
- `get_unified_data_service` definition and facade helpers
- cache prewarming provider work

## Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/industry-concept-unified-data-service-cleanup-implementation-2026-05-29.json` | Machine-readable G2.225 implementation evidence |
| `docs/reports/quality/backend-industry-concept-unified-data-service-cleanup-implementation-2026-05-29.md` | Human-readable G2.225 implementation report |
| `governance/mainline/task-cards/pr-378.yaml` | Mainline governance task card |

## Next Gate

After review and merge, run G2.226 closeout / residual refresh before selecting
another unified-data or cache provider candidate. Do not use this PR to edit
`get_unified_data_service`, cache prewarming, route contracts, or frontend code.

## Rollback

Revert the PR. The route file returns to the prior no-op constructor calls and
the test file returns to metadata-only assertions.
