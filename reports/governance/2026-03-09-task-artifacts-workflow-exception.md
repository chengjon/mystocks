# Task Artifacts Workflow Exception Report

- Date: `2026-03-09`
- Worktree: `dev-repo-hygiene-b1`
- Change: `integrate-repository-hygiene`

## Summary

- Goal: reclassify root `TASK.md` and `TASK-REPORT.md` from migration debt to workflow-approved exceptions.
- Before remediation:
  - `errors: 0`
  - `warnings: 8`
- After remediation:
  - `errors: 0`
  - `warnings: 6`

## Why

- In this repository, `TASK.md` and `TASK-REPORT.md` are not accidental root clutter.
- They are the formal human/CLI coordination contract for:
  - main CLI task decomposition and assignment
  - worker CLI progress reporting
  - local-first multi-CLI orchestration

## Changes

- Added `root.workflow_exception_files` to `governance/mainline/policies/directory-structure.yaml`.
- Moved `TASK.md` and `TASK-REPORT.md` out of `tolerated_files`.
- Updated `scripts/maintenance/check_structure.py` to skip approved workflow exceptions instead of reporting them as warnings.
- Added regression coverage in `tests/unit/scripts/test_check_structure_policy.py`.
- Added authoritative wording to `docs/guides/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`.

## Evidence

- `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py tests/unit/scripts/test_repository_hygiene_paths.py -q -o addopts=''`
- `openspec validate integrate-repository-hygiene --strict`
- `python scripts/maintenance/check_structure.py --format text`
