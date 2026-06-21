# B4.012-M3a-E3b Repository Hygiene Docs Truth Drift Decision

- Date: 2026-06-22
- Node: `b4-012-m3a-e3b-repository-hygiene-docs-truth-drift-decision`
- Parent: `b4-012-m3a-e3-governance-script-tests-split`
- Trigger: `b4-012-m3a-e3a-repository-hygiene-unit-script-authorization` could not close because its focused pytest gate is broadly red.
- Source edits authorized: false

## Scope

This is a no-source decision package. It records the current repository-hygiene docs truth drift that blocks E3a.

No source, runtime, OpenSpec, OpenStock, frontend, backend, docs policy, test assertion, skip/xfail, or generated index file was modified in this package.

External dirty files remain isolated. The target E3a test file is clean before this decision package:

- `tests/unit/scripts/test_repository_hygiene_paths.py`: no unstaged diff after the strict E3a rollback.

## Fresh Evidence

Commands executed against current HEAD `941898da3`:

- `python -m py_compile tests/unit/scripts/test_repository_hygiene_paths.py`
  - Result: pass.
- `ruff check tests/unit/scripts/test_repository_hygiene_paths.py`
  - Result: fail, 3 lint errors.
  - `F821 Undefined name guides_index` at `tests/unit/scripts/test_repository_hygiene_paths.py:1687`.
  - `F841 Local variable guides_index is assigned to but never used` at `tests/unit/scripts/test_repository_hygiene_paths.py:1694`.
  - `F841 Local variable maestro_quick_start is assigned to but never used` at `tests/unit/scripts/test_repository_hygiene_paths.py:1745`.
- `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q --tb=short --no-cov`
  - Result: fail.
  - Collected: 102 tests.
  - Summary: `87 failed, 15 passed in 10.07s`.

## Failure Families

The pytest failures are not limited to the three lint issues. They show broad repository-hygiene documentation truth drift.

### 1. Docs Root Entrypoint Drift

Representative failure:

- `test_docs_root_entrypoints_are_frozen_to_index_and_function_tree`

The docs root file list no longer matches the asserted frozen entrypoint contract. Current facts include extra root docs such as `PRODUCT.md`, `README.md`, and `troubleshooting.md`.

### 2. Missing Reports / Cleanup Index Artifacts

Representative missing paths:

- `docs/reports/reviews/INDEX.md`
- `docs/reports/cleanup/index-artifacts/INDEX_root.md`
- `docs/reports/cleanup/INDEX.md`
- `docs/reports/completion_reports/INDEX.md`
- `docs/reports/tasks/INDEX.md`
- `docs/reports/code_quality/INDEX.md`
- `docs/reports/quality/README.md`
- `docs/reports/worklogs/INDEX.md`
- `docs/reports/analysis/INDEX.md`

These failures indicate the test still expects generated or historical index artifacts that are not present in the current worktree.

### 3. Missing Guide Family Indexes

Representative missing paths:

- `docs/guides/openspec-cmd/README.md`
- `docs/guides/superpowers/INDEX.md`
- `docs/guides/templates/INDEX.md`
- `docs/guides/data-interface/INDEX.md`
- `docs/guides/quant-trading/INDEX.md`
- `docs/guides/features/INDEX.md`
- `docs/guides/wencai/INDEX.md`
- `docs/guides/tdx-integration/INDEX.md`
- `docs/guides/buger/INDEX.md`

These failures are docs-truth or generated-index decisions, not test lint cleanup.

### 4. Historical Reports / Retired Material Drift

Representative failures:

- `test_phase1_governance_approval_doc_is_converged_under_reports_reviews`
- `test_directory_organization_review_doc_is_converged_under_reports_reviews`
- `test_selected_completion_reports_are_converged_under_reports_completion_reports`
- `test_recurring_claude_auto_worklog_is_converged_under_reports_worklogs_trunk`

These tests are asserting historical report placement and index visibility. The current repository state no longer satisfies those assumptions.

### 5. Root Agent Instruction Contract Drift

Representative failure:

- `test_root_agents_and_claude_document_gitnexus_staged_microbatch_rule`

The test expects the exact historical snippet `gitnexus_detect_changes({scope: "staged"})` in root agent instructions. Current root instructions use the active GitNexus CLI/MCP wording instead.

## Decision

E3a should stay blocked. Its prepared authorization is too narrow:

- It allows lint/import hygiene in `tests/unit/scripts/test_repository_hygiene_paths.py`.
- It forbids assertion weakening, docs policy changes, skip/xfail additions, restore/migration, and broad repository-hygiene rewrites.
- The current blocker is not only lint/import hygiene. It is a repository-hygiene docs truth drift across docs root, generated indexes, guide-family indexes, historical reports, and root agent instruction expectations.

Therefore E3a must not be used to repair docs truth, regenerate indexes, delete assertions, or accept broad pytest failures implicitly.

## Recommended Next Authorization

Create a separate package before unblocking E3a:

### `B4.012-M3a-E3b-A repository hygiene docs truth baseline decision`

Mode: no-source first.

Allowed actions:

- classify each failing family as one of:
  - active docs truth to repair;
  - generated artifact to regenerate;
  - historical assertion to retire;
  - pre-existing repository-hygiene debt to baseline;
  - obsolete test contract to split into a later explicit test-policy package.
- decide whether E3a can be narrowed to lint-only acceptance while recording the remaining pytest failures as known baseline debt.

Forbidden actions:

- no source/runtime/OpenSpec/OpenStock changes;
- no test assertion deletion or weakening;
- no skip/xfail additions;
- no docs/index repair until a follow-up docs-authorized package is approved;
- no broad `tests/unit/scripts/test_repository_hygiene_paths.py` rewrite.

After E3b-A, choose one of two implementation tracks:

1. `E3a-lint-only`: fix the three ruff issues and explicitly waive broad pytest failures as pre-existing baseline debt for this package only.
2. `E3b-B docs truth repair`: docs-authorized family repair of active docs/index truth, followed by a focused test run.

## Current Gate Impact

- `b4-012-m3a-e3a-repository-hygiene-unit-script-authorization`: remains blocked.
- `b4-012-m3a-e3-governance-script-tests-split`: remains decision-prepared.
- This E3b node is prepared as a no-source decision package to unblock sequencing clarity, not to authorize implementation.
