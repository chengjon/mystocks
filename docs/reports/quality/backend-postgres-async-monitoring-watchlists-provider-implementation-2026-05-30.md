# G2.256 Postgres Async Monitoring Watchlists Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation evidence for review
- Prepared at: `2026-05-30T22:07:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `8866cfe8ba081957714c8c51e948be9340fc45ac`
- Worktree branch: `g2-256-monitoring-watchlists-postgres-provider`
- Parent gate: G2.255 / PR `#408`
- Parent merge commit: `8866cfe8ba081957714c8c51e948be9340fc45ac`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`

## Authorization Boundary

G2.255 authorized one path-limited `monitoring_watchlists.py` postgres async
route provider implementation after PR `#408` merged at
`8866cfe8ba081957714c8c51e948be9340fc45ac`. G2.256 used that authority only
for:

- `web/backend/app/api/monitoring_watchlists.py`
- `tests/api/file_tests/test_watchlist_api.py`
- `web/backend/tests/test_monitoring_watchlists_runtime_fallback.py`
- this evidence package and steward-tree metadata

This lane did not modify `src/monitoring/infrastructure/**`, signal monitoring
route consumers, route paths, response models, summaries, OpenAPI exposure,
frontend code, configuration, scripts, or OpenSpec change/spec files.

## Implementation Summary

`monitoring_watchlists.py` now exposes a route-local dependency provider:

- `get_monitoring_watchlists_postgres_async()`

The provider delegates to the canonical infrastructure facade:

- `src.monitoring.infrastructure.postgresql_async_v3.get_postgres_async()`

The seven authorized watchlist handlers now receive the dependency through
FastAPI `Depends(get_monitoring_watchlists_postgres_async)`:

- `create_watchlist`
- `list_watchlists`
- `get_watchlist`
- `delete_watchlist`
- `add_stock_to_watchlist`
- `list_watchlist_stocks`
- `remove_stock_from_watchlist`

Direct route-body calls to `get_postgres_async()` inside these handlers were
removed. `update_watchlist` remains intentionally untouched because G2.255 did
not identify a direct route-body `get_postgres_async()` call in that handler.
The `StockToAdd` import/use in `add_stock_to_watchlist` was preserved.

Route decorators, paths, HTTP methods, response models, summaries, tags, and
OpenAPI exposure were intentionally left unchanged.

## Structural Evidence

| Check | Before | After |
|---|---:|---:|
| Authorized route-body `get_postgres_async()` calls | 7 | 0 |
| Authorized handler dependency parameters using `get_monitoring_watchlists_postgres_async` | 0 | 7 |
| Module-level `get_postgres_async()` calls after migration | n/a | 1 provider call |
| Watchlist route count in app route table | 8 | 8 |
| `StockToAdd` import/use in `add_stock_to_watchlist` | present | present |

## TDD Evidence

Red test:

```bash
PYTHONPATH=. pytest -q tests/api/file_tests/test_watchlist_api.py::test_watchlist_handlers_use_postgres_dependency_provider -n 0 --tb=short --no-cov
```

Observed failure before implementation:

```text
AssertionError: provider function missing
```

Green test:

```bash
PYTHONPATH=. pytest -q tests/api/file_tests/test_watchlist_api.py::test_watchlist_handlers_use_postgres_dependency_provider -n 0 --tb=short --no-cov
```

Result:

```text
1 passed
```

Focused file regression:

```bash
PYTHONPATH=. pytest -q tests/api/file_tests/test_watchlist_api.py web/backend/tests/test_monitoring_watchlists_runtime_fallback.py -n 0 --tb=short --no-cov
```

Result:

```text
29 passed
```

## Route / OpenAPI Smoke

Smoke command imported `app.main`, generated `app.openapi()`, and listed routes
owned by `app.api.monitoring_watchlists` with transient placeholder environment
values.

Result:

```text
routes=548 paths=500 watchlist_route_count=8
POST /api/v1/monitoring/watchlists
GET /api/v1/monitoring/watchlists
GET /api/v1/monitoring/watchlists/{watchlist_id}
PUT /api/v1/monitoring/watchlists/{watchlist_id}
DELETE /api/v1/monitoring/watchlists/{watchlist_id}
POST /api/v1/monitoring/watchlists/{watchlist_id}/stocks
GET /api/v1/monitoring/watchlists/{watchlist_id}/stocks
DELETE /api/v1/monitoring/watchlists/{watchlist_id}/stocks/{stock_code}
```

## Lint / OpenSpec

Ruff:

```bash
ruff check web/backend/app/api/monitoring_watchlists.py tests/api/file_tests/test_watchlist_api.py web/backend/tests/test_monitoring_watchlists_runtime_fallback.py
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

GitNexus impact analysis was attempted before implementation.

Observed degradation:

- MCP `impact` and `context` calls failed with transport closure.
- CLI `context -f web/backend/app/api/monitoring_watchlists.py` resolved an
  exact handler UID for `add_stock_to_watchlist`.
- CLI `impact` does not expose file-path or UID disambiguation and returned
  ambiguous `risk=UNKNOWN` for common handler names.
- CLI `status` was tied to the root checkout path and therefore could not be
  treated as a current-worktree freshness proof.

This is recorded as a degraded gate, not as a successful LOW-risk report.
Scope is instead constrained by the G2.255 authorization, path-limited task
card, focused TDD structural test, OpenAPI smoke, and mainline scope gate.

Staged `detect_changes` was attempted before commit:

- MCP `detect_changes(scope=staged)` failed with transport closure.
- CLI `gitnexus verify-staged -r mystocks --cwd <worktree> --json` returned
  `ok=true`, `status=stale`, `risk_level=low`, `changed_files=12`,
  `changed_count=23`, and `affected_count=0`.
- The reported stale reason was
  `current_commit_differs_from_indexed_commit`, with indexed commit
  `5f890d8b2e3ea183dd42e3d08d5b599c9582f3ab` and current commit
  `8866cfe8ba081957714c8c51e948be9340fc45ac`.

Treat the CLI result as a stale-index warning, not as current graph approval.
Review should keep using the path-limited task card, focused tests, OpenAPI
smoke, and mainline scope gate as blocking evidence until the GitNexus index is
refreshed.

## Residual Policy

G2.256 does not authorize broader `get_postgres_async()` consumer migration.
Specifically, it does not authorize changes to:

- `web/backend/app/api/signal_monitoring/**`
- `web/backend/app/api/monitoring_analysis.py`
- `web/backend/app/api/_monitoring_portfolio_router.py`
- `web/backend/app/api/_data_source_config_responses.py`
- `web/backend/app/api/v1/system/settings.py`
- `src/monitoring/infrastructure/**`

If this implementation is accepted, the next lane should be:

- G2.257 no-source monitoring watchlists provider closeout / residual refresh

That lane should confirm the seven authorized route-body calls remain removed,
refresh residual route consumer counts, and decide the next governance gate
without editing source code.
