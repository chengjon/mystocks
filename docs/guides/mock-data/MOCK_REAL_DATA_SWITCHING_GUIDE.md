# Mock/Real 数据切换指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 📋 目录

1. [架构概述](#架构概述)
2. [切换机制](#切换机制)
3. [数据源类型](#数据源类型)
4. [使用方法](#使用方法)
5. [实战示例](#实战示例)
6. [核心特性](#核心特性)
7. [常见问题](#常见问题)
8. [相关文档](#相关文档)

---

## 架构概述

### 三层数据源设计

```
┌──────────────────────────────────────────────────────────┐
│              业务层 (Business Layer)                      │
│         复杂业务逻辑、策略回测、风险分析                    │
├──────────────────────────────────────────────────────────┤
│           数据源工厂 (DataSourceFactory)                   │
│        环境变量驱动 → 动态路由 → 单例管理                   │
├──────────────────┬───────────────────────────────────────┤
│   Mock数据源      │            真实数据源                   │
│  (开发/测试)      │          (生产环境)                     │
│                  │                                       │
│ • 时序Mock       │  • TDengine (高频时序)                 │
│ • 关系Mock       │  • PostgreSQL (日线/参考/交易)           │
│ • 业务Mock       │  • Composite (复合业务)                 │
└──────────────────┴───────────────────────────────────────┘
```

### 核心组件

| 组件 | 位置 | 作用 |
|------|------|------|
| **DataSourceFactory** | `src/data_sources/factory.py` | 数据源工厂，统一管理和路由 |
| **Mock数据源** | `src/data_sources/mock/` | 开发测试用Mock数据 |
| **真实数据源** | `src/data_sources/real/` | 生产环境真实数据 |
| **接口定义** | `src/interfaces/` | 统一的数据源接口标准 |

---

## 切换机制

### 环境变量控制（核心开关）

通过 `.env` 文件控制数据源类型：

```bash
# ============================================
# 开发环境 - 全部使用Mock数据
# ============================================
TIMESERIES_DATA_SOURCE=mock      # 时序数据源
RELATIONAL_DATA_SOURCE=mock      # 关系数据源
BUSINESS_DATA_SOURCE=mock        # 业务数据源
USE_MOCK_DATA=true               # 全局开关

# ============================================
# 生产环境 - 使用真实数据库
# ============================================
TIMESERIES_DATA_SOURCE=tdengine     # TDengine高频数据
RELATIONAL_DATA_SOURCE=postgresql   # PostgreSQL通用数据
BUSINESS_DATA_SOURCE=composite      # 复合业务数据源
USE_MOCK_DATA=false
```

### 工厂模式自动路由

```python
# src/data_sources/factory.py

class DataSourceFactory:
    """数据源工厂 - 单例模式，环境变量驱动"""

    def get_timeseries_source(self, source_type=None):
        """
        智能获取数据源实例

        逻辑流程:
        1. source_type 为 None → 从环境变量读取
        2. source_type 指定 → 使用指定类型
        3. 单例缓存 → 避免重复创建
        """
        if source_type is None:
            # 从环境变量读取配置
            source_type = os.getenv("TIMESERIES_DATA_SOURCE", "mock")

        # 获取对应的实现类
        source_class = self._timeseries_registry[source_type]

        # 创建或返回缓存实例
        return source_class()
```

---

## 数据源类型

### 三种数据源对比

| 数据类型 | Mock实现 | 真实实现 | 用途 |
|---------|---------|---------|------|
| **时序数据** | `MockTimeSeriesDataSource` | `TDengineTimeSeriesDataSource` | K线、实时行情、资金流向 |
| **关系数据** | `MockRelationalDataSource` | `PostgreSQLRelationalDataSource` | 自选股、搜索、配置 |
| **业务数据** | `MockBusinessDataSource` | `CompositeBusinessDataSource` | 仪表盘、回测、风险指标 |

### 支持的数据源类型

```python
# 时序数据源
SUPPORTED_TIMESERIES_TYPES = ["mock", "tdengine", "api"]

# 关系数据源
SUPPORTED_RELATIONAL_TYPES = ["mock", "postgresql"]

# 业务数据源
SUPPORTED_BUSINESS_TYPES = ["mock", "composite"]
```

---

## 使用方法

### 方式1：环境变量驱动（推荐生产环境）

```bash
# 1. 设置环境变量
export TIMESERIES_DATA_SOURCE=tdengine
export RELATIONAL_DATA_SOURCE=postgresql

# 2. 代码中无需修改，自动使用真实数据
from src.data_sources.factory import get_timeseries_source

source = get_timeseries_source()  # 自动从环境变量读取
kline_data = source.get_kline_data("600000", start, end, "1d")
```

### 方式2：显式指定（推荐测试环境）

```python
from src.data_sources.factory import get_timeseries_source

# 强制使用Mock数据
mock_source = get_timeseries_source(source_type="mock")
data = mock_source.get_kline_data("600000", start, end, "1d")

# 强制使用真实数据
real_source = get_timeseries_source(source_type="tdengine")
data = real_source.get_kline_data("600000", start, end, "1d")
```

### 方式3：运行时切换（灵活调试）

```python
from src.data_sources.factory import DataSourceFactory

factory = DataSourceFactory()

# 开发阶段使用Mock
mock_data = factory.get_timeseries_source("mock").get_realtime_quotes(["600000"])

# 测试真实数据
real_data = factory.get_timeseries_source("tdengine").get_realtime_quotes(["600000"])

# 清除缓存，重新实例化
factory.clear_cache(category="timeseries")
```

---

## 实战示例

### 开发阶段（使用Mock）

**`.env.development` 配置**：
```bash
TIMESERIES_DATA_SOURCE=mock
RELATIONAL_DATA_SOURCE=mock
BUSINESS_DATA_SOURCE=mock
```

**代码示例**：
```python
from src.data_sources.factory import get_timeseries_source

source = get_timeseries_source()  # 自动使用Mock
quotes = source.get_realtime_quotes(["600000", "000001"])
print(quotes)
# 输出: [{'symbol': '600000', 'price': 25.50, 'change': 0.35, ...}]
```

### 生产环境（使用真实数据）

**`.env.production` 配置**：
```bash
TIMESERIES_DATA_SOURCE=tdengine
RELATIONAL_DATA_SOURCE=postgresql
BUSINESS_DATA_SOURCE=composite
```

**代码示例**（完全相同！）：
```python
from src.data_sources.factory import get_timeseries_source

source = get_timeseries_source()  # 自动使用TDengine
quotes = source.get_realtime_quotes(["600000", "000001"])
print(quotes)
# 输出: [{'symbol': '600000', 'price': 12.48, 'change': -0.15, ...}] 真实数据
```

### 混合使用（Mock + Real）

```python
from src.data_sources.factory import get_timeseries_source, get_relational_source

# 时序数据使用真实数据库
ts_source = get_timeseries_source(source_type="tdengine")
real_kline = ts_source.get_kline_data("600000", start, end, "1d")

# 关系数据使用Mock（测试中）
rel_source = get_relational_source(source_type="mock")
mock_watchlist = rel_source.get_watchlist(user_id=1)
```

---

## 核心特性

### 1. 统一接口标准

所有Mock和真实数据源都实现相同的接口：

```python
# src/interfaces/timeseries_data_source.py

class ITimeSeriesDataSource(ABC):
    @abstractmethod
    def get_kline_data(symbol, start_time, end_time, interval):
        """获取K线数据 - Mock和真实实现返回相同结构"""
        pass

    @abstractmethod
    def get_realtime_quotes(symbols):
        """获取实时行情 - 数据结构完全一致"""
        pass
```

### 2. 单例模式 + 缓存管理

```python
# 同一配置只创建一个实例
source1 = get_timeseries_source()  # 创建实例
source2 = get_timeseries_source()  # 返回缓存
assert source1 is source2  # True

# 配置变更时清除缓存
factory = DataSourceFactory()
factory.clear_cache(category="timeseries")
```

### 3. 类型安全 + 异常处理

```python
from src.data_sources.factory import UnsupportedDataSourceType

try:
    # 错误的数据源类型
    source = get_timeseries_source(source_type="mongodb")
except UnsupportedDataSourceType as e:
    print(f"错误: {e.message}")
    # 输出: Unsupported data source type: 'mongodb'.
    #       Supported types: mock, tdengine, api
```

### 4. Mock数据的特殊特性

#### 随机种子支持（可复现测试）

```python
source = get_timeseries_source(source_type="mock")
source.set_random_seed(42)

data1 = source.get_kline_data("600000", start, end, "1d")

source.set_random_seed(42)
data2 = source.get_kline_data("600000", start, end, "1d")

# data1 == data2 ✅ 完全相同
```

#### 真实数据模拟

```python
# Mock数据符合市场规律
# - 价格对数正态分布
# - 涨跌幅限制 -10% ~ +10%
# - 高开低收价格合理关系
# - 成交量合理范围波动
```

---

## 常见问题

### Q1: 如何确认当前使用的数据源类型？

```python
from src.data_sources.factory import DataSourceFactory

factory = DataSourceFactory()

# 查看当前环境变量配置
config = factory.get_current_config()
print(config)
# 输出: {
#   "timeseries": "mock",
#   "relational": "postgresql",
#   "business": "composite"
# }

# 查看所有已注册的数据源
registered = factory.list_registered_sources()
print(registered)
# 输出: {
#   "timeseries": ["mock", "tdengine", "api"],
#   "relational": ["mock", "postgresql"],
#   "business": ["mock", "composite"]
# }
```

### Q2: Mock数据不够真实怎么办？

A: Mock数据源基于faker库生成，支持参数化配置。如果需要更真实的测试数据，可以：

1. **使用真实数据快照**：将生产数据导出为Mock数据
2. **调整Mock生成参数**：修改 `src/data_sources/mock/` 中的生成逻辑
3. **混合使用**：关键数据用真实数据，其他用Mock

### Q3: 切换数据源需要重启服务吗？

A: **不需要重启**。使用 `clear_cache()` 方法即可：

```python
from src.data_sources.factory import DataSourceFactory

factory = DataSourceFactory()
factory.clear_cache()  # 清除所有缓存

# 下次获取数据源时，会读取新的环境变量配置
source = get_timeseries_source()  # 使用新配置
```

### Q4: 如何调试数据源切换问题？

```python
import os
import logging
from src.data_sources.factory import get_timeseries_source

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

# 检查环境变量
print(f"TIMESERIES_DATA_SOURCE={os.getenv('TIMESERIES_DATA_SOURCE')}")

# 获取数据源并测试
source = get_timeseries_source()
print(f"数据源类型: {type(source).__name__}")

# 测试数据获取
data = source.get_realtime_quotes(["600000"])
print(f"数据: {data}")
```

### Q5: 能否同时使用多个数据源？

A: **可以**。工厂模式支持同时创建多个数据源实例：

```python
from src.data_sources.factory import get_timeseries_source

# Mock数据源用于测试
mock_source = get_timeseries_source(source_type="mock")

# TDengine数据源用于生产
real_source = get_timeseries_source(source_type="tdengine")

# 对比数据
mock_data = mock_source.get_kline_data("600000", start, end, "1d")
real_data = real_source.get_kline_data("600000", start, end, "1d")
```

---

## 相关文档

### 核心文档
- **[Mock数据使用规则](./MOCK_DATA_USAGE_RULES.md)** - Mock数据的详细使用规范
- **[数据源接口定义](../../src/interfaces/README.md)** - 统一接口标准
- **[快速开始指南](./QUICKSTART.md)** - 项目快速入门

### 代码实现
- **[工厂模式实现](../../src/data_sources/factory.py)** - DataSourceFactory源码
- **[Mock数据源](../../src/data_sources/mock/)** - Mock数据源实现
- **[真实数据源](../../src/data_sources/real/)** - 真实数据源实现

### 配置文件
- **[环境变量配置](../../.env.example)** - 环境变量模板
- **[数据库配置](../../config/mystocks_table_config.yaml)** - 数据库表配置

---

## 附录：完整数据源接口

### ITimeSeriesDataSource 接口

```python
class ITimeSeriesDataSource(ABC):
    # K线数据
    def get_kline_data(symbol, start_time, end_time, interval)

    # 实时行情
    def get_realtime_quotes(symbols)

    # 资金流向
    def get_fund_flow(symbol, days)

    # 市场概览
    def get_market_overview()
```

### IRelationalDataSource 接口

```python
class IRelationalDataSource(ABC):
    # 自选股
    def get_watchlist(user_id)

    # 股票搜索
    def search_stocks(keyword)

    # 行业列表
    def get_industry_list()
```

### IBusinessDataSource 接口

```python
class IBusinessDataSource(ABC):
    # 仪表盘数据
    def get_dashboard_summary(user_id)

    # 回测执行
    def execute_backtest(strategy_config, start_date, end_date)

    # 风险指标
    def calculate_risk_metrics(portfolio_id)
```

---

**文档版本**: v1.0
**创建日期**: 2026-01-01
**维护者**: MyStocks Backend Team
**相关文档**: [CLAUDE.md](../../CLAUDE.md)
