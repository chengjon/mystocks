# Backend Next High-Risk Service Getter Track Selection After Indicator/Data

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Task: G2.164 next high-risk service getter track selection after Indicator/Data  
Branch: `g2-164-high-risk-service-getter-track-selection-after-indicator-data`  
Base: `wip/root-dirty-20260403`  
Current HEAD: `8b5fb7359a007db704e9f3dfb575d4f5b656075d`  
Created: 2026-05-27

Boundary: this is a decision package only. It does not edit backend source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not authorize implementation.

## Purpose

G2.163 refreshed the high-risk service getter inventory after the Indicator/Data source provider seam closed. This package selects the next high-risk getter track from that refreshed matrix without opening a source implementation lane.

## Parent State

| Input | State |
|---|---|
| PR `#316` | merged into `wip/root-dirty-20260403` |
| Merge commit | `8b5fb7359a007db704e9f3dfb575d4f5b656075d` |
| Parent evidence | `docs/reports/quality/backend-service-lifecycle-candidate-refresh-after-indicator-data-2026-05-27.md` |
| Parent generated artifact | `.planning/codebase/generated/service-lifecycle-candidate-refresh-after-indicator-data-2026-05-27.json` |

G2.163 confirmed that Indicator/Data direct route/helper body calls to `get_data_service()` are closed. Remaining `get_data_service()` hits in the Indicator/Data scope are provider fallbacks in `get_indicator_data_service()` and `get_strategy_indicator_data_service()`.

## Refreshed Track Evidence

| Track | Primary getter | Risk | Impact | Current disposition |
|---|---|---:|---|---|
| Indicator/Data residual | `get_data_service` | CRITICAL | impacted `5`, direct `3`, processes `7` | Recently closed as a direct body-call debt; retain as provider-governed runtime seam, not the next source lane. |
| Strategy adapter / strategy-management | `get_strategy_service` | CRITICAL | impacted `13`, direct `6`, processes `0` | Select as next design/authorization track. |
| Realtime streaming/socket | `get_streaming_service` | HIGH | impacted `9`, direct `9`, processes `0` | Keep in the realtime/socket track; do not mix with strategy adapter work. |
| Dashboard/TDX residual | `get_tdx_service` | CRITICAL | impacted `6`, direct `2`, processes `5` | Keep as a residual Dashboard/TDX decision packet; prior Dashboard/TDX lane closed direct helper debt. |

## Current Token Surface

Scope: `web/backend/app/api`, `web/backend/app/services`, `web/backend/app/core`, and `web/backend/tests` at HEAD `8b5fb7359a007db704e9f3dfb575d4f5b656075d`.

| Getter | Token count | Files |
|---|---:|---:|
| `get_data_service` | `9` | `4` |
| `get_strategy_service` | `10` | `5` |
| `get_streaming_service` | `25` | `6` |
| `get_tdx_service` | `6` | `4` |
| `get_market_data_service` | `19` | `8` |
| `get_market_data_service_v2_dependency` | `18` | `4` |
| `get_indicator_data_service` | `4` | `2` |
| `get_strategy_indicator_data_service` | `3` | `2` |
| `get_indicator_registry_dependency` | `5` | `3` |

## Strategy Track Detail

GitNexus reports `get_strategy_service` as CRITICAL with `13` impacted symbols, `6` direct callers, and `5` affected modules.

Direct caller set:

| Direct caller | File | Track implication |
|---|---|---|
| `_get_strategy_service` | `web/backend/app/services/data_adapters/strategy.py` | Adapter/provider duplication surface. |
| `_get_strategy_service` | `web/backend/app/services/adapters/strategy_adapter.py` | Adapter/provider duplication surface. |
| `query_strategy_results` | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | Route dependency/provider governance surface. |
| `get_matched_stocks` | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | Route dependency/provider governance surface. |
| `get_strategy_summary` | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | Route dependency/provider governance surface. |
| `_resolve_backtest_data_source` | `web/backend/app/tasks/backtest_tasks.py` | Task/backtest resolution surface. |

