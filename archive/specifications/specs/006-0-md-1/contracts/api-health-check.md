# Contract: Web API健康检查契约

**Feature**: 系统规范化改进
**Branch**: 006-0-md-1
**Date**: 2025-10-16
**Type**: API Validation

## 目的

定义10个关键Web页面的API健康检查标准和契约，确保Web前端能正确获取和显示数据。

## 前置条件

**必须满足**:
1. ✅ 4个数据库中至少3个连接成功 (MySQL, PostgreSQL, Redis必须通过)
2. ❌ Web Backend服务已启动 (`python -m uvicorn app.main:app --port 8000`)
3. ⚠️ .env配置正确或config.py从环境变量读取

**当前状态**:
- 数据库: 3/4通过 (TDengine需修复)
- Backend: ❌ 未启动
- 前端: ⚠️ 未验证

## 10个关键页面及其API依赖

### 1. 登录页面 (认证模块)

**页面路由**: `/login`
**API端点**: `POST /api/auth/login`
**依赖数据库**: 无 (使用JWT, 内存或文件存储)
**优先级**: P1

**API契约**:
```bash
# 请求
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 预期响应 (200 OK)
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}

# 失败响应 (401 Unauthorized)
{
  "detail": "Incorrect username or password"
}
```

**验证检查**:
- [ ] 返回200状态码
- [ ] access_token字段存在且非空
- [ ] token_type为"bearer"
- [ ] Token可用于后续API认证

---

### 2. TDX实时行情页面

**页面路由**: `/market/tdx-realtime`
**API端点**: `GET /api/tdx/quote/{symbol}`
**依赖数据库**: TDengine ❌
**优先级**: P1

**API契约**:
```bash
# 请求
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/tdx/quote/600519"

# 预期响应 (200 OK)
{
  "symbol": "600519",
  "name": "贵州茅台",
  "current_price": 1650.00,
  "change": 12.50,
  "change_pct": 0.76,
  "open": 1640.00,
  "high": 1655.00,
  "low": 1638.00,
  "volume": 1234567,
  "amount": 2034567890.00,
  "timestamp": "2025-10-16T14:30:00Z"
}
```

**验证检查**:
- [ ] 返回200状态码
- [ ] 包含所有必需字段
- [ ] 价格数据为合理数值
- [ ] timestamp为最近时间

---

### 3. TDX多周期K线页面

**页面路由**: `/market/tdx-kline`
**API端点**: `GET /api/tdx/kline?symbol={symbol}&period={period}`
**依赖数据库**: TDengine ❌
**优先级**: P1

**API契约**:
```bash
# 请求
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/tdx/kline?symbol=600519&period=1d&limit=100"

# 预期响应 (200 OK)
{
  "symbol": "600519",
  "period": "1d",
  "data": [
    {
      "timestamp": "2025-10-15T00:00:00Z",
      "open": 1640.00,
      "high": 1655.00,
      "low": 1635.00,
      "close": 1650.00,
      "volume": 5678900
    },
    // ... 更多K线数据
  ],
  "count": 100
}
```

**验证检查**:
- [ ] 返回200状态码
- [ ] data数组长度>0
- [ ] OHLCV数据完整
- [ ] 支持6种周期(1m/5m/15m/30m/1h/1d)

---

### 4. 市场行情页面

**页面路由**: `/market/quotes`
**API端点**: `GET /api/market/quotes`
**依赖数据库**: MySQL ✅
**优先级**: P1

**API契约**:
```bash
# 请求
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/market/quotes?symbols=600519,000001"

# 预期响应 (200 OK)
{
  "quotes": [
    {
      "symbol": "600519",
      "name": "贵州茅台",
      "current_price": 1650.00,
      "change_pct": 0.76
    },
    {
      "symbol": "000001",
      "name": "平安银行",
      "current_price": 10.50,
      "change_pct": -0.28
    }
  ]
}
```

**验证检查**:
- [ ] 返回200状态码
- [ ] quotes数组长度与请求symbols匹配
- [ ] 每个quote包含必需字段

---

### 5. 股票列表页面

**页面路由**: `/market/stocks`
**API端点**: `GET /api/market/stocks`
**依赖数据库**: MySQL (stock_info表) ✅
**优先级**: P2

