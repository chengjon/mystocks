# Root Reviews and Archived Convergence Report

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


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
