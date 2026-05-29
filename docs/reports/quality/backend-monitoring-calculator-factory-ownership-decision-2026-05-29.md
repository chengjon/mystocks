# Backend Monitoring Calculator Factory Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.236
- Status: for review
- Generated at: `2026-05-29T18:30:00+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `383598ab2a30da31513468b97537183322b46af9`
- Parent PR: `#388`
- Source edit authority: No
- G2.237 created: No
- Fixed guard: G2.236 does not authorize source edits and does not create G2.237.

This package is a no-source ownership / provider seam decision packet for
`get_calculator_factory`. It does not authorize backend source edits, test
edits, route/OpenAPI changes, issue label movement, OpenSpec proposal creation,
PM2 commands, frontend work, or creation of a G2.237 implementation lane.

## Parent State

PR `#388` merged G2.235 at
`383598ab2a30da31513468b97537183322b46af9`.

G2.235 selected `get_calculator_factory` as the next bounded HIGH-risk
service-lifecycle decision target after `get_config_manager` was closed for
active route-body calls.

## Ownership Classification

| Surface | Current owner | Decision |
|---|---|---|
| `src/monitoring/domain/calculator_factory.py:get_calculator_factory` | Monitoring domain calculator factory | Retain as canonical domain factory / singleton-backed factory accessor |
| API call sites in `_monitoring_portfolio_router.py` and `monitoring_analysis.py` | Monitoring analysis API route layer | Classify as route-body direct factory lookup seam |
| `src/monitoring/domain/calculator_factory.py:calculate_health_score` | Monitoring domain helper | Retain; not a route-provider migration target |

The active architecture issue is not a domain factory rewrite. It is a route
provider seam: several route handlers call the domain factory accessor directly
inside handler bodies.

## Active Route Consumers

| File | Handler | Route | Direct call |
|---|---|---|---:|
| `web/backend/app/api/_monitoring_portfolio_router.py` | `get_portfolio_summary` | `GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}/summary` | line 159 |
| `web/backend/app/api/_monitoring_portfolio_router.py` | `get_portfolio_alerts` | `GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}/alerts` | line 228 |
| `web/backend/app/api/_monitoring_portfolio_router.py` | `get_rebalance_suggestions` | `GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}/rebalance` | line 299 |
| `web/backend/app/api/monitoring_analysis.py` | `calculate_health_score` | `POST /api/v1/monitoring/analysis/calculate` | line 152 |
| `web/backend/app/api/monitoring_analysis.py` | `batch_calculate_health_scores` | `POST /api/v1/monitoring/analysis/calculate/batch` | line 212 |
| `web/backend/app/api/monitoring_analysis.py` | `analyze_portfolio` | `GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}` | line 349 |
| `web/backend/app/api/monitoring_analysis.py` | `identify_market_regime` | `GET /api/v1/monitoring/analysis/market-regime` | line 476 |
| `web/backend/app/api/monitoring_analysis.py` | `get_engine_status` | `GET /api/v1/monitoring/analysis/engine/status` | line 517 |

All listed routes are included in the OpenAPI schema. Current app/OpenAPI smoke
remains `routes=548`, `paths=500`.

`web/backend/app/api/monitoring_analysis.py:get_health_score_history` lives in
the same module but does not call `get_calculator_factory()` and should not be
included as a provider-injection target without new evidence.

## GitNexus Risk Signal

The current root GitNexus index is stale relative to the G2.236 worktree, so the
impact sample is directional rather than binding. Current-HEAD text scan and
app/OpenAPI smoke are the binding evidence for this decision packet.

| Target | Risk | Direct | Affected processes | Affected modules |
|---|---:|---:|---:|---:|
| `get_calculator_factory` | HIGH | 9 | 3 | 2 |

Affected process names reported by GitNexus:

- `get_portfolio_summary`
- `get_rebalance_suggestions`
- `get_portfolio_alerts`

## Decision

`get_calculator_factory` should remain owned by the monitoring domain factory.
The API layer owns the provider seam problem.

If G2.236 is accepted, the next step should be a separate no-source G2.237
authorization packet for a monitoring calculator factory provider injection
lane. G2.236 does not create G2.237 and does not authorize implementation.

G2.237, if created after review, should evaluate this minimum future scope:

- `web/backend/app/api/_monitoring_portfolio_router.py`
- `web/backend/app/api/monitoring_analysis.py`
- `tests/api/file_tests/test_monitoring_analysis_api.py`
- optional focused provider-injection regression test

The likely future source pattern is route/API-level provider injection or
provider wrapper introduction while leaving the domain factory contract intact.
G2.237 must decide the exact implementation shape before any code is edited.

## Required Preservation Boundary

A future authorization packet must preserve:

- route paths
- `response_model` declarations
- OpenAPI `include_in_schema` states
- request and response schemas
- current error handling via `@handle_exceptions`
- domain factory default behavior
- lazy import / startup behavior unless explicitly approved

A future authorization packet must not include:

- rewriting `src/monitoring/domain/calculator_factory.py`
- `get_mock_data_manager`
- `get_monitoring_db`
- `get_postgres_async`
- route/OpenAPI contract edits
- frontend edits
- config or script edits
- OpenSpec change creation

## Verification

| Check | Result |
|---|---|
| Current HEAD scan | Completed at `383598ab2a30da31513468b97537183322b46af9` |
| `tests/api/file_tests/test_monitoring_analysis_api.py` | 16 passed |
| `web/backend/tests/test_health_route_conflicts.py --collect-only` | 121 tests collected |
| app/OpenAPI smoke | `routes=548`, `paths=500` |
| Source files changed | None |
| Test files changed | None |
| OpenSpec changes created | None |

Remaining required gates before PR review:

- JSON parse for generated artifact and `steward-index.json`
- Markdown governance gate
- OpenSpec strict validate for `migrate-backend-singletons-to-lifecycle-di`
- Mainline scope gate
- GitNexus staged/compare detect for docs-only diff

## Next Gate

Review G2.236. Only if accepted, consider creating G2.237 as a no-source
monitoring calculator factory provider authorization packet. Do not start source
implementation from G2.236.
