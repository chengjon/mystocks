# MyStocks API CSRF 保护启用指南

**指南日期**: 2025-11-30
**优先级**: 🔴 P0-3
**状态**: ✅ 已准备就绪，需要激活
**工作量**: 1 小时

---

## 📋 CSRF 保护现状

### 当前情况
- ✅ **代码已实现**: CSRF 保护中间件已完全编写，位于 `/main.py:192-240`
- ⏳ **状态**: 当前被注释禁用（`#` 符号）
- ✅ **CSRFTokenManager**: 已在 `main.py:43-68` 实现
- ✅ **CSRF token 端点**: `/api/csrf-token` 已实现

### 需要的激活步骤

CSRF 中间件已经准备好，只需要取消注释即可启用。

---

## 🔓 激活 CSRF 保护（手动步骤）

### 步骤 1: 编辑 main.py

打开文件: `/opt/claude/mystocks_spec/web/backend/app/main.py`

定位到 **第 192 行**，找到：

```python
# SECURITY FIX 1.2: CSRF验证中间件 - 已禁用
# @app.middleware("http")
# async def csrf_protection_middleware(request: Request, call_next):
```

修改为：

```python
# SECURITY FIX 1.2: CSRF验证中间件 - 已启用
@app.middleware("http")
async def csrf_protection_middleware(request: Request, call_next):
```

### 步骤 2: 取消注释中间件函数体

将 **第 195-240 行** 的所有 `#` 符号删除（每行开头的注释符号）

修改前：
```python
# async def csrf_protection_middleware(request: Request, call_next):
#     """
#     CSRF保护中间件 - 验证修改操作的CSRF token
#     ...
```

修改后：
```python
async def csrf_protection_middleware(request: Request, call_next):
    """
    CSRF保护中间件 - 验证修改操作的CSRF token
    ...
```

### 步骤 3: 验证代码完整性

确保整个函数是有效的 Python 代码（无前导 `#`）

### 步骤 4: 重启后端服务

```bash
# 停止现有服务
pkill -f "uvicorn"

# 启动后端
cd /opt/claude/mystocks_spec/web/backend
uvicorn app.main:app --reload --port 8000
```

验证启动输出，应该看到：
```
✅ 应用启动成功
✅ CSRF保护中间件已启用
```

---

## 🧪 CSRF 保护验证

### 测试 1: 获取 CSRF Token

```bash
curl -X GET http://localhost:8000/api/csrf-token

# 预期响应
{
    "csrf_token": "abc123...",
    "timestamp": "2025-11-30T12:00:00"
}
```

### 测试 2: 没有 CSRF Token 的 POST 请求被拒绝

```bash
curl -X POST http://localhost:8000/api/data/query \
    -H "Content-Type: application/json" \
    -d '{"query": "test"}'

# 预期响应 (403)
{
    "error": "CSRF token missing",
    "message": "CSRF token is required for this request"
}
```

### 测试 3: 使用有效 CSRF Token 的 POST 请求成功

```bash
# 1. 获取 token
TOKEN=$(curl -s http://localhost:8000/api/csrf-token | jq -r .csrf_token)

# 2. 使用 token 发送 POST 请求
curl -X POST http://localhost:8000/api/data/query \
    -H "Content-Type: application/json" \
    -H "X-CSRF-Token: $TOKEN" \
    -d '{"query": "test"}'

# 预期响应: 200 OK 与数据
```

### 测试 4: 无效的 CSRF Token 被拒绝

```bash
curl -X POST http://localhost:8000/api/data/query \
    -H "Content-Type: application/json" \
    -H "X-CSRF-Token: invalid_token_12345" \
    -d '{"query": "test"}'

# 预期响应 (403)
{
    "error": "CSRF token invalid",
    "message": "CSRF token is invalid or expired"
}
```

### 测试 5: 排除的端点不需要 CSRF Token

```bash
# 登录端点不需要 CSRF token
curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123"

# 预期响应: 200 OK 与 token
{
    "access_token": "...",
    "token_type": "bearer"
}
```

---

## 🎯 CSRF 保护工作流程

### 客户端流程 (Vue.js 前端)

1. **应用启动时获取 CSRF Token**
   ```javascript
   // 在 main.ts 或 App.vue 中
   import axios from 'axios'

   async function initializeCsrfToken() {
       try {
           const response = await axios.get('/api/csrf-token')
           const csrfToken = response.data.csrf_token

           // 将 token 存储在内存中
           sessionStorage.setItem('csrf_token', csrfToken)

           // 为所有后续请求配置默认头
           axios.defaults.headers.common['X-CSRF-Token'] = csrfToken
       } catch (error) {
           console.error('Failed to get CSRF token:', error)
       }
   }

   // 应用初始化时调用
   initializeCsrfToken()
   ```

2. **发送修改请求时自动包含 CSRF Token**
   ```javascript
   // POST 请求自动包含 CSRF token
   async function createStrategy(strategyData) {
       const response = await axios.post('/api/v1/strategy/create', strategyData)
       return response.data
   }
   ```

3. **错误处理**
   ```javascript
   axios.interceptors.response.use(
       response => response,
       error => {
           if (error.response?.status === 403) {
               const errorData = error.response.data
               if (errorData.error === 'CSRF token missing') {
                   // 重新获取 token 并重试
                   return initializeCsrfToken()
                       .then(() => axios.request(error.config))
               }
           }
           throw error
       }
   )
   ```

### 服务器端流程 (FastAPI)

1. **接收请求**
   ```
   POST /api/v1/strategy/create HTTP/1.1
   X-CSRF-Token: abc123...
   Content-Type: application/json
   ```

