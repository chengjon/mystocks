# Mock-Real 数据映射规范

**文档版本**: 1.0
**创建时间**: 2025-01-21
**作者**: MyStocks Backend Team
**更新时间**: 2025-01-21

---

## 📋 概述

本文档定义MyStocks系统中Mock数据与Real数据之间的标准化映射规范，确保：

1. **数据格式一致性**: Mock数据结构与Real数据结构完全兼容
2. **平滑过渡**: 支持Mock→Real数据源的无缝切换
3. **开发体验**: 开发阶段使用Mock数据，生产环境使用Real数据
4. **测试保障**: Mock数据覆盖所有Real数据场景

### 核心原则

- **结构兼容**: Mock数据结构必须与Real数据结构100%兼容
- **语义一致**: Mock数据必须符合实际业务逻辑和数据约束
- **边界覆盖**: Mock数据需要覆盖正常、边界、异常场景
- **性能保障**: Mock数据生成性能应满足开发和测试需求

---

## 🏗️ 数据源架构

### 三层抽象架构

```
┌─────────────────────────────────────────────────────────────┐
│                    业务层 (Business Layer)                   │
│     Dashboard, Analytics, Reports, Alerts                  │
├─────────────────────────────────────────────────────────────┤
│                  业务数据源 (Business Source)                │
│           MockBusinessDataSource → CompositeBusinessDataSource │
├─────────────────────────────────────────────────────────────┤
│   时序数据源 (TimeSeries)    │    关系数据源 (Relational)      │
│  MockTimeSeriesDataSource  │  MockRelationalDataSource     │
│  ↓ TDengineTimeSeriesData  │  ↓ PostgreSQLRelationalData   │
├─────────────────────────────────────────────────────────────┤
│                    数据存储层 (Storage Layer)                │
│          TDengine (时序数据)  │  PostgreSQL (关系数据)       │
└─────────────────────────────────────────────────────────────┘
```

### 数据源工厂模式

```python
# 环境变量配置
TIMESERIES_DATA_SOURCE=mock|tdengine|api
RELATIONAL_DATA_SOURCE=mock|postgresql
BUSINESS_DATA_SOURCE=mock|composite

# 工厂模式获取
from src.data_sources.factory import get_timeseries_source

ts_source = get_timeseries_source()  # 根据环境变量自动选择
ts_source = get_timeseries_source("mock")  # 强制使用Mock
```

---

## 📊 数据类型映射规范

### 1. 时序数据 (Time Series Data)

#### 1.1 实时行情数据

**接口**: `get_realtime_quotes(symbols, fields)`

| 字段 | Mock数据 | Real数据 | 数据类型 | 说明 |
|------|---------|---------|----------|------|
| symbol | 股票代码 | 股票代码 | str | 6位数字代码 |
| name | 股票名称 | 股票名称 | str | 中文名称 |
| price | 当前价格 | 最新价 | float | 2位小数 |
| change | 涨跌额 | 涨跌额 | float | 2位小数 |
| change_percent | 涨跌幅 | 涨跌幅 | float | 2位小数，±10%限制 |
| volume | 成交量 | 成交量 | int | 手数单位 |
| amount | 成交额 | 成交额 | float | 2位小数 |
| high | 最高价 | 最高价 | float | 2位小数 |
| low | 最低价 | 最低价 | float | 2位小数 |
| open | 开盘价 | 开盘价 | float | 2位小数 |
| pre_close | 昨收价 | 昨收价 | float | 2位小数 |
| timestamp | 时间戳 | 更新时间 | str | YYYY-MM-DD HH:MM:SS |

**Mock数据生成规则**:
```python
# 基准价格随机波动 (±2%)
price = base_price * (1 + random.uniform(-0.02, 0.02))
change = price - pre_close
change_percent = (change / pre_close) * 100 if pre_close > 0 else 0

# 成交量范围: 100万 - 1亿手
volume = random.randint(1000000, 100000000)

# 涨跌幅限制: ±10%
change_percent = max(-10.0, min(10.0, change_percent))
```

#### 1.2 K线数据

