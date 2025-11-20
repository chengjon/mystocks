# MyStocks Mock数据系统快速参考

## 快速启用Mock数据

### 1. 环境变量设置

```bash
# 方法1: 设置环境变量
export USE_MOCK_DATA=true

# 方法2: 在Python代码中设置
import os
os.environ['USE_MOCK_DATA'] = 'true'
```

### 2. 前端页面Mock数据覆盖情况

| 前端页面 | API端点 | Mock数据类型 | 状态 |
|---------|---------|-------------|------|
| Dashboard.vue | `/api/dashboard/*` | `dashboard` | ✅ 已支持 |
| MarketData.vue | `/api/market/*` | `market_*` | ✅ 新增支持 |
| Stocks.vue | `/api/stock/*` | `stock_*` | ✅ 新增支持 |
| TradingView组件 | `/api/tradingview/*` | `tradingview_*` | ✅ 新增支持 |
| TechnicalAnalysis.vue | `/api/technical/*` | `technical` | ✅ 已支持 |
| Wencai.vue | `/api/wencai/*` | `wencai` | ✅ 已支持 |
| RealTimeMonitor.vue | `/api/monitoring/*` | `monitoring` | ✅ 已支持 |

## Mock数据类型详情

### 市场数据 (market_*)
```python
# 市场热力图
manager.get_data('market_heatmap', market='cn', limit=50)

# 实时行情
manager.get_data('real_time_quotes', symbols=['000001', '000002'])

# 股票列表
manager.get_data('stock_list', limit=100, search='平安')

# 资金流向
manager.get_data('fund_flow', symbol='000001', timeframe='1')

# ETF列表
manager.get_data('etf_list', keyword='指数', limit=50)
```

### 股票搜索 (stock_*)
```python
# 股票搜索
manager.get_data('stock_search', keyword='平安', limit=20)

# 股票报价
manager.get_data('stock_quote', symbol='000001', market='cn')

# 公司信息
manager.get_data('stock_profile', symbol='000001')

# 股票新闻
manager.get_data('stock_news', symbol='000001', days=7)

# 分析师推荐
manager.get_data('stock_recommendation', symbol='000001')
```

### TradingView (tradingview_*)
```python
# TradingView图表配置
manager.get_data('tradingview_chart', 
                symbol='000001', 
                market='CN',
                interval='D',
                theme='dark',
                locale='zh_CN')

# 迷你图表
manager.get_data('tradingview_mini_chart',
                symbol='000001',
                theme='dark',
                locale='zh_CN')

# 滚动行情条
manager.get_data('tradingview_ticker_tape',
                symbols=['000001', '000002'],
                theme='dark')

# 市场概览
manager.get_data('tradingview_market_overview',
                market='china',
                theme='dark')
```

## API端点Mock集成示例

### 市场热力图API
```python
@router.get("/heatmap")
async def get_market_heatmap(
    market: str = Query(default="cn"),
    limit: int = Query(default=50),
    current_user: User = Depends(get_current_user)
):
    use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
    
    if use_mock:
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
        # 真实数据获取逻辑
        # ...
```

### 股票搜索API
```python
@router.get("/search")
async def search_stocks(
    q: str = Query(..., description="搜索关键词"),
    market: str = Query("auto", description="市场类型"),
    current_user: User = Depends(get_current_user)
):
    use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
    
    if use_mock:
        from app.mock.unified_mock_data import get_mock_data_manager
        mock_manager = get_mock_data_manager()
        mock_data = mock_manager.get_data("stock_search", keyword=q, market=market)
        return mock_data.get("data", [])
    else:
        # 真实搜索逻辑
        # ...
```

## 前端调用示例

### Vue组件中调用
```javascript
// 市场热力图
async loadMarketHeatmap() {
  const response = await fetch('/api/market/heatmap?market=cn&limit=50', {
    headers: { 'Authorization': `Bearer ${this.getToken()}` }
  });
  const data = await response.json();
  this.heatmapData = data.data;
}

// 股票搜索
async searchStocks(keyword) {
  const response = await fetch(`/api/stock/search?q=${keyword}`, {
    headers: { 'Authorization': `Bearer ${this.getToken()}` }
  });
  const results = await response.json();
  this.searchResults = results;
}

// TradingView图表
async loadTradingView(symbol) {
  const response = await fetch('/api/tradingview/chart/config', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.getToken()}`
    },
    body: JSON.stringify({
      symbol: symbol,
      market: 'CN',
      interval: 'D',
      theme: 'dark',
      locale: 'zh_CN'
    })
  });
  const config = await response.json();
  this.initTradingView(config.config);
}
```

## 数据源切换

### 自动降级机制
```python
def get_data_with_fallback(data_type: str, **kwargs):
    """带降级的数据获取"""
    try:
        # 尝试使用真实数据
        return get_real_data(data_type, **kwargs)
    except Exception as e:
        logger.warning(f"真实数据获取失败，降级到Mock数据: {e}")
        # 降级到Mock数据
        mock_manager = get_mock_data_manager()
        return mock_manager.get_data(data_type, **kwargs)
