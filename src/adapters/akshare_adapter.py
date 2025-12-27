"""
# 功能：AkShare数据源适配器，提供A股行情和基本面数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import pandas as pd
from typing import Dict, List, Optional, Any
import akshare as ak
import sys
import os
import datetime
from functools import wraps

# 常量定义
MAX_RETRIES = 3
RETRY_DELAY = 1
REQUEST_TIMEOUT = 10

# 将当前目录的父目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.error_handler import retry_on_failure  # noqa: E402
from src.interfaces.data_source import IDataSource  # noqa: E402
from src.utils.date_utils import normalize_date  # noqa: E402
from src.utils.symbol_utils import (  # noqa: E402
    format_stock_code_for_source,
    format_index_code_for_source,
)
from src.utils.column_mapper import ColumnMapper  # noqa: E402

# 统一日志配置
import logging

# 获取或创建logger
logger = logging.getLogger(__name__)

# 确保日志配置已设置
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class AkshareDataSource(IDataSource):
    """Akshare数据源实现

    属性:
        api_timeout (int): API请求超时时间(秒)
        max_retries (int): 最大重试次数
    """

    def __init__(self, api_timeout: int = REQUEST_TIMEOUT, max_retries: int = MAX_RETRIES):
        """初始化Akshare数据源

        Args:
            api_timeout: API请求超时时间(秒)
            max_retries: 最大重试次数
        """
        self.api_timeout = api_timeout
        self.max_retries = max_retries
        logger.info(f"[Akshare] 数据源初始化完成 (超时: {api_timeout}s, 重试: {max_retries}次)")

    def _retry_api_call(self, func):
        """API调用重试装饰器 - 使用统一错误处理"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 使用统一错误处理的重试机制
            retry_decorator = retry_on_failure(
                max_retries=self.max_retries,
                delay=RETRY_DELAY,
                backoff=1.0,
                exceptions=(Exception,),
                context=f"Akshare API调用: {func.__name__}",
            )
            return retry_decorator(func)(*args, **kwargs)

        return wrapper

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据-Akshare实现"""
        try:
            # 处理股票代码格式 - 使用专门的格式化函数
            stock_code = format_stock_code_for_source(symbol, "akshare")

            # 处理日期格式
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)

            logger.info(
                str(f"Akshare尝试获取股票日线数据: 代码={stock_code}, 开始日期={start_date}, 结束日期={end_date}")
            )

            # 尝试多种API获取股票数据
            df = None

            # 方法1: stock_zh_a_hist (主要API)
            try:
                # 根据文档要求，日期格式应为YYYYMMDD
                start_date_fmt = start_date.replace("-", "")
                end_date_fmt = end_date.replace("-", "")

                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date=start_date_fmt,
                    end_date=end_date_fmt,
                    adjust="qfq",  # 前复权
                    timeout=self.api_timeout,
                )
                logger.info(
                    str(
                        f"主要API调用成功，参数: symbol={stock_code}, start_date={start_date_fmt}, end_date={end_date_fmt}"
                    )
                )
            except Exception as e:
                logger.error(f"主要API调用失败: {e}")
                df = None

            # 方法2: stock_zh_a_spot (备用API)
            if df is None or df.empty:
                try:
                    logger.info(r"尝试备用API(stock_zh_a_spot)")
                    spot_df = ak.stock_zh_a_spot()
                    if spot_df is not None and not spot_df.empty:
                        # 筛选指定股票代码
                        spot_df = spot_df[spot_df["代码"] == stock_code]
                        if not spot_df.empty:
                            # 转换为日线格式
                            df = pd.DataFrame(
                                {
                                    "date": [normalize_date(datetime.datetime.now())],
                                    "open": [spot_df.iloc[0]["今开"]],
                                    "close": [spot_df.iloc[0]["最新价"]],
                                    "high": [spot_df.iloc[0]["最高"]],
                                    "low": [spot_df.iloc[0]["最低"]],
                                    "volume": [spot_df.iloc[0]["成交量"]],
                                    "amount": [spot_df.iloc[0]["成交额"]],
                                }
                            )
                except Exception as e:
                    logger.error(f"备用API调用失败: {e}")

            if df is None or df.empty:
                logger.info(r"Akshare返回的数据为空")
                return pd.DataFrame()

            logger.info(f"Akshare获取到原始数据: {len(df)}行, 列名={df.columns.tolist()}")

            # 使用统一列名映射器标准化列名
            df = ColumnMapper.to_english(df)

            return df
        except Exception as e:
            logger.error(f"Akshare获取股票日线数据失败: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数日线数据-Akshare实现
        使用优先级：
        1. 新浪接口(stock_zh_index_daily)
        2. 东方财富接口(stock_zh_index_daily_em)
        3. 通用接口(index_zh_a_hist)
        """
        try:
            # 处理日期格式
            start_date = normalize_date(start_date)
            end_date = normalize_date(end_date)

            logger.info(f"尝试获取指数数据: {symbol}")

            # 使用专门的格式化函数处理指数代码
            index_code = format_index_code_for_source(symbol, "akshare")
            logger.info(f"处理指数: {index_code}")

            # 方法1: 新浪接口 (stock_zh_index_daily)
            try:
                logger.info(r"尝试新浪接口(stock_zh_index_daily)")
                df = ak.stock_zh_index_daily(symbol=index_code)

                if df is not None and not df.empty:
                    # 筛选日期范围
                    df["date"] = pd.to_datetime(df["date"])
                    mask = (df["date"] >= pd.to_datetime(normalize_date(start_date))) & (
                        df["date"] <= pd.to_datetime(normalize_date(end_date))
                    )
                    df = df[mask]

                    if not df.empty:
                        logger.info(f"新浪接口获取到{len(df)}行数据")
                        return self._process_index_data(df)
            except Exception as e:
                logger.error(f"新浪接口调用失败: {e}")

            # 方法2: 东方财富接口 (stock_zh_index_daily_em)
            try:
                logger.info(r"尝试东方财富接口(stock_zh_index_daily_em)")
                df = ak.stock_zh_index_daily_em(symbol=index_code)

                if df is not None and not df.empty:
                    # 筛选日期范围
                    df["date"] = pd.to_datetime(df["date"])
                    mask = (df["date"] >= pd.to_datetime(normalize_date(start_date))) & (
                        df["date"] <= pd.to_datetime(normalize_date(end_date))
                    )
                    df = df[mask]

                    if not df.empty:
                        logger.info(f"东方财富接口获取到{len(df)}行数据")
                        return self._process_index_data(df)
            except Exception as e:
                logger.error(f"东方财富接口调用失败: {e}")

            # 方法3: 通用接口 (index_zh_a_hist)
            try:
                logger.info(r"尝试通用接口(index_zh_a_hist)")
                # 提取纯数字代码
                pure_code = "".join(c for c in index_code if c.isdigit())
                start_date_fmt = start_date.replace("-", "")
                end_date_fmt = end_date.replace("-", "")

                df = ak.index_zh_a_hist(
                    symbol=pure_code,
                    period="daily",
                    start_date=start_date_fmt,
                    end_date=end_date_fmt,
                )

                if df is not None and not df.empty:
                    logger.info(f"通用接口获取到{len(df)}行数据")
                    return self._process_index_data(df)
            except Exception as e:
                logger.error(f"通用接口调用失败: {e}")

            logger.info(f"所有接口均未能获取到指数 {index_code} 的数据")
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Akshare获取指数日线数据失败: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def _process_index_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理指数数据统一格式"""
        # 使用统一列名映射器标准化列名
        return ColumnMapper.to_english(df)

    def get_stock_basic(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息-Akshare实现"""
        try:
            # 处理股票代码格式 - 使用专门的格式化函数
            stock_code = format_stock_code_for_source(symbol, "akshare")

            # 使用stock_individual_info_em接口获取股票基本信息
            # 参考文档: https://akshare.akfamily.xyz/data/stock/stock.html#id56
            df = ak.stock_individual_info_em(symbol=stock_code)

            if df is None or df.empty:
                logger.info(f"未能获取到股票 {stock_code} 的基本信息")
                return {}

            # 转换为字典
            info_dict = {}
            for _, row in df.iterrows():
                info_dict[row["item"]] = row["value"]

            return info_dict
        except Exception as e:
            logger.error(f"Akshare获取股票基本信息失败: {e}")
            return {}

    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股-Akshare实现"""
        try:
            # 使用index_stock_cons接口获取指数成分股
            # 参考文档: https://akshare.akfamily.xyz/data/index/index.html#id4
            df = ak.index_stock_cons(symbol=symbol)

            if df is None or df.empty:
                logger.info(f"未能获取到指数 {symbol} 的成分股")
                return []

            # 提取股票代码
            if "品种代码" in df.columns:
                return df["品种代码"].tolist()
            elif "成分券代码" in df.columns:
                return df["成分券代码"].tolist()
            else:
                logger.info(f"无法识别的成分股列名: {df.columns.tolist()}")
                return []
        except Exception as e:
            logger.error(f"Akshare获取指数成分股失败: {e}")
            return []

    def get_real_time_data(self, symbol: str) -> Dict[str, Any]:
        """获取实时数据-Akshare实现"""
        try:
            # 使用stock_zh_a_spot接口获取股票实时数据
            df = ak.stock_zh_a_spot()

            if df is None or df.empty:
                logger.info(f"未能获取到股票 {symbol} 的实时数据")
                return {}

            # 筛选指定股票
            filtered_df = df[df["代码"] == symbol]
            if filtered_df.empty:
                logger.info(f"未能找到股票 {symbol} 的实时数据")
                return {}

            # 转换为字典
            return filtered_df.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Akshare获取实时数据失败: {e}")
            return {}
            return {}

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取交易日历-Akshare实现"""
        try:
            # 使用tool_trade_date_hist_sina接口获取交易日历
            df = ak.tool_trade_date_hist_sina()

            if df is None or df.empty:
                logger.info(r"未能获取到交易日历数据")
                return pd.DataFrame()

            # 筛选日期范围
            df["trade_date"] = pd.to_datetime(df["trade_date"])
            start_date = pd.to_datetime(normalize_date(start_date))
            end_date = pd.to_datetime(normalize_date(end_date))

            mask = (df["trade_date"] >= start_date) & (df["trade_date"] <= end_date)
            filtered_df = df[mask]

            return filtered_df
        except Exception as e:
            logger.error(f"Akshare获取交易日历失败: {e}")
            return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """获取财务数据-Akshare实现"""
        try:
            # 使用stock_financial_abstract接口获取财务摘要数据
            stock_code = format_stock_code_for_source(symbol, "akshare")
            df = ak.stock_financial_abstract(symbol=stock_code)

            if df is None or df.empty:
                logger.info(f"未能获取到股票 {symbol} 的财务数据")
                return pd.DataFrame()

            return df
        except Exception as e:
            logger.error(f"Akshare获取财务数据失败: {e}")
            return pd.DataFrame()

    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """获取新闻数据-Akshare实现"""
        try:
            # 如果提供了股票代码，获取个股新闻；否则获取市场新闻
            if symbol:
                # 获取个股新闻
                stock_code = format_stock_code_for_source(symbol, "akshare")
                df = ak.stock_news_em(symbol=stock_code)
            else:
                # 获取市场新闻
                df = ak.stock_news_em()

            if df is None or df.empty:
                logger.info(r"未能获取到新闻数据")
                return []

            # 限制返回数量
            if limit and len(df) > limit:
                df = df.head(limit)

            # 转换为字典列表
            return df.to_dict("records")
        except Exception as e:
            logger.error(f"Akshare获取新闻数据失败: {e}")
            return []

    def get_ths_industry_summary(self) -> pd.DataFrame:
        """获取同花顺行业一览表数据-Akshare实现

        该接口获取同花顺网站的行业板块数据，包含行业名称、最新价、涨跌幅、
        涨跌额、成交量、成交额、领涨股等信息。

        Returns:
            pd.DataFrame: 同花顺行业一览表数据
                - 行业: 行业名称
                - 最新价: 行业指数最新价格
                - 涨跌幅: 涨跌幅百分比
                - 涨跌额: 涨跌绝对值
                - 成交量: 成交量
                - 成交额: 成交金额
                - 领涨股: 该行业领涨股票
                - 涨跌家数: 上涨/下跌股票家数

        示例用法:
            >>> adapter = AkshareDataSource()
            >>> industry_data = adapter.get_ths_industry_summary()
            >>> logger.info(str(industry_data.head()))
        """
        try:
            logger.info(r"[Akshare] 开始获取同花顺行业一览表数据...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_industry_data():
                return ak.stock_board_industry_summary_ths()

            # 调用akshare接口获取同花顺行业一览表数据
            df = _get_industry_data()

            if df is None or df.empty:
                logger.info(r"[Akshare] 未能获取到同花顺行业一览表数据")
                return pd.DataFrame()

            logger.info(f"[Akshare] 成功获取同花顺行业数据: {len(df)}行, 列名={df.columns.tolist()}")

            # 使用统一列名映射器标准化列名(如果需要)
            # 注意：这里保留原始中文列名，因为这是行业数据的特殊格式
            # 如果需要英文列名，可以取消下面的注释
            # df = ColumnMapper.to_english(df)

            # 添加数据获取时间戳
            df["数据获取时间"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            return df

        except Exception as e:
            logger.error(f"[Akshare] 获取同花顺行业一览表数据失败: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def get_ths_industry_stocks(self, industry_name: str) -> pd.DataFrame:
        """获取同花顺指定行业的成分股数据-Akshare实现

        该接口获取同花顺指定行业下的所有成分股信息。
        注意：由于akshare的接口限制，此方法将使用东方财富的行业成分股接口。

        Args:
            industry_name (str): 行业名称，例如："房地产开发", "银行", "白酒" 等

        Returns:
            pd.DataFrame: 指定行业的成分股数据
                - 代码: 股票代码
                - 名称: 股票名称
                - 最新价: 最新价格
                - 涨跌幅: 涨跌幅百分比
                - 涨跌额: 涨跌绝对值
                - 成交量: 成交量
                - 成交额: 成交金额
                - 市盈率: 市盈率
                - 流通市值: 流通市值

        示例用法:
            >>> adapter = AkshareDataSource()
            >>> bank_stocks = adapter.get_ths_industry_stocks("银行")
            >>> logger.info(str(bank_stocks.head()))
        """
        try:
            logger.info(f"[Akshare] 开始获取行业'{industry_name}'的成分股数据...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_industry_stocks():
                # 使用东方财富的行业成分股接口
                return ak.stock_board_industry_cons_em(symbol=industry_name)

            # 调用akshare接口获取指定行业成分股数据
            df = _get_industry_stocks()

            if df is None or df.empty:
                logger.info(f"[Akshare] 未能获取到行业'{industry_name}'的成分股数据")
                return pd.DataFrame()

            logger.info(f"[Akshare] 成功获取行业'{industry_name}'成分股数据: {len(df)}行, 列名={df.columns.tolist()}")

            # 添加行业信息和数据获取时间戳
            df["所属行业"] = industry_name
            df["数据获取时间"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            return df

        except Exception as e:
            logger.error(f"[Akshare] 获取行业'{industry_name}'成分股数据失败: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def get_ths_industry_names(self) -> pd.DataFrame:
        """获取同花顺行业名称列表-Akshare实现

        该接口获取同花顺的所有行业名称和代码。

        Returns:
            pd.DataFrame: 同花顺行业名称列表
                - name: 行业名称
                - code: 行业代码

        示例用法:
            >>> adapter = AkshareDataSource()
            >>> industry_names = adapter.get_ths_industry_names()
            >>> logger.info(str(industry_names.head()))
        """
        try:
            logger.info(r"[Akshare] 开始获取同花顺行业名称列表...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_industry_names():
                return ak.stock_board_industry_name_ths()

            # 调用akshare接口获取同花顺行业名称列表
            df = _get_industry_names()

            if df is None or df.empty:
                logger.info(r"[Akshare] 未能获取到同花顺行业名称列表")
                return pd.DataFrame()

            logger.info(f"[Akshare] 成功获取同花顺行业名称列表: {len(df)}行, 列名={df.columns.tolist()}")

            # 添加数据获取时间戳
            df["数据获取时间"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            return df

        except Exception as e:
            logger.error(f"[Akshare] 获取同花顺行业名称列表失败: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def get_minute_kline(self, symbol: str, period: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取分钟K线数据（通过TDX适配器获取，AkShare本身不直接支持分钟K线）

        Args:
            symbol: str - 股票代码
            period: str - 周期 (1m/5m/15m/30m/60m)
            start_date: str - 开始日期
            end_date: str - 结束日期

        Returns:
            pd.DataFrame: 分钟K线数据
        """
        # AkShare本身不直接支持分钟K线，需要通过TDX适配器获取
        # 这里返回空DataFrame，实际通过统一数据源调用TDX适配器
        logger.info("[Akshare] 注意：AkShare不直接支持分钟K线数据，建议使用TDX适配器")
        return pd.DataFrame()

    def get_industry_classify(self) -> pd.DataFrame:
        """
        获取行业分类数据

        Returns:
            pd.DataFrame: 行业分类数据
                - index: 行业代码
                - name: 行业名称
                - stock_count: 成分股数量
                - up_count: 上涨股票数
                - down_count: 下跌股票数
                - leader_stock: 领涨股
        """
        try:
            logger.info(r"[Akshare] 开始获取行业分类数据...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_industry_classify():
                return ak.stock_board_industry_name_em()

            # 调用akshare接口获取行业分类数据
            df = _get_industry_classify()

            if df is None or df.empty:
                logger.info(r"[Akshare] 未能获取到行业分类数据")
                return pd.DataFrame()

            logger.info(f"[Akshare] 成功获取行业分类数据，共 {len(df)} 条记录")

            # 标准化列名
            df = df.rename(
                columns={
                    "板块代码": "index",
                    "板块名称": "name",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "涨跌额": "change_amount",
                    "成交量": "volume",
                    "成交额": "amount",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                    "领涨股": "leader_stock",
                }
            )

            # 添加股票数量列（如果不存在）
            if "up_count" in df.columns and "down_count" in df.columns:
                df["stock_count"] = df["up_count"] + df["down_count"]

            return df

        except Exception as e:
            logger.error(f"[Akshare] 获取行业分类数据失败: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def get_concept_classify(self) -> pd.DataFrame:
        """
        获取概念分类数据

        Returns:
            pd.DataFrame: 概念分类数据
                - index: 概念代码
                - name: 概念名称
                - stock_count: 成分股数量
                - up_count: 上涨股票数
                - down_count: 下跌股票数
                - leader_stock: 领涨股
        """
        try:
            logger.info(r"[Akshare] 开始获取概念分类数据...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_concept_classify():
                return ak.stock_board_concept_name_em()

            # 调用akshare接口获取概念分类数据
            df = _get_concept_classify()

            if df is None or df.empty:
                logger.info(r"[Akshare] 未能获取到概念分类数据")
                return pd.DataFrame()

            logger.info(f"[Akshare] 成功获取概念分类数据，共 {len(df)} 条记录")

            # 标准化列名
            df = df.rename(
                columns={
                    "板块代码": "index",
                    "板块名称": "name",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "涨跌额": "change_amount",
                    "成交量": "volume",
                    "成交额": "amount",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                    "领涨股": "leader_stock",
                }
            )

            # 添加股票数量列（如果不存在）
            if "up_count" in df.columns and "down_count" in df.columns:
                df["stock_count"] = df["up_count"] + df["down_count"]

            return df

        except Exception as e:
            logger.error(f"[Akshare] 获取概念分类数据失败: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def get_stock_industry_concept(self, symbol: str) -> Dict:
        """
        获取个股的行业和概念分类信息

        Args:
            symbol: str - 股票代码

        Returns:
            Dict: 个股行业和概念信息
                - symbol: 股票代码
                - industries: 行业列表
                - concepts: 概念列表
        """
        try:
            logger.info(f"[Akshare] 开始获取个股 {symbol} 的行业和概念信息...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_stock_industry():
                return ak.stock_individual_info_em(symbol=symbol)

            # 调用akshare接口获取个股信息
            df = _get_stock_industry()

            if df is None or df.empty:
                logger.info(f"[Akshare] 未能获取到个股 {symbol} 的信息")
                return {"symbol": symbol, "industries": [], "concepts": []}

            logger.info(f"[Akshare] 成功获取个股 {symbol} 的信息")

            # 提取行业和概念信息
            industries = []
            concepts = []

            # 查找行业和概念相关的行
            for _, row in df.iterrows():
                if "行业" in str(row.get("item", "")) or "所属行业" in str(row.get("item", "")):
                    industry = row.get("value", "")
                    if industry and industry != "--":
                        industries.append(industry)
                elif "概念" in str(row.get("item", "")):
                    concept = row.get("value", "")
                    if concept and concept != "--":
                        # 概念可能包含多个，用逗号分隔
                        concept_list = [c.strip() for c in str(concept).split(",") if c.strip()]
                        concepts.extend(concept_list)

            return {
                "symbol": symbol,
                "industries": industries,
                "concepts": list(set(concepts)),  # 去重
            }

        except Exception as e:
            logger.error(f"[Akshare] 获取个股 {symbol} 的行业和概念信息失败: {e}")
            import traceback

            traceback.print_exc()
            return {"symbol": symbol, "industries": [], "concepts": []}