**接口**: `get_kline_data(symbol, start_time, end_time, interval)`

| 字段 | Mock数据 | Real数据 | 数据类型 | 说明 |
|------|---------|---------|----------|------|
| timestamp | 时间戳 | 交易时间 | datetime | 交易日期时间 |
| open | 开盘价 | 开盘价 | float | 2位小数 |
| high | 最高价 | 最高价 | float | 2位小数 |
| low | 最低价 | 最低价 | float | 2位小数 |
| close | 收盘价 | 收盘价 | float | 2位小数 |
| volume | 成交量 | 成交量 | int | 手数 |
| amount | 成交额 | 成交额 | float | 2位小数 |

**Mock数据生成规则**:
```python
# OHLC关系约束: high >= max(open, close) >= min(open, close) >= low
open_price = generate_price_movement(prev_close, 0.02)
close_price = generate_price_movement(open_price, 0.03)
high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
```

#### 1.3 资金流向数据

**接口**: `get_fund_flow(symbol, start_date, end_date, flow_type)`

| 字段 | Mock数据 | Real数据 | 数据类型 | 说明 |
|------|---------|---------|----------|------|
| trade_date | 交易日期 | 交易日期 | date | YYYY-MM-DD |
| main_net_inflow | 主力净流入 | 主力净流入 | float | 元，2位小数 |
| main_net_inflow_rate | 主力净流入率 | 主力净流入率 | float | 百分比，2位小数 |
| super_net_inflow | 超大单净流入 | 超大单净流入 | float | 元，2位小数 |
| large_net_inflow | 大单净流入 | 大单净流入 | float | 元，2位小数 |
| medium_net_inflow | 中单净流入 | 中单净流入 | float | 元，2位小数 |
| small_net_inflow | 小单净流入 | 小单净流入 | float | 元，2位小数 |

**Mock数据生成规则**:
```python
# 主力净流入范围: -5亿到+5亿
main_net_inflow = random.uniform(-500000000, 500000000)

# 资金分配关系: 超大单 + 大单 = 主力
super_net_inflow = main_net_inflow * random.uniform(0.4, 0.7)
large_net_inflow = main_net_inflow - super_net_inflow

# 中单 + 小单 = -主力 (资金平衡)
medium_net_inflow = -main_net_inflow * random.uniform(0.3, 0.6)
small_net_inflow = -main_net_inflow - medium_net_inflow
```

### 2. 关系数据 (Relational Data)

#### 2.1 股票基本信息

**接口**: `get_stock_basic_info(symbol)`

| 字段 | Mock数据 | Real数据 | 数据类型 | 说明 |
|------|---------|---------|----------|------|
| symbol | 股票代码 | 股票代码 | str | 6位数字 |
| name | 股票名称 | 股票名称 | str | 中文名称 |
| industry | 行业代码 | 行业代码 | str | IND01-IND99 |
| industry_name | 行业名称 | 行业名称 | str | 银行、证券等 |
| market | 市场类型 | 市场类型 | str | 上海A股/深圳A股 |
| list_date | 上市日期 | 上市日期 | str | YYYY-MM-DD |
| total_shares | 总股本 | 总股本 | int | 股数 |
| float_shares | 流通股本 | 流通股本 | int | 股数 |
| concepts | 概念列表 | 概念列表 | list[str] | 概念名称数组 |

#### 2.2 自选股数据

**接口**: `get_watchlist(user_id, group_name)`

| 字段 | Mock数据 | Real数据 | 数据类型 | 说明 |
|------|---------|---------|----------|------|
| id | 记录ID | 主键ID | int | 自增主键 |
| user_id | 用户ID | 用户ID | int | 关联用户 |
| symbol | 股票代码 | 股票代码 | str | 外键 |
| group_name | 分组名称 | 分组名称 | str | 默认分组 |
| note | 备注 | 备注 | str | 可选 |
| add_time | 添加时间 | 创建时间 | str | YYYY-MM-DD HH:MM:SS |
| stock_name | 股票名称 | 关联查询 | str | 从stock表关联 |
| industry | 行业 | 关联查询 | str | 从stock表关联 |

