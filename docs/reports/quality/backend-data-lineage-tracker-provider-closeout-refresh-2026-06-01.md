# Backend Data Lineage Tracker Provider Closeout / Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: G2.284
- Status: no-source closeout / residual refresh
- Prepared at: `2026-06-01T03:11:52+08:00`
- Base HEAD checked: `511e9d091bc2b29777c522c595a9f1454f50b973`
- Parent: G2.283 accepted/merged by PR `#436`
- Parent merge commit: `511e9d091bc2b29777c522c595a9f1454f50b973`
- Source edit authority: no

G2.284 records that the accepted G2.283 source lane is closed. It does not
authorize backend source edits, tests, route/OpenAPI contract changes, docs/api
artifact edits, frontend/config/script changes, OpenSpec changes, PM2 commands,
or runtime state changes.

## Closeout Evidence

The G2.283 implementation is now accepted/merged:

- PR: `#436`
- Merge commit: `511e9d091bc2b29777c522c595a9f1454f50b973`
- Merged at: `2026-05-31T19:05:43Z`

Current static closeout check for `web/backend/app/api/data_lineage.py`:

- Direct route-body `get_lineage_tracker()` calls: `0`
- Provider backing `get_lineage_tracker()` call: `1`
- Manual route-body `await conn.close()` calls: `0`
- `Depends(get_lineage_tracker_dependency)` bindings: `5`
- `get_lineage_tracker_dependency()` definitions: `1`

The remaining backing call is intentional: the route-local async generator
provider owns creation and cleanup of the tracker / connection adapter pair.

## Route / OpenAPI Smoke

Current app import and schema smoke with placeholder import-time environment
values completed successfully:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- Duplicate operation IDs: `0`
- Lineage paths present:
  - `/api/v1/governance/lineage/stats`
  - `/api/v1/lineage/graph`
  - `/api/v1/lineage/impact`
  - `/api/v1/lineage/record`
  - `/api/v1/lineage/{node_id}/downstream`
  - `/api/v1/lineage/{node_id}/upstream`

Known import-time warning noise remains limited to existing Pydantic/FastAPI
deprecation warnings and service initialization logs.

## Residual Refresh

Current refresh scanned `371` Python files under:

- `web/backend/app/api`
- `web/backend/app/services`

The scan keeps previously accepted closed surfaces out of the implementation
candidate queue, including `get_config_manager`, `get_monitoring_db`,
`get_postgres_async`, `get_data_quality_monitor`, `get_lineage_tracker`, and the
provider wrappers created by prior G2 nodes.

Deferred surfaces remain:

| Surface | Classification | Disposition |
|---|---|---|
| `get_integrated_services` | root facade compatibility surface | separate root facade compatibility decision |
| `get_indicator_registry` | ambiguous registry surface | disambiguate registry ownership first |
| `get_cache_manager` | ambiguous dashboard/cache helper | disambiguate dashboard/core cache ownership first |
| `get_redis_client` | infrastructure cache/client helper | infrastructure/cache ownership lane |
| `get_cache_integration` | cache integration infrastructure surface | infrastructure/cache ownership lane |

## Next Gate

Selected next gate after G2.284 acceptance:

- G2.285 no-source `governance_dashboard.get_postgres_connection` ownership /
  control-plane route-provider decision

Reason:

- `get_postgres_connection` has `5` active route-body calls in one route module:
  `web/backend/app/api/governance_dashboard.py`
- The helper is a control-plane DB connection helper, so it must be routed
  through route/OpenAPI/control-plane ownership before any source authorization.
- G2.285 must remain no-source. It should classify ownership, consumer/route
  exposure, and future authorization boundaries only.

## GitNexus Evidence

GitNexus CLI fallback for the selected next target found:

- Target: `Function:web/backend/app/api/governance_dashboard.py:get_postgres_connection`
- Direct callers: `5`
- Impacted count: `6`
- Risk: `MEDIUM`
- Affected processes: `0`
- Index status: stale warning

The MEDIUM risk is recorded as a future-decision constraint. It does not block
G2.284 because this package is no-source and does not authorize implementation.

## Evidence Artifacts

- `.planning/codebase/generated/data-lineage-tracker-provider-closeout-refresh-2026-06-01.json`
- `docs/reports/quality/backend-data-lineage-tracker-provider-closeout-refresh-2026-06-01.md`
- `governance/mainline/task-cards/pr-437.yaml`
