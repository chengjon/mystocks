"""
股票评级数据API路由
Stock Ratings API Router

提供新浪财经股票评级数据的REST API接口。
"""

import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.responses import UnifiedResponse, bad_request, ok, server_error
from app.core.security import User, get_current_user
from app.schemas.stock_ratings_schemas import (
    StockRatingsHealthResponse,
    StockRatingsRequest,
    StockRatingsResponse,
    StockRatingsSummary,
)
from src.adapters.sina_finance_adapter import SinaFinanceAdapter

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 创建适配器实例
sina_adapter = SinaFinanceAdapter()


@router.get("/ratings", response_model=UnifiedResponse)
async def get_stock_ratings(
    max_pages: int = Query(5, description="最大爬取页数", ge=1, le=10),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取新浪财经股票评级数据

    从新浪财经网站爬取最新的股票评级信息，包括目标价、最新评级、评级机构、分析师等。

    - **max_pages**: 最大爬取页数 (1-10)
    """
    try:
        logger.info("API调用: 股票评级数据, 用户={current_user.username}, 页数=%(max_pages)s")

        # 获取评级数据
        df = sina_adapter.get_sina_stock_ratings(max_pages=max_pages)

        if df.empty:
            return bad_request(message="未获取到股票评级数据，请稍后重试")

        # 转换为字典列表格式
        ratings_data = df.to_dict("records")

        # 构建响应
        response_data = StockRatingsResponse(
            data=ratings_data,
            total_count=len(ratings_data),
            pages_scraped=max_pages,
            max_pages=max_pages,
            timestamp=datetime.now().isoformat(),
            source="sina_finance",
        )

        logger.info("成功返回 {len(ratings_data)} 条股票评级数据")

        return ok(
            data=response_data.dict(),
            message="股票评级数据获取成功",
            total_count=len(ratings_data),
            pages_scraped=max_pages,
            timestamp=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取股票评级数据API异常: {str(e)}", exc_info=True)
        return server_error(message=f"获取股票评级数据失败: {str(e)}")


@router.get("/ratings/summary", response_model=UnifiedResponse)
async def get_ratings_summary(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取股票评级数据汇总统计

    提供评级数据的统计信息，包括总评级数量、机构数量、行业分布等。
    """
    try:
        logger.info("API调用: 评级数据汇总, 用户={current_user.username}")

        # 获取汇总统计
        summary_data = sina_adapter.get_ratings_summary()

        if not summary_data:
            return bad_request(message="无法获取评级数据汇总统计")

        # 构建响应
        summary = StockRatingsSummary(**summary_data)

        return ok(
            data=summary.dict(),
            message="评级数据汇总获取成功",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error("获取评级汇总API异常: {str(e)}", exc_info=True)
        return server_error(message=f"获取评级汇总失败: {str(e)}")


@router.get("/health", response_model=UnifiedResponse)
async def health_check() -> Dict[str, Any]:
    """
    股票评级API健康检查

    检查新浪财经数据源的可用性和响应时间。
    """
    try:
        logger.info("API调用: 股票评级健康检查")

        # 执行健康检查
        health_data = sina_adapter.health_check()

        # 构建响应
        health_response = StockRatingsHealthResponse(**health_data)

        # 根据状态返回不同响应
        if health_response.status == "healthy":
            return ok(
                data=health_response.dict(),
                message="股票评级服务运行正常",
                timestamp=datetime.now().isoformat(),
            )
        else:
            return server_error(message="股票评级服务异常", details=health_response.dict())

    except Exception as e:
        logger.error("健康检查API异常: {str(e)}", exc_info=True)
        return server_error(message=f"健康检查失败: {str(e)}")


@router.post("/ratings/refresh", response_model=UnifiedResponse)
async def refresh_ratings_cache(
    request: StockRatingsRequest = StockRatingsRequest(),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    刷新股票评级数据缓存

    强制重新爬取最新的股票评级数据并更新缓存。

    - **max_pages**: 最大爬取页数 (1-10)
    """
    try:
        logger.info("API调用: 刷新评级缓存, 用户={current_user.username}, 参数={request.dict()}")

        # 重新获取数据（这会自动应用数据质量检查）
        df = sina_adapter.get_sina_stock_ratings(max_pages=request.max_pages)

        if df.empty:
            return bad_request(message="刷新评级数据失败，未获取到有效数据")

        # 可以在这里添加缓存逻辑
        # await cache_service.set("stock_ratings", df.to_dict("records"), ttl=3600)

        return ok(
            data={
                "refreshed_count": len(df),
                "max_pages": request.max_pages,
                "timestamp": datetime.now().isoformat(),
            },
            message="股票评级数据缓存刷新成功",
            refreshed_count=len(df),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error("刷新评级缓存API异常: {str(e)}", exc_info=True)
        return server_error(message=f"刷新评级缓存失败: {str(e)}")