#### 2.3 策略配置数据

**接口**: `get_strategy_configs(user_id, status)`

| 字段 | Mock数据 | Real数据 | 数据类型 | 说明 |
|------|---------|---------|----------|------|
| id | 策略ID | 主键ID | str | UUID |
| user_id | 用户ID | 用户ID | int | 关联用户 |
| strategy_name | 策略名称 | 策略名称 | str | 用户自定义 |
| strategy_type | 策略类型 | 策略类型 | str | ma/macd/rsi等 |
| parameters | 策略参数 | 策略参数 | dict | JSON格式 |
| description | 描述 | 描述 | str | 可选 |
| status | 状态 | 状态 | str | active/inactive |
| create_time | 创建时间 | 创建时间 | str | YYYY-MM-DD HH:MM:SS |
| update_time | 更新时间 | 更新时间 | str | YYYY-MM-DD HH:MM:SS |

### 3. 业务数据 (Business Data)

#### 3.1 仪表盘汇总数据

**接口**: `get_dashboard_summary(user_id, include_sections)`

| 字段 | Mock数据 | Real数据 | 数据类型 | 说明 |
|------|---------|---------|----------|------|
| market_overview | 市场概览 | 市场概览 | dict | 包含市场统计 |
| watchlist_performance | 自选股表现 | 自选股表现 | list[dict] | 用户自选股数据 |
| top_fund_flow | 资金流向排行 | 资金流向排行 | list[dict] | TopN资金流向 |
| data_status | 数据状态 | 数据状态 | dict | 数据新鲜度 |
| user_stats | 用户统计 | 用户统计 | dict | 用户相关统计 |

#### 3.2 回测结果数据

**接口**: `execute_backtest(...)`

| 字段 | Mock数据 | Real数据 | 数据类型 | 说明 |
|------|---------|---------|----------|------|
| backtest_id | 回测ID | 回测ID | str | 唯一标识 |
| user_id | 用户ID | 用户ID | int | 关联用户 |
| initial_capital | 初始资金 | 初始资金 | float | 2位小数 |
| final_equity | 最终权益 | 最终权益 | float | 2位小数 |
| total_return | 总收益率 | 总收益率 | float | 2位小数 |
| annual_return | 年化收益率 | 年化收益率 | float | 2位小数 |
| max_drawdown | 最大回撤 | 最大回撤 | float | 2位小数 |
| sharpe_ratio | 夏普比率 | 夏普比率 | float | 2位小数 |
| win_rate | 胜率 | 胜率 | float | 2位小数 |
| trades | 交易记录 | 交易记录 | list[dict] | 详细交易历史 |
| equity_curve | 权益曲线 | 权益曲线 | list[dict] | 时间序列权益 |

---

## 🔄 数据转换映射

### Mock → Real 转换规则

#### 1. 数据类型转换

```python
# 时间戳标准化
def normalize_timestamp(timestamp):
    if isinstance(timestamp, str):
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    elif isinstance(timestamp, datetime):
        return timestamp
    else:
        return datetime.now()

# 价格精度处理
def normalize_price(price):
    return round(float(price), 2)

# 成交量单位转换
def normalize_volume(volume):
    # Mock数据用股数，Real数据可能用手数
    return int(volume) if isinstance(volume, (int, float)) else volume
```

#### 2. 字段映射表

```python
# 实时行情字段映射
REALTIME_QUOTES_MAPPING = {
    "symbol": "symbol",           # 直接映射
    "name": "name",               # 直接映射
    "price": "current_price",     # Mock price → Real current_price
    "change": "price_change",     # Mock change → Real price_change
    "change_percent": "change_pct", # Mock change_percent → Real change_pct
    "volume": "volume",           # 直接映射
    "amount": "turnover",         # Mock amount → Real turnover
    "timestamp": "update_time"    # Mock timestamp → Real update_time
}

# K线数据字段映射
KLINE_MAPPING = {
    "timestamp": "trade_time",    # Mock timestamp → Real trade_time
    "open": "open_price",         # Mock open → Real open_price
    "high": "high_price",         # Mock high → Real high_price
    "low": "low_price",           # Mock low → Real low_price
    "close": "close_price",       # Mock close → Real close_price
    "volume": "volume",           # 直接映射
    "amount": "turnover"          # Mock amount → Real turnover
}
```

