# G2.360 Strategy Execution Router Source Authorization Packet / No-Source

Date: 2026-06-05
Node: G2.360
Mode: strategy execution router source authorization packet / no-source
Branch: `wip/root-dirty-20260403`
Evidence HEAD: `c3bf82211`
Parent reports:
- `docs/reports/worklogs/claude-auto/g2-358-strategy-execution-router-provider-seam-authorization-preflight-2026-06-05.md`
- `docs/reports/worklogs/claude-auto/g2-359-strategy-execution-router-dirty-ownership-confirmation-2026-06-05.md`
Source edit authority: `false`

## Authorization Boundary

This node produces the final no-source authorization packet for a possible future strategy execution router provider-seam implementation. It does not implement the packet.

This node does not authorize source edits, test edits, dependency-injection rewrites, data-source factory changes, route behavior changes, file staging, or commits. It only records the exact package that would need explicit user approval before a source-authorized node may start.

## Current State

| Item | State |
|---|---|
| Branch | `wip/root-dirty-20260403` |
| HEAD | `c3bf82211` |
| Last commit | `c3bf82211 refactor(web): split responsive sidebar styles` |
| Staged changes | none |
| Report chain | G2.355-G2.359 are untracked report artifacts |
| Primary source dirty file | `web/backend/app/api/strategy_management/_strategy_execution_router.py` |
| Primary test dirty file | `tests/api/file_tests/test_strategy_management_api.py` |
| Factory implementation status | `web/backend/app/services/data_source_factory/data_source_factory.py` clean |
| Factory facade/export status | `web/backend/app/services/data_source_factory.py` and package `__init__.py` clean |

## Packet Decision Summary

| Decision | Recommendation | Status |
|---|---|---|
| Source/test edit authority | Do not infer from "continue"; require explicit `source/test edit authority=true`. | Pending user authorization |
| Router dirty hunks | Preserve as candidate baseline unless user directs supersede/reject. | Pending user choice |
| Test dirty hunks | Preserve as candidate test baseline except ambiguous hunk 5, which needs explicit handling. | Pending user choice |
| Canonical provider seam | Use `get_strategy_data_source` as the route-level provider seam. | Recommended |
| Factory implementation edits | Exclude by default. | Recommended |
| Factory facade/export edits | Exclude. | Recommended |
| Cache files | Exclude. | Closed line |
| Portfolio lifecycle files | Exclude. | Out of scope |
| GitNexus stale index | Refresh before implementation, or explicitly accept stale-index caveat. | Pending user choice |

## Proposed Source-Authorized Package

This package is proposed only. It is not active until the user explicitly approves source/test edit authority.

| Package component | Proposed inclusion | Scope rule |
|---|---:|---|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | yes | Limit to provider helper and its three direct route-handler call sites. |
| `get_strategy_data_source` | yes | Treat as the canonical helper seam unless implementation evidence proves otherwise. |
| `get_strategy_definitions` | conditional yes | Touch only if necessary to consume the helper seam consistently. |
| `run_strategy_single` | conditional yes | Touch only if necessary to consume the helper seam consistently. |
| `run_strategy_batch` | conditional yes | Touch only if necessary to consume the helper seam consistently. |
| `tests/api/file_tests/test_strategy_management_api.py` | conditional yes | Use as focused test baseline only after dirty test ownership is accepted. |
| `web/backend/app/services/data_source_factory/data_source_factory.py` | no by default | Clean implementation file; no current evidence points to factory internals. |
| `web/backend/app/services/data_source_factory.py` | no | Compatibility facade is not implicated by router dirty diff. |
| `web/backend/app/services/data_source_factory/__init__.py` | no | Export boundary is not implicated by router dirty diff. |
| `web/backend/app/api/data_source_registry.py` | no | Separate dirty blocker from G2.356/G2.357; not part of this package. |
| `tests/api/file_tests/test_data_source_registry_api.py` | no | Separate test consumer; not part of this package. |

## Explicit User Choices Required

Before a source-authorized implementation node may start, the user must explicitly decide:

| Required choice | Options | Default recommendation |
|---|---|---|
| Source/test edit authority | approve / reject | reject until explicitly approved |
| Router dirty hunk ownership | preserve current dirty shape / supersede current dirty shape / reject current dirty shape | preserve, because all 4 hunks classify as provider-seam related |
| Test dirty hunk ownership | preserve current dirty tests / supersede current dirty tests / reject current dirty tests | preserve candidate seam tests after confirmation |
| Ambiguous test hunk 5 | preserve / supersede / reject | supersede or manually review before absorption |
| GitNexus stale-index handling | refresh index / accept stale preflight caveat | refresh before implementation |
| Focused tests | choose command set below | run strategy management focused file tests first |

## Focused Verification Gates

These gates are proposed for a future source-authorized node. They were not run here.

| Gate | Command | Required when |
|---|---|---|
| Strategy management file tests | `pytest tests/api/file_tests/test_strategy_management_api.py -q` | Always, if router or its focused tests are touched. |
| Strategy management focused class | `pytest tests/api/file_tests/test_strategy_management_api.py::TestStrategyManagementAPIFile -q` | Use for fast inner-loop verification. |
| Adjacent strategy API file tests | `pytest tests/api/file_tests/test_strategy_api.py -q` | Use if route contract or strategy API behavior is touched. |
| Data-source factory tests | `pytest web/backend/tests/_test_data_source_factory_management.py web/backend/tests/_test_data_source_factory_convenience.py -q` | Only if source work touches factory import/provider behavior outside the router helper. |
| GitNexus impact refresh | `gitnexus analyze`, then impact checks | Required if stale-index caveat is not explicitly accepted. |

## Implementation Guardrails For A Future Source Node

If source/test edit authority is later granted, the implementation must stay inside these guardrails:

1. Do not modify data-source factory implementation files unless new evidence proves factory internals are the defect.
2. Do not modify cache files.
3. Do not modify portfolio lifecycle files.
4. Do not normalize unrelated dirty files.
5. Do not revert existing dirty hunks blindly; choose preserve, supersede, or reject explicitly.
6. Run GitNexus impact before editing target functions, or record explicit stale-index acceptance.
7. Run the selected focused pytest gates and report actual outcomes.
8. If the implementation changes API route behavior, report route/test impact separately before closeout.

## Authorization Checklist

The future source node may start only when all boxes below are answered yes:

| Check | Required answer |
|---|---|
| User explicitly approved `source/test edit authority=true` | yes |
| User selected router dirty hunk ownership policy | yes |
| User selected test dirty hunk ownership policy | yes |
| User selected ambiguous test hunk 5 handling | yes |
| GitNexus stale-index handling selected | yes |
| Focused verification gates selected | yes |
| Scope excludes factory internals unless separately justified | yes |
| Scope excludes cache and portfolio lifecycle files | yes |

## Decision Table

| Decision point | Decision |
|---|---|
| Does G2.360 authorize source edits? | No. |
| Does G2.360 authorize test edits? | No. |
| Is the router provider seam ready as a candidate source package? | Yes, conditionally. |
| Can implementation begin from "continue" alone? | No. |
| What must the next implementation approval say? | It must explicitly approve `source/test edit authority=true` and select dirty hunk handling. |
| Recommended next source-authorized node name | `G2.361 strategy execution router provider-seam implementation / source-authorized` |

## Closeout

G2.360 is complete as a no-source authorization packet. It prepares the exact future source package but authorizes no source or test edits. The next step is either explicit source/test authorization for G2.361 or a stop/hold decision.
