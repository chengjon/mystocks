"""
WebData Data Source Adapter
Webdata 数据源适配器

将 webdata 接口（新浪财经、腾讯股票）集成到 DataSourceManagerV2 系统中。
"""

import logging
import sys
from typing import Dict, List

import pandas as pd

sys.path.insert(0, "/opt/iflow/webdata")

from stock_api_functions import (
    get_sina_hfq_data,
    get_sina_keyword_search,
    get_sina_kline_data,
    get_sina_price_history,
    get_sina_qfq_data,
    get_tencent_5day_minute_chart,
    get_tencent_daily_kline,
    get_tencent_minute_chart,
    get_tencent_monthly_kline,
    get_tencent_realtime_volume,
    get_tencent_weekly_kline,
    get_tencent_yearly_daily_kline,
    parse_sina_kline_data,
)

logger = logging.getLogger(__name__)


def _parse_tencent_kline_data(data: str) -> List[Dict]:
    """
    解析腾讯K线数据（处理转义字符）

    Args:
        data: 原始JS格式数据

    Returns:
        标准格式的K线数据列表
    """
    result = []
    # 处理转义字符：将 \n\\ 转换为实际换行
    data = data.replace("\\n\\", "\n").replace("\\n", "\n")

    # 提取数据部分
    lines = data.strip().split("\n")
    for line in lines:
        # 跳过头部行
        if (
            not line
            or line.startswith("latest_")
            or line.startswith("num:")
            or line.startswith("daily_data")
            or line.startswith("monthly_data")
            or line.startswith("weekly_data")
        ):
            continue

        # 每行包含：日期 开盘价 最高价 最低价 收盘价 成交量
        parts = line.split()
        if len(parts) >= 6:
            try:
                result.append(
                    {
                        "date": parts[0],
                        "open": float(parts[1]),
                        "high": float(parts[2]),
                        "low": float(parts[3]),
                        "close": float(parts[4]),
                        "volume": int(parts[5]),
                    }
                )
            except (ValueError, IndexError):
                continue
    return result


def _normalize_symbol(symbol: str) -> str:
    """统一股票代码格式"""
    symbol = str(symbol).strip().lower()
    if symbol.startswith("sz") or symbol.startswith("sh"):
        return symbol
    elif symbol.isdigit() and len(symbol) == 6:
        if symbol.startswith(("0", "3")):
            return "sz" + symbol
        else:
            return "sh" + symbol
    return symbol


