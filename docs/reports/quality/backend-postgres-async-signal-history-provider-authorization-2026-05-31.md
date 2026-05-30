# Backend Postgres Async Signal History Provider Authorization - 2026-05-31

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a governance evidence artifact. It does not
authorize code changes, test changes, route/OpenAPI changes, OpenSpec proposal
creation, issue label changes, PM2 commands, or PR merges.

## Status

- Status: for review
- G2 node: G2.258
- Branch: `g2-258-signal-history-postgres-provider-authorization`
- Base: `wip/root-dirty-20260403`
- Current HEAD checked: `ad3cc58dbe0dc768488006d22de09085a1a8ee6f`
- Parent: G2.257 / PR `#410`, merged at `ad3cc58dbe0dc768488006d22de09085a1a8ee6f`
- Source edit authority: no

This report is a no-source authorization packet. It does not modify backend
source, tests, OpenAPI, frontend, config, scripts, PM2 state, or OpenSpec files.

## Decision Request

Approve a future G2.259 path-limited implementation lane for
`web/backend/app/api/signal_monitoring/signal_history_response.py`.

The future implementation may move only the four current route-body
`get_postgres_async()` lookups behind a route-local dependency provider, named
`get_signal_history_postgres_async` unless the implementation review finds a
better local name.

## Candidate Snapshot

Current HEAD exposes four active app routes from
`signal_history_response.py`. Each handler still calls `get_postgres_async()`
directly in the route body.

| Handler | Route | Response model | Direct calls | Authorized for future G2.259 |
|---|---|---|---:|---|
| `get_signal_history` | `GET /api/signals/history` | `UnifiedResponse[List[SignalHistoryResponse]]` | 1 | yes |
| `get_signal_quality_report` | `GET /api/signals/quality-report` | `UnifiedResponse[SignalQualityReportResponse]` | 1 | yes |
| `get_strategy_realtime_monitoring` | `GET /api/strategies/{strategy_id}/realtime` | `UnifiedResponse[StrategyRealtimeMonitoringResponse]` | 1 | yes |
| `health_check` | `GET /api/signals/health` | `UnifiedResponse[Dict[str, Any]]` | 1 | yes |

Direct lookup sites:

| Handler | Import line | Call line |
|---|---:|---:|
| `get_signal_history` | 153 | 155 |
| `get_signal_quality_report` | 320 | 322 |
| `get_strategy_realtime_monitoring` | 500 | 502 |
| `health_check` | 651 | 653 |

## Residual Context

G2.257 closed `monitoring_watchlists.py` route-body use and selected this file
as the next active app-route residual candidate.

Current route table smoke confirms:

| Module | App route count | Handling |
|---|---:|---|
| `app.api.signal_monitoring.signal_history_response` | 4 | Select for this no-source authorization |
| `app.api.signal_monitoring.get_signal_statistics` | 0 | Defer until route-registration / ownership confirmation |

G2.258 must not authorize `get_signal_statistics.py`, other
`signal_monitoring` files, route-adjacent helpers, infrastructure, frontend,
config, scripts, PM2 state, or OpenSpec changes.

## Authorized Future Shape

If this packet is approved and merged, G2.259 may implement:

- a route-local provider in
  `web/backend/app/api/signal_monitoring/signal_history_response.py`
- dependency injection parameters for the four authorized handlers
- focused tests that prove route handlers no longer perform route-body
  `get_postgres_async()` lookup
- focused handling for the current direct-call regression test debt without
  changing route contracts

Allowed future G2.259 paths:

- `web/backend/app/api/signal_monitoring/signal_history_response.py`
- `tests/api/file_tests/test_signal_monitoring_api.py`
- `web/backend/tests/test_signal_history_response_regressions.py`

The future implementation must preserve:

- all route paths, methods, summaries, response models, tags, and OpenAPI
  exposure
- `UnifiedResponse` response contracts
- authentication behavior for the three authenticated endpoints
- unauthenticated health-check behavior for `/api/signals/health`
- existing GPU utilization fallback behavior in
  `get_strategy_realtime_monitoring`
- the established route-local provider pattern from G2.250, G2.253, and G2.256

## Pre-existing Test / Lint Debt

Two facts matter before future implementation:

