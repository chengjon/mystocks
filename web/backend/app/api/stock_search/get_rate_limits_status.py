"""
# pylint: disable=no-member  # TODO: 修复异常类的 to_dict 方法
股票搜索 API
提供统一的股票搜索、报价和新闻接口
支持 A 股和 H 股（港股）

安全级别：分级别访问控制
- User endpoints: 股票搜索、报价、新闻（需要用户认证）
- Admin endpoints: 缓存管理、批量操作（需要管理员权限）
"""

import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field, ValidationError, field_validator

from app.api.auth import User, get_current_user
from app.core.circuit_breaker_manager import get_circuit_breaker  # 导入熔断器
from app.core.exceptions import BusinessException, ForbiddenException, NotFoundException, ValidationException
from app.core.responses import APIResponse, create_error_response
from app.schema import StockListQueryModel  # 导入P0改进的验证模型
from app.services.stock_search_service import get_stock_search_service
from src.core.exceptions import (
    DatabaseNotFoundError,
    DatabaseOperationError,
    DataFetchError,
    DataValidationError,
    NetworkError,
    ServiceError,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiting for search operations
search_operation_count = {}

# Search analytics
search_analytics = []

@router.get("/rate-limits/status", response_model=APIResponse)
async def get_rate_limits_status(
    user_id: Optional[int] = Query(None, description="查询特定用户的限制状态"),
    current_user: User = Depends(get_current_user),
):
    """
    获取访问频率限制状态

    Security:
        - 仅管理员可访问
        - 需要管理员权限
    """
    try:
        # 检查管理员权限
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized rate limits access attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 获取频率限制状态
        if user_id:
            # 查询特定用户
            user_limits = search_operation_count.get(user_id, {})
            return APIResponse(
                success=True,
                data={"user_id": user_id, "rate_limits": user_limits, "total_minutes": len(user_limits)},
                message=f"用户 {user_id} 的频率限制状态",
            )
        else:
            # 查询所有用户
            all_limits = {}
            for uid, limits in search_operation_count.items():
                all_limits[uid] = {
                    "rate_limits": limits,
                    "total_minutes": len(limits),
                    "current_minute_requests": limits.get(int(time.time() / 60), 0),
                }

            return APIResponse(
                success=True,
                data={"total_users": len(all_limits), "user_limits": all_limits},
                message="所有用户的频率限制状态",
            )

    except HTTPException:
        raise
    except (DatabaseNotFoundError, DataValidationError) as e:
        logger.error(
            f"Failed to get rate limits status for admin {current_user.username}: {e.message}", extra=e.to_dict()
        )
        raise BusinessException(
            detail="获取频率限制状态失败", status_code=500, error_code="RATE_LIMIT_STATUS_RETRIEVAL_FAILED"
        )
    except Exception:
        logger.error("Failed to get rate limits status for admin {current_user.username}: {str(e)}")
        raise BusinessException(
            detail="获取频率限制状态失败", status_code=500, error_code="RATE_LIMIT_STATUS_RETRIEVAL_FAILED"
        )


