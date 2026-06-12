# Backend Service Lifecycle DI Branch Anchor Reconciliation

Date: 2026-06-03
Freshness recheck: 2026-06-12
Node: `g2-329-service-lifecycle-di-branch-anchor-reconciliation-before-next-residual-selection`
Task card: `governance/mainline/task-cards/g2-329.yaml`
Evidence: `.planning/codebase/generated/service-lifecycle-di-branch-anchor-reconciliation-2026-06-03.json`

## Status

G2.329 is a no-source branch-anchor reconciliation gate. It does not authorize
source, test, API contract, frontend, config, script, OpenSpec, PM2, runtime
state, or shared DataSourceFactory implementation edits.

The node is accepted as reviewed no-source governance. Its purpose is to keep
the service lifecycle DI residual candidate pool from being skewed by branch
drift before G2.330 performs the next global residual screening.

## Parent State

| Surface | State |
|---|---|
| G2.321 watchlist DataSourceFactory provider | Merged through PR `#474` |
| G2.327 technical_analysis DataSourceFactory provider | Reviewed locally but not merged; no PR/merge claimed |
| G2.328 technical_analysis closeout / residual refresh | Accepted reviewed no-source |
| G2.329 branch-anchor reconciliation | Accepted reviewed no-source |
| G2.330 global residual screening | Planned no-source |

## Original Anchor Evidence

| Evidence | Value |
|---|---|
| Generated at | `2026-06-03T22:23:56+08:00` |
| Recorded workspace HEAD | `06b0fc09548774ba997784c878349c25087d7c88` |
| Recorded remote anchor | `origin/wip/root-dirty-20260403` at `2ebff6d7ded33403c691a60fc43f87dabf90a975` |
| Accepted PR anchor | PR `#474`, merge commit `2ebff6d7ded33403c691a60fc43f87dabf90a975` |
| Original classification | `local-head-and-remote-anchor-diverged` |
| Baseline policy | Use PR `#474` as accepted watchlist provider anchor; do not use local `watchlist.py` counts as residual truth |

## Watchlist Calibration

The generated evidence showed that local `watchlist.py` still contained inline
DataSourceFactory usage while the accepted PR `#474` anchor had moved the active
route surface to the provider/Depends pattern.

| Surface | DataSourceFactory calls | `get_data_source()` calls | Provider Depends calls | Disposition |
|---|---:|---:|---:|---|
| Local worktree in generated evidence | 8 | 8 | 0 | Exclude as branch-anchor drift |
| Current HEAD in generated evidence | 8 | 8 | 0 | Exclude as branch-anchor drift |
| PR `#474` anchor in generated evidence | 1 | 1 | 8 | Accepted watchlist provider anchor |

Decision: watchlist inline-call counts are not residual candidate truth for this
lane. G2.330 must not reselect watchlist from the local dirty branch counts.

## Candidate Pool Recalibration

The generated G2.329 pool used route-body DataSourceFactory scanning with two
normalization overlays:

| Candidate | Raw evidence | Normalized disposition |
|---|---|---|
| `web/backend/app/api/watchlist.py` | 8 direct handler calls in local branch evidence | Excluded by PR `#474` accepted watchlist anchor |
| `web/backend/app/api/technical_analysis.py` | Local reviewed G2.327 provider lane showed provider/Depends shape | Treated as closed only as a reviewed local overlay; no merge claimed |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 3 route-body DataSourceFactory / `get_data_source()` call expressions in generated evidence | Seed candidate for G2.330 no-source global residual screening |

Decision: after excluding accepted watchlist drift and applying the reviewed
technical_analysis overlay, the generated normalized route-body DataSourceFactory
pool had one seed candidate: `strategy_management/_strategy_execution_router.py`.

## Freshness Recheck

A read-only freshness recheck was run on 2026-06-12 before this report was
written. It found that the generated JSON is stale as current-branch evidence and
must be treated as the historical G2.329 reconciliation record, not as current
G2.330 screening truth.

| Check | 2026-06-12 value |
|---|---|
| Current report worktree HEAD | `022afee048dfb6dd0f8a73ba971fc33d8db7d771` |
| Current `origin/wip/root-dirty-20260403` | `e1dbb6d962affd2d04c7885879a9c9d19bcf0dfd` |
| PR `#474` merge commit | `2ebff6d7ded33403c691a60fc43f87dabf90a975` |
| PR `#474` state | `MERGED` |
| Current origin equals PR `#474` anchor | No |
| Generated JSON stale-if-local-head-changes | True |
| Generated JSON stale-if-origin-wip-moves | True |

Read-only spot counts from the freshness recheck:

| Ref | File | DataSourceFactory calls | `get_data_source()` calls | Provider Depends calls |
|---|---|---:|---:|---:|
| Local HEAD | `web/backend/app/api/watchlist.py` | 9 | 8 | 0 |
| PR `#474` | `web/backend/app/api/watchlist.py` | 2 | 1 | 8 |
| Current origin/wip | `web/backend/app/api/watchlist.py` | 2 | 1 | 8 |
| Local HEAD | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 2 | 1 | 0 |
| PR `#474` | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 4 | 3 | 0 |
| Current origin/wip | `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 4 | 3 | 0 |
| Local HEAD | `web/backend/app/api/technical_analysis.py` | 9 | 8 | 0 |
| Current origin/wip | `web/backend/app/api/technical_analysis.py` | 9 | 8 | 0 |

Freshness decision: G2.329 remains valid as a no-source branch-anchor
reconciliation record, but G2.330 must regenerate the normalized candidate pool
from the then-current accepted anchor before selecting or authorizing any source
lane.

## Verification

| Check | Result |
|---|---|
| Source files changed | None |
| Test files changed | None |
| Runtime behavior changed | No |
| OpenSpec implementation started | No |
| Function-tree catalog metadata | Stale literal entrypoints synchronized to current paths so the mainline scope gate can validate this no-source package |
| PR `#474` state checked | `MERGED` |
| Branch anchor rechecked | Current origin/wip has moved since generated evidence |
| Watchlist calibration rechecked | Watchlist local inline-call counts remain branch drift relative to PR `#474` / current origin provider shape |
| Candidate pool status | Historical G2.329 seed candidate is `strategy_management/_strategy_execution_router.py`; G2.330 must refresh before use |

## Next Gate

G2.330 may proceed only as no-source global residual candidate screening. It may
use this report to avoid reintroducing watchlist false positives, but it must
rerun current route-body DataSourceFactory screening before preparing any source
authorization packet.

No source implementation is selected or authorized by this report.
