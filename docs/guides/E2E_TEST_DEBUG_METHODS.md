# E2E测试调试方法与实战指南

## 目录

1. [测试运行方法](#测试运行方法)
2. [错误识别技术](#错误识别技术)
3. [常见问题与解决方案](#常见问题与解决方案)
4. [调试工作流程](#调试工作流程)
5. [实战案例：认证问题排查](#实战案例认证问题排查)

---

## 测试运行方法

### 基础命令

```bash
# 运行所有E2E测试
npx playwright test tests/e2e/

# 运行特定测试文件
npx playwright test tests/e2e/auth.spec.ts

# 运行特定测试用例（通过grep过滤）
npx playwright test tests/e2e/auth.spec.ts -g "管理员账号登录成功"

# 以有头模式运行（可以看到浏览器）
npx playwright test tests/e2e/auth.spec.ts --headed

# 以调试模式运行
npx playwright test tests/e2e/auth.spec.ts --debug

# 指定浏览器运行
npx playwright test tests/e2e/auth.spec.ts --project=chromium
```

### 测试报告查看

```bash
# 查看HTML报告
npx playwright show-report

# 查看测试结果摘要
npx playwright test tests/e2e/auth.spec.ts --reporter=line
```

---

## 错误识别技术

### 1. 查看错误上下文 (Error Context)

Playwright会为每个失败的测试生成错误上下文文件：

```bash
# 错误上下文文件位置
test-results/<test-name>/error-context.md
```

**示例内容**：
```yaml
# Page snapshot
- generic [active] [ref=e1]:
  - generic [ref=e4]:
    - heading "MyStocks 登录" [level=1]
    - paragraph: 量化交易数据管理系统
  - alert [ref=e46]:
    - paragraph: 未授权,但已禁用登录要求
    - paragraph: Request failed with status code 401
```

### 2. 查看测试截图

```bash
# 失败测试的截图
test-results/<test-name>/test-failed-1.png
```

### 3. 查看测试视频

```bash
# 测试执行过程视频
test-results/<test-name>/video.webm
```

### 4. 查看PM2日志

```bash
# 查看后端日志
pm2 logs mystocks-backend --lines 50

# 实时监控日志
pm2 logs mystocks-backend
```

### 5. 使用curl直接测试API

```bash
# 测试登录端点
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  -v 2>&1 | python3 -m json.tool
```

---

## 常见问题与解决方案

### 问题1: CSRF认证保护阻塞

**症状**：
```
Error: 403 Forbidden
Detail: CSRF token validation failed
```

**识别方法**：
1. 查看后端日志：`pm2 logs mystocks-backend`
2. 搜索CSRF相关错误：`pm2 logs mystocks-backend | grep -i csrf`

**解决方案**：

修改 `web/backend/app/main.py` 的CSRF中间件：

```python
@app.middleware("http")
async def csrf_protection_middleware(request: Request, call_next):
    """CSRF保护中间件"""
    # 检查是否为测试环境
    is_testing_environment = os.getenv("ENVIRONMENT", "development") == "test"

    # 对于修改操作，检查CSRF token
    if request.method in ["POST", "PUT", "PATCH", "DELETE"] and not is_testing_environment:
        # CSRF验证逻辑
        ...
    return await call_next(request)
```

在 `.env` 文件中添加：
```bash
ENVIRONMENT=test
```

### 问题2: 前端API端点路径错误

**症状**：
```
Error: 404 Not Found
Request URL: http://localhost:8000/api/auth/login
```

**识别方法**：
1. 查看浏览器Network面板
2. 查看错误上下文中的请求URL
3. 使用curl测试端点是否存在

**解决方案**：

修改 `web/frontend/src/api/index.js`：

```javascript
// 错误的路径
export const authApi = {
  login(username, password) {
    return request.post('/auth/login', { username, password })
  }
}

// 正确的路径
export const authApi = {
  login(username, password) {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    return request.post('/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  }
}
```

### 问题3: 请求格式不匹配

**症状**：
```
Error: 422 Unprocessable Entity
Detail: username or password field required
```

**识别方法**：
1. 查看后端日志中的请求数据
2. 检查后端API文档（Swagger）：`http://localhost:8000/docs`
3. 确认API期望的Content-Type

**解决方案**：

后端使用 `OAuth2PasswordRequestForm`，需要form-encoded格式：

```javascript
// ❌ 错误：发送JSON
return request.post('/v1/auth/login', {
  username: username,
  password: password
})

// ✅ 正确：发送form-encoded数据
const formData = new URLSearchParams()
formData.append('username', username)
formData.append('password', password)
return request.post('/v1/auth/login', formData, {
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
})
```

### 问题4: Mock认证密码配置缺失

**症状**：
```
Database authentication failed (will use fallback mock data)
Login failed (returns None)
```

**识别方法**：
1. 直接运行认证测试：
```python
from app.core.security import authenticate_user
user = authenticate_user('admin', 'admin123')
print(user)  # 输出: None
```

2. 查看配置文件：
```bash
grep -i "ADMIN_INITIAL_PASSWORD" web/backend/app/core/config.py
```

**解决方案**：

在 `.env` 文件中添加：
```bash
ADMIN_INITIAL_PASSWORD=admin123
```

重启后端服务：
```bash
pm2 restart mystocks-backend
```

### 问题5: 后端响应格式不匹配

**症状**：
前端显示"登录失败"，但后端返回200 OK

**识别方法**：
1. 使用curl测试API，查看实际响应格式
2. 检查前端store的响应解析逻辑

**解决方案**：

前端期望的格式：
```json
{
  "success": true,
  "data": {
    "token": "...",
    "user": {...}
  }
}
```

修改后端 `web/backend/app/api/auth.py`：

```python
# ❌ 错误的响应格式
@router.post("/login", response_model=Token)
async def login_for_access_token(...):
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {...}
    }

# ✅ 正确的响应格式
@router.post("/login")
async def login_for_access_token(...):
    return create_success_response(
        data={
            "token": access_token,  # 注意是 token 不是 access_token
            "token_type": "bearer",
            "user": {...}
        },
        message="登录成功"
    )
```

### 问题6: 页面路由404错误

**症状**：
```
Page snapshot:
  - paragraph: "404"
  - paragraph: 抱歉,您访问的页面不存在
```

**识别方法**：
1. 查看错误上下文中的页面快照
2. 检查当前URL是否正确

**解决方案**：

检查前端路由配置：
```bash
grep -r "backtest" web/frontend/src/router/
```

修正页面对象URL：
```typescript
// ❌ 错误的URL
this.url = `${baseUrl}/backtest-analysis`;

// ✅ 正确的URL
this.url = `${baseUrl}/strategy-hub/backtest`;
```

---

## 调试工作流程

### 标准调试流程

```
┌─────────────────┐
│  运行E2E测试    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     是     ┌─────────────────┐
│  测试是否通过？  ├──────────►│   完成测试      │
└────────┬────────┘           └─────────────────┘
         │ 否
         ▼
┌─────────────────┐
│ 查看错误上下文   │
│ (error-context) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  确定错误类型   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐  ┌───────┐
│前端   │  │后端   │
│错误   │  │错误   │
└───┬───┘  └───┬───┘
    │          │
    ▼          ▼
┌───────┐  ┌───────┐
│修复   │  │修复   │
│前端   │  │后端   │
└───┬───┘  └───┬───┘
    │          │
    └────┬─────┘
         ▼
┌─────────────────┐
│  重启相关服务   │
│ (pm2 restart)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  重新运行测试   │
└─────────────────┘
```

### 快速定位问题的技巧

1. **先看日志，再看代码**
   ```bash
   # 后端日志
   pm2 logs mystocks-backend --lines 100

   # 前端日志（浏览器Console）
   # 打开DevTools → Console标签
   ```

2. **使用curl快速验证API**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123" -v
   ```

3. **查看API文档确认接口定义**
   ```
   http://localhost:8000/docs
   ```

4. **逐步缩小测试范围**
   ```bash
   # 先运行单个测试
   npx playwright test tests/e2e/auth.spec.ts -g "测试名称" --headed

   # 再运行整个测试套件
   npx playwright test tests/e2e/auth.spec.ts
   ```

5. **使用调试模式暂停执行**
   ```bash
   npx playwright test tests/e2e/auth.spec.ts --debug
   # 可以逐步执行，查看每个步骤
   ```

---

## 实战案例：认证问题排查

### 问题描述

E2E认证测试全部失败，用户无法登录系统。

### 排查过程

#### 第1步：查看错误上下文

```bash
cat test-results/auth-*/error-context.md
```

发现：
- 用户名和密码正确填充
- 页面显示"未授权,但已禁用登录要求"
- 后端返回401错误

#### 第2步：检查后端日志

```bash
pm2 logs mystocks-backend | grep -i "auth\|login\|401"
```

发现：
```
Database authentication failed (will use fallback mock data)
401: 用户名或密码错误
```

#### 第3步：直接测试API

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" -v
```

发现：
- 返回401错误
- 但用户名密码都是正确的

#### 第4步：检查配置文件

```bash
grep -i "ADMIN_INITIAL_PASSWORD" .env web/backend/app/core/config.py
```

发现：
- `.env`中没有`ADMIN_INITIAL_PASSWORD`配置
- `config.py`中默认值为空字符串

#### 第5步：修复配置

在`.env`中添加：
```bash
ADMIN_INITIAL_PASSWORD=admin123
```

重启后端：
```bash
pm2 restart mystocks-backend
```

#### 第6步：验证修复

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | python3 -m json.tool
```

返回：
```json
{
  "success": true,
  "data": {
    "token": "...",
    "user": {...}
  }
}
```

#### 第7步：运行E2E测试验证

```bash
npx playwright test tests/e2e/auth.spec.ts -g "管理员账号登录成功"
```

结果：✅ **3个测试全部通过！**

### 完整修复清单

1. ✅ **CSRF保护**：修改`main.py`，测试环境禁用CSRF
2. ✅ **前端API路径**：修改`api/index.js`，使用`/v1/auth/*`
3. ✅ **请求格式**：使用`URLSearchParams`发送form-encoded数据
4. ✅ **密码配置**：在`.env`中添加`ADMIN_INITIAL_PASSWORD=admin123`
5. ✅ **响应格式**：修改`auth.py`，返回`APIResponse`格式

---

## 总结

### 关键原则

1. **分层排查**：从前端 → 后端 → 数据库，逐步定位问题
2. **日志优先**：先看日志，再看代码
3. **工具辅助**：善用curl、Swagger文档、浏览器DevTools
4. **小步验证**：每次修复后立即验证，不要累积太多修改

### 常用命令速查

```bash
# 运行测试
npx playwright test tests/e2e/auth.spec.ts -g "关键词" --headed

# 查看日志
pm2 logs mystocks-backend --lines 50

# 测试API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" -v

# 重启服务
pm2 restart mystocks-backend

# 查看报告
npx playwright show-report
```

### 文档参考

- Playwright官方文档：https://playwright.dev
- FastAPI文档：http://localhost:8000/docs
- 项目E2E测试框架：`tests/e2e/README.md`

---

**文档版本**: v1.0
**创建时间**: 2025-12-31
**作者**: Test CLI
**相关文档**: TASK.md, E2E_TEST_EXECUTION_REPORT.md
