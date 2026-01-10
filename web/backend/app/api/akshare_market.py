"""
AkShare Market Data API

提供akshare数据源的市场总貌数据API端点，包括：
- 上海证券交易所市场总貌
- 深圳证券交易所市场总貌
- 深圳地区交易排序数据
- 深圳行业成交数据
- 上海交易所每日概况

集成优化特性：
- SmartCache: 智能缓存系统
- CircuitBreaker: 熔断器保护
- DataQualityValidator: 数据质量验证
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from app.core.security import User, get_current_user
from app.core.responses import create_success_response, create_error_response, ErrorCodes
from src.adapters.akshare.market_data import AkshareMarketDataAdapter

# 创建akshare市场数据适配器实例
akshare_market_adapter = AkshareMarketDataAdapter()

router = APIRouter(prefix="/api/akshare/market", tags=["akshare-market"])


# ============================================================================
# Pydantic Models
# ============================================================================

class MarketOverviewSSERequest(BaseModel):
    """上海交易所市场总貌请求"""
    pass  # 无参数


class MarketOverviewSZSERequest(BaseModel):
    """深圳交易所市场总貌请求"""
    date: str = Field(..., description="查询日期", example="2024-01-15")


class AreaTradingRequest(BaseModel):
    """深圳地区交易排序请求"""
    date: str = Field(..., description="查询日期", example="2024-01-15")


class SectorTradingRequest(BaseModel):
    """深圳行业成交数据请求"""
    symbol: str = Field(..., description="行业代码", example="BK0477")
    date: str = Field(..., description="查询日期", example="2024-01-15")


class SSEDailyDealRequest(BaseModel):
    """上海交易所每日概况请求"""
    date: str = Field(..., description="查询日期", example="2024-01-15")


# ============================================================================
# 上海证券交易所市场总貌
# ============================================================================

@router.get("/sse/overview", summary="获取上海证券交易所市场总貌")
async def get_sse_market_overview(
    current_user: User = Depends(get_current_user),
):
    """
    获取上海证券交易所市场总貌数据

    返回上证指数、成交金额、涨跌幅等市场整体概况数据
    """
    try:
        df = await akshare_market_adapter.get_market_overview_sse()

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                "No SSE market overview data found"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "timestamp": datetime.now().isoformat(),
            "source": "akshare",
            "exchange": "SSE"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get SSE market overview: {str(e)}"
        )


# ============================================================================
# 深圳证券交易所市场总貌
# ============================================================================

@router.get("/szse/overview", summary="获取深圳证券交易所市场总貌")
async def get_szse_market_overview(
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    """
    获取深圳证券交易所市场总貌数据

    返回深证成指、创业板指、成交金额等市场整体概况数据
    """
    try:
        df = await akshare_market_adapter.get_market_overview_szse(date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No SZSE market overview data found for date {date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date": date,
            "timestamp": datetime.now().isoformat(),
            "source": "akshare",
            "exchange": "SZSE"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get SZSE market overview for {date}: {str(e)}"
        )


# ============================================================================
# 深圳地区交易排序数据
# ============================================================================

@router.get("/szse/area-trading", summary="获取深圳地区交易排序数据")
async def get_szse_area_trading(
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    """
    获取深圳地区交易排序数据

    返回各地区成交金额排序、涨跌情况等数据
    """
    try:
        df = await akshare_market_adapter.get_szse_area_trading_summary(date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No SZSE area trading data found for date {date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date": date,
            "timestamp": datetime.now().isoformat(),
            "source": "akshare",
            "region": "SZSE"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get SZSE area trading data for {date}: {str(e)}"
        )


# ============================================================================
# 深圳行业成交数据
# ============================================================================

@router.get("/szse/sector-trading", summary="获取深圳行业成交数据")
async def get_szse_sector_trading(
    symbol: str = Query(..., description="行业代码", example="BK0477"),
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    """
    获取深圳行业成交数据

    返回指定行业的成交金额、涨跌幅等数据
    """
    try:
        df = await akshare_market_adapter.get_szse_sector_trading_summary(symbol, date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No SZSE sector trading data found for symbol {symbol} on date {date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "symbol": symbol,
            "date": date,
            "timestamp": datetime.now().isoformat(),
            "source": "akshare",
            "region": "SZSE"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get SZSE sector trading data for {symbol} on {date}: {str(e)}"
        )


# ============================================================================
# Phase 2: 个股信息数据API
# ============================================================================

@router.get("/stock/individual-info/em", summary="获取个股信息查询-东财")
async def get_stock_individual_info_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取个股信息查询-东财 (akshare.stock_individual_info_em)

    返回个股基本信息，包括公司概况、财务数据、行业分类等
    """
    try:
        info_dict = await akshare_market_adapter.get_stock_individual_info_em(symbol)

        if "error" in info_dict:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No individual info found for stock {symbol}: {info_dict.get('error')}"
            )

        result = {
            "symbol": symbol,
            "data": info_dict,
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock individual info for {symbol}: {str(e)}"
        )


