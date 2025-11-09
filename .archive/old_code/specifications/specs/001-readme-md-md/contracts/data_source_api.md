# IDataSource Interface Contract

**创建人**: Claude (自动生成)
**版本**: 1.0.0
**创建日期**: 2025-10-11
**关联规格**: [../spec.md](../spec.md)

## 接口概述

`IDataSource` 是所有数据源适配器的统一抽象接口,定义了获取外部金融数据的标准方法。所有适配器必须实现此接口,确保不同数据源的调用方式和返回格式一致。

### 支持的适配器

1. **AkshareAdapter** - Akshare数据源 (主要数据源)
2. **TushareAdapter** - Tushare Pro数据源 (深度财务数据)
3. **BaostockAdapter** - Baostock数据源 (历史数据)
4. **ByapiAdapter** - Byapi数据源 (备用)
5. **CustomerAdapter** - 自定义适配器 (efinance等爬虫数据)

---

## 接口定义

### 基类定义

```python
from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd

class IDataSource(ABC):
    """数据源统一接口"""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """数据源名称"""
        pass

    @property
    @abstractmethod
    def supported_markets(self) -> List[str]:
        """支持的市场列表 (如 ['CN_A', 'HK', 'US'])"""
        pass

    @abstractmethod
    def get_kline_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        frequency: str = "daily"
    ) -> pd.DataFrame:
        """获取K线数据"""
        pass

    @abstractmethod
    def get_realtime_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """获取实时行情"""
        pass

    @abstractmethod
    def get_fundamental_data(
        self,
        symbol: str,
        report_period: str,
        data_type: str = "income"
    ) -> pd.DataFrame:
        """获取财务数据"""
        pass

    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        pass
```

---

## 方法详细说明

### 1. get_kline_data()

获取K线数据 (日线/分钟线等)。

#### 方法签名

```python
def get_kline_data(
    self,
    symbol: str,
    start_date: str,
    end_date: str,
    frequency: str = "daily"
) -> pd.DataFrame:
    """
    获取K线数据

    Args:
        symbol: 股票代码 (如 '600000.SH' 或 '600000')
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        frequency: 频率
            - "1min": 1分钟线
            - "5min": 5分钟线
            - "15min": 15分钟线
            - "30min": 30分钟线
            - "60min": 60分钟线
            - "daily": 日线 (默认)
            - "weekly": 周线
            - "monthly": 月线

    Returns:
        DataFrame with columns:
        - symbol: str - 股票代码
        - timestamp/date: datetime - 时间戳或日期 (UTC时区)
        - open: float - 开盘价
        - high: float - 最高价
        - low: float - 最低价
        - close: float - 收盘价
        - volume: int - 成交量
        - amount: float - 成交额
        [可选列]
        - turnover_rate: float - 换手率 (仅日线)
        - pe_ratio: float - 市盈率 (仅日线)
        - adj_factor: float - 复权因子 (仅日线)

    Raises:
        DataSourceError: API调用失败或数据获取失败
        ValueError: 参数无效
    """
```

#### 使用示例

```python
from adapters import AkshareAdapter

adapter = AkshareAdapter()

# 获取日线数据
daily_data = adapter.get_kline_data(
    symbol='600000.SH',
    start_date='2025-10-01',
    end_date='2025-10-11',
    frequency='daily'
)
print(daily_data)
```

---

### 2. get_realtime_quotes()

获取实时行情数据。

#### 方法签名

```python
def get_realtime_quotes(self, symbols: List[str]) -> pd.DataFrame:
    """
    获取实时行情

    Args:
        symbols: 股票代码列表 (如 ['600000.SH', '000001.SZ'])

    Returns:
        DataFrame with columns:
        - symbol: str - 股票代码
        - name: str - 股票名称
        - current_price: float - 当前价
        - change: float - 涨跌额
        - change_pct: float - 涨跌幅 (%)
        - open: float - 今开
        - high: float - 最高
        - low: float - 最低
        - pre_close: float - 昨收
        - volume: int - 成交量
        - amount: float - 成交额
        - bid_price_1: float - 买一价
        - ask_price_1: float - 卖一价
        - timestamp: datetime - 行情时间 (UTC)
        [可选列]
        - bid_volume_1: int - 买一量
        - ask_volume_1: int - 卖一量
        - turnover_rate: float - 换手率

    Raises:
        DataSourceError: 获取行情失败
    """
```

---

### 3. get_fundamental_data()

获取财务数据。

#### 方法签名

