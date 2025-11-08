# Dev Docs - Active Tasks

此目录包含所有活动任务的开发文档。

## 目录结构

每个任务一个子目录，包含三个核心文件：

```
<task-name>/
├── plan.md       - 战略目标和架构决策
├── context.md    - 关键上下文（<200行）
└── tasks.md      - 任务清单
```

## 使用方法

### 创建新任务文档

```bash
/dev-docs
```

Claude 会自动创建任务目录和三个文件。

### 更新任务文档

```bash
/dev-docs-update
```

在会话过程中或结束时更新文档。

### 自动恢复上下文

当新会话启动时，SessionStart hook 会自动读取 `context.md` 并注入到 Claude 上下文中，实现跨会话上下文恢复。

## Reddit 案例最佳实践

1. **context.md 必须精简** - 控制在 200 行以内，只记录最关键信息
2. **定期更新** - 每次重大进展后更新 tasks.md
3. **PreCompact 保存** - 压缩前自动保存，避免上下文丢失
4. **多任务并行** - 可以同时维护多个任务的文档

## 当前活动任务

- `example-task/` - 示例任务（可删除）