### 数据验证规则

#### 1. 业务约束验证

```python
def validate_realtime_quotes(data):
    """实时行情数据验证"""
    errors = []

    for quote in data:
        # 必填字段验证
        required_fields = ['symbol', 'price', 'volume']
        for field in required_fields:
            if field not in quote:
                errors.append(f"Missing required field: {field}")

        # 价格逻辑验证
        if 'price' in quote and quote['price'] <= 0:
            errors.append(f"Invalid price: {quote['price']}")

        # 涨跌幅限制验证
        if 'change_percent' in quote:
            pct = quote['change_percent']
            if abs(pct) > 10.01:  # 允许0.01的误差
                errors.append(f"Invalid change percent: {pct}")

        # OHLC关系验证（如果有）
        if all(k in quote for k in ['open', 'high', 'low', 'close']):
            o, h, l, c = quote['open'], quote['high'], quote['low'], quote['close']
            if not (h >= max(o, c) >= min(o, c) >= l):
                errors.append(f"Invalid OHLC relationship: {o},{h},{l},{c}")

    return errors

def validate_volume_data(data):
    """成交量数据验证"""
    errors = []

    for item in data:
        if 'volume' in item:
            volume = item['volume']
            if not isinstance(volume, (int, float)) or volume < 0:
                errors.append(f"Invalid volume: {volume}")
            if volume > 1000000000:  # 10亿手上限检查
                errors.append(f"Volume too large: {volume}")

    return errors
```

#### 2. 数据完整性验证

```python
def validate_data_completeness(data, expected_fields):
    """数据完整性验证"""
    completeness = {}

    for field in expected_fields:
        present_count = sum(1 for item in data if field in item and item[field] is not None)
        completeness[field] = {
            'present': present_count,
            'missing': len(data) - present_count,
            'completeness_rate': present_count / len(data) if data else 0
        }

    return completeness
```

---

## 📦 数据工厂配置

### 环境变量配置

```bash
# .env 文件配置
# 数据源类型选择
TIMESERIES_DATA_SOURCE=mock      # mock|tdengine|api
RELATIONAL_DATA_SOURCE=mock      # mock|postgresql
BUSINESS_DATA_SOURCE=mock        # mock|composite

# Mock数据配置
MOCK_DATA_SEED=42                # 随机种子，确保可重现
MOCK_DATA_LOCALE=zh_CN           # 语言区域
MOCK_DATA_CACHE_TTL=300          # 缓存时间(秒)
MOCK_DATA_PRECISION=2            # 价格精度(小数位)

# Real数据连接配置(未来使用)
TDENGINE_HOST=localhost
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=mystocks

POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=postgres
POSTGRESQL_DATABASE=mystocks
```

### 配置类实现

```python
# src/config/mock_config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class MockDataConfig:
    """Mock数据配置类"""
    seed: Optional[int] = None
    locale: str = "zh_CN"
    cache_ttl: int = 300
    price_precision: int = 2
    volume_precision: int = 0
    percentage_precision: int = 2

    @classmethod
    def from_env(cls) -> 'MockDataConfig':
        """从环境变量加载配置"""
        return cls(
            seed=int(os.getenv('MOCK_DATA_SEED', '0')) if os.getenv('MOCK_DATA_SEED') else None,
            locale=os.getenv('MOCK_DATA_LOCALE', 'zh_CN'),
            cache_ttl=int(os.getenv('MOCK_DATA_CACHE_TTL', '300')),
            price_precision=int(os.getenv('MOCK_DATA_PRECISION', '2')),
            volume_precision=int(os.getenv('MOCK_DATA_VOLUME_PRECISION', '0')),
            percentage_precision=int(os.getenv('MOCK_DATA_PERCENTAGE_PRECISION', '2'))
        )

@dataclass
class DataSourceConfig:
    """数据源配置类"""
    timeseries_source: str = "mock"
    relational_source: str = "mock"
    business_source: str = "mock"

    @classmethod
    def from_env(cls) -> 'DataSourceConfig':
        """从环境变量加载配置"""
        return cls(
            timeseries_source=os.getenv('TIMESERIES_DATA_SOURCE', 'mock').lower(),
            relational_source=os.getenv('RELATIONAL_DATA_SOURCE', 'mock').lower(),
            business_source=os.getenv('BUSINESS_DATA_SOURCE', 'mock').lower()
        )
```

