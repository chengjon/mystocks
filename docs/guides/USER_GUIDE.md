# MyStocks 用户使用指南

## 目录

- [快速开始](#快速开始)
- [功能介绍](#功能介绍)
- [API 使用](#api-使用)
- [策略管理](#策略管理)
- [回测功能](#回测功能)
- [交易功能](#交易功能)
- [常见问题](#常见问题)

---

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-org/mystocks.git
cd mystocks

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库连接等信息
```

### 2. 启动服务

```bash
# 启动后端服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 访问 API 文档
# 打开浏览器访问 http://localhost:8000/docs
```

### 3. 登录系统

```bash
# 使用默认管理员账户
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

---

## 功能介绍

### 市场数据

MyStocks 提供全面的市场数据功能：

| 功能 | 说明 |
|------|------|
| K 线数据 | 支持日/周/月级别 K 线 |
| 实时行情 | 毫秒级实时数据推送 |
| 资金流向 | 主力资金流向分析 |
| 龙虎榜 | 机构交易数据 |

### 策略管理

- **创建策略**: 支持多种策略类型
- **参数配置**: 灵活调整策略参数
- **回测验证**: 历史数据回测验证
- **模拟交易**: 实时模拟执行

### 回测功能

| 指标 | 说明 |
|------|------|
| 总收益率 | 策略总收益 |
| 年化收益率 | 年化收益 |
| 最大回撤 | 最大亏损幅度 |
| 夏普比率 | 风险调整收益 |
| 胜率 | 盈利交易比例 |

---

## API 使用

### 认证

```python
import requests

BASE_URL = "http://localhost:8000"

# 登录
def login(username, password):
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    return response.json()["data"]["access_token"]

# 获取用户信息
def get_me(token):
    response = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

### 获取 K 线数据

```python
def get_kline(symbol, start_date, end_date, interval="daily"):
    params = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "interval": interval
    }
    response = requests.get(
        f"{BASE_URL}/api/v1/market/kline",
        params=params
    )
    return response.json()["data"]

# 使用示例
kline = get_kline("000001.SZ", "2025-01-01", "2025-01-31", "daily")
```

### 获取实时行情

```python
def get_realtime(symbol):
    response = requests.get(
        f"{BASE_URL}/api/v1/market/realtime",
        params={"symbol": symbol}
    )
    return response.json()["data"]

# 使用示例
quote = get_realtime("000001.SZ")
print(f"当前价格: {quote['price']}")
```

---

## 策略管理

### 创建均线策略

```python
def create_strategy(token, name, short_period=5, long_period=20):
    data = {
        "name": name,
        "type": "ma_crossover",
        "description": "双均线交叉策略",
        "parameters": {
            "short_period": short_period,
            "long_period": long_period,
            "position_pct": 0.8,
            "stop_loss": 0.05,
            "take_profit": 0.15
        }
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/strategies",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()["data"]

# 使用示例
strategy = create_strategy(
    token,
    "5日-20日均线策略",
    short_period=5,
    long_period=20
)
```

### 策略参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| short_period | int | 5 | 短期均线周期 |
| long_period | int | 20 | 长期均线周期 |
| position_pct | float | 0.8 | 仓位比例 |
| stop_loss | float | 0.05 | 止损比例 |
| take_profit | float | 0.15 | 止盈比例 |

---

## 回测功能

### 创建回测

```python
def create_backtest(token, strategy_id, symbol, start_date, end_date):
    data = {
        "strategy_id": strategy_id,
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "initial_capital": 100000,
        "position_pct": 0.8
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/backtests",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()["data"]

# 使用示例
backtest = create_backtest(
    token,
    strategy_id=1,
    symbol="000001.SZ",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
print(f"回测ID: {backtest['id']}")
```

### 获取回测结果

```python
def get_backtest_result(token, backtest_id):
    response = requests.get(
        f"{BASE_URL}/api/v1/backtests/{backtest_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()["data"]

# 使用示例
result = get_backtest_result(token, backtest_id)
print(f"总收益率: {result['total_return']:.2f}%")
print(f"夏普比率: {result['sharpe_ratio']:.2f}")
print(f"最大回撤: {result['max_drawdown']:.2f}%")
```

---

## 交易功能

### 下单

```python
def place_order(token, symbol, action, quantity, order_type="market", price=None):
    data = {
        "symbol": symbol,
        "action": action,
        "order_type": order_type,
        "quantity": quantity,
        "price": price
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/trade/order",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()["data"]

# 使用示例
# 市价买入
order = place_order(token, "000001.SZ", "buy", 1000)

# 限价买入
order = place_order(token, "000001.SZ", "buy", 1000, "limit", 10.5)
```

### 查询持仓

```python
def get_positions(token):
    response = requests.get(
        f"{BASE_URL}/api/v1/trade/positions",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()["data"]

# 使用示例
positions = get_positions(token)
for pos in positions:
    print(f"{pos['symbol']}: {pos['quantity']}股, 盈亏: {pos['profit_loss']:.2f}")
```

---

## 常见问题

### Q1: 如何获取股票代码？

股票代码格式为 `代码.交易所`：
- 深圳: `000001.SZ`
- 上海: `600000.SH`

可以使用 API 获取支持的股票列表：

```python
def get_symbols():
    response = requests.get(f"{BASE_URL}/api/v1/market/symbols")
    return response.json()["data"]
```

### Q2: 回测需要多长时间？

回测时间取决于：
- 回测时间范围
- 策略复杂度
- 系统负载

一般情况下：
- 1 年日线数据: 1-5 秒
- 5 年日线数据: 5-15 秒

### Q3: 如何调整策略参数？

```python
def update_strategy(token, strategy_id, **kwargs):
    response = requests.put(
        f"{BASE_URL}/api/v1/strategies/{strategy_id}",
        json=kwargs,
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

# 使用示例
update_strategy(token, 1, parameters={"short_period": 10, "long_period": 30})
```

### Q4: 交易 수수료是多少？

| 交易类型 | 费率 |
|---------|------|
| 印花税 | 0.1%（卖出时收取） |
| 佣金 | 0.03%（最低 5 元） |
| 过户费 | 0.002%（上海） |

---

## 下一步

- [API 文档索引](../api/API_INDEX.md)
- [错误码参考](../api/ERROR_CODES.md)
- [部署指南](./DEPLOYMENT.md)
- [故障排查手册](./TROUBLESHOOTING.md)
