"""资金流向路由 (Fund Flow)"""

import asyncio

from fastapi import APIRouter, Query

from app.core.config import settings
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from src.services.openstock import OpenStockClient, DataCategory

from .base import akshare_market_adapter  # OPENSTOCK_GAP: hsgt-detail / 南向 / big-deal


router = APIRouter()

# 模块级 client 单例(懒初始化)
_client: OpenStockClient | None = None


def _get_client() -> OpenStockClient:
    global _client
    if _client is None:
        _client = OpenStockClient(
            base_url=settings.openstock_base_url,
            api_key=settings.openstock_api_key,
        )
    return _client


@router.get("/fund-flow/hsgt-summary", summary="获取沪深港通资金流向汇总")
async def get_hsgt_fund_flow_summary(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
):
    """获取沪深港通资金流向汇总 (OpenStock NORTHBOUND_FLOW)

    返回北向资金、南向资金的每日流向汇总数据.
    OPENSTOCK_NOTE: OpenStock NORTHBOUND_FLOW 返回当日汇总, 不按日期过滤; start_date/end_date 透传但暂不生效.
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.NORTHBOUND_FLOW,
            {"start_date": start_date, "end_date": end_date},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No HSGT fund flow summary data found for date range {start_date} to {end_date}",
            )

        result = {
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "date_range": {"start": start_date, "end": end_date},
            "source": "openstock",
            "provider": "openstock_gateway",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get HSGT fund flow summary: {e!s}")


@router.get("/fund-flow/hsgt-detail", summary="获取沪深港通资金流向明细")
async def get_hsgt_fund_flow_detail(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
):
    """获取沪深港通资金流向明细 (akshare.stock_hsgt_fund_flow_detail_em)

    OPENSTOCK_GAP: OpenStock NORTHBOUND_FLOW 仅提供当日汇总, 无明细分类. 保留原 adapter 调用.
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_fund_flow_detail_em(start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No HSGT fund flow detail data found for date range {start_date} to {end_date}",
            )

        result = {
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "source": "akshare",
            "provider": "em",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get HSGT fund flow detail: {e!s}")


@router.get("/fund-flow/north-daily", summary="获取北向资金每日统计")
async def get_north_fund_daily(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
):
    """获取北向资金每日统计 (OpenStock NORTHBOUND_FLOW)

    返回北向资金每日流入流出统计数据.
    OPENSTOCK_NOTE: OpenStock NORTHBOUND_FLOW 返回当日汇总, 不按日期过滤; start_date/end_date 透传但暂不生效.
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.NORTHBOUND_FLOW,
            {"start_date": start_date, "end_date": end_date},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No north fund daily data found for date range {start_date} to {end_date}",
            )

        result = {
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "date_range": {"start": start_date, "end": end_date},
            "fund_direction": "north",
            "source": "openstock",
            "provider": "openstock_gateway",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get north fund daily data: {e!s}")


@router.get("/fund-flow/south-daily", summary="获取南向资金每日统计")
async def get_south_fund_daily(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
):
    """获取南向资金每日统计 (akshare.stock_hsgt_south_net_flow_in_em)

    OPENSTOCK_GAP: OpenStock NORTHBOUND_FLOW 仅覆盖沪股通/深股通, 无南向(港股通)数据. 保留原 adapter 调用.
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_south_net_flow_in_em(start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No south fund daily data found for date range {start_date} to {end_date}",
            )

        result = {
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "fund_direction": "south",
            "source": "akshare",
            "provider": "em",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get south fund daily data: {e!s}")


@router.get("/fund-flow/north-stock/{symbol}", summary="获取北向资金个股统计")
async def get_north_fund_stock(
    symbol: str,
):
    """获取北向资金个股统计 (OpenStock NORTHBOUND_HOLDING)

    返回指定股票的北向资金持股情况
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.NORTHBOUND_HOLDING,
            {"symbol": symbol},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No north fund stock data found for symbol {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "fund_direction": "north",
            "source": "openstock",
            "provider": "openstock_gateway",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get north fund stock data for {symbol}: {e!s}",
        )


@router.get("/fund-flow/south-stock/{symbol}", summary="获取南向资金个股统计")
async def get_south_fund_stock(
    symbol: str,
):
    """获取南向资金个股统计 (akshare.stock_hsgt_south_acc_flow_in_em)

    OPENSTOCK_GAP: OpenStock NORTHBOUND_HOLDING 仅覆盖北向持股, 无南向个股数据. 保留原 adapter 调用.
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_south_acc_flow_in_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No south fund stock data found for symbol {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "fund_direction": "south",
            "source": "akshare",
            "provider": "em",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get south fund stock data for {symbol}: {e!s}",
        )


@router.get("/fund-flow/hsgt-holdings/{symbol}", summary="获取沪深港通持股明细")
async def get_hsgt_holdings(
    symbol: str,
):
    """获取沪深港通持股明细 (OpenStock NORTHBOUND_HOLDING)

    返回指定股票的沪深港通持股明细数据
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.NORTHBOUND_HOLDING,
            {"symbol": symbol},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No HSGT holdings data found for symbol {symbol}")

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get HSGT holdings data for {symbol}: {e!s}",
        )


@router.get("/fund-flow/big-deal", summary="获取资金流向大单统计")
async def get_fund_flow_big_deal():
    """获取资金流向大单统计 (akshare.stock_fund_flow_big_deal)

    OPENSTOCK_GAP: OpenStock FUND_FLOW 需按单只 symbol 拉取, 无全市场大单统计. 保留原 adapter 调用.
    """
    try:
        df = await akshare_market_adapter.get_stock_fund_flow_big_deal()

        if df.empty:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No fund flow big deal data found")

        result = {
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, f"Failed to get fund flow big deal data: {e!s}")
