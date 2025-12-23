"""
API监控中间件
自动收集所有API请求的性能和数据质量指标
"""

import time
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.api_monitoring import get_monitor

logger = structlog.get_logger()


class APIMonitoringMiddleware(BaseHTTPMiddleware):
    """API监控中间件 - 记录所有请求的性能指标"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录指标"""
        # 记录请求开始时间
        start_time = time.time()

        # 提取端点信息
        endpoint = request.url.path
        method = request.method

        # 初始化变量
        status_code = 500
        error_message = None
        response_data = None

        try:
            # 调用下一个中间件/处理器
            response = await call_next(request)
            status_code = response.status_code

            # 如果是JSON响应，尝试提取响应数据用于验证
            if response.media_type and "application/json" in response.media_type:
                # 如果响应有body，读取它
                # 注意：这可能会影响性能，所以只在需要时启用
                pass

            return response

        except Exception as e:
            # 捕获异常
            status_code = 500
            error_message = str(e)
            logger.error(
                f"Unhandled exception in {method} {endpoint}",
                error=error_message,
                exc_info=True,
            )
            # 重新抛出异常以让FastAPI处理
            raise

        finally:
            # 计算响应时间
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒

            # 记录指标
            monitor = get_monitor()
            monitor.record_request(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                error_message=error_message,
            )


def setup_monitoring_middleware(app):
    """设置监控中间件"""
    app.add_middleware(APIMonitoringMiddleware)
    logger.info("API Monitoring middleware enabled")
