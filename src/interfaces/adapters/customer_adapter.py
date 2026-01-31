"""
# 功能：自定义数据源适配器，支持用户扩展数据源
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast

import pandas as pd

# 将当前目录的父目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.interfaces.data_source import IDataSource  # noqa: E402

# 导入列名映射工具
try:
    from src.utils.column_mapper import ColumnMapper

    COLUMN_MAPPER_AVAILABLE = True
    print("[Customer] 列名映射工具加载成功")
except ImportError:
    COLUMN_MAPPER_AVAILABLE = False
    print("[Customer] 列名映射工具未找到，将跳过列名标准化")


class CustomerDataSource(IDataSource):
    """Customer数据源实现（统一管理efinance和easyquotation）

    属性:
        efinance_available (bool): efinance库是否可用
        easyquotation_available (bool): easyquotation库是否可用
        use_column_mapping (bool): 是否使用列名映射标准化
    """


def __init__(self, use_column_mapping: bool = True):
    """初始化Customer数据源

    Args:
        use_column_mapping: 是否启用列名映射标准化
    """
    self.efinance_available = False
    self.easyquotation_available = False
    self.use_column_mapping = use_column_mapping and COLUMN_MAPPER_AVAILABLE

    # 尝试导入efinance
    try:
        import efinance as ef

        self.ef = ef
        self.efinance_available = True
        print("[Customer] efinance库导入成功")
    except ImportError:
        print("[Customer] efinance库未安装，相关功能不可用")
    except Exception as e:
        print(f"[Customer] efinance库导入失败: {e}")

    # 尝试导入easyquotation
    try:
        import easyquotation as eq

        self.eq = eq
        self.easyquotation_available = True
        print("[Customer] easyquotation库导入成功")
    except ImportError:
        print("[Customer] easyquotation库未安装，相关功能不可用")
    except Exception as e:
        print(f"[Customer] easyquotation库导入失败: {e}")

    print("[Customer] 数据源初始化完成:")
    print(f"  - efinance: {'可用' if self.efinance_available else '不可用'}")
    print(f"  - easyquotation: {'可用' if self.easyquotation_available else '不可用'}")
    print(f"  - 列名标准化: {'启用' if self.use_column_mapping else '禁用'}")


def _standardize_dataframe(self, df: pd.DataFrame, data_type: str = "stock_daily") -> pd.DataFrame:
    """标准化DataFrame列名"""
    if not self.use_column_mapping or df.empty:
        return df

    try:
        # 应用列名映射
        standardized_df = ColumnMapper.to_english(df)
        print(f"[Customer] 列名标准化完成，数据类型: {data_type}")
        return standardized_df
    except Exception as e:
        print(f"[Customer] 列名标准化失败: {e}")
        return df


def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取股票日线数据-Customer实现"""
    print(f"[Customer] 尝试获取股票日线数据: {symbol}")

    # efinance实现
    if self.efinance_available:
        try:
            print("[Customer] 使用efinance获取股票日线数据")
            # 使用正确的efinance API获取日线数据
            # klt=101表示日K线数据
            df = self.ef.stock.get_quote_history(symbol, beg=start_date, end=end_date, klt=101)
            if df is not None and not df.empty:
                print(f"[Customer] efinance获取到{len(df)}行数据")
                return df
        except Exception as e:
            print(f"[Customer] efinance获取股票日线数据失败: {e}")

    # easyquotation实现（如果efinance不可用）
    if self.easyquotation_available:
        try:
            print("[Customer] 使用easyquotation获取股票日线数据")
            # 注意：easyquotation主要用于实时数据，历史数据可能需要其他方式获取
            # 这里只是一个示例实现
            quotation = self.eq.use("sina")  # 使用sina源
            data = quotation.real([symbol])  # 获取实时数据
            if data:
                # 转换为DataFrame格式
                df = pd.DataFrame([data[symbol]])
                print(f"[Customer] easyquotation获取到{len(df)}行数据")
                return df
        except Exception as e:
            print(f"[Customer] easyquotation获取股票日线数据失败: {e}")

    print("[Customer] 所有方法均未能获取到股票日线数据")
    return pd.DataFrame()


