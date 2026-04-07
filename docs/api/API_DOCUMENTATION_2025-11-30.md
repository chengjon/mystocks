# MyStocks Web API 完整文档

> **历史文档说明**:
> 本文件是 `2025-11-30` 的 API 文档快照，不是当前 API 契约、当前端点总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则或审批门禁，请优先遵循 `architecture/STANDARDS.md`；若涉及执行流程与协作约束，再参考根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内基础 URL、端点数量、认证流程和响应示例如未重新导出与复核，应视为历史快照，不得直接当作当前事实。

**历史文档生成日期快照**: 2025-11-30
**历史 API 版本快照**: 1.0.0
**历史基础 URL 快照**: http://localhost:8020

---

## 📋 API 总览

| 指标 | 数值 |
|------|------|
| **总端点数** | 6 个 |
| **GET 端点** | 5 个 |
| **POST 端点** | 1 个 |
| **认证方式** | JWT Token |
| **数据格式** | JSON |
| **CORS** | 启用 |

---

## 🔐 认证

### 认证流程

1. **获取 CSRF Token** (可选)
   - 请求: `GET /api/csrf-token`

2. **登录**
   - 请求: `POST /api/auth/login`
   - 返回 JWT Token

3. **使用 Token**
   - 在请求头中添加: `Authorization: Bearer <token>`

---

## 📡 API 端点详细文档

### 1. 🏥 系统健康检查

#### 端点信息
```
GET /health
```

#### 说明
系统健康检查端点，用于检查后端服务是否正常运行。

#### 请求示例
```bash
curl -X GET "http://localhost:8020/health"
```

#### 响应示例
```json
{
  "status": "healthy",
  "timestamp": "2025-11-30T20:16:00Z",
  "version": "1.0.0"
}
```

#### 响应码
- `200 OK` - 系统正常运行

---

### 2. 🏠 根路径重定向

#### 端点信息
```
GET /
```

#### 说明
根路径重定向到 Swagger API 文档页面。

#### 请求示例
```bash
curl -X GET "http://localhost:8020/"
```

#### 响应
重定向到 `/docs` 页面

#### 响应码
- `307 Temporary Redirect` - 重定向到 Swagger 文档

---

### 3. 📖 Swagger UI 文档

#### 端点信息
```
GET /docs
```

#### 说明
自定义 Swagger UI 页面，使用本地静态资源，展示所有可用的 API 端点。

#### 请求示例
```bash
curl -X GET "http://localhost:8020/docs"
```

#### 响应
返回 HTML 页面，可在浏览器中打开

#### 响应码
- `200 OK` - 成功返回 Swagger UI 页面

#### 访问方法
```
在浏览器中打开: http://localhost:8020/docs
```

---

### 4. 🔐 获取 CSRF Token

#### 端点信息
```
GET /api/csrf-token
```

#### 说明
获取 CSRF Token，用于防止跨站请求伪造攻击。(可选)

#### 请求示例
```bash
curl -X GET "http://localhost:8020/api/csrf-token"
```

#### 请求参数
无

#### 响应示例
```json
{
  "csrf_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 响应码
- `200 OK` - 成功获取 CSRF Token

#### 用途
- 防止跨站请求伪造 (CSRF) 攻击
- 在后续 POST/PUT/DELETE 请求中可以在请求头中使用

---

### 5. 🔑 用户登录

#### 端点信息
```
POST /api/auth/login
```

#### 说明
用户登录端点，验证用户凭证并返回 JWT Token。

#### 请求示例
```bash
curl -X POST "http://localhost:8020/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

#### 请求体
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

#### 请求参数说明
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

#### 响应示例 (成功)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_123",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

#### 响应示例 (失败)
```json
{
  "detail": "Invalid credentials"
}
```

#### 响应码
- `200 OK` - 登录成功
- `401 Unauthorized` - 用户名或密码错误
- `422 Unprocessable Entity` - 请求体格式错误

#### 返回值说明
| 字段 | 类型 | 说明 |
|------|------|------|
| access_token | string | JWT 认证令牌，用于后续请求 |
| token_type | string | 令牌类型，固定为 "bearer" |
| user | object | 用户信息对象 |
| user.id | string | 用户 ID |
| user.username | string | 用户名 |
| user.email | string | 邮箱地址 |
| user.role | string | 用户角色 |

#### 使用返回的 Token
```bash
# 在后续请求中，在 Authorization 头中添加 token
curl -X GET "http://localhost:8020/api/auth/user" \
  -H "Authorization: Bearer <access_token>"
```

#### 测试用例
```bash
# 正确的凭证
curl -X POST "http://localhost:8020/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 错误的凭证
curl -X POST "http://localhost:8020/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}'
```

---

### 6. 👤 获取当前用户信息

#### 端点信息
```
GET /api/auth/user
```

#### 说明
获取当前登录用户的信息。需要有效的 JWT Token。

#### 请求示例
```bash
curl -X GET "http://localhost:8020/api/auth/user" \
  -H "Authorization: Bearer <access_token>"
```

#### 请求头
| 头部 | 值 | 说明 |
|------|-----|------|
| Authorization | Bearer <token> | JWT 认证令牌 (必需) |

#### 响应示例
```json
{
  "id": "user_123",
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-11-30T20:16:00Z"
}
```

