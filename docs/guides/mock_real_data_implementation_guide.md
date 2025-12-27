# Mock-Real 数据映射实施指南

**文档版本**: 1.0
**创建时间**: 2025-01-21
**作者**: MyStocks Backend Team
**目标读者**: 开发人员、测试人员、架构师

---

## 🎯 实施目标

本指南提供Mock-Real数据映射规范的具体实施方案，确保：

1. **平滑过渡**: 从Mock数据无缝切换到Real数据
2. **质量保证**: Mock数据完全模拟Real数据特征
3. **开发效率**: 支持并行开发和测试
4. **生产稳定**: 确保生产环境数据可靠性

---

## 🛠️ 实施步骤

### Step 1: 环境配置标准化

#### 1.1 环境变量配置

```bash
# .env 文件配置示例
# 数据源类型 (mock=开发, real=生产)
TIMESERIES_DATA_SOURCE=mock      # mock|tdengine|api
RELATIONAL_DATA_SOURCE=mock      # mock|postgresql
BUSINESS_DATA_SOURCE=mock        # mock|composite

# Mock数据配置
MOCK_DATA_SEED=12345            # 固定种子确保可重现
MOCK_DATA_LOCALE=zh_CN          # 中文数据
MOCK_DATA_CACHE_TTL=300         # 缓存5分钟
MOCK_DATA_PRECISION=2           # 价格2位小数

# Real数据连接配置(用于Real模式)
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

#### 1.2 配置类实现

```python
# src/config/data_source_config.py
import os
from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum

class DataSourceType(Enum):
    MOCK = "mock"
    TDENGINE = "tdengine"
    POSTGRESQL = "postgresql"
    API = "api"
    COMPOSITE = "composite"

@dataclass
class MockDataConfig:
    """Mock数据配置"""
    seed: int = 12345
    locale: str = "zh_CN"
    cache_ttl: int = 300
    price_precision: int = 2
    volume_precision: int = 0
    percentage_precision: int = 2
    enable_cache: bool = True

    @classmethod
    def from_env(cls) -> 'MockDataConfig':
        return cls(
            seed=int(os.getenv('MOCK_DATA_SEED', '12345')),
            locale=os.getenv('MOCK_DATA_LOCALE', 'zh_CN'),
            cache_ttl=int(os.getenv('MOCK_DATA_CACHE_TTL', '300')),
            price_precision=int(os.getenv('MOCK_DATA_PRECISION', '2')),
            volume_precision=int(os.getenv('MOCK_DATA_VOLUME_PRECISION', '0')),
            percentage_precision=int(os.getenv('MOCK_DATA_PERCENTAGE_PRECISION', '2')),
            enable_cache=os.getenv('MOCK_DATA_CACHE_ENABLED', 'true').lower() == 'true'
        )

@dataclass
class DataSourceConfig:
    """数据源配置"""
    timeseries_source: DataSourceType = DataSourceType.MOCK
    relational_source: DataSourceType = DataSourceType.MOCK
    business_source: DataSourceType = DataSourceType.MOCK

    @classmethod
    def from_env(cls) -> 'DataSourceConfig':
        return cls(
            timeseries_source=DataSourceType(
                os.getenv('TIMESERIES_DATA_SOURCE', 'mock').lower()
            ),
            relational_source=DataSourceType(
                os.getenv('RELATIONAL_DATA_SOURCE', 'mock').lower()
            ),
            business_source=DataSourceType(
                os.getenv('BUSINESS_DATA_SOURCE', 'mock').lower()
            )
        )
```

### Step 2: 数据工厂增强

#### 2.1 智能数据源选择

```python
# src/core/smart_data_source_factory.py
from typing import Optional, Union
from src.config.data_source_config import DataSourceConfig, MockDataConfig
from src.interfaces.timeseries_data_source import ITimeSeriesDataSource
from src.interfaces.relational_data_source import IRelationalDataSource
from src.interfaces.business_data_source import IBusinessDataSource

