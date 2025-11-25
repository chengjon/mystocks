"""
Tushare 数据源适配器
实现了统一数据接口，提供 Tushare 数据访问

使用前需要：
1. 安装 tushare: pip install tushare
2. 申请 Tushare Token
3. 设置环境变量: TUSHARE_TOKEN=your_token
"""

import os
import sys
from typing import Dict, List, Optional, Union

import pandas as pd

# 将当前目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interfaces.refactored_interfaces import IDataSource


class TushareDataSource(IDataSource):
    """Tushare数据源实现"""

    def __init__(self):
        # 延迟导入tushare
        try:
            import tushare as ts

            token = os.getenv("TUSHARE_TOKEN")
            if not token:
                raise ImportError("请设置环境变量 TUSHARE_TOKEN")
            ts.set_token(token)
            self.ts = ts.pro_api()
            print("Tushare数据源初始化完成")
            self.available = True
        except ImportError as e:
            print(f"警告: 无法导入tushare: {e}")
            print("请安装tushare: pip install tushare")
            self.ts = None
            self.available = False
            raise ImportError(f"Tushare不可用: {e}")

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据-Tushare实现"""
        if not self.available:
            return pd.DataFrame()

        try:
            # 使用专门的格式化函数处理股票代码
            # Tushare使用 000001.SZ 格式
            ts_symbol = self._format_symbol_for_tushare(symbol)

            df = self.ts.daily(
                ts_code=ts_symbol,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
            )

            if df is None or df.empty:
                return pd.DataFrame()

            # 统一列名
            df = df.rename(
                columns={
                    "trade_date": "date",
                    "ts_code": "symbol",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "close": "close",
                    "vol": "volume",
                    "amount": "amount",
                }
            )

            return df
        except Exception as e:
            print(f"Tushare获取股票日线数据失败: {e}")
            return pd.DataFrame()

    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数日线数据-Tushare实现"""
        if not self.available:
            return pd.DataFrame()

        try:
            # Tushare指数代码处理
            ts_symbol = self._format_index_for_tushare(symbol)

            df = self.ts.index_daily(
                ts_code=ts_symbol,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
            )

            if df is None or df.empty:
                return pd.DataFrame()

            # 统一列名
            df = df.rename(
                columns={
                    "trade_date": "date",
                    "ts_code": "symbol",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "close": "close",
                    "vol": "volume",
                    "amount": "amount",
                }
            )

            return df
        except Exception as e:
            print(f"Tushare获取指数日线数据失败: {e}")
            return pd.DataFrame()

    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息-Tushare实现"""
        if not self.available:
            return {}

        try:
            ts_symbol = self._format_symbol_for_tushare(symbol)
            df = self.ts.stock_basic(ts_code=ts_symbol)

            if df is None or df.empty:
                return {}

            # 转换为字典
            return dict(df.iloc[0].to_dict())
        except Exception as e:
            print(f"Tushare获取股票基本信息失败: {e}")
            return {}

    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股-Tushare实现"""
        if not self.available:
            return []

        try:
            ts_symbol = self._format_index_for_tushare(symbol)
            df = self.ts.index_weight(index_code=ts_symbol)

            if df is None or df.empty:
                return []

            return list(df["con_code"].tolist())
        except Exception as e:
            print(f"Tushare获取指数成分股失败: {e}")
            return []

    def get_real_time_data(self, symbol: str) -> Union[Dict, str]:
        """获取实时数据-Tushare实现"""
        # Tushare主要提供历史数据，实时数据功能有限
        return {"error": "Tushare主要提供历史数据，请使用其他数据源获取实时数据"}

    def get_market_calendar(self, start_date: str, end_date: str) -> Union[pd.DataFrame, str]:
        """获取交易日历-Tushare实现"""
        if not self.available:
            return pd.DataFrame()

        try:
            df = self.ts.trade_cal(
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
            )
            return df
        except Exception as e:
            print(f"Tushare获取交易日历失败: {e}")
            return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual") -> Union[pd.DataFrame, str]:
        """获取财务数据-Tushare实现"""
        if not self.available:
            return pd.DataFrame()

        try:
            ts_symbol = self._format_symbol_for_tushare(symbol)
            if period == "annual":
                df = self.ts.income(ts_code=ts_symbol, period="A")
            else:
                df = self.ts.income(ts_code=ts_symbol, period="Q")
            return df
        except Exception as e:
            print(f"Tushare获取财务数据失败: {e}")
            return pd.DataFrame()

    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> Union[List[Dict], str]:
        """获取新闻数据-Tushare实现"""
        # Tushare的新闻数据功能有限
        return "Tushare新闻数据功能有限，请使用其他数据源"

    def _format_symbol_for_tushare(self, symbol: str) -> str:
        """格式化股票代码为Tushare格式"""
        # 简化处理，实际应该使用symbol_utils的逻辑
        symbol = symbol.replace(".", "").replace("sh", "").replace("sz", "")
        if symbol.startswith("6"):
            return f"{symbol}.SH"
        elif symbol.startswith("0") or symbol.startswith("3"):
            return f"{symbol}.SZ"
        return symbol

    def _format_index_for_tushare(self, symbol: str) -> str:
        """格式化指数代码为Tushare格式"""
        # 简化处理
        symbol = symbol.replace(".", "").replace("sh", "").replace("sz", "")
        if symbol.startswith("000"):
            return f"{symbol}.SH"
        elif symbol.startswith("399"):
            return f"{symbol}.SZ"
        return symbol
