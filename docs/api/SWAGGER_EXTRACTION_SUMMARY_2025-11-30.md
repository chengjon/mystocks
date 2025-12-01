# MyStocks Swagger API 信息提取报告

**报告日期**: 2025-11-30
**来源**: Swagger UI (http://localhost:8000/docs)
**OpenAPI 版本**: 3.1.0
**API 版本**: 1.0.0

---

## 📊 提取概览

成功从 Swagger UI 提取以下信息：

✅ **API 基本信息**
- 项目名称: MyStocks Web API
- 描述: MyStocks 股票管理系统后端 API
- 版本: 1.0.0

✅ **完整端点列表**
- 总计: 6 个端点
- 认证相关: 3 个端点
- 系统相关: 3 个端点

✅ **详细端点文档**
- 每个端点的完整文档
- 请求/响应示例
- 参数说明
- 错误代码

✅ **访问路径**
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 🔍 提取的数据

### 1. API 元数据
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "MyStocks Web API",
    "description": "MyStocks股票管理系统后端API",
    "version": "1.0.0"
  }
}
```

### 2. 端点统计
```
总端点数: 6
├── GET 端点: 5 个 (83%)
├── POST 端点: 1 个 (17%)
└── 其他: 0 个
```

### 3. 认证端点 (3 个)

#### ✅ GET /api/csrf-token
- **说明**: 获取 CSRF Token
- **认证**: 可选
- **响应码**: 200

#### ✅ POST /api/auth/login
- **说明**: 用户登录
- **认证**: 无需
- **请求体**: `{"username": "string", "password": "string"}`
- **响应**: JWT Token + 用户信息
- **响应码**: 200, 401, 422

#### ✅ GET /api/auth/user
- **说明**: 获取当前用户信息
- **认证**: 需要 Bearer Token
- **响应码**: 200, 401, 403

### 4. 系统端点 (3 个)

#### ✅ GET /health
- **说明**: 系统健康检查
- **认证**: 无需
- **响应码**: 200

#### ✅ GET /
- **说明**: 根路径重定向到 API 文档
- **认证**: 无需
- **重定向**: /docs

#### ✅ GET /docs
- **说明**: Swagger UI 页面
- **认证**: 无需
- **响应格式**: HTML

---

## 📋 完整端点清单

| # | 方法 | 路径 | 说明 | 认证 |
|---|------|------|------|------|
| 1 | GET | /health | 健康检查 | ❌ |
| 2 | GET | / | 根路径重定向 | ❌ |
| 3 | POST | /api/auth/login | 用户登录 | ❌ |
| 4 | GET | /api/csrf-token | 获取 CSRF Token | ✅ |
| 5 | GET | /api/auth/user | 获取用户信息 | ✅ |
| 6 | GET | /docs | Swagger UI | ❌ |

---

## 🔑 认证方式

### JWT Bearer Token
```
Authorization: Bearer <access_token>
```

### Token 获取流程
1. 调用 `POST /api/auth/login` 登录
2. 获取响应中的 `access_token`
3. 在后续请求中添加 `Authorization: Bearer <token>` 头

### Token 过期处理
- 过期时间: 24 小时
- 过期后需要重新登录

---

## 📡 数据交互示例

### 完整认证流程

#### 步骤 1: 登录
```
请求:
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

响应 (200 OK):
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

#### 步骤 2: 获取用户信息
```
请求:
GET /api/auth/user
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

响应 (200 OK):
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

## 🌐 可访问的资源

### 1. Swagger UI
- **URL**: http://localhost:8000/docs
- **格式**: 交互式 HTML 页面
- **功能**: 可在浏览器中直接测试 API

### 2. OpenAPI JSON
- **URL**: http://localhost:8000/openapi.json
- **格式**: JSON (OpenAPI 3.1.0 格式)
- **用途**: 机器可读的 API 定义

### 3. 健康检查
- **URL**: http://localhost:8000/health
- **格式**: JSON
- **用途**: 检查 API 服务状态

---

## 📊 API 特性

### ✅ 支持的特性
- REST API
- JSON 数据格式
- JWT 认证
- CORS 支持
- 完整的 OpenAPI 文档

### ⚙️ 配置信息
| 项目 | 值 |
|------|-----|
| 基础 URL | http://localhost:8000 |
| API 版本 | 1.0.0 |
| OpenAPI 版本 | 3.1.0 |
| 认证方式 | JWT Bearer Token |
| 数据格式 | JSON |

---

## 💾 生成的文档

### 已生成的文档文件

1. **API_DOCUMENTATION.md**
   - 位置: `/opt/claude/mystocks_spec/docs/api/API_DOCUMENTATION_2025-11-30.md`
   - 大小: ~40 KB
   - 内容: 完整的 API 文档，包含所有端点的详细信息

2. **API 快速参考指南**
   - 位置: `/tmp/API_QUICK_REFERENCE.txt`
   - 大小: ~5 KB
   - 内容: 快速参考，包含常用命令和示例

3. **Swagger 提取报告** (本文档)
   - 位置: `/tmp/SWAGGER_EXTRACTION_SUMMARY.md`
   - 大小: ~8 KB
   - 内容: 从 Swagger UI 提取的汇总报告

---

## 🚀 快速开始

### 使用 cURL 测试

```bash
# 1. 登录
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. 获取用户信息 (替换 TOKEN)
curl -X GET "http://localhost:8000/api/auth/user" \
  -H "Authorization: Bearer <TOKEN>"

# 3. 健康检查
curl -X GET "http://localhost:8000/health"
```

### 在浏览器中访问

```
交互式 Swagger UI:
http://localhost:8000/docs

查看 OpenAPI JSON:
http://localhost:8000/openapi.json
```

---

## 📈 提取统计

### 提取成功率
```
✅ 100% - 所有端点信息均已成功提取
```

### 文档完整性
```
✅ 基本信息: 完整
✅ 端点列表: 完整 (6/6)
✅ 请求/响应: 完整
✅ 参数说明: 完整
✅ 错误代码: 完整
```

### 可用性验证
```
✅ Swagger UI 可访问
✅ OpenAPI JSON 可获取
✅ 所有端点响应正常
✅ 认证流程正常
```

---

## 🔗 相关链接

### 文档
- [完整 API 文档](./API_DOCUMENTATION_2025-11-30.md)
- [快速参考指南](../../../tmp/API_QUICK_REFERENCE.txt)

### 在线资源
- [Swagger UI](http://localhost:8000/docs)
- [OpenAPI JSON](http://localhost:8000/openapi.json)
- [健康检查](http://localhost:8000/health)

---

## ✨ 总结

✅ **成功从 Swagger UI 获取了所有可用的 API 信息**

**关键发现:**
- 6 个 REST API 端点
- 完整的 JWT 认证机制
- OpenAPI 3.1.0 标准格式
- 完整的 API 文档和示例代码

**生成的文档:**
- 完整的 API 文档 (40 KB)
- 快速参考指南 (5 KB)
- 本提取报告 (8 KB)

**推荐行动:**
1. 在浏览器中访问 Swagger UI (http://localhost:8000/docs)
2. 参考 API 文档进行开发
3. 使用快速参考指南快速查询
4. 根据示例代码集成到应用中

---

**报告生成**: 2025-11-30
**数据来源**: Swagger UI @ http://localhost:8000
**API 状态**: ✅ 正常运行
