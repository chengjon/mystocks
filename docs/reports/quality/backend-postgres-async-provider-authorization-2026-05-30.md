# Backend Postgres Async Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: For review  
Date: 2026-05-30  
G2 node: G2.246  
Parent: G2.245 accepted by PR #398, merged at `6bb9104295c31eac0e5b99dcaa65264c79fda085`  
Branch: `g2-246-postgres-async-provider-authorization`  
Base: `wip/root-dirty-20260403` at `6bb9104295c31eac0e5b99dcaa65264c79fda085`

## Scope

This is a no-source provider authorization packet for `get_postgres_async`.

It authorizes only a future G2.247 source lane. It does not implement that lane.

Allowed work in this packet:

- confirm G2.245 ownership evidence
- choose the future provider-seam implementation shape
- define exact future source/test paths
- update steward-tree state

Not authorized in this packet:

- source implementation
- test implementation
- API route edits
- OpenAPI changes
- PM2 commands
- OpenSpec proposal or spec creation
- `get_monitoring_db` work

## Evidence Snapshot

| Evidence | Value |
|---|---:|
| Files scanned | 2318 |
| Definitions | 1 |
| Import lines | 28 |
| Public re-export imports | 27 |
| Direct singleton-module imports | 1 |
| Invocation calls | 30 |
| Active API route-body calls | 21 |
| Historical `.old.py` API calls | 1 |
| `Depends(get_postgres_async)` calls | 0 |
| Files with hits | 14 |

GitNexus MCP impact failed with `Transport closed`; CLI fallback was used.

| GitNexus CLI field | Value |
|---|---:|
| Risk | LOW |
| Impacted count | 4 |
| Direct | 3 |
| Processes affected | 0 |
| Modules affected | 2 |

## Authorization Decision

Authorize G2.247 as a path-limited source implementation lane to add an
infrastructure-level provider/reset seam around `get_postgres_async`.

The future implementation may touch only:

- `src/monitoring/infrastructure/_postgresql_async_v3_singleton.py`
- `src/monitoring/infrastructure/postgresql_async_v3.py`
- `tests/unit/monitoring/test_postgres_async_provider.py`

The future implementation must:

- add an explicit provider hook for `get_postgres_async`
- add a reset hook that clears explicit provider state and restores default
  singleton behavior
- preserve lazy `MonitoringPostgreSQLAccess` creation when no provider is
  installed
- preserve `initialize_postgres_async` and `close_postgres_async` behavior
- preserve imports from `src.monitoring.infrastructure.postgresql_async_v3`
- add focused tests for provider override, reset, fallback, and public re-export
  behavior

The future implementation must not:

- migrate API route-body consumers
- edit API route files
- change route paths, response contracts, or OpenAPI schema
- change background monitoring task behavior
- change database connection semantics
- delete `get_postgres_async`
- remove the public re-export
- edit `get_monitoring_db` or unrelated singleton seams

## Rejected Options

| Option | Reason |
|---|---|
| Route-local provider wrappers first | 21 active route-body calls span multiple route files; starting there would widen the first source lane and skip background-task compatibility concerns |
| Bulk consumer migration | Would mix API routes, monitoring infrastructure, historical compatibility, and tests in one lane |
| Delete or rename `get_postgres_async` | The symbol remains a compatibility accessor with 28 import lines, mostly through the public re-export |

## Required G2.247 Gates

Before future source work starts, G2.247 must:

- read `architecture/STANDARDS.md`
- run GitNexus impact/context for `get_postgres_async` and the singleton module,
  using CLI fallback if MCP remains unavailable
- run TDD red first for the provider/reset API
- limit staged files to the authorized paths
- run focused pytest for the new provider test and any existing singleton/import
  smoke
- run ruff on touched source/test files
- run app/OpenAPI smoke and confirm route/path count does not change
- run mainline scope gate with the future task card

## Verification

- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict`
  passed; PostHog telemetry emitted network noise only.
- GitNexus MCP impact failed with `Transport closed`; CLI impact fallback was
  recorded.

## Review Questions

- Does G2.246 correctly authorize only the minimal infrastructure provider/reset
  seam?
- Are route consumer migrations excluded from G2.247?
- Are the future source/test paths narrow enough?
- Does the packet preserve the public import surface and singleton fallback?
