# Backend Industry/Concept UnifiedDataService Cleanup Authorization - 2026-05-29

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2: `G2.224`
- Status: no-source authorization package for review
- Prepared at: `2026-05-29T08:42:47+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `5eef37a097d55d209a69485bc29e89dd3aeb4076`
- Parent: G2.223 / PR `#376`, merged at `5eef37a097d55d209a69485bc29e89dd3aeb4076`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`
- Source edit authority in this PR: no

Boundary note: this package authorizes a future path-limited source lane if the
maintainer accepts it. It does not itself modify backend source, tests,
route/OpenAPI contracts, frontend code, OpenSpec specs, issue labels, PM2 state,
or runtime configuration.

## Candidate

| Item | Value |
|---|---|
| Candidate source file | `web/backend/app/api/industry_concept_analysis.py` |
| Import candidate | line `26`, `from app.services.unified_data_service import UnifiedDataService` |
| No-op constructor call | line `224`, inside `get_industry_list` |
| No-op constructor call | line `277`, inside `get_concept_list` |
| Route 1 | `GET /api/analysis/industry/list` |
| Route 2 | `GET /api/analysis/concept/list` |
| Response model 1 | `IndustryListResponse` |
| Response model 2 | `ConceptListResponse` |

The two `UnifiedDataService()` calls are not assigned and do not feed the SQL
query path. The endpoints currently query PostgreSQL through
`get_postgresql_engine()`.

## Current-HEAD Evidence

Exact GitNexus context for `web/backend/app/api/industry_concept_analysis.py`:

| Function | Start line | Incoming graph callers | Outgoing calls |
|---|---:|---:|---|
| `get_industry_list` | 215 | 0 | `get_postgresql_engine` |
| `get_concept_list` | 268 | 0 | `get_postgresql_engine` |

Route contract evidence:

| Evidence | Industry | Concept |
|---|---|---|
| Router prefix | `/api/analysis` | `/api/analysis` |
| Route path | `/industry/list` | `/concept/list` |
| Response model | `IndustryListResponse` | `ConceptListResponse` |
| Responses object | `INDUSTRY_LIST_RESPONSES` | `CONCEPT_LIST_RESPONSES` |
| Error contract | `HTTPException(status_code=500, ...)` | `HTTPException(status_code=500, ...)` |

Current focused verification:

| Check | Result |
|---|---|
| Endpoint metadata test | `web/backend/tests/test_health_route_conflicts.py::test_industry_concept_analysis_endpoints_have_examples_and_error_responses`: `1 passed` |
| Ruff target check | `ruff check web/backend/app/api/industry_concept_analysis.py web/backend/tests/test_health_route_conflicts.py`: passed |

## Authorization Decision

G2.224 selects G2.225 as a future path-limited source implementation lane.
G2.224 itself does not authorize code changes.

If G2.224 is accepted, G2.225 may only:

- remove the unassigned `UnifiedDataService()` call in `get_industry_list`
- remove the unassigned `UnifiedDataService()` call in `get_concept_list`
- remove the `UnifiedDataService` import if it becomes unused

Future source scope, if separately approved:

- `web/backend/app/api/industry_concept_analysis.py`

Optional future test scope, only if needed:

- `web/backend/tests/test_health_route_conflicts.py`

## Forbidden In G2.225

G2.225 must not change:

- route paths
- `response_model` values
- OpenAPI exposure
- SQL query text or database access path
- `get_postgresql_engine`
- `HTTPException` / error-contract behavior
- `UnifiedDataService` constructor behavior
- `get_unified_data_service` deletion or rename
- cache prewarming provider work
- frontend behavior

## Required Future Verification

Before a G2.225 source PR can be proposed, it must run:

- GitNexus context / impact for `get_industry_list` and `get_concept_list`
  using the exact `web/backend/app/api/industry_concept_analysis.py` symbols
- `ruff check web/backend/app/api/industry_concept_analysis.py web/backend/tests/test_health_route_conflicts.py`
- `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py::test_industry_concept_analysis_endpoints_have_examples_and_error_responses -q --no-cov --tb=short`
- app.main / OpenAPI smoke with transient runtime environment
- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict`
- mainline scope gate
- GitNexus staged `detect_changes`

## Artifacts

| Artifact | Purpose |
|---|---|
| `.planning/codebase/generated/industry-concept-unified-data-service-cleanup-authorization-2026-05-29.json` | Machine-readable G2.224 authorization evidence |
| `docs/reports/quality/backend-industry-concept-unified-data-service-cleanup-authorization-2026-05-29.md` | Human-readable G2.224 authorization package |
| `governance/mainline/task-cards/pr-377.yaml` | Mainline governance task card |
