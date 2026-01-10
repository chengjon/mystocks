# Phase 12.3: Real-time Data Stream Integration

## 概述

实时数据流集成模块，提供 WebSocket 行情订阅和持仓市值实时计算功能。

## 核心组件

### 1. 行情数据解析器 (`src/services/market_data_parser.py`)

支持多种数据源的行情数据解析：
- efinance
- easyquotation
- WebSocket
- akshare

```python
from src.services.market_data_parser import get_market_data_parser

parser = get_market_data_parser()

# 解析数据
quote = parser.parse(data, source="efinance")

# 批量解析
quotes = parser.parse_batch(data_list, source="efinance")
```

### 2. 持仓市值计算引擎 (`src/services/position_mtm_engine.py`)

实时计算持仓市值和盈亏：

```python
from src.services.position_mtm_engine import get_mtm_engine

engine = get_mtm_engine()

# 注册持仓
engine.register_position(
    position_id="pos_001",
    portfolio_id="portfolio_001",
    symbol="600519",
    quantity=100,
    avg_price=1800.00
)

# 更新价格
updates = engine.update_price("600519", 1850.00)

# 批量更新
await engine.update_price_batch({"600519": 1850.00, "000001": 12.50})

# 获取组合快照
snapshot = engine.get_portfolio_snapshot("portfolio_001")
```

### 3. 性能优化模块 (`src/services/performance_optimizer.py`)

提供 LRU 缓存、批量处理器等优化功能：

```python
from src.services.performance_optimizer import (
    get_cache,
    get_batch_processor,
    get_performance_monitor
)

cache = get_cache()
cache.set("key", value)
value = cache.get("key")

batch_processor = get_batch_processor()
await batch_processor.add(item)

monitor = get_performance_monitor()
monitor.record_latency("operation", 0.05)
```

## WebSocket API

### 实时行情 WebSocket

```
ws://host/api/ws/market?client_id=xxx
```

消息格式：

```json
{
  "action": "subscribe",
  "symbol": "600519"
}
```

### 持仓市值 WebSocket

```
ws://host/api/ws/portfolio?portfolio_id=xxx&client_id=xxx
```

支持的操作：
- `register_position`: 注册持仓
- `update_price`: 更新价格
- `get_snapshot`: 获取快照
- `subscribe`: 订阅
- `unsubscribe`: 取消订阅
- `ping`: 心跳

## REST API

### 获取实时行情

```bash
GET /api/realtime/quote/{symbol}
GET /api/realtime/quotes?symbols=600519,000001
```

### 持仓市值

```bash
GET /api/mtm/portfolio/{portfolio_id}
GET /api/mtm/position/{position_id}
GET /api/mtm/stats
```

## 前端集成

```typescript
import { useRealtimeMarket } from '@/services/realtimeMarket'

const {
  service,
  connectionStatus,
  isConnected,
  connectWebSocket,
  getQuote,
  getPortfolioMTM,
  subscribe,
  on
} = useRealtimeMarket()

// 连接 WebSocket
connectWebSocket('portfolio_001')

// 监听更新
on('portfolio_update', (data) => {
  console.log('Portfolio updated:', data.snapshot)
})

// 获取行情
const quote = await getQuote('600519')

// 注册持仓
registerPosition('pos_001', '600519', 100, 1800.00)
```

## 错误处理和重连

模块已集成现有的重连管理器：
- 指数退避重连
- 断路器模式
- 心跳检测
- 消息队列

## 测试

```bash
# 运行单元测试
pytest tests/unit/test_realtime_integration.py -v

# 运行所有测试
pytest tests/unit/ -v
```

## 性能指标

- 批量更新：支持最多 500 个股票同时更新
- 缓存大小：默认 10,000 条
- 更新延迟：< 10ms
- WebSocket 心跳间隔：30 秒

## 文件结构

```
src/services/
├── market_data_parser.py      # 行情数据解析器
├── position_mtm_engine.py     # 持仓市值计算引擎
└── performance_optimizer.py   # 性能优化模块

web/backend/app/api/
└── realtime_market.py         # WebSocket 和 REST API

web/frontend/src/
├── services/
│   └── realtimeMarket.ts      # 前端 API 服务
└── components/realtime/
    └── RealtimePositionPanel.vue  # 实时持仓组件
```
