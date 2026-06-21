# B4.012-M3a-E3a-R1 Repository Hygiene Lint-Only Recovery Closeout

- Date: 2026-06-22
- Node: `b4-012-m3a-e3a-r1-repository-hygiene-lint-only-recovery-authorization`
- Parent: `b4-012-m3a-e3a-repository-hygiene-unit-script-authorization`
- Status at closeout: lint-only recovery committed as `a68d6a604`

## What Changed

Only lint-only variable hygiene was adjusted in `tests/unit/scripts/test_repository_hygiene_paths.py`:

- moved `guides_index` into `test_governance_guides_are_converged_under_guides_governance_family()`, where it is actually used;
- removed the unused `guides_index` read from `test_onboarding_guides_are_converged_under_guides_onboarding_family()`;
- removed the unused `maestro_quick_start` read from `test_maestro_and_multicli_runtime_docs_are_converged_under_guides_multicli_tasks()`.

No assertion text was changed.
No skip/xfail was added.
No docs/index/readme content was modified.
No source/runtime/OpenSpec/OpenStock/frontend/backend file was modified.

## Verification Results

Executed after the edit:

- `python -m py_compile tests/unit/scripts/test_repository_hygiene_paths.py`
  - Pass.
- `ruff check tests/unit/scripts/test_repository_hygiene_paths.py`
  - Pass.
- `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q --tb=short --no-cov`
  - Fail, but with the same broad repository-hygiene docs-truth baseline.
  - Summary: `87 failed, 15 passed`.

The focused pytest failure set still matches the already-baselined docs truth drift families from `E3b-A`:

- docs root / agent contract drift;
- reports cleanup and generated index drift;
- architecture / overview / standards docs drift;
- AI tooling and agent guide drift;
- web frontend guide drift;
- ops / CI/CD / monitoring guide drift;
- data / quant guide drift;
- legacy report placement drift;
- uncategorized supporting-guide drift.

This is expected. The package was explicitly scoped as lint-only recovery, not docs truth repair.

## Baseline Comparison

Compared with the `E3b-A` baseline decision:

- no new failure family was introduced by the lint-only edit;
- the overall broad pytest count remained `87 failed / 15 passed`;
- the lint-only diff did not change the repository-hygiene docs truth state;
- the work stays separated from the later docs-truth repair decision path.

## Gates

Passed before commit:

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus `verify-staged`
- GitNexus `detect-changes --scope staged`
- OPENDOG verification
- exact staged scope only

Passed after commit:

- GitNexus full rebuild / index refresh
- final `git diff --cached --name-status` empty
- final GitNexus `verify-staged` no changes
- final FUNCTION_TREE validate passed
- final OPENDOG verification still fresh with no failing runs

## Result

`B4.012-M3a-E3a-R1` is complete as a lint-only recovery package.

It closed the three ruff issues without changing assertion semantics and without widening the repository-hygiene docs truth scope.
