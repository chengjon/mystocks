"""
指数日线数据获取方法
"""

from typing import Dict
import pandas as pd
from loguru import logger
import akshare as ak

from src.utils import symbol_utils, date_utils


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
    logger.info("尝试获取指数 %s 的日线数据...", index_code)

    # 参数验证
    if not index_code:
        logger.error("指数代码不能为空")
        return pd.DataFrame()

    # 使用symbol_utils标准化股票代码
    normalized_index_code = symbol_utils.normalize_stock_code(index_code)
    if not normalized_index_code:
        logger.error("无效的指数代码: %s", index_code)
        return pd.DataFrame()

    # 使用date_utils标准化日期
    try:
        normalized_start_date = date_utils.normalize_date(start_date) if start_date else None
        normalized_end_date = date_utils.normalize_date(end_date) if end_date else None
    except ValueError as e:
        logger.error("日期格式错误: %s", e)
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

        logger.info("使用格式化代码: %s", formatted_code)

        # 获取历史行情数据
        logger.info("请求参数: code=%s, beg=%s, end=%s", formatted_code, normalized_start_date, normalized_end_date)
        if normalized_start_date and normalized_end_date:
            data = self.ef.stock.get_quote_history(formatted_code, beg=normalized_start_date, end=normalized_end_date)
        elif normalized_start_date:
            data = self.ef.stock.get_quote_history(formatted_code, beg=normalized_start_date)
        elif normalized_end_date:
            data = self.ef.stock.get_quote_history(formatted_code, end=normalized_end_date)
        else:
            data = self.ef.stock.get_quote_history(formatted_code)

        logger.info("efinance返回数据类型: %s", type(data))
        if isinstance(data, pd.DataFrame):
            logger.info("efinance返回数据行数: %s", len(data))

        # 如果使用日期参数没有获取到数据，则获取全部数据并进行过滤
        if (normalized_start_date or normalized_end_date) and (
            data is None or (isinstance(data, pd.DataFrame) and data.empty)
        ):
            logger.warning("使用日期参数未获取到数据，尝试获取全部数据并过滤...")
            data = self.ef.stock.get_quote_history(formatted_code)
            if data is not None and isinstance(data, pd.DataFrame) and not data.empty:
                # 过滤日期范围
                if normalized_start_date:
                    data = data[data["日期"] >= normalized_start_date]
                if normalized_end_date:
                    data = data[data["日期"] <= normalized_end_date]

        if data is not None and isinstance(data, pd.DataFrame) and not data.empty:
            logger.info("成功获取指数 %s 的日线数据，共 %s 条记录", index_code, len(data))
            # 验证和清洗数据
            cleaned_data = self._validate_and_clean_data(data, "index")
            return cleaned_data
        else:
            logger.warning("未获取到指数 %s 的日线数据", index_code)
            return pd.DataFrame()
    except Exception as e:
        logger.error("获取指数 %s 日线数据时发生错误: %s", index_code, str(e))
        import traceback

        logger.error(traceback.format_exc())
        return pd.DataFrame()


def get_stock_basic(self, symbol: str) -> Dict:
    """获取股票基本信息"""
    try:
        return ak.stock_individual_info_em(symbol=symbol)
    except Exception as e:
        logger.error("获取股票 %s 基本信息失败: %s", symbol, str(e))
        return {}