@router.get("/stock/individual-info/xq", summary="获取个股信息查询-雪球")
async def get_stock_individual_info_xq(
    symbol: str = Query(..., description="股票代码", example="SZ000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取个股信息查询-雪球 (akshare.stock_individual_basic_info_xq)

    返回雪球平台的个股基本信息
    """
    try:
        info_dict = await akshare_market_adapter.get_stock_individual_basic_info_xq(symbol)

        if "error" in info_dict:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No individual info found for stock {symbol}: {info_dict.get('error')}"
            )

        result = {
            "symbol": symbol,
            "data": info_dict,
            "source": "akshare",
            "provider": "xq"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock individual info from Xueqiu for {symbol}: {str(e)}"
        )


@router.get("/stock/business-intro/ths", summary="获取主营介绍-同花顺")
async def get_stock_business_intro_ths(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取主营介绍-同花顺 (akshare.stock_zyjs_ths)

    返回同花顺的主营介绍信息
    """
    try:
        info_dict = await akshare_market_adapter.get_stock_zyjs_ths(symbol)

        if "error" in info_dict:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No business intro found for stock {symbol}: {info_dict.get('error')}"
            )

        result = {
            "symbol": symbol,
            "data": info_dict,
            "source": "akshare",
            "provider": "ths"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get business intro from THS for {symbol}: {str(e)}"
        )


@router.get("/stock/business-composition/em", summary="获取主营构成-东财")
async def get_stock_business_composition_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取主营构成-东财 (akshare.stock_zygc_em)

    返回东财的主营构成数据
    """
    try:
        df = await akshare_market_adapter.get_stock_zygc_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No business composition data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get business composition from EM for {symbol}: {str(e)}"
        )


@router.get("/stock/comment/em", summary="获取千股千评")
async def get_stock_comment_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取千股千评 (akshare.stock_comment_em)

    返回个股的分析师评级汇总数据
    """
    try:
        df = await akshare_market_adapter.get_stock_comment_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No comment data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock comment for {symbol}: {str(e)}"
        )


@router.get("/stock/comment-detail/em", summary="获取千股千评详情-机构评级")
async def get_stock_comment_detail_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取千股千评详情-机构评级 (akshare.stock_comment_detail_zlkp_jgcyd_em)

    返回个股的详细机构评级数据
    """
    try:
        df = await akshare_market_adapter.get_stock_comment_detail_zlkp_jgcyd_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No comment detail data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock comment detail for {symbol}: {str(e)}"
        )


@router.get("/stock/news/em", summary="获取个股新闻")
async def get_stock_news_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取个股新闻 (akshare.stock_news_em)

    返回个股相关的新闻数据
    """
    try:
        df = await akshare_market_adapter.get_stock_news_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No news data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock news for {symbol}: {str(e)}"
        )