class SmartDataSourceFactory:
    """智能数据源工厂 - 支持Mock/Real自动切换"""

    def __init__(self):
        self.config = DataSourceConfig.from_env()
        self.mock_config = MockDataConfig.from_env()
        self._instances = {}

    def get_timeseries_source(self, force_type: Optional[str] = None) -> ITimeSeriesDataSource:
        """获取时序数据源，支持强制类型指定"""
        source_type = force_type or self.config.timeseries_source.value

        cache_key = f"timeseries_{source_type}"
        if cache_key in self._instances:
            return self._instances[cache_key]

        if source_type == "mock":
            from src.data_sources.mock.timeseries_mock import MockTimeSeriesDataSource
            instance = MockTimeSeriesDataSource(
                seed=self.mock_config.seed,
                locale=self.mock_config.locale
            )
        elif source_type == "tdengine":
            from src.data_sources.real.tdengine_timeseries import TDengineTimeSeriesDataSource
            instance = TDengineTimeSeriesDataSource()
        elif source_type == "api":
            from src.data_sources.real.api_timeseries import APITimeSeriesDataSource
            instance = APITimeSeriesDataSource()
        else:
            raise ValueError(f"Unsupported timeseries source type: {source_type}")

        self._instances[cache_key] = instance
        return instance

    def get_data_with_fallback(self, data_type: str, method: str, *args, **kwargs):
        """获取数据，支持自动降级到Mock"""
        try:
            if data_type == "timeseries":
                source = self.get_timeseries_source()
            elif data_type == "relational":
                source = self.get_relational_source()
            elif data_type == "business":
                source = self.get_business_source()
            else:
                raise ValueError(f"Unknown data type: {data_type}")

            method_func = getattr(source, method)
            return method_func(*args, **kwargs)

        except Exception as e:
            import logging
            logging.warning(f"Primary data source failed ({data_type}.{method}): {e}")
            logging.info("Falling back to mock data source")

            # 强制使用Mock数据源
            if data_type == "timeseries":
                fallback_source = self.get_timeseries_source("mock")
            elif data_type == "relational":
                fallback_source = self.get_relational_source("mock")
            elif data_type == "business":
                fallback_source = self.get_business_source("mock")

            fallback_method = getattr(fallback_source, method)
            return fallback_method(*args, **kwargs)
```

#### 2.2 数据质量检查装饰器

```python
# src/decorators/data_quality.py
import functools
from typing import Any, Callable
import logging

