# Backend Signal Statistics Dormant Contract Closeout / Residual Refresh - 2026-05-31

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.266`
- Branch: `g2-266-signal-statistics-dormant-closeout-refresh`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `2b53352d6869f66147ce3892b1b0a7174ba064b4`
- Source edit authority: none
- Parent PR: `#418`, merged at `2b53352d6869f66147ce3892b1b0a7174ba064b4`

Boundary note: this report closes out G2.265 and refreshes residual ownership. It does not authorize backend source edits, route registration, provider injection, source retirement, frontend/config/script edits, OpenSpec mutation, or PM2/stateful commands.

## Closeout Result

G2.265 is accepted/merged by PR `#418`.

- `docs/api/openapi.yaml` target path references are now `0` for `/api/signals/statistics` and `0` for `/api/signals/active`.
- Runtime FastAPI smoke remains `548` routes and `500` OpenAPI paths.
- Runtime OpenAPI target paths remain absent: `[]`.
- Duplicate operation IDs remain `0`.
- Targeted tests pass `2/2`; both stale endpoint tests now assert explicit dormant-route `404 Not Found` behavior.
- `web/backend/app/api/signal_monitoring/get_signal_statistics.py` remains retained dormant source and is not a source implementation target.

## Residual Refresh

The post-closeout scan found `57` `get_*()` call-bearing files under `web/backend/app/api`. Monitoring/signal-shaped residuals still need classification before any implementation lane:

| File | Residual shape | G2.266 disposition |
|---|---|---|
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | `get_postgres_async` x3, `get_signal_result_tracker` x1 | Dormant retained source; do not edit from G2.266 |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | `get_postgres_async` x1 | Needs classification as provider backing vs active route-body residual |
| `web/backend/app/api/_monitoring_portfolio_router.py` | postgres/calculator/optimizer getters | Already passed earlier lanes; reclassify only if current evidence contradicts closeout |
| `web/backend/app/api/monitoring_analysis.py` | postgres/calculator getters | Already passed earlier lanes; reclassify only if current evidence contradicts closeout |
| `web/backend/app/api/monitoring_watchlists.py` | postgres getter | Already passed earlier lanes; reclassify only if current evidence contradicts closeout |
| `web/backend/app/api/v1/pool_monitoring.py` | PostgreSQL/TDengine pool stats accessors | Control-plane candidate; classify separately from service DI source lanes |

## Decision

G2.266 closes the signal statistics stale-contract branch and selects `G2.267 no-source monitoring/signal residual provider classification refresh`.

The next gate must remain no-source. It should classify the monitoring/signal residual set into active provider backing, retained control-plane accessors, dormant false positives, and possible future authorization candidates. It must not directly edit source.

## Verification

- PR `#418`: `MERGED`, merge commit `2b53352d6869f66147ce3892b1b0a7174ba064b4`.
- Targeted tests: `pytest -o addopts= -q --no-cov --tb=short tests/unit/test_signal_monitoring_integration.py::TestSignalMonitoringAPI::test_signal_statistics_endpoint tests/unit/test_signal_monitoring_integration.py::TestSignalMonitoringAPI::test_active_signals_endpoint` => `2 passed`.
- OpenAPI smoke: `routes=548`, `paths=500`, `target_paths=[]`, `duplicate_operation_ids=0`, `warning_count=119`.
- Reference count scan recorded in `.planning/codebase/generated/signal-statistics-dormant-contract-closeout-refresh-2026-05-31.json`.

## Rollback

Revert the future PR carrying this report and steward updates. No runtime code, routes, OpenAPI generation logic, provider binding, database state, frontend state, or OpenSpec state is changed by G2.266.