@router.get("/stock/bid-ask/em", summary="获取行情报价-五档报价")
async def get_stock_bid_ask_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取行情报价-五档报价 (akshare.stock_bid_ask_em)

    返回个股的五档买卖报价数据
    """
    try:
        df = await akshare_market_adapter.get_stock_bid_ask_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No bid-ask data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

            return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get bid-ask data for {symbol}: {str(e)}"
        )


# ============================================================================
# Phase 3: 资金流向数据API
# ============================================================================

@router.get("/fund-flow/hsgt-summary", summary="获取沪深港通资金流向汇总")
async def get_hsgt_fund_flow_summary(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取沪深港通资金流向汇总 (akshare.stock_hsgt_fund_flow_summary_em)

    返回北向资金、南向资金的每日流向汇总数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_fund_flow_summary_em(start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No HSGT fund flow summary data found for date range {start_date} to {end_date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get HSGT fund flow summary: {str(e)}"
        )


@router.get("/fund-flow/hsgt-detail", summary="获取沪深港通资金流向明细")
async def get_hsgt_fund_flow_detail(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取沪深港通资金流向明细 (akshare.stock_hsgt_fund_flow_detail_em)

    返回沪深港通资金流向的详细分类数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_fund_flow_detail_em(start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No HSGT fund flow detail data found for date range {start_date} to {end_date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get HSGT fund flow detail: {str(e)}"
        )


@router.get("/fund-flow/north-daily", summary="获取北向资金每日统计")
async def get_north_fund_daily(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取北向资金每日统计 (akshare.stock_hsgt_north_net_flow_in_em)

    返回北向资金每日流入流出统计数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_north_net_flow_in_em(start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No north fund daily data found for date range {start_date} to {end_date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "fund_direction": "north",
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get north fund daily data: {str(e)}"
        )


@router.get("/fund-flow/south-daily", summary="获取南向资金每日统计")
async def get_south_fund_daily(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取南向资金每日统计 (akshare.stock_hsgt_south_net_flow_in_em)

    返回南向资金每日流入流出统计数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_south_net_flow_in_em(start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No south fund daily data found for date range {start_date} to {end_date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "fund_direction": "south",
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get south fund daily data: {str(e)}"
        )


@router.get("/fund-flow/north-stock/{symbol}", summary="获取北向资金个股统计")
async def get_north_fund_stock(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取北向资金个股统计 (akshare.stock_hsgt_north_acc_flow_in_em)

    返回指定股票的北向资金持股情况
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_north_acc_flow_in_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No north fund stock data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "fund_direction": "north",
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get north fund stock data for {symbol}: {str(e)}"
        )


@router.get("/fund-flow/south-stock/{symbol}", summary="获取南向资金个股统计")
async def get_south_fund_stock(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取南向资金个股统计 (akshare.stock_hsgt_south_acc_flow_in_em)

    返回指定股票的南向资金持股情况
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_south_acc_flow_in_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No south fund stock data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "fund_direction": "south",
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get south fund stock data for {symbol}: {str(e)}"
        )


@router.get("/fund-flow/hsgt-holdings/{symbol}", summary="获取沪深港通持股明细")
async def get_hsgt_holdings(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取沪深港通持股明细 (akshare.stock_hsgt_hold_stock_em)

    返回指定股票的沪深港通持股明细数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_hold_stock_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No HSGT holdings data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get HSGT holdings data for {symbol}: {str(e)}"
        )


@router.get("/fund-flow/big-deal", summary="获取资金流向大单统计")
async def get_fund_flow_big_deal(
    current_user: User = Depends(get_current_user),
):
    """
    获取资金流向大单统计 (akshare.stock_fund_flow_big_deal)

    返回全市场资金流向大单统计数据
    """
    try:
        df = await akshare_market_adapter.get_stock_fund_flow_big_deal()

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                "No fund flow big deal data found"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get fund flow big deal data: {str(e)}"
        )


@router.get("/chip-distribution/{symbol}", summary="获取筹码分布数据")
async def get_chip_distribution(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取筹码分布数据 (akshare.stock_cyq_em)

    返回指定股票的筹码分布分析数据
    """
    try:
        df = await akshare_market_adapter.get_stock_cyq_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No chip distribution data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

            return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get chip distribution data for {symbol}: {str(e)}"
        )


