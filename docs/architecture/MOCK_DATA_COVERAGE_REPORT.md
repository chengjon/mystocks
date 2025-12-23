# MyStocks Mock数据系统覆盖报告

## 概述

本报告分析了MyStocks系统的前端页面与Mock数据系统的对应关系，为前端开发和测试提供详细的技术参考。

### Mock数据系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                  UnifiedMockDataManager                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              _get_mock_data()                       │   │
│  │  ├── Dashboard (已有)                               │   │
│  │  ├── Stocks (已有)                                  │   │
│  │  ├── Technical (已有)                               │   │
│  │  ├── Wencai (已有)                                  │   │
│  │  ├── Strategy (已有)                                │   │
│  │  ├── Monitoring (已有)                              │   │
│  │  ├── MarketData (新增) ◀─────────────────────────┐  │   │
│  │  ├── StockSearch (新增) ◀───────────────────────┐  │   │
│  │  └── TradingView (新增) ◀─────────────────────┐  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  mock_Market    │  │ mock_StockSearch│  │mock_TradingView │
│                │  │                │  │                │
│ 8个函数        │  │ 4个函数        │  │ 6个函数        │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 前端页面与API端点对应关系

### 1. 市场数据模块 (MarketData.vue)

**前端页面**: `/src/views/MarketData.vue`

**API依赖**:
```javascript
// 市场热力图
GET /api/market/heatmap

// 实时行情
GET /api/market/realtime

// 股票列表
GET /api/market/stock-list

// 资金流向
GET /api/market/fund-flow

// ETF列表
GET /api/market/etf-list

// 筹码分布
GET /api/market/chip-distribution

// 龙虎榜详情
GET /api/market/lhb-detail
```

**Mock数据类型**: `market_*`
- `market_heatmap`: 市场热力图数据
- `real_time_quotes`: 实时行情数据
- `stock_list`: 股票列表数据
- `fund_flow`: 资金流向数据
- `etf_list`: ETF列表数据
- `chip_race`: 筹码分布数据
- `lhb_detail`: 龙虎榜详情数据

**实现状态**: ✅ **完全支持**

### 2. 股票搜索模块

**前端页面**: `/src/views/Stocks.vue`

**API依赖**:
```javascript
// 股票搜索
GET /api/stock/search?q={keyword}

// 股票报价
GET /api/stock/quote/{symbol}

// 公司信息
GET /api/stock/profile/{symbol}

// 股票新闻
GET /api/stock/news/{symbol}

// 分析师推荐
GET /api/stock/recommendation/{symbol}
```

**Mock数据类型**: `stock_*`
- `stock_search`: 股票搜索数据
- `stock_quote`: 股票报价数据
- `stock_profile`: 公司信息数据
- `stock_news`: 股票新闻数据
- `stock_recommendation`: 分析师推荐数据

**实现状态**: ✅ **完全支持**

### 3. TradingView图表模块

**前端页面**: `/src/components/TradingViewWidget.vue`

**API依赖**:
```javascript
// TradingView图表配置
POST /api/tradingview/chart/config

// 迷你图表配置
POST /api/tradingview/mini-chart

// 滚动行情条
POST /api/tradingview/ticker-tape

// 市场概览
POST /api/tradingview/market-overview

// 股票筛选器
POST /api/tradingview/screener

// 代码格式转换
GET /api/tradingview/symbol-convert
```

**Mock数据类型**: `tradingview_*`
- `tradingview_chart`: TradingView图表配置
- `tradingview_mini_chart`: 迷你图表配置
- `tradingview_ticker_tape`: 滚动行情配置
- `tradingview_market_overview`: 市场概览配置
- `tradingview_screener`: 股票筛选器配置
- `tradingview_symbol_convert`: 代码格式转换

**实现状态**: ✅ **完全支持**

### 4. 仪表板模块 (Dashboard.vue)

**前端页面**: `/src/views/Dashboard.vue`

