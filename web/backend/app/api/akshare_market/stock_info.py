"""
个股信息与新闻路由 (Stock Info & News)
"""

from fastapi import APIRouter, Depends, Query

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


STOCK_INDIVIDUAL_INFO_EM_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到东方财富个股基本信息",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No individual info found for stock 000001"},
    ),
    **_error_response_spec(
        500,
        "东方财富个股基本信息查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get stock individual info for 000001"},
    ),
    **_success_response_spec(
        "东方财富个股基本信息",
        {
            "success": True,
            "data": {
                "symbol": "000001",
                "data": {
                    "股票代码": "000001",
                    "股票简称": "平安银行",
                    "所属行业": "银行",
                    "总市值": "2.3万亿",
                },
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

STOCK_INDIVIDUAL_INFO_XQ_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到雪球个股基本信息",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No individual info found for stock SZ000001"},
    ),
    **_error_response_spec(
        500,
        "雪球个股基本信息查询失败",
        {
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "Failed to get stock individual info from Xueqiu for SZ000001",
        },
    ),
    **_success_response_spec(
        "雪球个股基本信息",
        {
            "success": True,
            "data": {
                "symbol": "SZ000001",
                "data": {
                    "symbol": "SZ000001",
                    "name": "平安银行",
                    "market": "CN",
                    "exchange": "SZSE",
                },
                "source": "akshare",
                "provider": "xq",
            },
        },
    ),
}

STOCK_BUSINESS_INTRO_THS_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到同花顺主营介绍信息",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No business intro found for stock 000001"},
    ),
    **_error_response_spec(
        500,
        "同花顺主营介绍查询失败",
        {
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "Failed to get business intro from THS for 000001",
        },
    ),
    **_success_response_spec(
        "同花顺主营介绍信息",
        {
            "success": True,
            "data": {
                "symbol": "000001",
                "data": {
                    "主营业务": "商业银行业务",
                    "核心产品": "零售银行、公司金融、财富管理",
                },
                "source": "akshare",
                "provider": "ths",
            },
        },
    ),
}

STOCK_BUSINESS_COMPOSITION_EM_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到东方财富主营构成数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No business composition data found for stock 000001"},
    ),
    **_error_response_spec(
        500,
        "东方财富主营构成查询失败",
        {
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "Failed to get business composition from EM for 000001",
        },
    ),
    **_success_response_spec(
        "东方财富主营构成数据",
        {
            "success": True,
            "data": {
                "symbol": "000001",
                "data": [{"分类方向": "按产品", "分类": "零售银行", "营业收入": 102300000000.0}],
                "count": 1,
                "columns": ["分类方向", "分类", "营业收入"],
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

STOCK_COMMENT_EM_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到千股千评汇总数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No comment data found for stock 000001"},
    ),
    **_error_response_spec(
        500,
        "千股千评汇总查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get stock comment for 000001"},
    ),
    **_success_response_spec(
        "千股千评汇总数据",
        {
            "success": True,
            "data": {
                "symbol": "000001",
                "data": [{"日期": "2024-01-15", "综合评分": 72, "评级": "增持"}],
                "count": 1,
                "columns": ["日期", "综合评分", "评级"],
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

STOCK_COMMENT_DETAIL_EM_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到机构评级详情数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No comment detail data found for stock 000001"},
    ),
    **_error_response_spec(
        500,
        "机构评级详情查询失败",
        {
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "Failed to get stock comment detail for 000001",
        },
    ),
    **_success_response_spec(
        "机构评级详情数据",
        {
            "success": True,
            "data": {
                "symbol": "000001",
                "data": [{"机构名称": "中信证券", "评级": "买入", "目标价": 18.5}],
                "count": 1,
                "columns": ["机构名称", "评级", "目标价"],
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

STOCK_NEWS_EM_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到个股新闻数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No news data found for stock 000001"},
    ),
    **_error_response_spec(
        500,
        "个股新闻查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get stock news for 000001"},
    ),
    **_success_response_spec(
        "个股新闻数据",
        {
            "success": True,
            "data": {
                "symbol": "000001",
                "data": [{"标题": "平安银行发布季度业绩快报", "发布时间": "2024-01-15T09:30:00"}],
                "count": 1,
                "columns": ["标题", "发布时间"],
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

STOCK_BID_ASK_EM_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到五档报价数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No bid-ask data found for stock 000001"},
    ),
    **_error_response_spec(
        500,
        "五档报价查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get stock bid-ask data for 000001"},
    ),
    **_success_response_spec(
        "五档报价数据",
        {
            "success": True,
            "data": {
                "symbol": "000001",
                "data": [{"买一价": 10.53, "买一量": 1200, "卖一价": 10.54, "卖一量": 900}],
                "count": 1,
                "columns": ["买一价", "买一量", "卖一价", "卖一量"],
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

@router.get("/stock/individual-info/em", summary="获取个股信息查询-东财", responses=STOCK_INDIVIDUAL_INFO_EM_RESPONSES)
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


@router.get("/stock/individual-info/xq", summary="获取个股信息查询-雪球", responses=STOCK_INDIVIDUAL_INFO_XQ_RESPONSES)
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


@router.get("/stock/business-intro/ths", summary="获取主营介绍-同花顺", responses=STOCK_BUSINESS_INTRO_THS_RESPONSES)
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


@router.get("/stock/business-composition/em", summary="获取主营构成-东财", responses=STOCK_BUSINESS_COMPOSITION_EM_RESPONSES)
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


@router.get("/stock/comment/em", summary="获取千股千评", responses=STOCK_COMMENT_EM_RESPONSES)
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


@router.get("/stock/comment-detail/em", summary="获取千股千评详情-机构评级", responses=STOCK_COMMENT_DETAIL_EM_RESPONSES)
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


@router.get("/stock/news/em", summary="获取个股新闻", responses=STOCK_NEWS_EM_RESPONSES)
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


@router.get("/stock/bid-ask/em", summary="获取行情报价-五档报价", responses=STOCK_BID_ASK_EM_RESPONSES)
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
