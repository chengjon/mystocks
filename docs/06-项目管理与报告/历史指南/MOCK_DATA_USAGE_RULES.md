# Mock数据使用规则文档

## 概述

本文档规定了 MyStocks 项目中 Mock 数据的使用规则，确保代码质量和数据管理的一致性。

**核心原则**: 所有模拟数据必须通过 Mock 数据模块提供，**严禁在业务代码中直接硬编码数据**。

---

## Mock数据架构

### 三层数据源架构

```
┌─────────────────────────────────────────────────────────────┐
│                    业务数据源 (Business)                      │
│                       business_mock.py                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐       │
│  │  时序数据源            │    │  关系数据源           │       │
│  │  (TimeSeries)         │    │  (Relational)        │       │
│  │  timeseries_mock.py   │    │  relational_mock.py  │       │
│  └──────────────────────┘    └──────────────────────┘       │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                    数据源工厂 (Factory)                       │
│                        factory.py                            │
└─────────────────────────────────────────────────────────────┘
```

### 数据源切换机制

通过环境变量控制数据源类型：

| 环境变量 | 可选值 | 说明 |
|---------|--------|------|
| `TIMESERIES_DATA_SOURCE` | mock / tdengine | 时序数据源 |
| `RELATIONAL_DATA_SOURCE` | mock / postgresql | 关系数据源 |
| `BUSINESS_DATA_SOURCE` | mock / composite | 业务数据源 |
| `USE_MOCK_DATA` | true / false | 全局Mock开关 |

---

## Mock数据文件清单

### 1. 核心数据源模块 (`src/data_sources/`)

| 文件路径 | 用途 | 关键接口 |
|---------|------|---------|
| `factory.py` | 数据源工厂 | `get_timeseries_source()`, `get_relational_source()`, `get_business_source()` |
| `mock/timeseries_mock.py` | Mock时序数据 | `get_realtime_quotes()`, `get_kline_data()`, `get_fund_flow()` |
| `mock/relational_mock.py` | Mock关系数据 | `get_watchlist()`, `get_strategy_configs()`, `search_stocks()` |
| `mock/business_mock.py` | Mock业务数据 | `get_dashboard_summary()`, `execute_backtest()`, `calculate_risk_metrics()` |

### 2. 页面Mock模块 (`src/mock/`)

| 文件名 | 用途 | 主要函数 |
|--------|------|----------|
| `mock_Dashboard.py` | 仪表盘数据 | `get_market_hot()`, `get_plate_performance()`, `get_fund_flow()` |
| `mock_Market.py` | 市场行情 | `get_market_heatmap()`, `get_real_time_quotes()`, `get_etf_list()` |
| `mock_Stocks.py` | 股票详情 | `get_stock_list()`, `get_real_time_quote()`, `get_history_profit()` |
| `mock_TechnicalAnalysis.py` | 技术分析 | `get_stock_kline()`, `get_technical_indicators()`, `get_signal_analysis()` |
| `mock_Wencai.py` | 问财查询 | `get_wencai_queries()`, `get_query_results()` |
| `mock_StrategyManagement.py` | 策略管理 | `get_strategy_definitions()`, `run_strategy_single()`, `get_strategy_results()` |
| `mock_RealTimeMonitor.py` | 实时监控 | `get_realtime_alerts()`, `get_monitoring_summary()` |
| `mock_IndicatorLibrary.py` | 指标库 | `get_indicator_list()`, `get_indicator_detail()` |

### 3. 后端统一Mock管理 (`web/backend/app/mock/`)

| 文件名 | 用途 | 主要函数 |
|--------|------|----------|
| `unified_mock_data.py` | 统一Mock管理 | `get_dashboard_data()`, `get_stocks_data()`, `get_technical_data()` |

---

## 使用规则

### 规则1: 禁止硬编码数据

**错误示例** ❌
```python
# 直接在代码中写入数据 - 严禁!
def get_stock_info():
    return {
        "symbol": "600000",
        "name": "浦发银行",
        "price": 12.50,
        "change": 0.15,
        "volume": 12345678
    }
```

**正确示例** ✅
```python
from src.data_sources.factory import get_timeseries_source

def get_stock_info(symbol: str):
    source = get_timeseries_source(source_type="mock")
    return source.get_realtime_quotes([symbol])[0]
```

### 规则2: 通过工厂函数获取数据源

