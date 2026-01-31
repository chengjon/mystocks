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

# Use environment variable for environment check instead of settings
import os

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
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )


# 模块级便捷函数
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(name: str = "MyStocks") -> StructuredLogger:
    """获取结构化日志记录器"""
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name=name)
    return _loggers[name]


def get_trace_id() -> Optional[str]:
    """获取当前trace_id"""
    return trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
    """设置trace_id"""
    trace_id_var.set(trace_id)


def get_request_id() -> Optional[str]:
    """获取当前request_id"""
    return request_id_var.get()


def set_request_id(request_id: str) -> None:
    """设置request_id"""
    request_id_var.set(request_id)


def set_user_id(user_id: str) -> None:
    """设置user_id"""
    user_id_var.set(user_id)


def clear_context() -> None:
    """清除上下文变量"""
    trace_id_var.set(None)
    request_id_var.set(None)
    user_id_var.set(None)


class LogContext:
    """日志上下文管理器"""

    def __init__(
        self,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        self.prev_trace_id = trace_id_var.get()
        self.prev_request_id = request_id_var.get()
        self.prev_user_id = user_id_var.get()
        self.new_trace_id = trace_id or self.prev_trace_id
        self.new_request_id = request_id or self.prev_request_id
        self.new_user_id = user_id or self.prev_user_id

    def __enter__(self) -> "LogContext":
        if self.new_trace_id:
            trace_id_var.set(self.new_trace_id)
        if self.new_request_id:
            request_id_var.set(self.new_request_id)
        if self.new_user_id:
            user_id_var.set(self.new_user_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        trace_id_var.set(self.prev_trace_id)
        request_id_var.set(self.prev_request_id)
        user_id_var.set(self.prev_user_id)


class RequestLoggingMiddleware:
    """请求日志中间件"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())[:8]
        set_request_id(request_id)

        await self.app(scope, receive, send)