---

## 🧪 测试策略

### Mock数据测试用例

#### 1. 数据格式兼容性测试

```python
def test_mock_real_compatibility():
    """Mock与Real数据格式兼容性测试"""
    # 创建Mock数据源
    mock_source = MockTimeSeriesDataSource(seed=42)

    # 生成Mock数据
    mock_quotes = mock_source.get_realtime_quotes(['600000', '000001'])

    # 验证数据格式
    for quote in mock_quotes:
        # 必填字段检查
        assert 'symbol' in quote
        assert 'price' in quote
        assert 'volume' in quote

        # 数据类型检查
        assert isinstance(quote['symbol'], str)
        assert isinstance(quote['price'], (int, float))
        assert isinstance(quote['volume'], int)

        # 业务逻辑检查
        assert len(quote['symbol']) == 6
        assert quote['price'] > 0
        assert quote['volume'] >= 0
        assert -10.01 <= quote.get('change_percent', 0) <= 10.01
```

#### 2. 数据一致性测试

```python
def test_data_consistency():
    """Mock数据一致性测试"""
    mock_source = MockTimeSeriesDataSource(seed=123)

    # 获取同一股票的不同数据
    quotes = mock_source.get_realtime_quotes(['600000'])
    klines = mock_source.get_kline_data(
        '600000',
        datetime.now() - timedelta(days=5),
        datetime.now()
    )

    # 检查数据一致性
    if quotes and not klines.empty:
        quote_price = quotes[0]['price']
        latest_kline = klines.iloc[-1]
        kline_price = latest_kline['close']

        # 价格应该相近（允许小幅差异）
        assert abs(quote_price - kline_price) / kline_price < 0.05  # 5%差异
```

#### 3. 性能基准测试

```python
def test_mock_performance():
    """Mock数据生成性能测试"""
    mock_source = MockTimeSeriesDataSource()

    import time

    # 测试实时行情生成性能
    start = time.time()
    quotes = mock_source.get_realtime_quotes(symbols=[f"60{str(i).zfill(4)}" for i in range(1000)])
    duration = time.time() - start

    assert len(quotes) == 1000
    assert duration < 1.0  # 1000条数据应在1秒内生成
    print(f"Generated {len(quotes)} quotes in {duration:.3f}s")
```

### 自动化测试集成

```python
# scripts/tests/test_mock_real_mapping.py
class TestMockRealMapping:
    """Mock-Real数据映射测试套件"""

    def test_all_data_types_compatibility(self):
        """所有数据类型的兼容性测试"""
        test_cases = [
            ('realtime_quotes', self._test_realtime_quotes),
            ('kline_data', self._test_kline_data),
            ('fund_flow', self._test_fund_flow),
            ('stock_info', self._test_stock_info),
            ('watchlist', self._test_watchlist),
            ('strategy_config', self._test_strategy_config)
        ]

        for data_type, test_func in test_cases:
            with self.subTest(data_type=data_type):
                test_func()

    def _test_realtime_quotes(self):
        """实时行情数据测试"""
        # 实现具体测试逻辑
        pass

    def _test_kline_data(self):
        """K线数据测试"""
        # 实现具体测试逻辑
        pass
```

---

## 📈 迁移策略

### 阶段性迁移计划

#### Phase 1: Mock数据标准化 (当前阶段)
- ✅ 完成Mock数据结构规范
- ✅ 实现Mock-Real数据映射
- ✅ 建立数据验证机制
- 🔄 完善测试覆盖

