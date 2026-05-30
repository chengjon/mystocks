# G2.250 Postgres Async Monitoring Portfolio Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation evidence for review
- Prepared at: `2026-05-30T18:13:12+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `db1a0653737c8239a937a97a5fd32730e2c25bc3`
- Worktree branch: `g2-250-postgres-async-monitoring-portfolio-provider`
- Parent gate: G2.249 / PR `#402`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`

## Authorization Boundary

G2.249 authorized one path-limited route consumer provider pilot. G2.250 used
that authority only for:

- `web/backend/app/api/_monitoring_portfolio_router.py`
- `tests/api/file_tests/test_monitoring_analysis_api.py`
- this evidence package and steward-tree metadata

This lane did not modify `src/monitoring/infrastructure/**`, broader API route
consumers, OpenAPI specs, frontend code, configuration, scripts, or OpenSpec
change/spec files.

## Implementation Summary

The monitoring portfolio router now exposes a route-local dependency provider:

- `get_monitoring_postgres_async()`

The provider delegates to the canonical infrastructure facade:

- `src.monitoring.infrastructure.postgresql_async_v3.get_postgres_async()`

The three authorized portfolio handlers now receive the dependency through
FastAPI `Depends(get_monitoring_postgres_async)`:

- `get_portfolio_summary`
- `get_portfolio_alerts`
- `get_rebalance_suggestions`

Direct route-body calls to `get_postgres_async()` inside these handlers were
removed. Route decorators, paths, HTTP methods, response models, summaries, and
OpenAPI exposure were intentionally left unchanged.

## Structural Evidence

| Check | Before | After |
|---|---:|---:|
| Authorized route-body `get_postgres_async()` calls | 3 | 0 |
| Authorized handler dependency parameters using `get_monitoring_postgres_async` | 0 | 3 |
| Target router path count in app route table | 3 | 3 |
| OpenAPI exposure for target routes | included | included |

## TDD Evidence

Red test:

```bash
env PYTHONPATH=. pytest -q tests/api/file_tests/test_monitoring_analysis_api.py::TestMonitoringAnalysisAPIFile::test_monitoring_portfolio_postgres_async_uses_route_dependency_provider -n 0 --tb=short --no-cov
```

Observed failure before implementation:

```text
AssertionError: get_monitoring_postgres_async not found in module
```

Green test:

```bash
env PYTHONPATH=. pytest -q tests/api/file_tests/test_monitoring_analysis_api.py::TestMonitoringAnalysisAPIFile::test_monitoring_portfolio_postgres_async_uses_route_dependency_provider -n 0 --tb=short --no-cov
```

Result:

```text
1 passed
```

Focused file regression:

```bash
env PYTHONPATH=. pytest -q tests/api/file_tests/test_monitoring_analysis_api.py -n 0 --tb=short --no-cov
```

Result:

```text
18 passed
```

## Route / OpenAPI Smoke

Smoke command imported `app.main`, generated `app.openapi()`, and listed routes
owned by `app.api._monitoring_portfolio_router` with transient test environment
values.

Result:

```text
routes=548 paths=500
GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}/summary include_in_schema=True
GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}/alerts include_in_schema=True
GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}/rebalance include_in_schema=True
```

## Lint / OpenSpec

Ruff:

```bash
ruff check web/backend/app/api/_monitoring_portfolio_router.py tests/api/file_tests/test_monitoring_analysis_api.py
```

Result:

```text
All checks passed!
```

OpenSpec:

```bash
openspec validate migrate-backend-singletons-to-lifecycle-di --strict
```

Result:

```text
Change 'migrate-backend-singletons-to-lifecycle-di' is valid
```

PostHog `ECONNREFUSED` output, if present, is telemetry noise and not an
OpenSpec validation failure.

## GitNexus Gate

GitNexus impact analysis was attempted before implementation for the affected
route handler symbols:

- `get_portfolio_summary`
- `get_portfolio_alerts`
- `get_rebalance_suggestions`

Observed degradation:

- MCP impact calls failed with transport closure.
- CLI impact fallback hung / timed out before returning a usable report.

This is recorded as a degraded gate, not as a successful LOW-risk report.
Scope is instead constrained by the G2.249 authorization, path-limited task
card, focused TDD structural test, OpenAPI smoke, and mainline scope gate.

Staged `detect_changes` was attempted before commit:

- MCP `detect_changes(scope=staged)` failed with transport closure.
- CLI `gitnexus verify-staged -r mystocks --cwd <worktree> --json` returned
  `status=stale`, `risk_level=high`, `changed_files=11`,
  `changed_count=19`, and `affected_count=9`.
- The reported stale reason was
  `current_commit_differs_from_indexed_commit`, with indexed commit
  `fdb91e614c28ee74db77c0fc13e74aff2bfd18bf` and current commit
  `db1a0653737c8239a937a97a5fd32730e2c25bc3`.

Treat the CLI result as a stale-index warning, not as current graph approval.
Review should keep using the path-limited task card, focused tests, OpenAPI
smoke, and mainline scope gate as blocking evidence until the GitNexus index is
refreshed.

## Residual Policy

G2.250 does not authorize broader `get_postgres_async()` consumer migration.
If this implementation is accepted, the next lane should be:

- G2.251 no-source monitoring portfolio provider closeout / residual refresh

That lane should confirm the three authorized route-body calls remain removed,
refresh residual route consumer counts, and decide the next governance gate
without editing source code.
