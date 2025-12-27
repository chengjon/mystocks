"""
Multi-source Data API
Multi-data Source Support

提供多数据源管理和查询的API端点
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.multi_source_manager import get_multi_source_manager
from app.adapters.base import DataSourceType, DataCategory

router = APIRouter(prefix="/api/multi-source", tags=["multi-source"])


# ============================================================================
# Pydantic Models
# ============================================================================


class DataSourceHealthResponse(BaseModel):
    """数据源健康状态响应"""

    source_type: str
    status: str
    enabled: bool
    priority: int
    success_rate: float
    avg_response_time: float
    error_count: int
    last_check: str
    supported_categories: List[str]
    total_requests: int
    success_count: int


class DataFetchResponse(BaseModel):
    """数据获取响应"""

    success: bool
    source: Optional[str] = None
    data: Optional[dict] = None
    count: Optional[int] = None
    response_time: Optional[float] = None
    cached: Optional[bool] = None
    error: Optional[str] = None


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/health", response_model=List[DataSourceHealthResponse])
async def get_all_data_sources_health():
    """
    获取所有数据源的健康状态

    Returns:
        List[DataSourceHealthResponse]: 所有数据源的健康状态
    """
    try:
        manager = get_multi_source_manager()
        statuses = manager.get_all_health_status()

        return statuses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/{source_type}")
async def get_data_source_health(source_type: str):
    """
    获取指定数据源的健康状态

    Args:
        source_type: 数据源类型 (eastmoney, cninfo, akshare, wencai)

    Returns:
        Dict: 健康状态详情
    """
    try:
        manager = get_multi_source_manager()

        # 验证数据源类型
        try:
            source_enum = DataSourceType(source_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source type: {source_type}")

        adapter = manager.get_adapter(source_enum)

        if not adapter:
            raise HTTPException(status_code=404, detail=f"Data source not found: {source_type}")

        health = adapter.check_health()
        stats = adapter.get_statistics()

        return {
            "source_type": source_type,
            "status": health.status.value,
            "enabled": adapter.get_config().enabled,
            "priority": adapter.get_config().priority,
            "success_rate": health.success_rate,
            "avg_response_time": health.avg_response_time,
            "error_count": health.error_count,
            "last_check": health.last_check.isoformat(),
            "supported_categories": [cat.value for cat in health.supported_categories],
            **stats,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/realtime-quote")
async def fetch_realtime_quote(
    symbols: Optional[str] = Query(None, description="股票代码，逗号分隔"),
    source: Optional[str] = Query(None, description="指定数据源"),
):
    """
    获取实时行情（支持多数据源）

    Args:
        symbols: 股票代码列表（逗号分隔）
        source: 指定数据源

    Returns:
        Dict: 实时行情数据
    """
    try:
        manager = get_multi_source_manager()

        # 解析股票代码
        symbol_list = symbols.split(",") if symbols else None

        # 解析数据源
        source_enum = None
        if source:
            try:
                source_enum = DataSourceType(source)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid source: {source}")

        # 获取数据
        result = manager.fetch_realtime_quote(symbols=symbol_list, source=source_enum)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to fetch data"))

        # 转换DataFrame为dict
        df = result.get("data")
        if df is not None and not df.empty:
            result["data"] = df.to_dict("records")
            result["count"] = len(df)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fund-flow")
async def fetch_fund_flow(
    symbol: Optional[str] = Query(None, description="股票代码"),
    timeframe: str = Query("今日", description="时间范围：今日、3日、5日、10日"),
    source: Optional[str] = Query(None, description="指定数据源"),
):
    """
    获取资金流向（支持多数据源）

    Args:
        symbol: 股票代码
        timeframe: 时间范围
        source: 指定数据源

    Returns:
        Dict: 资金流向数据
    """
    try:
        manager = get_multi_source_manager()

        source_enum = None
        if source:
            try:
                source_enum = DataSourceType(source)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid source: {source}")

        result = manager.fetch_fund_flow(symbol=symbol, timeframe=timeframe, source=source_enum)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to fetch data"))

        df = result.get("data")
        if df is not None and not df.empty:
            result["data"] = df.to_dict("records")
            result["count"] = len(df)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dragon-tiger")
async def fetch_dragon_tiger(
    date_str: str = Query(..., description="日期 (YYYY-MM-DD)"),
    source: Optional[str] = Query(None, description="指定数据源"),
):
    """
    获取龙虎榜（支持多数据源）

    Args:
        date_str: 日期
        source: 指定数据源

    Returns:
        Dict: 龙虎榜数据
    """
    try:
        manager = get_multi_source_manager()

        source_enum = None
        if source:
            try:
                source_enum = DataSourceType(source)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid source: {source}")

        result = manager.fetch_dragon_tiger(date_str=date_str, source=source_enum)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to fetch data"))

        df = result.get("data")
        if df is not None and not df.empty:
            result["data"] = df.to_dict("records")
            result["count"] = len(df)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-health")
async def refresh_data_source_health():
    """
    刷新所有数据源的健康状态

    Returns:
        Dict: 刷新结果
    """
    try:
        manager = get_multi_source_manager()

        # 刷新类别映射
        manager.refresh_category_mapping()

        # 获取最新健康状态
        statuses = manager.get_all_health_status()

        return {
            "success": True,
            "message": "Health status refreshed",
            "sources": len(statuses),
            "statuses": statuses,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_cache():
    """
    清空数据缓存

    Returns:
        Dict: 操作结果
    """
    try:
        manager = get_multi_source_manager()
        manager.clear_cache()

        return {"success": True, "message": "Cache cleared successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-categories")
async def get_supported_categories():
    """
    获取所有支持的数据类别及其对应的数据源

    Returns:
        Dict: 数据类别映射
    """
    try:
        manager = get_multi_source_manager()

        category_mapping = {}

        # 遍历所有数据类别
        for category in DataCategory:
            sources = manager.get_sources_for_category(category)
            if sources:
                category_mapping[category.value] = [src.value for src in sources]

        return {
            "success": True,
            "categories": category_mapping,
            "total_categories": len(category_mapping),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
