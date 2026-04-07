# Task Artifacts Workflow Exception Report

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


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
