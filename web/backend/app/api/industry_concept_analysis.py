"""
行业概念分析API模块

提供行业/概念分类数据的查询接口，包括：
- 获取行业列表
- 获取概念列表
- 获取指定行业的成分股
- 获取指定概念的成分股
- 获取行业表现数据
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import pandas as pd
from datetime import datetime

from app.models.schemas import (
    IndustryListResponse,
    ConceptListResponse,
    StockListResponse,
    IndustryPerformanceResponse,
    APIResponse,
)
from app.services.unified_data_service import UnifiedDataService
from app.core.database import get_postgresql_engine

router = APIRouter(prefix="/api/analysis", tags=["industry-concept-analysis"])


@router.get("/industry/list", response_model=IndustryListResponse)
async def get_industry_list():
    """
    获取所有行业分类列表
    
    Returns:
        IndustryListResponse: 行业列表
    """
    try:
        # 使用统一数据服务获取行业数据
        unified_service = UnifiedDataService()
        
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
        
        industries = result.to_dict('records') if not result.empty else []
        
        return IndustryListResponse(
            success=True,
            data={
                "industries": industries,
                "total_count": len(industries)
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行业列表失败: {str(e)}")


@router.get("/concept/list", response_model=ConceptListResponse)
async def get_concept_list():
    """
    获取所有概念分类列表
    
    Returns:
        ConceptListResponse: 概念列表
    """
    try:
        # 使用统一数据服务获取概念数据
        unified_service = UnifiedDataService()
        
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
        
        concepts = result.to_dict('records') if not result.empty else []
        
        return ConceptListResponse(
            success=True,
            data={
                "concepts": concepts,
                "total_count": len(concepts)
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取概念列表失败: {str(e)}")


@router.get("/industry/stocks", response_model=StockListResponse)
async def get_industry_stocks(
    industry_code: str = Query(..., description="行业代码"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="限制返回数量")
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
        
        stocks = result.to_dict('records') if not result.empty else []
        
        return StockListResponse(
            success=True,
            data={
                "stocks": stocks,
                "total_count": len(stocks),
                "industry_code": industry_code
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行业成分股失败: {str(e)}")


@router.get("/concept/stocks", response_model=StockListResponse)
async def get_concept_stocks(
    concept_code: str = Query(..., description="概念代码"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="限制返回数量")
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
        
        stocks = result.to_dict('records') if not result.empty else []
        
        return StockListResponse(
            success=True,
            data={
                "stocks": stocks,
                "total_count": len(stocks),
                "concept_code": concept_code
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取概念成分股失败: {str(e)}")


@router.get("/industry/performance", response_model=IndustryPerformanceResponse)
async def get_industry_performance(
    industry_code: str = Query(..., description="行业代码")
):
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
        
        up_count = len(stocks_result[stocks_result['change_percent'] > 0])
        down_count = len(stocks_result[stocks_result['change_percent'] < 0])
        
        # 找出领涨股
        leader_stock = None
        if not stocks_result.empty:
            leader_stock_row = stocks_result.nlargest(1, 'change_percent').iloc[0]
            leader_stock = {
                "symbol": leader_stock_row['symbol'],
                "price": leader_stock_row['latest_price'],
                "change_percent": leader_stock_row['change_percent']
            }
        
        return IndustryPerformanceResponse(
            success=True,
            data={
                "industry": industry_data,
                "up_count": up_count,
                "down_count": down_count,
                "leader_stock": leader_stock,
                "stocks_performance": stocks_result.to_dict('records') if not stocks_result.empty else []
            },
            timestamp=datetime.now().isoformat()
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
        {
            "path": "/api/analysis/industry/list",
            "method": "GET",
            "description": "获取所有行业分类列表"
        },
        {
            "path": "/api/analysis/concept/list", 
            "method": "GET",
            "description": "获取所有概念分类列表"
        },
        {
            "path": "/api/analysis/industry/stocks",
            "method": "GET",
            "description": "获取指定行业的成分股列表"
        },
        {
            "path": "/api/analysis/concept/stocks",
            "method": "GET", 
            "description": "获取指定概念的成分股列表"
        },
        {
            "path": "/api/analysis/industry/performance",
            "method": "GET",
            "description": "获取行业整体表现数据"
        }
    ]
    return endpoints