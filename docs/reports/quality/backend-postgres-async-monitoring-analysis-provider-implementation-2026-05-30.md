# G2.253 Postgres Async Monitoring Analysis Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation evidence for review
- Prepared at: `2026-05-30T19:38:06+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `c3e3452440455c8a7955b0779433219abee48c86`
- Worktree branch: `g2-253-monitoring-analysis-postgres-provider`
- Parent gate: G2.252 / PR `#405`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`

## Authorization Boundary

G2.252 authorized one path-limited `monitoring_analysis.py` route consumer
provider pilot after PR `#405` merged at
`c3e3452440455c8a7955b0779433219abee48c86`. G2.253 used that authority only
for:

- `web/backend/app/api/monitoring_analysis.py`
- `tests/api/file_tests/test_monitoring_analysis_api.py`
- this evidence package and steward-tree metadata

This lane did not modify `src/monitoring/infrastructure/**`, broader API route
consumers, route paths, response models, OpenAPI exposure, frontend code,
configuration, scripts, or OpenSpec change/spec files.

## Implementation Summary

`monitoring_analysis.py` now exposes a route-local dependency provider:

- `get_monitoring_analysis_postgres_async()`

The provider delegates to the canonical infrastructure facade:

- `src.monitoring.infrastructure.postgresql_async_v3.get_postgres_async()`

The two authorized monitoring analysis handlers now receive the dependency
through FastAPI `Depends(get_monitoring_analysis_postgres_async)`:

- `get_health_score_history`
- `analyze_portfolio`

Direct route-body calls to `get_postgres_async()` inside these handlers were
removed. `analyze_portfolio` continues to receive
`calculator_factory=Depends(get_monitoring_calculator_factory)`. Route
decorators, paths, HTTP methods, response models, summaries, and OpenAPI
exposure were intentionally left unchanged.

## Structural Evidence

| Check | Before | After |
|---|---:|---:|
| Authorized route-body `get_postgres_async()` calls | 2 | 0 |
| Authorized handler dependency parameters using `get_monitoring_analysis_postgres_async` | 0 | 2 |
| Module-level `get_postgres_async()` calls after migration | n/a | 1 provider call |
| Target router path count in app route table | 6 | 6 |
| OpenAPI exposure for target routes | included | included |

## TDD Evidence

Red test:

```bash
env PYTHONPATH=. pytest -q tests/api/file_tests/test_monitoring_analysis_api.py::TestMonitoringAnalysisAPIFile::test_monitoring_analysis_postgres_async_uses_route_dependency_provider -n 0 --tb=short --no-cov
```

Observed failure before implementation:

```text
AssertionError: get_monitoring_analysis_postgres_async not found in module
```

Green test:

```bash
env PYTHONPATH=. pytest -q tests/api/file_tests/test_monitoring_analysis_api.py::TestMonitoringAnalysisAPIFile::test_monitoring_analysis_postgres_async_uses_route_dependency_provider -n 0 --tb=short --no-cov
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
19 passed
```

## Route / OpenAPI Smoke

Smoke command imported `app.main`, generated `app.openapi()`, and listed routes
owned by `app.api.monitoring_analysis` with transient test environment values.

Result:

```text
routes=548 paths=500 monitoring_analysis_routes=6
('get_health_score_history', '/api/v1/monitoring/analysis/results/{stock_code}', ['GET'], True)
('analyze_portfolio', '/api/v1/monitoring/analysis/portfolio/{watchlist_id}', ['GET'], True)
```

## Lint / OpenSpec

Ruff:

```bash
ruff check web/backend/app/api/monitoring_analysis.py tests/api/file_tests/test_monitoring_analysis_api.py
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

- `get_health_score_history`
- `analyze_portfolio`

Observed degradation:

- MCP impact calls failed with transport closure.
- CLI `context -f web/backend/app/api/monitoring_analysis.py` resolved exact
  handler UIDs for both symbols.
- CLI `impact` does not expose file-path or UID disambiguation and returned
  ambiguous matches with `risk=UNKNOWN` for both names.

This is recorded as a degraded gate, not as a successful LOW-risk report.
Scope is instead constrained by the G2.252 authorization, path-limited task
card, focused TDD structural test, OpenAPI smoke, and mainline scope gate.

Staged `detect_changes` was attempted before commit:

- MCP `detect_changes(scope=staged)` failed with transport closure.
- CLI `gitnexus verify-staged -r mystocks --cwd <worktree> --json` returned
  `ok=true`, `status=stale`, `risk_level=low`, `changed_files=11`,
  `changed_count=19`, and `affected_count=0`.
- The reported stale reason was
  `current_commit_differs_from_indexed_commit`, with indexed commit
  `2ccaf3e5e21f5715c39c1a20642d0271521f9727` and current commit
  `c3e3452440455c8a7955b0779433219abee48c86`.

Treat the CLI result as a stale-index warning, not as current graph approval.
Review should keep using the path-limited task card, focused tests, OpenAPI
smoke, and mainline scope gate as blocking evidence until the GitNexus index is
refreshed.

## Residual Policy

G2.253 does not authorize broader `get_postgres_async()` consumer migration.
If this implementation is accepted, the next lane should be:

- G2.254 no-source monitoring analysis provider closeout / residual refresh

That lane should confirm the two authorized route-body calls remain removed,
refresh residual route consumer counts, and decide the next governance gate
without editing source code. It must not migrate `monitoring_watchlists.py` or
`signal_monitoring` from G2.253 authority.
