"""
自选股管理 API
提供用户自选股的增删改查功能
"""

import re
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Path
from pydantic import BaseModel, Field, field_validator

from app.api.auth import User, get_current_user
from app.core.exceptions import BusinessException, NotFoundException
from app.openapi_config import COMMON_RESPONSES
from app.services.data_source_factory import DataSourceFactory
from app.services.watchlist_service import WatchlistError, get_watchlist_service

WATCHLIST_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    401: COMMON_RESPONSES[401],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

router = APIRouter(tags=["watchlist"], responses=WATCHLIST_ROUTE_RESPONSES)


from web.backend.app.api._watchlist_responses import (
    _success_response_spec,
    WATCHLIST_ADD_REQUEST_EXAMPLES,
    WATCHLIST_CREATE_GROUP_REQUEST_EXAMPLES,
    WATCHLIST_UPDATE_GROUP_REQUEST_EXAMPLES,
    WATCHLIST_MOVE_REQUEST_EXAMPLES,
    WATCHLIST_NOTES_REQUEST_EXAMPLES,
    WATCHLIST_ITEM_EXAMPLE,
    WATCHLIST_GROUP_EXAMPLE,
    WATCHLIST_GROUP_STOCK_EXAMPLE,
    WATCHLIST_LIST_RESPONSES,
    WATCHLIST_SYMBOLS_RESPONSES,
    WATCHLIST_REMOVE_RESPONSES,
    WATCHLIST_CHECK_RESPONSES,
    WATCHLIST_COUNT_RESPONSES,
    WATCHLIST_CLEAR_RESPONSES,
    WATCHLIST_GROUP_LIST_RESPONSES,
    WATCHLIST_GROUP_DELETE_RESPONSES,
    WATCHLIST_GROUP_DETAIL_RESPONSES,
    WATCHLIST_WITH_GROUPS_RESPONSES,
    WATCHLIST_ADD_RESPONSES,
    WATCHLIST_NOTES_RESPONSES,
    WATCHLIST_GROUP_CREATE_RESPONSES,
    WATCHLIST_GROUP_UPDATE_RESPONSES,
    WATCHLIST_MOVE_RESPONSES
)



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
            raise ValueError(f"交易所代码无效，支持的交易所: {', '.join(valid_exchanges)}")
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


@router.get(
    "/",
    response_model=List[WatchlistItem],
    description="获取当前登录用户的自选股列表，返回股票代码、展示名称、交易所、备注和加入时间。",
    responses=WATCHLIST_LIST_RESPONSES,
)
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
            raise BusinessException(
                detail=result.get("error", "获取自选股列表失败"),
                status_code=500,
                error_code="WATCHLIST_RETRIEVAL_FAILED",
            )

        return result.get("data", [])

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(
            detail=f"获取自选股列表失败: {str(e)}", status_code=500, error_code="WATCHLIST_RETRIEVAL_FAILED"
        )


@router.get(
    "/symbols",
    response_model=List[str],
    description="获取当前登录用户自选股中的全部股票代码，适用于批量校验、联动筛选或本地缓存刷新。",
    responses=WATCHLIST_SYMBOLS_RESPONSES,
)
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
            raise BusinessException(
                detail=result.get("error", "获取自选股代码列表失败"),
                status_code=500,
                error_code="WATCHLIST_SYMBOLS_RETRIEVAL_FAILED",
            )

        return result.get("data", [])

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(
            detail=f"获取自选股代码列表失败: {str(e)}", status_code=500, error_code="WATCHLIST_SYMBOLS_RETRIEVAL_FAILED"
        )


@router.post(
    "/add",
    summary="添加自选股",
    description="添加股票到当前用户自选股列表，并支持按分组名称自动归档到指定分组。",
    responses=WATCHLIST_ADD_RESPONSES,
)
async def add_to_watchlist(
    request: AddWatchlistRequest = Body(..., openapi_examples=WATCHLIST_ADD_REQUEST_EXAMPLES),
    current_user: User = Depends(get_current_user),
) -> Dict:
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
            raise BusinessException(
                detail=result.get("error", "添加自选股失败"), status_code=500, error_code="STOCK_ADDITION_FAILED"
            )

        return {
            "success": True,
            "message": result.get("message", "已添加到自选股"),
            "symbol": request.symbol,
            "group_name": request.group_name if request.group_name else "默认分组",
        }

    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=f"添加自选股失败: {str(e)}", status_code=500, error_code="STOCK_ADDITION_FAILED")


