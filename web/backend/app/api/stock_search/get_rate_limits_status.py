"""Stock-search rate-limit status endpoint."""

from __future__ import annotations

import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.auth import User, get_current_user
from app.api.stock_search.openapi_metadata import RATE_LIMIT_STATUS_RESPONSES
from app.api.stock_search.stock_search_support import check_admin_privileges, search_operation_count
from app.core.exceptions import BusinessException, ForbiddenException
from app.core.responses import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/rate-limits/status",
    response_model=APIResponse,
    summary="查询股票搜索限流状态",
    description="管理员查看股票搜索接口的限流计数，可按用户筛选当前分钟和近几分钟的请求命中情况。",
    responses=RATE_LIMIT_STATUS_RESPONSES,
)
async def get_rate_limits_status(
    user_id: Optional[int] = Query(None, description="指定用户 ID；为空时返回所有用户的限流状态"),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    """Return stock-search rate-limit counters for one user or all users."""
    try:
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized rate limits access attempt by user: %s", current_user.username)
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        current_minute = int(time.time() / 60)

        if user_id is not None:
            user_limits = search_operation_count.get(user_id, {})
            return APIResponse(
                success=True,
                data={
                    "user_id": user_id,
                    "rate_limits": user_limits,
                    "total_minutes": len(user_limits),
                    "current_minute_requests": user_limits.get(current_minute, 0),
                },
                message=f"用户 {user_id} 的频率限制状态",
            )

        all_limits = {
            uid: {
                "rate_limits": limits,
                "total_minutes": len(limits),
                "current_minute_requests": limits.get(current_minute, 0),
            }
            for uid, limits in search_operation_count.items()
        }

        return APIResponse(
            success=True,
            data={"total_users": len(all_limits), "user_limits": all_limits},
            message="所有用户的频率限制状态",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to get rate limits status for admin %s", current_user.username)
        raise BusinessException(
            detail="获取频率限制状态失败", status_code=500, error_code="RATE_LIMIT_STATUS_RETRIEVAL_FAILED"
        )
