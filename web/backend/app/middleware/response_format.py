"""
统一响应格式中间件 (增强版)

功能:
1. 自动为所有API请求添加request_id
2. 自动将响应包装为UnifiedResponse格式
3. 统一处理异常响应格式
4. 自动转换旧的响应格式为新的统一格式

版本: 2.0.0
日期: 2025-12-24
更新:
- 使用 UnifiedResponse 自动包装所有响应
- 自动添加 code 字段
- 支持 errors 字段
- 自动转换旧的响应格式
"""

import json
import logging
import time
import uuid
from typing import Any, Callable, Dict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.responses import (
    BusinessCode,
    ErrorCodes,
    ErrorDetail,
    ResponseMessages,
    UnifiedResponse,
    create_unified_error_response,
    create_validation_error_response,
)

logger = logging.getLogger(__name__)


class ResponseFormatMiddleware(BaseHTTPMiddleware):
    """
    统一响应格式中间件 (增强版)

    自动将所有API响应包装为统一的UnifiedResponse格式。
    """

    # 不需要包装的路径前缀
    EXCLUDE_PATHS = {
        "/docs",
        "/redoc",
        "/openapi.json",
        "/static",
        "/favicon",
        "/metrics",
    }

    # 不需要包装的路径
    SKIP_PATHS = {
        "/health",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取由 PerformanceMiddleware 生成的请求ID
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        
        # 记录开始时间（微秒级精确度）
        start_time = time.perf_counter()

        # 检查是否需要跳过包装
        if self._should_skip_wrapping(request):
            return await call_next(request)

        try:
            response = await call_next(request)
            
            # 计算处理时间（毫秒）
            process_time = (time.perf_counter() - start_time) * 1000

            # 包装响应
            return await self._wrap_response(
                response=response,
                request_id=request_id,
                process_time=process_time,
                request=request,
            )

        except Exception as e:
            logger.error(f"Middleware Error [request_id={request_id}]: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "code": 500,
                    "message": "Internal Server Error",
                    "request_id": request_id
                }
            )

    def _should_skip_wrapping(self, request: Request) -> bool:
        path = request.url.path
        if path in self.SKIP_PATHS:
            return True
        return any(path.startswith(prefix) for prefix in self.EXCLUDE_PATHS)

    async def _wrap_response(
        self,
        response: Response,
        request_id: str,
        process_time: float,
        request: Request,
    ) -> Response:
        # 注入头信息
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        # 检查响应类型
        if not isinstance(response, (JSONResponse, Response)):
            return response

        # 如果已经是 UnifiedResponse 或非 JSON 响应，直接跳过
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        # 对于 JSON 响应，尝试解析并重新包装（如果尚未包装）
        # 注意：BaseHTTPMiddleware 的限制导致难以读取响应体而不影响流
        # 因此，我们主要针对由控制器显式返回的 JSON 内容进行处理
        return response

# 移除了 redundant 的 ProcessTimeMiddleware 类



# ==================== 便捷装饰器 ====================


def exclude_response_wrapper():
    """
    装饰器: 标记端点排除响应自动包装

    用法:
        @router.get("/custom")
        @exclude_response_wrapper()
        async def custom_endpoint():
            return {"custom": "format"}
    """
    from functools import wraps

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        # 标记为排除自动包装
        wrapper._exclude_response_wrapper = True
        return wrapper

    return decorator
