# Backend Service Lifecycle DI Global Residual Screening

Date: 2026-06-13
Task: G2.330
Mode: no-source governance screening
Base worktree: `g2-330-service-lifecycle-di-residual-screening`
Base commit: `bb15314e2553859c218065117a418927c701f76b`

## Status

G2.330 is a no-source global residual screening node for the backend service
lifecycle DI lane. It records current candidate evidence and base-branch split
decisions only.

This report does not authorize source, test, API contract, frontend, runtime,
script, configuration, OpenSpec implementation, or OpenStock internal changes.

## Screening Method

The scan used Python AST parsing over `web/backend/app/api/**/*.py` for each
reference. A route function was counted when it had a FastAPI route decorator
such as `get`, `post`, `put`, `delete`, `patch`, `options`, `head`,
`websocket`, or `api_route`.

Strict residual candidates are route function bodies containing
`DataSourceFactory()` and a body-level `get_data_source()` call. Dependency
defaults such as `Depends(get_data_source)` are tracked as context, but are not
treated as route-body residuals by themselves.

References screened:

| Reference | Commit | Purpose |
| --- | --- | --- |
| `origin/main` | `bb15314e2553` | Current mainline truth after PR `#477` |
| `origin/wip/root-dirty-20260403` | `e1dbb6d962af` | Active wip/root branch truth |
| PR `#474` merge | `2ebff6d7ded3` | Accepted watchlist provider anchor |

## Current Mainline Residual Pool

`origin/main` contains three strict `DataSourceFactory` route-body residual
files, totaling 19 route functions.

| File | Residual route functions | `DataSourceFactory()` calls | Body `get_data_source()` calls | Functions |
| --- | ---: | ---: | ---: | --- |
| `web/backend/app/api/strategy.py` | 3 | 3 | 3 | `get_strategy_definitions`, `run_strategy_single`, `run_strategy_batch` |
| `web/backend/app/api/technical_analysis.py` | 8 | 8 | 8 | `get_all_indicators`, `get_trend_indicators`, `get_momentum_indicators`, `get_volatility_indicators`, `get_volume_indicators`, `get_trading_signals`, `get_stock_history`, `get_batch_indicators` |
| `web/backend/app/api/watchlist.py` | 8 | 8 | 8 | `get_my_watchlist`, `get_my_watchlist_symbols`, `add_to_watchlist`, `remove_from_watchlist`, `check_in_watchlist`, `update_watchlist_notes`, `get_watchlist_count`, `clear_watchlist` |

The historical G2.329 seed file
`web/backend/app/api/strategy_management/_strategy_execution_router.py` is not
present on `origin/main`, so it is not a current mainline implementation
candidate.

## Mainline Observation Item

`web/backend/app/api/dashboard.py` contains one route body with a
`get_data_source()` call and no `DataSourceFactory()` constructor call:
`get_dashboard_summary`.

This is not a strict `DataSourceFactory` residual candidate for this lane. It
should remain an observation item unless a later authorization broadens the
screening rule from constructor residuals to service-provider boundary
normalization.

## Wip And PR Anchor Residual Pool

`origin/wip/root-dirty-20260403` and PR `#474` have the same strict residual
pool shape for this screening rule: two files and 11 route functions.

| Reference | File | Residual route functions | `DataSourceFactory()` calls | Body `get_data_source()` calls | Functions |
| --- | --- | ---: | ---: | ---: | --- |
| `origin/wip/root-dirty-20260403` | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 3 | 3 | 3 | `get_strategy_definitions`, `run_strategy_single`, `run_strategy_batch` |
| `origin/wip/root-dirty-20260403` | `web/backend/app/api/technical_analysis.py` | 8 | 8 | 8 | `get_all_indicators`, `get_trend_indicators`, `get_momentum_indicators`, `get_volatility_indicators`, `get_volume_indicators`, `get_trading_signals`, `get_stock_history`, `get_batch_indicators` |
| PR `#474` merge | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 3 | 3 | 3 | `get_strategy_definitions`, `run_strategy_single`, `run_strategy_batch` |
| PR `#474` merge | `web/backend/app/api/technical_analysis.py` | 8 | 8 | 8 | `get_all_indicators`, `get_trend_indicators`, `get_momentum_indicators`, `get_volatility_indicators`, `get_volume_indicators`, `get_trading_signals`, `get_stock_history`, `get_batch_indicators` |

Watchlist remains excluded from the wip/PR `#474` interpretation because the
accepted anchor has moved the watchlist route surface into provider dependency
shape for this lane. That exclusion does not erase the current `origin/main`
watchlist residual evidence; it only prevents reusing the wip anchor as a
mainline authorization shortcut.

## Branch Split Decision

G2.330 records a base-branch split:

| Candidate family | `origin/main` status | `origin/wip/root-dirty-20260403` / PR `#474` status | Decision |
| --- | --- | --- | --- |
| Strategy routes | `web/backend/app/api/strategy.py` exists and has 3 strict residual route functions | `strategy.py` is absent; `_strategy_execution_router.py` has the corresponding 3 strict residual route functions | Any implementation task must choose the target base before authorizing source edits |
| Technical analysis routes | Present as 8 strict residual route functions on both references | Present as 8 strict residual route functions on both references | Stable cross-ref residual family; suitable next no-source authorization candidate if scope is kept narrow |
| Watchlist routes | Present as 8 strict residual route functions on `origin/main` | Excluded by PR `#474` accepted provider anchor | Do not treat watchlist as a wip residual; if targeting `origin/main`, reconcile or merge the accepted provider branch first |
| Dashboard summary | One body-level `get_data_source()` call without `DataSourceFactory()` | Not selected by this screening rule | Observation only |

## OpenStock Boundary

OpenStock internals are out of scope for this task. The reported OpenStock
handoff is treated as completed external evidence, and this MyStocks package
only records local boundary implications: no OpenStock provider/runtime code,
tests, configuration, or repository files are selected or modified.

## Next Gate

No source implementation is selected or authorized by G2.330.

Before any source-authorized follow-up, the maintainer must pick the target base:

1. `origin/main` lane: reconcile the PR `#474` watchlist provider work or plan a
   mainline-specific provider injection slice.
2. `origin/wip/root-dirty-20260403` lane: treat
   `strategy_management/_strategy_execution_router.py` and
   `technical_analysis.py` as the strict residual pool.
3. Cross-ref stable lane: consider `technical_analysis.py` first because it is
   present and residual across all screened references.

Any follow-up implementation must be a separate `source-authorized` task card
with GitNexus impact analysis, source/test gates, and explicit path scope.

## Verification Scope

This package is expected to modify only:

| Path | Purpose |
| --- | --- |
| `docs/reports/quality/backend-service-lifecycle-di-global-residual-screening-2026-06-13.md` | G2.330 no-source residual evidence and branch split decision |
| `governance/mainline/task-cards/g2-330.yaml` | Mainline task card and no-source gate definition |

Expected verification:

| Check | Expected result |
| --- | --- |
| No-source path check | No changes under `src/**`, `web/backend/app/**`, `web/frontend/**`, `tests/**`, `scripts/**`, `config/**`, `openspec/changes/**`, or OpenStock internals |
| Mainline scope gate | G2.330 task card validates the exact changed file set |
| Git diff check | No whitespace errors |
| GitNexus staged detect changes | Governance-only change; no indexed source symbols affected |
