# G2.358 Strategy Execution Router Provider-Seam Authorization Preflight / No-Source

Date: 2026-06-05
Node: G2.358
Mode: strategy execution router provider-seam authorization preflight / no-source
Branch: `wip/root-dirty-20260403`
Evidence HEAD: `c3bf82211`
Parent reports:
- `docs/reports/worklogs/claude-auto/g2-355-service-lifecycle-residual-cluster-inventory-2026-06-05.md`
- `docs/reports/worklogs/claude-auto/g2-356-service-lifecycle-dirty-state-preflight-2026-06-05.md`
- `docs/reports/worklogs/claude-auto/g2-357-service-lifecycle-primary-dirty-state-reconciliation-2026-06-05.md`
Source edit authority: `false`

## Authorization Boundary

This node prepares a possible future authorization package for the strategy execution router provider seam. It does not grant that authorization.

This node is not authorized to edit source code, tests, router behavior, provider construction, dependency injection, compatibility shims, or cache files. It only records the provider seam, current dirty-state ownership questions, GitNexus impact targets, and focused test gates required before any source-authorized implementation can start.

## Evidence Summary

- Current branch: `wip/root-dirty-20260403`.
- Current HEAD: `c3bf82211`.
- Staged changes: none.
- Primary source target remains dirty:
  - `web/backend/app/api/strategy_management/_strategy_execution_router.py`
- Primary test consumer remains dirty:
  - `tests/api/file_tests/test_strategy_management_api.py`
- GitNexus impact was run in summary mode for four router symbols. All returned `LOW` risk, but all returned `index_status.stale=true` with `current_commit_differs_from_indexed_commit`. Therefore, GitNexus output is usable as preflight guidance only, not final implementation authorization.

## Provider-Seam Evidence

| Surface | Evidence | Interpretation |
|---|---|---|
| Source import boundary | `_strategy_execution_router.py` imports `DataSourceFactory` from `app.services.data_source_factory`. | The provider seam is in route-level consumption of the web backend data-source factory. |
| Provider helper | `get_strategy_data_source` exists in `_strategy_execution_router.py`; file markers show `DataSourceFactory`, `get_data_source`, and `get_strategy_data_source`. | This helper is the central seam for strategy router data-source access. |
| Dirty source diff | `_strategy_execution_router.py` is +9/-9 across 4 hunks. | The existing dirty diff already overlaps the intended provider seam and must be reconciled before any implementation work. |
| Handler callers | Dirty hunks affect `get_strategy_definitions`, `run_strategy_single`, and `run_strategy_batch`. | These are the immediate consumers of the provider helper. |
| Route structure | The file has 6 route decorators; dirty hunks do not touch imports or route decorators. | Current dirty state appears provider-call related, not route registration related. |
| Test consumer | `tests/api/file_tests/test_strategy_management_api.py` is +89/-4 and includes a `strategy_execution_module` fixture plus monkeypatch/provider assertions. | The test file already appears to be moving toward provider-seam coverage, but ownership and intended baseline are not confirmed. |

## Dirty Ownership Questions

These questions must be answered before any source-authorized node can start:

| Question | Why it blocks authorization | Required answer |
|---|---|---|
| Who owns the current `_strategy_execution_router.py` dirty diff? | It directly changes the provider helper and three handler call sites. | Confirm whether to preserve, supersede, or discard the current shape. |
| Who owns the current `test_strategy_management_api.py` dirty diff? | It adds fixture/monkeypatch coverage around the same seam. | Confirm whether those tests are intended baseline, partial work, or stale. |
| Should `get_strategy_data_source` be the canonical provider seam? | GitNexus and local diff both identify it as the direct helper used by route handlers. | Confirm this seam before changing route handlers or factory construction. |
| Should future source work touch `DataSourceFactory` implementation? | G2.355/G2.356 show the factory implementation is clean and the residual is route consumption. | Default answer should be no unless a concrete factory defect is proven. |
| Is the current GitNexus index fresh enough for implementation? | Impact results are stale by index status. | Run or require fresh GitNexus analysis before source edits, or explicitly document why stale indexed impact is acceptable. |

## GitNexus Impact Preflight

