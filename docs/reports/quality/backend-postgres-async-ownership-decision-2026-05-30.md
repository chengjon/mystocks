# Backend Postgres Async Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: For review  
Date: 2026-05-30  
G2 node: G2.245  
Parent: G2.244 accepted by PR #397, merged at `05844e89873ad4fc729dab87942ea80f81bde39a`  
Branch: `g2-245-postgres-async-ownership-decision`  
Base: `wip/root-dirty-20260403` at `05844e89873ad4fc729dab87942ea80f81bde39a`

## Scope

This is a no-source ownership and provider-seam decision packet for
`get_postgres_async`.

Allowed work:

- record current evidence for `get_postgres_async`
- classify ownership and consumer buckets
- update steward-tree state
- prepare the next gate

Not authorized:

- source implementation
- route migration
- test implementation
- runtime command execution
- OpenAPI or API contract changes
- OpenSpec proposal or spec creation
- deleting, renaming, or bypassing `get_postgres_async`

## Current Evidence

| Evidence | Value |
|---|---:|
| Files scanned | 2318 |
| Definitions | 1 |
| Import lines | 28 |
| Imports from public re-export `postgresql_async_v3.py` | 27 |
| Direct singleton-module imports | 1 |
| Invocation calls, excluding definition | 30 |
| Active API route-body calls | 21 |
| Historical `.old.py` API calls | 1 |
| `Depends(get_postgres_async)` calls | 0 |
| Files with hits | 14 |

The canonical definition remains:

- `src/monitoring/infrastructure/_postgresql_async_v3_singleton.py`

The public import surface remains:

- `src/monitoring/infrastructure/postgresql_async_v3.py`

## Consumer Buckets

| Bucket | Files | Calls | Decision |
|---|---:|---:|---|
| Monitoring infrastructure and background tasks | 4 | 4 | Preserve compatibility; future provider seam must not break non-API consumers |
| Singleton lifecycle helpers | 1 | 2 | `initialize_postgres_async` and `close_postgres_async` remain lifecycle helper consumers |
| Active API route-body consumers | 7 | 21 | Requires a follow-up provider authorization packet before source migration |
| Historical API file | 1 | 1 | Record as historical evidence only |
| Tests | 1 | 2 | Use as compatibility and future test-double evidence |

Active API route-body consumers:

- `web/backend/app/api/_data_source_config_responses.py`
- `web/backend/app/api/_monitoring_portfolio_router.py`
- `web/backend/app/api/monitoring_analysis.py`
- `web/backend/app/api/monitoring_watchlists.py`
- `web/backend/app/api/signal_monitoring/get_signal_statistics.py`
- `web/backend/app/api/signal_monitoring/signal_history_response.py`
- `web/backend/app/api/v1/system/settings.py`

Historical API consumer:

- `web/backend/app/api/data_source_config.old.py`

## GitNexus Evidence

GitNexus MCP impact failed with `Transport closed`; CLI fallback was used.

CLI impact result for `get_postgres_async` in repo `mystocks`:

| Field | Value |
|---|---:|
| Risk | LOW |
| Impacted count | 4 |
| Direct | 3 |
| Processes affected | 0 |
| Modules affected | 2 |

Affected modules:

- Infrastructure: 2 direct hits
- Api: 1 indirect hit

Graph context incoming calls:

- `initialize_postgres_async`
- `close_postgres_async`
- `PostgresSystemSettingsRepository.__init__`

Interpretation: the graph-level blast radius is low, but the static scan shows
21 active API route-body calls. Any future source lane must be authorized from
the static consumer matrix, not from graph risk alone.

## Decision

`get_postgres_async` is classified as an infrastructure-owned singleton
accessor and compatibility facade for `MonitoringPostgreSQLAccess`.

It is not:

- a route-owned helper
- a deletion candidate
- a direct low-risk source pilot
- a candidate for broad consumer migration from this packet

G2.245 therefore does not authorize code changes. It selects a follow-up
G2.246 no-source provider authorization packet.

G2.246 should decide whether a future implementation lane should use:

- an infrastructure-level provider/reset seam
- route-local provider wrappers for API route-body consumers
- a hybrid path preserving background task compatibility

`get_monitoring_db` remains deferred because it is a multi-definition
monitoring/risk/strategy seam and needs separate disambiguation.

## Verification

- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict`
  passed; PostHog telemetry emitted network noise only.
- GitNexus MCP impact failed with `Transport closed`; CLI impact/context
  fallback was recorded.

## Review Questions

- Does the report correctly classify `get_postgres_async` as infrastructure
  owned rather than route owned?
- Does the consumer matrix justify a no-source G2.246 authorization packet
  before any implementation?
- Does the packet avoid deleting, renaming, or bypassing the compatibility
  import surface?
- Does the packet keep `get_monitoring_db` deferred until disambiguation?
