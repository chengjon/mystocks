# G2.359 Strategy Execution Router Dirty Ownership Confirmation / No-Source

Date: 2026-06-05
Node: G2.359
Mode: strategy execution router dirty ownership confirmation / no-source
Branch: `wip/root-dirty-20260403`
Evidence HEAD: `c3bf82211`
Parent report: `docs/reports/worklogs/claude-auto/g2-358-strategy-execution-router-provider-seam-authorization-preflight-2026-06-05.md`
Source edit authority: `false`

## Authorization Boundary

This node confirms the ownership state of the current dirty files around the strategy execution router provider seam. It does not claim authorship of the dirty hunks, absorb them into a source package, edit source code, edit tests, stage files, or run implementation tests.

This node remains no-source. Any future source or test edit still requires explicit source/test edit authority.

## Current State

- Branch: `wip/root-dirty-20260403`.
- HEAD: `c3bf82211`.
- Staged changes: none.
- Existing reports G2.355-G2.358 are untracked report artifacts.
- Primary dirty source file:
  - `web/backend/app/api/strategy_management/_strategy_execution_router.py`
- Primary dirty test file:
  - `tests/api/file_tests/test_strategy_management_api.py`

## Ownership Confirmation Result

| File | Current dirty state | Evidence classification | Ownership result | Source authorization result |
|---|---:|---|---|---|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | +9/-9 across 4 hunks | All 4 hunks are provider-seam related. One hunk defines or reshapes the helper seam; three hunks affect direct handler call sites. | Candidate baseline for a future provider-seam source package, but ownership is externally unconfirmed by git evidence. | Not authorized. Must not be edited or absorbed under G2.359. |
| `tests/api/file_tests/test_strategy_management_api.py` | +89/-4 across 7 hunks | 6 hunks are provider/test seam candidates; 1 hunk is signature/test-shape only and remains externally ambiguous. | Candidate test baseline only after ownership confirmation; not a committed gate yet. | Not authorized. Must not be edited, normalized, or treated as passing baseline under G2.359. |

## Router Hunk Classification

| Hunk | Anchor | Classification | Readiness | Absorption rule |
|---:|---|---|---|---|
| 1 | module/helper area near `get_strategy_data_source` | Provider seam plus helper/signature shape | Helper-definition ownership required | Preserve or supersede only after explicit source authority. |
| 2 | `get_strategy_definitions` | Provider seam | Candidate to absorb after owner confirmation | Preserve or supersede only after explicit source authority. |
| 3 | `run_strategy_single` | Provider seam | Candidate to absorb after owner confirmation | Preserve or supersede only after explicit source authority. |
| 4 | `run_strategy_batch` | Provider seam | Candidate to absorb after owner confirmation | Preserve or supersede only after explicit source authority. |

## Test Hunk Classification

| Hunk | Anchor | Classification | Readiness | Absorption rule |
|---:|---|---|---|---|
| 1 | `strategy_module` / fixture area | Test seam plus new fixture/signature shape | Candidate test baseline after owner confirmation | Use as gate only after confirmation. |
| 2 | `TestStrategyManagementAPIFile` | Test seam | Candidate test baseline after owner confirmation | Use as gate only after confirmation. |
| 3 | `TestStrategyManagementAPIFile` | Test seam | Candidate test baseline after owner confirmation | Use as gate only after confirmation. |
| 4 | `TestStrategyManagementAPIFile` | Test seam | Candidate test baseline after owner confirmation | Use as gate only after confirmation. |
| 5 | `TestStrategyManagementAPIFile` | Signature/test-shape only | External confirmation required | Do not absorb by default. |
| 6 | `TestStrategyManagementAPIFile` | Test seam | Candidate test baseline after owner confirmation | Use as gate only after confirmation. |
| 7 | `TestStrategyManagementAPIFile` | Provider seam plus test seam plus new test/signature shape | Candidate test baseline after owner confirmation | Use as gate only after confirmation. |

## Ownership Decision Table

| Question | Confirmation | Governance decision |
|---|---|---|
| Can G2.359 identify the dirty hunks as authored by this node? | No. This node did not edit source or tests and has no git evidence proving author identity. | Treat all dirty hunks as externally unconfirmed. |
| Are the router dirty hunks relevant to the provider-seam candidate? | Yes. All router hunks classify as provider-seam related. | They may be preserved or superseded only inside a later source-authorized node. |
| Are the test dirty hunks relevant to the provider-seam candidate? | Mostly yes. Six of seven hunks classify as provider/test seam candidates. | They may become the focused test baseline only after ownership confirmation. |
| Is one test hunk ambiguous? | Yes. One hunk classifies only as signature/test-shape. | Do not absorb it by default; require explicit confirmation. |
| Can `DataSourceFactory` implementation files be changed now? | No. They are not dirty blockers in this ownership check. | Keep factory implementation files out of scope. |
| Can source implementation begin now? | No. | `source_edit_authority=false`; dirty ownership remains externally unconfirmed. |

## Future Authorization Gate

If the user later grants source/test edit authority, the implementation node must begin with an explicit ownership statement:

| Required decision | Accepted values |
|---|---|
| Router dirty hunk ownership | preserve current dirty shape / supersede current dirty shape / reject current dirty shape |
| Test dirty hunk ownership | preserve current dirty tests / supersede current dirty tests / reject current dirty tests |
| Ambiguous test hunk 5 | preserve / supersede / reject |
| GitNexus stale-index handling | refresh index / accept stale preflight with caveat |
| Focused test gate | choose exact pytest command set before editing |

## Clean Next Boundary

G2.359 closes the dirty ownership confirmation node without source authority. The next no-source continuation, if needed, should be:

`G2.360 strategy execution router source authorization packet / no-source`

That packet would be a final written authorization checklist only. It should not edit files. It should prepare the exact yes/no source package that the user can approve or reject.

If the user explicitly grants source/test edit authority instead, the implementation node should be renamed to make the authority explicit, for example:

`G2.361 strategy execution router provider-seam implementation / source-authorized`

## Closeout

G2.359 is complete as a no-source ownership confirmation. The dirty router hunks are provider-seam candidates, the dirty test hunks are mostly test-baseline candidates, and neither source nor tests are authorized for modification under this node.
