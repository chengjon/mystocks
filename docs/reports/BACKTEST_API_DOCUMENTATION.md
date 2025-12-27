# A股回测引擎API文档

## 概述

这是一个**复用主项目GPU加速回测引擎**的REST API服务器，提供高性能的量化交易回测服务。

**特点**:
- ✅ GPU加速（68.58x性能提升，如可用）
- ✅ CPU自动回退（确保稳定性）
- ✅ 异步后台执行（不阻塞API）
- ✅ 5种内置策略（MACD、RSI、布林带、双均线、动量）
- ✅ 完整性能指标（收益率、夏普比率、最大回撤、胜率）
- ✅ 模拟数据生成（演示用）

**服务器地址**: `http://localhost:8002`

**API文档**: `http://localhost:8002/docs` (Swagger UI)

---

## 快速开始

### 1. 安装依赖

```bash
cd /tmp/a-stock-backtest-api
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python3 backtest_api_server.py
```

输出示例:
```
======================================================================
🚀 A股回测引擎API服务器
======================================================================
📡 API地址: http://localhost:8002
🏥 健康检查: http://localhost:8002/health
📚 API文档: http://localhost:8002/docs
🎮 GPU加速: ✅ 已启用  或  ❌ 不可用
======================================================================
```

### 3. 测试API

```bash
# 健康检查
curl http://localhost:8002/health

# 查看可用策略
curl http://localhost:8002/api/strategies

# 启动回测
curl -X POST http://localhost:8002/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MACD策略回测",
    "config": {
      "strategy_type": "macd",
      "symbols": ["sh600000"],
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "initial_capital": 1000000
    }
  }'
```

---

## API端点

### 1. 根路径 - 服务信息

**请求**:
```http
GET /
```

**响应**:
```json
{
  "service": "A股回测引擎API",
  "version": "1.0.0",
  "gpu_available": true,
  "endpoints": {
    "POST /api/backtest/run": "启动回测",
    "GET /api/backtest/status/{backtest_id}": "查询回测状态",
    "GET /api/backtest/result/{backtest_id}": "获取回测结果",
    "GET /api/backtest/list": "列出所有回测",
    "GET /health": "健康检查"
  }
}
```

---

### 2. 健康检查

**请求**:
```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-26T11:16:10.561639",
  "gpu_available": false,
  "active_backtests": 0
}
```

---

### 3. 列出可用策略

**请求**:
```http
GET /api/strategies
```

**响应**:
```json
{
  "total": 5,
  "items": [
    {
      "id": "macd",
      "name": "MACD策略",
      "description": "基于MACD金叉死叉的趋势跟踪策略",
      "parameters": {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9
      }
    },
    {
      "id": "rsi",
      "name": "RSI策略",
      "description": "基于RSI超买超卖的均值回归策略",
      "parameters": {
        "period": 14,
        "oversold": 30,
        "overbought": 70
      }
    },
    {
      "id": "bollinger",
      "name": "布林带策略",
      "description": "基于布林带突破的波动率策略",
      "parameters": {
        "period": 20,
        "std_dev": 2
      }
    },
    {
      "id": "dual_ma",
      "name": "双均线策略",
      "description": "基于快慢均线交叉的趋势策略",
      "parameters": {
        "fast_period": 5,
        "slow_period": 20
      }
    },
    {
      "id": "momentum",
      "name": "动量策略",
      "description": "基于价格动量的趋势策略",
      "parameters": {
        "period": 10
      }
    }
  ]
}
```

---

### 4. 启动回测

**请求**:
```http
POST /api/backtest/run
Content-Type: application/json
```

**请求体**:
```json
{
  "name": "MACD策略回测-平安银行",
  "config": {
    "strategy_type": "macd",
    "symbols": ["sh600000"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 1000000,
    "commission_rate": 0.0003,
    "slippage_rate": 0.001,
    "max_position_size": 0.1,
    "stop_loss_pct": null,
    "take_profit_pct": null
  }
}
```

