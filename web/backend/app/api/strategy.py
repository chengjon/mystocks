"""
股票策略API端点
提供策略执行、查询、管理等RESTful接口
"""

import logging
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.data_source_factory import DataSourceFactory
from app.services.strategy_service import get_strategy_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/strategy")


# ==================== 请求/响应模型 ====================


class StrategyRunRequest(BaseModel):
    """运行策略请求"""

    strategy_code: str
    symbol: Optional[str] = None
    symbols: Optional[List[str]] = None
    check_date: Optional[str] = None
    limit: Optional[int] = None


class StrategyResultResponse(BaseModel):
    """策略结果响应"""

    success: bool
    data: Optional[dict] = None
    message: str


# ==================== 策略定义相关 ====================


@router.get("/definitions", tags=["strategy"])
async def get_strategy_definitions():
    """
    获取所有策略定义

    Returns:
        所有可用策略的定义列表
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        strategy_adapter = await data_source_factory.get_data_source("strategy")

        result = await strategy_adapter.get_data("definitions")

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "success": True,
            "data": result.get("data", []),
            "total": len(result.get("data", [])),
            "message": "获取策略定义成功",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略定义失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 策略执行相关 ====================


@router.post("/run/single", tags=["strategy"])
async def run_strategy_single(
    strategy_code: str = Query(..., description="策略代码"),
    symbol: str = Query(..., description="股票代码"),
    stock_name: Optional[str] = Query(None, description="股票名称"),
    check_date: Optional[str] = Query(None, description="检查日期 YYYY-MM-DD"),
):
    """
    对单只股票运行策略

    Args:
        strategy_code: 策略代码 (如: volume_surge)
        symbol: 股票代码 (如: 600519)
        stock_name: 股票名称 (可选)
        check_date: 检查日期 (可选，默认今天)

    Returns:
        策略执行结果
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        strategy_adapter = await data_source_factory.get_data_source("strategy")

        params = {"strategy_code": strategy_code, "symbol": symbol, "stock_name": stock_name, "check_date": check_date}

        result = await strategy_adapter.get_data("run_single", params)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "success": result.get("success", False),
            "data": result.get("data", {}),
            "message": result.get("message", ""),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"运行单只股票策略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/batch", tags=["strategy"])
async def run_strategy_batch(
    strategy_code: str = Query(..., description="策略代码"),
    symbols: Optional[str] = Query(None, description="股票代码列表，逗号分隔"),
    market: Optional[str] = Query("A", description="市场类型 (A/SH/SZ/CYB/KCB)"),
    limit: Optional[int] = Query(None, description="限制处理数量"),
    check_date: Optional[str] = Query(None, description="检查日期 YYYY-MM-DD"),
):
    """
    批量运行策略

    Args:
        strategy_code: 策略代码
        symbols: 股票代码列表，逗号分隔 (如: 600519,000001)
        market: 市场类型 (A=全部, SH=上证, SZ=深证, CYB=创业板, KCB=科创板)
        limit: 限制处理数量
        check_date: 检查日期 (可选)

    Returns:
        批量执行结果统计
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        strategy_adapter = await data_source_factory.get_data_source("strategy")

        params = {
            "strategy_code": strategy_code,
            "symbols": symbols,
            "market": market,
            "limit": limit,
            "check_date": check_date,
        }

        result = await strategy_adapter.get_data("run_batch", params)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "success": result.get("success", False),
            "data": result.get("data", {}),
            "message": result.get("message", ""),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量运行策略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 策略结果查询 ====================


@router.get("/results", tags=["strategy"])
async def query_strategy_results(
    strategy_code: Optional[str] = Query(None, description="策略代码"),
    symbol: Optional[str] = Query(None, description="股票代码"),
    check_date: Optional[str] = Query(None, description="检查日期 YYYY-MM-DD"),
    match_result: Optional[bool] = Query(None, description="是否匹配"),
    limit: int = Query(100, description="返回数量"),
    offset: int = Query(0, description="偏移量"),
):
    """
    查询策略结果

    Args:
        strategy_code: 策略代码 (可选)
        symbol: 股票代码 (可选)
        check_date: 检查日期 (可选)
        match_result: 是否匹配 (可选)
        limit: 返回数量 (默认100)
        offset: 偏移量 (默认0)

    Returns:
        策略结果列表
    """
    try:
        service = get_strategy_service()

        # 解析日期
        check_date_obj = None
        if check_date:
            check_date_obj = datetime.strptime(check_date, "%Y-%m-%d").date()

        results = service.query_strategy_results(
            strategy_code=strategy_code,
            symbol=symbol,
            check_date=check_date_obj,
            match_result=match_result,
            limit=limit,
            offset=offset,
        )

        return {
            "success": True,
            "data": results,
            "total": len(results),
            "message": "查询成功",
        }

    except Exception as e:
        logger.error(f"查询策略结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matched-stocks", tags=["strategy"])
async def get_matched_stocks(
    strategy_code: str = Query(..., description="策略代码"),
    check_date: Optional[str] = Query(None, description="检查日期 YYYY-MM-DD"),
    limit: int = Query(100, description="返回数量"),
):
    """
    获取匹配指定策略的股票列表

    Args:
        strategy_code: 策略代码
        check_date: 检查日期 (可选，默认最新)
        limit: 返回数量 (默认100)

    Returns:
        匹配的股票列表
    """
    try:
        service = get_strategy_service()

        # 解析日期
        check_date_obj = None
        if check_date:
            check_date_obj = datetime.strptime(check_date, "%Y-%m-%d").date()

        stocks = service.get_matched_stocks(strategy_code=strategy_code, check_date=check_date_obj, limit=limit)

        return {
            "success": True,
            "data": stocks,
            "total": len(stocks),
            "message": f"找到{len(stocks)}只匹配股票",
        }

    except Exception as e:
        logger.error(f"获取匹配股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 统计分析相关 ====================


@router.get("/stats/summary", tags=["strategy"])
async def get_strategy_summary(check_date: Optional[str] = Query(None, description="检查日期 YYYY-MM-DD")):
    """
    获取策略统计摘要

    Args:
        check_date: 检查日期 (可选，默认今天)

    Returns:
        各策略的匹配数量统计
    """
    try:
        service = get_strategy_service()

        # 解析日期
        check_date_obj = None
        if check_date:
            check_date_obj = datetime.strptime(check_date, "%Y-%m-%d").date()
        else:
            check_date_obj = datetime.now().date()

        # 获取所有策略
        strategies = service.get_strategy_definitions()

        # 统计每个策略的匹配数量
        summary = []
        for strategy in strategies:
            matched_stocks = service.get_matched_stocks(
                strategy_code=strategy["strategy_code"],
                check_date=check_date_obj,
                limit=10000,  # 大数以获取全部
            )

            summary.append(
                {
                    "strategy_code": strategy["strategy_code"],
                    "strategy_name_cn": strategy["strategy_name_cn"],
                    "strategy_name_en": strategy["strategy_name_en"],
                    "matched_count": len(matched_stocks),
                    "check_date": check_date or datetime.now().strftime("%Y-%m-%d"),
                }
            )

        return {"success": True, "data": summary, "message": "获取统计摘要成功"}

    except Exception as e:
        logger.error(f"获取策略统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
