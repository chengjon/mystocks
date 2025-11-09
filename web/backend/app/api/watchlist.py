"""
自选股管理 API
提供用户自选股的增删改查功能
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.services.watchlist_service import (
    get_watchlist_service,
    WatchlistService,
    WatchlistError,
)
from app.api.auth import get_current_user, User

router = APIRouter()


class WatchlistItem(BaseModel):
    """自选股条目"""

    id: int
    symbol: str = Field(..., description="股票代码")
    display_name: str = Field(None, description="显示名称")
    exchange: str = Field(None, description="交易所")
    added_at: str = Field(..., description="添加时间")
    notes: str = Field(None, description="备注")


class AddWatchlistRequest(BaseModel):
    """添加自选股请求"""

    symbol: str = Field(..., description="股票代码")
    display_name: str = Field(None, description="显示名称")
    exchange: str = Field(None, description="交易所")
    market: str = Field(None, description="市场（CN/HK）")
    notes: str = Field(None, description="备注")
    group_id: int = Field(None, description="分组ID")
    group_name: str = Field(None, description="分组名称（如果不存在则自动创建）")


class UpdateWatchlistNotesRequest(BaseModel):
    """更新备注请求"""

    notes: str = Field(..., description="备注内容")


class CreateGroupRequest(BaseModel):
    """创建分组请求"""

    group_name: str = Field(..., description="分组名称")


class UpdateGroupRequest(BaseModel):
    """更新分组请求"""

    group_name: str = Field(..., description="新的分组名称")


class MoveStockRequest(BaseModel):
    """移动股票请求"""

    symbol: str = Field(..., description="股票代码")
    from_group_id: int = Field(..., description="原分组ID")
    to_group_id: int = Field(..., description="目标分组ID")


@router.get("/", response_model=List[WatchlistItem])
async def get_my_watchlist(
    current_user: User = Depends(get_current_user),
) -> List[Dict]:
    """
    获取当前用户的自选股列表
    """
    try:
        service = get_watchlist_service()
        watchlist = service.get_user_watchlist(current_user.id)

        return watchlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取自选股列表失败: {str(e)}")


@router.get("/symbols", response_model=List[str])
async def get_my_watchlist_symbols(
    current_user: User = Depends(get_current_user),
) -> List[str]:
    """
    获取当前用户的自选股代码列表
    """
    try:
        service = get_watchlist_service()
        symbols = service.get_watchlist_symbols(current_user.id)

        return symbols
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取自选股代码列表失败: {str(e)}")


@router.post("/add")
async def add_to_watchlist(
    request: AddWatchlistRequest, current_user: User = Depends(get_current_user)
) -> Dict:
    """
    添加股票到自选股列表
    支持通过 group_id 或 group_name 指定分组
    如果提供 group_name 且分组不存在，会自动创建
    """
    try:
        service = get_watchlist_service()
        group_id = request.group_id

        # 如果提供了 group_name，获取或创建分组
        if request.group_name:
            group = service.get_or_create_group(current_user.id, request.group_name)
            if group:
                group_id = group["id"]
            else:
                raise HTTPException(
                    status_code=500, detail=f"无法创建分组 '{request.group_name}'"
                )

        success = service.add_to_watchlist(
            user_id=current_user.id,
            symbol=request.symbol,
            display_name=request.display_name,
            exchange=request.exchange,
            market=request.market,
            notes=request.notes,
            group_id=group_id,
        )

        if not success:
            raise HTTPException(status_code=500, detail="添加自选股失败")

        return {
            "success": True,
            "message": "已添加到自选股",
            "symbol": request.symbol,
            "group_name": request.group_name if request.group_name else "默认分组",
        }
    except HTTPException:
        raise
    except WatchlistError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加自选股失败: {str(e)}")


@router.delete("/remove/{symbol}")
async def remove_from_watchlist(
    symbol: str, current_user: User = Depends(get_current_user)
) -> Dict:
    """
    从自选股列表中删除股票
    """
    try:
        service = get_watchlist_service()
        success = service.remove_from_watchlist(current_user.id, symbol)

        if not success:
            raise HTTPException(status_code=404, detail="自选股不存在或删除失败")

        return {"success": True, "message": "已从自选股移除", "symbol": symbol}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除自选股失败: {str(e)}")


@router.get("/check/{symbol}")
async def check_in_watchlist(
    symbol: str, current_user: User = Depends(get_current_user)
) -> Dict:
    """
    检查股票是否在自选股列表中
    """
    try:
        service = get_watchlist_service()
        is_watched = service.is_in_watchlist(current_user.id, symbol)

        return {"symbol": symbol, "is_in_watchlist": is_watched}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查自选股失败: {str(e)}")


@router.put("/notes/{symbol}")
async def update_watchlist_notes(
    symbol: str,
    request: UpdateWatchlistNotesRequest,
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    更新自选股备注
    """
    try:
        service = get_watchlist_service()
        success = service.update_watchlist_notes(
            user_id=current_user.id, symbol=symbol, notes=request.notes
        )

        if not success:
            raise HTTPException(status_code=404, detail="自选股不存在或更新失败")

        return {"success": True, "message": "备注已更新", "symbol": symbol}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新备注失败: {str(e)}")