**参数说明**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 回测名称（用户自定义） |
| `config.strategy_type` | string | ✅ | 策略类型：macd, rsi, bollinger, dual_ma, momentum |
| `config.symbols` | string[] | ✅ | 股票代码列表，如 ["sh600000", "sz000001"] |
| `config.start_date` | string | ✅ | 开始日期，格式：YYYY-MM-DD |
| `config.end_date` | string | ✅ | 结束日期，格式：YYYY-MM-DD |
| `config.initial_capital` | float | ❌ | 初始资金，默认1000000 |
| `config.commission_rate` | float | ❌ | 手续费率，默认0.0003（万三） |
| `config.slippage_rate` | float | ❌ | 滑点率，默认0.001 |
| `config.max_position_size` | float | ❌ | 单股最大仓位，默认0.1（10%） |
| `config.stop_loss_pct` | float | ❌ | 止损百分比，如0.05表示5%止损 |
| `config.take_profit_pct` | float | ❌ | 止盈百分比，如0.10表示10%止盈 |

**响应**:
```json
{
  "backtest_id": "bt_20251226_111630_1",
  "status": "pending",
  "message": "回测任务已创建，正在后台执行"
}
```

---

### 5. 查询回测状态

**请求**:
```http
GET /api/backtest/status/{backtest_id}
```

**响应**:
```json
{
  "backtest_id": "bt_20251226_111630_1",
  "name": "MACD策略回测-平安银行",
  "status": "completed",
  "progress": 100,
  "created_at": "2025-12-26T11:16:30.143531",
  "started_at": "2025-12-26T11:16:30.250209",
  "completed_at": "2025-12-26T11:16:30.441270",
  "error": null
}
```

**状态值**:
- `pending` - 等待执行
- `running` - 执行中
- `completed` - 已完成
- `failed` - 执行失败

---

### 6. 获取回测结果

**请求**:
```http
GET /api/backtest/result/{backtest_id}
```

**响应**:
```json
{
  "backtest_id": "bt_20251226_111630_1",
  "name": "MACD策略回测-平安银行",
  "config": {
    "strategy_type": "macd",
    "symbols": ["sh600000"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 1000000.0,
    "commission_rate": 0.0003,
    "slippage_rate": 0.001,
    "max_position_size": 0.1
  },
  "status": "completed",
  "result": {
    "status": "success",
    "performance": {
      "total_return": -0.5393256307801297,
      "sharpe_ratio": -1.264663793597374,
      "max_drawdown": -0.5643078017603688,
      "win_rate": 0.9885057471264368,
      "final_capital": 460674.36921987025
    },
    "trades": 173,
    "signals": 366
  },
  "completed_at": "2025-12-26T11:16:30.441270"
}
```

**性能指标说明**:

| 指标 | 说明 |
|------|------|
| `total_return` | 总收益率（负数表示亏损） |
| `sharpe_ratio` | 夏普比率（>1为优秀，<0为差） |
| `max_drawdown` | 最大回撤（负数，越小越好） |
| `win_rate` | 胜率（0-1之间，1表示100%） |
| `final_capital` | 最终资金（元） |
| `trades` | 总交易次数 |
| `signals` | 总交易信号数 |

---

### 7. 列出所有回测

**请求**:
```http
GET /api/backtest/list
```

**响应**:
```json
{
  "total": 1,
  "items": [
    {
      "backtest_id": "bt_20251226_111630_1",
      "name": "MACD策略回测-平安银行",
      "status": "completed",
      "strategy": "macd",
      "created_at": "2025-12-26T11:16:30.143531",
      "progress": 100
    }
  ]
}
```

---

## 使用示例

### Python示例

```python
import requests
import time

API_BASE = "http://localhost:8002"

# 1. 启动回测
response = requests.post(f"{API_BASE}/api/backtest/run", json={
    "name": "RSI策略回测-招商银行",
    "config": {
        "strategy_type": "rsi",
        "symbols": ["sh600036"],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 1000000,
        "commission_rate": 0.0003
    }
})

backtest_id = response.json()["backtest_id"]
print(f"回测任务已创建: {backtest_id}")

# 2. 等待完成
while True:
    status = requests.get(f"{API_BASE}/api/backtest/status/{backtest_id}").json()
    if status["status"] in ["completed", "failed"]:
        break
    print(f"进度: {status['progress']}%")
    time.sleep(1)

# 3. 获取结果
result = requests.get(f"{API_BASE}/api/backtest/result/{backtest_id}").json()
print(f"总收益率: {result['result']['performance']['total_return']*100:.2f}%")
print(f"夏普比率: {result['result']['performance']['sharpe_ratio']:.2f}")
print(f"最大回撤: {result['result']['performance']['max_drawdown']*100:.2f}%")
print(f"胜率: {result['result']['performance']['win_rate']*100:.2f}%")
```