| Symbol | File | Direction | Risk | Direct upstream impact | Processes affected | Notes |
|---|---|---|---|---:|---:|---|
| `get_strategy_data_source` | `_strategy_execution_router.py` | upstream | LOW | 3 | 0 | Direct callers are `get_strategy_definitions`, `run_strategy_single`, and `run_strategy_batch`; relation type `CALLS`, confidence `0.85`. Index stale. |
| `get_strategy_definitions` | `_strategy_execution_router.py` | upstream | LOW | 0 | 0 | No indexed upstream impact in current stale index. |
| `run_strategy_single` | `_strategy_execution_router.py` | upstream | LOW | 0 | 0 | No indexed upstream impact in current stale index. |
| `run_strategy_batch` | `_strategy_execution_router.py` | upstream | LOW | 0 | 0 | No indexed upstream impact in current stale index. |

GitNexus module signal for `get_strategy_data_source` reported module `Akshare_market` with 3 direct hits. Because the index is stale, this is not sufficient to authorize edits by itself.

## Focused Test Gate Candidates

These commands are candidates for a future source-authorized node. They were not run in this no-source preflight.

| Gate | Command | Purpose |
|---|---|---|
| Strategy management file tests | `pytest tests/api/file_tests/test_strategy_management_api.py -q` | Validate route/provider seam contract and dirty test consumer behavior. |
| Strategy management API file test class | `pytest tests/api/file_tests/test_strategy_management_api.py::TestStrategyManagementAPIFile -q` | Narrow verification for the class that currently contains the dirty additions. |
| Backend strategy route smoke | `pytest tests/api/file_tests/test_strategy_api.py -q` | Adjacent strategy API regression surface if route behavior changes. |
| Data-source factory focused tests | `pytest web/backend/tests/_test_data_source_factory_management.py web/backend/tests/_test_data_source_factory_convenience.py -q` | Only needed if future implementation touches factory import or provider behavior beyond the router helper. |

## Authorization Package Shape

If the user later grants source authority, the safe implementation package should be narrow:

| Package item | Include? | Reason |
|---|---:|---|
| `_strategy_execution_router.py` provider helper | Yes | Primary seam and current dirty blocker. |
| Three handler call sites | Yes, only if preserving the helper seam requires it | They are the direct callers of `get_strategy_data_source`. |
| `test_strategy_management_api.py` | Yes, only after dirty ownership is confirmed | It already contains provider-seam test changes. |
| `web/backend/app/services/data_source_factory/data_source_factory.py` | No by default | Clean implementation file; no current evidence that factory implementation is the defect. |
| `web/backend/app/services/data_source_factory.py` facade | No | Compatibility-sensitive and not implicated by the dirty provider-seam diff. |
| Portfolio lifecycle files | No | Out of scope for strategy execution router provider seam. |
| Cache files | No | Cache line remains closed. |

## Decision Table

| Decision point | Decision | Rationale |
|---|---|---|
| Is G2.358 allowed to edit source or tests? | No. | `source_edit_authority=false`; this is only authorization preflight. |
| Is the strategy execution router provider seam a valid future source candidate? | Yes, conditionally. | Local diff and GitNexus both identify `get_strategy_data_source` and its three direct handler callers. |
| Is the candidate ready for implementation now? | No. | Primary source and test files are dirty, and GitNexus index is stale. |
| Is the risk currently high enough to block preflight? | No. | GitNexus reports LOW risk, but stale index requires refresh before implementation. |
| Should the future source package include factory implementation files? | No by default. | Evidence points to route/provider consumption, not factory internals. |
| What is the next non-source action? | Confirm dirty ownership and refresh impact evidence. | This is the minimum gate before any source-authorized node. |

## Clean Next Boundary

The next node should remain no-source unless the user explicitly grants source/test edit authority.

Recommended next no-source node:

`G2.359 strategy execution router dirty ownership confirmation / no-source`

Recommended source-authorized node only if explicitly approved later:

`G2.360 strategy execution router provider-seam implementation / source-authorized`

G2.360 must not start until:

1. Dirty ownership is confirmed for `_strategy_execution_router.py`.
2. Dirty ownership is confirmed for `tests/api/file_tests/test_strategy_management_api.py`.
3. GitNexus impact is refreshed or the stale-index caveat is explicitly accepted.
4. Focused test gates are selected.

## Closeout

G2.358 is complete as a no-source authorization preflight. It authorizes no source or test edits. The service lifecycle line is narrowed to a single conditional future source candidate: the strategy execution router provider seam.
