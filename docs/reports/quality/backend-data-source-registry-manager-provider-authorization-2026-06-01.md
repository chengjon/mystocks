# Backend Data Source Registry Manager Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: G2.290
- Status: for review in future PR `#443`
- Prepared at: `2026-06-01T10:36:04+08:00`
- Base HEAD checked: `1f0a909355f5db9002cfc2d0fcbba21e366dc0bf`
- Parent gate: G2.289, PR `#442`, merged at `1f0a909355f5db9002cfc2d0fcbba21e366dc0bf`

Boundary note: G2.290 is a no-source authorization package. It does not modify
backend source, tests, route contracts, generated OpenAPI artifacts, docs/api
artifacts, frontend, config, scripts, OpenSpec files, PM2 state, or runtime
state. It defines the envelope for a later source PR only after human acceptance.

## Authorization Decision

If PR `#443` is accepted, it authorizes only:

- future gate: G2.291
- future source path: `web/backend/app/api/data_source_registry.py`
- future target: `data_source_registry.get_manager`
- future pattern: route-local FastAPI dependency provider

Future G2.291 may add a route-local provider named
`get_data_source_registry_manager` that delegates to the existing `get_manager()`
helper. The existing `get_manager()` helper must remain as the backing
compatibility and monkeypatch seam.

Future G2.291 may move only these seven active route handlers from route-body
`manager = get_manager()` calls to dependency parameters:

| Handler | Method / path |
|---|---|
| `search_data_sources` | `GET /api/v1/data-sources/` |
| `get_category_stats` | `GET /api/v1/data-sources/categories` |
| `get_data_source` | `GET /api/v1/data-sources/{endpoint_name}` |
| `update_data_source` | `PUT /api/v1/data-sources/{endpoint_name}` |
| `test_data_source` | `POST /api/v1/data-sources/{endpoint_name}/test` |
| `health_check_data_source` | `POST /api/v1/data-sources/{endpoint_name}/health-check` |
| `health_check_all_data_sources` | `POST /api/v1/data-sources/health-check/all` |

The implementation may add `Depends` to the existing FastAPI import if needed.

## Explicit Non-Authorization

G2.290 does not authorize:

- editing `DataSourceManagerV2` internals
- introducing a process-level data-source registry singleton
- changing data-source config routes
- changing route paths, methods, response models, response metadata, operation IDs, OpenAPI exposure, auth behavior, `UnifiedResponse` behavior, or error-contract shape
- editing generated OpenAPI artifacts or docs/api artifacts
- changing frontend, config, scripts, OpenSpec, PM2, runtime state, or source retirement

The first source lane must preserve fresh `DataSourceManagerV2()` construction
through the existing `get_manager()` helper.

## Current Evidence

Current code shape at HEAD `1f0a909355f5db9002cfc2d0fcbba21e366dc0bf`:

- `get_manager` is defined in `web/backend/app/api/data_source_registry.py`
- current shape: returns a fresh `DataSourceManagerV2()` instance
- active route-body direct calls: `7`
- current FastAPI dependency bindings: `0`

Route/OpenAPI smoke with repo `.env` loaded into the subprocess recorded:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- duplicate operation IDs: `0`
- data-source registry runtime routes: `7`

GitNexus evidence:

- MCP context / impact: `Transport closed`
- CLI fallback context: found `Function:web/backend/app/api/data_source_registry.py:get_manager`
- CLI fallback impact: MEDIUM risk, `7` impacted symbols, `7` direct callers, `1` affected process, `1` affected module
- affected process: `test_data_source`
- index status: stale warning

## Future G2.291 Verification Requirements

Before editing source in G2.291:

- read `architecture/STANDARDS.md`
- read `openspec/AGENTS.md`
- run GitNexus context / impact for `data_source_registry.get_manager`
- stop if impact becomes HIGH or CRITICAL
- confirm route/OpenAPI baseline remains `548/500/0`

TDD red requirement:

- add a focused provider regression first
- the new test must fail before implementation for the expected missing provider or direct-call reason
- the test should prove the provider name, seven target handlers, no route-body direct `get_manager()` calls, and preserved `get_manager()` backing seam

TDD green and closeout requirements:

- focused provider regression passes
- focused data-source registry API / error contract / auth / metrics tests pass
- touched backend files pass `ruff check`
- route/OpenAPI smoke remains `548/500/0`
- no provider dependency parameters leak into OpenAPI
- GitNexus staged verification records expected scope

## Stop Rule

PR `#443` must stop for human review and must not auto-merge under limited
autopilot because it authorizes a future backend source implementation lane and
the target has GitNexus MEDIUM impact with one affected process.

## Artifacts

- `.planning/codebase/generated/data-source-registry-manager-provider-authorization-2026-06-01.json`
- `docs/reports/quality/backend-data-source-registry-manager-provider-authorization-2026-06-01.md`
- `governance/mainline/task-cards/pr-443.yaml`
