# Dev Docs Update - 更新开发文档

更新 Dev Docs 文件，同步当前会话的进展、决策、待办。

## 任务

1. 更新 `context.md` - 添加新的关键决策和上下文
2. 更新 `tasks.md` - 标记完成的任务，添加新任务
3. 可选：更新 `plan.md` 如果战略方向有变化

## 使用示例

```bash
# 手动触发更新
/dev-docs-update

# 或在 Stop/PreCompact hook 中自动调用
```

在会话结束或即将压缩时调用，确保上下文不丢失。
