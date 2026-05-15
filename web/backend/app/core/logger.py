"""
Unified logger facade for MyStocks backend.

STANDARDS.md §一.4 mandates: `from app.core.logger import logger`

This module delegates to app.core.logging.structured.StructuredLogger (loguru-based)
and provides a module-level ``logger`` instance for the common import path.

Usage:
    from app.core.logger import logger          # default instance
    from app.core.logger import get_logger       # named instance

The underlying StructuredLogger provides:
    - JSON + console output via loguru
    - Automatic trace_id / request_id / user_id injection
    - Domain-specific helpers: logger.request(), logger.database(), logger.performance()
"""

from app.core.logging.structured import StructuredLogger, get_logger as _get_structured_logger  # noqa: E402

logger: StructuredLogger = _get_structured_logger("MyStocks")


def get_logger(name: str = "MyStocks") -> StructuredLogger:
    return _get_structured_logger(name)


__all__ = ["logger", "get_logger", "StructuredLogger"]
