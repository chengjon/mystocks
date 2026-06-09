# G2.357 Service Lifecycle Primary Dirty-State Reconciliation / No-Source

Date: 2026-06-05
Node: G2.357
Mode: service lifecycle primary dirty-state reconciliation / no-source
Branch: `wip/root-dirty-20260403`
Evidence HEAD: `c3bf82211`
Parent reports:
- `docs/reports/worklogs/claude-auto/g2-355-service-lifecycle-residual-cluster-inventory-2026-06-05.md`
- `docs/reports/worklogs/claude-auto/g2-356-service-lifecycle-dirty-state-preflight-2026-06-05.md`
Source edit authority: `false`

## Authorization Boundary

This node reconciles the two primary dirty-state blockers identified by G2.356:

- `web/backend/app/api/data_source_registry.py`
- `web/backend/app/api/strategy_management/_strategy_execution_router.py`

It is inventory and reconciliation only. It does not authorize editing either file, editing tests, rewriting provider seams, touching compatibility shims, or reopening cache work.

## Evidence Summary

- Current branch: `wip/root-dirty-20260403`.
- Current HEAD: `c3bf82211`.
- Staged changes: none.
- Evidence was derived from `git diff --unified=0`, `git diff --numstat`, function/class anchors, route decorators, and marker counts.
- No raw source diff was copied into this report.
- No source or test files were edited.

## Primary Dirty-State Reconciliation

| Primary target | Current dirty stat | Changed anchors | Touched structural surfaces | Reconciliation decision |
|---|---:|---|---|---|
| `web/backend/app/api/data_source_registry.py` | +1/-1 across 1 hunk | `search_data_sources` only | No import changes, no route decorator changes, no function signature changes, no startup/shutdown hook changes. | Dirty state is narrow and route-internal. It still blocks source authorization because the file is already modified and ownership of the change is unconfirmed. |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | +9/-9 across 4 hunks | provider helper area, `get_strategy_definitions`, `run_strategy_single`, `run_strategy_batch` | No import changes and no route decorator changes. The provider helper hunk touches a function signature and contains `DataSourceFactory` / `get_data_source` markers; handler hunks replace provider-call shape in three route handlers. | Dirty state is directly related to the suspected provider seam. This is the highest-priority blocker before any source-authorized work. |

## File-Level Evidence Table

| File | Route surface | Lifecycle markers | Diff shape | Risk reading |
|---|---|---|---|---|
| `web/backend/app/api/data_source_registry.py` | 7 route decorators; `APIRouter` present | `UnifiedResponse` markers present; startup/shutdown hook markers present; one `get_data_source` function name marker | One internal hunk inside `search_data_sources` | Low structural risk by diff shape, but not source-ready until dirty ownership is resolved. |
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | 6 route decorators; `APIRouter` present | `DataSourceFactory` and `get_data_source` markers present; no startup/shutdown lifecycle hooks | One provider-helper hunk plus three handler hunks | Medium governance risk: the dirty change overlaps the exact route/provider residual seam from G2.355. |

## Authorization Readiness

| Candidate source node | Current readiness | Blocking facts | Minimum evidence before source authorization |
|---|---|---|---|
| Data-source registry route cleanup or lifecycle change | Not ready | Primary file dirty; associated test consumer was already dirty in G2.356; ownership of +1/-1 change not confirmed. | Confirm whether the current dirty hunk is intentional, stale, or from another batch; refresh route/test evidence at current HEAD; run GitNexus impact for any function to be edited. |
| Strategy execution router provider-seam source work | Not ready, but highest-priority candidate | Dirty diff already touches provider helper and three strategy route handlers; associated route test consumer is dirty; provider helper overlaps `DataSourceFactory` and `.get_data_source(...)` residual seam. | Confirm ownership of current dirty diff; decide whether to preserve, absorb, or supersede the existing provider-helper shape; run GitNexus impact on `get_strategy_data_source`, `get_strategy_definitions`, `run_strategy_single`, and `run_strategy_batch`; define focused API tests. |
| Broad service lifecycle cluster source work | Not ready | G2.355 showed multiple active ownership bands; G2.356 showed many adjacent dirty files. | Select one concrete source candidate. Do not authorize broad cluster edits. |

## Decision Table

| Decision point | Decision | Reason |
|---|---|---|
| Can either primary dirty file be edited now? | No. | `source_edit_authority=false`; both primary files already have unowned dirty diffs. |
| Which blocker should be resolved first? | `_strategy_execution_router.py`. | Its dirty diff overlaps the exact provider seam from the service lifecycle residual queue. |
| Is `data_source_registry.py` lower priority? | Yes for this line. | Current dirty hunk is narrow and does not touch imports, route decorators, signatures, or startup/shutdown hooks. |
| Can the web backend data-source factory implementation be changed instead? | No. | The implementation file is clean, but the active residual is in route/provider consumption. Editing the factory would skip the dirty route evidence. |
| Can portfolio lifecycle source work start from this reconciliation? | No. | Portfolio primary files are not the two current dirty blockers; G2.356 requires band selection and caller evidence first. |
| Can cache work be reopened? | No. | Cache line remains closed and out of scope. |

## Clean Next Boundary

The next safe node, if continuing without source authority, should be:

`G2.358 strategy execution router provider-seam authorization preflight / no-source`

That node should stay report-only unless source authority is explicitly granted. Its purpose would be to prepare, not execute, a possible source-authorized package by collecting:

1. Dirty-diff ownership for `_strategy_execution_router.py`.
2. Route test consumer dirty-state ownership for `tests/api/file_tests/test_strategy_management_api.py`.
3. GitNexus impact targets for the provider helper and three route handlers.
4. Focused test commands required if source authorization is later granted.

## Closeout

G2.357 is complete as a no-source reconciliation node. It authorizes no source or test edits. The service lifecycle line is now narrowed from a broad residual cluster to one primary future preflight candidate: the strategy execution router provider seam.
