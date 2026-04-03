"""
龙虎榜数据路由 (Dragon Tiger)
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.security import User, get_current_user
from app.core.responses import UnifiedResponse, ok, server_error

router = APIRouter()

@router.get(
    "/dragon-tiger/detail",
    response_model=UnifiedResponse,
    description="查询龙虎榜明细数据，支持按日期范围和返回条数筛选榜单结果。",
)
async def get_dragon_tiger_detail(
    start_date: str = Query(..., description="查询开始日期，格式为 YYYY-MM-DD。"),
    end_date: str = Query(..., description="查询结束日期，格式为 YYYY-MM-DD。"),
    limit: int = Query(100, description="单次请求返回的最大龙虎榜记录数。"),
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data("data", "dragon-tiger/detail", {"start_date": start_date, "end_date": end_date, "limit": limit})
        return ok(data=result.get("data", []))
    except Exception as e:
        return server_error(message=str(e))

@router.get("/dragon-tiger/institution-stats")
async def get_dragon_tiger_institution_stats(
    period: str = Query("近一月"),
    limit: int = 50,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data("data", "dragon-tiger/institution-stats", {"period": period, "limit": limit})
        return {"success": True, "data": result.get("data", []), "period": period}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