@router.delete(
    "/remove/{symbol}",
    description="从当前用户自选股列表中移除指定股票，适用于取消关注、误加回滚或策略切换场景。",
    responses=WATCHLIST_REMOVE_RESPONSES,
)
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
            raise NotFoundException(resource="自选股", identifier="查询条件")

        return {"success": True, "message": "已从自选股移除", "symbol": symbol}
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=f"删除自选股失败: {str(e)}", status_code=500, error_code="STOCK_DELETION_FAILED")


@router.get(
    "/check/{symbol}",
    description="检查指定股票是否已存在于当前用户自选股列表中，便于搜索页和详情页展示关注状态。",
    responses=WATCHLIST_CHECK_RESPONSES,
)
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
            raise BusinessException(
                detail=result.get("error", "检查自选股失败"), status_code=500, error_code="STOCK_CHECK_FAILED"
            )

        return {"symbol": symbol, "is_in_watchlist": result.get("data", {}).get("is_in_watchlist", False)}
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=f"检查自选股失败: {str(e)}", status_code=500, error_code="STOCK_CHECK_FAILED")


@router.put(
    "/notes/{symbol}",
    summary="更新自选股备注",
    description="更新指定自选股的备注信息，便于记录交易计划或观察结论。",
    responses=WATCHLIST_NOTES_RESPONSES,
)
async def update_watchlist_notes(
    request: UpdateWatchlistNotesRequest = Body(..., openapi_examples=WATCHLIST_NOTES_REQUEST_EXAMPLES),
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
            raise NotFoundException(resource="自选股", identifier="查询条件")

        return {"success": True, "message": "备注已更新", "symbol": symbol}
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=f"更新备注失败: {str(e)}", status_code=500, error_code="NOTE_UPDATE_FAILED")


@router.get(
    "/count",
    description="获取当前用户自选股总数，可用于首页统计卡、容量提示和自选池规模监控。",
    responses=WATCHLIST_COUNT_RESPONSES,
)
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
            raise BusinessException(
                detail=result.get("error", "获取自选股数量失败"),
                status_code=500,
                error_code="WATCHLIST_COUNT_RETRIEVAL_FAILED",
            )

        return {"count": result.get("data", {}).get("count", 0)}
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(
            detail=f"获取自选股数量失败: {str(e)}", status_code=500, error_code="WATCHLIST_COUNT_RETRIEVAL_FAILED"
        )


@router.delete(
    "/clear",
    description="清空当前登录用户的全部自选股记录，常用于重建观察池或批量重置个人配置。",
    responses=WATCHLIST_CLEAR_RESPONSES,
)
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
            raise BusinessException(
                detail=result.get("error", "清空自选股失败"), status_code=500, error_code="WATCHLIST_CLEAR_FAILED"
            )

        return {"success": True, "message": "自选股列表已清空"}
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(
            detail=f"清空自选股失败: {str(e)}", status_code=500, error_code="WATCHLIST_CLEAR_FAILED"
        )


# ==================== 分组管理 API ====================


@router.get(
    "/groups",
    description="获取当前用户已创建的全部自选股分组，用于分组筛选、分组迁移和分组视图初始化。",
    responses=WATCHLIST_GROUP_LIST_RESPONSES,
)
async def get_user_groups(current_user: User = Depends(get_current_user)) -> List[Dict]:
    """
    获取当前用户的所有自选股分组
    """
    try:
        service = get_watchlist_service()
        groups = service.get_user_groups(current_user.id)
        return groups
    except Exception as e:
        raise BusinessException(
            detail=f"获取分组列表失败: {str(e)}", status_code=500, error_code="GROUP_LIST_RETRIEVAL_FAILED"
        )


