# G2.257 Postgres Async Monitoring Watchlists Provider Closeout / Residual Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: closeout / residual refresh evidence for review
- Prepared at: `2026-05-31T00:15:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `536b0634a51ea580f1a384d07a8ee605fbed8567`
- Worktree branch: `g2-257-monitoring-watchlists-provider-closeout-refresh`
- Parent gate: G2.256 / PR `#409`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`
- Source edit authority: no

## Boundary

G2.257 is a no-source closeout and residual-refresh lane after PR `#409`
merged G2.256 at `536b0634a51ea580f1a384d07a8ee605fbed8567`.

This lane records accepted implementation evidence, refreshes residual
`get_postgres_async()` route-consumer distribution, and selects the next
governance gate. It does not authorize or perform backend source edits, test
edits, route path changes, response model changes, OpenAPI exposure changes,
frontend changes, configuration changes, script changes, OpenSpec changes, or
PM2 commands.

## Parent Closeout

G2.256 added `get_monitoring_watchlists_postgres_async()` in
`web/backend/app/api/monitoring_watchlists.py` and moved the seven authorized
route-body `get_postgres_async()` calls behind FastAPI dependency injection.

Closed handlers:

- `create_watchlist`
- `list_watchlists`
- `get_watchlist`
- `delete_watchlist`
- `add_stock_to_watchlist`
- `list_watchlist_stocks`
- `remove_stock_from_watchlist`

Current closeout result:

| Check | Current HEAD |
|---|---:|
| Authorized route-body `get_postgres_async()` calls in `monitoring_watchlists.py` | 0 |
| `get_monitoring_watchlists_postgres_async()` provider calls | 1 |
| Authorized handler dependency parameters | 7 |
| Target watchlist route count | 8 |
| OpenAPI path count | 500 |
| `StockToAdd` import/use in `add_stock_to_watchlist` | preserved |

`update_watchlist` remains untouched because G2.255 did not identify a direct
route-body `get_postgres_async()` call there.

## Residual Refresh

Current `web/backend/app/api` scan:

| Metric | Count |
|---|---:|
| Python files scanned | 219 |
| `get_postgres_async` import lines | 13 |
| Actual `get_postgres_async()` calls | 13 |
| Active app-route residual calls | 4 |
| Static route-like calls not present in current app route table | 3 |
| Retained route-local provider seam calls | 3 |
| Route-adjacent / legacy calls | 3 |

Residual distribution:

| File | Calls | Classification | Functions |
|---|---:|---|---|
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | active app-route residual | `get_signal_history`, `get_signal_quality_report`, `get_strategy_realtime_monitoring`, `health_check` |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | static route-like but not app-registered in current smoke | `get_signal_statistics`, `get_active_signals`, `get_strategy_detailed_health` |
| `web/backend/app/api/monitoring_watchlists.py` | 1 | retained route-local provider seam | `get_monitoring_watchlists_postgres_async` |
| `web/backend/app/api/monitoring_analysis.py` | 1 | retained route-local provider seam | `get_monitoring_analysis_postgres_async` |
| `web/backend/app/api/_monitoring_portfolio_router.py` | 1 | retained route-local provider seam | `get_monitoring_postgres_async` |
| `web/backend/app/api/_data_source_config_responses.py` | 1 | route-adjacent helper | `get_config_manager` |
| `web/backend/app/api/v1/system/settings.py` | 1 | control-plane route-adjacent class | `__init__` |
| `web/backend/app/api/data_source_config.old.py` | 1 | legacy old file | `get_config_manager` |

The provider-only calls in `monitoring_watchlists.py`, `monitoring_analysis.py`,
and `_monitoring_portfolio_router.py` are retained route-local provider seams,
not active route-body residuals.

## Verification

Focused file regression:

```bash
PYTHONPATH=. pytest -q tests/api/file_tests/test_watchlist_api.py web/backend/tests/test_monitoring_watchlists_runtime_fallback.py -n 0 --tb=short --no-cov
```

Result:

```text
29 passed
```

Ruff:

```bash
ruff check web/backend/app/api/monitoring_watchlists.py tests/api/file_tests/test_watchlist_api.py web/backend/tests/test_monitoring_watchlists_runtime_fallback.py
```

Result:

```text
All checks passed!
```

Route / OpenAPI smoke:

```text
routes=548 paths=500 watchlist_route_count=8 signal_history_routes=4 signal_statistics_routes=0 settings_routes=4
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
  `5f890d8b2e3ea183dd42e3d08d5b599c9582f3ab` and current commit
  `536b0634a51ea580f1a384d07a8ee605fbed8567`.

Treat the CLI result as a stale-index warning, not as current graph approval.
Review should keep using the no-source task card, markdown governance gate,
OpenAPI smoke, and mainline scope gate as blocking evidence until the GitNexus
index is refreshed.

## Decision

G2.256 is closed for the seven authorized `monitoring_watchlists.py` route
handlers.

Next gate:

- G2.258 no-source `signal_monitoring/signal_history_response.py` postgres
  async route provider authorization

Rationale:

- `signal_history_response.py` is the largest remaining active app-route
  residual surface with four direct `get_postgres_async()` calls in the current
  route table.
- `get_signal_statistics.py` still has three static route-like calls, but the
  current `app.main` route table smoke does not expose those functions as active
  app routes. It should be handled only after a separate route-registration /
  ownership check.
- G2.257 does not authorize source edits or bulk route consumer migration.