# ============================================================================
# Phase 4: 预测和分析数据API
# ============================================================================

@router.get("/forecast/profit/em/{symbol}", summary="获取盈利预测-东方财富")
async def get_profit_forecast_em(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取盈利预测-东方财富 (akshare.stock_profit_forecast_em)

    返回指定股票的东方财富盈利预测数据
    """
    try:
        df = await akshare_market_adapter.get_stock_profit_forecast_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No profit forecast data found for stock {symbol} from EM"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "forecast_type": "profit"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get profit forecast from EM for {symbol}: {str(e)}"
        )


@router.get("/forecast/profit/ths/{symbol}", summary="获取盈利预测-同花顺")
async def get_profit_forecast_ths(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取盈利预测-同花顺 (akshare.stock_profit_forecast_ths)

    返回指定股票的同花顺盈利预测数据
    """
    try:
        df = await akshare_market_adapter.get_stock_profit_forecast_ths(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No profit forecast data found for stock {symbol} from THS"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "ths",
            "forecast_type": "profit"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get profit forecast from THS for {symbol}: {str(e)}"
        )


@router.get("/technical/indicators/em/{symbol}", summary="获取技术指标数据")
async def get_technical_indicators_em(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取技术指标数据 (akshare.stock_technical_indicator_em)

    返回指定股票的技术指标数据（均线、MACD、RSI、KDJ、布林带等）
    """
    try:
        df = await akshare_market_adapter.get_stock_technical_indicator_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No technical indicator data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "indicator_types": ["ma", "macd", "rsi", "kdj", "boll"]
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get technical indicators for {symbol}: {str(e)}"
        )


@router.get("/market/account-statistics", summary="获取股票账户统计月度")
async def get_account_statistics_em(
    date: str = Query(..., description="查询月份", example="2024-01"),
    current_user: User = Depends(get_current_user),
):
    """
    获取股票账户统计月度 (akshare.stock_account_statistics_em)

    返回指定月份的股票账户统计数据
    """
    try:
        df = await akshare_market_adapter.get_stock_account_statistics_em(date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No account statistics data found for month {date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "query_month": date,
            "source": "akshare",
            "provider": "em",
            "statistics_type": "account"
        }

            return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get account statistics for {date}: {str(e)}"
        )


# ============================================================================
# Phase 5: 板块和行业数据API
# ============================================================================

@router.get("/board/concept/cons/{symbol}", summary="获取概念板块成分股")
async def get_concept_board_constituents(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取概念板块成分股 (akshare.stock_board_concept_cons_em)

    返回指定概念板块的成分股列表
    """
    try:
        df = await akshare_market_adapter.get_stock_board_concept_cons_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No concept board constituents found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "board_type": "concept"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get concept board constituents for {symbol}: {str(e)}"
        )


@router.get("/board/concept/history/{symbol}", summary="获取概念板块行情")
async def get_concept_board_history(
    symbol: str,
    start_date: str = Query(None, description="开始日期", example="2024-01-01"),
    end_date: str = Query(None, description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取概念板块行情 (akshare.stock_board_concept_hist_em)

    返回指定概念板块的历史行情数据
    """
    try:
        df = await akshare_market_adapter.get_stock_board_concept_hist_em(symbol, start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No concept board history data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date} if start_date and end_date else None,
            "source": "akshare",
            "provider": "em",
            "board_type": "concept",
            "data_type": "daily"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get concept board history for {symbol}: {str(e)}"
        )


@router.get("/board/concept/minute/{symbol}", summary="获取概念板块分钟行情")
async def get_concept_board_minute(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取概念板块历史行情-分钟 (akshare.stock_board_concept_hist_min_em)

    返回指定概念板块的分钟行情数据
    """
    try:
        df = await akshare_market_adapter.get_stock_board_concept_hist_min_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No concept board minute data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "board_type": "concept",
            "data_type": "minute"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get concept board minute data for {symbol}: {str(e)}"
        )


@router.get("/board/industry/cons/{symbol}", summary="获取行业板块成分股")
async def get_industry_board_constituents(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取行业板块成分股 (akshare.stock_board_industry_cons_em)

    返回指定行业板块的成分股列表
    """
    try:
        df = await akshare_market_adapter.get_stock_board_industry_cons_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No industry board constituents found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "board_type": "industry"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get industry board constituents for {symbol}: {str(e)}"
        )


@router.get("/board/industry/history/{symbol}", summary="获取行业板块行情")
async def get_industry_board_history(
    symbol: str,
    start_date: str = Query(None, description="开始日期", example="2024-01-01"),
    end_date: str = Query(None, description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取行业板块行情 (akshare.stock_board_industry_hist_em)

    返回指定行业板块的历史行情数据
    """
    try:
        df = await akshare_market_adapter.get_stock_board_industry_hist_em(symbol, start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No industry board history data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date} if start_date and end_date else None,
            "source": "akshare",
            "provider": "em",
            "board_type": "industry",
            "data_type": "daily"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get industry board history for {symbol}: {str(e)}"
        )


@router.get("/board/industry/minute/{symbol}", summary="获取行业板块分钟行情")
async def get_industry_board_minute(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取行业板块历史行情-分钟 (akshare.stock_board_industry_hist_min_em)

    返回指定行业板块的分钟行情数据
    """
    try:
        df = await akshare_market_adapter.get_stock_board_industry_hist_min_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No industry board minute data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "board_type": "industry",
            "data_type": "minute"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get industry board minute data for {symbol}: {str(e)}"
        )


@router.get("/sector/hot-ranking", summary="获取热门行业排行")
async def get_sector_hot_ranking(
    current_user: User = Depends(get_current_user),
):
    """
    获取热门行业排行 (akshare.stock_sector_spot_em)

    返回全市场热门行业的排行数据
    """
    try:
        df = await akshare_market_adapter.get_stock_sector_spot_em()

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                "No sector hot ranking data found"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "ranking_type": "hot_sector"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get sector hot ranking: {str(e)}"
        )


@router.get("/sector/fund-flow-ranking", summary="获取行业资金流向")
async def get_sector_fund_flow_ranking(
    current_user: User = Depends(get_current_user),
):
    """
    获取行业资金流向 (akshare.stock_sector_fund_flow_rank_em)

    返回全市场行业资金流向排行数据
    """
    try:
        df = await akshare_market_adapter.get_stock_sector_fund_flow_rank_em()

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                "No sector fund flow ranking data found"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "ranking_type": "fund_flow"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get sector fund flow ranking: {str(e)}"
        )


# ============================================================================
# 上海交易所每日概况
# ============================================================================

@router.get("/sse/daily-deal", summary="获取上海交易所每日概况")
async def get_sse_daily_deal(
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    """
    获取上海交易所每日概况数据

    返回上证指数每日成交概况、涨跌家数等数据
    """
    try:
        df = await akshare_market_adapter.get_sse_daily_deal_summary(date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No SSE daily deal data found for date {date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date": date,
            "timestamp": datetime.now().isoformat(),
            "source": "akshare",
            "exchange": "SSE"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get SSE daily deal data for {date}: {str(e)}"
        )</content>
<parameter name="filePath">web/backend/app/api/akshare_market.py