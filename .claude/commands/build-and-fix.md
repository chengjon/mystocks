# Build and Fix - 构建并修复错误

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
