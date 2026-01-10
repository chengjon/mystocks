# CSRF Protection Capability Spec (Delta)

## MODIFIED Requirements

### Requirement: 测试环境可以禁用CSRF保护 (MUST)

**ID**: RQ-CSRF-001
**Priority**: High
**Status**: Modified

**Description**:
为了支持E2E测试自动化，测试环境可以禁用CSRF保护。生产环境MUST保持CSRF保护启用。

**Rationale**:
E2E测试需要在自动化环境中运行，CSRF保护会阻止测试请求。测试环境禁用CSRF是行业通行做法。

**Original Requirement**:
所有环境（生产、开发、测试）都MUST启用CSRF保护。

**Modified Requirement**:
生产环境和开发环境MUST启用CSRF保护，测试环境可以禁用CSRF保护。

#### Scenario: 测试环境禁用CSRF

**Given**:
- 环境变量 `TESTING=true`
- 后端配置文件 `web/backend/.env.testing` 设置了 `CSRF_ENABLED=false`

**When**:
- 后端服务启动
- E2E测试发送请求到后端API

**Then**:
- CSRF中间件不检查CSRF token
- E2E测试请求正常通过
- 生产环境CSRF保护保持启用

**Verification Steps**:
1. 检查 `web/backend/app/core/config.py` 包含 `testing` 和 `csrf_enabled` 配置项
2. 检查 `web/backend/.env.testing` 设置了 `TESTING=true` 和 `CSRF_ENABLED=false`
3. 启动后端服务，验证CSRF中间件未启用（检查日志或中间件列表）
4. 运行E2E测试，验证通过率从85.7%提升到≥95%

#### Scenario: 生产环境CSRF保持启用

**Given**:
- 环境变量 `TESTING=false` 或未设置
- 后端使用生产配置

**When**:
- 后端服务启动
- 用户发送POST/PUT/DELETE请求

**Then**:
- CSRF中间件检查CSRF token
- 无token的请求返回403 Forbidden
- 用户MUST先获取CSRF token（通过 `/api/auth/csrf-token`）

**Verification Steps**:
1. 检查生产环境配置文件不包含 `TESTING=true`
2. 启动生产环境后端，验证CSRF中间件已启用
3. 发送无CSRF token的POST请求，验证返回403
4. 发送有CSRF token的POST请求，验证请求成功

---

### Requirement: E2E测试提供认证工具函数 (MUST)

**ID**: RQ-CSRF-002
**Priority**: High
**Status**: Added

**Description**:
E2E测试框架MUST提供认证工具函数，自动处理登录和token获取，简化测试编写。

**Rationale**:
140+个E2E测试需要认证，每个测试手动处理认证逻辑会导致代码重复和维护困难。

#### Scenario: 使用认证工具函数登录

**Given**:
- E2E测试需要认证
- 测试框架提供了 `loginAndGetCsrfToken()` 工具函数

**When**:
- 测试在 `beforeEach` 中调用工具函数:
  ```typescript
  test.beforeEach(async ({ page }) => {
    await loginAndGetCsrfToken(page, 'admin', 'admin123')
  })
  ```

**Then**:
- 工具函数自动完成登录流程
- 工具函数获取JWT token并存储到localStorage
- 工具函数设置后续请求的认证header
- 测试可以直接访问需要认证的页面

**Verification Steps**:
1. 检查 `tests/e2e/helpers/auth.ts` 包含 `loginAndGetCsrfToken()` 函数
2. 检查函数实现包括: 访问登录页 → 填写表单 → 提交 → 获取token → 存储到localStorage
3. 编写示例测试使用该函数，验证测试能正常通过
4. 检查token正确存储在localStorage中

#### Scenario: 测试不同权限场景

**Given**:
- 系统支持管理员和普通用户两种角色
- 测试需要验证不同角色的权限

**When**:
- 测试使用不同的用户登录:
  ```typescript
  test('admin can delete strategy', async ({ page }) => {
    await loginAndGetCsrfToken(page, 'admin', 'admin123')
    // ... 测试管理员功能
  })

  test('user cannot delete strategy', async ({ page }) => {
    await loginAndGetCsrfToken(page, 'user', 'user123')
    // ... 测试普通用户权限
  })
  ```

**Then**:
- 管理员测试能执行所有操作
- 普通用户测试被拒绝（返回403或显示权限不足提示）
- 测试正确验证了权限控制逻辑

**Verification Steps**:
1. 编写两个测试用例，分别测试管理员和普通用户权限
2. 验证管理员测试能正常执行删除操作
3. 验证普通用户测试被正确拒绝
4. 检查测试日志包含正确的权限验证信息

---

## Related Capabilities

- **code-quality**: Pre-commit hooks检查认证工具函数代码质量
- **e2e-testing**: E2E测试依赖认证工具函数提高通过率
- **session-management**: Session持久化与认证工具函数配合使用
