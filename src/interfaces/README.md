# 数据源抽象接口层

> **版本**: 1.0.0
> **创建日期**: 2025-11-21
> **作者**: MyStocks Backend Team

---

## 📋 目录

1. [架构概述](#架构概述)
2. [三层接口设计](#三层接口设计)
3. [接口文件说明](#接口文件说明)
4. [使用指南](#使用指南)
5. [实现要求](#实现要求)
6. [性能规范](#性能规范)

---

## 🏗️ 架构概述

本目录定义了MyStocks系统的**数据源抽象接口层**，实现了数据访问与业务逻辑的完全解耦。

### 设计目标

- ✅ **接口标准化**: 统一的方法签名和返回格式
- ✅ **数据源解耦**: Mock/TDengine/PostgreSQL/API无缝切换
- ✅ **配置驱动**: 通过环境变量控制数据源类型
- ✅ **性能优化**: 针对时序和关系数据的专门优化
- ✅ **类型安全**: 完整的类型注解和返回格式规范

### 三层架构

```
┌─────────────────────────────────────────────┐
│          IBusinessDataSource                │
│      (业务逻辑层 - 复合操作)                  │
│  • 仪表盘汇总  • 策略回测  • 风险分析         │
└─────────────────────────────────────────────┘
              ↓ 依赖
┌──────────────────────┬──────────────────────┐
│ ITimeSeriesDataSource│ IRelationalDataSource│
│   (时序数据层)        │    (关系数据层)       │
│ • 实时行情            │ • 自选股管理          │
│ • K线数据             │ • 策略配置            │
│ • 资金流向            │ • 风险预警            │
│ • 技术指标            │ • 用户偏好            │
└──────────────────────┴──────────────────────┘
              ↓ 实现
┌─────────────────────────────────────────────┐
│          数据源工厂 (Factory Pattern)         │
│  Mock / TDengine / PostgreSQL / API         │
└─────────────────────────────────────────────┘
```

---

## 📦 三层接口设计

### 1. ITimeSeriesDataSource (时序数据源)

**文件**: `timeseries_data_source.py`
**适用数据库**: TDengine (时序数据库)
**适用场景**: 高频市场数据、实时行情、技术分析

**核心功能模块**:
- **实时行情**: `get_realtime_quotes()`, `get_index_realtime()`
- **K线数据**: `get_kline_data()`, `get_intraday_chart()`
- **资金流向**: `get_fund_flow()`, `get_top_fund_flow_stocks()`
- **市场概览**: `get_market_overview()`
- **技术指标**: `calculate_technical_indicators()`
- **竞价数据**: `get_auction_data()`
- **数据质量**: `check_data_quality()`, `health_check()`

**方法数量**: 10个抽象方法

---

### 2. IRelationalDataSource (关系数据源)

**文件**: `relational_data_source.py`
**适用数据库**: PostgreSQL (关系数据库)
**适用场景**: 配置管理、用户数据、策略存储

**核心功能模块**:
- **自选股管理**: `get_watchlist()`, `add_to_watchlist()`, `remove_from_watchlist()`
- **策略配置**: `get_strategy_configs()`, `save_strategy_config()`, `update_strategy_status()`
- **风险预警**: `get_risk_alerts()`, `save_risk_alert()`, `toggle_risk_alert()`
- **用户偏好**: `get_user_preferences()`, `update_user_preferences()`
- **股票信息**: `get_stock_basic_info()`, `search_stocks()`
- **行业概念**: `get_industry_list()`, `get_concept_list()`, `get_stocks_by_industry()`
- **事务管理**: `begin_transaction()`, `commit_transaction()`, `rollback_transaction()`

**方法数量**: 18个抽象方法

---

### 3. IBusinessDataSource (业务逻辑数据源)

**文件**: `business_data_source.py`
**适用场景**: 复合查询、业务聚合、跨源协调

**核心功能模块**:
- **仪表盘**: `get_dashboard_summary()`, `get_sector_performance()`
- **策略回测**: `execute_backtest()`, `get_backtest_results()`
- **风险管理**: `calculate_risk_metrics()`, `check_risk_alerts()`
- **交易信号**: `analyze_trading_signals()`
- **组合分析**: `get_portfolio_analysis()`, `perform_attribution_analysis()`
- **股票筛选**: `execute_stock_screener()`

**方法数量**: 10个抽象方法

---

## 📚 接口文件说明

### timeseries_data_source.py

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import pandas as pd

class ITimeSeriesDataSource(ABC):
    """时序数据源抽象接口"""

    @abstractmethod
    def get_realtime_quotes(
        self,
        symbols: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """获取实时行情数据"""
        pass
```

**关键特性**:
- 完整的类型注解 (Type Hints)
- 详细的Docstring (参数、返回值、示例、性能要求)
- 性能SLA嵌入文档 (如: `<100ms`, `<500ms`)
- 异常类型说明 (`DataSourceException`)

---

### relational_data_source.py

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import date

class IRelationalDataSource(ABC):
    """关系数据源抽象接口"""

    @abstractmethod
    def get_watchlist(
        self,
        user_id: int,
        group_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取用户自选股列表"""
        pass
```

**关键特性**:
- PostgreSQL优化模式文档 (如: `joinedload()` 避免N+1查询)
- 事务管理支持
- 性能优化建议嵌入Docstring

---

### business_data_source.py

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import date, datetime
import pandas as pd

class IBusinessDataSource(ABC):
    """业务逻辑数据源抽象接口"""

    @abstractmethod
    def get_dashboard_summary(
        self,
        user_id: int,
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取仪表盘汇总数据"""
        pass
```

**关键特性**:
- 跨数据源协调逻辑
- 复杂聚合操作定义
- 详细的返回数据结构示例

---

## 🛠️ 使用指南

### 1. 实现接口

创建具体实现类继承对应接口:

```python
from src.interfaces.timeseries_data_source import ITimeSeriesDataSource

class MockTimeSeriesDataSource(ITimeSeriesDataSource):
    """Mock数据源实现 - 用于开发测试"""

    def get_realtime_quotes(
        self,
        symbols: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        # Mock数据生成逻辑
        return [
            {
                "symbol": "600000",
                "name": "浦发银行",
                "price": 10.5,
                "change": 0.3,
                "change_percent": 2.94,
                # ... 更多字段
            }
        ]
```

### 2. 使用工厂模式

通过工厂获取数据源实例:

```python
from src.data_sources.factory import DataSourceFactory

# 获取时序数据源 (根据环境变量自动选择Mock/TDengine)
ts_source = DataSourceFactory.get_timeseries_source()
quotes = ts_source.get_realtime_quotes(symbols=["600000", "000001"])

# 获取关系数据源 (根据环境变量自动选择Mock/PostgreSQL)
rel_source = DataSourceFactory.get_relational_source()
watchlist = rel_source.get_watchlist(user_id=1)

# 获取业务数据源
biz_source = DataSourceFactory.get_business_source()
dashboard = biz_source.get_dashboard_summary(user_id=1)
```

### 3. 环境变量配置

在 `.env` 文件中配置数据源类型:

```bash
# 时序数据源类型: mock / tdengine / api
TIMESERIES_DATA_SOURCE=mock

# 关系数据源类型: mock / postgresql
RELATIONAL_DATA_SOURCE=mock

# 业务数据源类型: mock / composite
BUSINESS_DATA_SOURCE=mock
```

---

## ✅ 实现要求

### 必须遵守的规范

1. **方法签名一致性**
   - 参数名称、类型、默认值必须与接口定义完全一致
   - 返回值类型必须匹配接口规范

2. **返回数据格式统一**
   - 所有实现返回的数据结构必须100%对齐
   - 字段名称、数据类型、嵌套结构保持一致

3. **异常处理规范**
   - 统一抛出 `DataSourceException` 或其子类
   - 异常信息包含 `error_code` 和 `source_type`

4. **性能要求达标**
   - 单股票查询 < 50ms
   - 批量查询(10个) < 100ms
   - K线数据(250天) < 200ms
   - 仪表盘汇总 < 1s

5. **类型注解完整**
   - 所有参数和返回值必须有类型注解
   - 使用 `mypy` 工具进行类型检查

---

## ⚡ 性能规范

### ITimeSeriesDataSource 性能要求

| 方法 | 性能目标 | 关键指标 |
|------|---------|---------|
| `get_realtime_quotes()` | 单股票 <50ms, 批量10个 <100ms | 响应时间 |
| `get_kline_data()` | 日线250天 <200ms, 分钟1天 <300ms | 响应时间 |
| `get_intraday_chart()` | <150ms | 响应时间 |
| `get_fund_flow()` | 30天 <200ms, 90天 <400ms | 响应时间 |
| `get_market_overview()` | <200ms | 响应时间 |
| `calculate_technical_indicators()` | 单指标 <200ms, 5指标 <500ms | 响应时间 |

### IRelationalDataSource 性能要求

| 方法 | 性能目标 | 关键指标 |
|------|---------|---------|
| `get_watchlist()` | <100ms | 响应时间, N+1查询避免 |
| `get_strategy_configs()` | <150ms | 响应时间, joinedload |
| `get_risk_alerts()` | <200ms | 响应时间 |
| `search_stocks()` | <200ms | 响应时间, 全文索引 |

### IBusinessDataSource 性能要求

| 方法 | 性能目标 | 关键指标 |
|------|---------|---------|
| `get_dashboard_summary()` | <1s | 响应时间, 并发查询 |
| `execute_backtest()` | 1年50股票 <30s | 计算时间, GPU加速 |
| `calculate_risk_metrics()` | <800ms | 响应时间 |
| `execute_stock_screener()` | <1.5s | 响应时间 |

---

## 📝 开发检查清单

在实现接口时，请确认以下检查项:

- [ ] 所有抽象方法已实现
- [ ] 方法签名与接口定义完全一致
- [ ] 返回数据格式符合接口文档示例
- [ ] 性能要求达标 (通过性能测试)
- [ ] 异常处理符合规范
- [ ] 类型注解完整 (通过mypy检查)
- [ ] 单元测试覆盖率 >= 80%
- [ ] 集成测试通过
- [ ] 契约测试通过 (Mock与真实数据格式一致性)
- [ ] 代码文档完整 (Docstring)

---

## 🔗 相关文档

- **实施方案**: [docs/architecture/数据源架构优化实施方案_v1.0.md](../../docs/architecture/数据源架构优化实施方案_v1.0.md)
- **执行摘要**: [docs/architecture/数据源架构优化-执行摘要.md](../../docs/architecture/数据源架构优化-执行摘要.md)
- **API文档**: [docs/api/API_GUIDE.md](../../docs/api/API_GUIDE.md)

---

## 📞 技术支持

如有疑问或发现接口设计问题，请:

1. 查看完整实施方案文档
2. 检查接口文件中的详细Docstring
3. 参考Mock实现示例
4. 联系开发团队

---

**最后更新**: 2025-11-21
**维护团队**: MyStocks Backend Team
