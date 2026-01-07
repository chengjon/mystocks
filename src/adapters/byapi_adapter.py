"""
# 功能：Byapi (biyingapi.com) 数据源适配器，提供A股实时行情、K线和财务数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2024-08-29
# 版本：2.1.0
# 依赖：requests, pandas (详见requirements.txt)
# 注意事项：
#   - API License: 04C01BF1-7F2F-41A3-B470-1F81F14B1FC8
#   - 内置频率控制: 300请求/分钟 (0.2s间隔)
#   - 支持A股市场，实时行情+历史K线+财务报表+涨跌停股池
#   - 辅助文件位于adapters/byapi/目录 (API文档和映射表)
# 版权：MyStocks Project © 2025
"""

import time
import requests
import pandas as pd
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class DataSourceError(Exception):
    """数据源异常"""

    pass


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
        """支持的市场列表"""
        pass

    @abstractmethod
    def get_kline_data(self, symbol: str, start_date: str, end_date: str, frequency: str = "daily") -> pd.DataFrame:
        """获取K线数据"""
        pass

    @abstractmethod
    def get_realtime_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """获取实时行情"""
        pass

    @abstractmethod
    def get_fundamental_data(self, symbol: str, report_period: str, data_type: str = "income") -> pd.DataFrame:
        """获取财务数据"""
        pass

    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        pass