**API依赖**:
```javascript
// 市场概览
GET /api/dashboard/market-overview

// 市场统计
GET /api/dashboard/market-stats

// 市场热力图
GET /api/dashboard/market-heat

// 领涨板块
GET /api/dashboard/leading-sectors
```

**Mock数据类型**: `dashboard`
- `dashboard`: 仪表板数据（包含市场概览、统计、热力图、板块等）

**实现状态**: ✅ **已有支持**

### 5. 技术分析模块 (TechnicalAnalysis.vue)

**前端页面**: `/src/views/TechnicalAnalysis.vue`

**API依赖**:
```javascript
// 技术指标
GET /api/technical/{symbol}/indicators

// 交易信号
GET /api/technical/{symbol}/signals

// 趋势分析
GET /api/technical/{symbol}/trend

// 动量分析
GET /api/technical/{symbol}/momentum
```

**Mock数据类型**: `technical`
- `technical`: 技术分析数据

**实现状态**: ✅ **已有支持**

### 6. 问财模块 (Wencai.vue)

**前端页面**: `/src/views/Wencai.vue`

**API依赖**:
```javascript
// 获取问财查询
GET /api/wencai/queries

// 获取查询结果
GET /api/wencai/query-results/{query_name}
```

**Mock数据类型**: `wencai`
- `wencai`: 问财数据

**实现状态**: ✅ **已有支持**

### 7. 实时监控模块 (RealTimeMonitor.vue)

**前端页面**: `/src/views/RealTimeMonitor.vue`

**API依赖**:
```javascript
// 实时告警
GET /api/monitoring/realtime

// 龙虎榜数据
GET /api/monitoring/dragon-tiger

// 监控摘要
GET /api/monitoring/summary
```

**Mock数据类型**: `monitoring`
- `monitoring`: 监控数据

**实现状态**: ✅ **已有支持**

## Mock数据系统使用指南

### 1. 环境变量配置

```bash
# 启用Mock数据
export USE_MOCK_DATA=true

# 禁用Mock数据（使用真实数据库）
export USE_MOCK_DATA=false
```

### 2. 前端页面使用示例

#### Vue组件中使用

```javascript
// 在Vue组件中调用API
export default {
  methods: {
    async loadMarketData() {
      try {
        const response = await fetch('/api/market/heatmap?market=cn&limit=50', {
          headers: {
            'Authorization': `Bearer ${this.getToken()}`
          }
        });
        const data = await response.json();
        this.heatmapData = data.data;
      } catch (error) {
        console.error('获取市场数据失败:', error);
      }
    }
  }
}
```

#### 图表组件中使用

```javascript
// TradingView图表配置
export default {
  async loadTradingView() {
    try {
      const response = await fetch('/api/tradingview/chart/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getToken()}`
        },
        body: JSON.stringify({
          symbol: '000001',
          market: 'CN',
          interval: 'D',
          theme: 'dark',
          locale: 'zh_CN',
          container_id: 'tradingview_chart'
        })
      });
      const config = await response.json();
      this.initTradingView(config.config);
    } catch (error) {
      console.error('加载TradingView图表失败:', error);
    }
  }
}
```

### 3. Mock数据管理器直接调用

```python
# 在Python中直接使用Mock数据管理器
from app.mock.unified_mock_data import get_mock_data_manager

manager = get_mock_data_manager()

# 获取市场热力图数据
heatmap_data = manager.get_data('market_heatmap', market='cn', limit=50)

# 获取股票搜索结果
search_results = manager.get_data('stock_search', keyword='平安', limit=10)

# 获取TradingView图表配置
chart_config = manager.get_data('tradingview_chart',
                               symbol='000001',
                               market='CN',
                               theme='dark',
                               locale='zh_CN')
