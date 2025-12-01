"""
统一响应格式中间件

为所有API请求添加request_id，并统一处理异常响应格式。

版本: 1.0.0
日期: 2025-12-01
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.responses import ErrorCodes, ResponseMessages, create_error_response


class ResponseFormatMiddleware(BaseHTTPMiddleware):
    """统一响应格式中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成唯一的请求ID
        request_id = str(uuid.uuid4())

        # 将request_id添加到请求状态
        request.state.request_id = request_id

        # 记录请求开始时间
        start_time = time.time()

        try:
            # 调用下一个中间件或路由处理器
            response = await call_next(request)

            # 如果响应已经是JSON格式且包含统一格式，直接返回
            if isinstance(response, JSONResponse):
                return response

            # 处理其他类型的响应
            if hasattr(response, "status_code"):
                if response.status_code >= 400:
                    # 将HTTPException转换为统一错误响应
                    return self._create_error_response(
                        status_code=response.status_code,
                        detail=getattr(response, "detail", ResponseMessages.INTERNAL_ERROR),
                        request_id=request_id,
                    )
                elif response.status_code == 200:
                    # 为成功响应添加request_id
                    if hasattr(response, "body") and response.body:
                        try:
                            import json

                            body_data = json.loads(response.body.decode())
                            if isinstance(body_data, dict):
                                body_data["request_id"] = request_id
                                return JSONResponse(content=body_data, status_code=response.status_code)
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass

            return response

        except Exception as e:
            # 处理未捕获的异常
            logger = getattr(request.app.state, "logger", None)
            if logger:
                logger.error(f"未处理的异常: {str(e)}", exc_info=True)

            return create_error_response(
                error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
                message=ResponseMessages.INTERNAL_ERROR,
                details={"exception": str(e)},
                request_id=request_id,
            )

    def _create_error_response(self, status_code: int, detail: str, request_id: str) -> JSONResponse:
        """创建统一的错误响应"""
        # 根据状态码确定错误类型
        error_code = self._get_error_code(status_code)

        error_response = create_error_response(error_code=error_code, message=detail, request_id=request_id)

        return JSONResponse(content=error_response.dict(exclude_unset=True), status_code=status_code)

    def _get_error_code(self, status_code: int) -> str:
        """根据HTTP状态码获取错误代码"""
        error_map = {
            400: ErrorCodes.BAD_REQUEST,
            401: ErrorCodes.UNAUTHORIZED,
            403: ErrorCodes.FORBIDDEN,
            404: ErrorCodes.NOT_FOUND,
            405: ErrorCodes.METHOD_NOT_ALLOWED,
            422: ErrorCodes.VALIDATION_ERROR,
            429: ErrorCodes.RATE_LIMIT_EXCEEDED,
            500: ErrorCodes.INTERNAL_SERVER_ERROR,
            502: ErrorCodes.SERVICE_UNAVAILABLE,
            503: ErrorCodes.SERVICE_UNAVAILABLE,
        }

        return error_map.get(status_code, ErrorCodes.INTERNAL_SERVER_ERROR)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """处理时间记录中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始时间
        start_time = time.time()

        # 调用下一个中间件或路由处理器
        response = await call_next(request)

        # 计算处理时间（毫秒）
        process_time = (time.time() - start_time) * 1000

        # 将处理时间添加到响应头
        if hasattr(response, "headers"):
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            response.headers["X-Request-ID"] = getattr(request.state, "request_id", "unknown")

        return response
