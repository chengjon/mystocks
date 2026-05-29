# Backend Postgres Async Provider Reset Seam

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: For review  
Date: 2026-05-30  
G2 node: G2.247  
Parent: G2.246 accepted by PR #399, merged at `efeaaebc031844e8393e8ca1bff723a5900f1a61`  
Branch: `g2-247-postgres-async-provider-reset-seam`  
Base: `wip/root-dirty-20260403` at `efeaaebc031844e8393e8ca1bff723a5900f1a61`

## Scope

G2.247 implements the path-limited provider/reset seam authorized by G2.246.

Modified runtime/test files:

- `src/monitoring/infrastructure/_postgresql_async_v3_singleton.py`
- `src/monitoring/infrastructure/postgresql_async_v3.py`
- `tests/unit/monitoring/test_postgres_async_provider.py`

Not changed:

- API route consumers
- route paths
- response contracts
- OpenAPI schema
- background monitoring task code
- database connection semantics
- `get_monitoring_db`
- OpenSpec files

## Implementation

Added to the singleton module:

- `PostgresAsyncProvider`
- `set_postgres_async_provider(provider)`
- `reset_postgres_async_provider()`
- explicit provider branch in `get_postgres_async()`

Updated the public re-export module:

- `set_postgres_async_provider`
- `reset_postgres_async_provider`

Preserved behavior:

- lazy `MonitoringPostgreSQLAccess` fallback when no provider is installed
- `initialize_postgres_async()`
- `close_postgres_async()`
- imports from `src.monitoring.infrastructure.postgresql_async_v3`

## TDD Evidence

Red:

- Command: `env PYTHONPATH=. pytest -q tests/unit/monitoring/test_postgres_async_provider.py -n 0 --tb=short --no-cov`
- Result: collection failed before implementation
- Failure: `ImportError: cannot import name 'reset_postgres_async_provider' from 'src.monitoring.infrastructure.postgresql_async_v3'`

Green:

- Command: `env PYTHONPATH=. pytest -q tests/unit/monitoring/test_postgres_async_provider.py -n 0 --tb=short --no-cov`
- Result: `3 passed`

Focused tests cover:

- explicit provider override
- reset restoring lazy singleton behavior
- lifecycle helpers using the explicit provider
- public re-export behavior

## Verification

| Check | Result |
|---|---|
| GitNexus MCP impact/context | failed with `Transport closed` |
| GitNexus CLI pre-edit impact | LOW, 4 impacted, 3 direct, 0 processes, 2 modules |
| Focused pytest | 3 passed |
| Ruff on touched files | All checks passed |
| app/OpenAPI smoke | `routes=548`, `paths=500` |

The first OpenAPI smoke attempt lacked `BACKEND_PORT` and `BACKEND_BACKUP_PORT`.
It was rerun with a complete transient test environment and passed.

## Next Gate

If accepted, start G2.248 as a no-source closeout and residual refresh.

G2.248 should confirm:

- provider/reset seam is closed
- route consumer migration remains unstarted
- public import surface is preserved
- next residual candidate or route-consumer authorization needs a separate
  decision packet
