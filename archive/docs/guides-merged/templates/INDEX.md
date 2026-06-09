# Templates Guide Family

> **导航说明**:
> 本文件是 `docs/guides/templates/` 的 transition index，不是仓库共享规则、当前实施口径或唯一模板真相源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及具体执行流程与协作约束，再结合根目录 `AGENTS.md` 与当前实际工作流。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于任务初始化和治理模板参考，不承担仓库级 trunk。推荐阅读顺序：

1. [`INITIALIZATION_PROMPT.md`](./INITIALIZATION_PROMPT.md)
2. 再按需进入任务卡模板和技术债例外模板

## Active Supporting Guides

- [`INITIALIZATION_PROMPT.md`](./INITIALIZATION_PROMPT.md)
  - Frontend CLI 任务初始化模板

## Retained Specialized References

- [`task-card-standard-template.md`](./task-card-standard-template.md)
  - 标准化任务卡模板
- [`tech-debt-exception-template.md`](./tech-debt-exception-template.md)
  - 技术债例外申请模板

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只暴露最常用的初始化模板，其余治理模板统一通过本 index 进入
- 若后续模板入链继续下降，再按 bounded batch 单独评估 archive/delete