#### 响应码
- `200 OK` - 成功获取用户信息
- `401 Unauthorized` - 缺少或无效的 Token
- `403 Forbidden` - 无权访问

#### 返回值说明
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 用户 ID |
| username | string | 用户名 |
| email | string | 邮箱地址 |
| role | string | 用户角色 (admin/user) |
| created_at | string | 账户创建时间 (ISO 8601) |
| last_login | string | 最后登录时间 (ISO 8601) |

#### 使用场景
- 在应用启动时获取当前用户信息
- 验证用户身份
- 更新用户的最后登录时间

#### 测试用例
```bash
# 首先登录获取 token
TOKEN=$(curl -s -X POST "http://localhost:8020/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 使用 token 获取用户信息
curl -X GET "http://localhost:8020/api/auth/user" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔄 完整工作流示例

### 场景: 用户登录和获取用户信息

#### 第1步: 登录
```bash
curl -X POST "http://localhost:8020/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**响应:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_123",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

#### 第2步: 使用 Token 获取用户信息
```bash
curl -X GET "http://localhost:8020/api/auth/user" \
  -H "Authorization: Bearer <jwt-token>"
```

**响应:**
```json
{
  "id": "user_123",
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-11-30T20:16:00Z"
}
```

---

## 🛠️ 错误处理

### 常见错误响应

#### 401 Unauthorized
```json
{
  "detail": "Unauthorized"
}
```
**原因**: 缺少或无效的认证令牌

#### 403 Forbidden
```json
{
  "detail": "Forbidden"
}
```
**原因**: 用户无权访问该资源

#### 404 Not Found
```json
{
  "detail": "Not Found"
}
```
**原因**: 请求的资源不存在

#### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**原因**: 请求体格式错误或缺少必需字段

---

## 💾 数据格式

### 日期时间格式
所有日期和时间都遵循 ISO 8601 标准:
```
2025-11-30T20:16:00Z
```

### 用户角色
- `admin` - 管理员，拥有所有权限
- `user` - 普通用户，权限受限

### Token 格式
使用 JWT (JSON Web Token) 格式:
```
<jwt-token>
```

---

## 📊 API 使用统计

### 端点分布
```
认证相关:
  ├── GET  /api/csrf-token     (获取 CSRF Token)
  ├── POST /api/auth/login     (用户登录)
  └── GET  /api/auth/user      (获取用户信息)

系统相关:
  ├── GET  /health             (健康检查)
  ├── GET  /                   (根路径)
  └── GET  /docs               (API 文档)
```

### HTTP 方法分布
- GET: 5 个端点 (83.3%)
- POST: 1 个端点 (16.7%)

### 响应格式
- JSON: 100%
- HTML: 1 个端点 (/docs)

---

## 🔗 相关资源

### 访问 Swagger UI
```
URL: http://localhost:8020/docs
描述: 交互式 API 文档，可在浏览器中直接测试所有端点
```

### OpenAPI Schema
```
URL: http://localhost:8020/openapi.json
格式: JSON
描述: 机器可读的 OpenAPI 3.1.0 规范
```

### API 健康检查
```
URL: http://localhost:8020/health
方法: GET
用途: 检查后端服务是否正常运行
```

---

## 🚀 快速开始

### 使用 Python requests
```python
import requests
import json

# 登录
response = requests.post(
    "http://localhost:8020/api/auth/login",
    json={
        "username": "admin",
        "password": "admin123"
    }
)

if response.status_code == 200:
    data = response.json()
    token = data["access_token"]

    # 获取用户信息
    headers = {"Authorization": f"Bearer {token}"}
    user_response = requests.get(
        "http://localhost:8020/api/auth/user",
        headers=headers
    )

    print(user_response.json())
```

### 使用 JavaScript (Fetch API)
```javascript
// 登录
const loginResponse = await fetch('http://localhost:8020/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const loginData = await loginResponse.json();
const token = loginData.access_token;

// 获取用户信息
const userResponse = await fetch('http://localhost:8020/api/auth/user', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const userData = await userResponse.json();
console.log(userData);
```

### 使用 cURL
```bash
#!/bin/bash

# 第一步: 登录
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8020/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

# 提取 token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Login successful, token: $TOKEN"

# 第二步: 使用 token 获取用户信息
curl -X GET "http://localhost:8020/api/auth/user" \
  -H "Authorization: Bearer $TOKEN"
```

---

## ⚙️ 配置信息

### 服务器信息
| 项目 | 值 |
|------|-----|
| 主机 | localhost |
| 端口 | 8000 |
| 协议 | HTTP |
| API 版本 | 1.0.0 |

### 安全配置
- JWT Token 过期时间: 24 小时
- CORS 已启用
- CSRF 保护已启用
- HTTPS (在生产环境推荐)

---

## 📝 注意事项

1. **Token 安全**: 不要在客户端代码中暴露 Token，应该存储在安全的位置
2. **HTTPS**: 在生产环境中，应该使用 HTTPS 而不是 HTTP
3. **CORS**: 跨域请求已启用，但在生产环境中应该配置受信任的域名
4. **速率限制**: 目前没有速率限制，生产环境中应该添加

---

## 🔄 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2025-11-30 | 初始版本，包含基本认证和用户管理 API |

---

**最后更新**: 2025-11-30
**文档维护者**: MyStocks 开发团队