class WebDataAdapter:
    """
    WebData 数据源适配器

    提供与 DataSourceManagerV2 兼容的接口。
    数据来源: 新浪财经、腾讯股票
    """

    def __init__(self):
        pass

    def get_sina_minute_kline(self, symbol: str, scale: int = 60, datalen: int = 1023) -> pd.DataFrame:
        """
        获取新浪K线数据（分钟级别）

        Args:
            symbol: 股票代码 (如 sz000510, sh600000)
            scale: 周期 (5, 10, 30, 60分钟)
            datalen: 数据长度 (最多1023)

        Returns:
            DataFrame with columns: day, open, high, low, close, volume
        """
        symbol = _normalize_symbol(symbol)
        data = get_sina_kline_data(symbol, scale, datalen)

        if data:
            df = pd.DataFrame(parse_sina_kline_data(data))
            if not df.empty:
                df["datetime"] = pd.to_datetime(df["datetime"])
            return df
        return pd.DataFrame()

    def get_sina_qfq_data(self, symbol: str, date: str = None) -> Dict:
        """
        获取新浪前复权数据

        Args:
            symbol: 股票代码 (如 sz002095)
            date: 日期 (格式: YYYY-MM-DD)

        Returns:
            前复权数据字典
        """
        symbol = _normalize_symbol(symbol)
        return get_sina_qfq_data(symbol, date) or {}

    def get_sina_hfq_data(self, symbol: str, date: str = None) -> Dict:
        """
        获取新浪后复权数据

        Args:
            symbol: 股票代码 (如 sz002095)
            date: 日期 (格式: YYYY-MM-DD)

        Returns:
            后复权数据字典
        """
        symbol = _normalize_symbol(symbol)
        return get_sina_hfq_data(symbol, date) or {}

    def get_sina_price_distribution(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """
        获取新浪分价表数据

        Args:
            symbol: 股票代码 (如 sz000510)
            start_date: 开始日期 (格式: YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYY-MM-DD)

        Returns:
            分价数据列表，每个元素包含 price, volume, percentage
        """
        symbol = _normalize_symbol(symbol)
        html_data = get_sina_price_history(symbol, start_date, end_date)
        if html_data:
            from parse_price_history import get_and_parse_price_history

            return get_and_parse_price_history(symbol, start_date, end_date)
        return []

    def get_sina_keyword_search(self, keyword: str) -> str:
        """
        新浪关键词查询股票

        Args:
            keyword: 搜索关键词

        Returns:
            搜索结果（JS格式字符串）
        """
        return get_sina_keyword_search(keyword) or ""

    def get_tencent_daily_kline(self, symbol: str) -> pd.DataFrame:
        """
        获取腾讯日K线数据

        Args:
            symbol: 股票代码 (如 sz000002)

        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        symbol = _normalize_symbol(symbol)
        raw_data = get_tencent_daily_kline(symbol)

        if raw_data:
            data = _parse_tencent_kline_data(raw_data)
            if data:
                df = pd.DataFrame(data)
                return df
        return pd.DataFrame()

    def get_tencent_minute_chart(self, symbol: str) -> str:
        """
        获取腾讯分时图数据

        Args:
            symbol: 股票代码 (如 sz000001)

        Returns:
            分时图数据（JS格式字符串）
        """
        symbol = _normalize_symbol(symbol)
        return get_tencent_minute_chart(symbol) or ""

    def get_tencent_5day_minute_chart(self, symbol: str) -> str:
        """
        获取腾讯五天分时图数据

        Args:
            symbol: 股票代码 (如 sz000002)

        Returns:
            五天分时图数据（JS格式字符串）
        """
        symbol = _normalize_symbol(symbol)
        return get_tencent_5day_minute_chart(symbol) or ""

    def get_tencent_yearly_daily_kline(self, symbol: str, year: int) -> pd.DataFrame:
        """
        获取腾讯指定年份的日K线数据

        Args:
            symbol: 股票代码 (如 sz000750)
            year: 年份 (如 17 代表2017年)

        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        symbol = _normalize_symbol(symbol)
        raw_data = get_tencent_yearly_daily_kline(symbol, year)

        if raw_data:
            data = _parse_tencent_kline_data(raw_data)
            if data:
                df = pd.DataFrame(data)
                return df
        return pd.DataFrame()

    def get_tencent_weekly_kline(self, symbol: str) -> pd.DataFrame:
        """
        获取腾讯周K线数据

        Args:
            symbol: 股票代码 (如 sz000002)

        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        symbol = _normalize_symbol(symbol)
        raw_data = get_tencent_weekly_kline(symbol)

        if raw_data:
            data = _parse_tencent_kline_data(raw_data)
            if data:
                df = pd.DataFrame(data)
                return df
        return pd.DataFrame()

    def get_tencent_monthly_kline(self, symbol: str) -> pd.DataFrame:
        """
        获取腾讯月K线数据

        Args:
            symbol: 股票代码 (如 sz000002)

        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        symbol = _normalize_symbol(symbol)
        raw_data = get_tencent_monthly_kline(symbol)

        if raw_data:
            data = _parse_tencent_kline_data(raw_data)
            if data:
                df = pd.DataFrame(data)
                return df
        return pd.DataFrame()

    def get_tencent_realtime_volume(self, symbol: str, page: int = 1) -> str:
        """
        获取腾讯实时成交量明细

        Args:
            symbol: 股票代码 (如 sz002451)
            page: 页码

        Returns:
            实时成交量明细数据（JS格式字符串）
        """
        symbol = _normalize_symbol(symbol)
        return get_tencent_realtime_volume(symbol, page) or ""
