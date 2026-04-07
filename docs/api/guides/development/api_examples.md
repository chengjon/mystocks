# MyStocks API 使用示例和最佳实践

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


> **版本**: 2.0.0
> **更新日期**: 2025-11-21
> **文档类型**: API使用指南

本文档提供MyStocks API的详细使用示例、常见场景和最佳实践。

---

## 📋 目录

1. [快速开始](#快速开始)
2. [认证和安全](#认证和安全)
3. [市场数据API](#市场数据api)
4. [策略管理API](#策略管理api)
5. [缓存管理API](#缓存管理api)
6. [技术指标API](#技术指标api)
7. [错误处理](#错误处理)
8. [性能优化](#性能优化)
9. [客户端SDK](#客户端sdk)

---

## 🚀 快速开始

### 基础配置

```python
import requests
from datetime import datetime, date

# API基础URL
BASE_URL = "http://localhost:8020"

# 请求头配置
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

### 第一个API调用

```python
# 获取市场概览数据
response = requests.get(f"{BASE_URL}/api/market/overview", headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"✅ 请求成功: {data['message']}")
    print(f"📊 数据: {data['data']}")
else:
    print(f"❌ 请求失败: {response.status_code}")
    print(f"错误: {response.json()}")
```

---

## 🔐 认证和安全

### JWT Token认证

#### 1. 获取访问Token

```python
# 登录获取JWT Token
def login(username: str, password: str):
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": username,
            "password": password
        }
    )

    if response.status_code == 200:
        data = response.json()
        return data['data']['access_token']
    else:
        raise Exception(f"登录失败: {response.json()['message']}")

# 使用Token
token = login("admin", "your_password")

# 在后续请求中使用Token
auth_headers = {
    **headers,
    "Authorization": f"Bearer {token}"
}
```

#### 2. Token刷新机制

```python
def refresh_token(refresh_token: str):
    """刷新访问Token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/refresh",
        json={"refresh_token": refresh_token},
        headers=headers
    )

    return response.json()['data']['access_token']
```

### CSRF保护

对于所有修改操作（POST/PUT/PATCH/DELETE），需要CSRF Token：

```python
# 获取CSRF Token
def get_csrf_token():
    response = requests.get(f"{BASE_URL}/api/auth/csrf-token")
    return response.json()['data']['csrf_token']

# 在修改操作中使用
csrf_token = get_csrf_token()

response = requests.post(
    f"{BASE_URL}/api/market/fund-flow/refresh",
    json={"symbol": "600519"},
    headers={
        **auth_headers,
        "X-CSRF-Token": csrf_token
    }
)
```

---

## 📊 市场数据API

### 场景1: 查询个股资金流向

#### 请求示例

```python
# 方式1: 查询最近1天的资金流向
response = requests.get(
    f"{BASE_URL}/api/market/fund-flow",
    params={
        "symbol": "600519.SH",  # 贵州茅台
        "timeframe": "1"         # 1天
    },
    headers=auth_headers
)

# 方式2: 查询指定日期范围
response = requests.get(
    f"{BASE_URL}/api/market/fund-flow",
    params={
        "symbol": "600519.SH",
        "start_date": "2025-01-01",
        "end_date": "2025-01-31"
    },
    headers=auth_headers
)
```

#### 响应示例

```json
[
  {
    "trade_date": "2025-01-20",
    "symbol": "600519.SH",
    "name": "贵州茅台",
    "latest_price": 1750.50,
    "change_percent": 1.25,
    "main_net_inflow": 125000000.00,
    "small_net_inflow": -35000000.00,
    "medium_net_inflow": -15000000.00,
    "large_net_inflow": -75000000.00,
    "super_net_inflow": 200000000.00,
    "main_net_inflow_rate": 8.5,
    "timestamp": "2025-01-20T15:30:00Z"
  }
]
```

#### 完整使用示例

```python
def analyze_fund_flow(symbol: str, days: int = 5):
    """
    分析个股资金流向趋势

    Args:
        symbol: 股票代码
        days: 分析天数

    Returns:
        dict: 分析结果
    """
    response = requests.get(
        f"{BASE_URL}/api/market/fund-flow",
        params={"symbol": symbol, "timeframe": str(days)},
        headers=auth_headers
    )

    if response.status_code != 200:
        return {"error": response.json()['message']}

    data = response.json()

    # 分析资金流向趋势
    main_inflows = [item['main_net_inflow'] for item in data]
    avg_inflow = sum(main_inflows) / len(main_inflows)

    trend = "流入" if avg_inflow > 0 else "流出"

    return {
        "symbol": symbol,
        "days": days,
        "average_main_inflow": avg_inflow,
        "trend": trend,
        "total_main_inflow": sum(main_inflows),
        "data_points": len(data)
    }

# 使用
result = analyze_fund_flow("600519.SH", days=5)
print(f"📈 {result['symbol']} 近{result['days']}日主力资金{result['trend']}")
print(f"💰 平均流入: {result['average_main_inflow']:,.2f}元")
```

### 场景2: ETF实时行情查询

#### 请求示例

```python
# 查询所有ETF并按涨跌幅排序
response = requests.get(
    f"{BASE_URL}/api/market/etf/list",
    params={"limit": 50},
    headers=auth_headers
)

# 搜索特定ETF
response = requests.get(
    f"{BASE_URL}/api/market/etf/list",
    params={"keyword": "科技", "limit": 20},
    headers=auth_headers
)

# 查询单个ETF
response = requests.get(
    f"{BASE_URL}/api/market/etf/list",
    params={"symbol": "159995"},  # 芯片ETF
    headers=auth_headers
)
```

#### 响应示例

```json
[
  {
    "symbol": "159995",
    "name": "芯片ETF",
    "latest_price": 0.856,
    "change_percent": 2.15,
    "change_amount": 0.018,
    "volume": 125000000,
    "amount": 107000000.00,
    "amplitude": 3.2,
    "highest": 0.865,
    "lowest": 0.838,
    "open": 0.840,
    "prev_close": 0.838,
    "turnover_rate": 5.6,
    "volume_ratio": 1.25,
    "timestamp": "2025-01-20T15:00:00Z"
  }
]
```

### 场景3: 刷新市场数据

```python
def refresh_market_data(symbol: str):
    """
    刷新个股的资金流向数据

    注意: 需要CSRF Token
    """
    csrf_token = get_csrf_token()

    response = requests.post(
        f"{BASE_URL}/api/market/fund-flow/refresh",
        params={
            "symbol": symbol,
            "timeframe": "1"
        },
        headers={
            **auth_headers,
            "X-CSRF-Token": csrf_token
        }
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        return result['data']
    else:
        raise Exception(f"刷新失败: {response.json()['message']}")

# 使用
refresh_market_data("600519.SH")
```

---

## 📋 策略管理API

### 场景1: 获取所有策略定义

#### 请求示例

```python
response = requests.get(
    f"{BASE_URL}/api/strategy/definitions",
    headers=auth_headers
)
```

#### 响应示例

```json
{
  "success": true,
  "message": "获取策略列表成功",
  "data": [
    {
      "strategy_code": "MACD_CROSS",
      "strategy_name_cn": "MACD金叉策略",
      "strategy_name_en": "MACD Golden Cross",
      "description": "当MACD线上穿信号线时产生买入信号",
      "parameters": {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9
      },
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 10,
  "timestamp": "2025-01-20T16:00:00Z"
}
```

### 场景2: 运行单只股票策略

#### 请求示例

```python
def run_strategy_single(strategy_code: str, symbol: str, check_date: str = None):
    """
    运行策略检查单只股票

    Args:
        strategy_code: 策略代码 (如 "MACD_CROSS")
        symbol: 股票代码 (如 "600519")
        check_date: 检查日期 (可选，默认今日)
    """
    params = {
        "strategy_code": strategy_code,
        "symbol": symbol
    }

    if check_date:
        params["check_date"] = check_date

    response = requests.post(
        f"{BASE_URL}/api/strategy/run/single",
        params=params,
        headers={
            **auth_headers,
            "X-CSRF-Token": get_csrf_token()
        }
    )

    return response.json()

# 使用
result = run_strategy_single("MACD_CROSS", "600519", "2025-01-20")
```

#### 响应示例

```json
{
  "success": true,
  "message": "策略执行完成",
  "data": {
    "strategy_code": "MACD_CROSS",
    "symbol": "600519",
    "stock_name": "贵州茅台",
    "check_date": "2025-01-20",
    "match_result": true,
    "match_score": 85.5,
    "signals": [
      {
        "type": "buy",
        "strength": "strong",
        "price": 1750.50,
        "reason": "MACD金叉，DIF上穿DEA"
      }
    ],
    "indicators": {
      "macd": 15.23,
      "signal": 10.45,
      "histogram": 4.78,
      "dif": 15.23,
      "dea": 10.45
    },
    "latest_price": 1750.50,
    "change_percent": 1.25
  },
  "timestamp": "2025-01-20T16:05:00Z"
}
```

### 场景3: 批量运行策略（全市场扫描）

#### 请求示例

```python
def run_strategy_batch(strategy_code: str, limit: int = None):
    """
    批量运行策略扫描全市场股票

    Args:
        strategy_code: 策略代码
        limit: 限制扫描数量（可选）
    """
    params = {"strategy_code": strategy_code}

    if limit:
        params["limit"] = limit

    response = requests.post(
        f"{BASE_URL}/api/strategy/run/batch",
        params=params,
        headers={
            **auth_headers,
            "X-CSRF-Token": get_csrf_token()
        }
    )

    return response.json()

# 使用 - 扫描前100只股票
result = run_strategy_batch("MACD_CROSS", limit=100)
```

#### 响应示例

```json
{
  "success": true,
  "message": "批量策略执行完成",
  "data": {
    "strategy_code": "MACD_CROSS",
    "total": 100,
    "matched": 15,
    "failed": 2,
    "match_rate": 0.15,
    "execution_time": 5.23,
    "results": [
      {
        "symbol": "600519",
        "stock_name": "贵州茅台",
        "match_result": true,
        "match_score": 90.5,
        "latest_price": 1750.50,
        "change_percent": 1.25
      },
      {
        "symbol": "000858",
        "stock_name": "五粮液",
        "match_result": true,
        "match_score": 85.2,
        "latest_price": 165.30,
        "change_percent": 0.95
      }
    ]
  },
  "timestamp": "2025-01-20T16:10:00Z"
}
```

### 场景4: 查询策略执行结果

#### 请求示例

```python
# 查询特定策略的所有结果
response = requests.get(
    f"{BASE_URL}/api/strategy/results",
    params={
        "strategy_code": "MACD_CROSS",
        "match_result": True,  # 只看匹配的
        "limit": 50
    },
    headers=auth_headers
)

# 查询特定股票的策略结果
response = requests.get(
    f"{BASE_URL}/api/strategy/results",
    params={"symbol": "600519"},
    headers=auth_headers
)
```

#### 响应示例

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "strategy_code": "MACD_CROSS",
      "symbol": "600519",
      "stock_name": "贵州茅台",
      "check_date": "2025-01-20",
      "match_result": true,
      "match_score": 90.5,
      "latest_price": 1750.50,
      "change_percent": 1.25,
      "created_at": "2025-01-20T16:05:00Z"
    }
  ],
  "total": 15,
  "timestamp": "2025-01-20T16:15:00Z"
}
```

---

## 💾 缓存管理API

### 场景1: 查询缓存统计

```python
response = requests.get(
    f"{BASE_URL}/api/cache/stats",
    headers=auth_headers
)
```

#### 响应示例

```json
{
  "success": true,
  "data": {
    "total_entries": 1250,
    "total_size_mb": 45.6,
    "hit_rate": 0.85,
    "total_hits": 15000,
    "total_misses": 2500,
    "cache_keys": [
      "fund_flow:600519:1",
      "etf_spot:159995",
      "chip_race:open:2025-01-20"
    ],
    "cache_ttl": {
      "fund_flow": 300,
      "etf_spot": 60,
      "chip_race": 300
    }
  },
  "timestamp": "2025-01-20T16:20:00Z"
}
```

### 场景2: 清理缓存

```python
def clear_cache(cache_pattern: str = None):
    """
    清理缓存

    Args:
        cache_pattern: 缓存模式 (可选)
                      如 "fund_flow:*" 清理所有资金流向缓存
                      None 则清理所有缓存
    """
    params = {}
    if cache_pattern:
        params["pattern"] = cache_pattern

    response = requests.delete(
        f"{BASE_URL}/api/cache/clear",
        params=params,
        headers={
            **auth_headers,
            "X-CSRF-Token": get_csrf_token()
        }
    )

    return response.json()

# 清理特定模式的缓存
result = clear_cache("fund_flow:*")
print(f"✅ {result['message']}")
print(f"🗑️  清理了 {result['data']['cleared_count']} 个缓存条目")
```

---

## 📈 技术指标API

### 场景1: 计算技术指标

```python
def calculate_indicators(symbol: str, indicators: list, period: int = 30):
    """
    计算技术指标

    Args:
        symbol: 股票代码
        indicators: 指标列表 ["MA", "MACD", "RSI", "KDJ"]
        period: 计算周期（天数）
    """
    response = requests.post(
        f"{BASE_URL}/api/indicators/calculate",
        json={
            "symbol": symbol,
            "indicators": indicators,
            "period": period,
            "end_date": date.today().isoformat()
        },
        headers={
            **auth_headers,
            "X-CSRF-Token": get_csrf_token()
        }
    )

    return response.json()

# 使用
result = calculate_indicators("600519", ["MA", "MACD", "RSI"], period=30)
```

#### 响应示例

```json
{
  "success": true,
  "data": {
    "symbol": "600519",
    "name": "贵州茅台",
    "period": 30,
    "indicators": {
      "MA": {
        "ma5": 1748.30,
        "ma10": 1742.50,
        "ma20": 1735.80,
        "ma30": 1728.90
      },
      "MACD": {
        "dif": 15.23,
        "dea": 10.45,
        "macd": 9.56
      },
      "RSI": {
        "rsi6": 62.5,
        "rsi12": 58.3,
        "rsi24": 55.7
      }
    },
    "latest_price": 1750.50,
    "timestamp": "2025-01-20T16:25:00Z"
  }
}
```

---

## ❌ 错误处理

### 统一错误响应格式

所有错误都遵循统一格式：

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {},
  "timestamp": "2025-01-20T16:30:00Z"
}
```

### 常见错误码

| HTTP状态码 | error_code | 说明 | 处理建议 |
|-----------|------------|------|---------|
| 400 | INVALID_PARAMETER | 参数错误 | 检查请求参数格式 |
| 401 | UNAUTHORIZED | 未授权 | 重新登录获取Token |
| 403 | FORBIDDEN | 禁止访问 | 检查CSRF Token |
| 404 | RESOURCE_NOT_FOUND | 资源不存在 | 确认资源ID正确 |
| 422 | VALIDATION_ERROR | 数据验证失败 | 检查数据格式和类型 |
| 429 | RATE_LIMIT_EXCEEDED | 请求频率超限 | 降低请求频率 |
| 500 | INTERNAL_ERROR | 服务器错误 | 稍后重试或联系支持 |

### 错误处理示例

```python
from requests.exceptions import RequestException
import time

def api_call_with_retry(url, max_retries=3, backoff_factor=2):
    """
    带重试机制的API调用

    Args:
        url: API URL
        max_retries: 最大重试次数
        backoff_factor: 退避因子
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=auth_headers, timeout=10)

            # 成功
            if response.status_code == 200:
                return response.json()

            # 客户端错误 (4xx) - 不重试
            if 400 <= response.status_code < 500:
                error_data = response.json()
                raise Exception(f"客户端错误: {error_data['message']}")

            # 服务器错误 (5xx) - 重试
            if response.status_code >= 500:
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    print(f"⚠️  服务器错误，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("达到最大重试次数")

        except RequestException as e:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                print(f"⚠️  网络错误，{wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                raise Exception(f"网络错误: {str(e)}")

    raise Exception("请求失败")

# 使用
try:
    data = api_call_with_retry(f"{BASE_URL}/api/market/fund-flow?symbol=600519")
    print("✅ 请求成功")
except Exception as e:
    print(f"❌ 请求失败: {e}")
```

---

## ⚡ 性能优化

### 1. 使用缓存

```python
# ✅ 好的做法 - 利用API缓存
# 第一次调用会从数据库查询
data1 = requests.get(f"{BASE_URL}/api/market/fund-flow?symbol=600519").json()

# 5分钟内的后续调用会从缓存返回（更快）
data2 = requests.get(f"{BASE_URL}/api/market/fund-flow?symbol=600519").json()
```

### 2. 批量操作

```python
# ❌ 不好的做法 - 逐个查询
for symbol in ["600519", "000858", "000001"]:
    response = requests.get(f"{BASE_URL}/api/market/fund-flow?symbol={symbol}")
    # ... 处理

# ✅ 好的做法 - 批量查询
symbols = ["600519", "000858", "000001"]
response = requests.post(
    f"{BASE_URL}/api/market/fund-flow/batch",
    json={"symbols": symbols},
    headers={**auth_headers, "X-CSRF-Token": get_csrf_token()}
)
```

### 3. 分页查询大数据

```python
def get_all_strategy_results(strategy_code: str, page_size: int = 100):
    """
    分页获取所有策略结果

    Args:
        strategy_code: 策略代码
        page_size: 每页大小
    """
    all_results = []
    page = 1

    while True:
        response = requests.get(
            f"{BASE_URL}/api/strategy/results",
            params={
                "strategy_code": strategy_code,
                "page": page,
                "page_size": page_size
            },
            headers=auth_headers
        )

        data = response.json()
        results = data['data']
        all_results.extend(results)

        # 没有更多数据
        if len(results) < page_size:
            break

        page += 1

    return all_results
```

---

## 🔌 客户端SDK

### Python客户端示例

```python
class MyStocksClient:
    """MyStocks API 客户端"""

    def __init__(self, base_url: str, username: str = None, password: str = None):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.csrf_token = None

        if username and password:
            self.login(username, password)

    def login(self, username: str, password: str):
        """登录获取Token"""
        response = self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data['data']['access_token']
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            self._refresh_csrf_token()
        else:
            raise Exception(f"登录失败: {response.json()['message']}")

    def _refresh_csrf_token(self):
        """刷新CSRF Token"""
        response = self.session.get(f"{self.base_url}/api/auth/csrf-token")
        self.csrf_token = response.json()['data']['csrf_token']

    def get_fund_flow(self, symbol: str, timeframe: str = "1"):
        """获取资金流向"""
        response = self.session.get(
            f"{self.base_url}/api/market/fund-flow",
            params={"symbol": symbol, "timeframe": timeframe}
        )
        return response.json()

    def run_strategy(self, strategy_code: str, symbol: str):
        """运行策略"""
        self.session.headers.update({"X-CSRF-Token": self.csrf_token})

        response = self.session.post(
            f"{self.base_url}/api/strategy/run/single",
            params={"strategy_code": strategy_code, "symbol": symbol}
        )
        return response.json()

# 使用SDK
client = MyStocksClient("http://localhost:8020", "admin", "password")

# 获取资金流向
fund_flow = client.get_fund_flow("600519", timeframe="5")
print(fund_flow)

# 运行策略
result = client.run_strategy("MACD_CROSS", "600519")
print(result)
```

### JavaScript客户端示例

```javascript
class MyStocksClient {
  constructor(baseURL, username = null, password = null) {
    this.baseURL = baseURL;
    this.token = null;
    this.csrfToken = null;

    if (username && password) {
      this.login(username, password);
    }
  }

  async login(username, password) {
    const response = await fetch(`${this.baseURL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
      this.token = data.data.access_token;
      await this.refreshCSRFToken();
    } else {
      throw new Error(`登录失败: ${data.message}`);
    }
  }

  async refreshCSRFToken() {
    const response = await fetch(`${this.baseURL}/api/auth/csrf-token`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });

    const data = await response.json();
    this.csrfToken = data.data.csrf_token;
  }

  async getFundFlow(symbol, timeframe = '1') {
    const params = new URLSearchParams({ symbol, timeframe });

    const response = await fetch(
      `${this.baseURL}/api/market/fund-flow?${params}`,
      {
        headers: { 'Authorization': `Bearer ${this.token}` }
      }
    );

    return await response.json();
  }

  async runStrategy(strategyCode, symbol) {
    const params = new URLSearchParams({
      strategy_code: strategyCode,
      symbol
    });

    const response = await fetch(
      `${this.baseURL}/api/strategy/run/single?${params}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'X-CSRF-Token': this.csrfToken
        }
      }
    );

    return await response.json();
  }
}

// 使用SDK
const client = new MyStocksClient('http://localhost:8020');
await client.login('admin', 'password');

// 获取资金流向
const fundFlow = await client.getFundFlow('600519', '5');
console.log(fundFlow);

// 运行策略
const result = await client.runStrategy('MACD_CROSS', '600519');
console.log(result);
```

---

## 📝 最佳实践总结

### ✅ 推荐做法

1. **使用Token认证** - 所有API调用都应包含有效的JWT Token
2. **处理CSRF Token** - 所有修改操作都应包含CSRF Token
3. **实现重试机制** - 对临时错误（5xx）进行指数退避重试
4. **利用缓存** - 充分利用API的缓存机制，减少数据库压力
5. **批量操作** - 尽量使用批量API代替多次单个请求
6. **错误处理** - 正确处理所有可能的错误码
7. **超时设置** - 为所有请求设置合理的超时时间
8. **日志记录** - 记录API调用和错误信息便于调试

### ❌ 避免的做法

1. **硬编码Token** - 不要在代码中硬编码Token
2. **忽略错误** - 不要忽略API返回的错误
3. **频繁请求** - 不要在短时间内发送大量重复请求
4. **跳过CSRF** - 不要尝试绕过CSRF保护
5. **明文传输** - 生产环境必须使用HTTPS
6. **缓存敏感数据** - 不要在客户端缓存敏感信息

---

## 📞 获取帮助

- **Swagger UI**: http://localhost:8020/api/docs
- **ReDoc**: http://localhost:8020/api/redoc
- **健康检查**: http://localhost:8020/health
- **问题反馈**: api@mystocks.com

---

**文档版本**: 2.0.0
**最后更新**: 2025-11-21
**维护者**: MyStocks开发团队
