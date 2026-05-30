# G2.260 Signal History Postgres Async Provider Closeout / Residual Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review
- Prepared at: `2026-05-31T02:09:47+08:00`
- Branch: `g2-260-signal-history-provider-closeout-refresh`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `5dc148e0aa4653f0803eb6a088e90544b6c051e4`
- Parent implementation: G2.259, PR `#412`, merged at `5dc148e0aa4653f0803eb6a088e90544b6c051e4`
- Implementation commit: `f3a99422ea9407ad78a2a31deaeb5c3c857a08ee`
- OpenSpec lane: `migrate-backend-singletons-to-lifecycle-di`

Boundary note: this report is no-source closeout / residual refresh evidence.
It does not authorize source edits, route registration changes, OpenAPI changes,
frontend/config/script edits, PM2 commands, or OpenSpec source/spec edits.

## Parent Closeout

G2.259 remains closed at current HEAD:

| Metric | Result |
|---|---:|
| `app.routes` | 548 |
| `app.openapi()["paths"]` | 500 |
| Active API routes scanned | 513 |
| `get_signal_history_postgres_async` exists | `true` |
| Provider backing `get_postgres_async()` calls | 1 |
| Target route-body direct `get_postgres_async()` calls | 0 |
| Target `postgres_async=Depends(...)` parameters | 4 |

Closed target handlers:

- `get_signal_history`
- `get_signal_quality_report`
- `get_strategy_realtime_monitoring`
- `health_check`

Route/OpenAPI contract state:

- route paths unchanged
- response models unchanged
- OpenAPI exposure unchanged
- target routes remain present in schema

## Verification

Focused tests:

```text
PYTHONPATH=. pytest -q tests/api/file_tests/test_signal_monitoring_api.py web/backend/tests/test_signal_history_response_regressions.py -n 0 --tb=short --no-cov
```

Result:

- `15 passed`

Ruff:

```text
ruff check --no-fix web/backend/app/api/signal_monitoring/signal_history_response.py tests/api/file_tests/test_signal_monitoring_api.py web/backend/tests/test_signal_history_response_regressions.py
```

Result:

- `All checks passed!`

OpenSpec:

```text
openspec validate migrate-backend-singletons-to-lifecycle-di --strict
```

Result:

- `valid`

GitNexus staged check:

- MCP `detect_changes` failed with `Transport closed`.
- CLI fallback `npx gitnexus verify-staged ... --json` returned `ok=true`,
  `risk_level=low`, `changed_count=0`, `affected_count=0`, `changed_files=9`.
- CLI result carried a stale-index warning:
  `current_commit_differs_from_indexed_commit`.

Mainline scope gate:

- command: `python governance/mainline/scripts/mainline_scope_gate.py --task-card governance/mainline/task-cards/pr-413.yaml --schema governance/mainline/schemas/ai-task-card.schema.json --base-sha 5dc148e0aa4653f0803eb6a088e90544b6c051e4 --head-sha HEAD --report /tmp/pr413-mainline-governance-report.json`
- result: `pass=True`
- problem count: `0`
- changed files count: `9`

OpenAPI smoke:

- `routes=548`
- `paths=500`
- `target_route_count=4`

Non-blocking smoke note:

- Import still emits the existing GPU warning:
  `Numba needs NumPy 2.2 or less. Got NumPy 2.4.`

## Residual Refresh

The active app-route body `get_postgres_async()` migration queue is closed at
current HEAD:

| Metric | Result |
|---|---:|
| API Python files scanned | 219 |
| Functions with direct `get_postgres_async()` calls | 10 |
| Total direct `get_postgres_async()` calls | 10 |
| Active app-route body call sites | 0 |

Residual classification:

| Class | Residuals | Handling |
|---|---:|---|
| Retained route-local provider seams | 4 | Keep as provider backing calls |
| Legacy / compatibility surfaces | 3 | Do not migrate from this closeout |
| Static route-like but not app-registered | 3 | Route-registration / ownership decision required |
| Active app-route body consumers | 0 | Closed |

Retained provider seams:

- `web/backend/app/api/_monitoring_portfolio_router.py::get_monitoring_postgres_async`
- `web/backend/app/api/monitoring_analysis.py::get_monitoring_analysis_postgres_async`
- `web/backend/app/api/monitoring_watchlists.py::get_monitoring_watchlists_postgres_async`
- `web/backend/app/api/signal_monitoring/signal_history_response.py::get_signal_history_postgres_async`

Legacy / compatibility surfaces:

- `web/backend/app/api/_data_source_config_responses.py::get_config_manager`
- `web/backend/app/api/data_source_config.old.py::get_config_manager`
- `web/backend/app/api/v1/system/settings.py::__init__`

Static route-like but not app-registered:

- `web/backend/app/api/signal_monitoring/get_signal_statistics.py::get_signal_statistics`
- `web/backend/app/api/signal_monitoring/get_signal_statistics.py::get_active_signals`
- `web/backend/app/api/signal_monitoring/get_signal_statistics.py::get_strategy_detailed_health`

## Decision

Do not open another source implementation lane directly from G2.260.

The active app-route body queue is closed. The remaining actionable uncertainty
is not a simple provider injection; it is route registration and ownership for
`web/backend/app/api/signal_monitoring/get_signal_statistics.py`.

## Next Gate

Start G2.261 as a no-source route-registration / ownership decision package:

- confirm whether `get_signal_statistics.py` is intentionally unregistered
- decide whether it is legacy/deferred, a route ownership gap, or a future
  separately authorized route/provider candidate
- do not edit source, route registration, OpenAPI, frontend, config, scripts, or
  OpenSpec from G2.261
