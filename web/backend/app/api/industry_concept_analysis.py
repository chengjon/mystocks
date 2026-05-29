"""
行业概念分析API模块

提供行业/概念分类数据的查询接口，包括：
- 获取行业列表
- 获取概念列表
- 获取指定行业的成分股
- 获取指定概念的成分股
- 获取行业表现数据
"""

from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.core.database import get_postgresql_engine
from app.models.schemas import (
    ConceptListResponse,
    IndustryListResponse,
    IndustryPerformanceResponse,
    StockListResponse,
)
from app.openapi_config import COMMON_RESPONSES

INDUSTRY_CONCEPT_ROUTE_RESPONSES = {
    500: COMMON_RESPONSES[500],
}

router = APIRouter(
    prefix="/api/analysis",
    tags=["industry-concept-analysis"],
    responses=INDUSTRY_CONCEPT_ROUTE_RESPONSES,
)


def _success_response_spec(description: str, example: dict) -> dict[int, dict]:
    return {
        200: {
            "description": description,
            "content": {"application/json": {"example": example}},
        }
    }


INDUSTRY_LIST_RESPONSES = {
    **INDUSTRY_CONCEPT_ROUTE_RESPONSES,
    **_success_response_spec(
        "行业分类列表查询成功。",
        {
            "success": True,
            "data": {
                "industries": [
                    {
                        "industry_code": "BK0475",
                        "industry_name": "证券",
                        "stock_count": 48,
                        "up_count": 31,
                        "down_count": 14,
                        "latest_price": 1245.32,
                        "change_percent": 1.82,
                        "change_amount": 22.31,
                        "volume": 125000000,
                        "amount": 3680000000,
                        "total_market_value": 5820000000000,
                        "turnover_rate": 2.14,
                        "updated_at": "2026-04-08T10:00:00",
                    }
                ],
                "total_count": 1,
            },
            "timestamp": "2026-04-08T10:00:00",
        },
    ),
}

CONCEPT_LIST_RESPONSES = {
    **INDUSTRY_CONCEPT_ROUTE_RESPONSES,
    **_success_response_spec(
        "概念分类列表查询成功。",
        {
            "success": True,
            "data": {
                "concepts": [
                    {
                        "concept_code": "GN1234",
                        "concept_name": "人工智能",
                        "stock_count": 86,
                        "up_count": 52,
                        "down_count": 24,
                        "latest_price": 2188.6,
                        "change_percent": 3.25,
                        "change_amount": 68.92,
                        "volume": 182000000,
                        "amount": 5210000000,
                        "total_market_value": 9200000000000,
                        "turnover_rate": 3.41,
                        "updated_at": "2026-04-08T10:00:00",
                    }
                ],
                "total_count": 1,
            },
            "timestamp": "2026-04-08T10:00:00",
        },
    ),
}

INDUSTRY_STOCKS_RESPONSES = {
    **INDUSTRY_CONCEPT_ROUTE_RESPONSES,
    **_success_response_spec(
        "行业成分股列表查询成功。",
        {
            "success": True,
            "data": {
                "stocks": [
                    {
                        "symbol": "600030.SH",
                        "category_name": "证券",
                        "latest_price": 24.36,
                        "change_percent": 2.51,
                        "volume": 18500000,
                        "amount": 451000000,
                    }
                ],
                "total_count": 1,
                "industry_code": "BK0475",
            },
            "timestamp": "2026-04-08T10:00:00",
        },
    ),
}

CONCEPT_STOCKS_RESPONSES = {
    **INDUSTRY_CONCEPT_ROUTE_RESPONSES,
    **_success_response_spec(
        "概念成分股列表查询成功。",
        {
            "success": True,
            "data": {
                "stocks": [
                    {
                        "symbol": "300308.SZ",
                        "category_name": "人工智能",
                        "latest_price": 56.72,
                        "change_percent": 5.18,
                        "volume": 26500000,
                        "amount": 1502000000,
                    }
                ],
                "total_count": 1,
                "concept_code": "GN1234",
            },
            "timestamp": "2026-04-08T10:00:00",
        },
    ),
}

INDUSTRY_PERFORMANCE_RESPONSES = {
    404: {
        "description": "指定行业不存在或当前无可用表现数据。",
        "content": {"application/json": {"example": {"detail": "未找到行业: BK9999"}}},
    },
    **INDUSTRY_CONCEPT_ROUTE_RESPONSES,
    **_success_response_spec(
        "行业整体表现查询成功。",
        {
            "success": True,
            "data": {
                "industry": {
                    "industry_code": "BK0475",
                    "industry_name": "证券",
                    "stock_count": 48,
                    "up_count": 31,
                    "down_count": 14,
                    "leader_stock": "600030.SH",
                    "latest_price": 1245.32,
                    "change_percent": 1.82,
                    "change_amount": 22.31,
                    "volume": 125000000,
                    "amount": 3680000000,
                    "total_market_value": 5820000000000,
                    "turnover_rate": 2.14,
                    "updated_at": "2026-04-08T10:00:00",
                },
                "up_count": 31,
                "down_count": 14,
                "leader_stock": {
                    "symbol": "600030.SH",
                    "price": 24.36,
                    "change_percent": 2.51,
                },
                "stocks_performance": [
                    {
                        "symbol": "600030.SH",
                        "latest_price": 24.36,
                        "change_percent": 2.51,
                    }
                ],
            },
            "timestamp": "2026-04-08T10:00:00",
        },
    ),
}


