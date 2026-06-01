# Backend Governance Dashboard Postgres Provider Closeout / Residual Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: G2.288
- Status: for review in future PR `#441`
- Prepared at: `2026-06-01T08:49:27+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `67ef9b9d8f9dd420de80995f624fa54e41493415`
- Parent gate: G2.287 provider implementation, PR `#440`, merged at `67ef9b9d8f9dd420de80995f624fa54e41493415`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`

Boundary note: G2.288 is a no-source closeout / residual refresh package. It
does not authorize backend source edits, route/OpenAPI contract changes,
frontend/config/script changes, OpenSpec proposal edits, PM2 commands, runtime
state changes, source retirement, or automatic merge of the next MEDIUM-risk
target.

## Closeout Result

G2.287 is accepted/merged and the governance dashboard provider lane is closed.

Current scan of `web/backend/app/api/governance_dashboard.py` records:

- `get_governance_dashboard_postgres_connection` exists
- provider backing `await get_postgres_connection()` calls: `1`
- direct route-body `await get_postgres_connection()` calls: `0`
- route-body manual `conn.close()` calls: `0`
- `Depends(get_governance_dashboard_postgres_connection)` bindings: `5`

Closed target handlers:

| Handler | Direct route-body calls | Manual `conn.close()` calls | Provider binding |
|---|---:|---:|---:|
| `get_quality_overview` | 0 | 0 | 1 |
| `get_lineage_stats` | 0 | 0 | 1 |
| `get_assets_catalog` | 0 | 0 | 1 |
| `get_compliance_metrics` | 0 | 0 | 1 |
| `get_dashboard_summary` | 0 | 0 | 1 |

## Route / OpenAPI Smoke

Import-time route/OpenAPI smoke with placeholder environment values records:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- duplicate operation IDs: `0`
- governance dashboard provider parameter leaks: `0`

Governance dashboard paths remain present:

- `/api/v1/governance/assets/catalog`
- `/api/v1/governance/compliance/metrics`
- `/api/v1/governance/dashboard/summary`
- `/api/v1/governance/lineage/stats`
- `/api/v1/governance/quality/overview`

The smoke produced expected import-time service logs and historical deprecation
warnings; these did not affect route/OpenAPI counts.

## Residual Refresh

Active FastAPI route-handler getter scan found `47` remaining direct getter-like
calls after excluding the just-closed governance dashboard and data lineage
provider lanes.

The next selected target is:

- gate: G2.289
- file: `web/backend/app/api/data_source_registry.py`
- symbol: `get_manager`
- UID: `Function:web/backend/app/api/data_source_registry.py:get_manager`
- active route-body callers: `7`
- classification: active data-source registry route helper requiring no-source
  ownership / route-provider decision first

Target route handlers:

- `search_data_sources`
- `get_category_stats`
- `get_data_source`
- `update_data_source`
- `test_data_source`
- `health_check_data_source`
- `health_check_all_data_sources`

GitNexus evidence for the selected next target:

- MCP impact: `Transport closed`
- CLI context: found the target symbol and seven incoming calls
- CLI impact by UID:
  - risk: `MEDIUM`
  - impacted symbols: `7`
  - direct callers: `7`
  - affected processes: `1`
  - affected modules: `1`
  - index status: stale warning

Staged verification for this no-source closeout package:

- MCP `detect_changes`: `Transport closed`
- CLI `verify-staged`: low risk
- changed files: `9`
- changed symbols: `0`
- affected processes: `0`
- index status: stale warning

Because the selected next target has MEDIUM impact and one affected process,
G2.288 must stop for human review and must not auto-merge under the limited
autopilot rule.

## Deferred / Excluded Residuals

`web/backend/app/api/data_source_config.old.py:get_config_manager` appears in
raw text scans but is not selected from the active FastAPI route-handler scan.
It requires separate historical / compatibility classification before any
source lane.

`web/backend/app/services/__init__.py:get_integrated_services` remains a root
facade compatibility / service seam concern, not a route-body provider
candidate.

`web/backend/app/api/_cache_basic_routes.py:get_cache_manager` remains in the
residual pool, but it ranks after `data_source_registry.get_manager` because
the current active route-body count is lower.

## Decision

G2.288 closes the governance dashboard provider lane and selects only the next
no-source decision target:

G2.289 no-source `data_source_registry.get_manager` ownership / route-provider
decision.

G2.288 does not authorize G2.289 implementation. G2.289 must classify
ownership, route/OpenAPI exposure, consumer-contract boundaries, lifecycle
shape, and GitNexus blast radius before any future authorization package.

## Evidence

- `.planning/codebase/generated/governance-dashboard-postgres-provider-closeout-refresh-2026-06-01.json`
- `docs/reports/quality/backend-governance-dashboard-postgres-provider-closeout-refresh-2026-06-01.md`
- `governance/mainline/task-cards/pr-441.yaml`