**错误示例** ❌
```python
# 直接实例化Mock类 - 不推荐
from src.data_sources.mock.timeseries_mock import MockTimeSeriesDataSource
source = MockTimeSeriesDataSource()
```

**正确示例** ✅
```python
# 通过工厂函数获取 - 推荐
from src.data_sources.factory import get_timeseries_source

source = get_timeseries_source(source_type="mock")
data = source.get_kline_data(
    symbol="600000",
    start_time=datetime(2025, 1, 1),
    end_time=datetime(2025, 10, 31),
    interval="1d"
)
```

### 规则3: 使用统一的数据接口

**时序数据获取**:
```python
from src.data_sources.factory import get_timeseries_source

source = get_timeseries_source(source_type="mock")

# K线数据
kline_df = source.get_kline_data(symbol, start_time, end_time, interval)

# 实时行情
quotes = source.get_realtime_quotes(symbols)

# 资金流向
fund_flow = source.get_fund_flow(symbol, days)

# 市场概览
overview = source.get_market_overview()
```

**关系数据获取**:
```python
from src.data_sources.factory import get_relational_source

source = get_relational_source(source_type="mock")

# 自选股
watchlist = source.get_watchlist(user_id)

# 股票搜索
results = source.search_stocks(keyword)

# 行业列表
industries = source.get_industry_list()
```

**业务数据获取**:
```python
from src.data_sources.factory import get_business_source

source = get_business_source(source_type="mock")

# 仪表盘数据
dashboard = source.get_dashboard_summary()

# 回测执行
backtest_result = source.execute_backtest(strategy_config, start_date, end_date)

# 风险指标
risk_metrics = source.calculate_risk_metrics(portfolio_id)
```

### 规则4: 参数优化中的Mock数据使用

在策略参数优化中，必须使用Mock数据源而非硬编码数据：

**错误示例** ❌
```python
# 硬编码历史数据 - 严禁!
def run_backtest(params):
    historical_data = [
        {"date": "2025-01-01", "close": 10.5},
        {"date": "2025-01-02", "close": 10.8},
        # ... 直接写入数据
    ]
    return simulate(historical_data, params)
```

**正确示例** ✅
```python
from src.data_sources.factory import get_timeseries_source

def run_backtest(params):
    source = get_timeseries_source(source_type="mock")
    historical_data = source.get_kline_data(
        symbol="600000",
        start_time=datetime(2025, 1, 1),
        end_time=datetime(2025, 10, 31),
        interval="1d"
    )
    return simulate(historical_data, params)
```

### 规则5: 支持随机种子保证可复现

Mock数据支持随机种子，确保测试结果可复现：

```python
from src.data_sources.factory import get_timeseries_source

# 设置随机种子
source = get_timeseries_source(source_type="mock")
source.set_random_seed(42)

# 现在生成的数据是可复现的
data1 = source.get_kline_data(symbol, start, end)

# 重新设置相同种子，得到相同数据
source.set_random_seed(42)
data2 = source.get_kline_data(symbol, start, end)
# data1 == data2
```

### 规则6: 保持数据结构一致性

Mock数据结构应与真实API返回一致，便于无缝切换：

```python
# Mock数据结构必须与真实API一致
def get_stock_quote(symbol: str) -> Dict:
    return {
        "symbol": symbol,           # 股票代码
        "name": "示例股票",          # 股票名称
        "price": 25.50,             # 当前价格
        "change": 0.35,             # 涨跌额
        "change_pct": 1.39,         # 涨跌幅%
        "volume": 12345678,         # 成交量
        "amount": 315678900,        # 成交额
        "high": 26.00,              # 最高价
        "low": 24.80,               # 最低价
        "open": 25.20,              # 开盘价
        "pre_close": 25.15,         # 昨收价
        "timestamp": datetime.now().isoformat()
    }
```

---

## 添加新Mock数据的流程

### 1. 确定数据类别

| 数据类型 | 对应模块 | 说明 |
|---------|---------|------|
| 行情/K线 | `timeseries_mock.py` | 时序类数据 |
| 用户/配置 | `relational_mock.py` | 关系类数据 |
| 业务/分析 | `business_mock.py` | 复合业务数据 |
| 页面专用 | `src/mock/mock_*.py` | 页面级数据 |

### 2. 实现数据生成函数

