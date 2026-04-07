# Test Route - API 路由测试

> **补充规范说明**:
> 本文件是特定工具、代理、命令、技能、工作流或规则的局部执行提示，不是仓库共享规则的唯一事实来源。
> 涉及项目治理、审批门禁、共享红线或主线口径时，应优先遵循 `architecture/STANDARDS.md`；执行流程与协作约束再参考根目录 `AGENTS.md`。


测试指定 API 路由的完整流程（认证、授权、错误处理）。

## 测试内容

1. 认证检查 - 未认证用户被拒绝
2. 授权检查 - 权限不足被拒绝
3. 正常流程 - 有效请求正确响应
4. 错误处理 - 边界情况和异常处理

## 使用示例

```bash
# 测试单个路由
/test-route /api/users/login

# 调用项目脚本（如果存在）
scripts/test-auth-route.js
```

与 auth-route-tester agent 配合使用。
