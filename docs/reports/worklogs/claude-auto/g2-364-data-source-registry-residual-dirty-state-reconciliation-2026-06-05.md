# G2.364 Data Source Registry Residual Dirty-State Reconciliation / No-Source

Date: 2026-06-05

Mode: no-source

source_edit_authority: false

test_edit_authority: false

## Boundary

This node reconciles the remaining data-source registry dirty pair left after the committed strategy execution router provider-seam line.

This node does not authorize:

- source edits;
- test edits;
- revert operations;
- staging;
- commit or amend.

Scope is limited to:

- `web/backend/app/api/data_source_registry.py`
- `tests/api/file_tests/test_data_source_registry_api.py`

No cache files, provider-seam files, portfolio lifecycle files, ArtDeco files, or unrelated worktree changes are part of this node.

## Current Commit Context

| Item | Value |
|---|---|
| Current `HEAD` | `ddf4ecc4b33c2ebee28f9467e60dc3827f9c1189` |
| Current `HEAD` subject | `refactor(web): split ArtDeco sidebar styles` |
| Provider-seam commit | `1682c27e5d2370bc57d48ddb32034d27303e7b06` |
| Provider-seam subject | `refactor(api): route strategy execution through provider seam` |
| Provider-seam ancestry | ancestor of current `HEAD` |

G2.361/G2.362 are closed. This report does not reopen the provider-seam line.

## Evidence Collected

| Evidence | Result |
|---|---|
| Relevant status | `M tests/api/file_tests/test_data_source_registry_api.py`; `M web/backend/app/api/data_source_registry.py` |
| Diff stat | 2 files changed, 1 insertion, 2 deletions |
| Source numstat | 1 insertion, 1 deletion in `data_source_registry.py` |
| Test numstat | 1 deletion in `test_data_source_registry_api.py` |
| Diff hygiene | `git diff --check -- ...` passed |
| Focused pytest | `pytest tests/api/file_tests/test_data_source_registry_api.py -q --no-cov`: 15 passed in 0.41s |

## Dirty Hunk Inventory

| File | Hunk | Observed change | Runtime/API impact signal |
|---|---|---|---|
| `web/backend/app/api/data_source_registry.py` | `search_data_sources` docstring near line 105 | endpoint docstring expanded from generic search/filter wording to explicit category/type/health/keyword wording | No signature, decorator, response model, import, branch, or data path change observed |
| `tests/api/file_tests/test_data_source_registry_api.py` | import area near line 19 | explicit import of `api_test_fixtures` from `conftest.py` removed | Pytest fixture is still resolved by fixture injection; focused file test passed |

## Fixture Import Finding

`api_test_fixtures` remains heavily used as a pytest fixture parameter in `test_data_source_registry_api.py`.

The removed line is an explicit import from `tests.api.file_tests.conftest`. Pytest does not require direct imports for fixtures defined in `conftest.py`, and the focused test file passed after the import removal.

This supports a low behavioral-risk classification, but it does not by itself authorize accepting the edit under a no-source node.

## Ownership Classification

| Hunk | Classification | Reason |
|---|---|---|
| `search_data_sources` docstring refinement | Ambiguous-origin, low-risk documentation/source hunk | It is source-file content, but observed change is docstring-only and behavior-neutral by evidence. |
| `api_test_fixtures` explicit import removal | Ambiguous-origin, low-risk test cleanup hunk | It is test-file content, but focused pytest confirms fixture resolution still works. |

The hunks are not classified as user-approved implementation. They are also not classified as safe to revert. They are simply narrow, low-risk residual dirty hunks requiring explicit next-step authority.

## Decision Table

| Question | Decision | Rationale |
|---|---|---|
| Is this part of the committed provider-seam package? | No | Provider-seam commit did not include these files. |
| Does G2.364 authorize accepting these hunks? | No | `source_edit_authority=false`, `test_edit_authority=false`. |
| Does G2.364 authorize reverting these hunks? | No | Revert is also a source/test mutation. |
| Is the residual broad? | No | Two files, two hunks, three changed lines total. |
| Is a future source/test-authorized node warranted? | Yes, if the user wants to clear the dirty residual | The hunks are narrow and focused pytest passes, so they are suitable for a small explicit acceptance or rejection package. |

## Future Authorization Options

Recommended next node:

`G2.365 data source registry residual acceptance package / source-authorized`

Recommended default strategy if approved:

- preserve the current `data_source_registry.py` docstring refinement;
- preserve the current `test_data_source_registry_api.py` import cleanup;
- stage only these two files plus the G2.363/G2.364 evidence reports if the user wants the governance trail committed;
- run `git diff --cached --check`;
- run focused pytest: `pytest tests/api/file_tests/test_data_source_registry_api.py -q --no-cov`;
- run GitNexus staged change detection before commit;
- do not touch provider-seam, cache, portfolio, or ArtDeco files.

Alternative if the user rejects the residual:

- require explicit revert authorization;
- revert only the two hunks above;
- re-run the same focused pytest gate;
- keep provider-seam and unrelated worktree changes untouched.

## Clean Boundary

Include candidates for a future authorized package:

| File | Include candidate? | Reason |
|---|---:|---|
| `web/backend/app/api/data_source_registry.py` | yes | One docstring-only source hunk. |
| `tests/api/file_tests/test_data_source_registry_api.py` | yes | One explicit fixture import cleanup hunk. |
| `docs/reports/worklogs/claude-auto/g2-363-service-lifecycle-post-commit-closeout-and-registry-residual-handoff-2026-06-05.md` | optional | Prior handoff evidence. |
| `docs/reports/worklogs/claude-auto/g2-364-data-source-registry-residual-dirty-state-reconciliation-2026-06-05.md` | optional | Current reconciliation evidence. |

Exclude:

| File group | Exclude? | Reason |
|---|---:|---|
| Strategy execution router provider-seam files | yes | Closed and committed. |
| Cache files | yes | Cache line is closed. |
| Portfolio lifecycle files | yes | Not part of this dirty pair. |
| ArtDeco/frontend style files | yes | Unrelated parallel work. |
| Any additional source/test files | yes | No evidence requires expansion. |

## Closeout

G2.364 is complete as a no-source dirty-state reconciliation node.

It identifies the remaining data-source registry residual as a two-file, low-risk, ambiguous-origin dirty pair. Focused pytest passes, and diff hygiene passes. No source or test changes were made by this node.

Next action requires explicit user authorization: either accept the current two hunks under a small source/test-authorized package, or explicitly reject/revert them under an equally narrow authorization.
