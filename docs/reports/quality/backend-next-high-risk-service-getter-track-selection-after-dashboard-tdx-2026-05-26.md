# Backend Next High-Risk Service Getter Track Selection After Dashboard/TDX

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-26

Status: Ready for review

Scope: G2.158 governance decision only.

Base HEAD: `97442014ea3ea3e63ffa170cd00b54889c158924`

Parent: G2.157, PR `#310`, merged as `97442014ea3ea3e63ffa170cd00b54889c158924`.

Boundary: this is a decision package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not authorize implementation.

## Decision

Select the Indicator/Data service seam as the next high-risk getter design track.

The next gate is G2.159: Indicator/Data design and authorization package.

G2.158 does not authorize source implementation.

## Current Queue State

Dashboard/TDX is closed by G2.157 without source implementation because current-head direct dashboard helper getter debt is `0`.

Realtime/socket is also closed for now by the earlier G2.154 closeout. Do not reopen it from this package without a new current-head contradiction.

Remaining queue:

| Track | Status |
|---|---|
| Indicator/Data | Selected for next design package |
| Strategy adapter | Deferred; broader cross-module impact |
| root facade compatibility | Locked governance surface |
| route dependency/provider governance | Locked route contract surface |

## Refreshed Impact

| Getter | Risk | Impacted | Direct callers | Processes | Disposition |
|---|---:|---:|---:|---:|---|
| `get_data_service` | CRITICAL | 5 | 3 | 7 | Select for G2.159 design package |
| `get_strategy_service` | CRITICAL | 13 | 6 | 0 | Defer to dedicated Strategy adapter package |
| `get_streaming_service` | HIGH | 9 | 9 | 0 | Already closed by realtime/socket closeout |

`get_data_service` direct callers:

- `web/backend/app/api/indicators/indicator_cache.py::calculate_indicators`
- `web/backend/app/api/indicators/indicator_cache.py::_calculate_single_indicator`
- `web/backend/app/api/v1/strategy/indicators.py::get_technical_indicators`

`get_strategy_service` direct callers:

- `web/backend/app/services/data_adapters/strategy.py::_get_strategy_service`
- `web/backend/app/services/adapters/strategy_adapter.py::_get_strategy_service`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py::query_strategy_results`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py::get_matched_stocks`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py::get_strategy_summary`
- `web/backend/app/tasks/backtest_tasks.py::_resolve_backtest_data_source`

## Token Surface

`get_data_service` current token scan:

| File | Count |
|---|---:|
| `web/backend/app/services/data_service.py` | 1 |
| `web/backend/app/api/v1/strategy/indicators.py` | 2 |
| `web/backend/app/api/indicators/indicator_cache.py` | 3 |
| `web/backend/tests/test_v1_indicators_regressions.py` | 2 |
| `web/backend/tests/test_integration_e2e.py` | 4 |

Current source hit lines:

| File | Line | Text |
|---|---:|---|
| `web/backend/app/api/indicators/indicator_cache.py` | 40 | import `get_data_service` |
| `web/backend/app/api/indicators/indicator_cache.py` | 343 | `data_service = get_data_service()` |
| `web/backend/app/api/indicators/indicator_cache.py` | 613 | `data_service = get_data_service()` |
| `web/backend/app/api/v1/strategy/indicators.py` | 17 | import `get_data_service` |
| `web/backend/app/api/v1/strategy/indicators.py` | 201 | `get_data_service().get_daily_ohlcv(...)` |

`get_strategy_service` current token scan:

| File | Count |
|---|---:|
| `web/backend/app/tasks/backtest_tasks.py` | 2 |
| `web/backend/app/services/adapters/strategy_adapter.py` | 2 |
| `web/backend/app/services/strategy_service.py` | 1 |
| `web/backend/app/services/data_adapters/strategy.py` | 2 |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 4 |
| `web/backend/tests/test_backtest_tasks_regressions.py` | 1 |

## Selection Rationale

Indicator/Data is the next most contained CRITICAL seam after Dashboard/TDX:

- direct caller count is `3`, compared with Strategy adapter `6`;
- impacted count is `5`, compared with Strategy adapter `13`;
- affected modules are Indicators and Strategy, compared with Strategy adapter crossing adapters, data adapters, strategy-management routes, and backtest tasks;
- the surface has clear focused test candidates: indicator cache, v1 strategy indicator regressions, and integration E2E references.

This does not make Indicator/Data safe for direct source implementation. It has process participation and public API consumers, so it needs a dedicated design and authorization package before any edit.

## G2.159 Minimum Requirements

G2.159 must be a design and authorization package before implementation.

It must include:

- refreshed GitNexus impact for `get_data_service` and its three direct callers;
- Indicator/Data consumer contract matrix for `calculate_indicators`, `_calculate_single_indicator`, `get_technical_indicators`, `calculate_single_request`, and `limited_calculate`;
- current-head hit classification for each `get_data_service` textual hit;
- strategy indicator consumer parity requirements;
- focused test plan for indicator cache and v1 strategy indicator behavior;
- OpenAPI example/drift rule if response contracts are touched;
- explicit allowed source/test paths and stop conditions.

## Explicit Boundaries

Do not implement source changes from G2.158.

Do not:

- delete or privatize `get_data_service`;
- edit Strategy adapter files;
- retire root facade compatibility getters;
- treat FastAPI dependency/provider getters as singleton cleanup;
- change route paths, response contracts, or OpenAPI exposure;
- change frontend, PM2, OpenSpec, config, scripts, issue labels, or GitHub issue state.

## Next Gate

Review this package. If accepted, start G2.159 as an Indicator/Data design and authorization package. G2.159 should still be source-closed until it defines exact paths, tests, rollback, impact evidence, and stop conditions.