@router.get("/count")
async def get_watchlist_count(current_user: User = Depends(get_current_user)) -> Dict:
    """
    获取自选股数量
    """
    try:
        service = get_watchlist_service()
        count = service.get_watchlist_count(current_user.id)

        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取自选股数量失败: {str(e)}")


@router.delete("/clear")
async def clear_watchlist(current_user: User = Depends(get_current_user)) -> Dict:
    """
    清空当前用户的自选股列表
    """
    try:
        service = get_watchlist_service()
        success = service.clear_watchlist(current_user.id)

        if not success:
            raise HTTPException(status_code=500, detail="清空自选股失败")

        return {"success": True, "message": "自选股列表已清空"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空自选股失败: {str(e)}")


# ==================== 分组管理 API ====================


@router.get("/groups")
async def get_user_groups(current_user: User = Depends(get_current_user)) -> List[Dict]:
    """
    获取当前用户的所有自选股分组
    """
    try:
        service = get_watchlist_service()
        groups = service.get_user_groups(current_user.id)
        return groups
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分组列表失败: {str(e)}")


@router.post("/groups")
async def create_group(
    request: CreateGroupRequest, current_user: User = Depends(get_current_user)
) -> Dict:
    """
    创建新的自选股分组
    """
    try:
        service = get_watchlist_service()
        group = service.create_group(current_user.id, request.group_name)

        if not group:
            raise HTTPException(status_code=400, detail="分组创建失败")

        return {
            "success": True,
            "message": f"分组 '{request.group_name}' 创建成功",
            "group": group,
        }
    except HTTPException:
        raise
    except WatchlistError as e:
        # 捕获自定义异常并返回具体错误信息
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建分组失败: {str(e)}")


@router.put("/groups/{group_id}")
async def update_group(
    group_id: int,
    request: UpdateGroupRequest,
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    修改分组名称
    """
    try:
        service = get_watchlist_service()
        success = service.update_group(current_user.id, group_id, request.group_name)

        if not success:
            raise HTTPException(status_code=404, detail="分组不存在或更新失败")

        return {
            "success": True,
            "message": f"分组已更新为 '{request.group_name}'",
            "group_id": group_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新分组失败: {str(e)}")


@router.delete("/groups/{group_id}")
async def delete_group(
    group_id: int, current_user: User = Depends(get_current_user)
) -> Dict:
    """
    删除分组（会同时删除该分组下的所有自选股）
    """
    try:
        service = get_watchlist_service()
        success = service.delete_group(current_user.id, group_id)

        if not success:
            raise HTTPException(
                status_code=404, detail="分组不存在或无法删除（默认分组不能删除）"
            )

        return {"success": True, "message": "分组已删除", "group_id": group_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除分组失败: {str(e)}")


@router.get("/group/{group_id}")
async def get_watchlist_by_group(
    group_id: int, current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """
    获取指定分组的自选股列表
    """
    try:
        service = get_watchlist_service()
        watchlist = service.get_watchlist_by_group(current_user.id, group_id)
        return watchlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分组自选股失败: {str(e)}")


@router.put("/move")
async def move_stock_to_group(
    request: MoveStockRequest, current_user: User = Depends(get_current_user)
) -> Dict:
    """
    将股票从一个分组移动到另一个分组
    """
    try:
        service = get_watchlist_service()
        success = service.move_stock_to_group(
            user_id=current_user.id,
            symbol=request.symbol,
            from_group_id=request.from_group_id,
            to_group_id=request.to_group_id,
        )

        if not success:
            raise HTTPException(status_code=404, detail="移动失败，股票或分组不存在")

        return {
            "success": True,
            "message": f"股票 {request.symbol} 已移动到新分组",
            "symbol": request.symbol,
            "to_group_id": request.to_group_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"移动股票失败: {str(e)}")


@router.get("/with-groups")
async def get_watchlist_with_groups(
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    获取所有分组及其包含的自选股（分组视图）
    """
    try:
        service = get_watchlist_service()
        result = service.get_watchlist_with_groups(current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分组视图失败: {str(e)}")