class ByapiAdapter(IDataSource):
    """
    Byapi (biyingapi.com) 数据源适配器

    特点:
    - 支持A股市场全量数据
    - 提供实时行情和历史K线
    - 包含完整的财务报表数据
    - 内置频率控制 (300请求/分钟)

    Args:
        licence: biyingapi.com API许可证
        base_url: API基础URL (默认: http://api.biyingapi.com)
        min_interval: 最小请求间隔秒数 (默认: 0.2s, 对应300次/分钟)
    """

    def __init__(
        self,
        licence: str = "04C01BF1-7F2F-41A3-B470-1F81F14B1FC8",
        base_url: str = "http://api.biyingapi.com",
        min_interval: float = 0.2,
    ):
        self.licence = licence
        self.base_url = base_url
        self.min_interval = min_interval
        self.last_request_time = 0.0

        # 创建session对象
        self.session = requests.Session()
        # 配置连接池
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=5,
            pool_maxsize=50,
            max_retries=3,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 频率映射: IDataSource标准 -> byapi参数
        self.frequency_map = {
            "1min": "5",  # byapi最小5分钟
            "5min": "5",
            "15min": "15",
            "30min": "30",
            "60min": "60",
            "daily": "d",
            "weekly": "w",
            "monthly": "m",
            "yearly": "y",
        }

        # 财务数据类型映射
        self.fundamental_type_map = {
            "income": "income",  # 利润表
            "balance": "balance",  # 资产负债表
            "cashflow": "cashflow",  # 现金流量表
            "metrics": "pershareindex",  # 财务指标
        }

    @property
    def source_name(self) -> str:
        return "Byapi"

    @property
    def supported_markets(self) -> List[str]:
        return ["CN_A"]  # 仅支持A股市场

    def _standardize_symbol(self, symbol: str) -> str:
        """
        标准化股票代码格式

        Args:
            symbol: 原始代码 (如 '600000.SH' 或 '600000')

        Returns:
            byapi格式代码 (如 '600000.SH')
        """
        if "." in symbol:
            return symbol

        # 根据代码前缀判断交易所
        if symbol.startswith("6"):
            return f"{symbol}.SH"
        elif symbol.startswith(("0", "3")):
            return f"{symbol}.SZ"
        else:
            raise ValueError(f"无法识别的股票代码: {symbol}")

    def _rate_limit(self):
        """控制API请求频率"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        self.last_request_time = time.time()

    def _request(self, url: str, timeout: int = 30) -> Dict[Any, Any]:
        """
        发送HTTP请求并返回JSON数据

        Args:
            url: 完整的API URL
            timeout: 超时时间(秒)

        Returns:
            解析后的JSON对象

        Raises:
            DataSourceError: API请求失败
        """
        self._rate_limit()

        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise DataSourceError(f"Byapi API请求失败: {url}\n错误: {e}")
        except ValueError as e:
            raise DataSourceError(f"Byapi返回数据解析失败: {e}")

    def get_stock_list(self) -> pd.DataFrame:
        """
        获取股票列表

        API: http://api.biyingapi.com/hslt/list/licence

        Returns:
            DataFrame包含:
            - symbol: 股票代码 (如 '600000.SH')
            - name: 股票名称
            - exchange: 交易所 (SSE/SZSE)
            - list_date: 上市日期
            - status: 状态 (固定为 'ACTIVE')
        """
        url = f"{self.base_url}/hslt/list/{self.licence}"

        try:
            data = self._request(url)

            if not isinstance(data, list) or len(data) == 0:
                raise DataSourceError("股票列表数据为空")

            df = pd.DataFrame(data)

            # 列名映射: byapi -> 标准
            column_map = {
                "dm": "symbol",  # byapi已经返回标准格式如 '000001.SZ'
                "mc": "name",
                "jys": "exchange_code",
            }

            df = df.rename(columns=column_map)

            # 标准化交易所名称 (jys字段: 'SH' 或 'SZ')
            df["exchange"] = df["exchange_code"].map({"SH": "SSE", "SZ": "SZSE"}).fillna("UNKNOWN")

            # byapi不提供上市日期,设置为None
            df["list_date"] = pd.NaT
            df["status"] = "ACTIVE"

            return df[["symbol", "name", "exchange", "list_date", "status"]]

        except Exception as e:
            raise DataSourceError(f"获取股票列表失败: {e}")

    def get_kline_data(self, symbol: str, start_date: str, end_date: str, frequency: str = "daily") -> pd.DataFrame:
        """
        获取K线数据

        API: https://api.biyingapi.com/hsstock/history/{symbol}/{level}/n/{licence}?st={start}&et={end}

        Args:
            symbol: 股票代码 (如 '600000.SH')
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: 频率 (daily/5min/15min/30min/60min/weekly/monthly)

        Returns:
            DataFrame包含:
            - symbol, timestamp/date, open, high, low, close, volume, amount
        """
        std_symbol = self._standardize_symbol(symbol)

        # 获取byapi频率参数
        level = self.frequency_map.get(frequency)
        if not level:
            raise ValueError(f"不支持的频率: {frequency}. 支持: {list(self.frequency_map.keys())}")

        # 构建API URL (使用https)
        url = (
            f"https://api.biyingapi.com/hsstock/history/{std_symbol}/{level}/n/{self.licence}"
            f"?st={start_date.replace('-', '')}&et={end_date.replace('-', '')}"
        )

        try:
            data = self._request(url)

            if not isinstance(data, list) or len(data) == 0:
                return pd.DataFrame(
                    columns=[
                        "symbol",
                        "date",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "amount",
                    ]
                )

            df = pd.DataFrame(data)

            # 列名映射: byapi -> 标准
            column_map = {
                "t": "timestamp",
                "o": "open",
                "h": "high",
                "l": "low",
                "c": "close",
                "v": "volume",
                "a": "amount",
            }

            df = df.rename(columns=column_map)

            # 添加symbol列
            df["symbol"] = std_symbol

            # 时间戳转换为UTC datetime
            if frequency == "daily":
                df["date"] = pd.to_datetime(df["timestamp"], utc=True)
                df = df.drop("timestamp", axis=1)
                return df[
                    [
                        "symbol",
                        "date",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "amount",
                    ]
                ]
            else:
                df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
                return df[
                    [
                        "symbol",
                        "timestamp",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "amount",
                    ]
                ]

        except Exception as e:
            raise DataSourceError(f"获取K线数据失败 [{symbol}]: {e}")

    def get_realtime_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """
        获取实时行情

        API (旧): http://api.biyingapi.com/hsrl/ssjy/{code}/{licence}
        API (新): https://api.biyingapi.com/hsstock/real/time/{symbol}/{licence}

        优先使用旧接口(更稳定),新接口作为备选

        Args:
            symbols: 股票代码列表 (如 ['600000.SH', '000001.SZ'])

        Returns:
            DataFrame包含:
            - symbol, name, current_price, change, change_pct, open, high, low,
              pre_close, volume, amount, timestamp
        """
        result_list = []

        for symbol in symbols:
            std_symbol = self._standardize_symbol(symbol)
            code = std_symbol.split(".")[0]  # 提取纯代码

            # 优先使用旧接口
            url = f"{self.base_url}/hsrl/ssjy/{code}/{self.licence}"

            try:
                data = self._request(url)

                # byapi实时接口返回单个对象,不是列表
                if not isinstance(data, dict):
                    continue

                record = data

                # 构建标准格式
                quote = {
                    "symbol": std_symbol,
                    "name": "",  # byapi实时接口不提供股票名称
                    "current_price": record.get("p", 0.0),
                    "open": record.get("o", 0.0),
                    "high": record.get("h", 0.0),
                    "low": record.get("l", 0.0),
                    "pre_close": record.get("yc", 0.0),
                    "volume": int(record.get("v", 0)),
                    "amount": record.get("cje", 0.0),
                    "change": record.get("ud", 0.0),
                    "change_pct": record.get("pc", 0.0),
                    "bid_price_1": 0.0,  # byapi需单独调用五档盘口接口
                    "ask_price_1": 0.0,
                    "timestamp": pd.to_datetime(record.get("t", datetime.now().isoformat()), utc=True),
                    "turnover_rate": record.get("hs", 0.0),
                }

                result_list.append(quote)

            except DataSourceError:
                # 单个股票失败时跳过,继续处理其他股票
                continue

        if not result_list:
            raise DataSourceError("获取实时行情失败: 所有股票均无数据")

        return pd.DataFrame(result_list)

    def get_fundamental_data(self, symbol: str, report_period: str, data_type: str = "income") -> pd.DataFrame:
        """
        获取财务数据

        API: http://api.biyingapi.com/hsstock/financial/{type}/{symbol}/{licence}?st={start}&et={end}

        Args:
            symbol: 股票代码 (如 '600000.SH')
            report_period: 报告期 (YYYY-MM-DD 或 'latest' 获取最新一期)
            data_type: 数据类型
                - "income": 利润表
                - "balance": 资产负债表
                - "cashflow": 现金流量表
                - "metrics": 财务指标

        Returns:
            DataFrame包含财务数据 (列名根据data_type不同而不同)
        """
        std_symbol = self._standardize_symbol(symbol)

        # 获取byapi财务类型
        api_type = self.fundamental_type_map.get(data_type)
        if not api_type:
            raise ValueError(f"不支持的财务数据类型: {data_type}. 支持: {list(self.fundamental_type_map.keys())}")

        # 构建URL
        if report_period == "latest":
            # 获取最近1条记录
            url = f"http://api.biyingapi.com/hsstock/financial/{api_type}/{std_symbol}/{self.licence}?lt=1"
        else:
            # 获取指定日期前后的数据
            period_date = report_period.replace("-", "")
            url = (
                f"http://api.biyingapi.com/hsstock/financial/{api_type}/{std_symbol}/{self.licence}"
                f"?st={period_date}&et={period_date}"
            )

        try:
            data = self._request(url)

            if not isinstance(data, list) or len(data) == 0:
                return pd.DataFrame()

            df = pd.DataFrame(data)

            # 添加symbol列
            df["symbol"] = std_symbol

            # 标准化日期列名
            if "jzrq" in df.columns:
                df["report_period"] = pd.to_datetime(df["jzrq"])

            return df

        except Exception as e:
            raise DataSourceError(f"获取财务数据失败 [{symbol}, {data_type}]: {e}")

    def get_limit_up_stocks(self, trade_date: str) -> pd.DataFrame:
        """
        获取涨停股池 (byapi特有功能)

        API: http://api.biyingapi.com/hslt/ztgc/{date}/{licence}

        Args:
            trade_date: 交易日期 (YYYY-MM-DD)

        Returns:
            DataFrame包含涨停股票列表
        """
        url = f"{self.base_url}/hslt/ztgc/{trade_date.replace('-', '')}/{self.licence}"

        try:
            data = self._request(url)

            if not isinstance(data, list):
                return pd.DataFrame()

            df = pd.DataFrame(data)
            df["trade_date"] = trade_date

            return df

        except Exception as e:
            raise DataSourceError(f"获取涨停股池失败 [{trade_date}]: {e}")

    def get_limit_down_stocks(self, trade_date: str) -> pd.DataFrame:
        """
        获取跌停股池 (byapi特有功能)

        API: http://api.biyingapi.com/hslt/dtgc/{date}/{licence}

        Args:
            trade_date: 交易日期 (YYYY-MM-DD)

        Returns:
            DataFrame包含跌停股票列表
        """
        url = f"{self.base_url}/hslt/dtgc/{trade_date.replace('-', '')}/{self.licence}"

        try:
            data = self._request(url)

            if not isinstance(data, list):
                return pd.DataFrame()

            df = pd.DataFrame(data)
            df["trade_date"] = trade_date

            return df

        except Exception as e:
            raise DataSourceError(f"获取跌停股池失败 [{trade_date}]: {e}")

    def close(self):
        """关闭session"""
        if self.session is not None:
            self.session.close()

    def __del__(self):
        """析构函数"""
        self.close()


# 向后兼容: 别名
ByapiDataSource = ByapiAdapter


if __name__ == "__main__":
    """使用示例"""

    # 初始化适配器
    adapter = ByapiAdapter(licence="04C01BF1-7F2F-41A3-B470-1F81F14B1FC8")

    print(f"数据源: {adapter.source_name}")
    print(f"支持市场: {adapter.supported_markets}")
    print("\n" + "=" * 60 + "\n")

    # 1. 获取股票列表
    print("【测试1】获取股票列表 (前10条):")
    try:
        stocks = adapter.get_stock_list()
        print(stocks.head(10))
        print(f"总计: {len(stocks)} 只股票\n")
    except DataSourceError as e:
        print(f"错误: {e}\n")

    # 2. 获取日线数据
    print("【测试2】获取日线数据 (平安银行 000001.SZ):")
    try:
        kline = adapter.get_kline_data(
            symbol="000001.SZ",
            start_date="2025-10-01",
            end_date="2025-10-11",
            frequency="daily",
        )
        print(kline)
        print()
    except DataSourceError as e:
        print(f"错误: {e}\n")

    # 3. 获取实时行情
    print("【测试3】获取实时行情 (平安银行、浦发银行):")
    try:
        quotes = adapter.get_realtime_quotes(["000001.SZ", "600000.SH"])
        print(quotes[["symbol", "current_price", "change_pct", "volume", "amount"]])
        print()
    except DataSourceError as e:
        print(f"错误: {e}\n")

    # 4. 获取财务数据
    print("【测试4】获取最新利润表 (平安银行):")
    try:
        financial = adapter.get_fundamental_data(symbol="000001.SZ", report_period="latest", data_type="income")
        if not financial.empty:
            print(f"报告期: {financial.iloc[0].get('jzrq', 'N/A')}")
            print(f"营业收入: {financial.iloc[0].get('yysr', 'N/A')}")
            print(f"净利润: {financial.iloc[0].get('jlr', 'N/A')}")
        else:
            print("暂无财务数据")
        print()
    except DataSourceError as e:
        print(f"错误: {e}\n")

    # 5. 获取涨停股池
    print("【测试5】获取涨停股池 (2025-10-10):")
    try:
        limit_up = adapter.get_limit_up_stocks("2025-10-10")
        print(f"涨停股票数: {len(limit_up)}")
        if not limit_up.empty:
            print(limit_up.head())
        print()
    except DataSourceError as e:
        print(f"错误: {e}\n")

    print("=" * 60)
    print("所有测试完成!")
