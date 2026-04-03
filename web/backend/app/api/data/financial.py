"""
财务数据路由 (Financial Data)
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, Query

from app.core.security import User, get_current_user

router = APIRouter()

@router.get(
    "/financial",
    description="查询股票财务报表数据，支持报表类型、报告期间和返回条数等筛选条件。",
)
async def get_financial_data(
    symbol: str = Query(..., description="股票代码。"),
    report_type: str = Query("balance", description="财务报表类型，例如 balance、income 或 cashflow。"),
    period: str = Query("all", description="报告期间筛选，例如 annual、quarterly 或 all。"),
    limit: int = Query(20, description="单次请求返回的最大财务记录数。"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    from app.services.data_source_factory import get_data_source_factory
    factory = await get_data_source_factory()
    params = {"symbol": symbol, "report_type": report_type, "period": period, "limit": limit}
    result = await factory.get_data("data", "financial", params)
    return {"success": True, "data": result.get("data", [])}
