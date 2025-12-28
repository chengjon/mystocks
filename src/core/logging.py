"""
统一日志系统模块
为MyStocks系统提供统一的日志记录接口
"""

import sys
from pathlib import Path
from contextlib import contextmanager
from loguru import logger as loguru_logger
from functools import wraps

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

# 4. JSON格式日志 (用于日志分析和监控)
loguru_logger.add(
    LOG_DIR / "mystocks_{time:YYYY-MM-DD}.json",
    format="{message}",
    level="INFO",
    rotation="00:00",
    retention="7 days",
    compression="zip",
    encoding="utf-8",
    serialize=True,  # JSON格式
)


class UnifiedLogger:
    """统一日志记录器类"""

    def __init__(self, name: str = "MyStocks"):
        self.logger = loguru_logger.bind(name=name)

    def trace(self, message: str, **kwargs):
        """追踪级别日志"""
        self.logger.opt(depth=1).trace(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """调试级别日志"""
        self.logger.opt(depth=1).debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """信息级别日志"""
        self.logger.opt(depth=1).info(message, **kwargs)

    def success(self, message: str, **kwargs):
        """成功级别日志"""
        self.logger.opt(depth=1).success(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """警告级别日志"""
        self.logger.opt(depth=1).warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """错误级别日志"""
        self.logger.opt(depth=1).error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """严重级别日志"""
        self.logger.opt(depth=1).critical(message, **kwargs)

    def exception(self, message: str, **kwargs):
        """异常级别日志（自动包含异常堆栈）"""
        self.logger.opt(depth=1, exception=True).error(message, **kwargs)

    @contextmanager
    def catch(
        self,
        message: str = "发生异常",
        reraise: bool = True,
        exclude=None,
        level="ERROR",
    ):
        """
        异常捕获上下文管理器

        Args:
            message: 异常发生时记录的消息
            reraise: 是否重新抛出异常
            exclude: 要排除的异常类型
            level: 日志级别
        """
        try:
            yield self.logger
        except Exception as e:
            if exclude and isinstance(e, exclude):
                if reraise:
                    raise
                return

            # 记录异常
            getattr(self.logger.opt(exception=True), level.lower())(message)

            if reraise:
                raise

    def log_performance(self, func):
        """
        记录函数执行时间的装饰器

        Usage:
            @logger.log_performance
            def my_function():
                pass
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = self.logger.catch()(lambda: __import__("time").time())()
            try:
                result = func(*args, **kwargs)
                duration = (self.logger.catch()(lambda: __import__("time").time())() - start_time) * 1000  # ms
                self.info(f"{func.__name__} 执行完成，耗时: {duration:.2f}ms")
                return result
            except Exception as e:
                duration = (self.logger.catch()(lambda: __import__("time").time())() - start_time) * 1000
                self.error(f"{func.__name__} 执行失败，耗时: {duration:.2f}ms, 错误: {e}")
                raise

        return wrapper


# 创建全局logger实例
logger = UnifiedLogger("MyStocks")


# 导出常用的loguru函数
def add_handler(*args, **kwargs):
    """添加日志处理器"""
    return loguru_logger.add(*args, **kwargs)


def remove_handler(handler_id):
    """移除日志处理器"""
    return loguru_logger.remove(handler_id)


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
            "exception": (str(message.record["exception"]) if message.record["exception"] else None),
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
    loguru_logger.add(
        db_sink,
        level="WARNING",
        format="{message}",
    )
except Exception as e:
    logger.warning("无法配置数据库日志sink: %s", e)


# 初始化完成日志
logger.info("统一日志系统初始化完成")
logger.info("日志目录: %s", LOG_DIR)
logger.info("日志级别: 控制台=INFO, 文件=DEBUG, 数据库=WARNING")
