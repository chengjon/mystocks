"""
融资融券数据路由 (Margin Trading)
"""
from fastapi import APIRouter, Depends, Query
from app.core.security import User, get_current_user
from app.core.responses import UnifiedResponse, ok, server_error

router = APIRouter()

@router.get("/margin/account-info", response_model=UnifiedResponse)
async def get_margin_account_info(current_user: User = Depends(get_current_user)) -> UnifiedResponse:
    """获取全市场融资融券账户统计信息"""
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data("data", "margin/account-info", {})
        if result.get("status") == "success":
            return ok(data=result.get("data", []))
        return server_error(message="获取失败")
    except Exception as e:
        return server_error(message=str(e))

@router.get("/margin/detail/sse", response_model=UnifiedResponse)
async def get_margin_detail_sse(date: str = Query(...), current_user: User = Depends(get_current_user)) -> UnifiedResponse:
    """获取上证所融资融券明细数据"""
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data("data", "margin/detail/sse", {"date": date})
        return ok(data=result.get("data", []))
    except Exception as e:
        return server_error(message=str(e))

@router.get("/margin/detail/szse", response_model=UnifiedResponse)
async def get_margin_detail_szse(date: str = Query(...), current_user: User = Depends(get_current_user)) -> UnifiedResponse:
    """获取深证所融资融券明细数据"""
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data("data", "margin/detail/szse", {"date": date})
        return ok(data=result.get("data", []))
    except Exception as e:
        return server_error(message=str(e))
