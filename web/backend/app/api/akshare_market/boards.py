"""
板块与行业路由 (Boards & Sectors)
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


CONCEPT_BOARD_CONSTITUENTS_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定概念板块成分股",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No concept board constituents found for symbol BK0816"},
    ),
    **_error_response_spec(
        500,
        "概念板块成分股查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get concept board constituents for BK0816"},
    ),
    **_success_response_spec(
        "概念板块成分股数据",
        {
            "success": True,
            "data": {
                "symbol": "BK0816",
                "data": [{"代码": "300750", "名称": "宁德时代", "涨跌幅": 2.31}],
                "count": 1,
                "columns": ["代码", "名称", "涨跌幅"],
                "source": "akshare",
                "provider": "em",
                "board_type": "concept",
            },
        },
    ),
}

CONCEPT_BOARD_HISTORY_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定概念板块历史行情",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No concept board history data found for symbol BK0816"},
    ),
    **_error_response_spec(
        500,
        "概念板块历史行情查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get concept board history for BK0816"},
    ),
    **_success_response_spec(
        "概念板块历史行情数据",
        {
            "success": True,
            "data": {
                "symbol": "BK0816",
                "data": [{"日期": "2024-01-15", "开盘": 1280.5, "收盘": 1296.2}],
                "count": 1,
                "columns": ["日期", "开盘", "收盘"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-15"},
                "source": "akshare",
                "provider": "em",
                "board_type": "concept",
                "data_type": "daily",
            },
        },
    ),
}

CONCEPT_BOARD_MINUTE_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定概念板块分钟行情",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No concept board minute data found for symbol BK0816"},
    ),
    **_error_response_spec(
        500,
        "概念板块分钟行情查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get concept board minute data for BK0816"},
    ),
    **_success_response_spec(
        "概念板块分钟行情数据",
        {
            "success": True,
            "data": {
                "symbol": "BK0816",
                "data": [{"时间": "09:35", "价格": 1290.4, "成交额": 356000000.0}],
                "count": 1,
                "columns": ["时间", "价格", "成交额"],
                "source": "akshare",
                "provider": "em",
                "board_type": "concept",
                "data_type": "minute",
            },
        },
    ),
}

INDUSTRY_BOARD_CONSTITUENTS_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定行业板块成分股",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No industry board constituents found for symbol BK0475"},
    ),
    **_error_response_spec(
        500,
        "行业板块成分股查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get industry board constituents for BK0475"},
    ),
    **_success_response_spec(
        "行业板块成分股数据",
        {
            "success": True,
            "data": {
                "symbol": "BK0475",
                "data": [{"代码": "600036", "名称": "招商银行", "涨跌幅": 1.56}],
                "count": 1,
                "columns": ["代码", "名称", "涨跌幅"],
                "source": "akshare",
                "provider": "em",
                "board_type": "industry",
            },
        },
    ),
}

INDUSTRY_BOARD_HISTORY_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定行业板块历史行情",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No industry board history data found for symbol BK0475"},
    ),
    **_error_response_spec(
        500,
        "行业板块历史行情查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get industry board history for BK0475"},
    ),
    **_success_response_spec(
        "行业板块历史行情数据",
        {
            "success": True,
            "data": {
                "symbol": "BK0475",
                "data": [{"日期": "2024-01-15", "开盘": 1588.2, "收盘": 1602.8}],
                "count": 1,
                "columns": ["日期", "开盘", "收盘"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-15"},
                "source": "akshare",
                "provider": "em",
                "board_type": "industry",
                "data_type": "daily",
            },
        },
    ),
}

INDUSTRY_BOARD_MINUTE_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定行业板块分钟行情",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No industry board minute data found for symbol BK0475"},
    ),
    **_error_response_spec(
        500,
        "行业板块分钟行情查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get industry board minute data for BK0475"},
    ),
    **_success_response_spec(
        "行业板块分钟行情数据",
        {
            "success": True,
            "data": {
                "symbol": "BK0475",
                "data": [{"时间": "09:35", "价格": 1598.6, "成交额": 268000000.0}],
                "count": 1,
                "columns": ["时间", "价格", "成交额"],
                "source": "akshare",
                "provider": "em",
                "board_type": "industry",
                "data_type": "minute",
            },
        },
    ),
}

SECTOR_HOT_RANKING_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到热门行业排行数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No sector hot ranking data found"},
    ),
    **_error_response_spec(
        500,
        "热门行业排行查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get sector hot ranking"},
    ),
    **_success_response_spec(
        "热门行业排行数据",
        {
            "success": True,
            "data": {
                "data": [{"板块名称": "证券", "涨跌幅": 3.25, "主力净流入": 1860000000.0}],
                "count": 1,
                "columns": ["板块名称", "涨跌幅", "主力净流入"],
                "source": "akshare",
                "provider": "em",
                "ranking_type": "hot_sector",
            },
        },
    ),
}

SECTOR_FUND_FLOW_RANKING_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到行业资金流向排行数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No sector fund flow ranking data found"},
    ),
    **_error_response_spec(
        500,
        "行业资金流向排行查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get sector fund flow ranking"},
    ),
    **_success_response_spec(
        "行业资金流向排行数据",
        {
            "success": True,
            "data": {
                "data": [{"行业名称": "银行", "今日主力净流入": 1280000000.0, "排名": 1}],
                "count": 1,
                "columns": ["行业名称", "今日主力净流入", "排名"],
                "source": "akshare",
                "provider": "em",
                "ranking_type": "fund_flow",
            },
        },
    ),
}


@router.get(
    "/board/concept/cons/{symbol}",
    summary="获取概念板块成分股",
    description="按概念板块代码查询成分股列表，用于观察 A 股概念板块构成与成分股表现。",
    responses=CONCEPT_BOARD_CONSTITUENTS_RESPONSES,
)
async def get_concept_board_constituents(
    symbol: str = Path(..., description="概念板块代码，例如 BK0816"),
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


@router.get(
    "/board/concept/history/{symbol}",
    summary="获取概念板块行情",
    description="按概念板块代码查询历史行情，支持时间区间过滤，用于板块趋势复盘。",
    responses=CONCEPT_BOARD_HISTORY_RESPONSES,
)
async def get_concept_board_history(
    symbol: str = Path(..., description="概念板块代码，例如 BK0816"),
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


@router.get(
    "/board/concept/minute/{symbol}",
    summary="获取概念板块分钟行情",
    description="按概念板块代码查询分钟级行情，用于盘中板块热度与资金节奏观察。",
    responses=CONCEPT_BOARD_MINUTE_RESPONSES,
)
async def get_concept_board_minute(
    symbol: str = Path(..., description="概念板块代码，例如 BK0816"),
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


@router.get(
    "/board/industry/cons/{symbol}",
    summary="获取行业板块成分股",
    description="按行业板块代码查询成分股列表，用于行业维度成分股跟踪和板块拆解。",
    responses=INDUSTRY_BOARD_CONSTITUENTS_RESPONSES,
)
async def get_industry_board_constituents(
    symbol: str = Path(..., description="行业板块代码，例如 BK0475"),
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


@router.get(
    "/board/industry/history/{symbol}",
    summary="获取行业板块行情",
    description="按行业板块代码查询历史行情，支持时间区间过滤，用于行业趋势和轮动分析。",
    responses=INDUSTRY_BOARD_HISTORY_RESPONSES,
)
async def get_industry_board_history(
    symbol: str = Path(..., description="行业板块代码，例如 BK0475"),
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


@router.get(
    "/board/industry/minute/{symbol}",
    summary="获取行业板块分钟行情",
    description="按行业板块代码查询分钟级行情，用于盘中行业强弱和成交节奏分析。",
    responses=INDUSTRY_BOARD_MINUTE_RESPONSES,
)
async def get_industry_board_minute(
    symbol: str = Path(..., description="行业板块代码，例如 BK0475"),
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


@router.get(
    "/sector/hot-ranking",
    summary="获取热门行业排行",
    description="查询全市场热门行业排行，返回行业热度与涨跌表现，用于板块轮动观察。",
    responses=SECTOR_HOT_RANKING_RESPONSES,
)
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


@router.get(
    "/sector/fund-flow-ranking",
    summary="获取行业资金流向",
    description="查询全市场行业资金流向排行，返回主力净流入等指标，用于行业资金强弱分析。",
    responses=SECTOR_FUND_FLOW_RANKING_RESPONSES,
)
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
