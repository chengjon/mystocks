"""
财务数据路由 (Financial Data)
"""
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Query

from app.core.security import User, get_current_user
from app.core.exceptions import BusinessException

router = APIRouter()

@router.get("/financial")
async def get_financial_data(
    symbol: str,
    report_type: str = "balance",
    period: str = "all",
    limit: int = 20,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    from app.services.data_source_factory import get_data_source_factory
    factory = await get_data_source_factory()
    params = {"symbol": symbol, "report_type": report_type, "period": period, "limit": limit}
    result = await factory.get_data("data", "financial", params)
    return {"success": True, "data": result.get("data", [])}
