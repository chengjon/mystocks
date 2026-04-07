# 2026-03-25 Directory Governance Batch Staging Plan

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## Goal

在不污染当前已有 `499` 个 staged 文件的前提下，为本轮目录治理收敛整理出一份可独立执行的暂存清单。

## Important Constraint

- 当前仓库已经存在大量与本轮无关的 staged 变更。
- 因此本清单只提供“建议暂存范围”，不直接操作现有 index。
- 若要得到准确的 GitNexus 微批次风险结果，必须在独立、干净的 staged 视角下运行：
  - `git add <本批次文件>`
  - `gitnexus_detect_changes({scope: "staged"})`

## Recommended Split

### Batch A: Governance and Runtime Hygiene

文件清单：

- [2026-03-25-directory-governance-batch-a-files.txt](./2026-03-25-directory-governance-batch-a-files.txt)

建议纳入：

```text
.gitignore
AGENTS.md
CLAUDE.md
governance/mainline/policies/directory-structure.yaml
scripts/hooks/check_directory_structure.py
scripts/maintenance/check_structure.py
scripts/tree-lint.sh
pytest.ini
mypy.ini
pyproject.toml
tests/pytest_runtime_artifacts.py
tests/run_all_tests.py
scripts/tests/run_e2e_tests.sh
tests/unit/scripts/test_check_structure_policy.py
tests/unit/scripts/test_pytest_runtime_artifacts.py
tests/unit/scripts/test_repository_hygiene_paths.py
tui.json
```

建议命令：

```bash
git add .gitignore \
  AGENTS.md \
  CLAUDE.md \
  governance/mainline/policies/directory-structure.yaml \
  scripts/hooks/check_directory_structure.py \
  scripts/maintenance/check_structure.py \
  scripts/tree-lint.sh \
  pytest.ini \
  mypy.ini \
  pyproject.toml \
  tests/pytest_runtime_artifacts.py \
  tests/run_all_tests.py \
  scripts/tests/run_e2e_tests.sh \
  tests/unit/scripts/test_check_structure_policy.py \
  tests/unit/scripts/test_pytest_runtime_artifacts.py \
  tests/unit/scripts/test_repository_hygiene_paths.py \
  tui.json
```

等价写法：

```bash
xargs -d '\n' git add -- < docs/reports/tasks/2026-03-25-directory-governance-batch-a-files.txt
```

建议提交信息：

```text
chore(governance): tighten root hygiene and local-only config rules
```

说明：

- `tui.json` 在此批次中是删除项。
- 这一批的核心目标是：
  - 根目录运行产物与缓存收口
  - `opencode.json` / `tui.json` local-only 化
  - `.aider.*` 退役后规则固化
  - `check_structure` / `tree-lint` / policy / GitNexus dirty-worktree 口径统一

### Batch B: Directory-Organization Docs Convergence

文件清单：

- [2026-03-25-directory-governance-batch-b-files.txt](./2026-03-25-directory-governance-batch-b-files.txt)

建议纳入：

```text
docs/INDEX.md
docs/reports/cleanup/INDEX.md
docs/reports/cleanup/directory-organization/INDEX.md
docs/reports/cleanup/directory-organization/legacy/
docs/reports/INDEX.md
docs/reports/reviews/DIRECTORY_ORGANIZATION_REVIEW.md
docs/reports/openspec_audit_summary.md
docs/guides/ai-tools/OMO_SETUP_GUIDE.md
docs/guides/ai-tools/OpenCode生产级配置与固化指南.md
docs/guides/documentation/超长文档拆分办法.md
docs/guides/ARTDECO_COMPONENT_GUIDE.md
docs/guides/ARTDECO_MASTER_INDEX.md
docs/reports/tasks/2026-03-25-directory-governance-batch-staging-plan.md
```

说明：

- 这批包含：
  - 删除根层 ArtDeco redirect 文件
  - 将 `directory-organization/` 历史草案降到 `legacy/`
  - 更新上层索引到新路径
- 同时纳入这轮已经稳定的文档口径修正：
  - `OMO_SETUP_GUIDE.md`
  - `OpenCode生产级配置与固化指南.md`
  - `超长文档拆分办法.md`
  - `DIRECTORY_ORGANIZATION_REVIEW.md`
- 再附带记录本次批次拆分方法的 staging plan 文档本身

建议命令：

```bash
git add docs/INDEX.md \
  docs/reports/cleanup/INDEX.md \
  docs/reports/cleanup/directory-organization/INDEX.md \
  docs/reports/cleanup/directory-organization/legacy \
  docs/reports/INDEX.md \
  docs/reports/reviews/DIRECTORY_ORGANIZATION_REVIEW.md \
  docs/reports/openspec_audit_summary.md \
  docs/guides/ai-tools/OMO_SETUP_GUIDE.md \
  'docs/guides/ai-tools/OpenCode生产级配置与固化指南.md' \
  'docs/guides/documentation/超长文档拆分办法.md' \
  docs/guides/ARTDECO_COMPONENT_GUIDE.md \
  docs/guides/ARTDECO_MASTER_INDEX.md \
  docs/reports/tasks/2026-03-25-directory-governance-batch-staging-plan.md
```

等价写法：

```bash
xargs -d '\n' git add -- < docs/reports/tasks/2026-03-25-directory-governance-batch-b-files.txt
```

建议提交信息：

```text
docs(cleanup): archive legacy directory-organization drafts
```

## Validation Commands

在任一批次暂存后，建议运行：

```bash
pytest tests/unit/governance/test_function_tree_doc_sync.py \
  tests/unit/scripts/test_check_structure_policy.py \
  tests/unit/scripts/test_docs_indexer.py \
  tests/unit/scripts/test_pytest_runtime_artifacts.py \
  tests/unit/scripts/test_repository_hygiene_paths.py \
  tests/unit/core/test_docker_root_compatibility.py \
  -q --no-cov -o tdd_guard_project_root=/opt/claude/mystocks_spec \
  --timing-file=/tmp/test_timing.csv

python -m scripts.maintenance.check_structure --format text .

bash scripts/tree-lint.sh
```

若 staged 视角干净，再执行：

```text
gitnexus_detect_changes({scope: "staged"})
```

## Current Observation

- 本轮稳定治理改动的文件级范围共有 `22` 个路径差异。
- 当前全仓 staged 已有 `499` 个文件，因此 **不应** 在当前 index 上直接把本批次与既有 staged 混合解释成同一微批次。

## Practical Next Step

如果要真正执行这两个批次，建议先在当前工作区外建立一个干净的提交视角，再按上面两批次逐个 `git add`。

若继续留在当前工作区操作，也应先确认现有 `499` 个 staged 文件如何处理，否则 `scope="staged"` 仍然会混入它们。

独立工作树执行说明：

- [2026-03-25-directory-governance-isolated-execution-guide.md](./2026-03-25-directory-governance-isolated-execution-guide.md)
