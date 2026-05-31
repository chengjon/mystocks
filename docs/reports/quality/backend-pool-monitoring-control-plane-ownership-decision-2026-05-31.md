# Backend Pool Monitoring Control-Plane Ownership Decision - 2026-05-31

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.271`
- Branch: `g2-271-pool-monitoring-control-plane-ownership`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `5b3ffd1f114b612810e96c463c651befeb005222`
- Source edit authority: none
- Parent PR: `#423`, merged at `5b3ffd1f114b612810e96c463c651befeb005222`

Boundary note: this report is an ownership and route-governance decision only.
It does not authorize backend source edits, route registration changes, provider
injection, source retirement, test edits, docs/api edits, frontend/config/script
edits, OpenSpec mutation, or PM2/stateful commands.

## Decision

`web/backend/app/api/v1/pool_monitoring.py` is an active control-plane route
contract, not a plain service lifecycle DI implementation candidate.

Selected next gate:

`G2.272 no-source service lifecycle residual candidate refresh after pool-monitoring deferral`

If pool monitoring changes are needed later, they must be routed through a
separate route/OpenAPI/control-plane authorization package before any source,
docs/api, or OpenAPI artifact edits.

## Route / OpenAPI Facts

Fresh route/OpenAPI smoke at HEAD `5b3ffd1f114b612810e96c463c651befeb005222`:

| Metric | Value |
|---|---:|
| FastAPI routes | 548 |
| OpenAPI paths | 500 |
| Duplicate operation IDs | 0 |
| Pool monitoring active routes | 4 |
| Pool monitoring OpenAPI paths | 4 |

| Method | Path | Endpoint | Operation ID |
|---|---|---|---|
| GET | `/api/pool-monitoring/postgresql/stats` | `get_postgresql_pool_stats` | `get_postgresql_pool_stats_api_pool_monitoring_postgresql_stats_get` |
| GET | `/api/pool-monitoring/tdengine/stats` | `get_tdengine_pool_stats` | `get_tdengine_pool_stats_api_pool_monitoring_tdengine_stats_get` |
| GET | `/api/pool-monitoring/health` | `connection_pools_health_check` | `connection_pools_health_check_api_pool_monitoring_health_get` |
| GET | `/api/pool-monitoring/alerts` | `check_connection_pool_alerts` | `check_connection_pool_alerts_api_pool_monitoring_alerts_get` |

All four routes are `include_in_schema=true` and carry the tags
`pool-monitoring` and `Connection Pool Monitoring`.

## Accessor Inventory

| Accessor / residual | Count | Decision |
|---|---:|---|
| `get_postgresql_engine()` | 1 | Infrastructure pool accessor used by active control-plane route; not a service DI candidate from G2.271 |
| `get_tdengine_manager()` | 1 | Infrastructure pool accessor used by active control-plane route; not a service DI candidate from G2.271 |
| `get_postgresql_pool_stats()` | 2 | Route-local stats function and endpoint share name; keep under route/OpenAPI/control-plane ownership |
| `get_tdengine_pool_stats()` | 2 | Route-local stats function and endpoint share name; keep under route/OpenAPI/control-plane ownership |

The module remains a control-plane monitoring surface because route semantics,
OpenAPI exposure, database pool ownership, and health/status interpretation are
coupled. It should not be batched with ordinary service getter provider
injection lanes.

## Consumer / Artifact Evidence

Existing contract/documentation artifacts reference this route family:

- `docs/api/openapi.json`
- `docs/api/openapi/market-data-api-full.json`
- `docs/api/API_ARCHITECTURE_DATA_2025-11-30.json`
- `docs/api/API_ARCHITECTURE_COMPREHENSIVE_SUMMARY_2025-11-30.md`

G2.271 intentionally does not edit those artifacts. If the pool monitoring
contract needs documentation or schema updates, create a future approved
route/OpenAPI/control-plane package.

## GitNexus Note

GitNexus MCP timed out after 120 seconds for:

- route map lookup for `/api/pool-monitoring`
- context lookup for `get_postgresql_pool_stats`
- context lookup for `get_tdengine_pool_stats`

G2.271 therefore uses AST/function inventory, FastAPI route table, OpenAPI
schema smoke, and static artifact references as no-source decision evidence.
Future source authorization must retry GitNexus or explicitly record a CLI
fallback before editing any symbol.

## Verification

- PR `#423`: `MERGED`, merge commit `5b3ffd1f114b612810e96c463c651befeb005222`.
- Runtime/OpenAPI smoke: `548` routes, `500` paths, duplicate operation IDs `0`.
- Pool monitoring route map: 4 active routes, 4 OpenAPI paths, all `include_in_schema=true`.
- Static inventory: residual accessors are infrastructure/control-plane pool accessors or route-local stats helpers.

## Rollback

Revert the future PR carrying this report and steward updates. No runtime code,
route registration, provider binding, test contract, docs/api artifact,
frontend state, database state, or OpenSpec state is changed by G2.271.
