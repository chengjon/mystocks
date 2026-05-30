# G2.252 Monitoring Analysis Postgres Async Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: no-source authorization packet for review
- Prepared at: `2026-05-30T19:10:19+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `d6c98b1f0747f9be694451a2e8d4a49d6d67341f`
- Worktree branch: `g2-252-monitoring-analysis-postgres-provider-authorization`
- Parent gate: G2.251 / PR `#404`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`

## Boundary

G2.252 is authorization only. It does not modify backend source, tests, route
contracts, OpenAPI, frontend, config, scripts, PM2 state, or OpenSpec files.

If accepted, it authorizes only a future G2.253 source lane for:

- `web/backend/app/api/monitoring_analysis.py`
- `tests/api/file_tests/test_monitoring_analysis_api.py`

It does not authorize bulk `get_postgres_async()` consumer migration.

## Current Residual Snapshot

Current HEAD:

- `d6c98b1f0747f9be694451a2e8d4a49d6d67341f`

Summary:

| Metric | Value |
|---|---:|
| Python files scanned under `web/backend/app/api` | 218 |
| `get_postgres_async` import lines | 19 |
| Actual `get_postgres_async()` calls | 19 |
| Route-decorated residual files | 4 |
| Route-decorated residual calls | 16 |
| Route-adjacent residual files | 3 |
| Route-adjacent residual calls | 3 |

Remaining route-decorated residuals:

| File | Calls | Handling |
|---|---:|---|
| `web/backend/app/api/monitoring_watchlists.py` | 7 | Defer as higher-call batch |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | Defer as signal domain batch |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | Defer as signal domain batch |
| `web/backend/app/api/monitoring_analysis.py` | 2 | Authorize as next path-limited pilot candidate |

## Candidate Details

`monitoring_analysis.py` has two route-decorated direct
`get_postgres_async()` consumers:

| Handler | Route | Response model | Existing dependency to preserve |
|---|---|---|---|
| `get_health_score_history` | `GET /results/{stock_code}` | `UnifiedResponse[List[HealthScoreResponse]]` | none |
| `analyze_portfolio` | `GET /portfolio/{watchlist_id}` | `UnifiedResponse[PortfolioAnalysisResponse]` | `calculator_factory=Depends(get_monitoring_calculator_factory)` |

Selection rationale:

- It is the smallest remaining route-decorated residual file after G2.250 and
  G2.251.
- It has 2 direct route-body calls, both in the same module.
- It already shares the focused file-test surface used by the previous
  monitoring analysis and portfolio route governance work.

## Authorized Future Shape

If G2.252 is accepted, G2.253 may add a route-local provider in
`monitoring_analysis.py`, tentatively:

- `get_monitoring_analysis_postgres_async`

The provider should delegate to:

- `src.monitoring.infrastructure.postgresql_async_v3.get_postgres_async`

Future G2.253 must preserve:

- route paths
- HTTP methods
- `response_model` declarations
- `UnifiedResponse` behavior
- `include_in_schema` behavior
- `calculator_factory=Depends(get_monitoring_calculator_factory)` on
  `analyze_portfolio`
- existing database connection error behavior

## Forbidden For G2.253

The future source lane must not touch:

- `web/backend/app/api/_monitoring_portfolio_router.py`
- `web/backend/app/api/monitoring_watchlists.py`
- `web/backend/app/api/signal_monitoring/**`
- `web/backend/app/api/_data_source_config_responses.py`
- `web/backend/app/api/v1/system/settings.py`
- `src/monitoring/infrastructure/**`
- `web/backend/app/services/**`
- `web/backend/app/tasks/**`
- `web/frontend/**`
- `docs/api/**`
- `docs/FUNCTION_TREE.md`
- `governance/function-tree/catalog.yaml`
- `config/**`
- `scripts/**`
- `openspec/changes/**`
- `openspec/specs/**`

## Decision

Authorize G2.253 as a future path-limited implementation lane for
`monitoring_analysis.py` and the existing focused file-test path.

Do not implement source changes from G2.252. The next lane must run its own
pre-edit GitNexus impact attempt, TDD red/green, focused tests, OpenAPI smoke,
mainline scope gate, and staged change detection.

## Verification

Focused file tests:

```bash
env PYTHONPATH=. pytest -q tests/api/file_tests/test_monitoring_analysis_api.py -n 0 --tb=short --no-cov
```

Result:

```text
18 passed
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

Staged `detect_changes` was attempted before commit:

- MCP `detect_changes(scope=staged)` failed with transport closure.
- CLI `gitnexus verify-staged -r mystocks --cwd <worktree> --json` returned
  `status=blocked`.
- The CLI error said LadybugDB was unavailable for `mystocks` and may be under
  rebuild; the runtime exception was read-only shadow page replay failure.

Treat this as a degraded GitNexus gate. G2.252 remains no-source and is also
bounded by the PR task card, markdown governance gate, OpenSpec validation, and
mainline scope gate.
