"""
资金流向路由 (Fund Flow)
"""
from fastapi import APIRouter, Depends, Path, Query
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from .base import akshare_market_adapter

router = APIRouter()


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
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get north fund stock data for 600519"},
    ),
    **_success_response_spec(
        "北向资金个股统计数据",
        {
            "success": True,
            "data": {
                "symbol": "600519",
                "data": [{"持股日期": "2024-01-15", "持股数量": 1234567, "持股市值": 2345000000.0}],
                "count": 1,
                "columns": ["持股日期", "持股数量", "持股市值"],
                "fund_direction": "north",
                "source": "akshare",
                "provider": "em",
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
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get HSGT fund flow summary"},
    ),
    **_success_response_spec(
        "沪深港通资金流向汇总数据",
        {
            "success": True,
            "data": {
                "data": [{"日期": "2024-01-15", "北向净流入": 18.2, "南向净流入": 6.4}],
                "count": 1,
                "columns": ["日期", "北向净流入", "南向净流入"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-05"},
                "source": "akshare",
                "provider": "em",
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
    获取北向资金个股统计.

    P0 fix (B4.014, 2026-06-29): 底层 akshare.stock_hsgt_north_acc_flow_in_em 在
    akshare 1.18.60 已被移除, 该 endpoint 暂返回 501. 待 Phase 1.1 第二批切换
    OpenStock NORTHBOUND_HOLDING 类别后恢复.
    TODO(B4.014-Phase1.1-batch2): 切换 OpenStock NORTHBOUND_HOLDING.
    """
    return create_error_response(
        ErrorCodes.INTERNAL_ERROR,
        f"north-stock/{symbol} 暂不可用: akshare.stock_hsgt_north_acc_flow_in_em "
        f"在 akshare 1.18.60 已移除, 待 OpenStock NORTHBOUND_HOLDING 切换恢复"
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
