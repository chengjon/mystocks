"""
资金流向路由 (Fund Flow)
"""
import os

from fastapi import APIRouter, Depends, Path, Query
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from app.services.openstock_client import (
    OpenStockClient,
    OpenStockClientConfig,
    OpenStockClientError,
)
from .base import akshare_market_adapter

router = APIRouter()

DEFAULT_OPENSTOCK_BASE_URL = "http://192.168.123.104:8040"


def _build_openstock_client() -> OpenStockClient:
    """Build an OpenStockClient from environment.

    Mirrors `market_data_request.get_openstock_market_client` so endpoint-layer
    switches share the same configuration source.
    """
    base_url = (
        os.getenv("OPENSTOCK_BASE_URL")
        or os.getenv("OPENSTOCK_API_BASE_URL")
        or DEFAULT_OPENSTOCK_BASE_URL
    ).strip()
    try:
        timeout_seconds = float(os.getenv("OPENSTOCK_TIMEOUT_SECONDS", "5.0"))
    except ValueError:
        timeout_seconds = 5.0
    api_key = os.getenv("OPENSTOCK_API_KEY", "").strip() or None
    return OpenStockClient(
        OpenStockClientConfig(
            base_url=base_url or DEFAULT_OPENSTOCK_BASE_URL,
            timeout_seconds=timeout_seconds,
            api_key=api_key,
        )
    )


def _translate_northbound_flow_row(record: dict) -> dict:
    """Translate OpenStock NORTHBOUND_FLOW row → frontend truth-source contract.

    Truth source: `web/frontend/src/views/data/fundFlowPageData.ts` consumes
    `板块 / 资金方向 / 成交净买额 / 指数涨跌幅 / 交易日`.
    """
    return {
        "板块": record.get("board_name"),
        "资金方向": record.get("fund_direction"),
        "成交净买额": record.get("net_buy_amount"),
        "指数涨跌幅": record.get("index_change_pct"),
        "交易日": record.get("trade_date"),
        # Preserved extra fields for downstream observability (not consumed by frontend):
        "同期上涨家数": record.get("up_count"),
        "同期下跌家数": record.get("down_count"),
        "同期平盘家数": record.get("flat_count"),
        "关联指数": record.get("related_index"),
        "资金净流入": record.get("fund_net_inflow"),
    }


def _translate_northbound_holding_row(record: dict, symbol: str) -> dict:
    """Translate OpenStock NORTHBOUND_HOLDING row → frontend-friendly columns.

    Frontend FundFlow.vue currently does not consume north-stock; this contract
    mirrors the akshare predecessor (Chinese wide-table) for parity with future
    consumer code and preserves OpenStock richer fields.
    """
    return {
        "symbol": symbol,
        "持股日期": record.get("trade_date"),
        "收盘价": record.get("close"),
        "涨跌幅": record.get("change_pct"),
        "持股数量": record.get("holding_shares"),
        "持股市值": record.get("holding_market_cap"),
        "持股比例": record.get("holding_shares_ratio"),
        "增持数量": record.get("add_shares"),
        "增持金额": record.get("add_amount"),
        "持股市值变化": record.get("holding_market_cap_change"),
    }


def _success_response_spec(description: str, example: dict) -> dict[int, dict]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


def _error_response_spec(status_code: int, description: str, example: dict) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


NORTH_FUND_STOCK_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定股票的北向资金持股数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No north fund stock data found for symbol 600519"},
    ),
    **_error_response_spec(
        500,
        "北向资金个股统计查询失败",
        {"success": False, "error_code": "INTERNAL_SERVER_ERROR", "message": "Failed to get north fund stock data for 600519"},
    ),
    **_success_response_spec(
        "北向资金个股统计数据",
        {
            "success": True,
            "data": {
                "symbol": "600519",
                "data": [
                    {
                        "symbol": "600519",
                        "持股日期": "2024-01-15",
                        "持股数量": 1234567,
                        "持股市值": 2345000000.0,
                        "持股比例": 5.87,
                        "增持数量": -18873.0,
                        "增持金额": -7153938.99,
                    }
                ],
                "count": 1,
                "columns": ["持股日期", "持股数量", "持股市值", "持股比例", "增持数量", "增持金额"],
                "fund_direction": "north",
                "source": "openstock",
                "provider": "akshare",
            },
        },
    ),
}

