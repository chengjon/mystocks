# Backend Monitoring Calculator Factory Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2: `G2.237`
- Status: authorization packet for review
- Prepared at: `2026-05-29T19:13:42+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `f39aca8815d59739787349ed1025e7a1b7e2c050`
- Parent: G2.236, PR `#389`, merge commit `f39aca8815d59739787349ed1025e7a1b7e2c050`
- Source edit authority now: No
- Fixed guard: G2.237 does not authorize source edits in this PR and does not create G2.238.

This is a no-source authorization packet. It turns the accepted G2.236 ownership
decision into a bounded future implementation lane proposal. It does not modify
backend source files, tests, OpenAPI schema, route behavior, issue labels, or
OpenSpec specs.

## Parent Decision

G2.236 accepted this classification:

- `src/monitoring/domain/calculator_factory.py:get_calculator_factory` remains
  owned by the monitoring domain.
- The active migration concern is not a domain factory rewrite.
- The active seam is an API route/provider seam: 8 route handlers call
  `get_calculator_factory()` inside route bodies.
- A future provider lane must preserve the domain factory and route contracts.

## Authorization Recommendation

If G2.237 is accepted, create a separate source implementation lane:

- Future lane: `G2.238 monitoring calculator factory provider injection`
- Future source authority: only after G2.237 is accepted
- Future source files:
  - `web/backend/app/api/monitoring_analysis.py`
  - `web/backend/app/api/_monitoring_portfolio_router.py`
- Future test file:
  - `tests/api/file_tests/test_monitoring_analysis_api.py`
- Verification-only file:
  - `web/backend/tests/test_health_route_conflicts.py`

G2.237 itself authorizes none of those source or test edits.

## Authorized Future Shape

The recommended future implementation shape is intentionally narrow:

1. Add explicit FastAPI dependency provider(s), recommended name
   `get_monitoring_calculator_factory`, returning `HealthCalculatorFactory`.
2. Preserve lazy import behavior by keeping the domain import inside the provider
   unless fresh startup evidence proves module-level import is safe.
3. Replace the 8 route-body `get_calculator_factory()` calls with
   `Depends(get_monitoring_calculator_factory)` parameters.
4. Keep provider definitions local to the two authorized API modules unless a
   future authorization explicitly permits a shared helper file.
5. Preserve all route paths, methods, response models, `UnifiedResponse`
   contracts, status semantics, and OpenAPI exposure.

## Active Route Consumers

| File | Handler | Factory call line | Route |
|---|---:|---:|---|
| `web/backend/app/api/_monitoring_portfolio_router.py` | `get_portfolio_summary` | 159 | `GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}/summary` |
| `web/backend/app/api/_monitoring_portfolio_router.py` | `get_portfolio_alerts` | 228 | `GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}/alerts` |
| `web/backend/app/api/_monitoring_portfolio_router.py` | `get_rebalance_suggestions` | 299 | `GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}/rebalance` |
| `web/backend/app/api/monitoring_analysis.py` | `calculate_health_score` | 152 | `POST /api/v1/monitoring/analysis/calculate` |
| `web/backend/app/api/monitoring_analysis.py` | `batch_calculate_health_scores` | 212 | `POST /api/v1/monitoring/analysis/calculate/batch` |
| `web/backend/app/api/monitoring_analysis.py` | `analyze_portfolio` | 349 | `GET /api/v1/monitoring/analysis/portfolio/{watchlist_id}` |
| `web/backend/app/api/monitoring_analysis.py` | `identify_market_regime` | 476 | `GET /api/v1/monitoring/analysis/market-regime` |
| `web/backend/app/api/monitoring_analysis.py` | `get_engine_status` | 517 | `GET /api/v1/monitoring/analysis/engine/status` |

Non-consumer in the same module:

- `web/backend/app/api/monitoring_analysis.py:get_health_score_history`
  serves `GET /api/v1/monitoring/analysis/results/{stock_code}` and does not
  call `get_calculator_factory()`.

## GitNexus Risk Signal

The GitNexus MCP impact call returned `Transport closed`, so this packet uses
the CLI fallback:

```text
gitnexus impact get_calculator_factory --direction upstream --repo mystocks --summary-only
```

Result:

- Risk: HIGH
- Impacted count: 9
- Direct: 9
- Processes affected: 3
- Modules affected: 2

This is why G2.237 is an authorization packet rather than a direct source lane.
A future G2.238 implementation must run fresh GitNexus impact/context before
editing and staged/compare detect before commit.

## Required Preservation Boundary

A future implementation must preserve:

- all current route paths and HTTP methods
- app/OpenAPI smoke `routes=548`, `paths=500`, unless the base changes
- response models and `UnifiedResponse` contracts
- `HealthCalculatorFactory` domain ownership and behavior
- lazy import/startup behavior unless implementation evidence proves otherwise
- existing monitoring analysis test behavior

A future implementation must not:

- rewrite `src/monitoring/domain/calculator_factory.py`
- change calculator construction or GPU/CPU/risk selection semantics
- edit `get_mock_data_manager`, `get_monitoring_db`, or `get_postgres_async`
- bundle unrelated monitoring route cleanup
- change frontend, config, docs API contracts, OpenSpec changes, or route paths

## Required Future Verification

G2.238, if created, must include at least:

- GitNexus impact/context before editing `get_calculator_factory` consumers
- `pytest -o addopts= tests/api/file_tests/test_monitoring_analysis_api.py -q --no-cov --tb=short`
- `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov`
- `app.main` import and `app.openapi()` smoke
- ruff check for authorized future source/test files
- static guard showing active route-body `get_calculator_factory()` calls in the
  8 target handlers are reduced to `0`
- GitNexus staged and compare detect

## Current Verification

This G2.237 packet reuses the accepted G2.236 current-HEAD evidence and adds the
authorization boundary. Fresh PR validation for this no-source packet must still
run:

- JSON parse for the generated authorization artifact and steward index
- Markdown governance gate for the changed docs
- OpenSpec strict validation for `migrate-backend-singletons-to-lifecycle-di`
- app/OpenAPI smoke
- mainline scope gate for PR `#390`
- GitNexus staged/compare detect

## Next Gate

Review G2.237. If accepted, create G2.238 as a separate implementation lane with
only the bounded source/test paths listed above. Do not start source
implementation from G2.237 before review acceptance.
