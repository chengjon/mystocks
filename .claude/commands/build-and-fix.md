# Build and Fix - 构建并修复错误

> **补充规范说明**:
> 本文件是特定工具、代理、命令、技能、工作流或规则的局部执行提示，不是仓库共享规则的唯一事实来源。
> 涉及项目治理、审批门禁、共享红线或主线口径时，应优先遵循 `architecture/STANDARDS.md`；执行流程与协作约束再参考根目录 `AGENTS.md`。


运行完整构建流程，检测所有 TypeScript/编译错误并自动修复。

## 任务流程

1. 运行项目构建命令
2. 收集所有编译错误
3. 如果错误 ≥5，调用 build-error-resolver agent
4. 系统化修复每个错误
5. 重新构建验证

## 使用示例

```bash
# 当 Stop hook 检测到大量错误时
/build-and-fix

# 或手动触发完整构建检查
/build-and-fix
```

这是 Reddit 案例"6个月零错误"的核心工具。
