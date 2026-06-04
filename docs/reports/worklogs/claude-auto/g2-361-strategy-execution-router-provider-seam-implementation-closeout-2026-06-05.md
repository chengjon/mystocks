# G2.361 Strategy Execution Router Provider-Seam Implementation Closeout / Source-Authorized

Date: 2026-06-05
Node: G2.361
Mode: strategy execution router provider-seam implementation / source-authorized
Branch: `wip/root-dirty-20260403`
Evidence HEAD: `a13eb4257`
Parent report: `docs/reports/worklogs/claude-auto/g2-360-strategy-execution-router-source-authorization-packet-2026-06-05.md`
Source/test edit authority: `true`, explicitly granted by user

## Authorization Boundary

The user explicitly approved source/test edit authority for the strategy execution router provider-seam implementation and selected the default strategy from G2.360:

- preserve the current router dirty shape;
- preserve the current test candidate baseline;
- structurally review the ambiguous test hunk before deciding;
- refresh GitNexus or accept the stale-index caveat;
- execute focused pytest gates.

No authority was granted to modify data-source factory implementation files, compatibility facades, cache files, portfolio lifecycle files, data-source registry files, or unrelated dirty files.

## Current HEAD Refresh

Before implementation, the current HEAD was refreshed:

- G2.360 report evidence HEAD: `c3bf82211`.
- Current implementation HEAD: `a13eb4257`.
- Latest commit at implementation time: `a13eb4257 refactor(web): split ArtDeco button styles`.

Because HEAD advanced, the G2.360 evidence was treated as stale and rechecked before closeout.

## Implementation Decision

The current dirty router/test shape already matched the authorized package. Therefore G2.361 adopted and verified the existing dirty shape instead of adding further source/test edits.

| File | Status | Decision | Reason |
|---|---:|---|---|
| `web/backend/app/api/strategy_management/_strategy_execution_router.py` | dirty | Preserve current dirty shape | It defines `get_strategy_data_source` and routes `get_strategy_definitions`, `run_strategy_single`, and `run_strategy_batch` through that helper. |
| `tests/api/file_tests/test_strategy_management_api.py` | dirty | Preserve current test candidate baseline | It adds focused monkeypatch coverage proving handlers use the overridable provider seam instead of direct `DataSourceFactory()` construction. |
| `web/backend/app/services/data_source_factory/data_source_factory.py` | clean | Do not touch | No evidence showed factory internals were the defect. |
| `web/backend/app/services/data_source_factory.py` | clean | Do not touch | Compatibility facade is outside the authorized seam. |
| `web/backend/app/services/data_source_factory/__init__.py` | clean | Do not touch | Export boundary is outside the authorized seam. |
| `web/backend/app/api/data_source_registry.py` | dirty | Do not touch | Separate G2.356/G2.357 blocker, not part of this package. |
| `tests/api/file_tests/test_data_source_registry_api.py` | dirty | Do not touch | Separate test consumer, not part of this package. |

## Ambiguous Test Hunk Review

G2.359 identified one ambiguous test hunk in `tests/api/file_tests/test_strategy_management_api.py`: the chart-data route assertion changed from "exported but not wired" to "exported and wired".

G2.361 structurally reviewed it and did not modify it:

| Item | Decision |
|---|---|
| Provider-seam relevance | Not directly provider-seam related. |
| Current route contract signal | The focused file test suite passes with 23 route method pairs, including the chart-data route. |
| Absorption decision | Preserve as current route-contract baseline, but record it as adjacent to the provider-seam package rather than core provider-seam work. |
| Additional edit | None. |

## GitNexus Evidence

GitNexus impact was re-run at current HEAD for the provider helper and the three direct handler targets.

| Symbol | Risk | Direct upstream impact | Processes affected | Index status |
|---|---|---:|---:|---|
| `get_strategy_data_source` | LOW | 3 | 0 | stale |
| `get_strategy_definitions` | LOW | 0 | 0 | stale |
| `run_strategy_single` | LOW | 0 | 0 | stale |
| `run_strategy_batch` | LOW | 0 | 0 | stale |

For `get_strategy_data_source`, GitNexus identified direct callers:

- `get_strategy_definitions`
- `run_strategy_single`
- `run_strategy_batch`

All GitNexus checks initially reported `index_status.stale=true` with `current_commit_differs_from_indexed_commit`. An initial refresh attempt used the wrong invocation form; this was corrected after user review because the project rule requires `gitnexus analyze`.

The corrected command `gitnexus analyze` was then executed from `/opt/claude/mystocks_spec` and completed successfully in 108.7s, indexing 235,580 nodes, 322,969 edges, 2742 clusters, and 300 flows. It reported optional `.proto` grammar unavailability and skipped 35 large generated/vendored files. A subsequent impact check still reported `index_status.stale=true` with `current_commit_differs_from_indexed_commit`. G2.361 therefore proceeds under the user-approved stale-index caveat while retaining LOW risk summary evidence and records that the project-required command was executed.

No `gitnexus analyze` process remained running after the refresh attempt.

## Verification Results

| Gate | Command | Result |
|---|---|---|
| Full focused strategy management file tests with default coverage config | `pytest tests/api/file_tests/test_strategy_management_api.py -q` | 11 tests passed, but pytest exited with coverage failure because total coverage was 4 and `fail-under=80`. This is a repository coverage gate outcome, not a provider-seam test failure. |
| Strategy management file tests without coverage | `pytest tests/api/file_tests/test_strategy_management_api.py -q --no-cov` | 11 passed, 1 warning, 3.52s. |
| Provider seam focused test without coverage | `pytest tests/api/file_tests/test_strategy_management_api.py::TestStrategyManagementAPIFile::test_strategy_execution_handlers_use_overridable_strategy_data_source -q --no-cov` | 1 passed, 1 warning, 6.50s. |
| Adjacent strategy API file tests without coverage | `pytest tests/api/file_tests/test_strategy_api.py -q --no-cov` | 18 passed, 0.51s. |
| Diff hygiene | `git diff --check -- <target files and reports>` | Passed. |

Warnings observed during pytest were pre-existing runtime/import noise around deprecated `HTTP_422_UNPROCESSABLE_ENTITY` and mock fallback logging for unimplemented real backtest data. They did not fail the focused gates.

## Final Scope Status

| Scope item | Status |
|---|---|
| Router provider seam | Implemented by preserving current dirty helper/call-site shape. |
| Focused provider-seam test | Present and passing with `--no-cov`. |
| Route contract baseline in same test file | Preserved and passing with `--no-cov`. |
| Factory implementation files | Untouched. |
| Data-source registry files | Untouched. |
| Cache files | Untouched. |
| Portfolio lifecycle files | Untouched. |
| Staged changes | None. |

## Closeout

G2.361 is complete as a source-authorized implementation closeout. The provider seam is in place through `get_strategy_data_source`, the three direct strategy execution handlers use that seam, focused tests pass without coverage, and no additional source/test edits were needed beyond adopting the current dirty shape authorized by the user.
