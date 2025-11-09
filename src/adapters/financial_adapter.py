"""
# 功能：财务数据适配器，整合多源财务报表和指标数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

"""
财务数据适配器 - 参考数据/基本面数据统一门户

本适配器是**财务/基本面数据的统一入口**,整合多个数据源提供完整的财务数据获取能力:

数据分类: 第2类-参考数据-基本面数据(DataClassification.FUNDAMENTAL_METRICS)
- 结构化财务指标:营收、净利润、EPS、ROE等
- 数据特性:相对静态、关系型结构、低频更新(季度/年度)
- 存储策略:MySQL/MariaDB(支持复杂JOIN和ACID事务)

多数据源支持:
- efinance: 东方财富数据(当前主要数据源)
- easyquotation: 实时行情备用源
- akshare: 财务报表、财务指标(计划集成)
- tushare: 专业财务数据接口(计划集成)
- byapi: 财务数据接口(计划集成)
- 新浪财经: 网页爬虫方法(计划集成)

设计理念:
- 统一接口:对外提供一致的财务数据获取方法
- 自动降级:数据源失败时自动切换备用源
- 扩展性强:便于添加新的财务数据源
"""
import pandas as pd
from typing import Dict, List, Optional, Union
import sys
import os
import traceback
from datetime import datetime, timedelta

# 导入loguru而不是logging
from loguru import logger

# 导入接口定义
from mystocks.interfaces.data_source import IDataSource

# 导入工具函数
from mystocks.utils import date_utils, symbol_utils

# 配置loguru
logger.remove()  # 移除默认的日志处理器
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
)
logger.add(
    "financial_adapter.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
    encoding="utf-8",
    rotation="10 MB",
)

# 移除logging相关代码
# logger = logging.getLogger('FinancialDataSource')


class FinancialDataSource(IDataSource):
    """
    财务数据适配器 - 参考数据/基本面数据统一门户

    数据分类: DataClassification.FUNDAMENTAL_METRICS (第2类-参考数据-基本面数据)
    存储目标: MySQL/MariaDB
    数据特性: 低频、结构化、关系型

    多数据源整合:
    - 当前实现: efinance(主要) + easyquotation(备用)
    - 计划扩展: akshare、tushare、byapi、新浪财经爬虫

    核心能力:
    - 统一的财务数据获取接口
    - 多数据源自动降级切换
    - 数据验证和清洗
    - 智能缓存机制
    """

    def __init__(self):
        """
        初始化财务数据适配器

        当前支持: efinance + easyquotation
        扩展计划: akshare、tushare、byapi、新浪财经爬虫
        """
        logger.info("初始化财务数据适配器...")
        # 当前实现的数据源
        self.efinance_available = False
        self.easyquotation_available = False
        # 计划扩展的数据源 (预留标志位)
        self.akshare_available = False
        self.tushare_available = False
        self.byapi_available = False
        self.sina_crawler_available = False
        # 初始化缓存字典
        self.data_cache = {}
        self._init_data_sources()
        logger.info(
            f"数据源初始化完成 (efinance: {'可用' if self.efinance_available else '不可用'}, easyquotation: {'可用' if self.easyquotation_available else '不可用'})"
        )

    def _get_cache_key(self, symbol: str, data_type: str, **kwargs) -> str:
        """
        生成缓存键

        Args:
            symbol: 股票代码
            data_type: 数据类型
            **kwargs: 其他参数

        Returns:
            str: 缓存键
        """
        # 将参数转换为字符串并组合成键
        key_parts = [symbol, data_type]
        # 按键排序以确保相同参数生成相同的键
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return "|".join(key_parts)

    def _get_from_cache(self, cache_key: str):
        """
        从缓存中获取数据

        Args:
            cache_key: 缓存键

        Returns:
            缓存的数据，如果不存在或过期则返回None
        """
        if cache_key in self.data_cache:
            cached_item = self.data_cache[cache_key]
            # 检查缓存是否过期（这里设置为5分钟）
            if (datetime.now() - cached_item["timestamp"]).total_seconds() < 300:
                logger.info(f"使用缓存数据: {cache_key}")
                return cached_item["data"]
            else:
                # 删除过期缓存
                del self.data_cache[cache_key]
        return None

    def _save_to_cache(self, cache_key: str, data):
        """
        保存数据到缓存

        Args:
            cache_key: 缓存键
            data: 要缓存的数据
        """
        self.data_cache[cache_key] = {"data": data, "timestamp": datetime.now()}
        logger.info(f"数据已缓存: {cache_key}")

    def _init_data_sources(self):
        """
        初始化多数据源

        当前实现: efinance + easyquotation
        扩展计划: akshare、tushare、byapi、新浪财经爬虫
        """
        # 初始化efinance (当前主要数据源)
        try:
            import efinance as ef

            self.ef = ef
            self.efinance_available = True
            logger.info("efinance库导入成功")
        except ImportError:
            logger.warning("efinance库导入失败")
            self.efinance_available = False

        # 初始化easyquotation (当前备用数据源)
        try:
            import easyquotation as eq

            self.eq = eq
            self.easyquotation_available = True
            logger.info("easyquotation库导入成功")
        except ImportError:
            logger.warning("easyquotation库导入失败")
            self.easyquotation_available = False

        # TODO: 扩展其他数据源
        # - akshare: 财务报表、财务指标接口
        # - tushare: 专业财务数据接口(需token)
        # - byapi: 财务数据接口
        # - 新浪财经: 网页爬虫方法

    def get_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        获取股票日线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame: 包含股票日线数据的DataFrame
        """
        logger.info(f"尝试获取股票日线数据: {symbol}")

        # 参数验证
        if not symbol:
            logger.error("股票代码不能为空")
            return pd.DataFrame()

        # 使用symbol_utils标准化股票代码
        normalized_symbol = symbol_utils.normalize_stock_code(symbol)
        if not normalized_symbol:
            logger.error(f"无效的股票代码: {symbol}")
            return pd.DataFrame()

        # 使用date_utils标准化日期
        try:
            normalized_start_date = (
                date_utils.normalize_date(start_date) if start_date else None
            )
            normalized_end_date = (
                date_utils.normalize_date(end_date) if end_date else None
            )
        except ValueError as e:
            logger.error(f"日期格式错误: {e}")
            return pd.DataFrame()

        if not normalized_start_date or not normalized_end_date:
            logger.warning("日期参数不完整，将使用默认日期范围")

        # 首先尝试使用efinance获取数据
        if self.efinance_available:
            try:
                # 使用efinance获取股票日线数据
                logger.info("使用efinance获取股票日线数据")
                logger.info(
                    f"请求参数: symbol={normalized_symbol}, beg={normalized_start_date}, end={normalized_end_date}"
                )
                data = self.ef.stock.get_quote_history(
                    normalized_symbol,
                    beg=normalized_start_date,
                    end=normalized_end_date,
                )
                logger.info(f"efinance返回数据类型: {type(data)}")
                if isinstance(data, pd.DataFrame):
                    logger.info(f"efinance返回数据行数: {len(data)}")
                    if not data.empty:
                        logger.info(f"efinance获取到{len(data)}行日线数据")
                        # 确保列名是中文
                        expected_columns = [
                            "日期",
                            "开盘",
                            "收盘",
                            "最高",
                            "最低",
                            "成交量",
                            "成交额",
                        ]
                        if all(col in data.columns for col in expected_columns):
                            logger.info("数据格式正确")
                            # 验证和清洗数据
                            cleaned_data = self._validate_and_clean_data(data, "stock")
                            return cleaned_data
                        else:
                            logger.warning(
                                f"数据列名不匹配，实际列名: {list(data.columns)}"
                            )
                            # 尝试重命名列
                            renamed_data = self._rename_columns(data)
                            # 验证和清洗数据
                            cleaned_data = self._validate_and_clean_data(
                                renamed_data, "stock"
                            )
                            return cleaned_data
                    else:
                        logger.warning("efinance返回空数据")
                        # 尝试更广泛的日期范围
                        logger.info("尝试更广泛的日期范围...")
                        broader_data = self.ef.stock.get_quote_history(
                            normalized_symbol, beg="2020-01-01", end="2024-12-31"
                        )
                        if not broader_data.empty:
                            logger.info(
                                f"更广泛日期范围获取到{len(broader_data)}行数据"
                            )
                            # 过滤日期范围
                            broader_data["日期"] = pd.to_datetime(broader_data["日期"])
                            start_date_dt = pd.to_datetime(
                                date_utils.normalize_date(normalized_start_date)
                            )
                            end_date_dt = pd.to_datetime(
                                date_utils.normalize_date(normalized_end_date)
                            )
                            filtered_data = broader_data[
                                (broader_data["日期"] >= start_date_dt)
                                & (broader_data["日期"] <= end_date_dt)
                            ]
                            if not filtered_data.empty:
                                logger.info(f"过滤后得到{len(filtered_data)}行数据")
                                # 验证和清洗数据
                                cleaned_data = self._validate_and_clean_data(
                                    filtered_data, "stock"
                                )
                                return cleaned_data
                            else:
                                logger.warning("过滤后数据为空")
                                return pd.DataFrame()
                        else:
                            logger.warning("更广泛日期范围也未获取到数据")
                            return pd.DataFrame()
                else:
                    logger.error(f"efinance返回数据类型不正确: {type(data)}")
                    return pd.DataFrame()
            except Exception as e:
                logger.error(f"efinance获取日线数据失败: {e}")
                import traceback

                logger.error(traceback.format_exc())
                return pd.DataFrame()

        # 如果efinance不可用或失败，尝试使用easyquotation
        if self.easyquotation_available:
            try:
                logger.info("使用easyquotation获取股票数据")
                # 使用easyquotation获取实时数据作为替代
                quotation = self.eq.use("sina")  # 使用sina源
                data = quotation.real([normalized_symbol])  # 获取实时数据
                if data and normalized_symbol in data:
                    logger.info("easyquotation获取到股票数据")
                    # 转换为DataFrame格式
                    df_data = data[normalized_symbol]
                    df = pd.DataFrame([df_data])
                    # 添加必要的列以匹配预期格式
                    if "date" not in df.columns and "datetime" in df.columns:
                        df["date"] = df["datetime"].str[:10]  # 从datetime提取日期
                    elif "date" not in df.columns:
                        df["date"] = date_utils.normalize_date(datetime.now())
                    # 重命名列以匹配预期格式
                    column_mapping = {
                        "date": "日期",
                        "open": "开盘",
                        "close": "收盘",
                        "high": "最高",
                        "low": "最低",
                        "volume": "成交量",
                        "amount": "成交额",
                    }
                    df = df.rename(columns=column_mapping)
                    # 确保包含所有必要列
                    expected_columns = [
                        "日期",
                        "开盘",
                        "收盘",
                        "最高",
                        "最低",
                        "成交量",
                        "成交额",
                    ]
                    for col in expected_columns:
                        if col not in df.columns:
                            df[col] = 0  # 默认值
                    # 验证和清洗数据
                    cleaned_data = self._validate_and_clean_data(
                        df[expected_columns], "stock"
                    )  # 按预期顺序返回列
                    return cleaned_data
                else:
                    logger.warning("easyquotation未获取到股票数据")
            except Exception as e:
                logger.error(f"easyquotation获取股票数据失败: {e}")
                import traceback

                logger.error(traceback.format_exc())

        logger.warning("所有方法均未能获取到股票日线数据")
        return pd.DataFrame()

    def _rename_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        重命名列名以匹配预期格式

        Args:
            data: 原始数据

        Returns:
            DataFrame: 重命名后的数据
        """
        # 这里可以根据实际返回的列名进行映射
        column_mapping = {
            # 可能的英文列名映射
            "date": "日期",
            "open": "开盘",
            "close": "收盘",
            "high": "最高",
            "low": "最低",
            "volume": "成交量",
            "amount": "成交额",
        }

        # 应用列名映射
        renamed_data = data.rename(columns=column_mapping)
        return renamed_data

    def get_index_daily(self, index_code, start_date=None, end_date=None):
        """
        获取指数日线数据

        Args:
            index_code (str): 指数代码
            start_date (str, optional): 开始日期，格式为'YYYY-MM-DD'
            end_date (str, optional): 结束日期，格式为'YYYY-MM-DD'

        Returns:
            pd.DataFrame: 指数日线数据
        """
        logger.info(f"尝试获取指数 {index_code} 的日线数据...")

        # 参数验证
        if not index_code:
            logger.error("指数代码不能为空")
            return pd.DataFrame()

        # 使用symbol_utils标准化股票代码
        normalized_index_code = symbol_utils.normalize_stock_code(index_code)
        if not normalized_index_code:
            logger.error(f"无效的指数代码: {index_code}")
            return pd.DataFrame()

        # 使用date_utils标准化日期
        try:
            normalized_start_date = (
                date_utils.normalize_date(start_date) if start_date else None
            )
            normalized_end_date = (
                date_utils.normalize_date(end_date) if end_date else None
            )
        except ValueError as e:
            logger.error(f"日期格式错误: {e}")
            return pd.DataFrame()

        if not self.efinance_available:
            logger.warning("efinance库不可用")
            return pd.DataFrame()

        try:
            # 格式化指数代码，使用东方财富的指数代码格式
            if normalized_index_code == "000300":
                formatted_code = "399300"  # 沪深300指数在东方财富的代码为399300
            else:
                formatted_code = normalized_index_code

            logger.info(f"使用格式化代码: {formatted_code}")

            # 获取历史行情数据
            logger.info(
                f"请求参数: code={formatted_code}, beg={normalized_start_date}, end={normalized_end_date}"
            )
            if normalized_start_date and normalized_end_date:
                data = self.ef.stock.get_quote_history(
                    formatted_code, beg=normalized_start_date, end=normalized_end_date
                )
            elif normalized_start_date:
                data = self.ef.stock.get_quote_history(
                    formatted_code, beg=normalized_start_date
                )
            elif normalized_end_date:
                data = self.ef.stock.get_quote_history(
                    formatted_code, end=normalized_end_date
                )
            else:
                data = self.ef.stock.get_quote_history(formatted_code)

            logger.info(f"efinance返回数据类型: {type(data)}")
            if isinstance(data, pd.DataFrame):
                logger.info(f"efinance返回数据行数: {len(data)}")

            # 如果使用日期参数没有获取到数据，则获取全部数据并进行过滤
            if (normalized_start_date or normalized_end_date) and (
                data is None or (isinstance(data, pd.DataFrame) and data.empty)
            ):
                logger.warning(f"使用日期参数未获取到数据，尝试获取全部数据并过滤...")
                data = self.ef.stock.get_quote_history(formatted_code)
                if (
                    data is not None
                    and isinstance(data, pd.DataFrame)
                    and not data.empty
                ):
                    # 过滤日期范围
                    if normalized_start_date:
                        data = data[data["日期"] >= normalized_start_date]
                    if normalized_end_date:
                        data = data[data["日期"] <= normalized_end_date]

            if data is not None and isinstance(data, pd.DataFrame) and not data.empty:
                logger.info(
                    f"成功获取指数 {index_code} 的日线数据，共 {len(data)} 条记录"
                )
                # 验证和清洗数据
                cleaned_data = self._validate_and_clean_data(data, "index")
                return cleaned_data
            else:
                logger.warning(f"未获取到指数 {index_code} 的日线数据")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取指数 {index_code} 日线数据时发生错误: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            return pd.DataFrame()

    def get_stock_basic(self, symbol: str) -> Dict:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            Dict: 包含股票基本信息的字典
        """
        logger.info(f"尝试获取股票基本信息: {symbol}")

        # 参数验证
        if not symbol:
            logger.error("股票代码不能为空")
            return {}

        # 使用symbol_utils标准化股票代码
        normalized_symbol = symbol_utils.normalize_stock_code(symbol)
        if not normalized_symbol:
            logger.error(f"无效的股票代码: {symbol}")
            return {}

        # 首先尝试使用efinance获取数据
        if self.efinance_available:
            try:
                # 使用efinance获取股票基本信息
                logger.info("使用efinance获取股票基本信息")
                data = self.ef.stock.get_base_info(normalized_symbol)
                logger.info(f"efinance返回数据类型: {type(data)}")
                if data is not None:
                    logger.info("efinance获取到股票基本信息")
                    # 如果data是DataFrame，转换第一行为字典
                    if isinstance(data, pd.DataFrame):
                        logger.info(f"efinance返回数据行数: {len(data)}")
                        if not data.empty:
                            # 验证和清洗数据
                            cleaned_data = self._validate_and_clean_data(data, "stock")
                            # 返回第一行数据的字典形式
                            return cleaned_data.iloc[0].to_dict()
                        else:
                            logger.warning("efinance返回空数据")
                            return {}
                    # 如果data是Series，转换为字典
                    elif isinstance(data, pd.Series):
                        # 验证和清洗数据
                        df_data = data.to_frame().T  # 转换为DataFrame
                        cleaned_data = self._validate_and_clean_data(df_data, "stock")
                        return cleaned_data.iloc[0].to_dict()
                    # 如果data已经是字典，直接返回
                    elif isinstance(data, dict):
                        return data
                    else:
                        # 其他情况尝试直接返回
                        logger.warning(f"efinance返回数据类型不支持: {type(data)}")
                        return data if data else {}
                else:
                    logger.warning("efinance未获取到股票基本信息")
            except Exception as e:
                logger.error(f"efinance获取股票基本信息失败: {e}")
                import traceback

                logger.error(traceback.format_exc())

        # 如果efinance不可用或失败，尝试使用easyquotation
        if self.easyquotation_available:
            try:
                logger.info("使用easyquotation获取股票基本信息")
                quotation = self.eq.use("sina")  # 使用sina源
                data = quotation.real(
                    [normalized_symbol]
                )  # 获取实时数据，其中包含基本信息
                logger.info(f"easyquotation返回数据类型: {type(data)}")
                if data and normalized_symbol in data:
                    logger.info("easyquotation获取到股票数据")
                    # 转换为DataFrame格式
                    df = pd.DataFrame([data[normalized_symbol]])
                    logger.info(f"easyquotation返回数据行数: {len(df)}")
                    # 验证和清洗数据
                    cleaned_data = self._validate_and_clean_data(df, "stock")
                    return cleaned_data.iloc[0].to_dict()
                else:
                    logger.warning("easyquotation未获取到股票数据")
            except Exception as e:
                logger.error(f"easyquotation获取股票基本信息失败: {e}")
                import traceback

                logger.error(traceback.format_exc())

        logger.warning("所有方法均未能获取到股票基本信息")
        return {}

    def get_index_components(self, index_code):
        """
        获取指数的成分股数据

        Args:
            index_code (str): 指数代码或名称

        Returns:
            pd.DataFrame: 指数成分股数据
        """
        logger.info(f"尝试获取指数 {index_code} 的成分股数据...")

        # 参数验证
        if not index_code:
            logger.error("指数代码不能为空")
            return pd.DataFrame()

        # 使用symbol_utils标准化股票代码
        normalized_index_code = symbol_utils.normalize_stock_code(index_code)
        if not normalized_index_code:
            logger.error(f"无效的指数代码: {index_code}")
            return pd.DataFrame()

        if not self.efinance_available and not self.easyquotation_available:
            logger.warning("数据源未初始化或不可用")
            return pd.DataFrame()

        try:
            # 使用efinance的stock.get_members方法获取指数成分股
            logger.info(f"使用efinance获取指数 {index_code} 的成分股数据")
            df = self.ef.stock.get_members(normalized_index_code)

            # 检查返回的数据是否有效
            logger.info(f"efinance返回数据类型: {type(df)}")
            if df is not None and not df.empty:
                logger.info(f"成功获取指数{index_code}的成分股数据，共{len(df)}只股票")
                # 验证和清洗数据
                cleaned_data = self._validate_and_clean_data(df, "stock")
                return cleaned_data
            else:
                logger.warning(f"获取指数{index_code}的成分股数据为空")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取指数{index_code}的成分股数据时发生错误: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            return pd.DataFrame()

    def get_real_time_data(self, symbol: str = None) -> pd.DataFrame:
        """
        获取实时数据（仅支持A股市场）

        Args:
            symbol: 股票代码（可选）

        Returns:
            DataFrame: 包含实时数据的DataFrame
        """
        logger.info(f"尝试获取实时数据: symbol={symbol}")

        # 参数验证
        if symbol and not isinstance(symbol, str):
            logger.error("股票代码必须是字符串类型")
            return pd.DataFrame()

        # 生成缓存键
        cache_key = self._get_cache_key(symbol or "market_snapshot", "realtime")

        # 尝试从缓存中获取数据
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            logger.info(f"使用缓存数据: {cache_key}")
            return cached_data

        # 首先尝试使用efinance获取数据
        if self.efinance_available:
            try:
                if symbol:
                    # 使用symbol_utils标准化股票代码
                    normalized_symbol = symbol_utils.normalize_stock_code(symbol)
                    if not normalized_symbol:
                        logger.error(f"无效的股票代码: {symbol}")
                        return pd.DataFrame()

                    # 获取特定股票的实时数据
                    logger.info(f"获取特定股票实时数据: {normalized_symbol}")
                    data = self.ef.stock.get_realtime_quotes(symbol=normalized_symbol)
                else:
                    # 获取市场快照（仅支持A股市场）
                    logger.info("获取A股市场快照")
                    # 对于A股市场，获取主要指数的实时数据作为市场快照
                    major_indices = [
                        "000001",
                        "399001",
                        "399006",
                    ]  # 上证指数、深证成指、创业板指
                    data = pd.DataFrame()
                    for index_code in major_indices:
                        try:
                            index_data = self.ef.stock.get_realtime_quotes(
                                symbol=index_code
                            )
                            if (
                                isinstance(index_data, pd.DataFrame)
                                and not index_data.empty
                            ):
                                data = pd.concat([data, index_data], ignore_index=True)
                        except Exception as e:
                            logger.error(f"获取指数{index_code}数据失败: {e}")
                            import traceback

                            logger.error(traceback.format_exc())

                logger.info(f"efinance返回数据类型: {type(data)}")
                if isinstance(data, pd.DataFrame):
                    logger.info(f"efinance返回数据行数: {len(data)}")
                    if not data.empty:
                        logger.info(f"efinance获取到{len(data)}行实时数据")
                        # 验证和清洗数据
                        cleaned_data = self._validate_and_clean_data(data, "stock")
                        # 保存到缓存
                        self._save_to_cache(cache_key, cleaned_data)
                        return cleaned_data
                    else:
                        logger.warning("efinance返回空数据")
                        return pd.DataFrame()
                else:
                    logger.error(f"efinance返回数据类型不正确: {type(data)}")
                    return pd.DataFrame()
            except Exception as e:
                logger.error(f"efinance获取实时数据失败: {e}")
                import traceback

                logger.error(traceback.format_exc())
                return pd.DataFrame()

        # 如果efinance不可用或失败，尝试使用easyquotation
        if self.easyquotation_available:
            try:
                logger.info("使用easyquotation获取实时数据")
                quotation = self.eq.use("sina")  # 使用sina源

                if symbol:
                    # 使用symbol_utils标准化股票代码
                    normalized_symbol = symbol_utils.normalize_stock_code(symbol)
                    if not normalized_symbol:
                        logger.error(f"无效的股票代码: {symbol}")
                        return pd.DataFrame()

                    # 获取特定股票的实时数据
                    logger.info(f"获取特定股票实时数据: {normalized_symbol}")
                    data = quotation.real([normalized_symbol])
                    if data and normalized_symbol in data:
                        logger.info("easyquotation获取到股票数据")
                        # 转换为DataFrame格式
                        df = pd.DataFrame([data[normalized_symbol]])
                        # 验证和清洗数据
                        cleaned_data = self._validate_and_clean_data(df, "stock")
                        # 保存到缓存
                        self._save_to_cache(cache_key, cleaned_data)
                        return cleaned_data
                    else:
                        logger.warning("easyquotation未获取到指定股票数据")
                        return pd.DataFrame()
                else:
                    # 获取市场快照（仅支持A股市场）
                    logger.info("获取A股市场快照")
                    # 获取A股市场快照（需要提供股票代码列表）
                    # 扩展股票代码列表以获取更全面的市场快照
                    stock_codes = [
                        "000001",
                        "000002",
                        "600000",
                        "600036",  # 平安银行、万科A、浦发银行、招商银行
                        "600519",
                        "000858",
                        "002594",
                        "300750",  # 贵州茅台、五粮液、比亚迪、宁德时代
                        "399001",
                        "399006",
                        "000001",  # 深证成指、创业板指、上证指数
                    ]
                    data = quotation.real(stock_codes)
                    if data:
                        logger.info(f"easyquotation获取到{len(data)}只股票数据")
                        # 转换为DataFrame格式
                        df = pd.DataFrame(data).T  # 转置以使每行代表一只股票
                        # 验证和清洗数据
                        cleaned_data = self._validate_and_clean_data(df, "stock")
                        # 保存到缓存
                        self._save_to_cache(cache_key, cleaned_data)
                        return cleaned_data
                    else:
                        logger.warning("easyquotation未获取到市场快照数据")
                        return pd.DataFrame()

            except Exception as e:
                logger.error(f"easyquotation获取实时数据失败: {e}")
                import traceback

                logger.error(traceback.format_exc())
                return pd.DataFrame()

        logger.warning("所有方法均未能获取到实时数据")
        return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """
        获取股票财务数据

        Args:
            symbol: 股票代码
            period: 报告期类型 ("annual" 年报或 "quarterly" 季报)

        Returns:
            DataFrame: 包含股票财务数据的DataFrame
        """
        logger.info(f"尝试获取财务数据: {symbol}, period: {period}")

        # 参数验证
        if not symbol:
            logger.error("股票代码不能为空")
            return pd.DataFrame()

        # 使用symbol_utils标准化股票代码
        normalized_symbol = symbol_utils.normalize_stock_code(symbol)
        if not normalized_symbol:
            logger.error(f"无效的股票代码: {symbol}")
            return pd.DataFrame()

        if period not in ["annual", "quarterly"]:
            logger.warning(f"不支持的报告期类型: {period}，将使用默认年报类型")
            period = "annual"

        if not self.efinance_available:
            logger.warning("efinance库不可用")
            return pd.DataFrame()

        # 生成缓存键
        cache_key = self._get_cache_key(normalized_symbol, "financial", period=period)

        # 尝试从缓存中获取数据
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            logger.info(f"使用缓存数据: {cache_key}")
            return cached_data

        try:
            # 根据报告期类型选择不同的数据获取方式
            if period == "annual":
                # 获取年报数据
                logger.info("使用efinance获取年报数据")
                # 尝试直接获取指定股票的财务数据，而不是获取所有公司的数据
                # 注意：efinance库可能没有get_stock_financial_analysis方法，直接使用传统方法
                try:
                    # 注释掉不存在的方法调用
                    # financial_summary = self.ef.stock.get_stock_financial_analysis(normalized_symbol)
                    # if financial_summary is not None and not financial_summary.empty:
                    #     logger.info(f"efinance获取到个股财务摘要数据: {len(financial_summary)}行")
                    #     # 验证和清洗数据
                    #     cleaned_data = self._validate_and_clean_data(financial_summary, "financial")
                    #     # 保存到缓存
                    #     self._save_to_cache(cache_key, cleaned_data)
                    #     return cleaned_data
                    pass  # 占位符，避免空的try块
                except Exception as e:
                    logger.error(f"获取个股财务摘要数据失败: {e}")
                    import traceback

                    logger.error(traceback.format_exc())

                # 如果无法获取个股摘要数据，则获取所有公司数据后筛选
                logger.info("使用传统方法获取财务数据")
                all_data = self.ef.stock.get_all_company_performance()

                if not all_data.empty:
                    # 筛选出指定股票的数据
                    filtered_data = all_data[
                        (all_data["股票代码"] == normalized_symbol)
                        | (
                            all_data["股票简称"].str.contains(
                                normalized_symbol, na=False
                            )
                        )
                    ]

                    if not filtered_data.empty:
                        logger.info(f"efinance获取到{len(filtered_data)}行财务数据")
                        # 添加报告期类型标识
                        filtered_data = (
                            filtered_data.copy()
                        )  # 创建副本避免SettingWithCopyWarning
                        filtered_data.loc[:, "报告期类型"] = "annual"
                        # 验证和清洗数据
                        cleaned_data = self._validate_and_clean_data(
                            filtered_data, "financial"
                        )
                        # 保存到缓存
                        self._save_to_cache(cache_key, cleaned_data)
                        return cleaned_data
                    else:
                        logger.warning("未找到指定股票的财务数据")
                        return pd.DataFrame()
                else:
                    logger.warning("efinance未获取到财务数据")
                    return pd.DataFrame()
            else:
                # 获取季报数据
                logger.info("使用efinance获取季报数据")
                try:
                    # 尝试获取季度财务数据
                    quarterly_data = self.ef.stock.get_quarterly_performance(
                        normalized_symbol
                    )
                    if quarterly_data is not None and not quarterly_data.empty:
                        logger.info(f"efinance获取到{len(quarterly_data)}行季报数据")
                        # 添加报告期类型标识
                        quarterly_data = (
                            quarterly_data.copy()
                        )  # 创建副本避免SettingWithCopyWarning
                        quarterly_data.loc[:, "报告期类型"] = "quarterly"
                        # 验证和清洗数据
                        cleaned_data = self._validate_and_clean_data(
                            quarterly_data, "financial"
                        )
                        # 保存到缓存
                        self._save_to_cache(cache_key, cleaned_data)
                        return cleaned_data
                    else:
                        logger.warning("efinance未获取到季报数据")
                        return pd.DataFrame()
                except Exception as e:
                    logger.error(f"获取季报数据失败: {e}")
                    import traceback

                    logger.error(traceback.format_exc())
                    return pd.DataFrame()
        except Exception as e:
            logger.error(f"efinance获取财务数据失败: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return pd.DataFrame()

    def get_market_calendar(self) -> pd.DataFrame:
        """
        获取交易日历

        Returns:
            DataFrame: 包含交易日历的DataFrame
        """
        logger.info("尝试获取交易日历")
        if not self.efinance_available:
            logger.warning("efinance库不可用")
            return pd.DataFrame()

        # 生成缓存键
        cache_key = self._get_cache_key("market_calendar", "calendar")

        # 尝试从缓存中获取数据
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            logger.info(f"使用缓存数据: {cache_key}")
            return cached_data

        try:
            # 使用efinance获取交易日历
            logger.info("使用efinance获取交易日历")
            data = self.ef.stock.get_all_report_dates()
            logger.info(f"efinance返回数据类型: {type(data)}")
            if isinstance(data, pd.DataFrame):
                logger.info(f"efinance返回数据行数: {len(data)}")
                if not data.empty:
                    logger.info(f"efinance获取到{len(data)}个交易日")
                    # 保存到缓存
                    self._save_to_cache(cache_key, data)
                    return data
                else:
                    logger.warning("efinance未获取到交易日历")
                    return pd.DataFrame()
            else:
                logger.error(f"efinance返回数据类型不正确: {type(data)}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"efinance获取交易日历失败: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return pd.DataFrame()

    def get_news_data(self, symbol: str) -> pd.DataFrame:
        """
        获取股票新闻数据

        Args:
            symbol: 股票代码

        Returns:
            DataFrame: 包含股票新闻数据的DataFrame
        """
        logger.info(f"尝试获取股票新闻数据: {symbol}")

        # 参数验证
        if not symbol:
            logger.error("股票代码不能为空")
            return pd.DataFrame()

        # 使用symbol_utils标准化股票代码
        normalized_symbol = symbol_utils.normalize_stock_code(symbol)
        if not normalized_symbol:
            logger.error(f"无效的股票代码: {symbol}")
            return pd.DataFrame()

        if not self.efinance_available:
            logger.warning("efinance库不可用")
            return pd.DataFrame()

        # 生成缓存键
        cache_key = self._get_cache_key(normalized_symbol, "news")

        # 尝试从缓存中获取数据
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            logger.info(f"使用缓存数据: {cache_key}")
            return cached_data

        try:
            # 使用efinance获取股票新闻数据
            logger.info("使用efinance获取股票新闻数据")
            # 注意：efinance可能没有直接获取新闻数据的接口
            # 这里返回空DataFrame作为占位符
            logger.warning("efinance暂不支持获取新闻数据")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"efinance获取股票新闻数据失败: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return pd.DataFrame()

    def _validate_and_clean_data(
        self, data: pd.DataFrame, data_type: str = "stock"
    ) -> pd.DataFrame:
        """
        验证和清洗数据

        Args:
            data: 原始数据
            data_type: 数据类型 ("stock", "index", "financial")

        Returns:
            DataFrame: 清洗后的数据
        """
        if data is None or data.empty:
            logger.warning("输入数据为空")
            return pd.DataFrame()

        try:
            logger.info(f"开始验证和清洗{data_type}数据，原始行数: {len(data)}")

            # 创建数据副本以避免修改原始数据
            cleaned_data = data.copy()

            # 通用清洗步骤
            # 1. 删除完全重复的行
            initial_rows = len(cleaned_data)
            cleaned_data = cleaned_data.drop_duplicates()
            if len(cleaned_data) < initial_rows:
                logger.info(f"删除了{initial_rows - len(cleaned_data)}行完全重复的数据")

            # 2. 处理缺失值
            # 对于数值列，用前向填充或后向填充填补缺失值
            numeric_columns = cleaned_data.select_dtypes(include=["number"]).columns
            if len(numeric_columns) > 0:
                # 使用前向填充，如果前面没有数据则使用后向填充
                # 替换已弃用的fillna(method='ffill')方法
                cleaned_data[numeric_columns] = (
                    cleaned_data[numeric_columns].ffill().bfill()
                )
                # 如果仍有缺失值，使用列的均值填充
                for col in numeric_columns:
                    if cleaned_data[col].isna().any():
                        mean_value = cleaned_data[col].mean()
                        # 替换使用inplace=True的fillna方法
                        cleaned_data.loc[:, col] = cleaned_data[col].fillna(mean_value)
                        logger.info(f"使用均值 {mean_value} 填充列 {col} 的缺失值")

            # 3. 数据类型转换和验证
            if data_type == "stock" or data_type == "index":
                # 确保日期列是datetime类型
                if "日期" in cleaned_data.columns:
                    # 处理日期列中的异常值
                    original_dates = len(cleaned_data)
                    cleaned_data["日期"] = pd.to_datetime(
                        cleaned_data["日期"], errors="coerce"
                    )
                    # 删除日期转换失败的行
                    invalid_date_rows = cleaned_data["日期"].isna().sum()
                    if invalid_date_rows > 0:
                        logger.info(f"删除了{invalid_date_rows}行日期无效的数据")
                        cleaned_data = cleaned_data.dropna(subset=["日期"])

                    # 检查日期是否在合理范围内（1990年至今）
                    valid_date_range = (cleaned_data["日期"] >= "1990-01-01") & (
                        cleaned_data["日期"]
                        <= pd.to_datetime(date_utils.normalize_date(datetime.now()))
                        + pd.Timedelta(days=1)
                    )
                    invalid_dates = ~valid_date_range
                    invalid_date_count = invalid_dates.sum()
                    if invalid_date_count > 0:
                        logger.info(
                            f"删除了{invalid_date_count}行日期超出合理范围的数据"
                        )
                        cleaned_data = cleaned_data[valid_date_range]

                # 确保价格相关列是数值类型
                price_columns = ["开盘", "收盘", "最高", "最低", "成交量", "成交额"]
                for col in price_columns:
                    if col in cleaned_data.columns:
                        original_type = cleaned_data[col].dtype
                        cleaned_data[col] = pd.to_numeric(
                            cleaned_data[col], errors="coerce"
                        )
                        # 删除数值转换失败的行
                        invalid_numeric_rows = cleaned_data[col].isna().sum()
                        if invalid_numeric_rows > 0:
                            logger.info(f"发现{invalid_numeric_rows}行{col}列数据无效")
                            # 如果是价格列，尝试用其他价格列的数据推算
                            if (
                                col in ["开盘", "收盘", "最高", "最低"]
                                and invalid_numeric_rows < len(cleaned_data) * 0.1
                            ):
                                # 简单的前向和后向填充
                                # 替换已弃用的fillna(method='ffill')方法
                                cleaned_data[col] = cleaned_data[col].ffill().bfill()
                                logger.info(f"使用前向/后向填充处理{col}列的缺失值")

            elif data_type == "financial":
                # 财务数据特殊处理
                # 确保数值列是数值类型
                object_columns = cleaned_data.select_dtypes(include=["object"]).columns
                for col in object_columns:
                    # 尝试将可能的数值字符串转换为数值
                    original_values = cleaned_data[col].copy()
                    cleaned_data[col] = pd.to_numeric(
                        cleaned_data[col].astype(str).str.replace(",", ""),
                        errors="coerce",
                    )
                    # 记录转换结果
                    converted_count = (
                        cleaned_data[col].notna() & original_values.notna()
                    ).sum()
                    if converted_count > 0:
                        logger.info(
                            f"成功转换{converted_count}个{col}列的字符串值为数值"
                        )

            # 4. 数据范围验证
            if data_type == "stock" or data_type == "index":
                # 验证价格合理性
                if "收盘" in cleaned_data.columns:
                    # 删除价格为负数或异常大的数据
                    invalid_price_rows = cleaned_data[
                        (cleaned_data["收盘"] < 0) | (cleaned_data["收盘"] > 100000)
                    ].shape[0]
                    if invalid_price_rows > 0:
                        logger.info(f"删除了{invalid_price_rows}行价格异常的数据")
                        cleaned_data = cleaned_data[
                            (cleaned_data["收盘"] >= 0)
                            & (cleaned_data["收盘"] <= 100000)
                        ]

                # 验证最高价、最低价、开盘价与收盘价的合理性
                if all(
                    col in cleaned_data.columns
                    for col in ["开盘", "最高", "最低", "收盘"]
                ):
                    # 检查最高价是否小于最低价等不合理情况
                    invalid_price_relation_rows = cleaned_data[
                        (cleaned_data["最高"] < cleaned_data["最低"])
                        | (cleaned_data["开盘"] > cleaned_data["最高"])
                        | (cleaned_data["开盘"] < cleaned_data["最低"])
                        | (cleaned_data["收盘"] > cleaned_data["最高"])
                        | (cleaned_data["收盘"] < cleaned_data["最低"])
                    ].shape[0]
                    if invalid_price_relation_rows > 0:
                        logger.info(
                            f"发现{invalid_price_relation_rows}行价格关系异常的数据"
                        )
                        # 对于价格关系异常的数据，我们可以尝试修复而不是直接删除
                        # 例如，将最高价设置为四个价格中的最大值
                        price_cols = ["开盘", "收盘", "最高", "最低"]
                        max_prices = cleaned_data[price_cols].max(axis=1)
                        min_prices = cleaned_data[price_cols].min(axis=1)

                        # 更新最高价和最低价
                        cleaned_data["最高"] = max_prices
                        cleaned_data["最低"] = min_prices
                        logger.info("已修复价格关系异常的数据")

            # 5. 数据排序
            if "日期" in cleaned_data.columns:
                cleaned_data = cleaned_data.sort_values("日期").reset_index(drop=True)
                logger.info("数据已按日期排序")

            logger.info(f"数据清洗完成，清洗后行数: {len(cleaned_data)}")
            return cleaned_data
        except Exception as e:
            logger.error(f"数据验证和清洗过程中发生错误: {e}")
            import traceback

            logger.error(traceback.format_exc())
            # 返回原始数据的副本以避免修改原始数据
            return data.copy()