def validate_data_quality(data_type: str):
    """数据质量验证装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            # 执行数据质量检查
            quality_issues = _check_data_quality(result, data_type)
            if quality_issues:
                logging.warning(f"Data quality issues detected in {data_type}: {quality_issues}")

            return result
        return wrapper
    return decorator

def _check_data_quality(data: Any, data_type: str) -> list:
    """检查数据质量"""
    issues = []

    if data_type == "realtime_quotes":
        issues.extend(_validate_realtime_quotes(data))
    elif data_type == "kline_data":
        issues.extend(_validate_kline_data(data))
    elif data_type == "fund_flow":
        issues.extend(_validate_fund_flow(data))

    return issues

def _validate_realtime_quotes(quotes: list) -> list:
    """验证实时行情数据质量"""
    issues = []

    if not isinstance(quotes, list):
        issues.append("Data is not a list")
        return issues

    for i, quote in enumerate(quotes):
        if not isinstance(quote, dict):
            issues.append(f"Quote {i} is not a dict")
            continue

        # 检查必填字段
        required_fields = ['symbol', 'price', 'volume']
        for field in required_fields:
            if field not in quote:
                issues.append(f"Quote {i}: missing required field '{field}'")

        # 检查数据类型和值
        if 'symbol' in quote and not isinstance(quote['symbol'], str):
            issues.append(f"Quote {i}: symbol must be string")

        if 'price' in quote:
            price = quote['price']
            if not isinstance(price, (int, float)) or price <= 0:
                issues.append(f"Quote {i}: invalid price {price}")

        if 'change_percent' in quote:
            pct = quote['change_percent']
            if isinstance(pct, (int, float)) and abs(pct) > 10.01:
                issues.append(f"Quote {i}: change percent {pct} exceeds limits")

    return issues
```

### Step 3: Mock数据增强实现

#### 3.1 时序数据源增强

```python
# src/data_sources/mock/enhanced_timeseries_mock.py
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from faker import Faker
from src.data_sources.mock.timeseries_mock import MockTimeSeriesDataSource
from src.config.data_source_config import MockDataConfig

class EnhancedMockTimeSeriesDataSource(MockTimeSeriesDataSource):
    """增强版Mock时序数据源 - 完全符合Real数据规范"""

    def __init__(self, config: Optional[MockDataConfig] = None):
        if config is None:
            config = MockDataConfig()

        super().__init__(seed=config.seed, locale=config.locale)
        self.config = config
        self._cache = {}
        self._cache_timestamps = {}

    def get_realtime_quotes(
        self, symbols: Optional[List[str]] = None, fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """获取实时行情 - 严格遵循数据映射规范"""
        cache_key = f"quotes_{hash(tuple(symbols or []))}_{hash(tuple(fields or []))}"

        # 检查缓存
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]

        # 生成基础数据
        quotes = super().get_realtime_quotes(symbols, fields)

        # 应用精度和格式化
        formatted_quotes = []
        for quote in quotes:
            formatted_quote = self._format_realtime_quote(quote)
            formatted_quotes.append(formatted_quote)

        # 缓存结果
        self._cache[cache_key] = formatted_quotes
        self._cache_timestamps[cache_key] = datetime.now()

        return formatted_quotes

    def _format_realtime_quote(self, quote: Dict[str, Any]) -> Dict[str, Any]:
        """格式化实时行情数据"""
        formatted = quote.copy()

        # 应用精度控制
        if 'price' in formatted:
            formatted['price'] = round(formatted['price'], self.config.price_precision)

        if 'change' in formatted:
            formatted['change'] = round(formatted['change'], self.config.price_precision)

        if 'change_percent' in formatted:
            formatted['change_percent'] = round(formatted['change_percent'], self.config.percentage_precision)

        if 'volume' in formatted:
            formatted['volume'] = int(formatted['volume'])

        if 'amount' in formatted:
            formatted['amount'] = round(formatted['amount'], self.config.price_precision)

        # 标准化时间戳格式
        if 'timestamp' in formatted and isinstance(formatted['timestamp'], str):
            try:
                dt = datetime.strptime(formatted['timestamp'], "%Y-%m-%d %H:%M:%S")
                formatted['timestamp'] = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                formatted['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return formatted

    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if not self.config.enable_cache:
            return False

        if cache_key not in self._cache:
            return False

        if cache_key not in self._cache_timestamps:
            return False

        age = (datetime.now() - self._cache_timestamps[cache_key]).total_seconds()
        return age < self.config.cache_ttl
```

#### 3.2 业务数据源增强

```python
# src/data_sources/mock/enhanced_business_mock.py
from typing import List, Dict, Optional, Any
from datetime import date, datetime
from src.data_sources.mock.business_mock import MockBusinessDataSource
from src.config.data_source_config import MockDataConfig

class EnhancedMockBusinessDataSource(MockBusinessDataSource):
    """增强版Mock业务数据源"""

    def __init__(self, config: Optional[MockDataConfig] = None):
        if config is None:
            config = MockDataConfig()

        super().__init__(seed=config.seed)
        self.config = config

    def execute_backtest(
        self,
        user_id: int,
        strategy_config: Dict[str, Any],
        symbols: List[str],
        start_date: date,
        end_date: date,
        initial_capital: float = 1000000.0,
    ) -> Dict[str, Any]:
        """执行策略回测 - 完全遵循数据映射规范"""

        # 获取基础回测结果
        result = super().execute_backtest(
            user_id, strategy_config, symbols, start_date, end_date, initial_capital
        )

        # 应用数据映射规范
        mapped_result = self._map_backtest_result(result)

        return mapped_result

    def _map_backtest_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """映射回测结果到规范格式"""
        mapped = result.copy()

        # 应用精度控制
        precision_fields = ['initial_capital', 'final_equity', 'total_return',
                          'annual_return', 'max_drawdown', 'sharpe_ratio', 'win_rate']

        for field in precision_fields:
            if field in mapped:
                mapped[field] = round(float(mapped[field]), 2)

        # 格式化交易记录
        if 'trades' in mapped:
            formatted_trades = []
            for trade in mapped['trades']:
                formatted_trade = self._format_trade_record(trade)
                formatted_trades.append(formatted_trade)
            mapped['trades'] = formatted_trades

        # 格式化权益曲线
        if 'equity_curve' in mapped:
            formatted_curve = []
            for point in mapped['equity_curve']:
                formatted_point = self._format_equity_point(point)
                formatted_curve.append(formatted_point)
            mapped['equity_curve'] = formatted_curve

        return mapped

    def _format_trade_record(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """格式化交易记录"""
        formatted = trade.copy()

        # 价格精度
        for price_field in ['price', 'commission']:
            if price_field in formatted:
                formatted[price_field] = round(float(formatted[price_field]), 2)

        # 数量为整数
        if 'quantity' in formatted:
            formatted['quantity'] = int(formatted['quantity'])

        # 标准化日期格式
        if 'trade_date' in formatted:
            date_str = formatted['trade_date']
            if isinstance(date_str, str) and len(date_str) == 10:
                formatted['trade_date'] = f"{date_str} 00:00:00"
            elif isinstance(date_str, str):
                formatted['trade_date'] = date_str

        return formatted

    def _format_equity_point(self, point: Dict[str, Any]) -> Dict[str, Any]:
        """格式化权益曲线点"""
        formatted = point.copy()

        # 权益精度
        if 'equity' in formatted:
            formatted['equity'] = round(float(formatted['equity']), 2)

        if 'cumulative_return' in formatted:
            formatted['cumulative_return'] = round(float(formatted['cumulative_return']), 2)

        # 标准化日期格式
        if 'date' in formatted:
            date_str = formatted['date']
            if isinstance(date_str, str) and len(date_str) == 10:
                formatted['date'] = f"{date_str} 00:00:00"

        return formatted
```

### Step 4: 测试实施

#### 4.1 兼容性测试套件

```python
# scripts/tests/test_mock_real_compatibility.py
import pytest
from datetime import datetime, timedelta
from src.core.smart_data_source_factory import SmartDataSourceFactory
from src.config.data_source_config import MockDataConfig

class TestMockRealCompatibility:
    """Mock-Real数据兼容性测试套件"""

    def setup_method(self):
        """测试设置"""
        self.factory = SmartDataSourceFactory()
        self.mock_config = MockDataConfig(seed=12345)  # 固定种子确保可重现

    def test_realtime_quotes_compatibility(self):
        """测试实时行情数据兼容性"""
        # 获取Mock数据
        mock_source = self.factory.get_timeseries_source("mock")
        quotes = mock_source.get_realtime_quotes(['600000', '000001'])

        # 验证数据格式
        assert isinstance(quotes, list)
        assert len(quotes) == 2

        for quote in quotes:
            # 验证必填字段
            required_fields = ['symbol', 'name', 'price', 'change_percent', 'volume', 'timestamp']
            for field in required_fields:
                assert field in quote, f"Missing field: {field}"

            # 验证数据类型
            assert isinstance(quote['symbol'], str)
            assert isinstance(quote['name'], str)
            assert isinstance(quote['price'], (int, float))
            assert isinstance(quote['change_percent'], (int, float))
            assert isinstance(quote['volume'], int)
            assert isinstance(quote['timestamp'], str)

            # 验证数据约束
            assert len(quote['symbol']) == 6
            assert quote['price'] > 0
            assert quote['volume'] >= 0
            assert -10.01 <= quote['change_percent'] <= 10.01

            # 验证时间戳格式
            try:
                datetime.strptime(quote['timestamp'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pytest.fail(f"Invalid timestamp format: {quote['timestamp']}")

    def test_kline_data_compatibility(self):
        """测试K线数据兼容性"""
        mock_source = self.factory.get_timeseries_source("mock")

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        klines = mock_source.get_kline_data('600000', start_date, end_date, '1d')

        # 验证DataFrame格式
        import pandas as pd
        assert isinstance(klines, pd.DataFrame)
        assert len(klines) > 0

        # 验证必填列
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'amount']
        for col in required_columns:
            assert col in klines.columns, f"Missing column: {col}"

        # 验证OHLC关系
        for _, row in klines.iterrows():
            o, h, l, c = row['open'], row['high'], row['low'], row['close']
            assert h >= max(o, c) >= min(o, c) >= l, f"Invalid OHLC relationship: {o},{h},{l},{c}"

    def test_data_precision_control(self):
        """测试数据精度控制"""
        # 自定义配置
        custom_config = MockDataConfig(
            seed=12345,
            price_precision=3,
            percentage_precision=3
        )

        from src.data_sources.mock.enhanced_timeseries_mock import EnhancedMockTimeSeriesDataSource
        enhanced_source = EnhancedMockTimeSeriesDataSource(custom_config)

        quotes = enhanced_source.get_realtime_quotes(['600000'])

        for quote in quotes:
            # 验证精度控制
            if 'price' in quote:
                price_str = str(quote['price'])
                decimal_places = len(price_str.split('.')[-1]) if '.' in price_str else 0
                assert decimal_places <= custom_config.price_precision

            if 'change_percent' in quote:
                pct_str = str(quote['change_percent'])
                decimal_places = len(pct_str.split('.')[-1]) if '.' in pct_str else 0
                assert decimal_places <= custom_config.percentage_precision

    def test_cache_mechanism(self):
        """测试缓存机制"""
        from src.data_sources.mock.enhanced_timeseries_mock import EnhancedMockTimeSeriesDataSource

        config = MockDataConfig(seed=12345, cache_ttl=5, enable_cache=True)
        enhanced_source = EnhancedMockTimeSeriesDataSource(config)

        # 第一次调用 - 生成新数据
        import time
        start_time = time.time()
        quotes1 = enhanced_source.get_realtime_quotes(['600000'])
        first_call_time = time.time() - start_time

        # 第二次调用 - 使用缓存
        start_time = time.time()
        quotes2 = enhanced_source.get_realtime_quotes(['600000'])
        second_call_time = time.time() - start_time

        # 验证缓存效果
        assert len(quotes1) == len(quotes2)
        assert quotes1[0]['symbol'] == quotes2[0]['symbol']  # 缓存应返回相同数据
        assert second_call_time < first_call_time  # 缓存调用应更快

    def test_fallback_mechanism(self):
        """测试降级机制"""
        # 尝试获取不存在的数据源，应该降级到Mock
        result = self.factory.get_data_with_fallback(
            "timeseries", "get_realtime_quotes", ['600000']
        )

        # 验证降级成功
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'symbol' in result[0]
```

#### 4.2 性能测试套件

```python
# scripts/tests/test_mock_performance.py
import time
import pytest
from src.data_sources.mock.enhanced_timeseries_mock import EnhancedMockTimeSeriesDataSource
from src.config.data_source_config import MockDataConfig

class TestMockPerformance:
    """Mock数据性能测试套件"""

    def setup_method(self):
        self.config = MockDataConfig(seed=12345)
        self.source = EnhancedMockTimeSeriesDataSource(self.config)

    def test_realtime_quotes_performance(self):
        """测试实时行情生成性能"""
        # 测试不同数据量的性能
        test_cases = [
            (100, "小批量"),
            (1000, "中批量"),
            (5000, "大批量")
        ]

        for symbol_count, description in test_cases:
            symbols = [f"60{str(i).zfill(4)}" for i in range(symbol_count)]

            start_time = time.time()
            quotes = self.source.get_realtime_quotes(symbols)
            duration = time.time() - start_time

            # 性能断言
            assert len(quotes) == symbol_count, f"{description}: 数据量不匹配"
            assert duration < 1.0, f"{description}: 生成时间过长 {duration:.3f}s"

            # 计算性能指标
            records_per_second = symbol_count / duration
            print(f"{description} - {symbol_count}条记录: {duration:.3f}s, {records_per_second:.0f}记录/秒")

            # 性能基准
            if symbol_count == 100:
                assert duration < 0.1, f"小批量应在0.1秒内完成: {duration:.3f}s"
            elif symbol_count == 1000:
                assert duration < 0.5, f"中批量应在0.5秒内完成: {duration:.3f}s"

    def test_kline_data_performance(self):
        """测试K线数据生成性能"""
        test_cases = [
            (30, "月度数据"),
            (90, "季度数据"),
            (252, "年度数据")
        ]

        for days, description in test_cases:
            start_time = time.time()
            klines = self.source.get_kline_data(
                '600000',
                datetime(2024, 1, 1),
                datetime(2024, 1, 1) + timedelta(days=days),
                '1d'
            )
            duration = time.time() - start_time

            # 性能断言
            assert len(klines) <= days, f"{description}: 数据量超出预期"
            assert duration < 1.0, f"{description}: 生成时间过长 {duration:.3f}s"

            print(f"{description} - {len(klines)}条K线: {duration:.3f}s")

    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 生成大量数据
        for i in range(100):
            symbols = [f"60{str(j).zfill(4)}" for j in range(100)]
            quotes = self.source.get_realtime_quotes(symbols)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # 内存使用断言
        assert memory_increase < 100, f"内存增长过多: {memory_increase:.2f}MB"

        print(f"内存使用: 初始 {initial_memory:.2f}MB -> 最终 {final_memory:.2f}MB (增长 {memory_increase:.2f}MB)")
```

### Step 5: 监控实施

#### 5.1 数据质量监控

```python
# src/monitoring/data_quality_monitor.py
import logging
from datetime import datetime
from typing import Dict, List, Any
from src.decorators.data_quality import _check_data_quality

class DataQualityMonitor:
    """数据质量监控器"""

    def __init__(self):
        self.quality_metrics = {}
        self.logger = logging.getLogger(__name__)

    def monitor_data_quality(self, data: Any, data_type: str, source: str = "unknown") -> Dict[str, Any]:
        """监控数据质量"""
        timestamp = datetime.now()

        # 执行质量检查
        issues = _check_data_quality(data, data_type)

        # 计算质量分数
        quality_score = max(0, 100 - len(issues) * 10)

        # 记录质量指标
        self.quality_metrics[f"{data_type}_{timestamp.isoformat()}"] = {
            'timestamp': timestamp,
            'data_type': data_type,
            'source': source,
            'quality_score': quality_score,
            'issues': issues,
            'record_count': len(data) if isinstance(data, (list, tuple)) else 1
        }

        # 记录日志
        if quality_score < 80:
            self.logger.warning(f"Low data quality detected for {data_type}: score={quality_score}, issues={issues}")
        elif quality_score < 95:
            self.logger.info(f"Data quality acceptable for {data_type}: score={quality_score}")
        else:
            self.logger.debug(f"Data quality excellent for {data_type}: score={quality_score}")

        return {
            'timestamp': timestamp,
            'quality_score': quality_score,
            'issues': issues,
            'status': 'good' if quality_score >= 80 else 'poor'
        }

    def get_quality_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取质量摘要"""
        from datetime import timedelta

        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_metrics = {
            key: value for key, value in self.quality_metrics.items()
            if value['timestamp'] >= cutoff_time
        }

        if not recent_metrics:
            return {'status': 'no_data', 'message': f'No quality data in last {hours} hours'}

        # 计算统计指标
        scores = [m['quality_score'] for m in recent_metrics.values()]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)

        # 按数据类型分组
        type_scores = {}
        for metric in recent_metrics.values():
            data_type = metric['data_type']
            if data_type not in type_scores:
                type_scores[data_type] = []
            type_scores[data_type].append(metric['quality_score'])

        type_stats = {}
        for data_type, scores in type_scores.items():
            type_stats[data_type] = {
                'avg_score': sum(scores) / len(scores),
                'min_score': min(scores),
                'max_score': max(scores),
                'count': len(scores)
            }

        return {
            'period_hours': hours,
            'total_checks': len(recent_metrics),
            'overall_avg_score': avg_score,
            'overall_min_score': min_score,
            'overall_max_score': max_score,
            'type_breakdown': type_stats,
            'status': 'good' if avg_score >= 80 else 'poor'
        }
