"""
# pylint: disable=no-member  # TODO: 实现缺失的 GPU/业务方法
Legacy AkShare Market Data Functions (兼容版本)

⚠️  注意: 这些是旧的同步版本的函数，保留用于向后兼容
📦 用途: 当不需要异步功能时，可以使用这些简化版本
🔄 迁移: 新代码应使用 AkshareMarketDataAdapter 中的 async 版本

创建日期: 2026-01-27
从: src/adapters/akshare/market_data.py (Lines 47-105)
"""

import logging
import pandas as pd
import akshare as ak

logger = logging.getLogger(__name__)


# ============================================================================
# Legacy Market Data Functions (同步版本，向后兼容)
# ============================================================================


def get_market_overview_sse() -> pd.DataFrame:
    """
    获取上海证券交易所市场总貌数据（同步版本）

    ⚠️ Legacy版本: 新代码应使用 AkshareMarketDataAdapter.get_market_overview_sse() (async)

    Returns:
        pd.DataFrame: 上海交易所市场总貌数据
            - project: 项目名称 (流通股本、总市值、平均市盈率等)
            - stock: 股票数据
            - kcb: 科创板数据
            - main_board: 主板数据
    """
    try:
        logger.info("[Akshare][Legacy] 开始获取上海证券交易所市场总貌数据...")

        # 使用重试装饰器包装API调用
        @_retry_api_call
        def _get_sse_summary():
            return ak.stock_sse_summary()

        # 调用akshare接口获取上海交易所市场总貌数据
        df = _get_sse_summary()

        logger.info("[Akshare][Legacy] 成功获取上海证券交易所市场总貌数据: %s 行", len(df))
        return df

    except Exception as e:
        logger.error("[Akshare][Legacy] 获取上海证券交易所市场总貌数据失败: %s", e)
        raise


def get_market_overview_szse(date: str = None) -> pd.DataFrame:
    """
    获取深圳证券交易所市场总貌数据（同步版本）

    ⚠️ Legacy版本: 新代码应使用 AkshareMarketDataAdapter.get_market_overview_szse() (async)

    Args:
        date: 日期字符串 (YYYY-MM-DD 格式)，默认为最新交易日

    Returns:
        pd.DataFrame: 深圳交易所市场总貌数据
    """
    try:
        logger.info("[Akshare][Legacy] 开始获取深圳证券交易所市场总貌数据: %s", date or "最新")

        # 使用重试装饰器包装API调用
        @_retry_api_call
        def _get_szse_summary():
            if date:
                return ak.stock_szse_summary(date=date)
            return ak.stock_szse_summary()

        # 调用akshare接口获取深圳交易所市场总貌数据
        df = _get_szse_summary()

        logger.info("[Akshare][Legacy] 成功获取深圳证券交易所市场总貌数据: %s 行", len(df))
        return df

    except Exception as e:
        logger.error("[Akshare][Legacy] 获取深圳证券交易所市场总貌数据失败: %s", e)
        raise


def get_szse_area_trading_summary(date: str) -> pd.DataFrame:
    """
    获取深圳证券交易所区域交易汇总表（同步版本）

    ⚠️ Legacy版本: 新代码应使用 AkshareMarketDataAdapter.get_szse_area_trading_summary() (async)

    Args:
        date: 日期字符串 (YYYY-MM-DD 格式)

    Returns:
        pd.DataFrame: 区域交易汇总数据
    """
    try:
        logger.info("[Akshare][Legacy] 开始获取深圳证券交易所区域交易汇总表: %s", date)

        # 使用重试装饰器包装API调用
        @_retry_api_call
        def _get_area_summary():
            return ak.stock_szse_area_summary(date=date)

        # 调用akshare接口获取区域交易汇总表
        df = _get_area_summary()

        logger.info("[Akshare][Legacy] 成功获取区域交易汇总表: %s 行", len(df))
        return df

    except Exception as e:
        logger.error("[Akshare][Legacy] 获取深圳证券交易所区域交易汇总表失败: %s", e)
        raise


def get_szse_sector_trading_summary(symbol: str, date: str) -> pd.DataFrame:
    """
    获取深圳证券交易所行业交易汇总表（同步版本）

    ⚠️ Legacy版本: 新代码应使用 AkshareMarketDataAdapter.get_szse_sector_trading_summary() (async)

    Args:
        symbol: 行业代码
        date: 日期字符串 (YYYY-MM-DD 格式)

    Returns:
        pd.DataFrame: 行业交易汇总数据
    """
    try:
        logger.info("[Akshare][Legacy] 开始获取深圳证券交易所行业交易汇总表: %s, %s", symbol, date)

        # 使用重试装饰器包装API调用
        @_retry_api_call
        def _get_sector_summary():
            return ak.stock_szse_sector_summary(symbol=symbol, date=date)

        # 调用akshare接口获取行业交易汇总表
        df = _get_sector_summary()

        logger.info("[Akshare][Legacy] 成功获取行业交易汇总表: %s 行", len(df))
        return df

    except Exception as e:
        logger.error("[Akshare][Legacy] 获取深圳证券交易所行业交易汇总表失败: %s", e)
        raise


def get_sse_daily_deal_summary(date: str) -> pd.DataFrame:
    """
    获取上海证券交易所每日成交汇总表（同步版本）

    ⚠️ Legacy版本: 新代码应使用 AkshareMarketDataAdapter.get_sse_daily_deal_summary() (async)

    Args:
        date: 日期字符串 (YYYY-MM-DD 格式)

    Returns:
        pd.DataFrame: 每日成交汇总数据
    """
    try:
        logger.info("[Akshare][Legacy] 开始获取上海证券交易所每日成交汇总表: %s", date)

        # 使用重试装饰器包装API调用
        @_retry_api_call
        def _get_daily_summary():
            # pylint: disable=no-member
            return ak.stock_sse_deal_summary(date=date)

        # 调用akshare接口获取每日成交汇总表
        df = _get_daily_summary()

        logger.info("[Akshare][Legacy] 成功获取每日成交汇总表: %s 行", len(df))
        return df

    except Exception as e:
        logger.error("[Akshare][Legacy] 获取上海证券交易所每日成交汇总表失败: %s", e)
        raise


# ============================================================================
# Helper Functions for Legacy Functions
# ============================================================================


def _retry_api_call(func, max_retries=3, delay=1):
    """API调用重试装饰器（同步版本）"""
    import asyncio
    from functools import wraps

    @wraps(func)
    async def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (2**attempt))  # 指数退避
                    continue
        raise last_exception

    return wrapper