#### Phase 2: Real数据接入 (下一阶段)
- ⏳ 实现TDengine时序数据源
- ⏳ 实现PostgreSQL关系数据源
- ⏳ 实现Composite业务数据源
- ⏳ 建立数据质量监控

#### Phase 3: 渐进式切换
- ⏳ 开发环境使用Mock数据
- ⏳ 测试环境支持Mock/Real切换
- ⏳ 生产环境使用Real数据
- ⏳ 建立数据降级机制

### 切换机制实现

```python
# src/core/data_source_manager.py
class DataSourceManager:
    """数据源管理器"""

    def __init__(self):
        self.config = DataSourceConfig.from_env()
        self.mock_config = MockDataConfig.from_env()

    def get_timeseries_source(self):
        """获取时序数据源"""
        if self.config.timeseries_source == "mock":
            return MockTimeSeriesDataSource(
                seed=self.mock_config.seed,
                locale=self.mock_config.locale
            )
        elif self.config.timeseries_source == "tdengine":
            return TDengineTimeSeriesDataSource()
        elif self.config.timeseries_source == "api":
            return APITimeSeriesDataSource()
        else:
            raise ValueError(f"Unsupported timeseries source: {self.config.timeseries_source}")

    def get_data_with_fallback(self, method_name, *args, **kwargs):
        """带降级机制的数据获取"""
        try:
            source = self.get_timeseries_source()
            method = getattr(source, method_name)
            return method(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary data source failed: {e}, falling back to mock")
            fallback_source = MockTimeSeriesDataSource()
            fallback_method = getattr(fallback_source, method_name)
            return fallback_method(*args, **kwargs)
```

---

## 🔍 监控和质量保证

### 数据质量指标

#### 1. 完整性指标
- **字段完整率**: 必填字段的非空比例
- **记录完整率**: 期望记录数的实际获取比例
- **时间连续性**: 时间序列数据的连续性

#### 2. 准确性指标
- **价格合理性**: 价格在合理范围内
- **成交量合理性**: 成交量符合市场规律
- **涨跌幅限制**: 涨跌幅在±10%范围内

#### 3. 一致性指标
- **OHLC关系**: high >= max(open, close) >= min(open, close) >= low
- **资金平衡**: 各类资金流入流出平衡
- **关联数据**: 关联表数据的一致性

### 监控实现

```python
# src/monitoring/data_quality_monitor.py
class DataQualityMonitor:
    """数据质量监控器"""

    def __init__(self):
        self.metrics = {}

    def check_realtime_quotes_quality(self, data):
        """实时行情数据质量检查"""
        quality_score = 100.0
        issues = []

        # 完整性检查
        required_fields = ['symbol', 'price', 'volume']
        missing_fields = self._check_missing_fields(data, required_fields)
        if missing_fields:
            quality_score -= len(missing_fields) * 10
            issues.append(f"Missing fields: {missing_fields}")

        # 准确性检查
        for quote in data:
            if 'price' in quote and quote['price'] <= 0:
                quality_score -= 5
                issues.append(f"Invalid price: {quote['price']}")

            if 'change_percent' in quote:
                pct = quote['change_percent']
                if abs(pct) > 10.01:
                    quality_score -= 5
                    issues.append(f"Invalid change percent: {pct}")

        return {
            'quality_score': max(0, quality_score),
            'issues': issues,
            'total_records': len(data),
            'valid_records': len(data) - len(issues)
        }
```

---

## 📚 最佳实践

### Mock数据使用规范

#### 1. 开发环境
```python
# 设置环境变量
os.environ['TIMESERIES_DATA_SOURCE'] = 'mock'
os.environ['MOCK_DATA_SEED'] = '42'  # 固定种子，确保可重现

# 使用工厂模式获取数据源
from src.data_sources.factory import get_timeseries_source
ts_source = get_timeseries_source()

# 获取数据
quotes = ts_source.get_realtime_quotes(['600000', '000001'])
```

