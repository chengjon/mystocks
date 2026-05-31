# Backend Monitoring / Signal Residual Classification Refresh - 2026-05-31

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.267`
- Branch: `g2-267-monitoring-signal-residual-classification-refresh`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `eec68bb47a4ee98508480ef0ac2cdd3716e04b05`
- Source edit authority: none
- Parent PR: `#419`, merged at `eec68bb47a4ee98508480ef0ac2cdd3716e04b05`

Boundary note: this report classifies residual provider-shaped calls only. It does not authorize backend source edits, route registration, provider injection, source retirement, test edits, docs/api edits, frontend/config/script edits, OpenSpec mutation, or PM2/stateful commands.

## Classification Result

G2.267 classifies the monitoring/signal residual set into five groups:

| Bucket | Files / symbols | Decision |
|---|---|---|
| Active route-body authorization candidate | `web/backend/app/api/_monitoring_portfolio_router.py` calls `get_portfolio_optimizer()` in `get_portfolio_summary`, `get_portfolio_alerts`, and `get_rebalance_suggestions` | Select `G2.268 no-source monitoring portfolio optimizer route provider authorization` |
| Retained provider backing wrappers | `get_monitoring_calculator_factory`, `get_monitoring_postgres_async`, `get_monitoring_analysis_postgres_async`, `get_monitoring_watchlists_postgres_async`, `get_signal_history_postgres_async` | Retain; do not open source lane from G2.267 |
| Route helper / self-call false positive | `web/backend/app/api/monitoring.py::analyze_monitoring` calls `get_monitoring_summary()` | Not a service singleton provider candidate |
| Control-plane pool accessors | `web/backend/app/api/v1/pool_monitoring.py` calls PostgreSQL/TDengine pool accessors and local stats functions | Route/OpenAPI/control-plane governance candidate, not service DI source lane |
| Dormant false positive | `web/backend/app/api/signal_monitoring/get_signal_statistics.py` has route-shaped getter calls but `0` active FastAPI routes | Retain dormant; do not register, inject, or retire source |

## Active Route Evidence

FastAPI route module map:

| Module | Active routes | Classification |
|---|---:|---|
| `app.api._monitoring_portfolio_router` | 3 | Active route-body candidate |
| `app.api.monitoring` | 13 | Mostly route/helper and monitoring control surface |
| `app.api.monitoring_analysis` | 6 | Retained provider backing wrappers |
| `app.api.monitoring_watchlists` | 8 | Retained provider backing wrapper |
| `app.api.signal_monitoring.get_signal_statistics` | 0 | Dormant false positive |
| `app.api.signal_monitoring.signal_history_response` | 4 | Previously governed signal-history route surface |
| `app.api.v1.pool_monitoring` | 4 | Control-plane pool monitoring |

Static grep for the selected candidate found one definition and three active route call sites:

- `src/monitoring/domain/portfolio_optimizer.py:383`: `def get_portfolio_optimizer(...)`
- `web/backend/app/api/_monitoring_portfolio_router.py:171`
- `web/backend/app/api/_monitoring_portfolio_router.py:239`
- `web/backend/app/api/_monitoring_portfolio_router.py:309`

## GitNexus Note

GitNexus MCP `context` and `impact` queries for `get_portfolio_optimizer` timed out after 120 seconds in this session. G2.267 therefore records the timeout and uses static AST / route-table / grep evidence for no-source classification only.

This timeout must be revisited in G2.268 before any future authorization package can approve source edits. If GitNexus remains unavailable, the authorization package must explicitly document fallback evidence and risk limits.

## Decision

G2.267 does not authorize source implementation.

Selected next gate:

`G2.268 no-source monitoring portfolio optimizer route provider authorization`

G2.268 should decide whether the three active `get_portfolio_optimizer()` route-body calls in `_monitoring_portfolio_router.py` are suitable for a future path-limited provider injection lane. It must remain no-source unless separately approved.

## Verification

- PR `#419`: `MERGED`, merge commit `eec68bb47a4ee98508480ef0ac2cdd3716e04b05`.
- AST residual context: monitoring/signal files classified by enclosing function, decorator, and active-route status.
- FastAPI route module map: `get_signal_statistics.py` has `0` active routes; `_monitoring_portfolio_router.py` has `3` active routes.
- Static grep: `get_portfolio_optimizer` has one definition and three active route call sites.

## Rollback

Revert the future PR carrying this report and steward updates. No runtime code, route registration, provider binding, test contract, docs/api artifact, frontend state, database state, or OpenSpec state is changed by G2.267.
