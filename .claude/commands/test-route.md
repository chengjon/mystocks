# Test Route - API 路由测试

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
