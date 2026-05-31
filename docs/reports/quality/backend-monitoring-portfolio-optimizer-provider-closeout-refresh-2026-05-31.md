# Backend Monitoring Portfolio Optimizer Provider Closeout / Residual Refresh - 2026-05-31

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.270`
- Branch: `g2-270-monitoring-provider-closeout-refresh`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `7ed8f8e352f29c9c48bc4a45ea77661b08de89da`
- Source edit authority: none
- Parent PR: `#422`, merged at `7ed8f8e352f29c9c48bc4a45ea77661b08de89da`

Boundary note: this report closes out G2.269 and refreshes residual
monitoring/signal provider-shaped surfaces. It does not authorize backend source
edits, route registration, provider injection, source retirement, test edits,
docs/api edits, frontend/config/script edits, OpenSpec mutation, or
PM2/stateful commands.

## Closeout Result

G2.269 is accepted/merged.

| Check | Current result |
|---|---|
| Parent PR | `#422` is `MERGED` |
| Merge commit | `7ed8f8e352f29c9c48bc4a45ea77661b08de89da` |
| Target route module | `web/backend/app/api/_monitoring_portfolio_router.py` |
| Route-local provider | `get_monitoring_portfolio_optimizer` |
| Target handlers | `get_portfolio_summary`, `get_portfolio_alerts`, `get_rebalance_suggestions` |
| Direct route-body `get_portfolio_optimizer()` calls | `0` |
| Provider backing `get_portfolio_optimizer()` calls | `1` |
| Dependency parameters | `3` |
| Route contract changes | none |

The remaining `get_portfolio_optimizer` references are the domain definition and
the route-local provider import/call:

- `src/monitoring/domain/portfolio_optimizer.py:383`
- `web/backend/app/api/_monitoring_portfolio_router.py:115`
- `web/backend/app/api/_monitoring_portfolio_router.py:117`

## Runtime / OpenAPI Snapshot

Fresh smoke at HEAD `7ed8f8e352f29c9c48bc4a45ea77661b08de89da`:

| Metric | Value |
|---|---:|
| FastAPI routes | 548 |
| OpenAPI paths | 500 |
| Duplicate operation IDs | 0 |
| `_monitoring_portfolio_router` active routes | 3 |
| `monitoring` active routes | 13 |
| `monitoring_analysis` active routes | 6 |
| `monitoring_watchlists` active routes | 8 |
| `signal_monitoring.get_signal_statistics` active routes | 0 |
| `signal_monitoring.signal_history_response` active routes | 4 |
| `v1.pool_monitoring` active routes | 4 |

The smoke used local non-production test environment values. It did not write
environment values or secrets to repository files. A GPU backtest dependency
warning remains unrelated to this no-source closeout.

## Residual Refresh

G2.270 found no remaining active route-body `get_portfolio_optimizer()`
candidate. The remaining monitoring/signal residual set is split as follows:

| Bucket | Files / residuals | Decision |
|---|---|---|
| Retained provider backing wrappers | `_monitoring_portfolio_router.py`, `monitoring_analysis.py`, `monitoring_watchlists.py`, and `signal_history_response.py` each retain one provider backing `get_postgres_async()` call | Retain; do not open source lane from G2.270 |
| Route helper / self-call false positive | `monitoring.py` calls `get_monitoring_summary()` once | Not a service singleton provider candidate |
| Dormant route-shaped source | `signal_monitoring/get_signal_statistics.py` has `0` active routes and retains `get_signal_result_tracker()` / `get_postgres_async()` calls | Already governed by G2.261-G2.266; do not register, inject, or retire source here |
| Control-plane pool accessors | `v1/pool_monitoring.py` calls `get_postgresql_engine()`, `get_tdengine_manager()`, `get_postgresql_pool_stats()`, and `get_tdengine_pool_stats()` | Route/OpenAPI/control-plane ownership decision candidate, not a service DI implementation lane |

## Decision

G2.270 does not authorize source implementation.

Selected next gate:

`G2.271 no-source pool monitoring control-plane accessor ownership / route governance decision`

Rationale: G2.269 closed the only concentrated active monitoring portfolio
optimizer route-body candidate. The remaining actionable residual is a
control-plane route/OpenAPI ownership question in `v1/pool_monitoring.py`, not a
plain service lifecycle DI source lane.

## Verification

- PR `#422`: `MERGED`, merge commit `7ed8f8e352f29c9c48bc4a45ea77661b08de89da`.
- Static residual scan: direct route-body `get_portfolio_optimizer()` calls are `0`.
- Runtime/OpenAPI smoke: `548` routes, `500` paths, duplicate operation IDs `0`.
- Route module map: `get_signal_statistics.py` remains at `0` active routes; `v1.pool_monitoring` has `4` active routes.

## Rollback

Revert the future PR carrying this report and steward updates. No runtime code,
route registration, provider binding, test contract, docs/api artifact,
frontend state, database state, or OpenSpec state is changed by G2.270.
