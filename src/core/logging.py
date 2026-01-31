"""
统一日志系统模块
为MyStocks系统提供统一的日志记录接口
"""

import sys
from contextlib import contextmanager
from functools import wraps
from pathlib import Path

from loguru import logger as loguru_logger

# 移除默认的handler
loguru_logger.remove()

# 配置日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 配置格式
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# 1. 控制台输出 (INFO及以上)
loguru_logger.add(
    sys.stderr,
    format=LOG_FORMAT,
    level="INFO",
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# 2. 一般日志文件 (DEBUG及以上，按日期轮转)
loguru_logger.add(
    LOG_DIR / "mystocks_{time:YYYY-MM-DD}.log",
    format=LOG_FORMAT,
    level="DEBUG",
    rotation="00:00",  # 每天午夜轮转
    retention="7 days",  # 保留7天
    compression="zip",  # 压缩旧日志
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
)

# 3. 错误日志文件 (ERROR及以上，单独文件)
loguru_logger.add(
    LOG_DIR / "error_{time:YYYY-MM-DD}.log",
    format=LOG_FORMAT,
    level="ERROR",
    rotation="00:00",
    retention="30 days",  # 保留30天
    compression="zip",
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
)
