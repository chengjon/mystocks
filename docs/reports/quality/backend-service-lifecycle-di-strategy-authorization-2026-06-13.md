# Backend Service Lifecycle DI Strategy Authorization

Date: 2026-06-13
Task: G2.336
Mode: no-source authorization preflight
Base worktree: `g2-336-strategy-datasourcefactory-provider-authorization`
Base commit: `1cca050be6e2704af84890812a759765c9445557`

## Status

G2.336 is a no-source authorization preflight for the backend service lifecycle
DI lane. It selects the next MyStocks-side candidate family after G2.335
refreshed the residual pool, and records the implementation boundary for a
later source-authorized task.

This package does not modify or authorize in-place changes to source, tests,
API contracts, frontend code, runtime state, scripts, configuration, dependency
manifests, OpenSpec implementation files, deletion paths, or OpenStock internals.

## Parent Evidence

G2.335 refreshed the current `origin/main` residual pool after PR #480 landed
the technical-analysis provider injection:

| Candidate family | Current `origin/main` status | G2.336 disposition |
| --- | --- | --- |
| Technical analysis routes | `technical_analysis.py` has 0 strict route-body `DataSourceFactory()` residuals | Closed for this strict residual rule |
| Strategy routes | `strategy.py` has 3 strict route-body `DataSourceFactory()` residuals | Select as the next narrow mainline candidate |
| Watchlist routes | `watchlist.py` has 8 strict route-body `DataSourceFactory()` residuals | Defer; must reconcile PR #474 / wip-root accepted provider anchor before mainline source work |
| Dashboard summary | One body-level `get_data_source(...)` call without `DataSourceFactory()` | Observation only |

The selected candidate is `web/backend/app/api/strategy.py` because it is the
smallest current-main strict residual family and avoids the watchlist branch
anchor conflict.

## Current Strategy Residuals

The current `origin/main` route-body scan finds 3 strict residual route
functions in `web/backend/app/api/strategy.py`.

| Function | Line | Route | Data source key | `DataSourceFactory()` calls | Body `get_data_source()` calls |
| --- | ---: | --- | --- | ---: | ---: |
| `get_strategy_definitions` | 182 | `GET /definitions` | `strategy` | 1 | 1 |
| `run_strategy_single` | 219 | `POST /run/single` | `strategy` | 1 | 1 |
| `run_strategy_batch` | 273 | `POST /run/batch` | `strategy` | 1 | 1 |

Total residuals: 3 route functions, 3 `DataSourceFactory()` calls, and 3
body-level `get_data_source("strategy")` calls.

Other route functions in `strategy.py` do not match this strict constructor
residual rule.

## GitNexus And Route Index Snapshot

GitNexus `api_impact(file="web/backend/app/api/strategy.py")` did not resolve
current `strategy.py` routes. `route_map("/strategy")` returned indexed routes
for `web/backend/app/api/strategy_management/_strategy_execution_router.py`,
but that file is absent from current `origin/main`.

Local Git and AST evidence at `1cca050be` confirms:

| Path | Current main status |
| --- | --- |
| `web/backend/app/api/strategy.py` | Exists and owns the current mainline strategy routes |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | Absent |

GitNexus symbol impact for the three selected current-main functions also
returned `not_found`. This is treated as an index coverage limitation, not as a
proof of no impact.

Any future source-authorized implementation must rerun impact/API-impact from
its own branch. If GitNexus still cannot resolve the current route file, the
implementation task must explicitly record the limitation and rely on local AST
route evidence plus focused route tests as the hard gate.

## Baseline Test Snapshot

The following focused baseline checks passed before this authorization package
was written:

| Check | Result |
| --- | --- |
| `python -m py_compile web/backend/app/api/strategy.py` | Pass |
| `pytest --no-cov tests/api/file_tests/test_strategy_api.py` | 18 passed |
| `pytest --no-cov tests/unit/api/test_strategy_api.py` | 17 passed |

These checks are baseline evidence only. The future implementation task must
rerun focused tests after source edits.

## Proposed Implementation Boundary

The later source-authorized task should keep the change narrow:

| Scope | Proposed path |
| --- | --- |
| Primary source file | `web/backend/app/api/strategy.py` |
| Route/API regression tests | `tests/api/file_tests/test_strategy_api.py` and `tests/unit/api/test_strategy_api.py` |
| Provider-injection regression test | A focused test may be added under `web/backend/tests/` or another existing backend route-test location if needed |

The expected implementation pattern should follow the already-landed
technical-analysis provider shape:

1. Move `DataSourceFactory()` construction out of the three selected route
   bodies into a small provider helper such as `get_strategy_data_source()`.
2. Inject the strategy adapter into the three route handlers with `Depends(...)`.
3. Preserve route paths, response models, response envelopes, parameter
   validation, exception mapping, and adapter method calls.
4. Add or adjust focused tests only for the provider-injection behavior and the
   affected strategy route contract.

## Non-Goals

The follow-up implementation must not:

| Non-goal | Reason |
| --- | --- |
| Modify OpenStock internals | OpenStock work is owned separately and remains out of scope |
| Rewrite strategy execution algorithms or adapter behavior | G2.336 only targets route-body `DataSourceFactory()` lifecycle residuals |
| Change response schemas, return envelopes, or OpenAPI contracts | The task is DI lifecycle cleanup, not API redesign |
| Touch watchlist residuals | Watchlist has branch-anchor reconciliation risk and needs separate authorization |
| Broaden to dashboard `get_data_source()` observation | It does not match the strict `DataSourceFactory()` residual rule |
| Delete or retire files | Deletion/retirement requires separate authorization under repository standards |

## Authorization Decision

G2.336 authorizes only the next planning direction:

| Decision | Result |
| --- | --- |
| Next candidate family | `strategy.py` service lifecycle DI residuals |
| Target base | `origin/main` |
| Source implementation status | Not implemented by this task |
| Required next node | Separate source-authorized task card before any code/test edits |
| OpenStock status | Boundary-only; no OpenStock development or modification |

## Required Next Gate

Before editing source in the next node, the implementation branch must:

1. Create a source-authorized task card with explicit allowed source and test
   paths.
2. Rerun GitNexus impact/API-impact for `web/backend/app/api/strategy.py` and
   report either the resolved risk level or the current route-index limitation.
3. Inspect existing strategy tests and choose focused regression coverage before
   writing implementation code.
4. Run `python -m py_compile`, focused strategy API tests, mainline scope gate,
   path whitelist, `git diff --check`, GitNexus detect changes, and GitHub CI.
5. Keep OpenStock internals out of scope.

## Verification Scope

This package is expected to modify only:

| Path | Purpose |
| --- | --- |
| `docs/reports/quality/backend-service-lifecycle-di-strategy-authorization-2026-06-13.md` | G2.336 no-source authorization preflight evidence |
| `governance/mainline/task-cards/g2-336.yaml` | G2.336 mainline task card and no-source gate definition |
