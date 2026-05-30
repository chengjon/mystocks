# G2.251 Postgres Async Monitoring Portfolio Provider Closeout / Residual Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: no-source closeout / residual refresh for review
- Prepared at: `2026-05-30T18:37:32+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `27b3fbe5dbf5bb9c941490e9d921fedc5b38f8db`
- Worktree branch: `g2-251-monitoring-portfolio-provider-closeout-refresh`
- Parent gate: G2.250 / PR `#403`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`

## Boundary

G2.251 is a no-source closeout and residual-refresh lane. It records the
accepted G2.250 provider implementation and chooses the next governance gate.

It does not authorize or perform:

- backend source edits
- test edits
- route path, response model, or OpenAPI exposure changes
- frontend, config, script, PM2, or OpenSpec changes
- broader `get_postgres_async()` route consumer migration

## Parent Closeout

PR `#403` merged G2.250 at
`27b3fbe5dbf5bb9c941490e9d921fedc5b38f8db`.

Accepted implementation:

| Evidence | Value |
|---|---:|
| Route-local provider | `get_monitoring_postgres_async` |
| Authorized handlers updated | 3 |
| Authorized route-body `get_postgres_async()` calls | 0 |
| Authorized `Depends(get_monitoring_postgres_async)` parameters | 3 |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| Target monitoring portfolio routes | 3 |

The route-local provider call in `_monitoring_portfolio_router.py` is now an
intentional provider seam. It is not route-body debt.

## Residual Refresh

Current scan root:

- `web/backend/app/api`

Current HEAD:

- `27b3fbe5dbf5bb9c941490e9d921fedc5b38f8db`

Summary:

| Metric | Value |
|---|---:|
| Python files scanned | 218 |
| `get_postgres_async` import lines | 19 |
| Actual `get_postgres_async()` calls | 19 |
| Files with function-level calls | 7 |
| Route-decorated residual files | 4 |
| Route-decorated residual calls | 16 |
| Route-adjacent residual files | 3 |
| Route-adjacent residual calls | 3 |

Route-decorated residuals:

| File | Calls | Handling |
|---|---:|---|
| `web/backend/app/api/monitoring_watchlists.py` | 7 | Defer as higher-call batch |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | Defer as signal domain batch |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | Defer as signal domain batch |
| `web/backend/app/api/monitoring_analysis.py` | 2 | Select for next no-source authorization gate |

Route-adjacent residuals:

| File | Calls | Handling |
|---|---:|---|
| `web/backend/app/api/_monitoring_portfolio_router.py` | 1 | Intentional route-local provider seam |
| `web/backend/app/api/_data_source_config_responses.py` | 1 | Helper / facade ownership decision needed |
| `web/backend/app/api/v1/system/settings.py` | 1 | Repository constructor ownership decision needed |

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
ruff check web/backend/app/api/_monitoring_portfolio_router.py tests/api/file_tests/test_monitoring_analysis_api.py
```

Result:

```text
All checks passed!
```

Route / OpenAPI smoke:

```text
routes=548 paths=500 target_routes=3
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
  `status=stale`, `risk_level=low`, `changed_files=9`,
  `changed_count=0`, `affected_count=0`, `changed_symbols=0`, and
  `affected_processes=0`.
- The stale reason was `current_commit_differs_from_indexed_commit`, with
  indexed commit `8bb84173873600c448354d18ac5f530848aaad72` and current commit
  `27b3fbe5dbf5bb9c941490e9d921fedc5b38f8db`.

Treat this as degraded GitNexus evidence because the index is stale. It is still
consistent with the no-source scope: no symbols or execution flows were reported
for the staged governance-only diff.

## Decision

Close G2.250 as accepted and route the next step to:

- G2.252 no-source `monitoring_analysis.py` postgres async route consumer
  provider authorization

Reason:

- `monitoring_analysis.py` is the smallest remaining route-decorated residual
  file after the portfolio pilot, with 2 route-body `get_postgres_async()` calls.
- Starting with an authorization packet preserves the established conveyor:
  refresh -> decision / authorization -> implementation -> closeout.

G2.251 does not authorize source work for G2.252. G2.252 should only decide
whether a future path-limited implementation lane may touch
`web/backend/app/api/monitoring_analysis.py` and the existing focused file-test
surface.
