# MyStocks Web API 使用指南

> **版本**: 2.0.0
> **最后更新**: 2025-11-09
> **OpenAPI 版本**: 3.1.0

---

## 📋 目录

1. [快速开始](#快速开始)
2. [认证授权](#认证授权)
3. [API 规范文件](#api-规范文件)
4. [主要模块概览](#主要模块概览)
5. [常用端点示例](#常用端点示例)
6. [响应格式](#响应格式)
7. [错误处理](#错误处理)
8. [在线文档](#在线文档)
9. [工具集成](#工具集成)

---

## 🚀 快速开始

### 基本信息

- **Base URL**: `http://localhost:8020` (端口范围: 8000-8010)
- **文档地址**: `http://localhost:8020/api/docs` (Swagger UI, 端口范围: 8000-8010)
- **备用文档**: `http://localhost:8020/api/redoc` (ReDoc, 端口范围: 8000-8010)
- **健康检查**: `http://localhost:8020/health` (端口范围: 8000-8010)

### 第一个请求

```bash
# 1. 健康检查 (端口可能为8000-8010范围内的可用端口)
curl http://localhost:8020/health

# 2. 获取CSRF Token (端口可能为8000-8010范围内的可用端口)
curl http://localhost:8020/api/csrf-token

# 3. 登录获取JWT Token (端口可能为8000-8010范围内的可用端口)
curl -X POST http://localhost:8020/api/auth/login \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <your-csrf-token>" \
  -d '{
    "username": "admin",
    "password": "your-password"
  }'

# 4. 使用JWT Token访问受保护的端点 (端口可能为8000-8010范围内的可用端口)
curl http://localhost:8020/api/market/realtime \
  -H "Authorization: Bearer <your-jwt-token>"
```

---

## 🔐 认证授权

### 认证流程

MyStocks API 使用 **双重安全机制**：

1. **JWT Token** - 用于身份认证
2. **CSRF Token** - 用于防止跨站请求伪造

### 获取 JWT Token

```bash
# 步骤 1: 获取 CSRF Token
GET /api/csrf-token

# 响应示例
{
  "csrf_token": "abc123...",
  "token_type": "Bearer",
  "expires_in": 3600
}

# 步骤 2: 使用 CSRF Token 登录
POST /api/auth/login
Headers:
  Content-Type: application/json
  X-CSRF-Token: abc123...
Body:
  {
    "username": "admin",
    "password": "your-password"
  }

# 响应示例
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 使用 JWT Token

**所有需要认证的请求**都需要在请求头中添加：

```
Authorization: Bearer <your-jwt-token>
```

### CSRF 保护

**所有修改操作** (POST, PUT, PATCH, DELETE) 都需要在请求头中添加：

```
X-CSRF-Token: <your-csrf-token>
```

**排除端点** (不需要 CSRF Token):
- `/api/csrf-token` - CSRF Token 获取端点
- `/api/auth/login` - 登录端点
- `/api/docs` - 文档端点
- `/api/redoc` - 备用文档端点

---

## 📄 API 规范文件

### OpenAPI 3.0 规范

本项目提供完整的 OpenAPI 3.0 规范文件，支持多种格式：

| 格式 | 文件路径 | 大小 | 用途 |
|------|---------|------|------|
| **JSON** | `docs/api/openapi.json` | 470KB | 机器可读，工具集成 |
| **YAML** | `docs/api/openapi.yaml` | 311KB | 人类可读，版本控制 |

### API 统计

- **总端点数**: 204 个
- **标签分组**: 24 个模块
- **OpenAPI 版本**: 3.1.0
- **支持的认证方式**: JWT Bearer Token + CSRF Token

### 规范内容

OpenAPI 规范文件包含：

✅ **完整的端点定义** - 所有 204 个 API 端点
✅ **请求参数** - Query、Path、Header、Body 参数
✅ **响应模式** - 成功响应和错误响应
✅ **数据模型** - Pydantic Schema 定义
✅ **认证方案** - JWT 和 CSRF Token 配置
✅ **标签分组** - 24 个功能模块分类
✅ **示例数据** - 请求和响应示例

---

## 📊 主要模块概览

### 1. 认证授权 (auth)
**端点数**: 3 个
**主要功能**: 用户登录、JWT Token管理、CSRF保护

```bash
POST   /api/auth/login           # 用户登录
POST   /api/auth/logout          # 用户登出
GET    /api/auth/verify          # Token验证
```

### 2. 市场数据 (market / market-v2)
**端点数**: 35+ 个
**主要功能**: 实时行情、历史数据、资金流向、ETF数据

```bash
# V1 API (AKShare/Baostock)
GET    /api/market/realtime                    # 实时行情
GET    /api/market/kline                       # K线数据
GET    /api/market/fund-flow                   # 资金流向
GET    /api/market/industry-fund-flow          # 行业资金流向
GET    /api/market/etf/list                    # ETF列表
GET    /api/market/chip-distribution           # 筹码分布

# V2 API (东方财富直接API - 更快更准确)
GET    /api/market/v2/realtime                 # 实时行情 (增强版)
GET    /api/market/v2/fund-flow                # 资金流向 (增强版)
GET    /api/market/v2/dragon-tiger             # 龙虎榜
GET    /api/market/v2/large-orders             # 大单追踪
```

### 3. 缓存管理 (cache)
**端点数**: 8 个
**主要功能**: TDengine缓存管理、缓存统计、智能淘汰

```bash
GET    /api/cache/stats                        # 缓存统计
POST   /api/cache/write                        # 写入缓存
GET    /api/cache/read                         # 读取缓存
DELETE /api/cache/evict                        # 缓存淘汰
POST   /api/cache/warmup                       # 缓存预热
GET    /api/cache/health                       # 健康检查
GET    /api/cache/hot-keys                     # 热点数据
POST   /api/cache/clear                        # 清空缓存
```

### 4. 技术指标 (indicators)
**端点数**: 12 个
**主要功能**: 常用技术指标计算

```bash
GET    /api/indicators/ma                      # 移动平均线
GET    /api/indicators/macd                    # MACD
GET    /api/indicators/rsi                     # RSI
GET    /api/indicators/kdj                     # KDJ
GET    /api/indicators/boll                    # 布林带
GET    /api/indicators/volume                  # 成交量指标
POST   /api/indicators/custom                  # 自定义指标
```

### 5. 机器学习 (machine-learning)
**端点数**: 18 个
**主要功能**: 模型训练、预测、评估

```bash
POST   /api/ml/train                           # 模型训练
POST   /api/ml/predict                         # 预测推理
GET    /api/ml/models                          # 模型列表
GET    /api/ml/models/{id}                     # 模型详情
POST   /api/ml/evaluate                        # 模型评估
GET    /api/ml/features                        # 特征工程
```

### 6. 策略管理 (strategy / strategy-management)
**端点数**: 22 个
**主要功能**: 策略配置、回测、风险管理

```bash
# InStock 策略系统
GET    /api/strategy/list                      # 策略列表
POST   /api/strategy/execute                   # 执行策略
GET    /api/strategy/result                    # 策略结果

# 企业级策略管理 (Week 1)
POST   /api/strategy-management/strategies     # 创建策略
GET    /api/strategy-management/strategies     # 策略列表
PUT    /api/strategy-management/strategies/{id} # 更新策略
DELETE /api/strategy-management/strategies/{id} # 删除策略
GET    /api/strategy-management/backtest       # 回测系统
```

### 7. 风险管理 (risk-management)
**端点数**: 15 个
**主要功能**: 风险指标计算、告警配置

```bash
POST   /api/risk/calculate                     # 风险计算
GET    /api/risk/alerts                        # 告警列表
POST   /api/risk/alerts                        # 创建告警
GET    /api/risk/portfolio                     # 组合风险
GET    /api/risk/var                           # VaR计算
GET    /api/risk/drawdown                      # 回撤分析
```

### 8. 实时推送 (sse / monitoring)
**端点数**: 12 个
**主要功能**: SSE流式推送、WebSocket实时数据

```bash
# SSE 实时推送
GET    /api/sse/training                       # 训练进度推送
GET    /api/sse/backtest                       # 回测进度推送
GET    /api/sse/alerts                         # 告警推送
GET    /api/sse/dashboard                      # 仪表盘数据推送

# 监控系统
GET    /api/monitoring/metrics                 # 监控指标
GET    /api/monitoring/alerts                  # 监控告警
POST   /api/monitoring/alerts                  # 创建告警
```

### 9. 自选股管理 (watchlist)
**端点数**: 8 个
**主要功能**: 自选股分组、添加/删除

```bash
GET    /api/watchlist/groups                   # 自选股分组
POST   /api/watchlist/groups                   # 创建分组
GET    /api/watchlist/stocks                   # 自选股列表
POST   /api/watchlist/stocks                   # 添加股票
DELETE /api/watchlist/stocks/{id}              # 删除股票
```

### 10. 数据管理 (data)
**端点数**: 10 个
**主要功能**: 数据导入、导出、同步

```bash
POST   /api/data/import                        # 数据导入
GET    /api/data/export                        # 数据导出
POST   /api/data/sync                          # 数据同步
POST   /api/data/validate                      # 数据校验
```

---

## 💡 常用端点示例

### 1. 获取实时行情

```bash
GET /api/market/realtime?symbols=000001.SZ,600000.SH
Authorization: Bearer <token>

# 响应
{
  "success": true,
  "data": [
    {
      "symbol": "000001.SZ",
      "name": "平安银行",
      "price": 12.56,
      "change": 0.23,
      "change_percent": 1.86,
      "volume": 15234567,
      "amount": 191234567.89,
      "timestamp": "2025-11-09T15:00:00"
    }
  ]
}
```

### 2. 获取K线数据

```bash
GET /api/market/kline?symbol=000001.SZ&period=day&start_date=2025-01-01&end_date=2025-11-09
Authorization: Bearer <token>

# 响应
{
  "success": true,
  "data": {
    "symbol": "000001.SZ",
    "period": "day",
    "klines": [
      {
        "date": "2025-01-02",
        "open": 12.30,
        "high": 12.65,
        "low": 12.25,
        "close": 12.56,
        "volume": 15234567,
        "amount": 191234567.89
      }
    ]
  }
}
```

### 3. 获取行业资金流向

```bash
GET /api/market/fund-flow?industry_type=sw_l1&limit=10
Authorization: Bearer <token>

# 响应
{
  "success": true,
  "data": [
    {
      "industry_code": "801010",
      "industry_name": "农林牧渔",
      "main_net_inflow": 123456789.12,
      "main_net_inflow_rate": 2.34,
      "retail_net_inflow": -98765432.10,
      "date": "2025-11-09"
    }
  ]
}
```

### 4. 计算技术指标

```bash
POST /api/indicators/calculate
Authorization: Bearer <token>
X-CSRF-Token: <csrf-token>
Content-Type: application/json

{
  "symbol": "000001.SZ",
  "indicators": ["MA", "MACD", "RSI"],
  "period": "day",
  "start_date": "2025-01-01"
}

# 响应
{
  "success": true,
  "data": {
    "MA": {
      "MA5": [12.30, 12.45, 12.56, ...],
      "MA10": [12.20, 12.35, 12.50, ...],
      "MA20": [12.10, 12.25, 12.40, ...]
    },
    "MACD": {
      "DIF": [0.05, 0.08, 0.12, ...],
      "DEA": [0.03, 0.06, 0.10, ...],
      "MACD": [0.04, 0.06, 0.08, ...]
    },
    "RSI": {
      "RSI6": [45.3, 52.1, 58.7, ...],
      "RSI12": [48.5, 50.2, 54.3, ...]
    }
  }
}
```

### 5. 缓存操作

```bash
# 写入缓存
POST /api/cache/write
Authorization: Bearer <token>
X-CSRF-Token: <csrf-token>
Content-Type: application/json

{
  "key": "market:realtime:000001.SZ",
  "value": {
    "price": 12.56,
    "volume": 15234567
  },
  "ttl": 300
}

# 读取缓存
GET /api/cache/read?key=market:realtime:000001.SZ
Authorization: Bearer <token>

# 响应
{
  "success": true,
  "data": {
    "key": "market:realtime:000001.SZ",
    "value": {
      "price": 12.56,
      "volume": 15234567
    },
    "hit": true,
    "ttl": 245
  }
}
```

---

## 📋 响应格式

### 成功响应

所有成功的 API 响应都遵循统一格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 实际数据内容
  },
  "timestamp": "2025-11-09T12:34:56.789Z"
}
```

### 分页响应

对于返回列表的端点，使用分页格式：

```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 1000,
    "page": 1,
    "page_size": 20,
    "total_pages": 50
  },
  "timestamp": "2025-11-09T12:34:56.789Z"
}
```

---

## ❌ 错误处理

### 错误响应格式

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {
    // 详细错误信息
  },
  "timestamp": "2025-11-09T12:34:56.789Z"
}
```

### HTTP 状态码

| 状态码 | 说明 | 常见原因 |
|--------|------|----------|
| **200** | 成功 | 请求成功处理 |
| **400** | 请求参数错误 | 参数缺失、格式错误 |
| **401** | 未授权 | JWT Token缺失或过期 |
| **403** | 禁止访问 | CSRF Token无效、权限不足 |
| **404** | 资源不存在 | 端点不存在、数据不存在 |
| **422** | 数据验证失败 | Pydantic验证失败 |
| **500** | 服务器错误 | 内部错误 |

### 常见错误代码

| 错误代码 | 说明 | 解决方案 |
|----------|------|----------|
| `UNAUTHORIZED` | 未授权访问 | 检查JWT Token是否有效 |
| `FORBIDDEN` | 权限不足或CSRF验证失败 | 检查CSRF Token |
| `INVALID_PARAMETER` | 参数验证失败 | 检查请求参数格式 |
| `RESOURCE_NOT_FOUND` | 资源不存在 | 检查资源ID或端点 |
| `VALIDATION_ERROR` | 数据验证失败 | 检查请求体Schema |
| `INTERNAL_ERROR` | 服务器内部错误 | 联系管理员 |

### 错误处理示例

```bash
# 401 未授权
{
  "success": false,
  "message": "未授权访问",
  "error_code": "UNAUTHORIZED",
  "timestamp": "2025-11-09T12:34:56.789Z"
}

# 403 CSRF验证失败
{
  "success": false,
  "message": "权限不足或CSRF验证失败",
  "error_code": "FORBIDDEN",
  "timestamp": "2025-11-09T12:34:56.789Z"
}

# 422 数据验证失败
{
  "success": false,
  "message": "数据验证失败",
  "error_code": "VALIDATION_ERROR",
  "details": [
    {
      "loc": ["body", "symbol"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "timestamp": "2025-11-09T12:34:56.789Z"
}
```

---

## 📚 在线文档

### Swagger UI (推荐)

访问地址: **http://localhost:8020/api/docs**

**功能特点**:
- ✅ 交互式 API 测试
- ✅ 请求/响应示例
- ✅ Schema 定义
- ✅ 在线试用
- ✅ JWT Token 配置
- ✅ 按标签分组

**使用步骤**:
1. 访问 `/api/docs`
2. 点击右上角 "Authorize" 按钮
3. 输入 JWT Token: `Bearer <your-token>`
4. 选择端点并点击 "Try it out"
5. 填写参数并执行

### ReDoc (备用文档)

访问地址: **http://localhost:8020/api/redoc**

**功能特点**:
- ✅ 更清晰的文档结构
- ✅ 三栏布局
- ✅ 搜索功能
- ✅ 代码示例
- ✅ 适合阅读和参考

---

## 🛠️ 工具集成

### 1. Postman 集成

**导入 OpenAPI 规范**:

```bash
# 步骤 1: 下载 OpenAPI 文件
curl http://localhost:8020/openapi.json > mystocks-api.json

# 步骤 2: 在 Postman 中
# Import → Upload Files → 选择 mystocks-api.json
# Postman 会自动创建完整的 API 集合
```

**配置环境变量**:
```
base_url: http://localhost:8020
jwt_token: <your-jwt-token>
csrf_token: <your-csrf-token>
```

### 2. curl 脚本

```bash
#!/bin/bash

# 配置
BASE_URL="http://localhost:8020"
USERNAME="admin"
PASSWORD="your-password"

# 1. 获取 CSRF Token
CSRF_TOKEN=$(curl -s "$BASE_URL/api/csrf-token" | jq -r '.csrf_token')
echo "CSRF Token: $CSRF_TOKEN"

# 2. 登录获取 JWT Token
JWT_TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" \
  | jq -r '.access_token')
echo "JWT Token: $JWT_TOKEN"

# 3. 使用 JWT Token 访问 API
curl -s "$BASE_URL/api/market/realtime?symbols=000001.SZ" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  | jq '.'
```

### 3. Python SDK

```python
import requests
from typing import Dict, Any

class MyStocksAPI:
    def __init__(self, base_url: str = "http://localhost:8020"):
        self.base_url = base_url
        self.csrf_token = None
        self.jwt_token = None

    def get_csrf_token(self) -> str:
        """获取CSRF Token"""
        response = requests.get(f"{self.base_url}/api/csrf-token")
        self.csrf_token = response.json()["csrf_token"]
        return self.csrf_token

    def login(self, username: str, password: str) -> str:
        """登录获取JWT Token"""
        if not self.csrf_token:
            self.get_csrf_token()

        response = requests.post(
            f"{self.base_url}/api/auth/login",
            headers={
                "Content-Type": "application/json",
                "X-CSRF-Token": self.csrf_token
            },
            json={"username": username, "password": password}
        )
        self.jwt_token = response.json()["access_token"]
        return self.jwt_token

    def get_realtime(self, symbols: str) -> Dict[str, Any]:
        """获取实时行情"""
        response = requests.get(
            f"{self.base_url}/api/market/realtime",
            headers={"Authorization": f"Bearer {self.jwt_token}"},
            params={"symbols": symbols}
        )
        return response.json()

# 使用示例
api = MyStocksAPI()
api.login("admin", "password")
data = api.get_realtime("000001.SZ,600000.SH")
print(data)
```

### 4. JavaScript/TypeScript SDK

```typescript
class MyStocksAPI {
  private baseUrl: string;
  private csrfToken?: string;
  private jwtToken?: string;

  constructor(baseUrl: string = "http://localhost:8020") {
    this.baseUrl = baseUrl;
  }

  async getCsrfToken(): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/csrf-token`);
    const data = await response.json();
    this.csrfToken = data.csrf_token;
    return this.csrfToken;
  }

  async login(username: string, password: string): Promise<string> {
    if (!this.csrfToken) {
      await this.getCsrfToken();
    }

    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": this.csrfToken!
      },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    this.jwtToken = data.access_token;
    return this.jwtToken;
  }

  async getRealtime(symbols: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/market/realtime?symbols=${symbols}`,
      {
        headers: {
          "Authorization": `Bearer ${this.jwtToken}`
        }
      }
    );
    return await response.json();
  }
}

// 使用示例
const api = new MyStocksAPI();
await api.login("admin", "password");
const data = await api.getRealtime("000001.SZ,600000.SH");
console.log(data);
```

---

## 📖 相关文档

- **OpenAPI JSON**: `docs/api/openapi.json`
- **OpenAPI YAML**: `docs/api/openapi.yaml`
- **Swagger UI**: `http://localhost:8020/api/docs`
- **ReDoc**: `http://localhost:8020/api/redoc`
- **项目 README**: `README.md`
- **CLAUDE 开发指南**: `CLAUDE.md`

---

## 🔄 版本历史

### v2.0.0 (2025-11-09)
- ✅ 完整的 OpenAPI 3.0 规范
- ✅ 204 个 API 端点
- ✅ 24 个功能模块
- ✅ JWT + CSRF 双重认证
- ✅ 统一响应格式
- ✅ 完整的错误处理
- ✅ Swagger UI 和 ReDoc 文档

### v1.0.0 (2025-11-06)
- ✅ 基础 API 框架
- ✅ 市场数据模块
- ✅ 认证授权模块

---

## 📞 联系支持

- **API 支持邮箱**: api@mystocks.com
- **技术支持网站**: https://mystocks.com/support
- **问题反馈**: https://github.com/mystocks/issues

---

**生成时间**: 2025-11-09
**文档版本**: 2.0.0
**API 版本**: 2.0.0
