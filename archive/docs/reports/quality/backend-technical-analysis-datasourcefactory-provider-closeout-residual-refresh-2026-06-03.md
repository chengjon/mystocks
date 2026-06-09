# Backend Technical Analysis DataSourceFactory Provider Closeout / Residual Refresh - 2026-06-03

## Status

- Node: `G2.328`
- Type: no-source closeout / residual refresh
- Status: accepted reviewed no-source
- Parent: `G2.327 technical_analysis DataSourceFactory provider implementation`
- Parent disposition: reviewed-but-not-merged
- Source edits in this node: none

## Review Input

The human maintainer explicitly accepted the local G2.327 source implementation
as reviewed, while also requiring:

- no PR creation
- no code merge
- no unrelated dirty-worktree handling
- governance-only continuation

G2.327 therefore remains `source_implementation_review_required` and is marked
reviewed-but-not-merged, not accepted_merged.

## Residual Refresh

G2.328 refreshes only the technical_analysis provider lane. It does not perform
a worktree-wide candidate promotion because current `HEAD` is not a descendant
of the accepted PR #474 merge commit, and current `watchlist.py` does not match
the accepted PR #474 providerized state.

Technical analysis current worktree:

| Metric | Count |
|---|---:|
| route decorators | 8 |
| authorized handlers | 8 |
| provider present | yes |
| module `DataSourceFactory()` calls | 1 |
| module `.get_data_source(...)` calls | 1 |
| `Depends(get_technical_analysis_data_source)` bindings | 8 |
| handler direct `DataSourceFactory()` calls | 0 |
| handler direct `.get_data_source(...)` calls | 0 |

Baseline at current `HEAD` before local G2.327 source edits:

| Metric | Count |
|---|---:|
| provider present | no |
| module `DataSourceFactory()` calls | 8 |
| module `.get_data_source(...)` calls | 8 |
| `Depends(get_technical_analysis_data_source)` bindings | 0 |

## Branch Anchor Drift

`git merge-base --is-ancestor 2ebff6d7ded33403c691a60fc43f87dabf90a975 HEAD`
returned non-zero. Current `HEAD` is not a descendant of the PR #474 merge
commit even though PR #474 is the accepted watchlist provider anchor for this
line.

Observed watchlist counts:

| Source | `DataSourceFactory()` | `.get_data_source(...)` | provider dependency bindings |
|---|---:|---:|---:|
| current `HEAD` | 8 | 8 | 0 |
| current worktree | 8 | 8 | 0 |
| PR #474 merge commit | 1 | 1 | 8 |

This is recorded as branch-anchor drift, not as a new residual candidate. G2.328
does not touch `watchlist.py`.

## Closeout Decision

G2.328 closes the local reviewed technical_analysis provider lane for governance
purposes only. The technical_analysis handler residuals are closed in the
current worktree, while the source node remains reviewed-but-not-merged.

Next gate:

- `G2.329 service lifecycle DI branch-anchor reconciliation before next residual selection`
- Type: no-source
- Reason: a worktree-wide residual scan would rehydrate already accepted
  watchlist work as a false current candidate until PR #474 ancestry/current
  branch state is reconciled.
