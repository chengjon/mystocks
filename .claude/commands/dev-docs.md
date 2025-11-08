# Dev Docs - 创建开发文档系统

创建 Dev Docs 三文档系统，用于持久化项目上下文和任务跟踪。

## 任务

1. 在 `.claude/dev/active/<task-name>/` 创建目录
2. 创建以下文件：
   - `plan.md` - 战略目标和架构决策
   - `context.md` - 关键文件、依赖、注意事项（<200行）
   - `tasks.md` - 任务清单（已完成/进行中/待办）

## 使用示例

```bash
# 自动根据当前任务创建 dev docs
/dev-docs
```

这将生成完整的开发文档结构，供后续会话恢复上下文使用。