def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取指数日线数据-Customer实现"""
    print(f"[Customer] 尝试获取指数日线数据: {symbol}")

    # efinance实现
    if self.efinance_available:
        try:
            print("[Customer] 使用efinance获取指数日线数据")
            # 注意：需要根据efinance的实际API调整
            df = self.ef.index.get_quote_history(symbol, start_date, end_date)
            if df is not None and not df.empty:
                print(f"[Customer] efinance获取到{len(df)}行数据")
                return df
        except Exception as e:
            print(f"[Customer] efinance获取指数日线数据失败: {e}")

    print("[Customer] 未能获取到指数日线数据")
    return pd.DataFrame()


def get_stock_basic(self, symbol: str) -> Dict[str, Any]:
    """获取股票基本信息-Customer实现"""
    print(f"[Customer] 尝试获取股票基本信息: {symbol}")

    # efinance实现
    if self.efinance_available:
        try:
            print("[Customer] 使用efinance获取股票基本信息")
            # 使用正确的efinance API获取股票基本信息
            info = self.ef.stock.get_base_info(symbol)
            if info is not None:
                print("[Customer] efinance获取到股票基本信息")
                # 将pandas.Series转换为字典
                return (
                    cast(Dict[str, Any], info.to_dict())
                    if hasattr(info, "to_dict")
                    else cast(Dict[str, Any], dict(info))
                )
        except Exception as e:
            print(f"[Customer] efinance获取股票基本信息失败: {e}")

    print("[Customer] 未能获取到股票基本信息")
    return {}


def get_index_components(self, symbol: str) -> List[str]:
    """获取指数成分股-Customer实现"""
    print(f"[Customer] 尝试获取指数成分股: {symbol}")

    # efinance实现
    if self.efinance_available:
        try:
            print("[Customer] 使用efinance获取指数成分股")
            # 注意：需要根据efinance的实际API调整
            components = self.ef.index.get_index_components(symbol)
            if components:
                print(f"[Customer] efinance获取到{len(components)}个成分股")
                return cast(List[str], components)
        except Exception as e:
            print(f"[Customer] efinance获取指数成分股失败: {e}")

    print("[Customer] 未能获取到指数成分股")
    return []


def _process_realtime_dataframe(
    self,
    df: pd.DataFrame,
    symbol: str,
    data_source: str,
    data_type: str,
) -> pd.DataFrame:
    """
    处理实时数据DataFrame，包括数据增强、列名标准化、核心列保留和数值清洗。
    """
    if df.empty:
        return df

    df = df.copy()
    df["fetch_timestamp"] = datetime.now()
    df["data_source"] = data_source
    df["data_type"] = data_type
    if data_type == "realtime_quotes" and symbol.lower() in ["sh", "sz", "hs"]:
        df["market"] = symbol.upper()

    standardized_df = self._standardize_dataframe(df, data_type)

    core_columns = [
        "symbol",
        "name",
        "pct_chg",
        "close",
        "high",
        "low",
        "open",
        "change",
        "turnover_rate",
        "volume",
        "amount",
        "total_mv",
        "circ_mv",
        "fetch_timestamp",
        "data_source",
        "data_type",
        "market",
    ]

    available_columns = [col for col in core_columns if col in standardized_df.columns]
    standardized_df = standardized_df[available_columns]

    numeric_columns = [
        "pct_chg",
        "close",
        "high",
        "low",
        "open",
        "change",
        "turnover_rate",
        "volume",
        "amount",
        "total_mv",
        "circ_mv",
    ]

    for col in numeric_columns:
        if col in standardized_df.columns:
            standardized_df[col] = standardized_df[col].replace(["-", "--", "", "nan", "NaN", "None"], None)
            standardized_df[col] = pd.to_numeric(standardized_df[col], errors="coerce")

    print(f"[Customer] 数据处理完成：{len(standardized_df)}行数据，列名已标准化，数值清洗完成")
    return standardized_df


def get_real_time_data(self, symbol: str) -> Union[pd.DataFrame, Dict[str, Any]]:
    """获取实时数据-Customer实现（重点实现efinance的沪深市场A股最新状况功能）"""
    print(f"[Customer] 尝试获取实时数据: {symbol}")

    # efinance实现 - 沪深市场A股最新状况（优先使用）
    if self.efinance_available:
        try:
            print("[Customer] 使用efinance获取沪深市场A股最新状况")

            if symbol.lower() in ["sh", "sz", "hs"]:  # 市场代码
                df = self.ef.stock.get_realtime_quotes()
                if df is not None and not df.empty:
                    return self._process_realtime_dataframe(df, symbol, "efinance", "realtime_quotes")

            else:
                # 获取特定股票的实时数据
                print(f"[Customer] 获取单只股票{symbol}的实时数据")
                try:
                    # 方法1：尝试通过实时行情获取单只股票
                    all_quotes = self.ef.stock.get_realtime_quotes()
                    if all_quotes is not None and not all_quotes.empty:
                        # 过滤出指定股票
                        stock_data = None
                        for col in ["股票代码", "代码", "symbol"]:
                            if col in all_quotes.columns:
                                stock_data = all_quotes[all_quotes[col] == symbol]
                                break

                        if stock_data is None:
                            # 尝试按第一列过滤
                            stock_data = all_quotes[all_quotes.iloc[:, 0] == symbol]

                        if stock_data is not None and not stock_data.empty:
                            print(f"[Customer] 从实时行情中找到股票{symbol}的数据")
                            return (
                                self._process_realtime_dataframe(
                                    stock_data, symbol, "efinance", "realtime_quotes"
                                ).to_dict("records")[0]
                                if not stock_data.empty
                                else {}
                            )

                    # 方法2：如果上面方法失败，尝试获取历史数据的最新点
                    print(f"[Customer] 尝试通过历史数据获取{symbol}最新行情")
                    df = self.ef.stock.get_quote_history(symbol, klt=1)  # klt=1表示1分钟K线
                    if df is not None and not df.empty:
                        latest_data = df.tail(1).copy()
                        print(f"[Customer] 获取到股票{symbol}的最新数据")
                        return (
                            self._process_realtime_dataframe(latest_data, symbol, "efinance", "stock_daily").to_dict(
                                "records"
                            )[0]
                            if not latest_data.empty
                            else {}
                        )

                except Exception as stock_error:
                    print(f"[Customer] 获取单只股票数据时出错: {stock_error}")

        except Exception as e:
            print(f"[Customer] efinance获取实时数据失败: {e}")
            print(f"[Customer] 错误详情: {str(e)}")

    # easyquotation实现（智能切换的备用方案）
    if self.easyquotation_available:
        try:
            print("[Customer] 智能切换到easyquotation获取实时数据")
            quotation = self.eq.use("sina")  # 使用sina源

            if symbol.lower() in ["sh", "sz", "hs"]:  # 市场代码
                # 获取市场整体数据
                print("[Customer] easyquotation获取市场快照数据")
                try:
                    data = quotation.market_snapshot(prefix=True)  # 获取市场快照
                    if data:
                        print("[Customer] easyquotation获取到市场快照数据")
                        # 转换为DataFrame格式以保持一致性
                        df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
                        return self._process_realtime_dataframe(df, symbol, "easyquotation", "market_snapshot")
                except Exception:
                    # 如果market_snapshot不可用，尝试其他方法
                    print("[Customer] market_snapshot不可用，尝试其他方法")

            else:
                # 获取特定股票的实时数据
                print(f"[Customer] easyquotation获取股票{symbol}实时数据")
                data = quotation.real([symbol])
                if data and symbol in data:
                    result = data[symbol].copy()
                    # 将字典转换为DataFrame以便进行列名标准化
                    df = pd.DataFrame([result])
                    standardized_result = (
                        self._process_realtime_dataframe(df, symbol, "easyquotation", "realtime_quotes").to_dict(
                            "records"
                        )[0]
                        if not df.empty
                        else result
                    )

                    print(f"[Customer] easyquotation获取到股票{symbol}的实时数据")
                    return standardized_result

        except Exception as e:
            print(f"[Customer] easyquotation获取实时数据失败: {e}")

    print("[Customer] 所有数据源均未能获取到实时数据")
    return {}


def get_market_realtime_quotes(self) -> pd.DataFrame:
    """专门获取沪深市场A股最新状况的方法"""
    print("[Customer] 专门获取沪深市场A股最新状况")
    result = self.get_real_time_data("hs")
    if isinstance(result, pd.DataFrame):
        return result
    else:
        return pd.DataFrame()


def get_market_calendar(self, start_date: str, end_date: str) -> Union[pd.DataFrame, str]:
    """获取交易日历-Customer实现"""
    print(f"[Customer] 尝试获取交易日历: {start_date} to {end_date}")

    # 使用akshare获取交易日历
    try:
        import akshare as ak

        # 获取交易日历
        calendar_df = ak.tool_trade_date_hist_sina()

        # 过滤指定日期范围
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # 确保日期列是datetime类型
        calendar_df["trade_date"] = pd.to_datetime(calendar_df["trade_date"])

        # 过滤日期范围
        filtered_df = calendar_df[(calendar_df["trade_date"] >= start_date) & (calendar_df["trade_date"] <= end_date)]

        # 重命名列以符合标准格式
        if "trade_date" in filtered_df.columns:
            filtered_df = filtered_df.rename(columns={"trade_date": "date"})

        print(f"[Customer] 成功获取交易日历: {len(filtered_df)}个交易日")
        return filtered_df
    except ImportError:
        print("[Customer] akshare库未安装，无法获取交易日历")
        return pd.DataFrame()
    except Exception as e:
        print(f"[Customer] 获取交易日历时出错: {str(e)}")
        return pd.DataFrame()


def get_financial_data(self, symbol: str, period: str = "annual") -> Union[pd.DataFrame, str]:
    """获取财务数据-Customer实现"""
    print(f"[Customer] 尝试获取财务数据: {symbol}, period: {period}")

    # efinance实现
    if self.efinance_available:
        try:
            print("[Customer] 使用efinance获取财务数据")
            # 使用efinance的get_all_company_performance方法获取财务数据
            df = self.ef.stock.get_all_company_performance()
            if df is not None and not df.empty:
                # 过滤指定股票的数据
                filtered_df = df[df["股票代码"] == symbol] if "股票代码" in df.columns else df[df["股票简称"] == symbol]
                if not filtered_df.empty:
                    print(f"[Customer] efinance获取到{len(filtered_df)}行财务数据")
                    return filtered_df
                else:
                    print(f"[Customer] efinance未找到股票{symbol}的财务数据")
        except Exception as e:
            print(f"[Customer] efinance获取财务数据失败: {e}")

    print("[Customer] 未能获取到财务数据")
    return pd.DataFrame()


def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """获取新闻数据-Customer实现"""
    print(f"[Customer] 尝试获取新闻数据: {symbol}")

    # 使用akshare获取新闻数据
    try:
        import akshare as ak

        if symbol:
            # 获取个股新闻（如果有接口的话）
            # akshare可能没有直接的个股新闻接口，这里提供通用新闻
            news_data = ak.stock_news_em(
                symbol=(
                    symbol
                    if len(symbol) == 6
                    else f"{
                    symbol.zfill(6)}"
                )
            )

            if not news_data.empty:
                # 标准化新闻数据格式
                news_list: List[Dict[str, Any]] = []
                for _, row in news_data.iterrows():
                    news_item: Dict[str, Any] = {
                        "title": row.get("title", ""),
                        "content": row.get("content", ""),
                        "publish_time": row.get("publish_time", ""),
                        "source": row.get("source", ""),
                        "url": row.get("url", ""),
                        "symbol": symbol,
                    }
                    news_list.append(news_item)

                print(f"[Customer] 成功获取{len(news_list)}条新闻数据")
                return news_list
            else:
                # 如果没有个股新闻，返回通用财经新闻
                print("[Customer] 个股新闻未找到，返回空列表")
                return cast(List[Dict[str, Any]], [])
        else:
            # 获取通用财经新闻
            # akshare可能没有通用财经新闻接口，返回空列表
            print("[Customer] 未指定股票，返回空新闻列表")
            return cast(List[Dict[str, Any]], [])
    except ImportError:
        print("[Customer] akshare库未安装，无法获取新闻数据")
        return cast(List[Dict[str, Any]], [])
    except Exception as e:
        print(f"[Customer] 获取新闻数据时出错: {str(e)}")
        return cast(List[Dict[str, Any]], [])