**API契约**:
```bash
# 请求
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/market/stocks?page=1&page_size=50"

# 预期响应 (200 OK)
{
  "stocks": [
    {
      "symbol": "600519",
      "name": "贵州茅台",
      "exchange": "SSE",
      "list_date": "2001-08-27"
    },
    // ... 更多股票
  ],
  "total": 5000,
  "page": 1,
  "page_size": 50
}
```

**验证检查**:
- [ ] 返回200状态码
- [ ] stocks数组长度<=page_size
- [ ] total反映实际股票总数

---

### 6. 历史K线查询页面

**页面路由**: `/data/kline`
**API端点**: `GET /api/data/kline/{symbol}`
**依赖数据库**: PostgreSQL (daily_kline表) ✅
**优先级**: P2

**API契约**:
```bash
# 请求
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/data/kline/600519?start_date=2025-10-01&end_date=2025-10-15"

# 预期响应 (200 OK)
{
  "symbol": "600519",
  "data": [
    {
      "date": "2025-10-01",
      "open": 1620.00,
      "high": 1635.00,
      "low": 1615.00,
      "close": 1630.00,
      "volume": 8901234
    },
    // ... 更多K线
  ]
}
```

**验证检查**:
- [ ] 返回200状态码
- [ ] data数组包含指定日期范围内的数据
- [ ] OHLCV数据完整

---

### 7. 财务数据查询页面

**页面路由**: `/data/financial`
**API端点**: `GET /api/data/financial/{symbol}`
**依赖数据库**: MySQL或PostgreSQL
**优先级**: P2

**API契约**:
```bash
# 请求
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/data/financial/600519?report_type=income&period=latest"

# 预期响应 (200 OK)
{
  "symbol": "600519",
  "report_type": "income",
  "report_period": "2025-09-30",
  "data": {
    "revenue": 120000000000,
    "net_profit": 60000000000,
    "eps": 50.00
  }
}
```

**验证检查**:
- [ ] 返回200状态码
- [ ] data包含财务指标
- [ ] report_period为有效日期

---

### 8. 技术指标计算页面

**页面路由**: `/indicators`
**API端点**: `POST /api/indicators/calculate`
**依赖数据库**: PostgreSQL ✅
**优先级**: P2

**API契约**:
```bash
# 请求
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "http://localhost:8000/api/indicators/calculate" \
  -d '{
    "symbol": "600519",
    "indicators": ["MA", "MACD"],
    "period": "1d",
    "ma_periods": [5, 10, 20]
  }'

# 预期响应 (200 OK)
{
  "symbol": "600519",
  "indicators": {
    "MA5": [1640, 1642, 1645, ...],
    "MA10": [1630, 1633, 1636, ...],
    "MA20": [1620, 1622, 1625, ...],
    "MACD": {...}
  }
}
```

**验证检查**:
- [ ] 返回200状态码
- [ ] indicators包含请求的所有指标
- [ ] 指标数据长度合理

---

### 9. 数据源管理页面

**页面路由**: `/system/datasources`
**API端点**: `GET /api/system/datasources`
**依赖数据库**: MySQL (data_sources表) ✅
**优先级**: P3

**API契约**:
```bash
# 请求
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/system/datasources"

# 预期响应 (200 OK)
{
  "datasources": [
    {
      "id": 1,
      "name": "akshare",
      "type": "A股数据",
      "status": "active",
      "last_updated": "2025-10-16T10:00:00Z"
    },
    {
      "id": 2,
      "name": "tdx",
      "type": "实时行情",
      "status": "active",
      "last_updated": "2025-10-16T14:30:00Z"
    }
  ]
}
```

**验证检查**:
- [ ] 返回200状态码
- [ ] datasources数组长度>0
- [ ] 包含主要数据源(akshare, tdx)

---

### 10. 系统监控页面

**页面路由**: `/system/health`
**API端点**: `GET /api/system/health`
**依赖数据库**: PostgreSQL (mystocks_monitoring) ✅
**优先级**: P2

**API契约**:
```bash
# 请求 (无需认证)
curl "http://localhost:8000/api/system/health"

# 预期响应 (200 OK)
{
  "status": "healthy",
  "databases": {
    "mysql": "connected",
    "postgresql": "connected",
    "tdengine": "error",
    "redis": "connected"
  },
  "uptime": 86400,
  "timestamp": "2025-10-16T14:30:00Z"
}
```

