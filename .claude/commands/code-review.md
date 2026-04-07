# Code Review - 代码架构审查

> **补充规范说明**:
> 本文件是特定工具、代理、命令、技能、工作流或规则的局部执行提示，不是仓库共享规则的唯一事实来源。
> 涉及项目治理、审批门禁、共享红线或主线口径时，应优先遵循 `architecture/STANDARDS.md`；执行流程与协作约束再参考根目录 `AGENTS.md`。


触发 code-architecture-reviewer agent 进行完整代码审查。

## 检查内容

1. 设计模式和 SOLID 原则
2. 安全漏洞（SQL注入、XSS、认证问题等）
3. 性能问题和可优化点
4. 可维护性和代码质量

## 使用示例

```bash
# 审查整个项目
/code-review

# 或审查特定目录
/code-review src/routes/
```

将调用 code-architecture-reviewer agent 生成详细审查报告。
