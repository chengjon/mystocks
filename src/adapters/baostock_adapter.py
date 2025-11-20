"""
# 功能：BaoStock数据源适配器，提供历史行情和财务数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import pandas as pd
from typing import Dict, List
import baostock as bs
import datetime
import sys
import os

# 将当前目录的父目录的父目录添加到模块搜索路径中
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from mystocks.interfaces.data_source import IDataSource
from mystocks.utils.symbol_utils import (
    format_stock_code_for_source,
    format_index_code_for_source,
)
from mystocks.utils.column_mapper import ColumnMapper
from mystocks.utils.date_utils import normalize_date


class BaostockDataSource(IDataSource):
    """Baostock数据源实现"""

    def __init__(self):
        # 延迟导入baostock
        try:
            import baostock as bs

            self.bs = bs
            # Baostock需要登录
            self.lg = bs.login()
            if self.lg.error_code != "0":
                print(f"Baostock登录失败: {self.lg.error_msg}")
                raise ImportError(f"Baostock登录失败: {self.lg.error_msg}")
            else:
                print("Baostock登录成功")
                self.available = True
        except ImportError as e:
            print(f"警告: 无法导入baostock: {e}")
            print("请安装baostock: pip install baostock")
            self.bs = None
            self.available = False
            raise ImportError(f"Baostock不可用: {e}")

    def __del__(self) -> None:
        # 退出时自动登出
        if hasattr(self, "bs"):
            self.bs.logout()

    def get_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """获取股票日线数据-Baostock实现"""
        try:
            # 使用专门的格式化函数处理股票代码
            symbol = format_stock_code_for_source(symbol, "baostock")
            print(f"Baostock尝试获取股票数据: {symbol}")
            # 获取A股股票日线数据
            rs = self.bs.query_history_k_data_plus(
                symbol,
                "date,code,open,high,low,close,volume,amount,turn,pctChg",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3",
            )

            if rs.error_code != "0":
                print(f"Baostock查询错误: {rs.error_msg}")
                return pd.DataFrame()

            # 转换为DataFrame
            data_list = []
            while (rs.error_code == "0") & rs.next():
                data_list.append(rs.get_row_data())

            df = pd.DataFrame(data_list, columns=rs.fields)

            # 转换数据类型
            numeric_columns = [
                "open",
                "high",
                "low",
                "close",
                "volume",
                "amount",
                "turn",
                "pctChg",
            ]
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # 使用统一列名映射器标准化列名
            df = ColumnMapper.to_english(df)

            return df
        except Exception as e:
            print(f"Baostock获取股票日线数据失败: {e}")
            return pd.DataFrame()

    def get_index_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """获取指数日线数据-Baostock实现"""
        try:
            # 使用专门的格式化函数处理指数代码
            symbol = format_index_code_for_source(symbol, "baostock")
            print(f"Baostock尝试获取指数数据: {symbol}")

            # 获取指数日线数据
            rs = self.bs.query_history_k_data_plus(
                symbol,
                "date,code,open,high,low,close,volume,amount,pctChg",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
            )

            if rs.error_code != "0":
                print(f"Baostock查询错误: {rs.error_msg}")
                return pd.DataFrame()

            # 转换为DataFrame
            data_list = []
            while (rs.error_code == "0") & rs.next():
                data_list.append(rs.get_row_data())

            df = pd.DataFrame(data_list, columns=rs.fields)

            # 转换数据类型
            numeric_columns = [
                "open",
                "high",
                "low",
                "close",
                "volume",
                "amount",
                "pctChg",
            ]
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # 统一列名
            df = df.rename(
                columns={
                    "date": "date",
                    "code": "symbol",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "close": "close",
                    "volume": "volume",
                    "amount": "amount",
                    "pctChg": "pct_chg",
                }
            )

            return df
        except Exception as e:
            print(f"Baostock获取指数日线数据失败: {e}")
            return pd.DataFrame()

    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息-Baostock实现"""
        try:
            # 使用专门的格式化函数处理股票代码
            symbol = format_stock_code_for_source(symbol, "baostock")

            # 获取股票基本信息
            rs = self.bs.query_stock_basic(code=symbol)
            if rs.error_code != "0":
                print(f"Baostock查询错误: {rs.error_msg}")
                return {}

            # 转换为字典
            data_list = []
            while (rs.error_code == "0") & rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return {}

            # 将数据转换为字典
            fields = rs.fields
            values = data_list[0]
            info_dict = dict(zip(fields, values))

            return info_dict
        except Exception as e:
            print(f"Baostock获取股票基本信息失败: {e}")
            return {}

    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股-Baostock实现"""
        try:
            # 获取指数成分股
            rs = self.bs.query_index_weight(
                code=symbol, start_date=normalize_date(datetime.datetime.now())
            )
            if rs.error_code != "0":
                print(f"Baostock查询错误: {rs.error_msg}")
                return []

            # 转换为列表
            data_list = []
            while (rs.error_code == "0") & rs.next():
                data_list.append(rs.get_row_data())

            # 提取股票代码
            codes = [item[1] for item in data_list] if data_list else []

            return codes
        except Exception as e:
            print(f"Baostock获取指数成分股失败: {e}")
            return []

    def get_real_time_data(self, symbol: str):
        """获取实时数据-Baostock实现"""
        try:
            # 使用stock_zh_a_spot接口获取股票实时数据
            rs = self.bs.query_all_stock(day=normalize_date(datetime.datetime.now()))
            if rs.error_code != "0":
                print(f"Baostock查询错误: {rs.error_msg}")
                return {}

            # 转换为DataFrame
            data_list = []
            while (rs.error_code == "0") & rs.next():
                data_list.append(rs.get_row_data())

            df = pd.DataFrame(data_list, columns=rs.fields)

            # 筛选指定股票
            filtered_df = df[df["code"] == symbol]
            if filtered_df.empty:
                print(f"未能找到股票 {symbol} 的实时数据")
                return {}

            # 转换为字典
            return filtered_df.iloc[0].to_dict()
        except Exception as e:
            print(f"Baostock获取实时数据失败: {e}")
            return {}

    def get_market_calendar(self, start_date: str, end_date: str):
        """获取交易日历-Baostock实现"""
        try:
            # Baostock没有直接提供交易日历接口，返回空DataFrame
            print("Baostock暂不支持交易日历查询")
            return pd.DataFrame()
        except Exception as e:
            print(f"Baostock获取交易日历失败: {e}")
            return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual"):
        """获取财务数据-Baostock实现"""
        try:
            # 使用query_stock_basic获取基本信息（作为财务数据的替代）
            rs = self.bs.query_stock_basic(code=symbol)
            if rs.error_code != "0":
                print(f"Baostock查询错误: {rs.error_msg}")
                return pd.DataFrame()

            # 转换为DataFrame
            data_list = []
            while (rs.error_code == "0") & rs.next():
                data_list.append(rs.get_row_data())

            df = pd.DataFrame(data_list, columns=rs.fields)
            return df
        except Exception as e:
            print(f"Baostock获取财务数据失败: {e}")
            return pd.DataFrame()

    def get_news_data(self, symbol: str = None, limit: int = 10):
        """获取新闻数据-Baostock实现"""
        try:
            # Baostock没有直接提供新闻数据接口，返回空列表
            print("Baostock暂不支持新闻数据查询")
            return []
        except Exception as e:
            print(f"Baostock获取新闻数据失败: {e}")
            return []