```python
# 在对应的mock模块中添加
def get_new_feature_data(
    param1: str,
    param2: int = 10
) -> Dict[str, Any]:
    """
    获取新功能数据

    Args:
        param1: 参数1说明
        param2: 参数2说明 (默认10)

    Returns:
        包含新功能数据的字典
    """
    # 使用随机数生成器
    import random
    rng = random.Random(42)  # 可复现

    return {
        "field1": rng.uniform(0, 100),
        "field2": rng.randint(1, 1000),
        "field3": [rng.random() for _ in range(param2)],
        "timestamp": datetime.now().isoformat()
    }
```

### 3. 导出函数

```python
# 在模块的 __all__ 中添加
__all__ = [
    'get_realtime_quotes',
    'get_kline_data',
    'get_new_feature_data',  # 新增
]
```

### 4. 更新工厂函数（如需要）

如果是新的数据源类型，需要在 `factory.py` 中注册。

---

## 导入规范

### 推荐的导入方式

```python
# 方式1: 通过工厂函数 (最推荐)
from src.data_sources.factory import get_timeseries_source
source = get_timeseries_source(source_type="mock")

# 方式2: 从统一管理模块导入
from web.backend.app.mock.unified_mock_data import get_dashboard_data
data = get_dashboard_data()

# 方式3: 从具体模块导入具体函数
from src.mock.mock_Dashboard import get_market_hot
data = get_market_hot()
```

### 避免的导入方式

```python
# 避免: 通配符导入
from src.mock.mock_Dashboard import *

# 避免: 直接访问内部变量
from src.data_sources.mock import timeseries_mock
data = timeseries_mock._internal_data  # 禁止!

# 避免: 硬编码实例化
source = MockTimeSeriesDataSource()  # 应使用工厂函数
```

---

## 环境变量配置

### 开发环境 (.env.development)
```bash
USE_MOCK_DATA=true
TIMESERIES_DATA_SOURCE=mock
RELATIONAL_DATA_SOURCE=mock
BUSINESS_DATA_SOURCE=mock
```

### 生产环境 (.env.production)
```bash
USE_MOCK_DATA=false
TIMESERIES_DATA_SOURCE=tdengine
RELATIONAL_DATA_SOURCE=postgresql
BUSINESS_DATA_SOURCE=composite
```

---

## 代码审查检查清单

在代码审查时，请检查以下项目：

- [ ] 没有硬编码的模拟数据
- [ ] 所有数据通过工厂函数或Mock模块的getter函数获取
- [ ] 导入路径正确
- [ ] 函数有类型注解和文档字符串
- [ ] 数据结构与预期API一致
- [ ] 新增的Mock函数已添加到对应模块
- [ ] 支持随机种子实现可复现性
- [ ] 没有使用通配符导入

---

## 常见问题

### Q: 为什么不能直接在代码中写数据？

A: 直接硬编码数据会导致：
- 代码难以维护和修改
- 无法统一管理数据质量
- 切换真实数据源时需要大量修改
- 违反DRY原则（Don't Repeat Yourself）
- 难以保证数据的一致性和真实性

### Q: Mock数据和真实数据结构不一致怎么办？

A: 应该以真实API的数据结构为准，修改Mock数据使其保持一致。如果真实API结构发生变化，需要同步更新Mock模块。

### Q: 如何生成符合市场规律的K线数据？

A: 参考 `timeseries_mock.py` 中的实现：
- 价格使用对数正态分布
- 涨跌幅限制在-10%到+10%
- 成交量在合理范围内波动
- 高开低收价格关系合理

### Q: 参数优化时Mock数据不够用怎么办？

A: Mock数据源支持动态生成任意时间范围的数据：
```python
source = get_timeseries_source(source_type="mock")
# 可以请求任意时间范围
data = source.get_kline_data(
    symbol="600000",
    start_time=datetime(2020, 1, 1),
    end_time=datetime(2025, 12, 31),
    interval="1d"
)
```

---

## 相关文件索引

| 文件 | 说明 |
|------|------|
| `src/data_sources/factory.py` | 数据源工厂 (入口) |
| `src/data_sources/mock/` | Mock数据源实现目录 |
| `src/mock/` | 页面级Mock数据目录 |
| `web/backend/app/mock/` | 后端统一Mock管理 |
| `scripts/tests/test_mock_*.py` | Mock测试脚本 |
| `examples/mock_data_demo.py` | Mock使用演示 |
| `CLAUDE.md` | 项目开发规范 |

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2025-11-22 | 初始版本，建立Mock数据使用规范 |
