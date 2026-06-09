# G2.367 Post-Service-Lifecycle Next-Line Candidate Screening / No-Source

Date: 2026-06-05

Mode: no-source

source_edit_authority: false

test_edit_authority: false

## Boundary

This node screens whether a new backend governance line should start immediately after the G2.355-G2.366 service lifecycle residual line.

It does not authorize:

- source edits;
- test edits;
- cleanup;
- deletion;
- revert;
- staging;
- commit or amend.

It also does not reopen:

- cache line;
- strategy execution router provider-seam line;
- data-source registry residual line;
- portfolio lifecycle line;
- ArtDeco/frontend style line.

## Current Commit Context

| Item | Value |
|---|---|
| Current `HEAD` | `d55418ad4d819daaf4091c07573b37ab776aea6e` |
| Current `HEAD` subject | `refactor(web): split performance table styles` |
| Service lifecycle provider-seam commit | `1682c27e5d2370bc57d48ddb32034d27303e7b06` |
| Data-source registry residual commit | `f3e82e13e30dd4743b525d0e5bddbea43b1a6ee3` |
| Git index before this report | empty |

The current `HEAD` moved after backend lifecycle commits because unrelated ArtDeco style commits continued in parallel.

## Dirty Worktree Screening

The wider worktree is still very dirty and should not be treated as a single cleanup package.

Aggregated dirty count at screening time:

| Group | Count | Main signal |
|---|---:|---|
| frontend | 343 | Broad parallel frontend / ArtDeco work. |
| docs_reports | 394 | Broad docs/report churn. |
| scripts | 190 | Broad script churn. |
| tests | 133 | Broad test churn, not a narrow single endpoint residual. |
| backend_app | 56 | Multiple backend API/service changes and deletions. |
| openspec | 109 | Broad proposal/spec archival or movement. |
| worklogs | 7 | Prior untracked G2.330-G2.334 reports plus G2.366. |
| other | 184 | Config, governance, root docs, and source-adjacent churn. |

Total dirty entries observed: 1416.

## Backend Candidate Signal

Backend-related dirty entries are broad, not a single self-contained continuation of G2.355-G2.366.

Sample backend signals include:

- many `tests/api/file_tests/*` files;
- many `tests/api/test_*_file.py` files;
- multiple `web/backend/app/api/*` files;
- `web/backend/app/api/data_source_config.py`;
- deleted `web/backend/app/api/data_source_config.old.py`;
- strategy-management response file changes;
- web backend factory convenience/management tests.

Service-lifecycle keyword hits observed after G2.366:

| Signal | Interpretation |
|---|---|
| `data_source_config.py` and related tests | Candidate for a separate data-source-config line, not part of the closed data-source-registry residual. |
| `_strategy_execution_responses.py` | Strategy-management adjacent, but not provider-seam source package. Requires fresh no-source inventory before any action. |
| backend data-source factory tests | Potential factory/test cleanup line, but too broad to accept without focused inventory. |

No current scoped dirty state remains in the closed service lifecycle files:

- `data_source_registry.py`;
- `test_data_source_registry_api.py`;
- `data_source_factory.py`;
- `_strategy_execution_router.py`;
- `portfolio_tracker.py`;
- `_monitoring_portfolio_router.py`.

## OPENDOG Screening

Required broad-exploration OPENDOG commands were executed:

```bash
opendog agent-guidance --project mystocks --top 5 --json
opendog verification --id mystocks --json
opendog stats --id mystocks --path-classification source
opendog unused --id mystocks --path-classification source
```

Relevant OPENDOG guardrails:

- do not treat activity-derived signals as proof of safety without shell verification;
- do not start broad cleanup or refactor work while verification is missing, failing, or stale;
- deletion/cleanup candidates require import/runtime/test validation and explicit user confirmation;
- direct repository truth remains required.

No OPENDOG result provided a safe immediate source-authorized cleanup candidate.

## Decision Table

| Question | Decision | Rationale |
|---|---|---|
| Continue G2.355-G2.366 as an open line? | No | G2.366 closed the service lifecycle residual line and scoped status is clean. |
| Start a source-authorized backend cleanup now? | No | Dirty state is broad and not backed by a focused evidence packet. |
| Treat dirty backend files as one batch? | No | Backend dirty spans many APIs/tests and should not be collapsed into one package. |
| Reopen provider-seam or registry work? | No | Both have landed commits and no scoped dirty residual. |
| Start a new no-source candidate inventory? | Yes, only with a narrow domain | Candidate domains exist, but each needs its own boundary and evidence. |

## Candidate New Lines

If the user wants to continue backend governance, recommended next options are:

| Candidate node | Mode | Scope |
|---|---|---|
| `G2.368 data source config residual inventory / no-source` | no-source | `data_source_config.py`, `_data_source_config_responses.py`, and directly paired tests only. |
| `G2.368 strategy management response residual inventory / no-source` | no-source | `_strategy_execution_responses.py` and directly paired strategy-management tests only. |
| `G2.368 backend file-test drift inventory / no-source` | no-source | Broad `tests/api/file_tests/*` drift inventory without source edits. |

Do not start any of these as source-authorized work without a new inventory and decision table.

## Closeout

G2.367 completes next-line screening.

There is no evidence-backed source-authorized continuation from the closed service lifecycle residual line.

The next safe move is a new narrow no-source inventory selected by domain, with data-source-config residual inventory as the most adjacent backend candidate if the user wants to continue in the backend API/data-source area.