2. **CSRF 中间件验证**
   - 检查是否是修改方法 (POST/PUT/PATCH/DELETE)
   - 检查是否在排除列表中
   - 获取请求头中的 `X-CSRF-Token`
   - 验证 token 有效性

3. **允许或拒绝请求**
   - ✅ 有效 → 继续处理请求
   - ❌ 无效 → 返回 403 Forbidden
   - ❌ 缺失 → 返回 403 Forbidden

---

## 📊 CSRF 保护配置详情

### 保护的 HTTP 方法
- ✅ **POST** - 创建资源
- ✅ **PUT** - 更新资源
- ✅ **PATCH** - 部分更新
- ✅ **DELETE** - 删除资源

### 排除的端点 (无需 CSRF Token)
```python
exclude_paths = [
    "/api/csrf-token",      # Token 获取端点
    "/api/auth/login",      # 登录端点
    "/docs",                # API 文档
    "/redoc",               # ReDoc 文档
    "/openapi.json",        # OpenAPI 规范
]
```

### Token 有效期
- 默认：**1 小时** (3600 秒)
- 在 `CSRFTokenManager` 中配置 (line 49)
- 可按需调整

### Token 存储
- **内存存储**: `CSRFTokenManager.tokens = {}` (line 48)
- **生产环境建议**: 迁移到 Redis 或数据库

---

## 🚀 前端集成示例

### Vue 3 + Axios 集成

创建文件: `/web/frontend/src/utils/csrf.ts`

```typescript
import axios from 'axios'

const CSRF_TOKEN_KEY = 'csrf_token'

export async function initializeCsrf() {
    try {
        const response = await axios.get('/api/csrf-token')
        const token = response.data.csrf_token

        // 存储 token
        sessionStorage.setItem(CSRF_TOKEN_KEY, token)

        // 为所有请求配置默认 header
        axios.defaults.headers.common['X-CSRF-Token'] = token
    } catch (error) {
        console.error('Failed to initialize CSRF protection', error)
    }
}

export function getCsrfToken(): string {
    return sessionStorage.getItem(CSRF_TOKEN_KEY) || ''
}

export function setCsrfToken(token: string) {
    sessionStorage.setItem(CSRF_TOKEN_KEY, token)
    axios.defaults.headers.common['X-CSRF-Token'] = token
}

// 配置响应拦截器处理 CSRF token 失效
axios.interceptors.response.use(
    response => response,
    async error => {
        if (error.response?.status === 403) {
            const { data } = error.response
            if (data?.error === 'CSRF token missing' ||
                data?.error === 'CSRF token invalid') {
                // 重新获取 token
                await initializeCsrf()
                // 重试原始请求
                return axios.request(error.config)
            }
        }
        return Promise.reject(error)
    }
)
```

在 `main.ts` 中初始化：

```typescript
import { createApp } from 'vue'
import App from './App.vue'
import { initializeCsrf } from '@/utils/csrf'

// 初始化 CSRF 保护
initializeCsrf()

const app = createApp(App)
app.mount('#app')
```

---

## ⚠️ 注意事项

### 生产环境迁移

当前 CSRF token 存储在内存中，不适合多进程部署：

```python
# 迁移到 Redis (推荐)
import redis
from app.core.config import settings

class CSRFTokenManager:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0
        )

    def generate_token(self) -> str:
        token = secrets.token_urlsafe(32)
        self.redis.setex(f"csrf:{token}", 3600, "valid")
        return token

    def validate_token(self, token: str) -> bool:
        return self.redis.exists(f"csrf:{token}")
```

### Token 刷新策略

建议定期刷新 token：

```javascript
// 定时刷新 token (每 45 分钟)
setInterval(() => {
    initializeCsrf()
}, 45 * 60 * 1000)
```

### 与 SPA 框架的兼容性

- ✅ **Vue.js 3**: 完全兼容
- ✅ **React**: 需要在根组件初始化
- ✅ **Angular**: 需要在应用启动时初始化
- ✅ **Svelte**: 需要在 `+page.svelte` 中初始化

---

## 📝 激活清单

在激活 CSRF 保护之前，请确保：

- [ ] 已读本文档
- [ ] 已取消注释 `/main.py` 中的 CSRF 中间件代码
- [ ] 前端已集成 CSRF token 获取逻辑
- [ ] 所有 POST/PUT/PATCH/DELETE 请求都包含 `X-CSRF-Token` 头
- [ ] 已测试排除的端点 (登录、文档等)
- [ ] 已测试 token 失效和刷新流程
- [ ] 已在测试环境验证
- [ ] 已准备好生产部署方案 (Redis 迁移等)

---

## 🔗 相关文档

- **完整分析报告**: `API_ARCHITECTURE_COMPREHENSIVE_SUMMARY_2025-11-30.md`
- **安全修复总结**: `API_SECURITY_FIXES_SUMMARY_2025-11-30.md`
- **后续建议**: `API_NEXT_STEPS_AND_RECOMMENDATIONS_2025-11-30.md`

---

## ❓ 常见问题

### Q: 为什么 CSRF token 没有包含在 GET 请求中？
A: GET 请求通常不修改数据，因此不需要 CSRF 保护。只有 POST/PUT/PATCH/DELETE 需要。

### Q: 如果用户多次刷新页面，token 会过期吗？
A: 否，每个 token 有 1 小时有效期。建议在前端定期刷新 token。

### Q: 能在单个请求中禁用 CSRF 检查吗？
A: 可以，将端点路径添加到 `exclude_paths` 列表中。

### Q: CSRF token 应该存储在 localStorage 还是 sessionStorage？
A: 建议使用 `sessionStorage`，因为关闭浏览器时会清除，更安全。

---

**指南版本**: 1.0
**最后更新**: 2025-11-30
**维护者**: AI Assistant