```

#### 5.2 性能监控

```python
# src/monitoring/performance_monitor.py
import time
import logging
from functools import wraps
from typing import Dict, Any

class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.performance_metrics = {}
        self.logger = logging.getLogger(__name__)

    def monitor_method_performance(self, method_name: str):
        """方法性能监控装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    duration = time.time() - start_time

                    # 记录性能指标
                    self._record_performance(method_name, duration, success, error)

                return result
            return wrapper
        return decorator

    def _record_performance(self, method_name: str, duration: float, success: bool, error: str = None):
        """记录性能指标"""
        timestamp = time.time()

        if method_name not in self.performance_metrics:
            self.performance_metrics[method_name] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_duration': 0.0,
                'min_duration': float('inf'),
                'max_duration': 0.0,
                'avg_duration': 0.0,
                'recent_calls': []
            }

        metrics = self.performance_metrics[method_name]
        metrics['total_calls'] += 1
        metrics['total_duration'] += duration
        metrics['min_duration'] = min(metrics['min_duration'], duration)
        metrics['max_duration'] = max(metrics['max_duration'], duration)
        metrics['avg_duration'] = metrics['total_duration'] / metrics['total_calls']

        if success:
            metrics['successful_calls'] += 1
        else:
            metrics['failed_calls'] += 1

        # 记录最近调用
        metrics['recent_calls'].append({
            'timestamp': timestamp,
            'duration': duration,
            'success': success,
            'error': error
        })

        # 只保留最近100次调用
        if len(metrics['recent_calls']) > 100:
            metrics['recent_calls'] = metrics['recent_calls'][-100:]

        # 性能警告
        if duration > 1.0:  # 超过1秒
            self.logger.warning(f"Slow method call: {method_name} took {duration:.3f}s")

        if metrics['failed_calls'] / metrics['total_calls'] > 0.1:  # 失败率超过10%
            self.logger.error(f"High failure rate for {method_name}: {metrics['failed_calls']}/{metrics['total_calls']}")

    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取性能摘要"""
        summary = {}

        for method_name, metrics in self.performance_metrics.items():
            success_rate = (metrics['successful_calls'] / metrics['total_calls'] * 100) if metrics['total_calls'] > 0 else 0

            summary[method_name] = {
                'total_calls': metrics['total_calls'],
                'success_rate': round(success_rate, 2),
                'avg_duration': round(metrics['avg_duration'], 3),
                'min_duration': round(metrics['min_duration'], 3),
                'max_duration': round(metrics['max_duration'], 3),
                'status': self._get_method_status(metrics)
            }

        return summary

    def _get_method_status(self, metrics: Dict[str, Any]) -> str:
        """获取方法状态"""
        if metrics['total_calls'] == 0:
            return 'no_calls'

        success_rate = metrics['successful_calls'] / metrics['total_calls']
        avg_duration = metrics['avg_duration']

        if success_rate >= 0.95 and avg_duration < 0.1:
            return 'excellent'
        elif success_rate >= 0.90 and avg_duration < 0.5:
            return 'good'
        elif success_rate >= 0.80 and avg_duration < 1.0:
            return 'acceptable'
        else:
            return 'poor'
