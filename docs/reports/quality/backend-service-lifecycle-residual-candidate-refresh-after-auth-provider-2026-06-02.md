# Backend Service Lifecycle Residual Candidate Refresh After Auth Provider

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: this report is a no-source candidate refresh package. It does
not edit backend source, tests, route contracts, docs/api artifacts, frontend,
config, scripts, OpenSpec changes/specs, PM2, or runtime state.

Status: for review in future PR `#462`.

## Summary

G2.309 starts after PR `#461` merged the G2.308 auth provider closeout at
`03ec65d765a72f131609e28d5121ec498dd6b54e`.

This package refreshes the service lifecycle getter/provider residual queue
after the auth PostgreSQL session provider lane closed. It does not authorize
implementation. It selects only one next no-source decision target: G2.310
`get_mysql_session` ownership / route-provider decision.

## Scanner Scope

| Item | Value |
|---|---:|
| Base HEAD | `03ec65d765a72f131609e28d5121ec498dd6b54e` |
| Roots scanned | `web/backend/app/api`, `web/backend/app/services` |
| Python files scanned | `371` |
| Getter-like names seen | `663` |
| Active interesting candidates after G2 exclusions | `54` |

The scan filtered for getter-like names that match singleton/provider naming
tokens such as manager, service, db, session, engine, client, adapter, core,
factory, monitor, registry, cache, provider, connection, module, and circuit.
Closed G2 provider seams were excluded so already accepted lanes do not reopen.

## Top Candidate Refresh

| Candidate | Bare API calls | Files | Handling |
|---|---:|---|---|
| `get_config_manager` | `9` | `data_source_config.py`, `data_source_config.old.py`, `_data_source_config_responses.py` | Defer; legacy/compat data-source-config surface and prior `get_config_manager_dependency` lane is closed |
| `get_cache_data` | `7` | `data/kline.py`, `data/market.py`, `data/stocks.py` | Defer; data/cache helper family needs data route ownership decision |
| `get_cache_manager` | `7` | `_cache_basic_routes.py`, `cache.py`, `dashboard.py` | Defer; dashboard/cache cross-route helper |
| `get_postgresql_engine` | `6` | `industry_concept_analysis.py`, `v1/pool_monitoring.py` | Defer; control-plane / DB engine helper |
| `get_risk_management_core` | `6` | `risk/v31.py`, `risk/stop_loss.py`, `risk/_alerts_responses.py` | Defer; risk core helper, do not combine with closed stop-loss lane |
| `get_mtm_engine` | `5` | `realtime_market.py`, `realtime_mtm_adapter.py` | Defer; realtime MTM / streaming-adjacent high-risk surface |
| `get_mysql_session` | `5` | `indicators/create_indicator_config.py` | Select for G2.310 no-source ownership / route-provider decision |
| `get_circuit_breaker` | `4` | `technical_analysis.py`, `stock_search_result.py`, `market_data_request.py` | Defer; cross-route resilience helper |
| `get_algorithms_module` | `3` | `algorithms/__init__.py`, `algorithms/get_algorithms_module.py` | Defer; algorithms package ownership decision |
| `get_factory` | `3` | `indicator_registry.py` | Defer; indicator registry factory decision |
| `get_kronos_client` | `3` | `v1/analysis/kronos.py`, `services/external/kronos_client.py` | Viable later bounded external-client decision |
| `get_target_database` | `3` | `v1/system/health.py`, `v1/system/routing.py` | Defer; system routing/control-plane helper |

## Selected Next Gate

G2.310 should be a no-source ownership / route-provider decision for
`get_mysql_session` in `web/backend/app/api/indicators/create_indicator_config.py`.

Selection rationale:

- The helper is concentrated in one API module.
- The scan found five bare route-body calls:
  - line `60`: `session = get_mysql_session()`
  - line `129`: `session = get_mysql_session()`
  - line `189`: `session = get_mysql_session()`
  - line `251`: `session = get_mysql_session()`
  - line `331`: `session = get_mysql_session()`
- It has lower ambiguity than dashboard/cache, risk core, realtime MTM,
  `get_postgresql_engine`, and data-source-config legacy surfaces.

G2.310 must still be decision-only. It must not edit source, tests, route
contracts, OpenAPI artifacts, MySQL helper behavior, or runtime state.

## Boundary

This report must not be treated as authorization to implement the
`get_mysql_session` provider. A future implementation lane, if any, requires a
separate authorization package and human review before source/test PR merge.

## Evidence

| Evidence | Result |
|---|---|
| Parent PR | PR `#461` is `MERGED` at `03ec65d765a72f131609e28d5121ec498dd6b54e` |
| Generated JSON | `.planning/codebase/generated/service-lifecycle-residual-candidate-refresh-after-auth-provider-2026-06-02.json` |
| Route/OpenAPI artifacts | Not edited |
| PM2/runtime state | Not touched |
| Source/test files | Not edited |

## Decision

Accept G2.309 as a no-source residual candidate refresh. The next allowed step
is G2.310 no-source `get_mysql_session` ownership / route-provider decision.