@router.get(
    "/industry/list",
    response_model=IndustryListResponse,
    summary="获取行业分类列表",
    description="返回当前数据库中的全部行业分类快照，包括涨跌家数、成交额和换手率等汇总指标。",
    responses=INDUSTRY_LIST_RESPONSES,
)
async def get_industry_list():
    """
    获取所有行业分类列表

    Returns:
        IndustryListResponse: 行业列表
    """
    try:
        # 从数据库查询行业分类数据
        query = """
            SELECT DISTINCT
                industry_code,
                industry_name,
                stock_count,
                up_count,
                down_count,
                latest_price,
                change_percent,
                change_amount,
                volume,
                amount,
                total_market_value,
                turnover_rate,
                updated_at
            FROM industry_classifications
            ORDER BY industry_name
        """

        engine = get_postgresql_engine()
        with engine.connect() as conn:
            result = pd.read_sql(query, conn)

        industries = result.to_dict("records") if not result.empty else []

        return IndustryListResponse(
            success=True,
            data={"industries": industries, "total_count": len(industries)},
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行业列表失败: {str(e)}")


@router.get(
    "/concept/list",
    response_model=ConceptListResponse,
    summary="获取概念分类列表",
    description="返回当前数据库中的全部概念分类快照，包括涨跌家数、成交额和换手率等汇总指标。",
    responses=CONCEPT_LIST_RESPONSES,
)
async def get_concept_list():
    """
    获取所有概念分类列表

    Returns:
        ConceptListResponse: 概念列表
    """
    try:
        # 从数据库查询概念分类数据
        query = """
            SELECT DISTINCT
                concept_code,
                concept_name,
                stock_count,
                up_count,
                down_count,
                latest_price,
                change_percent,
                change_amount,
                volume,
                amount,
                total_market_value,
                turnover_rate,
                updated_at
            FROM concept_classifications
            ORDER BY concept_name
        """

        engine = get_postgresql_engine()
        with engine.connect() as conn:
            result = pd.read_sql(query, conn)

        concepts = result.to_dict("records") if not result.empty else []

        return ConceptListResponse(
            success=True,
            data={"concepts": concepts, "total_count": len(concepts)},
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取概念列表失败: {str(e)}")


@router.get(
    "/industry/stocks",
    response_model=StockListResponse,
    summary="获取行业成分股列表",
    description="按行业代码查询该行业下的成分股列表，并返回最新价格、涨跌幅和成交额等字段。",
    responses=INDUSTRY_STOCKS_RESPONSES,
)
async def get_industry_stocks(
    industry_code: str = Query(..., description="行业代码"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="限制返回数量"),
):
    """
    获取指定行业的成分股列表

    Args:
        industry_code: 行业代码
        limit: 限制返回数量

    Returns:
        StockListResponse: 成分股列表
    """
    try:
        # 从关联表查询该行业的股票
        query = """
            SELECT
                si.symbol,
                si.category_name,
                k.close as latest_price,
                k.pct_chg as change_percent,
                k.volume,
                k.amount
            FROM stock_industry_concept_relations si
            LEFT JOIN daily_kline k ON si.symbol = k.symbol
                AND k.trade_date = (SELECT MAX(trade_date) FROM daily_kline)
            WHERE si.category_type = 'industry'
                AND si.category_code = :industry_code
                AND si.is_active = true
            ORDER BY k.pct_chg DESC NULLS LAST
        """

        params = {"industry_code": industry_code}
        if limit:
            query += f" LIMIT {limit}"

        engine = get_postgresql_engine()
        with engine.connect() as conn:
            result = pd.read_sql(query, conn, params=params)

        stocks = result.to_dict("records") if not result.empty else []

        return StockListResponse(
            success=True,
            data={"stocks": stocks, "total_count": len(stocks), "industry_code": industry_code},
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行业成分股失败: {str(e)}")


@router.get(
    "/concept/stocks",
    response_model=StockListResponse,
    summary="获取概念成分股列表",
    description="按概念代码查询该概念下的成分股列表，并返回最新价格、涨跌幅和成交额等字段。",
    responses=CONCEPT_STOCKS_RESPONSES,
)
async def get_concept_stocks(
    concept_code: str = Query(..., description="概念代码"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="限制返回数量"),
):
    """
    获取指定概念的成分股列表

    Args:
        concept_code: 概念代码
        limit: 限制返回数量

    Returns:
        StockListResponse: 成分股列表
    """
    try:
        # 从关联表查询该概念的股票
        query = """
            SELECT
                si.symbol,
                si.category_name,
                k.close as latest_price,
                k.pct_chg as change_percent,
                k.volume,
                k.amount
            FROM stock_industry_concept_relations si
            LEFT JOIN daily_kline k ON si.symbol = k.symbol
                AND k.trade_date = (SELECT MAX(trade_date) FROM daily_kline)
            WHERE si.category_type = 'concept'
                AND si.category_code = :concept_code
                AND si.is_active = true
            ORDER BY k.pct_chg DESC NULLS LAST
        """

        params = {"concept_code": concept_code}
        if limit:
            query += f" LIMIT {limit}"

        engine = get_postgresql_engine()
        with engine.connect() as conn:
            result = pd.read_sql(query, conn, params=params)

        stocks = result.to_dict("records") if not result.empty else []

        return StockListResponse(
            success=True,
            data={"stocks": stocks, "total_count": len(stocks), "concept_code": concept_code},
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取概念成分股失败: {str(e)}")


@router.get(
    "/industry/performance",
    response_model=IndustryPerformanceResponse,
    summary="获取行业整体表现",
    description="返回指定行业的整体表现、上涨下跌家数、领涨股以及行业内股票涨跌幅分布。",
    responses=INDUSTRY_PERFORMANCE_RESPONSES,
)
async def get_industry_performance(industry_code: str = Query(..., description="行业代码")):
    """
    获取行业整体表现数据

    Args:
        industry_code: 行业代码

    Returns:
        IndustryPerformanceResponse: 行业表现数据
    """
    try:
        # 查询行业整体表现数据
        query = """
            SELECT
                industry_code,
                industry_name,
                stock_count,
                up_count,
                down_count,
                leader_stock,
                latest_price,
                change_percent,
                change_amount,
                volume,
                amount,
                total_market_value,
                turnover_rate,
                updated_at
            FROM industry_classifications
            WHERE industry_code = :industry_code
        """

        params = {"industry_code": industry_code}

        engine = get_postgresql_engine()
        with engine.connect() as conn:
            result = pd.read_sql(query, conn, params=params)

        if result.empty:
            raise HTTPException(status_code=404, detail=f"未找到行业: {industry_code}")

        industry_data = result.iloc[0].to_dict()

        # 获取该行业上涨和下跌个股数量
        stocks_query = """
            SELECT
                si.symbol,
                k.close as latest_price,
                k.pct_chg as change_percent
            FROM stock_industry_concept_relations si
            LEFT JOIN daily_kline k ON si.symbol = k.symbol
                AND k.trade_date = (SELECT MAX(trade_date) FROM daily_kline)
            WHERE si.category_type = 'industry'
                AND si.category_code = :industry_code
                AND si.is_active = true
                AND k.pct_chg IS NOT NULL
        """

        with engine.connect() as conn:
            stocks_result = pd.read_sql(stocks_query, conn, params=params)

        up_count = len(stocks_result[stocks_result["change_percent"] > 0])
        down_count = len(stocks_result[stocks_result["change_percent"] < 0])

        # 找出领涨股
        leader_stock = None
        if not stocks_result.empty:
            leader_stock_row = stocks_result.nlargest(1, "change_percent").iloc[0]
            leader_stock = {
                "symbol": leader_stock_row["symbol"],
                "price": leader_stock_row["latest_price"],
                "change_percent": leader_stock_row["change_percent"],
            }

        return IndustryPerformanceResponse(
            success=True,
            data={
                "industry": industry_data,
                "up_count": up_count,
                "down_count": down_count,
                "leader_stock": leader_stock,
                "stocks_performance": stocks_result.to_dict("records") if not stocks_result.empty else [],
            },
            timestamp=datetime.now().isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行业表现数据失败: {str(e)}")


# 为API注册器添加一个函数来获取所有行业概念相关的端点
def get_industry_concept_endpoints():
    """
    获取所有行业概念分析端点信息
    """
    endpoints = [
        {"path": "/api/analysis/industry/list", "method": "GET", "description": "获取所有行业分类列表"},
        {"path": "/api/analysis/concept/list", "method": "GET", "description": "获取所有概念分类列表"},
        {"path": "/api/analysis/industry/stocks", "method": "GET", "description": "获取指定行业的成分股列表"},
        {"path": "/api/analysis/concept/stocks", "method": "GET", "description": "获取指定概念的成分股列表"},
        {"path": "/api/analysis/industry/performance", "method": "GET", "description": "获取行业整体表现数据"},
    ]
    return endpoints
