# Session Management Capability Spec (Delta)

## MODIFIED Requirements

### Requirement: SessionMUST持久化到localStorage (MUST)

**ID**: RQ-SESSION-001
**Priority**: Medium
**Status**: Modified

**Description**:
用户登录后的session信息（token和user）MUST自动保存到localStorage，刷新页面后能自动恢复。

**Rationale**:
当前实现刷新页面后登录状态丢失，用户体验差。MUST实现session持久化。

**Original Requirement**:
Session信息存储在Pinia store中（内存存储）。

**Modified Requirement**:
Session信息MUST同时存储在Pinia store和localStorage中，自动同步和恢复。

#### Scenario: 登录后自动保存session

**Given**:
- 用户访问登录页面 `/login`
- 用户输入用户名和密码

**When**:
- 用户点击"登录"按钮
- 登录API返回token和user信息

**Then**:
- Token自动保存到localStorage（`localStorage.setItem('token', token)`）
- User信息自动保存到localStorage（`localStorage.setItem('user', JSON.stringify(user))`）
- Pinia store状态也更新

**Verification Steps**:
1. 检查 `web/frontend/src/stores/auth.js` 使用Vue的 `watch` API监听token和user变化
2. 检查watch回调中包含 `localStorage.setItem()` 逻辑
3. 手动测试: 登录后打开浏览器DevTools → Application → Local Storage，验证存在token和user
4. 刷新页面，验证登录状态保持

#### Scenario: 刷新页面后自动恢复session

**Given**:
- 用户已登录
- localStorage中存在token和user信息

**When**:
- 用户刷新页面（F5或Ctrl+R）
- 应用启动，Pinia store初始化

**Then**:
- Pinia store从localStorage读取token和user
- 自动验证token有效性（调用 `/api/auth/me`）
- 如果token有效，恢复登录状态
- 如果token无效，清除localStorage并跳转到登录页

**Verification Steps**:
1. 检查 `auth.js` store初始化时从localStorage读取:
   ```javascript
   const token = ref(localStorage.getItem('token') || '')
   const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
   ```
2. 检查调用 `checkAuth()` 验证token有效性
3. 手动测试: 刷新页面后仍能访问需要认证的页面（如 `/dashboard`）
4. 手动测试: 清除localStorage后刷新，自动跳转到登录页

---

### Requirement: Token过期后自动清除session (MUST)

**ID**: RQ-SESSION-002
**Priority**: High
**Status**: Added

**Description**:
当API返回401 Unauthorized时，MUST自动清除localStorage中的session信息，并跳转到登录页。

**Rationale**:
Token过期后session无效，MUST清除本地存储，避免用户使用过期token继续操作。

#### Scenario: Token过期自动登出

**Given**:
- 用户已登录，localStorage中存在token
- Token已过期（2小时有效期）

**When**:
- 用户执行任何API请求（如获取股票列表）
- API返回401 Unauthorized

**Then**:
- Axios响应拦截器捕获401错误
- 自动清除localStorage中的token和user
- 跳转到登录页 `/login?message=登录已过期`
- 显示提示信息"登录已过期，请重新登录"

**Verification Steps**:
1. 检查 `web/frontend/src/api/axios.js` 或类似文件包含响应拦截器:
   ```javascript
   axios.interceptors.response.use(
     response => response,
     error => {
       if (error.response?.status === 401) {
         localStorage.removeItem('token')
         localStorage.removeItem('user')
         router.push('/login?message=登录已过期')
       }
       return Promise.reject(error)
     }
   )
   ```
2. 手动测试: 使用过期token调用API，验证自动登出
3. 检查登录页URL包含 `message=登录已过期` 参数
4. 检查登录页显示提示信息

---

### Requirement: 混合存储策略（httpOnly cookie + localStorage） (MUST)

**ID**: RQ-SESSION-003
**Priority**: Medium
**Status**: Added

**Description**:
敏感认证信息（token）MUST存储在httpOnly cookie中，用户信息MUST存储在localStorage中。

**Rationale**:
httpOnly cookie防止XSS攻击窃取token，localStorage方便前端访问用户信息。

#### Scenario: 登录成功后设置httpOnly cookie

**Given**:
- 用户提交登录表单
- 后端验证成功，返回JWT token

**When**:
- 前端收到登录响应
- 响应包含 `Set-Cookie: token=<jwt>; HttpOnly; Secure; SameSite=Strict`

**Then**:
- 浏览器自动存储token到httpOnly cookie
- 前端JavaScript无法访问cookie（防止XSS窃取）
- 后续API请求自动携带cookie

**Verification Steps**:
1. 检查后端登录接口返回 `Set-Cookie` header
2. 检查cookie包含 `HttpOnly`、`Secure`、`SameSite=Strict` 属性
3. 手动测试: 登录后打开DevTools → Application → Cookies，验证token cookie存在且标记为HttpOnly
4. 尝试在Console中访问 `document.cookie`，验证无法读取token

#### Scenario: localStorage存储用户信息

**Given**:
- 用户登录成功
- 后端返回用户信息（id, username, role, etc.）

**When**:
- 前端接收到用户信息

**Then**:
- 用户信息保存到localStorage（`localStorage.setItem('user', JSON.stringify(user))`）
- 前端可以直接读取用户信息（显示用户名、角色等）
- 刷新页面后用户信息保持

**Verification Steps**:
1. 检查登录成功后localStorage包含user对象
2. 检查user对象包含id、username、role等字段
3. 手动测试: 刷新页面后用户信息仍显示在UI上
4. 手动测试: 登出后localStorage中的user被清除

---

## Related Capabilities

- **csrf-protection**: CSRF token管理与session管理配合
- **e2e-testing**: E2E测试需要处理session持久化
- **type-safety**: Session管理代码需要严格类型检查