SOUTH_FUND_STOCK_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定股票的南向资金持股数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No south fund stock data found for symbol 00700"},
    ),
    **_error_response_spec(
        500,
        "南向资金个股统计查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get south fund stock data for 00700"},
    ),
    **_success_response_spec(
        "南向资金个股统计数据",
        {
            "success": True,
            "data": {
                "symbol": "00700",
                "data": [{"持股日期": "2024-01-15", "持股数量": 2234567, "持股市值": 3345000000.0}],
                "count": 1,
                "columns": ["持股日期", "持股数量", "持股市值"],
                "fund_direction": "south",
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

HSGT_HOLDINGS_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定股票的沪深港通持股明细",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No HSGT holdings data found for symbol 600519"},
    ),
    **_error_response_spec(
        500,
        "沪深港通持股明细查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get HSGT holdings data for 600519"},
    ),
    **_success_response_spec(
        "沪深港通持股明细数据",
        {
            "success": True,
            "data": {
                "symbol": "600519",
                "data": [{"日期": "2024-01-15", "机构名称": "沪股通", "持股数量": 1234567}],
                "count": 1,
                "columns": ["日期", "机构名称", "持股数量"],
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

FUND_FLOW_BIG_DEAL_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到资金流向大单统计数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No fund flow big deal data found"},
    ),
    **_error_response_spec(
        500,
        "资金流向大单统计查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get fund flow big deal data"},
    ),
    **_success_response_spec(
        "资金流向大单统计数据",
        {
            "success": True,
            "data": {
                "data": [{"代码": "600519", "名称": "贵州茅台", "大单净流入": 128000000.0}],
                "count": 1,
                "columns": ["代码", "名称", "大单净流入"],
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

HSGT_SUMMARY_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到沪深港通资金流向汇总数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No HSGT fund flow summary data found for date range 2024-01-01 to 2024-01-05"},
    ),
    **_error_response_spec(
        500,
        "沪深港通资金流向汇总查询失败",
        {"success": False, "error_code": "INTERNAL_SERVER_ERROR", "message": "Failed to get HSGT fund flow summary"},
    ),
    **_success_response_spec(
        "沪深港通资金流向汇总数据",
        {
            "success": True,
            "data": {
                "data": [
                    {
                        "板块": "沪股通",
                        "资金方向": "北向",
                        "成交净买额": 1234567.89,
                        "指数涨跌幅": 0.45,
                        "交易日": "2024-01-15",
                        "关联指数": "上证指数",
                    }
                ],
                "count": 1,
                "columns": ["板块", "资金方向", "成交净买额", "指数涨跌幅", "交易日"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-05"},
                "source": "openstock",
                "provider": "akshare",
            },
        },
    ),
}

HSGT_DETAIL_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到沪深港通资金流向明细数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No HSGT fund flow detail data found for date range 2024-01-01 to 2024-01-05"},
    ),
    **_error_response_spec(
        500,
        "沪深港通资金流向明细查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get HSGT fund flow detail"},
    ),
    **_success_response_spec(
        "沪深港通资金流向明细数据",
        {
            "success": True,
            "data": {
                "data": [{"日期": "2024-01-15", "市场": "沪股通", "净流入": 12.6}],
                "count": 1,
                "columns": ["日期", "市场", "净流入"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-05"},
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

NORTH_DAILY_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到北向资金每日统计数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No north fund daily data found for date range 2024-01-01 to 2024-01-05"},
    ),
    **_error_response_spec(
        500,
        "北向资金每日统计查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get north fund daily data"},
    ),
    **_success_response_spec(
        "北向资金每日统计数据",
        {
            "success": True,
            "data": {
                "data": [{"日期": "2024-01-15", "净流入额": 18.2}],
                "count": 1,
                "columns": ["日期", "净流入额"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-05"},
                "fund_direction": "north",
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

SOUTH_DAILY_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到南向资金每日统计数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No south fund daily data found for date range 2024-01-01 to 2024-01-05"},
    ),
    **_error_response_spec(
        500,
        "南向资金每日统计查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get south fund daily data"},
    ),
    **_success_response_spec(
        "南向资金每日统计数据",
        {
            "success": True,
            "data": {
                "data": [{"日期": "2024-01-15", "净流入额": 6.4}],
                "count": 1,
                "columns": ["日期", "净流入额"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-05"},
                "fund_direction": "south",
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

@router.get("/fund-flow/hsgt-summary", summary="获取沪深港通资金流向汇总", responses=HSGT_SUMMARY_RESPONSES)
async def get_hsgt_fund_flow_summary(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取沪深港通资金流向汇总 (OpenStock NORTHBOUND_FLOW).

    Phase 1.1 batch 2 (B4.014, 2026-06-29): 切换至 OpenStock. 字段契约为
    前端真相源 `fundFlowPageData.ts` 期望的中文宽表 (`板块/资金方向/成交净买额/
    指数涨跌幅/交易日`), 由 OpenStock 标准字段经 `board_name/fund_direction/
    net_buy_amount/index_change_pct/trade_date` 翻译而来.
    """
    try:
        client = _build_openstock_client()
        try:
            result_obj = await client.fetch(
                "NORTHBOUND_FLOW",
                params={"start_date": start_date, "end_date": end_date},
            )
        finally:
            await client.aclose()

        records = result_obj.data if isinstance(result_obj.data, list) else []
        if not records:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No HSGT fund flow summary data found for date range {start_date} to {end_date}"
            )

        translated = [_translate_northbound_flow_row(r) for r in records if isinstance(r, dict)]
        result = {
            "data": translated,
            "count": len(translated),
            "columns": ["板块", "资金方向", "成交净买额", "指数涨跌幅", "交易日"],
            "date_range": {"start": start_date, "end": end_date},
            "source": "openstock",
            "provider": "akshare",
        }

        return create_success_response(result)

    except OpenStockClientError as e:
        return create_error_response(
            ErrorCodes.INTERNAL_SERVER_ERROR,
            f"OpenStock NORTHBOUND_FLOW fetch failed: {str(e)}"
        )
    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_SERVER_ERROR,
            f"Failed to get HSGT fund flow summary: {str(e)}"
        )


@router.get("/fund-flow/hsgt-detail", summary="获取沪深港通资金流向明细", responses=HSGT_DETAIL_RESPONSES)
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


@router.get("/fund-flow/north-daily", summary="获取北向资金每日统计", responses=NORTH_DAILY_RESPONSES)
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


@router.get("/fund-flow/south-daily", summary="获取南向资金每日统计", responses=SOUTH_DAILY_RESPONSES)
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


@router.get(
    "/fund-flow/north-stock/{symbol}",
    summary="获取北向资金个股统计",
    description="按股票代码查询北向资金持股与持仓变化，用于跟踪 A 股北向资金偏好和持股结构。",
    responses=NORTH_FUND_STOCK_RESPONSES,
)
async def get_north_fund_stock(
    symbol: str = Path(..., description="股票代码，例如 600519"),
    current_user: User = Depends(get_current_user),
):
    """
    获取北向资金个股统计 (OpenStock NORTHBOUND_HOLDING).

    Phase 1.1 batch 2 (B4.014, 2026-06-29): 切换至 OpenStock. 之前因 akshare
    `stock_hsgt_north_acc_flow_in_em` 在 akshare 1.18.60 移除而返回 501; 现在
    由 OpenStock `NORTHBOUND_HOLDING` 类别接管. 返回中文宽表契约, 与 akshare
    时代字段名保持兼容.
    """
    try:
        client = _build_openstock_client()
        try:
            result_obj = await client.fetch(
                "NORTHBOUND_HOLDING",
                params={"symbol": symbol},
            )
        finally:
            await client.aclose()

        records = result_obj.data if isinstance(result_obj.data, list) else []
        if not records:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No north fund stock data found for symbol {symbol}"
            )

        translated = [_translate_northbound_holding_row(r, symbol) for r in records if isinstance(r, dict)]
        result = {
            "symbol": symbol,
            "data": translated,
            "count": len(translated),
            "columns": ["持股日期", "持股数量", "持股市值", "持股比例", "增持数量", "增持金额"],
            "fund_direction": "north",
            "source": "openstock",
            "provider": "akshare",
        }

        return create_success_response(result)

    except OpenStockClientError as e:
        return create_error_response(
            ErrorCodes.INTERNAL_SERVER_ERROR,
            f"OpenStock NORTHBOUND_HOLDING fetch failed for {symbol}: {str(e)}"
        )
    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_SERVER_ERROR,
            f"Failed to get north fund stock data for {symbol}: {str(e)}"
        )


@router.get(
    "/fund-flow/south-stock/{symbol}",
    summary="获取南向资金个股统计",
    description="按股票代码查询南向资金持股与持仓变化，用于跟踪港股通资金偏好和持股集中度。",
    responses=SOUTH_FUND_STOCK_RESPONSES,
)
async def get_south_fund_stock(
    symbol: str = Path(..., description="股票代码，例如 00700"),
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


@router.get(
    "/fund-flow/hsgt-holdings/{symbol}",
    summary="获取沪深港通持股明细",
    description="按股票代码查询沪深港通持股明细，返回通道维度持股记录，用于跨市场资金跟踪。",
    responses=HSGT_HOLDINGS_RESPONSES,
)
async def get_hsgt_holdings(
    symbol: str = Path(..., description="股票代码，例如 600519"),
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


@router.get(
    "/fund-flow/big-deal",
    summary="获取资金流向大单统计",
    description="查询全市场大单资金流向统计，返回大单净流入等指标，用于盘中主力资金观察。",
    responses=FUND_FLOW_BIG_DEAL_RESPONSES,
)
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
