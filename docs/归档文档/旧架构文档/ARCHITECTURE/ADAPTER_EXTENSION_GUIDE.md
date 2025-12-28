# MyStocks Adapter 功能实现与扩展指南

## 目录
1. [已实现功能清单](#已实现功能清单)
2. [功能扩展标准方法](#功能扩展标准方法)
3. [重复功能管理策略](#重复功能管理策略)
4. [完整扩展实例](#完整扩展实例)

---

## 已实现功能清单

### 1. IDataSource接口定义的标准功能

**位置**: `interfaces/data_source.py`

所有适配器必须实现以下8个核心方法：

| 方法名 | 功能说明 | 返回类型 | 实现状态 |
|-------|---------|---------|---------|
| `get_stock_daily()` | 获取股票日线数据 | `pd.DataFrame` | ✅ 全部实现 |
| `get_index_daily()` | 获取指数日线数据 | `pd.DataFrame` | ✅ 全部实现 |
| `get_stock_basic()` | 获取股票基本信息 | `Dict` | ✅ 全部实现 |
| `get_index_components()` | 获取指数成分股 | `List[str]` | ✅ 全部实现 |
| `get_real_time_data()` | 获取实时行情数据 | `Union[Dict, str]` | ✅ 全部实现 |
| `get_market_calendar()` | 获取交易日历 | `Union[pd.DataFrame, str]` | ✅ 全部实现 |
| `get_financial_data()` | 获取财务数据 | `Union[pd.DataFrame, str]` | ✅ 全部实现 |
| `get_news_data()` | 获取新闻数据 | `Union[List[Dict], str]` | ✅ 全部实现 |

### 2. 各适配器已实现功能对比

#### AkshareAdapter (`adapters/akshare_adapter.py`)

**标准接口实现** (8个):
- ✅ `get_stock_daily()` - 支持前复权，多API备用
- ✅ `get_index_daily()` - 支持新浪/东方财富/通用三个接口
- ✅ `get_stock_basic()` - 使用stock_individual_info_em
- ✅ `get_index_components()` - 使用index_stock_cons
- ✅ `get_real_time_data()` - 使用stock_zh_a_spot
- ✅ `get_market_calendar()` - 使用tool_trade_date_hist_sina
- ✅ `get_financial_data()` - 使用stock_financial_abstract
- ✅ `get_news_data()` - 使用stock_news_em

**扩展功能** (3个):
- ✅ `get_ths_industry_summary()` - 同花顺行业概览
- ✅ `get_ths_industry_stocks()` - 指定行业成分股
- ✅ `get_ths_industry_names()` - 行业名称列表

**特色功能**:
- 🔄 自动重试机制（最多3次）
- 🔀 多API备用策略
- 📝 完整的日志记录
- ⏱️ 超时控制
- 🗺️ 统一列名映射

#### TdxAdapter (`adapters/tdx_adapter.py`)

**标准接口实现** (8个):
- ✅ `get_stock_daily()` - 通达信历史日线
- ✅ `get_index_daily()` - 指数历史行情
- ✅ `get_stock_basic()` - 股票基本信息
- ✅ `get_index_components()` - 成分股列表
- ✅ `get_real_time_data()` - 5档行情快照
- ✅ `get_market_calendar()` - 交易日历
- ✅ `get_financial_data()` - 财务数据
- ✅ `get_news_data()` - 新闻数据

**扩展功能** (7个):
- ✅ `get_minute_data()` - 分钟K线数据
- ✅ `get_5min_data()` - 5分钟K线
- ✅ `get_transaction_data()` - 分笔成交
- ✅ `get_history_transaction_data()` - 历史成交
- ✅ `get_index_bars()` - 指数K线
- ✅ `get_minute_time_data()` - 分时行情
- ✅ `get_history_minute_time_data()` - 历史分时

**特色功能**:
- 🚀 极低延迟（本地通达信API）
- 📊 支持多周期（1分/5分/15分/30分/60分/日/周/月）
- 💾 自动连接管理
- 🔌 连接池支持

#### BaostockAdapter (`adapters/baostock_adapter.py`)

**标准接口实现** (8个):
- ✅ `get_stock_daily()` - 日线行情
- ✅ `get_index_daily()` - 指数行情
- ✅ `get_stock_basic()` - 证券基本资料
- ✅ `get_index_components()` - 指数成分股
- ✅ `get_real_time_data()` - 实时行情
- ✅ `get_market_calendar()` - 交易日历
- ✅ `get_financial_data()` - 财务数据
- ✅ `get_news_data()` - 新闻数据

**特色功能**:
- 🔐 自动登录/登出管理
- 📈 支持复权类型选择
- 📊 完整的财务数据

#### CustomerAdapter (`adapters/customer_adapter.py`)

**标准接口实现** (8个):
- ✅ `get_stock_daily()` - 历史行情
- ✅ `get_index_daily()` - 指数行情
- ✅ `get_stock_basic()` - 股票信息
- ✅ `get_index_components()` - 成分股
- ✅ `get_real_time_data()` - 实时行情
- ✅ `get_market_calendar()` - 交易日历
- ✅ `get_financial_data()` - 财务数据
- ✅ `get_news_data()` - 新闻数据

**扩展功能** (1个):
- ✅ `get_market_realtime_quotes()` - 沪深全市场实时行情

**特色功能**:
- 🎯 基于efinance库
- 🌐 完整市场覆盖
- 🗺️ 支持列名映射

#### FinancialAdapter (`adapters/financial_adapter.py`)

**标准接口实现** (8个):
- ✅ `get_stock_daily()` - 综合多源
- ✅ `get_index_daily()` - 综合多源
- ✅ `get_stock_basic()` - 综合多源
- ✅ `get_index_components()` - 综合多源
- ✅ `get_real_time_data()` - 综合多源
- ✅ `get_market_calendar()` - 综合多源
- ✅ `get_financial_data()` - 综合多源
- ✅ `get_news_data()` - 综合多源

**特色功能**:
- 🔀 自动多源切换
- 🛡️ 容错处理
- 📊 数据聚合

### 3. 功能实现统计

```
总计适配器数量: 5个
标准接口方法: 8个
必须实现方法: 8个（所有适配器100%实现）

扩展功能统计:
├── AkshareAdapter: 3个扩展方法
├── TdxAdapter: 7个扩展方法
├── BaostockAdapter: 0个扩展方法
├── CustomerAdapter: 1个扩展方法
└── FinancialAdapter: 0个扩展方法

总计扩展功能: 11个
```

### 4. 功能覆盖矩阵

| 功能类别 | AKShare | TDX | Baostock | Customer | Financial |
|---------|---------|-----|----------|----------|-----------|
| 日线数据 | ✅✅✅ | ✅✅ | ✅ | ✅ | ✅ |
| 分钟数据 | ✅ | ✅✅✅ | ✅ | ✅ | ✅ |
| 实时行情 | ✅✅ | ✅✅✅ | ✅ | ✅✅ | ✅ |
| 财务数据 | ✅✅ | ✅ | ✅✅ | ✅ | ✅✅ |
| 行业数据 | ✅✅✅ | ❌ | ❌ | ❌ | ✅ |
| 分笔成交 | ❌ | ✅✅✅ | ❌ | ❌ | ❌ |
| 新闻资讯 | ✅✅ | ✅ | ✅ | ✅ | ✅ |

**图例**: ✅ 基础实现 | ✅✅ 良好实现 | ✅✅✅ 优秀实现 | ❌ 未实现

---

## 功能扩展标准方法

### 扩展方式1: 在现有适配器中添加新方法

#### 步骤1: 评估是否需要加入IDataSource接口

**判断标准**:
- ✅ 如果功能是通用的（所有数据源都应该支持） → 加入接口
- ❌ 如果功能是特定数据源独有的 → 不加入接口

**示例**: 分钟K线数据

```python
# 决策: TDX特色功能，不加入IDataSource接口

# 在 adapters/tdx_adapter.py 中直接添加
class TdxDataSource(IDataSource):
    # ... 标准接口实现 ...

    def get_minute_data(
        self,
        symbol: str,
        period: int = 1,  # 1, 5, 15, 30, 60
        count: int = 800
    ) -> pd.DataFrame:
        """
        获取分钟K线数据（TDX特色功能）

        Args:
            symbol: 股票代码
            period: 周期（1/5/15/30/60）
            count: 数量

        Returns:
            pd.DataFrame: 分钟K线数据
        """
        # 实现逻辑
        pass
```

#### 步骤2: 添加方法文档和类型注解

```python
def get_minute_data(
    self,
    symbol: str,
    period: int = 1,
    count: int = 800
) -> pd.DataFrame:
    """
    获取分钟K线数据

    这是TDX数据源的特色功能，提供1/5/15/30/60分钟级别的K线数据。

    Args:
        symbol: 股票代码，格式如 '600000' 或 '000001'
        period: K线周期，支持 1, 5, 15, 30, 60 分钟
        count: 返回数据条数，默认800条

    Returns:
        pd.DataFrame: 分钟K线数据，包含以下列：
            - datetime: 时间
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量

    Raises:
        ValueError: 当period不在支持范围内时
        ConnectionError: 当TDX连接失败时

    Example:
        >>> tdx = TdxDataSource()
        >>> df = tdx.get_minute_data('600000', period=5, count=240)
        >>> print(f"获取到 {len(df)} 条5分钟K线数据")
    """
    # 实现逻辑
    pass
```

#### 步骤3: 实现并测试

```python
def get_minute_data(self, symbol: str, period: int = 1, count: int = 800) -> pd.DataFrame:
    """获取分钟K线数据"""
    try:
        # 1. 验证参数
        if period not in [1, 5, 15, 30, 60]:
            raise ValueError(f"不支持的周期: {period}，仅支持 1, 5, 15, 30, 60")

        # 2. 格式化股票代码
        market, stock_code = self._parse_symbol(symbol)

        # 3. 调用pytdx API
        data = self.api.get_security_bars(
            category=self._get_category_by_period(period),
            market=market,
            code=stock_code,
            start=0,
            count=count
        )

        # 4. 转换为DataFrame
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # 5. 标准化列名
        df = df.rename(columns={
            'datetime': 'datetime',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'vol': 'volume'
        })

        return df

    except Exception as e:
        print(f"获取分钟数据失败: {e}")
        return pd.DataFrame()
```

#### 步骤4: 编写单元测试

```python
# tests/test_tdx_adapter.py

def test_get_minute_data():
    """测试获取分钟K线"""
    tdx = TdxDataSource()

    # 测试1: 正常获取
    df = tdx.get_minute_data('600000', period=5, count=100)
    assert not df.empty
    assert len(df) <= 100
    assert 'datetime' in df.columns

    # 测试2: 无效周期
    with pytest.raises(ValueError):
        tdx.get_minute_data('600000', period=3)

    # 测试3: 无效代码
    df = tdx.get_minute_data('999999', period=1)
    assert df.empty
```

### 扩展方式2: 创建新的适配器

#### 适用场景
- 需要支持全新的数据源
- 现有适配器无法满足需求
- 数据源API差异较大

#### 标准模板

```python
# adapters/new_source_adapter.py

'''
# 功能: 新数据源适配器
# 作者: Your Name
# 创建日期: 2025-10-16
# 版本: 1.0.0
'''

import pandas as pd
from typing import Dict, List, Union, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interfaces.data_source import IDataSource
from utils.date_utils import normalize_date
from utils.symbol_utils import format_stock_code_for_source
from utils.column_mapper import ColumnMapper


class NewSourceAdapter(IDataSource):
    """
    新数据源适配器

    功能:
        - 实现IDataSource接口的所有标准方法
        - 提供数据源特色功能
        - 统一数据格式和列名

    使用示例:
        >>> adapter = NewSourceAdapter(api_key='your_key')
        >>> df = adapter.get_stock_daily('600000', '2024-01-01', '2024-12-31')
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        初始化适配器

        Args:
            api_key: API密钥（如需要）
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.config = kwargs
        print(f"[NewSource] 适配器初始化完成")

    # ==================== 必须实现的8个标准接口 ====================

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据"""
        try:
            # 1. 格式化参数
            stock_code = format_stock_code_for_source(symbol, 'new_source')
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)

            # 2. 调用数据源API
            # TODO: 实现实际的API调用
            data = self._fetch_daily_data(stock_code, start_date, end_date)

            # 3. 转换为DataFrame
            df = pd.DataFrame(data)

            # 4. 标准化列名
            df = ColumnMapper.to_english(df)

            return df

        except Exception as e:
            print(f"[NewSource] 获取日线数据失败: {e}")
            return pd.DataFrame()

    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数日线数据"""
        # TODO: 实现
        pass

    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息"""
        # TODO: 实现
        pass

    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股"""
        # TODO: 实现
        pass

    def get_real_time_data(self, symbol: str) -> Union[Dict, str]:
        """获取实时行情数据"""
        # TODO: 实现
        pass

    def get_market_calendar(self, start_date: str, end_date: str) -> Union[pd.DataFrame, str]:
        """获取交易日历"""
        # TODO: 实现
        pass

    def get_financial_data(self, symbol: str, period: str = "annual") -> Union[pd.DataFrame, str]:
        """获取财务数据"""
        # TODO: 实现
        pass

    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> Union[List[Dict], str]:
        """获取新闻数据"""
        # TODO: 实现
        pass

    # ==================== 扩展功能（可选） ====================

    def get_custom_feature(self, **kwargs):
        """
        自定义特色功能

        这是新数据源的特色功能，其他数据源不一定支持。
        """
        # TODO: 实现特色功能
        pass

    # ==================== 内部辅助方法 ====================

    def _fetch_daily_data(self, symbol: str, start_date: str, end_date: str):
        """内部方法：获取日线数据"""
        # 实际的API调用逻辑
        pass

    def _validate_symbol(self, symbol: str) -> bool:
        """内部方法：验证股票代码"""
        # 验证逻辑
        pass
```

#### 注册新适配器

```python
# 方式1: 在工厂类中注册
from factory.data_source_factory import DataSourceFactory
from adapters.new_source_adapter import NewSourceAdapter

DataSourceFactory.register_source('new_source', NewSourceAdapter)

# 方式2: 在管理器中注册
from adapters.data_source_manager import DataSourceManager

manager = DataSourceManager()
manager.register_source('new_source', NewSourceAdapter())

# 方式3: 批量注册
DataSourceFactory.register_multiple_sources({
    'new_source1': NewSource1Adapter,
    'new_source2': NewSource2Adapter,
})
```

### 扩展方式3: 修改IDataSource接口（慎重）

#### 适用场景
- 新功能确实是所有数据源都应该支持的
- 新功能对系统架构有重大价值
- 有足够时间更新所有现有适配器

#### 标准流程

**步骤1**: 在IDataSource中添加抽象方法

```python
# interfaces/data_source.py

class IDataSource(abc.ABC):
    # ... 现有方法 ...

    @abc.abstractmethod
    def get_option_data(self, symbol: str, option_type: str) -> pd.DataFrame:
        """
        获取期权数据（新增标准接口）

        Args:
            symbol: 标的代码
            option_type: 期权类型（call/put）

        Returns:
            pd.DataFrame: 期权数据
        """
        pass
```

**步骤2**: 更新所有现有适配器

```python
# adapters/akshare_adapter.py
class AkshareDataSource(IDataSource):
    def get_option_data(self, symbol: str, option_type: str) -> pd.DataFrame:
        """实现期权数据获取"""
        # 实现逻辑
        pass

# adapters/tdx_adapter.py
class TdxDataSource(IDataSource):
    def get_option_data(self, symbol: str, option_type: str) -> pd.DataFrame:
        """实现期权数据获取"""
        # 实现逻辑
        pass

# ... 更新所有其他适配器 ...
```

**步骤3**: 更新文档和测试

```python
# tests/test_interface_compliance.py

def test_all_adapters_implement_option_data():
    """测试所有适配器都实现了新接口"""
    from factory.data_source_factory import DataSourceFactory

    for source_type in DataSourceFactory.get_available_sources():
        adapter = DataSourceFactory.create_source(source_type)
        assert hasattr(adapter, 'get_option_data')
        # 测试实际调用
        df = adapter.get_option_data('510050', 'call')
        assert isinstance(df, pd.DataFrame)
```

---

## 重复功能管理策略

### 问题识别

当多个适配器实现相同功能时，可能存在以下问题：

1. **代码重复** - 相同逻辑在多处实现
2. **维护困难** - 修改需要同步多处
3. **一致性风险** - 不同实现可能产生不同结果
4. **测试冗余** - 重复的测试代码

### 管理策略

#### 策略1: 提取公共基类

**适用**: 多个适配器有相同的辅助逻辑

```python
# adapters/base_adapter.py

class BaseDataSourceAdapter(IDataSource):
    """
    数据源适配器基类

    提供通用的辅助方法和默认实现
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    # ==================== 公共辅助方法 ====================

    def _retry_with_backoff(self, func, max_retries=3, initial_delay=1):
        """
        带指数退避的重试机制（公共方法）

        Args:
            func: 要执行的函数
            max_retries: 最大重试次数
            initial_delay: 初始延迟（秒）

        Returns:
            函数执行结果
        """
        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                return func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    delay = initial_delay * (2 ** (attempt - 1))
                    self.logger.warning(f"第{attempt}次尝试失败,{delay}秒后重试: {e}")
                    time.sleep(delay)

        raise last_exception

    def _validate_date_range(self, start_date: str, end_date: str) -> bool:
        """
        验证日期范围（公共方法）

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            bool: 是否有效
        """
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            return start <= end
        except:
            return False

    def _standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化DataFrame格式（公共方法）

        统一处理:
        - 列名映射
        - 数据类型转换
        - 缺失值处理
        """
        if df.empty:
            return df

        # 列名标准化
        df = ColumnMapper.to_english(df)

        # 日期列处理
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # 数值列处理
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    # ==================== 默认实现（子类可覆盖） ====================

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        默认实现: 交易日历

        子类可以覆盖此方法提供特定实现
        """
        self.logger.warning(f"{self.__class__.__name__} 使用默认交易日历实现")

        # 提供简单的交易日历（周一到周五）
        date_range = pd.date_range(start=start_date, end=end_date, freq='B')
        return pd.DataFrame({'date': date_range, 'is_trading_day': True})
```

**使用基类**:

```python
# adapters/akshare_adapter.py

class AkshareDataSource(BaseDataSourceAdapter):
    """AKShare适配器 - 继承公共基类"""

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线"""

        # 使用基类的公共方法
        if not self._validate_date_range(start_date, end_date):
            raise ValueError("日期范围无效")

        # 使用基类的重试机制
        def fetch():
            return ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date)

        df = self._retry_with_backoff(fetch, max_retries=3)

        # 使用基类的标准化方法
        return self._standardize_dataframe(df)
```

#### 策略2: 创建工具函数库

**适用**: 独立的工具函数，不依赖适配器状态

```python
# utils/adapter_utils.py

"""
适配器通用工具函数库
"""

import pandas as pd
import time
from typing import Callable, Any
from functools import wraps


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    装饰器: 失败自动重试

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）

    Example:
        @retry_on_failure(max_retries=3, delay=2.0)
        def fetch_data():
            return api.get_data()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        print(f"第{attempt}次尝试失败,{delay}秒后重试: {e}")
                        time.sleep(delay * attempt)

            raise last_exception

        return wrapper
    return decorator


def safe_to_dataframe(data: Any) -> pd.DataFrame:
    """
    安全转换为DataFrame

    处理各种数据格式:
    - list of dict
    - dict
    - DataFrame
    - None/空数据

    Args:
        data: 原始数据

    Returns:
        pd.DataFrame: 转换后的DataFrame
    """
    if data is None:
        return pd.DataFrame()

    if isinstance(data, pd.DataFrame):
        return data

    if isinstance(data, list):
        return pd.DataFrame(data)

    if isinstance(data, dict):
        return pd.DataFrame([data])

    # 尝试强制转换
    try:
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()


def format_symbol_unified(symbol: str, market: str = 'CN') -> str:
    """
    统一股票代码格式

    Args:
        symbol: 原始代码
        market: 市场（CN/US/HK）

    Returns:
        str: 格式化后的代码
    """
    # 去除空格和特殊字符
    symbol = symbol.strip().upper()

    if market == 'CN':
        # 中国市场: 纯数字6位
        symbol = ''.join(filter(str.isdigit, symbol))
        return symbol.zfill(6)

    return symbol
```

**使用工具函数**:

```python
# adapters/any_adapter.py

from utils.adapter_utils import retry_on_failure, safe_to_dataframe

class AnyAdapter(IDataSource):

    @retry_on_failure(max_retries=3, delay=1.0)
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取日线数据 - 使用重试装饰器"""

        # API调用
        data = some_api.get_data(symbol, start_date, end_date)

        # 安全转换
        df = safe_to_dataframe(data)

        return df
```

#### 策略3: 适配器组合模式

**适用**: 需要组合多个数据源的功能

```python
# adapters/composite_adapter.py

class CompositeDataSource(IDataSource):
    """
    组合适配器

    特点:
    - 组合多个数据源
    - 自动选择最优数据源
    - 故障转移
    """

    def __init__(self):
        self.sources = {
            'akshare': AkshareDataSource(),
            'tdx': TdxDataSource(),
            'baostock': BaostockDataSource()
        }

        # 功能路由表
        self.routing_table = {
            'get_stock_daily': ['tdx', 'akshare', 'baostock'],
            'get_real_time_data': ['tdx', 'akshare'],
            'get_financial_data': ['akshare', 'baostock'],
            'get_news_data': ['akshare']
        }

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        组合实现: 按优先级尝试多个数据源

        优先级: TDX > AKShare > Baostock
        """
        method_name = 'get_stock_daily'
        priorities = self.routing_table[method_name]

        for source_name in priorities:
            try:
                source = self.sources[source_name]
                df = source.get_stock_daily(symbol, start_date, end_date)

                if not df.empty:
                    print(f"[Composite] 从 {source_name} 获取成功")
                    return df

            except Exception as e:
                print(f"[Composite] {source_name} 失败: {e}")
                continue

        print(f"[Composite] 所有数据源都失败")
        return pd.DataFrame()

    # 其他方法类似实现...
```

#### 策略4: 功能注册表模式

**适用**: 需要动态发现和管理功能

```python
# core/feature_registry.py

class FeatureRegistry:
    """
    功能注册表

    管理所有适配器的功能实现
    """

    def __init__(self):
        self._registry = {}  # {feature_name: {adapter_name: method}}

    def register_feature(self, feature_name: str, adapter_name: str, method: Callable):
        """
        注册功能实现

        Args:
            feature_name: 功能名称
            adapter_name: 适配器名称
            method: 实现方法
        """
        if feature_name not in self._registry:
            self._registry[feature_name] = {}

        self._registry[feature_name][adapter_name] = method

    def get_implementations(self, feature_name: str) -> Dict[str, Callable]:
        """
        获取功能的所有实现

        Returns:
            {adapter_name: method}
        """
        return self._registry.get(feature_name, {})

    def count_implementations(self, feature_name: str) -> int:
        """统计功能的实现数量"""
        return len(self.get_implementations(feature_name))

    def find_duplicate_features(self) -> Dict[str, List[str]]:
        """
        查找重复实现的功能

        Returns:
            {feature_name: [adapter_names]}
        """
        duplicates = {}

        for feature, impls in self._registry.items():
            if len(impls) > 1:
                duplicates[feature] = list(impls.keys())

        return duplicates

    def generate_report(self) -> str:
        """生成功能实现报告"""
        report = ["功能实现统计报告", "=" * 60]

        for feature, impls in sorted(self._registry.items()):
            report.append(f"\n{feature}:")
            report.append(f"  实现数量: {len(impls)}")
            report.append(f"  实现者: {', '.join(impls.keys())}")

        return "\n".join(report)


# 使用示例
registry = FeatureRegistry()

# 注册功能
for adapter_name, adapter_class in [('akshare', AkshareDataSource),
                                      ('tdx', TdxDataSource)]:
    adapter = adapter_class()

    # 注册标准功能
    registry.register_feature('get_stock_daily', adapter_name, adapter.get_stock_daily)
    registry.register_feature('get_real_time_data', adapter_name, adapter.get_real_time_data)

    # 注册扩展功能（如果有）
    if hasattr(adapter, 'get_minute_data'):
        registry.register_feature('get_minute_data', adapter_name, adapter.get_minute_data)

# 查找重复功能
duplicates = registry.find_duplicate_features()
print(f"重复实现的功能: {duplicates}")

# 生成报告
print(registry.generate_report())
```

### 重复功能管理决策树

```
功能重复了？
├─ 是
│  ├─ 是核心逻辑吗？
│  │  ├─ 是 → 使用策略1: 提取公共基类
│  │  └─ 否 → 使用策略2: 创建工具函数
│  │
│  ├─ 需要组合多个实现吗？
│  │  ├─ 是 → 使用策略3: 适配器组合
│  │  └─ 否 → 继续
│  │
│  └─ 需要动态管理吗？
│     ├─ 是 → 使用策略4: 功能注册表
│     └─ 否 → 使用策略1或2
│
└─ 否 → 保持现状
```

---

## 完整扩展实例

### 实例: 添加"获取ETF列表"功能

#### 需求分析

**功能描述**: 获取所有ETF基金的列表信息

**评估结果**:
- ✅ 通用功能 → 应该加入IDataSource接口
- ✅ 多个数据源都支持 → AKShare、TDX都能实现
- ✅ 对系统有价值 → 扩展基金数据支持

#### 实现步骤

**步骤1**: 修改接口定义

```python
# interfaces/data_source.py

class IDataSource(abc.ABC):
    # ... 现有方法 ...

    @abc.abstractmethod
    def get_etf_list(self, market: str = 'all') -> pd.DataFrame:
        """
        获取ETF列表（新增标准接口）

        Args:
            market: 市场类型
                - 'all': 全部市场
                - 'sh': 上海
                - 'sz': 深圳

        Returns:
            pd.DataFrame: ETF列表，包含以下列：
                - symbol: ETF代码
                - name: ETF名称
                - market: 所属市场
                - type: ETF类型
                - list_date: 上市日期

        Example:
            >>> adapter = AkshareDataSource()
            >>> etf_list = adapter.get_etf_list(market='sh')
            >>> print(f"上海市场ETF数量: {len(etf_list)}")
        """
        pass
```

**步骤2**: 在AKShare适配器中实现

```python
# adapters/akshare_adapter.py

class AkshareDataSource(IDataSource):
    # ... 现有方法 ...

    def get_etf_list(self, market: str = 'all') -> pd.DataFrame:
        """获取ETF列表 - AKShare实现"""
        try:
            print(f"[AKShare] 获取ETF列表: market={market}")

            # 使用akshare的fund_etf_spot_em接口
            df = ak.fund_etf_spot_em()

            if df is None or df.empty:
                return pd.DataFrame()

            # 标准化列名
            df = df.rename(columns={
                '代码': 'symbol',
                '名称': 'name',
                '最新价': 'price',
                '涨跌幅': 'change_pct',
                '成交量': 'volume',
                '成交额': 'amount'
            })

            # 添加市场字段
            df['market'] = df['symbol'].apply(
                lambda x: 'sh' if x.startswith('51') or x.startswith('50')
                else 'sz'
            )

            # 根据market参数筛选
            if market != 'all':
                df = df[df['market'] == market.lower()]

            print(f"[AKShare] 获取到 {len(df)} 只ETF")
            return df

        except Exception as e:
            print(f"[AKShare] 获取ETF列表失败: {e}")
            return pd.DataFrame()
```

**步骤3**: 在TDX适配器中实现

```python
# adapters/tdx_adapter.py

class TdxDataSource(IDataSource):
    # ... 现有方法 ...

    def get_etf_list(self, market: str = 'all') -> pd.DataFrame:
        """获取ETF列表 - TDX实现"""
        try:
            print(f"[TDX] 获取ETF列表: market={market}")

            results = []

            # TDX需要分市场获取
            markets_to_fetch = []
            if market == 'all':
                markets_to_fetch = [0, 1]  # 0=深圳, 1=上海
            elif market == 'sz':
                markets_to_fetch = [0]
            elif market == 'sh':
                markets_to_fetch = [1]

            for market_code in markets_to_fetch:
                # 获取ETF列表（类别31表示ETF）
                data = self.api.get_security_list(market=market_code, category=31)

                if data:
                    for item in data:
                        results.append({
                            'symbol': item['code'],
                            'name': item['name'],
                            'market': 'sh' if market_code == 1 else 'sz'
                        })

            df = pd.DataFrame(results)
            print(f"[TDX] 获取到 {len(df)} 只ETF")
            return df

        except Exception as e:
            print(f"[TDX] 获取ETF列表失败: {e}")
            return pd.DataFrame()
```

**步骤4**: 在其他适配器中提供简单实现

```python
# adapters/baostock_adapter.py

class BaostockDataSource(IDataSource):
    # ... 现有方法 ...

    def get_etf_list(self, market: str = 'all') -> pd.DataFrame:
        """获取ETF列表 - Baostock简单实现"""
        print(f"[Baostock] ETF列表功能暂不支持，返回空数据")
        return pd.DataFrame()
```

**步骤5**: 在DataSourceManager中添加路由

```python
# adapters/data_source_manager.py

class DataSourceManager:
    def __init__(self):
        # ... 现有初始化 ...

        # 更新优先级配置
        self._priority_config = {
            'real_time': ['tdx', 'akshare'],
            'daily': ['tdx', 'akshare'],
            'financial': ['akshare', 'tdx'],
            'etf_list': ['akshare', 'tdx']  # 新增ETF列表优先级
        }

    def get_etf_list(self, market: str = 'all', source: Optional[str] = None) -> pd.DataFrame:
        """
        获取ETF列表

        Args:
            market: 市场类型
            source: 指定数据源

        Returns:
            pd.DataFrame: ETF列表
        """
        if source:
            # 使用指定数据源
            data_source = self._sources.get(source)
            if not data_source:
                self.logger.error(f"数据源不存在: {source}")
                return pd.DataFrame()

            return data_source.get_etf_list(market)

        # 按优先级尝试多个数据源
        for source_name in self._priority_config['etf_list']:
            data_source = self._sources.get(source_name)
            if not data_source:
                continue

            self.logger.info(f"尝试从{source_name}获取ETF列表")
            df = data_source.get_etf_list(market)

            if not df.empty:
                self.logger.info(f"成功从{source_name}获取{len(df)}只ETF")
                return df
            else:
                self.logger.warning(f"{source_name}获取失败或数据为空")

        self.logger.error("所有数据源均获取失败")
        return pd.DataFrame()
```

**步骤6**: 编写测试

```python
# tests/test_etf_list.py

import pytest
from adapters.akshare_adapter import AkshareDataSource
from adapters.tdx_adapter import TdxDataSource
from adapters.data_source_manager import get_default_manager


class TestETFList:
    """测试ETF列表功能"""

    def test_akshare_get_etf_list(self):
        """测试AKShare获取ETF列表"""
        adapter = AkshareDataSource()
        df = adapter.get_etf_list(market='all')

        assert not df.empty
        assert 'symbol' in df.columns
        assert 'name' in df.columns
        assert 'market' in df.columns

    def test_tdx_get_etf_list(self):
        """测试TDX获取ETF列表"""
        adapter = TdxDataSource()
        df = adapter.get_etf_list(market='sh')

        assert not df.empty
        assert all(df['market'] == 'sh')

    def test_manager_auto_routing(self):
        """测试管理器自动路由"""
        manager = get_default_manager()
        df = manager.get_etf_list(market='all')

        assert not df.empty
        print(f"获取到 {len(df)} 只ETF")

    def test_manager_explicit_routing(self):
        """测试显式指定数据源"""
        manager = get_default_manager()

        # 显式使用AKShare
        df_ak = manager.get_etf_list(market='sh', source='akshare')
        assert not df_ak.empty

        # 显式使用TDX
        df_tdx = manager.get_etf_list(market='sh', source='tdx')
        assert not df_tdx.empty
```

**步骤7**: 更新文档

```python
# 在ADAPTER_ROUTING_GUIDE.md中添加

### 新增功能: ETF列表查询

**实现版本**: v2.2.0
**实现日期**: 2025-10-16

#### 功能说明
获取所有ETF基金的列表信息，支持按市场筛选。

#### 使用示例
```python
from adapters.data_source_manager import get_default_manager

manager = get_default_manager()

# 获取所有ETF
all_etfs = manager.get_etf_list(market='all')

# 只获取上海市场ETF
sh_etfs = manager.get_etf_list(market='sh')

# 指定使用TDX数据源
tdx_etfs = manager.get_etf_list(market='all', source='tdx')
```

#### 实现状态
| 适配器 | 实现状态 | 备注 |
|--------|---------|------|
| AKShare | ✅ 完整实现 | 使用fund_etf_spot_em |
| TDX | ✅ 完整实现 | 使用get_security_list |
| Baostock | ⚠️ 简单实现 | 返回空数据 |
| Customer | ⚠️ 简单实现 | 返回空数据 |
| Financial | ✅ 组合实现 | 自动路由 |
```

---

## 总结

### 功能扩展检查清单

- [ ] 评估是否需要加入IDataSource接口
- [ ] 编写完整的文档字符串（Args, Returns, Example）
- [ ] 实现具体功能逻辑
- [ ] 添加错误处理和日志记录
- [ ] 统一数据格式（使用ColumnMapper）
- [ ] 在DataSourceManager中添加路由支持
- [ ] 编写单元测试
- [ ] 更新系统文档
- [ ] 更新CHANGELOG.md

### 重复功能管理原则

1. **识别**: 使用功能注册表识别重复
2. **评估**: 评估重复的必要性
3. **重构**: 根据情况选择管理策略
4. **测试**: 确保重构不影响功能
5. **文档**: 更新文档说明变更

### 最佳实践

✅ **DO**:
- 遵循IDataSource接口规范
- 使用统一的列名映射
- 提供完整的文档和示例
- 编写单元测试
- 记录详细日志

❌ **DON'T**:
- 不要破坏现有接口
- 不要硬编码配置
- 不要忽略错误处理
- 不要跳过测试
- 不要遗漏文档

---

**创建时间**: 2025-10-16
**版本**: 1.0.0
**作者**: Claude Code
**项目**: MyStocks v2.1