```

### 4. API端点中的Mock集成

```python
@router.get("/heatmap")
async def get_market_heatmap(
    market: str = Query(default="cn", description="市场类型"),
    limit: int = Query(default=50, description="返回股票数量"),
    current_user: User = Depends(get_current_user),
):
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'

        if use_mock:
            # 使用Mock数据
            from app.mock.unified_mock_data import get_mock_data_manager
            mock_manager = get_mock_data_manager()
            mock_data = mock_manager.get_data("market_heatmap", market=market, limit=limit)
            return {
                "success": True,
                "data": mock_data.get("data", []),
                "total": len(mock_data.get("data", [])),
                "timestamp": mock_data.get("timestamp"),
                "source": "mock"
            }
        else:
            # 使用真实数据
            # ... 现有真实数据获取逻辑 ...

    except Exception as e:
        # 错误处理和降级逻辑
        logger.error(f"获取市场热力图失败: {str(e)}", exc_info=True)
        # 如果真实数据获取失败，降级到Mock数据
        return await get_market_heatmap_with_mock_fallback(market, limit, current_user)
```

## Mock数据结构说明

### 1. 市场数据Mock

```json
{
  "market_heatmap": {
    "data": [
      {
        "symbol": "000001",
        "name": "平安银行",
        "current": 15.32,
        "change": 0.45,
        "changePercent": 3.03,
        "volume": 123456789,
        "amount": 1890456789.45,
        "marketCap": 296786.54,
        "industry": "银行业",
        "timestamp": "2025-11-13T10:30:00.000Z"
      }
    ],
    "total": 50,
    "timestamp": "2025-11-13T10:30:00.000Z",
    "source": "mock"
  }
}
```

### 2. 股票搜索Mock

```json
{
  "stock_search": {
    "data": [
      {
        "symbol": "000001",
        "description": "平安银行",
        "displaySymbol": "000001.SZ",
        "type": "Common Stock",
        "exchange": "SZSE",
        "market": "cn"
      }
    ],
    "total": 20,
    "timestamp": "2025-11-13T10:30:00.000Z",
    "source": "mock"
  }
}
```

### 3. TradingView配置Mock

```json
{
  "tradingview_chart": {
    "config": {
      "container_id": "tradingview_chart",
      "symbol": "000001.SS",
      "theme": "dark",
      "locale": "zh_CN",
      "interval": "D",
      "studies": [
        "MACD@tv-basicstudies",
        "RSI@tv-basicstudies"
      ],
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "save_image": false,
      "height": 600,
      "width": "100%"
    },
    "timestamp": "2025-11-13T10:30:00.000Z",
    "source": "mock"
  }
}
```

## Mock数据系统优势

### 1. 开发效率提升
- **快速原型**: 无需依赖真实数据库即可进行前端开发
- **一致性数据**: 确保开发、测试环境的数据一致性
- **离线工作**: 支持完全离线的开发环境

### 2. 测试友好
- **可预测性**: Mock数据稳定，便于测试
- **边界测试**: 可生成各种边界情况的数据
- **性能测试**: 可模拟大量数据的性能表现

### 3. 架构优势
- **松耦合**: 前端不依赖后端具体实现
- **快速切换**: 一键切换Mock/真实数据
- **缓存优化**: 内置缓存机制，提高性能

### 4. 错误处理
- **自动降级**: 真实数据获取失败时自动切换到Mock数据
- **错误恢复**: Mock数据加载失败时提供备用方案
- **日志追踪**: 完整的数据源切换日志

## 扩展指南

### 1. 添加新的Mock数据类型

```python
# 在unified_mock_data.py中添加新的数据类型支持
elif data_type == "new_data_type":
    try:
        # 尝试导入对应的Mock模块
        from src.mock.mock_NewModule import get_new_data
        data = get_new_data(**kwargs)
        return {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }
    except ImportError:
        # 返回备用Mock数据
        return {
            "data": generate_fallback_data(),
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }
```

### 2. 创建新的Mock模块

```python
# 在src/mock/目录下创建新的Mock模块
# mock_NewModule.py