@router.post(
    "/groups",
    summary="创建自选股分组",
    description="创建新的自选股分组，用于管理不同主题、策略或观察清单。",
    responses=WATCHLIST_GROUP_CREATE_RESPONSES,
)
async def create_group(
    request: CreateGroupRequest = Body(..., openapi_examples=WATCHLIST_CREATE_GROUP_REQUEST_EXAMPLES),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    创建新的自选股分组
    """
    try:
        service = get_watchlist_service()
        group = service.create_group(current_user.id, request.group_name)

        if not group:
            raise BusinessException(detail="分组创建失败", status_code=400, error_code="GROUP_CREATION_FAILED")

        return {
            "success": True,
            "message": f"分组 '{request.group_name}' 创建成功",
            "group": group,
        }
    except (BusinessException, NotFoundException):
        raise
    except WatchlistError as e:
        # 捕获自定义异常并返回具体错误信息
        raise BusinessException(detail=str(e), status_code=400, error_code="VALIDATION_ERROR")
    except Exception as e:
        raise BusinessException(detail=f"创建分组失败: {str(e)}", status_code=500, error_code="GROUP_CREATION_FAILED")


@router.put(
    "/groups/{group_id}",
    summary="更新自选股分组",
    description="修改指定自选股分组的名称，并保留该分组下已有的股票成员。",
    responses=WATCHLIST_GROUP_UPDATE_RESPONSES,
)
async def update_group(
    request: UpdateGroupRequest = Body(..., openapi_examples=WATCHLIST_UPDATE_GROUP_REQUEST_EXAMPLES),
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
            raise NotFoundException(resource="分组", identifier="查询条件")

        return {
            "success": True,
            "message": f"分组已更新为 '{request.group_name}'",
            "group_id": group_id,
        }
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=f"更新分组失败: {str(e)}", status_code=500, error_code="GROUP_UPDATE_FAILED")


@router.delete(
    "/groups/{group_id}",
    description="删除指定自选股分组，并同步移除该分组下成员；默认分组不允许删除。",
    responses=WATCHLIST_GROUP_DELETE_RESPONSES,
)
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
            raise NotFoundException(resource="分组", identifier="查询条件（默认分组不能删除）")

        return {"success": True, "message": "分组已删除", "group_id": group_id}
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=f"删除分组失败: {str(e)}", status_code=500, error_code="GROUP_DELETION_FAILED")


@router.get(
    "/group/{group_id}",
    description="获取指定分组下的全部自选股成员，便于按主题、策略或观察池查看清单内容。",
    responses=WATCHLIST_GROUP_DETAIL_RESPONSES,
)
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
        raise BusinessException(
            detail=f"获取分组自选股失败: {str(e)}", status_code=500, error_code="GROUP_STOCKS_RETRIEVAL_FAILED"
        )


@router.put(
    "/move",
    summary="移动自选股分组",
    description="将指定股票从一个自选股分组移动到另一个分组，便于动态调整观察清单。",
    responses=WATCHLIST_MOVE_RESPONSES,
)
async def move_stock_to_group(
    request: MoveStockRequest = Body(..., openapi_examples=WATCHLIST_MOVE_REQUEST_EXAMPLES),
    current_user: User = Depends(get_current_user),
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
            raise NotFoundException(resource="股票或分组", identifier="移动操作")

        return {
            "success": True,
            "message": f"股票 {request.symbol} 已移动到新分组",
            "symbol": request.symbol,
            "to_group_id": request.to_group_id,
        }
    except (BusinessException, NotFoundException):
        raise
    except Exception as e:
        raise BusinessException(detail=f"移动股票失败: {str(e)}", status_code=500, error_code="STOCK_MOVE_FAILED")


@router.get(
    "/with-groups",
    description="获取所有分组及其包含的自选股明细，返回适用于分组树或看板视图的聚合结果。",
    responses=WATCHLIST_WITH_GROUPS_RESPONSES,
)
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
        raise BusinessException(
            detail=f"获取分组视图失败: {str(e)}", status_code=500, error_code="GROUP_VIEW_RETRIEVAL_FAILED"
        )
