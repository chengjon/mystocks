# G2.254 Postgres Async Monitoring Analysis Provider Closeout / Residual Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: closeout / residual refresh evidence for review
- Prepared at: `2026-05-30T20:12:49+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `767c92887348fe25eeaa92685ecb5343717fb326`
- Worktree branch: `g2-254-monitoring-analysis-provider-closeout-refresh`
- Parent gate: G2.253 / PR `#406`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`
- Source edit authority: no

## Boundary

G2.254 is a no-source closeout and residual-refresh lane after PR `#406`
merged G2.253 at `767c92887348fe25eeaa92685ecb5343717fb326`.

This lane records accepted implementation evidence, refreshes residual
`get_postgres_async()` route-consumer distribution, and selects the next
governance gate. It does not authorize or perform backend source edits, test
edits, route path changes, response model changes, OpenAPI exposure changes,
frontend changes, configuration changes, script changes, OpenSpec changes, or
PM2 commands.

## Parent Closeout

G2.253 added `get_monitoring_analysis_postgres_async()` in
`web/backend/app/api/monitoring_analysis.py` and moved the two authorized
route-body `get_postgres_async()` calls behind FastAPI dependency injection.

Closed handlers:

- `get_health_score_history`
- `analyze_portfolio`

Current closeout result:

| Check | Current HEAD |
|---|---:|
| Authorized route-body `get_postgres_async()` calls in `monitoring_analysis.py` | 0 |
| `get_monitoring_analysis_postgres_async()` provider calls | 1 |
| Authorized handler dependency parameters | 2 |
| Target `monitoring_analysis` route count | 6 |
| OpenAPI path count | 500 |

`analyze_portfolio` still preserves
`calculator_factory=Depends(get_monitoring_calculator_factory)`.

## Residual Refresh

Current `web/backend/app/api` scan:

| Metric | Count |
|---|---:|
| Python files scanned | 219 |
| `get_postgres_async` import lines | 19 |
| Actual `get_postgres_async()` calls | 19 |
| Route-decorated residual files | 3 |
| Route-decorated residual calls | 14 |
| Route-adjacent residual files | 5 |
| Route-adjacent residual calls | 5 |

Residual distribution:

| File | Total calls | Route-decorated calls | Route-adjacent calls | Functions |
|---|---:|---:|---:|---|
| `web/backend/app/api/monitoring_watchlists.py` | 7 | 7 | 0 | `create_watchlist`, `list_watchlists`, `get_watchlist`, `delete_watchlist`, `add_stock_to_watchlist`, `list_watchlist_stocks`, `remove_stock_from_watchlist` |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | 4 | 0 | `get_signal_history`, `get_signal_quality_report`, `get_strategy_realtime_monitoring`, `health_check` |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | 3 | 0 | `get_signal_statistics`, `get_active_signals`, `get_strategy_detailed_health` |
| `web/backend/app/api/_data_source_config_responses.py` | 1 | 0 | 1 | `get_config_manager` |
| `web/backend/app/api/_monitoring_portfolio_router.py` | 1 | 0 | 1 | `get_monitoring_postgres_async` |
| `web/backend/app/api/data_source_config.old.py` | 1 | 0 | 1 | `get_config_manager` |
| `web/backend/app/api/monitoring_analysis.py` | 1 | 0 | 1 | `get_monitoring_analysis_postgres_async` |
| `web/backend/app/api/v1/system/settings.py` | 1 | 0 | 1 | `__init__` |

The two provider-only calls in `_monitoring_portfolio_router.py` and
`monitoring_analysis.py` are retained route-local provider seams, not active
route-body residuals.

## Verification

Focused file regression:

```bash
env PYTHONPATH=. pytest -q tests/api/file_tests/test_monitoring_analysis_api.py -n 0 --tb=short --no-cov
```

Result:

```text
19 passed
```

Ruff:

```bash
ruff check web/backend/app/api/monitoring_analysis.py tests/api/file_tests/test_monitoring_analysis_api.py
```

Result:

```text
All checks passed!
```

Route / OpenAPI smoke:

```text
routes=548 paths=500 monitoring_analysis_routes=6
('get_health_score_history', '/api/v1/monitoring/analysis/results/{stock_code}', ['GET'], True)
('analyze_portfolio', '/api/v1/monitoring/analysis/portfolio/{watchlist_id}', ['GET'], True)
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

This is a no-source closeout branch. Staged `detect_changes` was attempted
before commit:

- MCP `detect_changes(scope=staged)` failed with transport closure.
- CLI `gitnexus verify-staged -r mystocks --cwd <worktree> --json` returned
  `ok=true`, `status=stale`, `risk_level=low`, `changed_files=9`,
  `changed_count=0`, and `affected_count=0`.
- The reported stale reason was
  `current_commit_differs_from_indexed_commit`, with indexed commit
  `2ccaf3e5e21f5715c39c1a20642d0271521f9727` and current commit
  `767c92887348fe25eeaa92685ecb5343717fb326`.

Treat the CLI result as a stale-index warning, not as current graph approval.
Review should keep using the no-source task card, markdown governance gate,
OpenAPI smoke, and mainline scope gate as blocking evidence until the GitNexus
index is refreshed.

## Decision

G2.253 is closed for the two authorized `monitoring_analysis.py` route handlers.

Next gate:

- G2.255 no-source `monitoring_watchlists.py` postgres async route provider
  authorization

Rationale:

- `monitoring_watchlists.py` is the largest remaining route-decorated residual
  with 7 direct route-body `get_postgres_async()` calls.
- It includes runtime fallback behavior and multiple CRUD surfaces, so it
  needs a separate no-source authorization packet before any source lane.
- G2.254 does not authorize source edits or bulk route consumer migration.