```

### Step 6: 部署指南

#### 6.1 开发环境部署

```bash
# 1. 配置开发环境
cp .env.example .env.dev

# 2. 编辑开发环境配置
cat > .env.dev << EOF
# 开发环境 - 使用Mock数据
TIMESERIES_DATA_SOURCE=mock
RELATIONAL_DATA_SOURCE=mock
BUSINESS_DATA_SOURCE=mock

# Mock数据配置
MOCK_DATA_SEED=12345
MOCK_DATA_LOCALE=zh_CN
MOCK_DATA_CACHE_TTL=60
MOCK_DATA_PRECISION=2
MOCK_DATA_CACHE_ENABLED=true

# 日志配置
LOG_LEVEL=DEBUG
LOG_FORMAT=detailed
EOF

# 3. 启动开发服务
export ENV_FILE=.env.dev
python -m src.main

# 4. 运行测试套件
python scripts/tests/test_mock_real_compatibility.py
python scripts/tests/test_mock_performance.py
```

#### 6.2 测试环境部署

```bash
# 1. 配置测试环境 - 支持Mock/Real切换
cat > .env.test << EOF
# 测试环境 - 可切换数据源
TIMESERIES_DATA_SOURCE=mock
RELATIONAL_DATA_SOURCE=mock
BUSINESS_DATA_SOURCE=mock

