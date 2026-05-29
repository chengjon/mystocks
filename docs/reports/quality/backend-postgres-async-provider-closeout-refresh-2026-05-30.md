# Backend Postgres Async Provider Closeout Refresh - 2026-05-30

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.248`
- Status: `for_review`
- Prepared at: `2026-05-30T01:56:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Current HEAD checked: `76b1644fe925a8c0684a820aa58a0aa8e8170190`
- Source PR closed out: `#400`
- Source merge commit: `76b1644fe925a8c0684a820aa58a0aa8e8170190`

Boundary: this package is a no-source closeout and residual refresh. It does not
authorize backend source edits, API route consumer migration, OpenAPI changes,
frontend changes, PM2 commands, OpenSpec proposal creation, or issue label
changes.

## Closeout Decision

G2.247 is accepted as the implemented infrastructure provider/reset seam for
`get_postgres_async`.

Current HEAD confirms:

- `set_postgres_async_provider(provider)` exists.
- `reset_postgres_async_provider()` exists.
- `PostgresAsyncProvider` exists.
- `src.monitoring.infrastructure.postgresql_async_v3` re-exports the provider
  and reset helpers.
- Lazy singleton fallback remains the default when no explicit provider is
  installed.
- `initialize_postgres_async()` and `close_postgres_async()` remain compatible
  with the provider seam.

The provider/reset seam is closed. Route consumer migration remains open and is
not authorized by this closeout.

## Verification

| Check | Result |
|---|---|
| Focused provider tests | `3 passed` |
| Ruff on provider source/test files | `All checks passed` |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| OpenSpec strict validation | `migrate-backend-singletons-to-lifecycle-di` valid |
| OpenSpec telemetry | PostHog `ECONNREFUSED` after successful validation; telemetry noise |

The app/OpenAPI smoke used test-only environment values and did not use
production secrets.

## Current Residual Snapshot

| Evidence | Value |
|---|---:|
| Files with `get_postgres_async` / provider refs | 70 |
| Definitions | 1 |
| Import lines | 31 |
| Actual calls | 47 |
| Active API files with route-body calls | 7 |
| Active API route-body calls | 21 |
| Active API `Depends(get_postgres_async)` calls | 0 |
| Historical `.old.py` calls | 1 |

Repository-wide token scans also found 4 `Depends(get_postgres_async)`-shaped
references, but the active API route-body consumer scan found `0` live route
dependency bindings. Treat the active API scan as the route migration planning
truth for this lane.

## Active API Route-Body Consumers

| File | Calls | Handling |
|---|---:|---|
| `web/backend/app/api/_data_source_config_responses.py` | 1 | Candidate for future route/provider authorization, not this lane |
| `web/backend/app/api/_monitoring_portfolio_router.py` | 3 | Candidate for future route/provider authorization, not this lane |
| `web/backend/app/api/monitoring_analysis.py` | 2 | Candidate for future route/provider authorization, not this lane |
| `web/backend/app/api/monitoring_watchlists.py` | 7 | Higher-call candidate; requires focused authorization before source work |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 3 | Candidate for future route/provider authorization, not this lane |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | Candidate for future route/provider authorization, not this lane |
| `web/backend/app/api/v1/system/settings.py` | 1 | Candidate for future route/provider authorization, not this lane |

Historical consumer:

- `web/backend/app/api/data_source_config.old.py`: 1 call, historical evidence
  only.

Retained non-API runtime consumers:

- `src/monitoring/async_monitoring.py`
- `src/monitoring/signal_aggregation_task.py`
- `src/monitoring/signal_recorder.py`
- `src/monitoring/signal_result_tracker.py`

These runtime consumers are not route migration targets for G2.248.

## Next Gate

Select G2.249 as a no-source postgres async route consumer provider
authorization package.

G2.249 should:

- classify the seven active API route-body consumer files into candidate
  batches
- choose whether a one-file route-local provider pilot is safe
- define exact future source paths, tests, rollback, and OpenAPI smoke
  requirements if a source lane is later authorized
- keep historical `.old.py`, background monitoring runtime consumers,
  `get_monitoring_db`, route paths, response contracts, and OpenAPI exposure out
  of scope unless separately approved

G2.249 should not edit source code. A source lane may begin only after G2.249 is
reviewed and explicitly accepted.

## Evidence Files

- `.planning/codebase/generated/postgres-async-provider-closeout-refresh-2026-05-30.json`
- `governance/mainline/task-cards/pr-401.yaml`
- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/completed-ledger.md`

## Forbidden Scope

This closeout forbids:

- backend source edits
- test source edits
- API route consumer migration
- route path or OpenAPI changes
- response model or response shape changes
- frontend changes
- PM2 commands
- OpenSpec proposal or spec creation
- `get_monitoring_db` work
- issue label changes