```python
def get_fundamental_data(
    self,
    symbol: str,
    report_period: str,
    data_type: str = "income"
) -> pd.DataFrame:
    """
    获取财务数据

    Args:
        symbol: 股票代码
        report_period: 报告期 (YYYY-MM-DD 或 'latest')
        data_type: 数据类型
            - "income": 利润表
            - "balance": 资产负债表
            - "cashflow": 现金流量表
            - "metrics": 财务指标

    Returns:
        DataFrame with columns (根据data_type不同):

        income (利润表):
        - symbol, report_period, revenue, net_profit, eps, gross_margin, ...

        balance (资产负债表):
        - symbol, report_period, total_assets, total_liabilities, shareholders_equity, ...

        cashflow (现金流量表):
        - symbol, report_period, operating_cash_flow, investing_cash_flow, ...

        metrics (财务指标):
        - symbol, report_period, roe, roa, debt_ratio, current_ratio, ...
    """
```

---

### 4. get_stock_list()

获取股票列表。

#### 方法签名

```python
def get_stock_list(self) -> pd.DataFrame:
    """
    获取股票列表

    Returns:
        DataFrame with columns:
        - symbol: str - 股票代码
        - name: str - 股票名称
        - exchange: str - 交易所 (SSE/SZSE)
        - list_date: date - 上市日期
        - status: str - 状态 (ACTIVE/SUSPENDED/DELISTED)
        [可选列]
        - security_type: str - 证券类型
        - listing_board: str - 上市板块
    """
```

---

## 适配器实现示例

### AkshareAdapter实现

```python
import akshare as ak

class AkshareAdapter(IDataSource):
    @property
    def source_name(self) -> str:
        return "Akshare"

    @property
    def supported_markets(self) -> List[str]:
        return ["CN_A", "HK", "US", "FUTURES", "FUND"]

    def get_kline_data(self, symbol, start_date, end_date, frequency="daily"):
        # 转换代码格式 (600000.SH -> 600000)
        code = symbol.split('.')[0]

        # 调用Akshare API
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily" if frequency == "daily" else "minute",
            start_date=start_date.replace('-', ''),
            end_date=end_date.replace('-', ''),
            adjust="qfq"
        )

        # 列名标准化
        df = df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount'
        })

        df['symbol'] = symbol
        df['date'] = pd.to_datetime(df['date'], utc=True)

        return df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'amount']]

    def get_realtime_quotes(self, symbols):
        df = ak.stock_zh_a_spot_em()
        df = df[df['代码'].isin([s.split('.')[0] for s in symbols])]

        df = df.rename(columns={
            '代码': 'code',
            '名称': 'name',
            '最新价': 'current_price',
            '涨跌幅': 'change_pct',
            '成交量': 'volume'
        })

        # 添加symbol列
        df['symbol'] = df['code'].apply(lambda x: f"{x}.SH" if x.startswith('6') else f"{x}.SZ")

        return df
```

---

## 数据源工厂

`DataSourceFactory` 实现多数据源的自动切换和降级。

```python
class DataSourceFactory:
    def __init__(self):
        self.sources = {
            'akshare': AkshareAdapter(),
            'baostock': BaostockAdapter(),
            'tushare': TushareAdapter()
        }

        # 数据类型优先级
        self.priority_map = {
            'kline_data': ['akshare', 'baostock', 'tushare'],
            'realtime_quotes': ['akshare', 'tushare'],
            'fundamental_data': ['tushare', 'akshare', 'baostock']
        }

    def get_data(self, data_type, fallback=True, **kwargs):
        priorities = self.priority_map.get(data_type, ['akshare'])

        for source_name in priorities:
            try:
                source = self.sources[source_name]
                method = getattr(source, f"get_{data_type}")
                result = method(**kwargs)
                return result
            except Exception as e:
                if not fallback:
                    raise
                print(f"❌ {source_name} 失败: {e}")

        raise DataSourceError(f"所有数据源均失败: {data_type}")
```

---

## 列名标准化

所有适配器返回的DataFrame必须使用标准列名,通过 `ColumnMapper` 实现自动转换:

```python
from utils import ColumnMapper

# 标准列名映射
mapper = ColumnMapper()

# Akshare列名 -> 标准列名
df_standardized = mapper.standardize(df_raw, source='akshare')
```

---

## 错误处理

所有适配器应捕获并转换异常为统一的 `DataSourceError`:

```python
class DataSourceError(Exception):
    """数据源异常"""
    pass

try:
    data = ak.stock_zh_a_hist(...)
except Exception as e:
    raise DataSourceError(f"Akshare API调用失败: {e}")
```

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-11
