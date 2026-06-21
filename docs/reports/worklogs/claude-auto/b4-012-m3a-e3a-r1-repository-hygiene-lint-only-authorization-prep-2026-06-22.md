# B4.012-M3a-E3a-R1 Repository Hygiene Lint-Only Authorization Prep

- Date: 2026-06-22
- Node: `b4-012-m3a-e3a-r1-repository-hygiene-lint-only-recovery-authorization`
- Parent: `b4-012-m3a-e3a-repository-hygiene-unit-script-authorization`
- Basis:
  - `b4-012-m3a-e3b-repository-hygiene-docs-truth-drift-decision`
  - `b4-012-m3a-e3b-a-repository-hygiene-docs-truth-baseline-decision`
- Source edits authorized by this package: false

## Purpose

Prepare a narrow follow-up authorization to unblock only the lint/import hygiene part of E3a without mixing in broad docs truth repair.

The E3b-A baseline decision classified the focused pytest failures as pre-existing repository-hygiene docs truth debt for the purpose of this narrow lint recovery.

## Proposed Allowed Paths

If explicitly approved later, E3a-R1 may edit only:

- `tests/unit/scripts/test_repository_hygiene_paths.py`
- `docs/reports/worklogs/claude-auto/b4-012-m3a-e3a-r1-repository-hygiene-lint-only-closeout-2026-06-22.md`

## Proposed Allowed Actions

Only the following lint-only fixes are in scope:

- fix `F821 Undefined name guides_index` at `tests/unit/scripts/test_repository_hygiene_paths.py:1687`;
- fix `F841 Local variable guides_index is assigned to but never used` at `tests/unit/scripts/test_repository_hygiene_paths.py:1694`;
- fix `F841 Local variable maestro_quick_start is assigned to but never used` at `tests/unit/scripts/test_repository_hygiene_paths.py:1745`.

The expected implementation is minimal variable placement/removal only. It must not change assertion semantics.

## Proposed Non-Goals

E3a-R1 must not:

- delete or weaken assertions;
- add skip/xfail;
- rewrite or split `tests/unit/scripts/test_repository_hygiene_paths.py`;
- edit README, AGENTS, docs indexes, guide files, reports, OpenSpec, OpenStock, frontend, backend, or runtime code;
- regenerate missing indexes;
- attempt to make the full 102-test repository-hygiene suite green;
- touch external dirty files.

## Proposed Commit Gates

Required:

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus `verify-staged`
- GitNexus `detect-changes --scope staged`
- OPENDOG verification
- exact staged scope only
- `python -m py_compile tests/unit/scripts/test_repository_hygiene_paths.py`
- `ruff check tests/unit/scripts/test_repository_hygiene_paths.py`
- `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q --tb=short --no-cov`

Focused pytest acceptance is adjusted for this package only:

- The command must be executed and recorded.
- The known broad docs-truth baseline may remain red at `87 failed / 15 passed` or equivalent broad docs truth failure count.
- No new failure family may be introduced by the lint-only diff.

## Proposed Closeout Gates

Closeout must record:

- exact lint fixes landed;
- confirmation that no assertions were changed;
- py_compile result;
- ruff result;
- focused pytest result and whether the remaining failures match the E3b-A baseline;
- staged file list;
- GitNexus and OPENDOG status;
- E3a-R1 remains separate from E3b-B docs truth repair.

## Authorization Status

This file prepares the authorization scope only.

Implementation is not authorized until the user explicitly approves:

`B4.012-M3a-E3a-R1 repository hygiene lint-only recovery implementation`.