```

### 手动切换模式
```python
from app.mock.unified_mock_data import get_mock_data_manager

manager = get_mock_data_manager()

# 切换到Mock模式
manager.set_mock_mode(True)

# 切换到真实数据模式
manager.set_mock_mode(False)

# 查看缓存信息
cache_info = manager.get_cache_info()
print(f"缓存大小: {cache_info['cache_size']}")
print(f"当前模式: {'Mock' if cache_info['mock_mode'] else '真实数据'}")

# 清除缓存
manager.clear_cache()
```

## 测试验证

### 验证Mock数据可用性
```python
import os
os.environ['USE_MOCK_DATA'] = 'true'

from app.mock.unified_mock_data import get_mock_data_manager

manager = get_mock_data_manager()

# 测试所有数据类型
test_cases = [
    ('market_heatmap', {'market': 'cn', 'limit': 10}),
    ('stock_search', {'keyword': '平安', 'limit': 5}),
    ('tradingview_chart', {'symbol': '000001', 'market': 'CN'}),
    ('stock_quote', {'symbol': '000001', 'market': 'cn'}),
]

for data_type, params in test_cases:
    try:
        result = manager.get_data(data_type, **params)
        print(f"✅ {data_type}: 测试通过")
    except Exception as e:
        print(f"❌ {data_type}: 测试失败 - {e}")
```

### 验证API端点
```bash
# 测试API端点Mock集成
curl -H "Authorization: Bearer <token>" \
     -H "USE_MOCK_DATA: true" \
     http://localhost:8888/api/market/heatmap?market=cn&limit=10

curl -H "Authorization: Bearer <token>" \
     -H "USE_MOCK_DATA: true" \
     http://localhost:8888/api/stock/search?q=平安
```

## 最佳实践

### 1. 开发阶段
- ✅ 设置 `USE_MOCK_DATA=true`
- ✅ 使用Mock数据进行UI开发和调试
- ✅ 利用稳定的Mock数据验证前端逻辑

### 2. 测试阶段
- ✅ 使用Mock数据进行单元测试
- ✅ 模拟各种边界情况
- ✅ 测试错误处理和降级逻辑

### 3. 部署阶段
- ⚠️ 设置 `USE_MOCK_DATA=false`
- ⚠️ 确保真实数据库连接正常
- ⚠️ 监控数据源切换日志

### 4. 性能优化
- ✅ 利用内置缓存机制
- ✅ 定期清除过期缓存
- ✅ 监控缓存命中率

## 故障排查

### 常见问题

1. **Mock数据无法加载**
   ```python
   # 检查环境变量
   import os
   print(f"USE_MOCK_DATA: {os.getenv('USE_MOCK_DATA')}")
   
   # 检查模块导入
   try:
       from app.mock.unified_mock_data import get_mock_data_manager
       print("✅ Mock数据管理器导入成功")
   except ImportError as e:
       print(f"❌ Mock数据管理器导入失败: {e}")
   ```

2. **API端点返回空数据**
   ```python
   # 检查Mock数据管理器状态
   manager = get_mock_data_manager()
   print(f"Mock模式: {manager.use_mock_data}")
   print(f"缓存大小: {len(manager._data_cache)}")
   
   # 清除缓存后重试
   manager.clear_cache()
   ```

3. **缓存问题**
   ```python
   # 检查缓存有效性
   cache_info = manager.get_cache_info()
   if cache_info['cache_size'] > 100:
       print("缓存过大，建议清除")
       manager.clear_cache()
   ```

## 扩展开发

### 添加新的Mock数据类型
```python
# 1. 在unified_mock_data.py中添加处理逻辑
elif data_type == "new_data_type":
    try:
        from src.mock.mock_NewModule import get_new_data
        data = get_new_data(**kwargs)
        return {"data": data, "timestamp": datetime.now().isoformat(), "source": "mock"}
    except ImportError:
        # 返回备用数据
        return {"data": [], "timestamp": datetime.now().isoformat(), "source": "mock"}

# 2. 创建对应的Mock模块
# src/mock/mock_NewModule.py
def get_new_data(param1: str = "", param2: int = 10) -> list:
    """生成新类型数据"""
    return [{"id": i, "value": param2 * i} for i in range(param2)]
```

### 优化Mock数据生成
```python
def generate_realistic_data(count: int = 100) -> list:
    """生成更真实的Mock数据"""
    import random
    import numpy as np
    
    # 使用正态分布生成更真实的价格数据
    prices = np.random.normal(50, 15, count)
    
    return [
        {
            "symbol": f"{i:06d}",
            "price": round(max(price, 1), 2),  # 确保价格为正
            "volume": random.randint(1000, 1000000),
            "change": round(random.uniform(-5, 5), 2)
        }
        for i, price in enumerate(prices, 1)
    ]
```

---

**Mock数据系统版本**: v2.0.0  
**最后更新**: 2025-11-13  
**覆盖范围**: 100% 前端页面数据需求  