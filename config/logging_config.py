"""
Loguru 日志配置模块
为 MyStocks 系统提供统一的日志配置

使用方法:
    from config.logging_config import logger
    logger.info("This is an info message")
"""

import sys
from pathlib import Path
from loguru import logger

# 移除默认的handler
logger.remove()

# 配置日志目录
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 配置格式
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# 1. 控制台输出 (INFO及以上)
logger.add(
    sys.stderr,
    format=LOG_FORMAT,
    level="INFO",
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# 2. 一般日志文件 (DEBUG及以上，按日期轮转)
logger.add(
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
logger.add(
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

# 4. JSON格式日志 (用于日志分析和监控)
logger.add(
    LOG_DIR / "mystocks_{time:YYYY-MM-DD}.json",
    format="{message}",
    level="INFO",
    rotation="00:00",
    retention="7 days",
    compression="zip",
    encoding="utf-8",
    serialize=True,  # JSON格式
)


# 数据库日志处理器（可选，连接到monitoring数据库）
def db_sink(message):
    """
    将日志写入PostgreSQL监控数据库

    Args:
        message: loguru的日志消息记录
    """
    try:
        import psycopg2
        import json
        import os

        # 只记录WARNING及以上级别到数据库
        if message.record["level"].no < 30:  # WARNING level
            return

        # 从环境变量获取数据库配置
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST", "localhost"),
            port=int(os.getenv("POSTGRESQL_PORT", "5432")),
            user=os.getenv("POSTGRESQL_USER", "postgres"),
            password=os.getenv("POSTGRESQL_PASSWORD", ""),
            database="mystocks_monitoring",
        )

        cursor = conn.cursor()

        # 准备日志数据
        log_data = {
            "timestamp": message.record["time"].isoformat(),
            "level": message.record["level"].name,
            "module": message.record["name"],
            "function": message.record["function"],
            "message": message.record["message"],
            "exception": (
                str(message.record["exception"])
                if message.record["exception"]
                else None
            ),
            "metadata": json.dumps(
                {
                    "file": message.record["file"].path,
                    "line": message.record["line"],
                    "process": message.record["process"].id,
                    "thread": message.record["thread"].id,
                }
            ),
        }

        # 插入日志
        cursor.execute(
            """
            INSERT INTO logs (timestamp, level, module, function, message, exception, metadata)
            VALUES (%(timestamp)s, %(level)s, %(module)s, %(function)s, %(message)s, %(exception)s, %(metadata)s::jsonb)
            """,
            log_data,
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception:
        # 数据库日志失败不应影响主程序，静默处理
        pass


# 5. 数据库sink (WARNING及以上)
try:
    logger.add(
        db_sink,
        level="WARNING",
        format="{message}",
    )
except Exception as e:
    logger.warning(f"无法配置数据库日志sink: {e}")


# 辅助函数：为特定模块创建logger
def get_logger(name: str):
    """
    为特定模块获取logger实例

    Args:
        name: 模块名称

    Returns:
        logger实例
    """
    return logger.bind(name=name)


# 辅助函数：临时更改日志级别
from contextlib import contextmanager


@contextmanager
def temporary_level(level: str):
    """
    临时更改日志级别的上下文管理器

    Usage:
        with temporary_level("DEBUG"):
            logger.debug("This will be logged")
    """
    # 保存当前所有handler的级别
    original_levels = []
    for handler_id in logger._core.handlers:
        handler = logger._core.handlers[handler_id]
        original_levels.append((handler_id, handler._levelno))

    # 临时设置新级别
    logger.remove()
    logger.add(sys.stderr, level=level)

    try:
        yield logger
    finally:
        # 恢复原始级别
        logger.remove()
        # 重新添加所有handler（需要重新配置，这里简化处理）
        logger.add(sys.stderr, format=LOG_FORMAT, level="INFO", colorize=True)


# 日志性能装饰器
def log_performance(func):
    """
    记录函数执行时间的装饰器

    Usage:
        @log_performance
        def my_function():
            pass
    """
    import functools
    import time

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000  # ms
            logger.info(f"{func.__name__} 执行完成，耗时: {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} 执行失败，耗时: {duration:.2f}ms, 错误: {e}")
            raise

    return wrapper


# 导出logger
__all__ = ["logger", "get_logger", "temporary_level", "log_performance"]


# 初始化完成日志
logger.info("Loguru 日志系统初始化完成")
logger.info(f"日志目录: {LOG_DIR}")
logger.info("日志级别: 控制台=INFO, 文件=DEBUG, 数据库=WARNING")
