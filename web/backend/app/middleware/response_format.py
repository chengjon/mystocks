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

    特性:
    - 自动生成request_id
    - 自动添加code字段
    - 自动转换旧格式响应
    - 支持errors数组
    - 侵入性极低，不需要修改现有API代码
    """

    # 不需要包装的路径前缀 (例如: docs, openapi.json, 健康检查等)
    EXCLUDE_PATHS = {
        "/docs",
        "/redoc",
        "/openapi.json",
        "/static",
        "/favicon",
    }

    # 不需要包装的路径 (完全跳过的路径)
    SKIP_PATHS = {
        "/health",  # 健康检查端点保持原样
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import sys

        print(f"[DEBUG] ResponseFormatMiddleware: {request.url.path}", file=sys.stderr, flush=True)

        # 生成唯一的请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录请求开始时间
        start_time = time.time()

        # 检查是否需要跳过包装
        if self._should_skip_wrapping(request):
            return await call_next(request)

        try:
            # 调用下一个中间件或路由处理器
            response = await call_next(request)

            # 计算处理时间
            process_time = (time.time() - start_time) * 1000

            # 包装响应
            wrapped_response = await self._wrap_response(
                response=response,
                request_id=request_id,
                process_time=process_time,
                request=request,
            )

            return wrapped_response

        except Exception as e:
            # 处理未捕获的异常
            logger.error("未处理的异常 [request_id={request_id}]: {str(e)}", exc_info=True)

            error_response = create_unified_error_response(
                code=BusinessCode.INTERNAL_ERROR,
                message=ResponseMessages.INTERNAL_ERROR,
                request_id=request_id,
            )

            return JSONResponse(
                content=error_response.model_dump(mode="json", exclude_unset=True),
                status_code=500,
            )

    def _should_skip_wrapping(self, request: Request) -> bool:
        """检查是否应该跳过响应包装"""
        path = request.url.path

        # 检查完全跳过的路径
        if path in self.SKIP_PATHS:
            return True

        # 检查排除的路径前缀
        for exclude_prefix in self.EXCLUDE_PATHS:
            if path.startswith(exclude_prefix):
                return True

        return False

    async def _wrap_response(
        self,
        response: Response,
        request_id: str,
        process_time: float,
        request: Request,
    ) -> Response:
        """
        包装响应为统一格式

        支持的输入格式:
        1. UnifiedResponse - 直接返回
        2. APIResponse / ErrorResponse (旧格式) - 转换为新格式
        3. 普通字典 - 自动包装
        4. JSONResponse - 解析后包装
        """
        # 添加处理时间到响应头
        if hasattr(response, "headers"):
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            response.headers["X-Request-ID"] = request_id

        # 情况1: 已经是 UnifiedResponse，直接返回
        if hasattr(response, "body") and response.body:
            try:
                body_data = json.loads(response.body.decode())
                if self._is_unified_response(body_data):
                    return response
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        # 情况2: 检查是否是错误响应
        status_code = getattr(response, "status_code", 200)
        if status_code >= 400:
            return await self._wrap_error_response(response, request_id, status_code)

        # 情况3: 包装成功响应
        return await self._wrap_success_response(response, request_id)

    async def _wrap_success_response(self, response: Response, request_id: str) -> Response:
        """包装成功响应"""
        status_code = getattr(response, "status_code", 200)

        # 尝试获取响应体
        if hasattr(response, "body"):
            try:
                body_bytes = response.body
                if body_bytes:
                    body_data = json.loads(body_bytes.decode())

                    # 如果已经是统一响应格式，直接返回
                    if self._is_unified_response(body_data):
                        return response

                    # 如果是旧的APIResponse格式，转换为新格式
                    if self._is_old_api_response(body_data):
                        return self._convert_to_unified(body_data, request_id, status_code)

                    # 其他格式，直接包装
                    return self._wrap_as_unified(body_data, request_id, status_code)

            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                pass

        # 无法解析响应体，直接返回原始响应（避免覆盖已有的数据）
        # 这确保了当端点返回 UnifiedResponse 时，数据不会被丢失
        # BaseHTTPMiddleware 将响应包装为 StreamingResponse，无法访问原始响应体
        # 因此当无法解析时，我们信任原始响应而不是返回默认的空响应
        return response

    async def _wrap_error_response(self, response: Response, request_id: str, status_code: int) -> Response:
        """包装错误响应"""
        # 获取错误详情
        detail = getattr(response, "detail", ResponseMessages.INTERNAL_ERROR)

        # 对于Pydantic验证错误，需要特殊处理
        if isinstance(detail, list):
            errors = self._parse_validation_errors(detail)
            unified_response = create_validation_error_response(errors=errors, request_id=request_id)
        else:
            # 普通错误
            message = str(detail) if detail else ResponseMessages.INTERNAL_ERROR
            unified_response = create_unified_error_response(
                code=status_code,
                message=message,
                request_id=request_id,
            )

        return JSONResponse(
            content=unified_response.model_dump(mode="json", exclude_unset=True),
            status_code=status_code,
        )

    def _is_unified_response(self, data: Dict) -> bool:
        """检查是否已经是统一响应格式"""
        return isinstance(data, dict) and "success" in data and "code" in data and "message" in data

    def _is_old_api_response(self, data: Dict) -> bool:
        """检查是否是旧的API响应格式"""
        return isinstance(data, dict) and (("success" in data and "data" in data) or ("error" in data))

    def _convert_to_unified(self, data: Dict, request_id: str, status_code: int) -> JSONResponse:
        """将旧格式响应转换为统一格式"""
        success = data.get("success", True)

        if success:
            # 成功响应
            unified = UnifiedResponse(
                success=True,
                code=status_code,
                message=data.get("message", "操作成功"),
                data=data.get("data"),
                request_id=request_id,
            )
        else:
            # 错误响应
            error_info = data.get("error", {})
            errors = None
            if isinstance(error_info, dict):
                if "details" in error_info:
                    # 转换旧的details格式为新的errors格式
                    errors = [
                        ErrorDetail(
                            code=error_info.get("code", "UNKNOWN_ERROR"),
                            message=error_info.get("message", str(error_info.get("details", ""))),
                        )
                    ]
                else:
                    errors = [
                        ErrorDetail(
                            code=error_info.get("code", "UNKNOWN_ERROR"),
                            message=error_info.get("message", ""),
                        )
                    ]

            unified = UnifiedResponse(
                success=False,
                code=status_code,
                message=data.get("message", "操作失败"),
                data=None,
                errors=errors,
                request_id=request_id,
            )

        return JSONResponse(
            content=unified.model_dump(mode="json", exclude_unset=True),
            status_code=status_code,
        )

    def _wrap_as_unified(self, data: Any, request_id: str, status_code: int) -> JSONResponse:
        """将任意数据包装为统一格式"""
        unified = UnifiedResponse(
            success=True,
            code=status_code,
            message="操作成功",
            data=data,
            request_id=request_id,
        )

        return JSONResponse(
            content=unified.model_dump(mode="json", exclude_unset=True),
            status_code=status_code,
        )

    def _parse_validation_errors(self, errors: list) -> list[ErrorDetail]:
        """
        解析Pydantic验证错误为ErrorDetail列表

        Args:
            errors: Pydantic ValidationError.errors() 返回的错误列表

        Returns:
            ErrorDetail列表
        """
        error_details = []

        for error in errors:
            # 获取字段名
            loc = error.get("loc", [])
            field = loc[0] if loc else None

            # 获取错误类型和消息
            error_type = error.get("type", "validation_error")
            error_msg = error.get("msg", "验证失败")

            # 映射错误代码
            error_code = self._map_validation_error_code(error_type)

            error_details.append(
                ErrorDetail(
                    field=str(field) if field else None,
                    code=error_code,
                    message=error_msg,
                )
            )

        return error_details

    def _map_validation_error_code(self, error_type: str) -> str:
        """映射Pydantic错误类型到业务错误码"""
        error_map = {
            "missing": ErrorCodes.MISSING_REQUIRED_FIELD,
            "value_error.missing": ErrorCodes.MISSING_REQUIRED_FIELD,
            "value_error.str.format": ErrorCodes.INVALID_FORMAT,
            "value_error.number.not_gt": ErrorCodes.OUT_OF_RANGE,
            "value_error.number.not_ge": ErrorCodes.OUT_OF_RANGE,
            "value_error.number.not_lt": ErrorCodes.OUT_OF_RANGE,
            "value_error.number.not_le": ErrorCodes.OUT_OF_RANGE,
            "value_error.email": ErrorCodes.INVALID_FORMAT,
            "value_error.url": ErrorCodes.INVALID_FORMAT,
            "value_error.date": ErrorCodes.INVALID_FORMAT,
        }

        return error_map.get(error_type, ErrorCodes.VALIDATION_ERROR)


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
