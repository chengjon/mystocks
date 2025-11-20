"""
FastAPI路由文件：Dashboard相关API
提供Dashboard页面所需的全部API端点

作者: Claude Code  
生成时间: 2025-11-13
"""

from typing import List, Dict, Optional
import os
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建路由实例
router = APIRouter(prefix="/data/markets", tags=["dashboard"])

# 环境变量控制的数据源切换
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
logger.info(f"数据源模式: {'Mock数据' if USE_MOCK_DATA else '真实数据库'}")

# 导入Mock数据或真实数据
if USE_MOCK_DATA:
    from src.mock.mock_Dashboard import (
        get_market_stats,
        get_market_heat_data, 
        get_leading_sectors,
        get_price_distribution,
        get_capital_flow_data,
        get_industry_fund_flow,
        get_favorite_stocks,
        get_strategy_stocks,
        get_industry_stocks,
        get_concept_stocks
    )
    logger.info("已加载Dashboard Mock数据模块")
else:
    # 实现真实数据库连接
    from src.database.database_service import db_service
    
    def get_market_stats():
        return db_service.get_monitoring_summary()
    
    def get_market_heat_data():
        # Using monitoring alerts as a proxy for market heat
        alerts = db_service.get_monitoring_alerts({'limit': 20})
        return alerts
    
    def get_leading_sectors():
        # Placeholder implementation
        return []
    
    def get_price_distribution():
        # Placeholder implementation
        return []
    
    def get_capital_flow_data():
        # Placeholder implementation
        return []
    
    def get_industry_fund_flow(standard="csrc"):
        # Placeholder implementation
        return {}
    
    def get_favorite_stocks():
        # Placeholder implementation
        return []
    
    def get_strategy_stocks():
        # Placeholder implementation
        return []
    
    def get_industry_stocks():
        # Placeholder implementation
        return []
    
    def get_concept_stocks():
        # Placeholder implementation
        return []
    
    logger.info("已加载Dashboard真实数据库模块")


@router.get("/overview")
async def get_market_overview():
    """
    获取市场概览数据（Dashboard核心API）
    
    返回：
        Dict: 包含市场统计、热度数据、板块表现等综合数据
    """
    try:
        logger.info("获取市场概览数据")
        
        # 并行获取多个数据源
        market_stats = get_market_stats()
        market_heat = get_market_heat_data()
        leading_sectors = get_leading_sectors()
        price_dist = get_price_distribution()
        capital_flow = get_capital_flow_data()
        
        # 组合所有数据
        overview_data = {
            "success": True,
            "data": {
                "market_stats": market_stats,
                "market_heat": market_heat,
                "leading_sectors": leading_sectors,
                "price_distribution": price_dist,
                "capital_flow": capital_flow,
                "industry_fund_flow": get_industry_fund_flow(),
                "favorite_stocks": get_favorite_stocks()[:10],  # 只返回前10个
                "strategy_stocks": get_strategy_stocks()[:10],
                "industry_stocks": get_industry_stocks()[:10],
                "concept_stocks": get_concept_stocks()[:10]
            },
            "message": "获取市场概览数据成功",
            "timestamp": market_stats.get("last_update")
        }
        
        logger.info("市场概览数据获取完成")
        return JSONResponse(content=overview_data)
        
    except Exception as e:
        logger.error(f"获取市场概览数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/stats")
async def get_market_statistics():
    """
    获取市场统计数据
    
    返回：
        Dict: 市场统计数据（对应Dashboard顶部4个卡片）
    """
    try:
        stats = get_market_stats()
        return JSONResponse(content={
            "success": True,
            "data": stats,
            "message": "获取市场统计数据成功"
        })
    except Exception as e:
        logger.error(f"获取市场统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heat")
async def get_market_heat(
    limit: Optional[int] = Query(default=20, description="返回数量限制")
):
    """
    获取市场热度数据
    
    参数：
        limit: int - 返回数量限制
        
    返回：
        List[Dict]: 市场热度数据
    """
    try:
        heat_data = get_market_heat_data()
        if limit:
            heat_data = heat_data[:limit]
        
        return JSONResponse(content={
            "success": True,
            "data": heat_data,
            "message": f"获取市场热度数据成功，共{len(heat_data)}条"
        })
    except Exception as e:
        logger.error(f"获取市场热度数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sectors")
async def get_leading_sectors_data():
    """
    获取领涨板块数据
    
    返回：
        List[Dict]: 领涨板块数据
    """
    try:
        sectors = get_leading_sectors()
        return JSONResponse(content={
            "success": True,
            "data": sectors,
            "message": f"获取领涨板块数据成功，共{len(sectors)}个板块"
        })
    except Exception as e:
        logger.error(f"获取领涨板块数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price-distribution")
async def get_price_distribution_data():
    """
    获取涨跌分布数据
    
    返回：
        List[Dict]: 涨跌分布数据
    """
    try:
        distribution = get_price_distribution()
        return JSONResponse(content={
            "success": True,
            "data": distribution,
            "message": f"获取涨跌分布数据成功"
        })
    except Exception as e:
        logger.error(f"获取涨跌分布数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capital-flow")
async def get_capital_flow():
    """
    获取资金流向数据
    
    返回：
        List[Dict]: 资金流向数据
    """
    try:
        flow_data = get_capital_flow_data()
        return JSONResponse(content={
            "success": True,
            "data": flow_data,
            "message": f"获取资金流向数据成功"
        })
    except Exception as e:
        logger.error(f"获取资金流向数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry-fund-flow")
async def get_industry_fund_flow(
    standard: str = Query(default="csrc", description="行业分类标准")
):
    """
    获取行业资金流向数据
    
    参数：
        standard: str - 行业分类标准 (csrc/sw_l1/sw_l2)
        
    返回：
        Dict: 行业资金流向数据
    """
    try:
        if standard not in ["csrc", "sw_l1", "sw_l2"]:
            raise HTTPException(status_code=400, detail="不支持的行业分类标准")
        
        flow_data = get_industry_fund_flow(standard)
        return JSONResponse(content={
            "success": True,
            "data": flow_data,
            "message": f"获取{standard}行业资金流向数据成功"
        })
    except Exception as e:
        logger.error(f"获取行业资金流向数据失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/{stock_type}")
async def get_stock_data_by_type(
    stock_type: str,
    limit: Optional[int] = Query(default=10, description="返回数量限制")
):
    """
    获取特定类型的股票数据
    
    参数：
        stock_type: str - 股票类型 (favorite/strategy/industry/concept)
        limit: int - 返回数量限制
        
    返回：
        List[Dict]: 股票数据列表
    """
    try:
        stock_data_map = {
            "favorite": get_favorite_stocks,
            "strategy": get_strategy_stocks, 
            "industry": get_industry_stocks,
            "concept": get_concept_stocks
        }
        
        if stock_type not in stock_data_map:
            raise HTTPException(status_code=400, detail="不支持的股票类型")
        
        stocks = stock_data_map[stock_type]()
        if limit:
            stocks = stocks[:limit]
        
        return JSONResponse(content={
            "success": True,
            "data": stocks,
            "type": stock_type,
            "message": f"获取{stock_type}股票数据成功，共{len(stocks)}只"
        })
    except Exception as e:
        logger.error(f"获取{stock_type}股票数据失败: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))