#### 2. 测试环境
```python
class TestTradingStrategy:
    def setUp(self):
        """测试设置"""
        # 使用固定种子确保测试可重现
        self.mock_source = MockTimeSeriesDataSource(seed=12345)

    def test_strategy_logic(self):
        """测试策略逻辑"""
        # 生成测试数据
        klines = self.mock_source.get_kline_data(
            '600000',
            datetime(2024, 1, 1),
            datetime(2024, 12, 31),
            interval='1d'
        )

        # 执行策略逻辑测试
        result = self.strategy.execute(klines)

        # 验证结果
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
```

#### 3. 生产降级
```python
def get_market_data_with_fallback():
    """带降级机制的市场数据获取"""
    try:
        # 尝试获取真实数据
        real_source = get_timeseries_source(source_type="tdengine")
        return real_source.get_realtime_quotes()
    except Exception as e:
        logger.error(f"Real data source failed: {e}")

        # 降级到Mock数据
        logger.warning("Falling back to mock data")
        mock_source = get_timeseries_source(source_type="mock")
        return mock_source.get_realtime_quotes()
```

### 性能优化建议

#### 1. Mock数据缓存
```python
class CachedMockDataSource:
    """带缓存的Mock数据源"""

    def __init__(self, cache_ttl=300):
        self.cache = {}
        self.cache_ttl = cache_ttl

    def get_realtime_quotes(self, symbols=None):
        cache_key = f"quotes_{hash(tuple(symbols or []))}"

        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data

        # 生成新数据
        data = self._generate_quotes(symbols)
        self.cache[cache_key] = (data, time.time())
        return data
```

#### 2. 批量数据生成
```python
def generate_batch_quotes(symbols, batch_size=100):
    """批量生成行情数据"""
    all_quotes = []

    for i in range(0, len(symbols), batch_size):
        batch_symbols = symbols[i:i + batch_size]
        batch_quotes = _generate_quotes_batch(batch_symbols)
        all_quotes.extend(batch_quotes)

    return all_quotes
```

---

## 🛠️ 实现指南

### 快速开始

#### 1. 环境配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
vim .env
```

#### 2. 代码示例
```python
# 使用工厂模式
from src.data_sources.factory import get_timeseries_source

# 获取Mock数据源
ts_source = get_timeseries_source()  # 自动使用环境变量配置

# 获取实时行情
quotes = ts_source.get_realtime_quotes(['600000', '000001'])
for quote in quotes:
    print(f"{quote['name']}({quote['symbol']}): ¥{quote['price']:.2f} ({quote['change_percent']:+.2f}%)")

# 获取K线数据
klines = ts_source.get_kline_data(
    '600000',
    datetime(2024, 1, 1),
    datetime(2024, 12, 31),
    interval='1d'
)
print(f"Generated {len(klines)} K-line records")
```

#### 3. 测试验证
```bash
# 运行Mock数据测试
python scripts/tests/test_mock_data_system.py

# 运行性能测试
python examples/mock_data_demo.py

# 验证数据质量
python scripts/tests/test_data_quality.py
```

### 扩展指南

#### 添加新的Mock数据类型
```python
# 1. 实现接口
class MockCustomDataSource(ICustomDataSource):
    def get_custom_data(self, params):
        return self._generate_custom_data(params)

    def _generate_custom_data(self, params):
        # 实现数据生成逻辑
        pass

# 2. 注册到工厂
factory = DataSourceFactory()
factory.register_custom_source("mock", MockCustomDataSource)

# 3. 环境变量配置
os.environ['CUSTOM_DATA_SOURCE'] = 'mock'

# 4. 使用
from src.data_sources.factory import get_custom_source
custom_source = get_custom_source()
data = custom_source.get_custom_data(params)
```

---

## 📖 相关文档

- [Mock数据系统架构文档](docs/architecture/mock_data_system.md)
- [数据源工厂使用指南](docs/guides/data_source_factory.md)
- [测试覆盖报告](docs/reports/test_coverage_report.md)
- [性能优化指南](docs/guides/performance_optimization.md)

---

## 📞 技术支持

如有问题或建议，请联系：

- **项目负责人**: MyStocks Backend Team
- **文档维护**: Claude Code Assistant
- **技术支持**: GitHub Issues

---

*本文档版本: v1.0 | 最后更新: 2025-01-21*