| Check | Current result | Handling |
|---|---|---|
| `web/backend/tests/test_signal_history_response_regressions.py` | `1 failed`: `AttributeError: 'dict' object has no attribute 'active_signals_count'` | Treat as existing direct-call test expectation debt. Future G2.259 must resolve or explicitly scope this before claiming runtime regression green. |
| `ruff check --no-fix ... test_signal_monitoring_api.py ...` | `F811`: imported `api_test_fixtures` is redefined by fixture argument | Treat as existing test lint debt. Future G2.259 may fix only if it touches that file for the authorized structural test. |

During G2.258, ruff auto-fix briefly removed the unused fixture import from
`tests/api/file_tests/test_signal_monitoring_api.py`. Because this lane is
no-source / no-test, that tool side effect was restored before this package was
authored.

## Forbidden For G2.258

G2.258 forbids:

- backend source edits
- test edits
- route or OpenAPI changes
- provider implementation
- `signal_monitoring/get_signal_statistics.py` migration
- other `signal_monitoring/*` migration
- infrastructure/provider reset changes
- frontend, config, scripts, PM2, OpenSpec, or FUNCTION_TREE changes

## Future G2.259 Gates

Before any source edit in G2.259:

1. Re-run GitNexus impact/context for the four target handler symbols.
2. Stop if GitNexus reports HIGH or CRITICAL risk.
3. Add or update a focused red test proving route-body lookup still exists.
4. Implement only the route-local provider seam and handler dependency
   parameters.
5. Resolve or explicitly scope the existing direct-call regression test debt.
6. Run focused signal monitoring file tests and relevant regression tests.
7. Run ruff with `--no-fix` first, then apply any authorized test lint cleanup
   only inside allowed paths.
8. Run app/OpenAPI smoke and preserve `548` routes / `500` paths unless a
   separately approved route/OpenAPI change exists.
9. Run `openspec validate migrate-backend-singletons-to-lifecycle-di --strict`.
10. Run GitNexus detect_changes before commit.

## Verification

| Check | Result |
|---|---|
| File tests | `13 passed` for `tests/api/file_tests/test_signal_monitoring_api.py` |
| Runtime regression test | `1 failed` in `web/backend/tests/test_signal_history_response_regressions.py`, current dict-vs-object expectation debt |
| Candidate source ruff | `ruff check --no-fix web/backend/app/api/signal_monitoring/signal_history_response.py` passed |
| Future touched-set ruff probe | Existing `F811` in `tests/api/file_tests/test_signal_monitoring_api.py`; do not treat as G2.258 source authority |
| App/OpenAPI smoke | `548` routes, `500` paths, `4` target `signal_history_response.py` routes with non-sensitive placeholder required env vars |
| OpenSpec validate | `migrate-backend-singletons-to-lifecycle-di` valid |
| Git status | Clean before authoring governance files |

## GitNexus Gate

G2.258 is no-source, so it does not run symbol impact as source-edit approval.
The future G2.259 implementation must rerun GitNexus impact/context before
editing and stop on HIGH or CRITICAL risk.

Staged `detect_changes` was attempted before commit:

- MCP `detect_changes(scope=staged)` failed with transport closure.
- CLI `gitnexus verify-staged -r mystocks --cwd <worktree> --json` returned
  `ok=true`, `status=stale`, `risk_level=low`, `changed_files=9`,
  `changed_count=0`, and `affected_count=0`.
- The reported stale reason was
  `current_commit_differs_from_indexed_commit`, with indexed commit
  `69210efb539686c22af457ce1e1fa96d43fd6f7d` and current commit
  `ad3cc58dbe0dc768488006d22de09085a1a8ee6f`.

Treat the CLI result as a stale-index warning, not as current graph approval.
Review should keep using the no-source task card, markdown governance gate,
OpenAPI smoke, and mainline scope gate as blocking evidence until the GitNexus
index is refreshed.

## Decision

Recommended review decision: approve G2.258 as a no-source authorization packet
for a future G2.259 path-limited implementation.

Do not migrate `get_signal_statistics.py`, other `signal_monitoring` files,
route-adjacent helpers, infrastructure, frontend, config, scripts, OpenSpec,
PM2 state, or broader route consumers from this packet.
