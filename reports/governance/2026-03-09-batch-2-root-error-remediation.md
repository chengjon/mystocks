# Batch 2 Root Error Remediation Report

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


- Date: `2026-03-09`
- Worktree: `dev-repo-hygiene-b1`
- Change: `integrate-repository-hygiene`

## Summary

- Goal: clear the first bounded batch of root-level governance `error` findings.
- Before remediation:
  - `errors: 2`
  - `warnings: 20`
  - root runtime artifacts:
    - `test_timing.csv`
    - `__pycache__/`
- After remediation:
  - `errors: 0`
  - `warnings: 20`

## Root Cause

- Targeted `pytest` runs under `tests/` resolved `rootdir` to `tests/pytest.ini`, so the repository-root `conftest.py` hooks were not active.
- Runtime artifact governance only existed in the repository-root `conftest.py`, which left `pytest_timing` writing `test_timing.csv` into the repository root during `pytest -o addopts=''`.
- `tests/unit/scripts/test_pytest_runtime_artifacts.py` imported the repository-root `conftest.py` as a normal module, which created a root `__pycache__/`.

## Remediation

- Extracted runtime artifact helpers into `tests/pytest_runtime_artifacts.py`.
- Wired the active `tests/conftest.py` hooks to:
  - canonicalize timing output to `var/reports/test_timing.csv`
  - clean root runtime artifacts during `pytest_sessionfinish`
  - clean root runtime artifacts again during `pytest_unconfigure`
- Updated `tests/unit/scripts/test_pytest_runtime_artifacts.py` to import the shared helper module instead of importing the repository-root `conftest.py`.
- Enabled `sys.dont_write_bytecode = True` in both conftest entrypoints to reduce stray bytecode output.

## Evidence

- `pytest tests/unit/scripts/test_pytest_runtime_artifacts.py -q -o addopts=''`
- `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py -q -o addopts=''`
- `openspec validate integrate-repository-hygiene --strict`
- `python scripts/maintenance/check_structure.py --format text`
