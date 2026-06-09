# Hooks Guide Family

> **导航说明**:
> 本文件是 `docs/guides/hooks/` 的 transition index，不是仓库共享规则、当前 trunk map 或当前实现状态的唯一事实来源。
> 若需确认文档系统主干与 reader routing，请优先阅读 [`docs/overview/documentation-system.md`](../../overview/documentation-system.md)；若涉及审批门禁、删除判定或共享治理规则，请回到 [`architecture/STANDARDS.md`](../../../architecture/STANDARDS.md)。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于 hook / workflow 专题说明，不承担仓库级治理 trunk。推荐阅读顺序：

1. [`docs/overview/documentation-system.md`](../../overview/documentation-system.md)
2. [`WEB_DEV_HOOKS_GUIDE.md`](./WEB_DEV_HOOKS_GUIDE.md) 或 [`web-dev-hooks-guide.md`](./web-dev-hooks-guide.md)
3. [`pre_commit_hook_setup_guide.md`](./pre_commit_hook_setup_guide.md)
4. 再按需进入本 family 的诊断、历史分析与补充使用说明

## Active Supporting Guides

- [`WEB_DEV_HOOKS_GUIDE.md`](./WEB_DEV_HOOKS_GUIDE.md)
  - 中文主入口，说明 web-dev hook 追踪、分类与运行时日志约束
- [`web-dev-hooks-guide.md`](./web-dev-hooks-guide.md)
  - 英文主入口，覆盖同主题的英文读者入口
- [`pre_commit_hook_setup_guide.md`](./pre_commit_hook_setup_guide.md)
  - pre-commit 文件大小检查与本地 hook 配置说明

## Retained Specialized References

以下文件继续保留在 `hooks/` family 中，但作为 supporting/reference docs 使用，不应被误读为主入口：

- [`hook-analysis-report.md`](./hook-analysis-report.md)
  - hook 现状分析与问题盘点
- [`hook-optimization-summary.md`](./hook-optimization-summary.md)
  - hook 优化波次总结
- [`hooks使用指南.md`](./hooks使用指南.md)
  - hooks 入门和基础操作说明
- [`hooks详细说明.md`](./hooks详细说明.md)
  - hooks 机制参考
- [`hooks错误处理方法.md`](./hooks错误处理方法.md)
  - 常见问题与排障方法
- [`post_tool_use_hook_error_diagnosis.md`](./post_tool_use_hook_error_diagnosis.md)
  - 一次具体 PostToolUse 错误诊断记录

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只应暴露少量主入口，其余诊断/历史材料统一经由本 index 进入
- 若后续某篇诊断或历史文档的 inbound links 继续下降，再按 bounded batch 单独评估 archive/delete