# Mock数据配置 - 使用固定种子确保测试可重现
MOCK_DATA_SEED=99999
MOCK_DATA_LOCALE=zh_CN
MOCK_DATA_CACHE_TTL=0  # 测试环境禁用缓存
MOCK_DATA_PRECISION=2
MOCK_DATA_CACHE_ENABLED=false

# 真实数据连接配置(用于Real模式测试)
TDENGINE_HOST=test-tdengine.example.com
TDENGINE_PORT=6030
TDENGINE_USER=test_user
TDENGINE_PASSWORD=test_password
TDENGINE_DATABASE=test_mystocks

POSTGRESQL_HOST=test-postgres.example.com
POSTGRESQL_PORT=5432
POSTGRESQL_USER=test_user
POSTGRESQL_PASSWORD=test_password
POSTGRESQL_DATABASE=test_mystocks

# 测试配置
ENABLE_DATA_QUALITY_MONITORING=true
ENABLE_PERFORMANCE_MONITORING=true
LOG_LEVEL=INFO
EOF

# 2. 运行兼容性测试
export ENV_FILE=.env.test
python scripts/tests/test_compatibility.py --env=test

# 3. 运行性能测试
python scripts/tests/test_performance.py --env=test

# 4. 数据质量检查
python scripts/monitoring/check_data_quality.py --env=test
```

#### 6.3 生产环境部署

```bash
# 1. 配置生产环境
cat > .env.prod << EOF
# 生产环境 - 使用Real数据
TIMESERIES_DATA_SOURCE=tdengine
RELATIONAL_DATA_SOURCE=postgresql
BUSINESS_DATA_SOURCE=composite