The strategy track should not be treated as a single mechanical getter replacement. It crosses three different decision surfaces:

1. adapter/provider duplication in two strategy adapter modules;
2. FastAPI route dependency/provider design for strategy-management endpoints;
3. task/backtest data-source resolution behavior.

## Decision

Select the Strategy adapter / strategy-management seam as the next high-risk service getter track.

The next gate is G2.165: Strategy service seam design and authorization package.

G2.165 must remain a design/authorization gate unless explicitly approved otherwise. It should decide the split between adapter, route, and task/backtest surfaces, define the exact implementation scope, and identify TDD tests before any source implementation starts.

## Deferred Tracks

| Track | Deferred reason | Future gate |
|---|---|---|
| Indicator/Data residual | G2.162 closed direct body-call debt; remaining graph risk is expected provider runtime flow. | Revisit only if a current-head contradiction appears. |
| Realtime streaming/socket | Socket manager and realtime lifecycle require a separate runtime/socket plan. | Dedicated realtime/socket decision or authorization package. |
| Dashboard/TDX residual | Prior Dashboard/TDX lane closed direct helper debt; residual graph risk is not the same as a new source lane. | Dedicated Dashboard/TDX residual decision packet. |
| Root facade compatibility | Active compatibility surface, not a cleanup candidate. | Separate compatibility-retirement decision only. |
| Route dependency/provider governance | Cross-cutting FastAPI provider contract surface. | Govern through track-specific provider decisions. |

## G2.165 Minimum Requirements

G2.165 should produce a design/authorization package before any strategy source implementation lane begins.

Minimum required content:

1. refreshed GitNexus impact for `get_strategy_service`;
2. static scan of `get_strategy_service()` call sites, separated into import/definition/provider/body-call categories;
3. direct caller matrix for the two adapter modules, the three strategy-management route handlers, and `_resolve_backtest_data_source`;
4. decision on whether the first implementation slice should target route provider injection, adapter provider consolidation, or task/backtest resolution;
5. exact allowed source/test file list for the future implementation lane;
6. focused TDD plan, including at least `test_strategy_mgmt_backtest_regressions.py`, `test_backtest_tasks_regressions.py`, and relevant strategy-management route tests if they are in scope;
7. rollback plan that preserves `get_strategy_service()` public fallback compatibility unless a later compatibility-retirement decision explicitly allows changing it;
8. OpenAPI/route smoke requirement if strategy-management route handlers are edited;
9. explicit non-goals for realtime/socket, Dashboard/TDX, Indicator/Data, frontend, PM2, OpenSpec state, and issue-label state.

## Explicit Boundaries

This package does not authorize:

- editing `web/backend/app/services/strategy_service.py`;
- deleting, privatizing, renaming, or changing `get_strategy_service()`;
- editing strategy adapter, strategy-management route, or backtest task source files;
- editing backend tests;
- changing route paths, response models, OpenAPI exposure, frontend callers, PM2 workflows, config, scripts, OpenSpec state, or GitHub issue labels;
- folding realtime/socket, Dashboard/TDX, or Indicator/Data residual work into the strategy lane.

## Verification

| Check | Result |
|---|---|
| Parent PR state | PR `#316` merged; merge commit `8b5fb7359a007db704e9f3dfb575d4f5b656075d` |
| Current HEAD | `8b5fb7359a007db704e9f3dfb575d4f5b656075d` |
| GitNexus impact: `get_data_service` | CRITICAL, impacted `5`, direct `3`, processes `7` |
| GitNexus impact: `get_strategy_service` | CRITICAL, impacted `13`, direct `6`, processes `0` |
| GitNexus impact: `get_streaming_service` | HIGH, impacted `9`, direct `9`, processes `0` |
| GitNexus impact: `get_tdx_service` | CRITICAL, impacted `6`, direct `2`, processes `5` |
| Static token scan | completed at current HEAD; values recorded above and in generated JSON |

## Next Gate

Review this G2.164 decision package. If accepted and merged, start G2.165 as a Strategy service seam design and authorization package. Do not start a strategy source implementation lane directly from G2.164.
