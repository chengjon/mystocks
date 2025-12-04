"""
自选股管理 API
提供用户自选股的增删改查功能
"""

import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.api.auth import User, get_current_user
from app.services.data_source_factory import DataSourceFactory

router = APIRouter()


class WatchlistItem(BaseModel):
    """自选股条目"""

    id: int = Field(..., description="条目ID", ge=1)
    symbol: str = Field(..., description="股票代码", min_length=1, max_length=20)
    display_name: Optional[str] = Field(None, description="显示名称", max_length=100)
    exchange: Optional[str] = Field(None, description="交易所", max_length=20)
    added_at: str = Field(..., description="添加时间", pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
    notes: Optional[str] = Field(None, description="备注", max_length=500)


class AddWatchlistRequest(BaseModel):
    """添加自选股请求"""

    symbol: str = Field(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$")
    display_name: Optional[str] = Field(None, description="显示名称", max_length=100)
    exchange: Optional[str] = Field(None, description="交易所", max_length=20, pattern=r"^[A-Z]+$")
    market: Optional[str] = Field(None, description="市场（CN/HK/US）", max_length=5, pattern=r"^(CN|HK|US)$")
    notes: Optional[str] = Field(None, description="备注", max_length=500)
    group_id: Optional[int] = Field(None, description="分组ID", ge=1)
    group_name: Optional[str] = Field(None, description="分组名称（如果不存在则自动创建）", min_length=1, max_length=50)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """验证股票代码格式"""
        if v.startswith("."):
            raise ValueError("股票代码不能以点开头")
        if ".." in v:
            raise ValueError("股票代码不能包含连续的点")
        return v.upper()

    @field_validator("exchange")
    @classmethod
    def validate_exchange(cls, v: Optional[str]) -> Optional[str]:
        """验证交易所代码"""
        if v is None:
            return v
        valid_exchanges = ["NYSE", "NASDAQ", "AMEX", "SSE", "SZSE", "HKEX", "NSE", "BSE"]
        if v.upper() not in valid_exchanges:
            raise ValueError(f'交易所代码无效，支持的交易所: {", ".join(valid_exchanges)}')
        return v.upper()

    @field_validator("group_name")
    @classmethod
    def validate_group_name(cls, v: Optional[str]) -> Optional[str]:
        """验证分组名称"""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("分组名称不能为空")
        # 检查是否包含特殊字符
        if re.search(r'[<>"\'/\\]', v):
            raise ValueError("分组名称不能包含特殊字符: < > \" ' / \\")
        return v.strip()


class UpdateWatchlistNotesRequest(BaseModel):
    """更新备注请求"""

    notes: str = Field(..., description="备注内容", min_length=0, max_length=500)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str) -> str:
        """验证备注内容"""
        # 检查是否包含恶意脚本标签
        if re.search(r"<script|javascript:|onload=|onerror=", v, re.IGNORECASE):
            raise ValueError("备注内容包含不安全的脚本或标签")
        return v.strip()


class CreateGroupRequest(BaseModel):
    """创建分组请求"""

    group_name: str = Field(..., description="分组名称", min_length=1, max_length=50, pattern=r'^[^\s<>"\'/\\]+$')

    @field_validator("group_name")
    @classmethod
    def validate_group_name(cls, v: str) -> str:
        """验证分组名称"""
        if not v.strip():
            raise ValueError("分组名称不能为空")
        # 检查是否包含特殊字符
        if re.search(r'[<>"\'/\\]', v):
            raise ValueError("分组名称不能包含特殊字符: < > \" ' / \\")
        # 检查是否为纯空格
        if v.isspace():
            raise ValueError("分组名称不能全是空格")
        return v.strip()


class UpdateGroupRequest(BaseModel):
    """更新分组请求"""

    group_name: str = Field(..., description="新的分组名称", min_length=1, max_length=50, pattern=r'^[^\s<>"\'/\\]+$')

    @field_validator("group_name")
    @classmethod
    def validate_group_name(cls, v: str) -> str:
        """验证分组名称"""
        if not v.strip():
            raise ValueError("分组名称不能为空")
        # 检查是否包含特殊字符
        if re.search(r'[<>"\'/\\]', v):
            raise ValueError("分组名称不能包含特殊字符: < > \" ' / \\")
        return v.strip()


class MoveStockRequest(BaseModel):
    """移动股票请求"""

    symbol: str = Field(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$")
    from_group_id: int = Field(..., description="原分组ID", ge=1)
    to_group_id: int = Field(..., description="目标分组ID", ge=1)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """验证股票代码格式"""
        if v.startswith("."):
            raise ValueError("股票代码不能以点开头")
        if ".." in v:
            raise ValueError("股票代码不能包含连续的点")
        return v.upper()

    @field_validator("to_group_id")
    @classmethod
    def validate_group_ids(cls, v: int, info) -> int:
        """验证不能移动到同一个分组"""
        if "from_group_id" in info.data and v == info.data["from_group_id"]:
            raise ValueError("不能移动到同一个分组")
        return v


@router.get("/", response_model=List[WatchlistItem])
async def get_my_watchlist(
    current_user: User = Depends(get_current_user),
) -> List[Dict]:
    """
    获取当前用户的自选股列表
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        watchlist_adapter = await data_source_factory.get_data_source("watchlist")

        params = {"user_id": current_user.id, "action": "list"}

        result = await watchlist_adapter.get_data("list", params)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "获取自选股列表失败"))

        return result.get("data", [])

    except HTTPException:
        raise
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
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        watchlist_adapter = await data_source_factory.get_data_source("watchlist")

        params = {"user_id": current_user.id, "action": "symbols"}

        result = await watchlist_adapter.get_data("symbols", params)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "获取自选股代码列表失败"))

        return result.get("data", [])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取自选股代码列表失败: {str(e)}")


@router.post("/add")
async def add_to_watchlist(request: AddWatchlistRequest, current_user: User = Depends(get_current_user)) -> Dict:
    """
    添加股票到自选股列表
    支持通过 group_id 或 group_name 指定分组
    如果提供 group_name 且分组不存在，会自动创建
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        watchlist_adapter = await data_source_factory.get_data_source("watchlist")

        params = {
            "user_id": current_user.id,
            "symbol": request.symbol,
            "display_name": request.display_name,
            "exchange": request.exchange,
            "market": request.market,
            "notes": request.notes,
            "group_id": request.group_id,
            "group_name": request.group_name,
            "action": "add",
        }

        result = await watchlist_adapter.get_data("add", params)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "添加自选股失败"))

        return {
            "success": True,
            "message": result.get("message", "已添加到自选股"),
            "symbol": request.symbol,
            "group_name": request.group_name if request.group_name else "默认分组",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加自选股失败: {str(e)}")


@router.delete("/remove/{symbol}")
async def remove_from_watchlist(
    symbol: str = Path(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    从自选股列表中删除股票
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        watchlist_adapter = await data_source_factory.get_data_source("watchlist")

        params = {"user_id": current_user.id, "symbol": symbol, "action": "remove"}

        result = await watchlist_adapter.get_data("remove", params)

        if not result.get("success", False):
            raise HTTPException(status_code=404, detail=result.get("error", "自选股不存在或删除失败"))

        return {"success": True, "message": "已从自选股移除", "symbol": symbol}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除自选股失败: {str(e)}")


@router.get("/check/{symbol}")
async def check_in_watchlist(
    symbol: str = Path(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    检查股票是否在自选股列表中
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        watchlist_adapter = await data_source_factory.get_data_source("watchlist")

        params = {"user_id": current_user.id, "symbol": symbol, "action": "check"}

        result = await watchlist_adapter.get_data("check", params)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "检查自选股失败"))

        return {"symbol": symbol, "is_in_watchlist": result.get("data", {}).get("is_in_watchlist", False)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查自选股失败: {str(e)}")


@router.put("/notes/{symbol}")
async def update_watchlist_notes(
    request: UpdateWatchlistNotesRequest,
    symbol: str = Path(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$"),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    更新自选股备注
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        watchlist_adapter = await data_source_factory.get_data_source("watchlist")

        params = {"user_id": current_user.id, "symbol": symbol, "notes": request.notes, "action": "update_notes"}

        result = await watchlist_adapter.get_data("update_notes", params)

        if not result.get("success", False):
            raise HTTPException(status_code=404, detail=result.get("error", "自选股不存在或更新失败"))

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
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        watchlist_adapter = await data_source_factory.get_data_source("watchlist")

        params = {"user_id": current_user.id, "action": "count"}

        result = await watchlist_adapter.get_data("count", params)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "获取自选股数量失败"))

        return {"count": result.get("data", {}).get("count", 0)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取自选股数量失败: {str(e)}")


@router.delete("/clear")
async def clear_watchlist(current_user: User = Depends(get_current_user)) -> Dict:
    """
    清空当前用户的自选股列表
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        watchlist_adapter = await data_source_factory.get_data_source("watchlist")

        params = {"user_id": current_user.id, "action": "clear"}

        result = await watchlist_adapter.get_data("clear", params)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "清空自选股失败"))

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
async def create_group(request: CreateGroupRequest, current_user: User = Depends(get_current_user)) -> Dict:
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
    request: UpdateGroupRequest,
    group_id: int = Path(..., description="分组ID", ge=1),
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
    group_id: int = Path(..., description="分组ID", ge=1), current_user: User = Depends(get_current_user)
) -> Dict:
    """
    删除分组（会同时删除该分组下的所有自选股）
    """
    try:
        service = get_watchlist_service()
        success = service.delete_group(current_user.id, group_id)

        if not success:
            raise HTTPException(status_code=404, detail="分组不存在或无法删除（默认分组不能删除）")

        return {"success": True, "message": "分组已删除", "group_id": group_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除分组失败: {str(e)}")


@router.get("/group/{group_id}")
async def get_watchlist_by_group(
    group_id: int = Path(..., description="分组ID", ge=1), current_user: User = Depends(get_current_user)
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
async def move_stock_to_group(request: MoveStockRequest, current_user: User = Depends(get_current_user)) -> Dict:
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
