# Backend Service Lifecycle Residual Candidate Refresh - 2026-05-31

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- G2 item: `G2.272`
- Branch: `g2-272-service-lifecycle-residual-candidate-refresh`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `8e0fcd6738c4e3a889b4851d058f8121f32b8ce8`
- Source edit authority: none
- Parent PR: `#424`, merged at `8e0fcd6738c4e3a889b4851d058f8121f32b8ce8`

Boundary note: this report refreshes the residual candidate queue only. It does
not authorize backend source edits, route registration changes, provider
injection, source retirement, test edits, docs/api edits, frontend/config/script
edits, OpenSpec mutation, or PM2/stateful commands.

## Scan Summary

G2.272 scanned current HEAD after deferring `pool_monitoring.py` to the
control-plane route/OpenAPI ownership track.

| Metric | Value |
|---|---:|
| Python files scanned | 371 |
| Active route-body candidate calls | 113 |
| Provider/dependency backing calls | 362 |
| API helper/module candidate calls | 70 |
| Known-deferred calls | 12 |
| Service-body candidate calls | 169 |

Scan filters excluded common non-candidate helpers such as `get_logger`,
`get_data`, `get_settings`, and user/auth dependencies. The scan also separated
known-deferred surfaces:

- `web/backend/app/api/v1/pool_monitoring.py`: deferred by G2.271 as
  control-plane route/OpenAPI ownership.
- `web/backend/app/api/signal_monitoring/get_signal_statistics.py`: dormant
  route-shaped source governed by G2.261-G2.266.

## Candidate Queue

| Candidate | Active route-body calls | Files | Current handling |
|---|---:|---|---|
| `get_monitoring_db` | 10 | `risk/alerts.py`, `risk/metrics.py`, `strategy_management/_strategy_crud_router.py` | Select G2.273 no-source ownership / route-provider decision |
| `get_data_source` | 7 | `strategy_management/_strategy_execution_router.py`, `watchlist.py` | Defer until after `get_monitoring_db` ownership decision |
| `get_config_manager` | 6 | `data_source_config.old.py` | Legacy/old route surface; requires stale-source/compatibility decision |
| `get_manager` | 5 | `data_source_registry.py` | Data-source registry ownership candidate; defer |
| `get_stock_data` | 5 | `ml.py` | ML route data access candidate; defer |
| `get_cache_manager` | 4 | `_cache_basic_routes.py`, `cache.py` | Cache/control-plane ownership candidate; defer |

The top service-body clusters remain internal service/facade surfaces, not
route-provider implementation targets:

- `get_session`: 9 calls in monitoring services.
- `get_mock_data_manager`: 6 calls across previously governed compatibility
  adapter surfaces.
- `get_data_quality_monitor`: 5 calls across previously governed data-quality
  surfaces.

## Decision

G2.272 does not authorize source implementation.

Selected next gate:

`G2.273 no-source get_monitoring_db ownership / route-provider decision`

Rationale: `get_monitoring_db` is the most concentrated remaining active
route-body candidate and spans risk plus strategy route surfaces. The symbol is
also ambiguous in GitNexus, so the next step must decide ownership and scope
before any implementation authorization is considered.

## GitNexus Note

GitNexus CLI impact for `get_monitoring_db` returned ambiguous:

- `web/backend/app/api/risk/_shared.py:get_monitoring_db`
- `web/backend/app/utils/risk_utils.py:get_monitoring_db`
- `web/backend/app/api/strategy_management/_helpers.py:get_monitoring_db`

The index reported stale warning with `commits_behind=0` and `has_embeddings=false`.
G2.273 must disambiguate these symbols before any future authorization package
can select implementation scope.

## Verification

- PR `#424`: `MERGED`, merge commit `8e0fcd6738c4e3a889b4851d058f8121f32b8ce8`.
- AST residual scan: `371` API/service Python files scanned.
- Candidate refresh: `get_monitoring_db` selected only for no-source ownership
  decision.
- No source, tests, route contracts, docs/api artifacts, frontend, config,
  scripts, OpenSpec, PM2, or runtime state were changed by G2.272.

## Rollback

Revert the future PR carrying this report and steward updates. No runtime code,
route registration, provider binding, test contract, docs/api artifact,
frontend state, database state, or OpenSpec state is changed by G2.272.
