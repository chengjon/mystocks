# B4.012-M3a-E3a Repository Hygiene Unit Script Authorization Prep

- Date: 2026-06-21
- Node: `b4-012-m3a-e3a-repository-hygiene-unit-script-authorization`
- Parent: `b4-012-m3a-e3-governance-script-tests-split`
- Source edits authorized: false

## No-Source Boundary Review

This package prepares implementation authorization only. It does not modify tests, source/runtime code, OpenSpec, OpenStock provider/runtime implementation, frontend/backend source, `scripts/tests/**`, untracked files, ST-HOLD, or `marketKlineData`.

E3 split evidence identified one tracked unit-script candidate:

- `tests/unit/scripts/test_repository_hygiene_paths.py`

Current sibling untracked files remain excluded and must stay under `B4.012-M3a-U` provenance review:

- `tests/unit/scripts/test_collect_tech_debt_baseline.py`
- `tests/unit/scripts/test_gitnexus_workflow_gate.py`
- `tests/unit/scripts/test_graphiti_post_commit_hook_integration.py`

`scripts/tests/**` remains excluded and must be handled by a later family split because it contains 28 tracked dirty files across legacy, security-auth, data-source/data-utility, performance/scalability, DB/logging, API-health, and governance-hygiene groups.

## Candidate Diff Shape

The tracked candidate currently has a small repository-hygiene test cleanup:

- removes one unused `readme = (PROJECT_ROOT / "README.md").read_text(...)` local from `test_ai_tooling_guides_are_converged_under_guides_ai_tools_family`

No repository hygiene assertion, path expectation, deletion policy, skip/xfail marker, or test function name is changed by the candidate diff.

## Proposed Authorization

Allowed implementation files:

- `tests/unit/scripts/test_repository_hygiene_paths.py`
- `docs/reports/worklogs/claude-auto/b4-012-m3a-e3a-repository-hygiene-unit-script-closeout-2026-06-21.md`

Allowed implementation actions:

- syntax/lint/import hygiene inside the exact tracked unit-script file
- preserving repository-hygiene test assertions and path-policy expectations
- focused verification of the explicit test file

Forbidden actions:

- no source/runtime changes
- no `scripts/tests/**`
- no untracked `tests/unit/scripts/**` files
- no OpenSpec/OpenStock provider/runtime changes
- no assertion weakening, skip/xfail addition, deletion, restore, migration, or broad refactor
- no ST-HOLD or `marketKlineData`

## Required Gates For Future Implementation

- `python -m py_compile tests/unit/scripts/test_repository_hygiene_paths.py`
- `ruff check tests/unit/scripts/test_repository_hygiene_paths.py`
- focused pytest for `tests/unit/scripts/test_repository_hygiene_paths.py`
- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus `verify-staged` and `detect-changes --scope staged`
- OPENDOG verification
- precise staged scope containing only E3a allowed files, generated governance state, and the E3a closeout worklog

## Disposition

E3a is ready for user review as an authorization-prepared package. No test implementation is authorized until this node is explicitly approved for implementation.