def get_new_data(param1: str = "", param2: int = 10) -> list:
    """获取新类型的数据

    Args:
        param1: 参数1
        param2: 参数2

    Returns:
        数据列表
    """
    return [
        {
            "id": i,
            "name": f"Item {i}",
            "value": param2 * i,
            "timestamp": datetime.now().isoformat()
        } for i in range(param2)
    ]
```

### 3. 配置Mock数据生成策略

```python
# 在Mock模块中添加更智能的数据生成
def generate_realistic_stock_data(count: int = 100) -> list:
    """生成更真实的股票数据"""
    import random
    import numpy as np

    stocks = []
    for i in range(count):
        # 生成更真实的价格分布
        base_price = random.uniform(10, 100)
        volatility = random.uniform(0.01, 0.1)

        stock = {
            "symbol": f"{i:06d}",
            "name": f"股票{i:03d}",
            "current": round(base_price, 2),
            "change": round(random.uniform(-5, 5), 2),
            "changePercent": round(random.uniform(-10, 10), 2),
            "volume": random.randint(1000000, 1000000000),
            "amount": random.randint(100000000, 100000000000),
            "marketCap": round(base_price * random.randint(1000000, 100000000), 2),
            "industry": random.choice(["科技", "医疗", "金融", "制造", "地产"]),
            "timestamp": datetime.now().isoformat()
        }
        stocks.append(stock)

    return stocks
```

## 测试验证

### 1. Mock数据系统测试

```bash
# 运行Mock数据系统测试
cd /opt/claude/mystocks_spec/web/backend
python -c "
import os
os.environ['USE_MOCK_DATA'] = 'true'
from app.mock.unified_mock_data import get_mock_data_manager

manager = get_mock_data_manager()

# 测试所有数据类型
test_types = [
    'market_heatmap',
    'stock_search',
    'tradingview_chart',
    'dashboard',
    'technical'
]

for data_type in test_types:
    try:
        result = manager.get_data(data_type)
        print(f'✅ {data_type}: 测试通过')
    except Exception as e:
        print(f'❌ {data_type}: 测试失败 - {e}')
"
```

### 2. API端点测试

```bash
# 测试API端点Mock集成
curl -H "Authorization: Bearer <token>" \
     -H "USE_MOCK_DATA: true" \
     http://localhost:8888/api/market/heatmap?market=cn&limit=10
```

### 3. 前端集成测试

```javascript
// 前端集成测试脚本
async function testMockIntegration() {
    const endpoints = [
        '/api/market/heatmap',
        '/api/stock/search?q=平安',
        '/api/tradingview/chart/config'
    ];

    for (const endpoint of endpoints) {
        try {
            const response = await fetch(endpoint);
            const data = await response.json();
            console.log(`✅ ${endpoint}: Mock集成成功`);
        } catch (error) {
            console.error(`❌ ${endpoint}: Mock集成失败`, error);
        }
    }
}
```

## 结论

MyStocks的Mock数据系统现在已经**完全覆盖**了所有主要前端页面的数据需求：

✅ **仪表板模块** - 完全支持
✅ **市场数据模块** - 完全支持
✅ **股票搜索模块** - 完全支持
✅ **TradingView图表模块** - 完全支持
✅ **技术分析模块** - 已有支持
✅ **问财模块** - 已有支持
✅ **实时监控模块** - 已有支持

**系统优势**:
- 统一的数据源管理
- 智能的数据降级机制
- 高性能的缓存策略
- 易于扩展的架构设计

**开发建议**:
1. 在开发阶段设置 `USE_MOCK_DATA=true`
2. 利用Mock数据进行前端功能验证
3. 通过Mock系统进行性能测试
4. 在部署前切换到真实数据源

Mock数据系统为MyStocks提供了强大的开发和测试基础设施，显著提高了开发效率和代码质量。