**验证检查**:
- [ ] 返回200状态码
- [ ] status为"healthy"或"degraded"
- [ ] databases反映实际连接状态

---

## 常见错误码和排查步骤

### HTTP 401 Unauthorized

**原因**: Token无效或过期
**排查**:
```bash
# 1. 重新获取Token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# 2. 检查Token
echo $TOKEN

# 3. 重试API
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/tdx/quote/600519"
```

### HTTP 500 Internal Server Error

**原因**: 后端代码异常或数据库连接失败
**排查**:
```bash
# 1. 查看后端日志
tail -f web/backend/server.log

# 2. 检查数据库连接
python utils/check_db_health.py

# 3. 检查具体错误栈
curl -v "http://localhost:8000/api/problematic/endpoint"
```

### HTTP 404 Not Found

**原因**: API端点不存在或路由未注册
**排查**:
```bash
# 1. 查看所有可用API
curl "http://localhost:8000/api/docs"

# 2. 检查路由注册
grep -r "router.add_api_route" web/backend/app/api/

# 3. 检查main.py是否include了所有路由
cat web/backend/app/main.py
```

### HTTP 503 Service Unavailable

**原因**: 依赖服务(如数据库)不可用
**排查**:
```bash
# 1. 检查数据库服务
systemctl status mysql
systemctl status postgresql
systemctl status taosd
systemctl status redis

# 2. 检查依赖的数据库连接
python utils/check_db_health.py

# 3. 重启Backend服务
pkill -f uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 自动化健康检查脚本

**工具**: `utils/check_api_health.py` (待创建)

```python
#!/usr/bin/env python3
"""
Web API健康检查脚本
"""

import requests
import sys

BASE_URL = "http://localhost:8000"
API_ENDPOINTS = [
    ("POST", "/api/auth/login", {"username": "admin", "password": "admin123"}),
    ("GET", "/api/tdx/quote/600519", None),
    ("GET", "/api/tdx/kline?symbol=600519&period=1d&limit=10", None),
    ("GET", "/api/market/quotes?symbols=600519", None),
    ("GET", "/api/market/stocks?page=1&page_size=10", None),
    ("GET", "/api/data/kline/600519?start_date=2025-10-01&end_date=2025-10-15", None),
    ("GET", "/api/data/financial/600519?report_type=income", None),
    ("POST", "/api/indicators/calculate", {"symbol": "600519", "indicators": ["MA"]}),
    ("GET", "/api/system/datasources", None),
    ("GET", "/api/system/health", None),
]

def check_api_health():
    token = None
    passed = 0
    total = len(API_ENDPOINTS)

    for method, endpoint, data in API_ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        headers = {}

        # 获取Token用于认证
        if endpoint == "/api/auth/login":
            resp = requests.post(url, data=data)
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                passed += 1
                print(f"✅ {endpoint}: 登录成功")
            else:
                print(f"❌ {endpoint}: 登录失败 ({resp.status_code})")
            continue

        # 添加认证头
        if token and endpoint != "/api/system/health":
            headers["Authorization"] = f"Bearer {token}"

        # 执行API请求
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=5)
            else:
                resp = requests.post(url, json=data, headers=headers, timeout=5)

            if resp.status_code == 200:
                passed += 1
                print(f"✅ {endpoint}: 成功 ({resp.status_code})")
            else:
                print(f"❌ {endpoint}: 失败 ({resp.status_code})")
        except Exception as e:
            print(f"❌ {endpoint}: 异常 ({str(e)})")

    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    return 0 if passed >= total * 0.8 else 1  # 80%通过率

if __name__ == "__main__":
    sys.exit(check_api_health())
```

## 验收标准

### 必须满足 (SC-010-NEW)

- [ ] 10个关键API中至少8个(≥80%)返回200状态码
- [ ] 所有P1级别API(登录、TDX行情、TDX K线、市场行情)必须通过
- [ ] `check_api_health.py` 脚本通过率≥80%

### 建议满足 (SC-011-NEW)

- [ ] 所有P1级别Web页面数据显示正常
- [ ] 响应时间<500ms (非批量查询)
- [ ] 错误消息清晰友好

---

**创建人**: Claude
**版本**: 1.0.0
**批准日期**: 待定
**最后修订**: 2025-10-16
**本次修订内容**: 基于R6研究结果创建API健康检查契约
