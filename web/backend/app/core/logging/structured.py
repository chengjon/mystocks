"""
Structured Logging Module for MyStocks
Provides context-aware logging with trace_id and request_id injection
"""

import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger as loguru_logger

from app.core.config import settings

trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


class StructuredLogger:
    """结构化日志记录器"""

    def __init__(
        self,
        name: str = "MyStocks",
        json_format: bool = True,
        log_dir: Optional[Path] = None,
    ):
        self.name = name
        self._logger = loguru_logger.bind(service=name)
        self._setup_logger(json_format, log_dir)

    def _setup_logger(self, json_format: bool, log_dir: Optional[Path]):
        """配置日志记录器"""
        loguru_logger.remove()

        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_format = self._get_log_format(json_format)

        if json_format:
            loguru_logger.add(
                log_dir / "mystocks_{time:YYYY-MM-DD}.json",
                format="{message}",
                level="INFO",
                rotation="00:00",
                retention="7 days",
                compression="zip",
                serialize=True,
            )
            loguru_logger.add(
                log_dir / "mystocks_error_{time:YYYY-MM-DD}.json",
                format="{message}",
                level="ERROR",
                rotation="00:00",
                retention="30 days",
                compression="zip",
                serialize=True,
            )
        else:
            loguru_logger.add(
                log_dir / "mystocks_{time:YYYY-MM-DD}.log",
                format=log_format,
                level="DEBUG",
                rotation="00:00",
                retention="7 days",
                compression="zip",
            )

        loguru_logger.add(
            sys.stderr,
            format=log_format,
            level="INFO",
            colorize=True,
        )

    def _get_log_format(self, json_format: bool) -> str:
        """获取日志格式"""
        if json_format:
            return "{message}"

        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    def _get_base_fields(self) -> Dict[str, Any]:
        """获取基础日志字段"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.name,
            "environment": getattr(settings, "ENVIRONMENT", "development"),
            "trace_id": trace_id_var.get(),
            "request_id": request_id_var.get(),
            "user_id": user_id_var.get(),
        }

    def _log(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ):
        """内部日志方法"""
        fields = self._get_base_fields()
        if extra:
            fields.update(extra)

        log_method = getattr(self._logger.opt(depth=1), level.lower())
        log_method(message, **fields, exc_info=exc_info)

    def debug(self, message: str, **extra):
        """DEBUG级别日志"""
        self._log("DEBUG", message, extra)

    def info(self, message: str, **extra):
        """INFO级别日志"""
        self._log("INFO", message, extra)

    def success(self, message: str, **extra):
        """SUCCESS级别日志"""
        self._log("SUCCESS", message, extra)

    def warning(self, message: str, **extra):
        """WARNING级别日志"""
        self._log("WARNING", message, extra)

    def error(self, message: str, exc_info: bool = True, **extra):
        """ERROR级别日志"""
        self._log("ERROR", message, extra, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = True, **extra):
        """CRITICAL级别日志"""
        self._log("CRITICAL", message, extra, exc_info=exc_info)

    def request(self, message: str, **extra):
        """请求日志专用"""
        self._log("INFO", message, {"log_type": "request", **extra})

    def database(self, message: str, **extra):
        """数据库日志专用"""
        self._log("INFO", message, {"log_type": "database", **extra})

    def performance(self, message: str, **extra):
        """性能日志专用"""
        self._log("INFO", message, {"log_type": "performance", **extra})

    def bind(self, **kwargs) -> "StructuredLogger":
        """绑定额外字段"""
        new_logger = StructuredLogger(self.name)
        new_logger._logger = self._logger.bind(**kwargs)
        return new_logger


class LogContext:
    """日志上下文管理器"""

    def __init__(
        self,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        self.trace_id = trace_id or f"trace-{uuid.uuid4().hex[:16]}"
        self.request_id = request_id or f"req-{uuid.uuid4().hex[:12]}"
        self.user_id = user_id
        self._tokens = []

    def __enter__(self):
        self._tokens.append(trace_id_var.set(self.trace_id))
        self._tokens.append(request_id_var.set(self.request_id))
        if self.user_id:
            self._tokens.append(user_id_var.set(self.user_id))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        trace_id_var.reset(self._tokens[0])
        request_id_var.reset(self._tokens[1])
        if self.user_id:
            user_id_var.reset(self._tokens[2])
        return False


def get_trace_id() -> str:
    """获取当前trace_id"""
    return trace_id_var.get() or f"trace-{uuid.uuid4().hex[:16]}"


def get_request_id() -> str:
    """获取当前request_id"""
    return request_id_var.get() or f"req-{uuid.uuid4().hex[:12]}"


def set_trace_id(trace_id: str):
    """设置trace_id"""
    trace_id_var.set(trace_id)


def set_request_id(request_id: str):
    """设置request_id"""
    request_id_var.set(request_id)


def set_user_id(user_id: str):
    """设置user_id"""
    user_id_var.set(user_id)


def clear_context():
    """清除上下文"""
    trace_id_var.set(None)
    request_id_var.set(None)
    user_id_var.set(None)


_global_logger: Optional[StructuredLogger] = None


def get_logger(name: str = "MyStocks") -> StructuredLogger:
    """获取全局日志记录器"""
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger(name)
    return _global_logger.bind(name=name)


class RequestLoggingMiddleware:
    """请求日志中间件"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = f"req-{uuid.uuid4().hex[:12]}"
        trace_id = f"trace-{uuid.uuid4().hex[:16]}"

        set_request_id(request_id)
        set_trace_id(trace_id)

        loguru_logger.info(
            "Request started",
            request_id=request_id,
            trace_id=trace_id,
            method=scope["method"],
            path=scope["path"],
        )

        await self.app(scope, receive, send)
