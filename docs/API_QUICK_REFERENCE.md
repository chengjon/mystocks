# MyStocks API 快速参考

**版本**: 2.0.0 | **更新日期**: 2025-10-25

---

## 🚀 快速开始

### 基础信息

```
Base URL: http://localhost:8000
API Docs: http://localhost:8000/api/docs
OpenAPI:  http://localhost:8000/openapi.json
```

### 认证

```bash
# 登录获取Token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 使用Token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/data/stocks/basic"
```

---

## 📊 核心端点速查

### 数据查询 (`/api/data`)

| 端点 | 方法 | 描述 | 示例 |
|------|------|------|------|
| `/stocks/basic` | GET | 股票基本信息 | `?limit=10&market=SH` |
| `/stocks/daily` | GET | 日线数据 | `?symbol=600519.SH` |
| `/stocks/search` | GET | 股票搜索 | `?keyword=茅台` |
| `/financial` | GET | 财务数据 | `?symbol=600519&report_type=income` |
| `/kline` | GET | K线数据别名 | `?symbol=600519.SH` |

### 市场数据 (`/api/market`)

| 端点 | 方法 | 描述 | 缓存时间 |
|------|------|------|----------|
| `/fund-flow` | GET | 资金流向 | 5分钟 |
| `/fund-flow/refresh` | POST | 刷新资金流向 | - |
| `/etf/list` | GET | ETF列表 | 1分钟 |
| `/etf/refresh` | POST | 刷新ETF数据 | - |
| `/chip-race` | GET | 竞价抢筹 | 5分钟 |
| `/chip-race/refresh` | POST | 刷新抢筹数据 | - |
| `/lhb` | GET | 龙虎榜 | 24小时 |
| `/lhb/refresh` | POST | 刷新龙虎榜 | - |
| `/quotes` | GET | 实时行情 | 10秒 |
| `/stocks` | GET | 股票列表 | - |

### 技术指标 (`/api/indicators`)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/registry` | GET | 指标注册表 |
| `/registry/{category}` | GET | 按分类获取指标 |
| `/calculate` | POST | 计算技术指标 |
| `/configs` | GET/POST | 指标配置管理 |
| `/configs/{id}` | GET/PUT/DELETE | 单个配置操作 |

### 系统管理 (`/api/system`)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 系统健康检查 |
| `/database/health` | GET | 数据库健康检查 |
| `/database/stats` | GET | 数据库统计 |
| `/adapters/health` | GET | 适配器健康检查 |
| `/logs` | GET | 系统日志 |
| `/logs/summary` | GET | 日志摘要 |
| `/architecture` | GET | 系统架构信息 |

---

## 🔑 常用查询参数

### 分页参数

```
limit: 返回记录数（默认100，最大看具体端点）
offset: 偏移量（用于分页）
```

### 日期参数

```
start_date: 开始日期 (YYYY-MM-DD)
end_date: 结束日期 (YYYY-MM-DD)
```

### 筛选参数

```
symbol: 股票代码 (如: 600519.SH)
market: 市场 (SH/SZ)
industry: 行业
keyword: 搜索关键词
```

---

## 📝 请求示例

### Python

```python
import requests

# 登录
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()['access_token']

# 查询股票
headers = {"Authorization": f"Bearer {token}"}
stocks = requests.get(
    "http://localhost:8000/api/data/stocks/basic",
    params={"limit": 10},
    headers=headers
).json()
```

### curl

```bash
# GET请求
curl "http://localhost:8000/api/market/quotes?symbols=600519.SH,000001.SZ"

# POST请求
curl -X POST "http://localhost:8000/api/indicators/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600519.SH",
    "indicators": [
      {"abbreviation": "SMA", "parameters": {"timeperiod": 20}}
    ]
  }'
```

### JavaScript/Fetch

```javascript
// 登录
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'username=admin&password=admin123'
});
const { access_token } = await loginResponse.json();

// 查询数据
const stocksResponse = await fetch('http://localhost:8000/api/data/stocks/basic?limit=10', {
  headers: {'Authorization': `Bearer ${access_token}`}
});
const stocks = await stocksResponse.json();
```

---

## 🚨 错误码速查

| 状态码 | 含义 | 常见原因 |
|--------|------|----------|
| 200 | 成功 | - |
| 400 | 请求错误 | 参数格式错误 |
| 401 | 未授权 | Token无效/过期 |
| 404 | 未找到 | 资源不存在 |
| 422 | 验证错误 | 参数验证失败 |
| 500 | 服务器错误 | 内部错误 |

---

## 💡 技巧和提示

### 1. 使用缓存

大多数查询端点支持缓存，合理利用可提升性能：

```bash
# 资金流向（5分钟缓存）
curl "http://localhost:8000/api/market/fund-flow?symbol=600519.SH"

# ETF列表（1分钟缓存）
curl "http://localhost:8000/api/market/etf/list"
```

### 2. 批量查询

使用逗号分隔查询多个股票：

```bash
curl "http://localhost:8000/api/market/quotes?symbols=600519.SH,000001.SZ,000002.SZ"
```

### 3. 日志调试

查看API调用日志：

```bash
# 只看ERROR日志
curl "http://localhost:8000/api/system/logs?level=ERROR&limit=50"

# 看数据库相关日志
curl "http://localhost:8000/api/system/logs?category=database"
```

### 4. 健康监控

定期检查系统健康：

```bash
# 快速健康检查
curl "http://localhost:8000/health"

# 详细健康检查
curl "http://localhost:8000/api/system/health"

# 数据库健康
curl "http://localhost:8000/api/system/database/health"
```

---

## 📚 相关资源

| 资源 | 链接 |
|------|------|
| **完整API文档** | [P5_API_DOCUMENTATION.md](./P5_API_DOCUMENTATION.md) |
| **Python SDK** | [api_client_sdk.py](../examples/api_client_sdk.py) |
| **OpenAPI规范** | [openapi.json](./openapi.json) |
| **Swagger UI** | http://localhost:8000/api/docs |
| **ReDoc** | http://localhost:8000/api/redoc |

---

## 🔧 常见问题

### Q: Token过期怎么办？

A: 使用 `/api/auth/refresh` 刷新Token，或重新登录。

### Q: 如何禁用缓存？

A: 某些端点支持 `use_cache=false` 参数。

### Q: 数据更新频率是多少？

A:
- 实时行情: 10秒
- ETF数据: 1分钟
- 资金流向: 5分钟
- 龙虎榜: 每日更新

### Q: 如何获取历史数据？

A: 使用 `/api/data/stocks/daily` 端点，指定 `start_date` 和 `end_date`。

---

**最后更新**: 2025-10-25
**版本**: 2.0.0