# 真实数据连接配置
TDENGINE_HOST=prod-tdengine-cluster.example.com
TDENGINE_PORT=6030
TDENGINE_USER=prod_user
TDENGINE_PASSWORD=prod_secure_password
TDENGINE_DATABASE=mystocks

POSTGRESQL_HOST=prod-postgres-cluster.example.com
POSTGRESQL_PORT=5432
POSTGRESQL_USER=prod_user
POSTGRESQL_PASSWORD=prod_secure_password
POSTGRESQL_DATABASE=mystocks

# 降级配置 - 紧急情况下使用Mock数据
ENABLE_MOCK_FALLBACK=true
MOCK_FALLBACK_THRESHOLD=0.1  # 10%失败率触发降级

# 监控配置
ENABLE_DATA_QUALITY_MONITORING=true
ENABLE_PERFORMANCE_MONITORING=true
MONITORING_ALERT_EMAIL=ops@example.com

# 日志配置
LOG_LEVEL=WARNING
LOG_FORMAT=json
LOG_FILE=/var/log/mystocks/data-source.log
EOF

# 2. 启动生产服务
export ENV_FILE=.env.prod
python -m src.main --production

# 3. 健康检查
curl http://localhost:8000/health

# 4. 数据质量检查
curl http://localhost:8000/monitoring/data-quality

