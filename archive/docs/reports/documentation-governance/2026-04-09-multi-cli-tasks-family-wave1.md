# Multi-CLI Tasks Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/multi-cli-tasks/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/multi-cli-tasks/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/multi-cli-tasks/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 之前把 registration、task pool、worker/main workflow、Mongo coordination、branch/worktree、Maestro/Symphony、prompt strategy、config 与历史提案材料全部平铺暴露
- 该 family 仍承担较强 operational duty，但不需要让所有子主题在根导航平级展示

## Changes

- 将 `docs/guides/multi-cli-tasks/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Multi Cli Tasks family 的根导航
- 根导航现在优先保留：
  - `guides/multi-cli-tasks/INDEX.md`
  - `guides/multi-cli-tasks/BRANCH_STRATEGY.md`
  - `guides/multi-cli-tasks/CLI_REGISTRATION_GUIDE.md`
  - `guides/multi-cli-tasks/CLI_WORKFLOW_GUIDE.md`
  - `guides/multi-cli-tasks/MAIN_CLI_WORKFLOW_STANDARDS.md`
  - `guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md`
  - `guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md`
  - `guides/multi-cli-tasks/MULTI_CLI_WORKTREE_MANAGEMENT.md`
  - `guides/multi-cli-tasks/TASK_POOL_USAGE_GUIDE.md`
  - `Supporting Guides` -> `guides/multi-cli-tasks/INDEX.md`
- 将 Maestro/Symphony、prompt、config、roles、optimization proposal 与其他历史 helper docs 收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - 无新增 canonical trunk；该 family 继续保持 `supporting`
- family transition index:
  - `docs/guides/multi-cli-tasks/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 Maestro/Symphony、prompt strategy、config、roles、optimization 与历史 helper leaf docs 的直接暴露
- retention duty:
  - `CLI_ROLES_REFERENCE.md`
  - `CONFIG_SYSTEM_GUIDE.md`
  - `GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md`
  - `MAESTRO_QUICK_START.md`
  - `MAESTRO_SUMMARY.md`
  - `MULTI_CLI_COLLABORATION_METHOD.md`
  - `MULTI_CLI_OPTIMIZATION_PROPOSAL.md`
  - `MULTI_CLI_PROMPT_STRATEGIES.md`
  - `SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`
  - `worktree.md`
  - 以上文档继续保留为 specialized/reference docs

## Expected Effect

- 根导航优先暴露当前仍有较高直接使用价值的 registration、task pool、worker/main workflow、Mongo coordination、worktree 与 branch runbook
- Maestro/Symphony、prompt、config、roles 与历史方法/提案材料不再与主入口平级暴露，但仍可通过 family index 进入
- 该 family 后续若继续治理，应围绕 retained specialized references 的实际入链下降情况做小批次处理，而不是 subtree-wide 收缩
