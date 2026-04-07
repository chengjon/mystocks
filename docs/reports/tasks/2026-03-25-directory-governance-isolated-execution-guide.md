# 2026-03-25 Directory Governance Isolated Execution Guide

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## Purpose

在当前主工作区已有大量无关 staged 变更的情况下，安全执行本轮目录治理收敛的两个微批次，而不污染现有 index。

## Current Reality

- 当前主工作区已有 `499` 个 staged 文件。
- 因此不要在当前工作区直接执行本轮批次的 `git add` / `git commit`。
- 推荐做法是在独立 linked worktree 中应用 patch，再按 `scope="staged"` 做微批次验证。

## Prepared Inputs

- Batch A file list:
  - [2026-03-25-directory-governance-batch-a-files.txt](./2026-03-25-directory-governance-batch-a-files.txt)
- Batch B file list:
  - [2026-03-25-directory-governance-batch-b-files.txt](./2026-03-25-directory-governance-batch-b-files.txt)
- Staging plan:
  - [2026-03-25-directory-governance-batch-staging-plan.md](./2026-03-25-directory-governance-batch-staging-plan.md)

Patch exports already generated:

```text
/tmp/directory-governance-batch-a.patch
/tmp/directory-governance-batch-b.patch
```

## Recommended Flow

### Batch A

1. 创建干净工作树：

```bash
git worktree add -b chore/directory-governance-batch-a ../mystocks_spec-governance-batch-a main
```

2. 进入工作树并应用 patch：

```bash
cd ../mystocks_spec-governance-batch-a
git apply /tmp/directory-governance-batch-a.patch
```

3. 按文件清单暂存：

```bash
xargs -d '\n' git add -- < /opt/claude/mystocks_spec/docs/reports/tasks/2026-03-25-directory-governance-batch-a-files.txt
```

4. 运行验证：

```bash
pytest tests/unit/governance/test_function_tree_doc_sync.py \
  tests/unit/scripts/test_check_structure_policy.py \
  tests/unit/scripts/test_docs_indexer.py \
  tests/unit/scripts/test_pytest_runtime_artifacts.py \
  tests/unit/scripts/test_repository_hygiene_paths.py \
  tests/unit/core/test_docker_root_compatibility.py \
  -q --no-cov -o tdd_guard_project_root=/opt/claude/mystocks_spec-governance-batch-a \
  --timing-file=/tmp/test_timing.csv

python -m scripts.maintenance.check_structure --format text .

bash scripts/tree-lint.sh
```

5. 在 AI 会话中对该工作树执行：

```text
gitnexus_detect_changes({scope: "staged"})
```

6. 提交：

```bash
git commit -m "chore(governance): tighten root hygiene and local-only config rules"
```

### Batch B

1. 创建干净工作树：

```bash
git worktree add -b docs/directory-governance-batch-b ../mystocks_spec-governance-batch-b main
```

2. 进入工作树并应用 patch：

```bash
cd ../mystocks_spec-governance-batch-b
git apply /tmp/directory-governance-batch-b.patch
```

3. 按文件清单暂存：

```bash
xargs -d '\n' git add -- < /opt/claude/mystocks_spec/docs/reports/tasks/2026-03-25-directory-governance-batch-b-files.txt
```

4. 运行验证：

```bash
pytest tests/unit/governance/test_function_tree_doc_sync.py \
  tests/unit/scripts/test_check_structure_policy.py \
  tests/unit/scripts/test_docs_indexer.py \
  tests/unit/scripts/test_pytest_runtime_artifacts.py \
  tests/unit/scripts/test_repository_hygiene_paths.py \
  tests/unit/core/test_docker_root_compatibility.py \
  -q --no-cov -o tdd_guard_project_root=/opt/claude/mystocks_spec-governance-batch-b \
  --timing-file=/tmp/test_timing.csv

python -m scripts.maintenance.check_structure --format text .

bash scripts/tree-lint.sh
```

5. 在 AI 会话中对该工作树执行：

```text
gitnexus_detect_changes({scope: "staged"})
```

6. 提交：

```bash
git commit -m "docs(cleanup): archive legacy directory-organization drafts"
```

## Notes

- 这两个 patch 是从当前主工作区的未提交差异导出的，不会自动带入你当前已有的 `499` 个 staged 文件。
- 如果 `git apply` 失败，说明主工作区和目标 worktree 的基础状态已经偏离，需要重新导出 patch。
- Batch B 会删除：
  - `docs/guides/ARTDECO_COMPONENT_GUIDE.md`
  - `docs/guides/ARTDECO_MASTER_INDEX.md`
- Batch A 会删除：
  - `tui.json`

## Why This Works

- 主工作区继续保留当前复杂 index，不做破坏性操作。
- 每个 linked worktree 都从 `main` 起步，天然拥有干净的 staged 视角。
- `gitnexus_detect_changes({scope: "staged"})` 在该场景下才能真正反映当前微批次，而不是整仓脏工作区噪音。
