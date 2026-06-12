# Backend Service Lifecycle DI Technical Analysis Authorization

Date: 2026-06-13
Task: G2.331
Mode: no-source authorization preflight
Base worktree: `g2-331-technical-analysis-datasourcefactory-authorization`
Base commit: `02eb277bb1fd9c9e75a82e8029d3b5e384a096fe`

## Status

G2.331 is a no-source authorization preflight for the backend service
lifecycle DI lane. It selects the next MyStocks-side candidate family and
records the implementation boundary for a later source-authorized task.

This package does not modify or authorize in-place changes to source, tests,
API contracts, frontend code, runtime state, scripts, configuration, OpenSpec
implementation files, or OpenStock internals.

## Parent Evidence

G2.330 recorded the current branch split after PR `#478`:

| Candidate family | `origin/main` status | `origin/wip/root-dirty-20260403` / PR `#474` status | G2.331 disposition |
| --- | --- | --- | --- |
| Strategy routes | `web/backend/app/api/strategy.py` has 3 strict route-body `DataSourceFactory()` residuals | `strategy.py` is absent; `strategy_management/_strategy_execution_router.py` has the corresponding 3 residuals | Defer until the target base branch is explicitly selected |
| Technical analysis routes | `web/backend/app/api/technical_analysis.py` has 8 strict route-body residuals | Same file has the same 8 strict residuals | Select as the next candidate family |
| Watchlist routes | `web/backend/app/api/watchlist.py` has 8 strict route-body residuals | PR `#474` / wip anchor already moved watchlist to provider dependency shape | Defer mainline reconciliation; do not treat as a wip residual |
| Dashboard summary | One body-level `get_data_source()` call without a `DataSourceFactory()` constructor | Not selected by the strict rule | Observation only |

The selected candidate is `web/backend/app/api/technical_analysis.py` because it
is stable across `origin/main`, `origin/wip/root-dirty-20260403`, and the PR
`#474` anchor. This avoids the strategy filename split and the watchlist
branch-anchor conflict.

## Current Technical Analysis Residuals

The current `origin/main` route-body scan finds 8 strict residual route
functions in `web/backend/app/api/technical_analysis.py`.

| Function | Line | Route | `DataSourceFactory()` calls | Body `get_data_source()` calls |
| --- | ---: | --- | ---: | ---: |
| `get_all_indicators` | 235 | `GET /{symbol}/indicators` | 1 | 1 |
| `get_trend_indicators` | 340 | `GET /{symbol}/trend` | 1 | 1 |
| `get_momentum_indicators` | 411 | `GET /{symbol}/momentum` | 1 | 1 |
| `get_volatility_indicators` | 462 | `GET /{symbol}/volatility` | 1 | 1 |
| `get_volume_indicators` | 512 | `GET /{symbol}/volume` | 1 | 1 |
| `get_trading_signals` | 562 | `GET /{symbol}/signals` | 1 | 1 |
| `get_stock_history` | 616 | `GET /{symbol}/history` | 1 | 1 |
| `get_batch_indicators` | 663 | `POST /batch/indicators` | 1 | 1 |

Total residuals: 8 route functions, 8 `DataSourceFactory()` calls, and 8
body-level `get_data_source()` calls.

## API Impact Snapshot

GitNexus `api_impact` was run against
`web/backend/app/api/technical_analysis.py`.

| Route | Direct consumers | Affected flows | Risk |
| --- | ---: | ---: | --- |
| `/{symbol}/indicators` | 0 | 0 | LOW |
| `/{symbol}/trend` | 0 | 0 | LOW |
| `/{symbol}/momentum` | 0 | 0 | LOW |
| `/{symbol}/volatility` | 0 | 0 | LOW |
| `/{symbol}/volume` | 0 | 0 | LOW |
| `/{symbol}/signals` | 0 | 0 | LOW |
| `/{symbol}/history` | 0 | 0 | LOW |
| `/batch/indicators` | 0 | 0 | LOW |

Index note: GitNexus reported a stale-index warning because the indexed commit
differs from the current commit, but the API impact result still provides a
useful preflight snapshot. Any future source-authorized implementation must
rerun GitNexus impact/API-impact from its own branch before editing route
handlers.

## Proposed Implementation Boundary

The later source-authorized task should keep the change narrow:

| Scope | Proposed path |
| --- | --- |
| Primary source file | `web/backend/app/api/technical_analysis.py` |
| Route/API regression tests | Existing technical-analysis API or route tests only, selected after inspection in the implementation branch |
| Contract/E2E smoke, if required by the implementation branch | Existing `/api/technical/*` coverage only |

The expected implementation pattern is the accepted PR `#474` watchlist provider
shape:

1. Move `DataSourceFactory()` construction out of individual route bodies into
   a small provider helper such as `get_technical_analysis_data_source()`.
2. Inject the adapter into the 8 route handlers with `Depends(...)`.
3. Preserve the current route paths, response models, validation behavior,
   circuit-breaker behavior, exception mapping, and adapter `get_data(...)`
   calls.
4. Add or adjust focused tests only for the provider-injection behavior and the
   affected technical-analysis route contract.

## Non-Goals

The follow-up implementation must not:

| Non-goal | Reason |
| --- | --- |
| Modify OpenStock internals | OpenStock work is owned separately and was reported complete by its own handoff |
| Rewrite the technical-analysis adapter or calculation logic | G2.331 only targets route-body `DataSourceFactory()` lifecycle residuals |
| Change response schemas or OpenAPI contracts | The task is DI lifecycle cleanup, not API redesign |
| Touch watchlist or strategy residuals | Those families have branch-split decisions and need separate authorization |
| Broaden to dashboard `get_data_source()` observation | It does not match the strict `DataSourceFactory()` residual rule |
| Delete or retire files | Deletion/retirement requires separate authorization under repository standards |

## Authorization Decision

G2.331 authorizes only the next planning direction:

| Decision | Result |
| --- | --- |
| Next candidate family | `technical_analysis.py` service lifecycle DI residuals |
| Target base | `origin/main` |
| Source implementation status | Not implemented by this task |
| Required next node | Separate source-authorized task card before any code/test edits |
| OpenStock status | Boundary-only; no OpenStock development or modification |

## Required Next Gate

Before editing source in the next node, the implementation branch must:

1. Create a source-authorized task card with explicit allowed source and test
   paths.
2. Rerun GitNexus impact/API-impact for
   `web/backend/app/api/technical_analysis.py` and report the risk level.
3. Inspect existing technical-analysis tests and choose focused regression
   coverage before writing implementation code.
4. Run the mainline scope gate, path whitelist, `git diff --check`, GitNexus
   detect changes, and project-native focused tests.
5. Keep OpenStock internals out of scope.

## Verification Scope

This package is expected to modify only:

| Path | Purpose |
| --- | --- |
| `docs/reports/quality/backend-service-lifecycle-di-technical-analysis-authorization-2026-06-13.md` | G2.331 no-source authorization preflight evidence |
| `governance/mainline/task-cards/g2-331.yaml` | G2.331 mainline task card and no-source gate definition |
