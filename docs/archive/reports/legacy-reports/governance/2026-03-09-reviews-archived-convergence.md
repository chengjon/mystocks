# Root Reviews and Archived Convergence Report

- Date: `2026-03-09`
- Worktree: `dev-repo-hygiene-b1`
- Change: `integrate-repository-hygiene`

## Summary

- Goal: eliminate root `reviews/` and root `archived/` lifecycle debt.
- Before remediation:
  - `errors: 0`
  - `warnings: 12`
- After remediation:
  - `errors: 0`
  - `warnings: 8`

## Changes

- Moved root review evidence:
  - `reviews/*.md` → `reports/reviews/*.md`
- Moved root archived legacy tree:
  - `archived/` → `archive/legacy-root-archived/`
- Updated repository hygiene regression tests:
  - `tests/unit/scripts/test_repository_hygiene_paths.py`
- Updated `.gitignore` to allow tracking `reports/reviews/**`.

## Remaining Warnings

- Workflow artifacts:
  - `TASK.md`
  - `TASK-REPORT.md`
- Documentation convergence:
  - `docs/completion_reports/**`
  - `docs/monitoring_reports/**`
  - `docs/phase_reports/**`
  - `docs/test_reports/**`
- Archive convergence:
  - `docs/archive/**`
  - `docs/legacy/**`

## Evidence

- `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py tests/unit/scripts/test_repository_hygiene_paths.py -q -o addopts=''`
- `openspec validate integrate-repository-hygiene --strict`
- `python scripts/maintenance/check_structure.py --format text`