### JavaScript示例

```javascript
const API_BASE = 'http://localhost:8002';

async function runBacktest() {
  // 1. 启动回测
  const response = await fetch(`${API_BASE}/api/backtest/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: '布林带策略回测',
      config: {
        strategy_type: 'bollinger',
        symbols: ['sh600000'],
        start_date: '2024-01-01',
        end_date: '2024-12-31',
        initial_capital: 1000000
      }
    })
  });

  const { backtest_id } = await response.json();
  console.log(`回测任务已创建: ${backtest_id}`);

  // 2. 等待完成
  let status = 'running';
  while (status === 'running' || status === 'pending') {
    const statusResponse = await fetch(`${API_BASE}/api/backtest/status/${backtest_id}`);
    const statusData = await statusResponse.json();
    status = statusData.status;
    console.log(`进度: ${statusData.progress}%`);
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // 3. 获取结果
  const resultResponse = await fetch(`${API_BASE}/api/backtest/result/${backtest_id}`);
  const result = await resultResponse.json();

  console.log('总收益率:', (result.result.performance.total_return * 100).toFixed(2) + '%');
  console.log('夏普比率:', result.result.performance.sharpe_ratio.toFixed(2));
  console.log('最大回撤:', (result.result.performance.max_drawdown * 100).toFixed(2) + '%');
  console.log('胜率:', (result.result.performance.win_rate * 100).toFixed(2) + '%');
}

runBacktest();
```

---

## GPU加速说明

### GPU加速原理

本API复用主项目的GPU加速回测引擎 (`/opt/claude/mystocks_spec/src/gpu/acceleration/backtest_engine_gpu.py`)

**核心技术**:
- **CuPy**: GPU矩阵运算（187.35x加速比）
- **CuDF**: GPU数据框操作（82.53x加速比）
- **智能内存管理**: 自动内存池，100%命中率
- **故障容灾**: GPU不可用时自动回退CPU

### 性能对比

| 操作 | CPU耗时 | GPU耗时 | 加速比 |
|------|---------|---------|--------|
| 矩阵运算 | 1850ms | 9.87ms | **187.35x** |
| 内存操作 | 1250ms | 15.14ms | **82.53x** |
| 综合回测 | 5000ms | 72.9ms | **68.58x** |

### GPU可用性检查

启动时会显示GPU状态:
```
🎮 GPU加速: ✅ 已启用  或  ❌ 不可用
```

即使GPU不可用，API也能正常工作（使用CPU模式）。

---

## 错误处理

### 常见错误码

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 回测任务不存在 |
| 500 | 服务器内部错误 |

### 错误响应示例

```json
{
  "detail": "回测任务不存在"
}
```

---

## 注意事项

1. **模拟数据**: 当前使用随机游走生成模拟价格，实际应用需连接真实数据源
2. **异步执行**: 回测在后台执行，需轮询状态查询结果
3. **GPU要求**: GPU加速需要CUDA 12.x和CuPy/CuDF库
4. **性能优化**: 大规模回测建议使用GPU模式

---

## 下一步开发

计划中的功能:
- [ ] 连接真实历史价格API
- [ ] 支持多股票组合回测
- [ ] 添加更多技术指标策略
- [ ] 回测结果可视化图表
- [ ] 参数优化功能（网格搜索）
- [ ] 实时交易信号推送

---

**创建时间**: 2025-12-26 11:16
**版本**: v1.0
**文件**: /tmp/a-stock-backtest-api/backtest_api_server.py
**文档**: /tmp/BACKTEST_API_DOCUMENTATION.md
