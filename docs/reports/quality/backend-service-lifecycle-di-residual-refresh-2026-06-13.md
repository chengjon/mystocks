# Backend Service Lifecycle DI Residual Refresh

## Status

- Date: 2026-06-13
- Task: G2.338
- Mode: no-source residual refresh
- Branch: `g2-338-service-di-residual-refresh`
- Base: `origin/main`
- Base commit: `6a858519c8a2d5c8948776ecc0986ef2b4a5f769`
- Parent PR: `https://github.com/chengjon/mystocks/pull/485`
- OpenStock boundary: no OpenStock internals, tests, runtime, configuration, packaging, or repository files changed.

## Scope

G2.338 refreshes the service lifecycle DI residual pool after G2.337 merged the strategy provider-injection implementation.

Allowed output:

- This report.
- G2.338 mainline task card.

Forbidden in this task:

- Source, tests, frontend, config, dependency, runtime, OpenSpec implementation, OpenStock, deletion, or retirement changes.

## Scan Method

The scan parsed Python AST from backend API route files and counted route-body calls to:

- `DataSourceFactory`
- `get_data_source`

Classification:

- **Strict constructor residual**: route body still calls `DataSourceFactory()` and `get_data_source(...)`.
- **Weak direct-source residual**: route body calls a module-level `get_data_source()` directly but does not construct `DataSourceFactory()`.
- **Provider boundary**: `DataSourceFactory()` and `get_data_source(...)` are contained in a non-route provider function, and route bodies receive the adapter/source through dependency injection or an equivalent provider boundary.

## Current Mainline Result

Current mainline ref:

| Ref | Commit | API files scanned | Residual files | Residual routes |
| --- | --- | ---: | ---: | ---: |
| `origin/main` | `6a858519c8a2d5c8948776ecc0986ef2b4a5f769` | 204 | 2 | 9 |

Current mainline strict constructor residuals:

| File | Route functions | Count | Decision |
| --- | --- | ---: | --- |
| `web/backend/app/api/watchlist.py` | `get_my_watchlist`, `get_my_watchlist_symbols`, `add_to_watchlist`, `remove_from_watchlist`, `check_in_watchlist`, `update_watchlist_notes`, `get_watchlist_count`, `clear_watchlist` | 8 | Next current-main strict constructor candidate. Requires separate source-authorized task. |

Current mainline weak direct-source residuals:

| File | Route function | Route | Evidence | Decision |
| --- | --- | --- | --- | --- |
| `web/backend/app/api/dashboard.py` | `get_dashboard_summary` | `GET /summary` | calls module-level `get_data_source()` in the route body, without constructing `DataSourceFactory()` | Track as a separate weak residual candidate after watchlist. Do not mix with watchlist implementation authorization. |

Current mainline resolved focus files:

| File | Status |
| --- | --- |
| `web/backend/app/api/strategy.py` | Resolved. No route-body residuals; provider boundary `get_strategy_data_source` remains as intended. |
| `web/backend/app/api/technical_analysis.py` | Resolved. No route-body residuals; provider boundary `get_technical_analysis_data_source` remains as intended. |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | Absent on current main. Do not use this historical seed as current-main source truth. |

## Multi-Ref Branch-Anchor Comparison

| Ref | Commit | Watchlist | Strategy | Technical Analysis | Dashboard weak residual |
| --- | --- | --- | --- | --- | --- |
| `origin/main` | `6a858519c8a2d5c8948776ecc0986ef2b4a5f769` | 8 strict constructor residuals in `watchlist.py` | resolved in `strategy.py` | resolved in `technical_analysis.py` | 1 weak direct-source residual in `dashboard.py` |
| `origin/wip/root-dirty-20260403` | `e1dbb6d962affd2d04c7885879a9c9d19bcf0dfd` | resolved through `get_watchlist_data_source` provider boundary | `strategy.py` absent; historical `_strategy_execution_router.py` has 3 strict constructor residuals | 8 strict constructor residuals | not selected in this scan |
| PR #474 merge | `2ebff6d7ded33403c691a60fc43f87dabf90a975` | resolved through `get_watchlist_data_source` provider boundary | `strategy.py` absent; historical `_strategy_execution_router.py` has 3 strict constructor residuals | 8 strict constructor residuals | not selected in this scan |

Interpretation:

- The G2.337 current-main strategy implementation is effective: `strategy.py` now has zero route-body residuals.
- The earlier G2.332 current-main technical-analysis implementation is effective: `technical_analysis.py` now has zero route-body residuals.
- Watchlist remains unresolved on current main, even though PR #474 and `origin/wip/root-dirty-20260403` show an accepted provider-boundary shape for the wip branch.
- The watchlist wip/PR #474 anchor is useful evidence but is not the same as current-main authorization. A future source task must work against current `origin/main` and may use the PR #474 pattern as evidence, not as a blind merge source.
- Dashboard `/summary` is a weaker direct-source residual, not a route-body `DataSourceFactory()` constructor residual. It should be handled separately after the strict constructor pool is closed.

## Decision

G2.338 does not authorize source implementation.

Recommended next gate:

1. Prepare a source-authorized watchlist provider-injection task against current `origin/main`.
2. Bound the allowed source/test files to `web/backend/app/api/watchlist.py` and focused watchlist provider/API tests.
3. Re-run GitNexus/API impact for `watchlist.py` before editing.
4. Preserve watchlist route paths, response envelopes, parameter validation, exception mapping, and data-source method payloads.
5. Record PR #474 as branch-anchor evidence only.
6. Leave dashboard weak residual for a later, separate no-source or source-authorized task.

## Verification

Commands/evidence:

- AST scan across `origin/main`, `origin/wip/root-dirty-20260403`, and PR #474 merge commit.
- Current-main focus scan confirmed:
  - `strategy.py`: zero route-body residuals.
  - `technical_analysis.py`: zero route-body residuals.
  - `watchlist.py`: eight strict constructor residuals.
  - `dashboard.py`: one weak direct-source residual.

Remaining required closeout checks:

- `git diff HEAD~1..HEAD --check`
- G2.338 mainline scope gate
- GitNexus `detect_changes(scope=compare, base_ref=origin/main)`
- PR CI before merge

## Rollback

Revert the G2.338 governance commit to remove this residual-refresh report and task card. No source behavior changes are involved.
