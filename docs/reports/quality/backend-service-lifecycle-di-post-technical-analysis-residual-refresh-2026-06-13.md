# Backend Service Lifecycle DI Post-Technical-Analysis Residual Refresh

Date: 2026-06-13
Task: G2.335
Mode: no-source governance refresh
Base worktree: `g2-335-service-lifecycle-di-residual-refresh`
Base commit: `74b548cf89bbb060ea17882cf6f750217e42c673`

## Status

G2.335 refreshes the service lifecycle DI residual pool after PR #480 landed the
technical-analysis provider injection on `main`.

This report is evidence only. It does not authorize source, test, API contract,
frontend, runtime, script, configuration, OpenSpec implementation, deletion, or
OpenStock internal changes.

## Screening Method

The scan used Python AST parsing over `web/backend/app/api/**/*.py` at
`origin/main` commit `74b548cf8`.

A route function was counted when it had a FastAPI route decorator such as
`get`, `post`, `put`, `delete`, `patch`, `options`, `head`, or `api_route`.

Strict residual candidates are route function bodies containing both:

- a `DataSourceFactory()` constructor call
- a body-level `get_data_source(...)` call

Provider/helper functions outside route bodies are not counted as route-body
residuals. Body-level `get_data_source(...)` calls without a
`DataSourceFactory()` constructor remain observation items only.

## Current Mainline Residual Pool

After PR #480, `technical_analysis.py` has no strict route-body
`DataSourceFactory` residuals.

Current strict residual pool:

| File | Residual route functions | Data source key | Functions |
| --- | ---: | --- | --- |
| `web/backend/app/api/watchlist.py` | 8 | `watchlist` | `get_my_watchlist`, `get_my_watchlist_symbols`, `add_to_watchlist`, `remove_from_watchlist`, `check_in_watchlist`, `update_watchlist_notes`, `get_watchlist_count`, `clear_watchlist` |
| `web/backend/app/api/strategy.py` | 3 | `strategy` | `get_strategy_definitions`, `run_strategy_single`, `run_strategy_batch` |

Total strict residual count: 11 route functions across 2 files.

## Closed Candidate

`web/backend/app/api/technical_analysis.py` is closed for this screening rule.

The file still contains `DataSourceFactory` text because PR #480 centralized the
factory construction in `get_technical_analysis_data_source()`, which is a
provider function rather than a route body. No route handler in
`technical_analysis.py` constructs `DataSourceFactory()` after PR #480.

## Observation Item

`web/backend/app/api/dashboard.py` still has a route-body `get_data_source(...)`
usage without an in-body `DataSourceFactory()` constructor. This remains outside
the strict residual definition and should not be used as source authorization
evidence unless a future task broadens the lane from constructor residuals to
general provider-boundary normalization.

## Branch Split Notes

The G2.330 branch split remains relevant:

| Candidate family | Current `origin/main` status | Wip / PR anchor implication | G2.335 decision |
| --- | --- | --- | --- |
| Technical analysis | Closed by PR #480 | Previously cross-ref stable residual | Remove from residual pool; no follow-up source task needed for this rule |
| Watchlist | 8 strict residual route handlers on current `main` | PR #474 accepted a watchlist provider anchor on the wip/root lane | Do not replay source work blindly; reconcile the accepted watchlist branch if selecting this family |
| Strategy | 3 strict residual route handlers in `web/backend/app/api/strategy.py` | Wip/root uses `strategy_management/_strategy_execution_router.py` for the corresponding strategy family | Suitable narrow mainline candidate if the next task explicitly targets `origin/main` |
| Dashboard summary | One body-level `get_data_source(...)` usage without constructor | Not selected by strict rule | Observation only |

## Recommended Next Gate

No source implementation is selected or authorized by G2.335.

Recommended next source-authorization candidates:

1. `strategy.py` mainline provider authorization: smallest current-main strict
   residual family, 3 route handlers, no watchlist branch-anchor duplication.
2. `watchlist.py` reconciliation authorization: larger current-main residual
   family, 8 route handlers, but must reconcile the accepted PR #474 / wip-root
   provider work before any mainline implementation decision.

Any follow-up implementation must be a separate source-authorized task card with
GitNexus impact analysis, route/API impact review, scoped source/test gates, and
explicit base-branch selection.

## OpenStock Boundary

OpenStock internals remain out of scope. This MyStocks package records only the
local residual evidence and branch-boundary implications. It does not modify
OpenStock provider/runtime code, tests, configuration, packaging, or repository
files.

## Verification Scope

This package is expected to modify only:

| Path | Purpose |
| --- | --- |
| `docs/reports/quality/backend-service-lifecycle-di-post-technical-analysis-residual-refresh-2026-06-13.md` | G2.335 no-source residual refresh evidence |
| `governance/mainline/task-cards/g2-335.yaml` | Mainline task card and no-source gate definition |

Expected verification:

| Check | Expected result |
| --- | --- |
| No-source path check | No changes under `src/**`, `web/backend/app/**`, `web/frontend/**`, `tests/**`, `scripts/**`, `config/**`, `openspec/changes/**`, or OpenStock internals |
| Residual refresh assertion | Strict residual pool is `watchlist.py` 8, `strategy.py` 3, `technical_analysis.py` 0 |
| Mainline scope gate | G2.335 task card validates the exact changed file set |
| Git diff check | No whitespace errors |
| GitNexus detect changes | Governance-only change; no indexed source symbols affected |
