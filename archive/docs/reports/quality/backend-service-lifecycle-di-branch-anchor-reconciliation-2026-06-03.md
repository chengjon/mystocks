# Backend Service Lifecycle DI Branch-Anchor Reconciliation - 2026-06-03

## Status

- Node: `G2.329`
- Type: no-source branch-anchor reconciliation
- Status: accepted reviewed no-source
- Source edits: none
- Parent: `G2.328 technical_analysis DataSourceFactory provider closeout / residual refresh`

## Baseline Anchor

Read-only git evidence:

| Ref | Commit |
|---|---|
| local `HEAD` | `06b0fc09548774ba997784c878349c25087d7c88` |
| `origin/wip/root-dirty-20260403` | `2ebff6d7ded33403c691a60fc43f87dabf90a975` |
| PR #474 merge commit | `2ebff6d7ded33403c691a60fc43f87dabf90a975` |

Ancestor checks:

| Check | Exit code | Meaning |
|---|---:|---|
| PR #474 ancestor of local `HEAD` | 1 | no |
| local `HEAD` ancestor of `origin/wip/root-dirty-20260403` | 1 | no |
| `origin/wip/root-dirty-20260403` ancestor of local `HEAD` | 1 | no |

Classification: local `HEAD` and the accepted remote/PR #474 anchor have
diverged. For service lifecycle residual statistics, PR #474 /
`origin/wip/root-dirty-20260403` is the accepted watchlist provider anchor.

## Watchlist Calibration

| Source | `DataSourceFactory()` | `.get_data_source(...)` | provider dependency bindings |
|---|---:|---:|---:|
| current worktree | 8 | 8 | 0 |
| current `HEAD` | 8 | 8 | 0 |
| PR #474 anchor | 1 | 1 | 8 |

Decision: current watchlist 8/8 inline calls are branch-anchor drift for this
line. They are excluded from normalized residual candidate statistics and are
not promoted as a new candidate in G2.329.

## Candidate Pool Recalibration

Read-only scan:

- API Python files scanned: `218`
- Raw route-body DataSourceFactory candidates: `2`
- Normalized route-body DataSourceFactory candidates: `1`

Raw candidates:

| File | Direct handlers | `DataSourceFactory()` | `.get_data_source(...)` | Classification |
|---|---:|---:|---:|---|
| `web/backend/app/api/watchlist.py` | 8/15 | 8 | 8 | excluded by PR #474 anchor |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 3/6 | 3 | 3 | normalized active candidate |

Normalized candidate pool:

| File | Direct handlers | `DataSourceFactory()` | `.get_data_source(...)` |
|---|---:|---:|---:|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 3/6 | 3 | 3 |

Technical analysis adjustment:

- Source: reviewed local G2.327 worktree
- Provider backing calls: `1/1`
- Dependency bindings: `8`
- Handler direct residuals: `0/0`

## Closeout Decision

G2.329 completes the no-source branch-anchor reconciliation and candidate-pool
statistics calibration. It does not edit source or tests.

Next gate:

- `G2.330 service lifecycle DI global residual candidate screening`
- Type: no-source
- Seed candidate: `web/backend/app/api/strategy_management/_strategy_execution_router.py`
- Reason: after excluding accepted watchlist drift and applying local reviewed
  technical_analysis closeout, this is the only normalized route-body
  DataSourceFactory candidate remaining in the read-only API scan.
