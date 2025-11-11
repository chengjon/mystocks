# Swagger UI 使用指南

> **当前状态**: ✅ 后端服务已启动，Swagger UI 可访问
> **访问地址**: http://localhost:8000/api/docs
> **最后更新**: 2025-11-09

---

## 📋 目录

1. [快速访问](#快速访问)
2. [Swagger UI 界面介绍](#swagger-ui-界面介绍)
3. [测试 API 的完整流程](#测试-api-的完整流程)
4. [常用功能](#常用功能)
5. [故障排查](#故障排查)

---

## 🚀 快速访问

### 方法 1: 浏览器直接访问 (推荐)

1. **确保后端服务已启动**:
   ```bash
   # 检查服务是否运行
   curl http://localhost:8000/health

   # 如果返回 {"status": "healthy"} 则服务正常
   ```

2. **打开浏览器访问**:
   ```
   http://localhost:8000/api/docs
   ```

3. **或者访问 ReDoc (更适合阅读)**:
   ```
   http://localhost:8000/api/redoc
   ```

### 方法 2: 从命令行启动浏览器

```bash
# Linux
xdg-open http://localhost:8000/api/docs

# macOS
open http://localhost:8000/api/docs

# Windows
start http://localhost:8000/api/docs
```

---

## 🎨 Swagger UI 界面介绍

### 主要区域

```
┌─────────────────────────────────────────────────────┐
│  MyStocks Web API - Swagger UI                     │ ← 标题栏
├─────────────────────────────────────────────────────┤
│  Servers: http://localhost:8000                    │ ← 服务器地址
├─────────────────────────────────────────────────────┤
│  🔍 [Authorize] 按钮                                │ ← 全局认证
├─────────────────────────────────────────────────────┤
│  ▼ auth - 认证授权模块                              │
│     POST /api/auth/login - 用户登录                │ ← API 端点
│     GET /api/csrf-token - 获取CSRF Token          │
│  ▼ market - 市场数据模块                           │
│     GET /api/market/realtime - 获取实时行情        │
│     GET /api/market/kline - 获取K线数据            │
│  ...                                               │
└─────────────────────────────────────────────────────┘
```

### 功能按钮说明

| 按钮/图标 | 功能 | 位置 |
|----------|------|------|
| **🔍 Authorize** | 配置全局认证 (JWT Token) | 右上角 |
| **▼ 展开/折叠** | 展开/折叠 API 模块 | 每个模块标题左侧 |
| **Try it out** | 测试 API | 点击某个 API 端点后显示 |
| **Execute** | 执行请求 | 填写参数后点击 |
| **Clear** | 清空参数 | Execute 按钮旁边 |
| **Download** | 下载 OpenAPI JSON | 右上角 |

---

## 🧪 测试 API 的完整流程

### 示例: 测试获取实时行情 API

#### 步骤 1: 获取 CSRF Token (首次需要)

1. **找到 CSRF Token 端点**:
   - 在 Swagger UI 中找到 `GET /api/csrf-token`
   - 点击展开

2. **执行请求**:
   ```
   1. 点击 "Try it out" 按钮
   2. 直接点击 "Execute" 按钮 (无需参数)
   3. 查看响应中的 csrf_token
   ```

3. **复制 CSRF Token**:
   ```json
   {
     "csrf_token": "WlZjNmRHOXJaVzRtMjM0NTY3ODk...",
     "token_type": "Bearer",
     "expires_in": 3600
   }
   ```
   复制 `csrf_token` 的值

#### 步骤 2: 登录获取 JWT Token

1. **找到登录端点**:
   - 找到 `POST /api/auth/login`
   - 点击展开

2. **填写登录信息**:
   ```
   1. 点击 "Try it out"
   2. 在 Request body 中填写:
   ```
   ```json
   {
     "username": "admin",
     "password": "your-password"
   }
   ```

3. **添加 CSRF Token**:
   ```
   在 Headers 区域添加:
   X-CSRF-Token: WlZjNmRHOXJaVzRtMjM0NTY3ODk...
   ```

4. **执行并获取 JWT Token**:
   ```
   点击 "Execute"
   ```

   响应示例:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "Bearer"
   }
   ```

5. **复制 JWT Token**:
   复制 `access_token` 的值

#### 步骤 3: 配置全局认证

1. **点击右上角 🔍 Authorize 按钮**

2. **在弹出窗口中填写**:
   ```
   Value: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

   **注意**: 必须包含 "Bearer " 前缀

3. **点击 "Authorize" 确认**

4. **点击 "Close" 关闭窗口**

#### 步骤 4: 测试实时行情 API

1. **找到实时行情端点**:
   - 找到 `GET /api/market/realtime`
   - 点击展开

2. **填写参数**:
   ```
   1. 点击 "Try it out"
   2. 在 symbols 参数中填写: 000001.SZ,600000.SH
   ```

3. **执行请求**:
   ```
   点击 "Execute"
   ```

4. **查看响应**:
   ```json
   {
     "code": 0,
     "message": "success",
     "data": [
       {
         "symbol": "000001.SZ",
         "name": "平安银行",
         "price": 12.56,
         "change": 0.05,
         "percent": 0.40,
         ...
       }
     ],
     "timestamp": 1762699683
   }
   ```

---

## 💡 常用功能

### 1. 批量测试多个 API

**技巧**: 保持 Authorize 配置，可以连续测试多个 API 而无需重复登录

```
1. 一次性完成认证配置
2. 逐个展开要测试的 API
3. 每个 API 都会自动携带 JWT Token
```

### 2. 下载 API 规范

```
点击右上角 "Download" 按钮 → 下载 openapi.json
可导入到 Postman、Insomnia 等工具
```

### 3. 查看请求/响应 Schema

```
每个 API 下方都有:
- Parameters: 请求参数定义
- Request body schema: 请求体结构
- Responses: 响应格式定义 (200, 400, 401, 403, 500)
```

### 4. 查看示例数据

```
点击 "Schema" 标签旁边的 "Example Value"
可以看到完整的请求/响应示例
```

### 5. 复制 cURL 命令

```
执行 API 后，在响应区域有 "Curl" 按钮
点击可复制完整的 curl 命令，可在终端中直接运行
```

**示例**:
```bash
curl -X 'GET' \
  'http://localhost:8000/api/market/realtime?symbols=000001.SZ' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

### 6. 按模块筛选 API

**所有 24 个模块**:

| 模块 | 标签名 | 主要功能 |
|------|--------|----------|
| 认证授权 | `auth` | 登录、Token 管理 |
| 市场数据 V1 | `market` | 实时行情、K线、资金流向 |
| 市场数据 V2 | `market-v2` | 东方财富直接 API |
| 缓存管理 | `cache` | TDengine 缓存操作 |
| 技术指标 | `indicators` | MA、MACD、RSI、KDJ |
| 机器学习 | `machine-learning` | 模型训练、预测 |
| 策略管理 | `strategy-management` | 策略 CRUD、回测 |
| 风险管理 | `risk-management` | VaR、回撤、告警 |
| 实时推送 | `sse` | SSE 流式推送 |
| 系统管理 | `system` | 健康检查、性能监控 |
| ... | ... | 还有 14 个模块 |

**完整列表**: 参见 [API_GUIDE.md](./API_GUIDE.md#主要模块概览)

---

## 🔧 故障排查

### 问题 1: 无法访问 http://localhost:8000/api/docs

**排查步骤**:

```bash
# 1. 检查服务是否启动
ps aux | grep uvicorn

# 2. 检查端口是否被占用
lsof -i :8000

# 3. 检查健康状态
curl http://localhost:8000/health

# 4. 启动服务 (如果未运行)
cd /opt/claude/mystocks_spec/web/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 问题 2: API 返回 401 Unauthorized

**原因**: JWT Token 缺失或过期

**解决方案**:
1. 重新执行登录流程获取新 Token
2. 点击 🔍 Authorize 按钮重新配置认证
3. 确保 Token 前面有 "Bearer " 前缀

### 问题 3: API 返回 403 Forbidden

**原因**: CSRF Token 缺失或无效

**解决方案**:
1. 重新获取 CSRF Token (`GET /api/csrf-token`)
2. 在 POST/PUT/DELETE 请求的 Headers 中添加:
   ```
   X-CSRF-Token: <your-csrf-token>
   ```

### 问题 4: Swagger UI 页面显示空白

**排查步骤**:

```bash
# 1. 检查浏览器控制台是否有错误
F12 → Console

# 2. 检查 OpenAPI JSON 是否正常
curl http://localhost:8000/openapi.json | jq '.' | head -20

# 3. 清除浏览器缓存
Ctrl+Shift+Del → 清除缓存

# 4. 尝试其他浏览器
```

### 问题 5: 请求超时

**可能原因**:
1. 数据库连接问题
2. API 处理时间过长
3. 网络问题

**解决方案**:
```bash
# 1. 检查后端日志
tail -f /opt/claude/mystocks_spec/web/backend/logs/*.log

# 2. 检查数据库连接
# PostgreSQL
PGPASSWORD=mystocks2025 psql -h localhost -U mystocks -d mystocks -c "SELECT version();"

# TDengine
taos -h 192.168.123.104 -P 6030

# 3. 增加超时时间 (在 Swagger UI 的 Request 中配置)
```

---

## 📊 快速参考

### 常用端点速查

| 功能 | HTTP方法 | 端点 | 认证 |
|------|---------|------|------|
| 获取 CSRF Token | GET | `/api/csrf-token` | ❌ 无需 |
| 用户登录 | POST | `/api/auth/login` | ✅ CSRF |
| 实时行情 | GET | `/api/market/realtime` | ✅ JWT |
| K线数据 | GET | `/api/market/kline` | ✅ JWT |
| 计算指标 | POST | `/api/indicators/calculate` | ✅ JWT + CSRF |
| 缓存统计 | GET | `/api/cache/stats` | ✅ JWT |
| 系统健康 | GET | `/health` | ❌ 无需 |

### 认证配置速查

```
1. 获取 CSRF Token:
   GET /api/csrf-token

2. 登录获取 JWT:
   POST /api/auth/login
   Headers: X-CSRF-Token: <csrf-token>
   Body: {"username": "admin", "password": "..."}

3. 配置全局认证:
   点击 🔍 Authorize
   填写: Bearer <jwt-token>

4. 测试任意需要认证的 API
```

---

## 🔗 相关资源

- **完整 API 文档**: [API_GUIDE.md](./API_GUIDE.md)
- **API-前端映射**: [API_FRONTEND_MAPPING.md](./API_FRONTEND_MAPPING.md)
- **OpenAPI 规范**: [openapi.json](./openapi.json)
- **项目 README**: [../../README.md](../../README.md)
- **在线 ReDoc**: http://localhost:8000/api/redoc

---

## 💡 使用技巧

### 技巧 1: 保存常用配置

使用浏览器的本地存储功能，Swagger UI 会自动记住:
- 最后使用的 Authorization Token
- 最近的请求参数

### 技巧 2: 使用浏览器书签

```
为常用 API 创建书签:
- http://localhost:8000/api/docs#/market
- http://localhost:8000/api/docs#/indicators
- http://localhost:8000/api/docs#/cache
```

### 技巧 3: 结合浏览器 DevTools 使用

```
F12 → Network 标签
可以看到 Swagger UI 发出的真实 HTTP 请求
包含完整的 Headers、Body、Response
```

### 技巧 4: 导出到 Postman 进行高级测试

```bash
# 1. 下载 openapi.json
curl http://localhost:8000/openapi.json > /tmp/mystocks-api.json

# 2. 在 Postman 中导入
Postman → Import → Upload Files → 选择 /tmp/mystocks-api.json

# 3. 在 Postman 中配置环境变量
base_url = http://localhost:8000
jwt_token = <your-token>
csrf_token = <your-csrf-token>
```

---

## ✅ 使用检查清单

测试前确认:
- [ ] 后端服务已启动 (`curl http://localhost:8000/health`)
- [ ] 浏览器能访问 http://localhost:8000/api/docs
- [ ] 获取了 CSRF Token
- [ ] 成功登录并获取了 JWT Token
- [ ] 配置了全局 Authorize (JWT)
- [ ] 理解了 API 的参数要求
- [ ] 准备好了测试数据 (如股票代码)

测试后检查:
- [ ] 响应状态码是否为 200
- [ ] 响应数据格式是否正确
- [ ] 错误情况是否有清晰的错误信息
- [ ] 性能是否满足要求 (响应时间)

---

**最后更新**: 2025-11-09
**维护者**: 开发团队
**服务状态**: ✅ 运行中
**访问地址**: http://localhost:8000/api/docs