# 5. 性能监控
curl http://localhost:8000/monitoring/performance
```

---

## 📊 实施检查清单

### Phase 1: 基础实施 (✅ 完成)

- [x] 环境变量配置标准化
- [x] 数据源工厂实现
- [x] Mock数据结构规范
- [x] 数据质量验证机制
- [x] 基础测试套件

### Phase 2: 增强实施 (🔄 进行中)

- [x] 增强版Mock数据源
- [x] 性能监控机制
- [x] 缓存机制优化
- [x] 兼容性测试套件
- [ ] 真实数据源接入
- [ ] 降级机制实现

### Phase 3: 生产就绪 (⏳ 待实施)

- [ ] 生产环境配置
- [ ] 监控告警系统
- [ ] 自动化测试流程
- [ ] 性能基准建立
- [ ] 文档完善
- [ ] 运维手册

### Phase 4: 持续优化 (⏳ 规划中)

- [ ] 数据质量持续改进
- [ ] 性能优化迭代
- [ ] 新数据类型支持
- [ ] 监控指标扩展
- [ ] 故障恢复机制
- [ ] 容量规划

---

## 🚀 快速开始

### 开发者快速入门

```python
# 1. 使用工厂模式获取数据源
from src.core.smart_data_source_factory import SmartDataSourceFactory

factory = SmartDataSourceFactory()

# 2. 获取Mock数据源(自动从环境变量读取)
ts_source = factory.get_timeseries_source()
rel_source = factory.get_relational_source()
business_source = factory.get_business_source()

# 3. 使用数据源
quotes = ts_source.get_realtime_quotes(['600000', '000001'])
watchlist = rel_source.get_watchlist(user_id=1)
dashboard = business_source.get_dashboard_summary(user_id=1)

# 4. 使用降级机制(推荐生产环境使用)
result = factory.get_data_with_fallback('timeseries', 'get_realtime_quotes', ['600000'])
```

### 测试用例示例

```python
# tests/test_example.py
import pytest
from src.core.smart_data_source_factory import SmartDataSourceFactory

class TestExample:
    def setup_method(self):
        self.factory = SmartDataSourceFactory()

    def test_example(self):
        # 获取Mock数据源
        mock_source = self.factory.get_timeseries_source("mock")

        # 验证数据质量
        quotes = mock_source.get_realtime_quotes(['600000'])
        assert len(quotes) > 0
        assert 'symbol' in quotes[0]
        assert quotes[0]['price'] > 0
```

---

## 📞 技术支持

### 常见问题解决

#### Q1: Mock数据与Real数据格式不一致
**解决方案**: 使用 `EnhancedMockDataSource` 替代基础Mock数据源，确保严格遵循数据映射规范。

#### Q2: 性能测试超时
**解决方案**: 调整Mock数据配置，禁用缓存或减少数据生成量。

#### Q3: 环境变量配置不生效
**解决方案**: 检查 `.env` 文件格式，确保没有语法错误，重启应用服务。

#### Q4: 降级机制未触发
**解决方案**: 检查降级配置和阈值设置，确保错误处理逻辑正确实现。

### 联系方式

- **技术负责人**: MyStocks Backend Team
- **文档维护**: Claude Code Assistant
- **问题反馈**: GitHub Issues
- **紧急支持**: ops@example.com

---

*本文档版本: v1.0 | 最后更新: 2025-01-21*
