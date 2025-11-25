"""
MyStocks 统一日志配置

提供统一的日志配置和管理
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }

    def format(self, record):
        # 添加颜色
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> None:
    """
    设置项目日志配置

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径 (可选)
        use_colors: 是否使用彩色输出
    """

    # 根环境变量
    log_level = os.getenv('LOG_LEVEL', level)

    # 创建根logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 清除现有handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)

    # 格式化器
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)

    # 文件handler (如果指定)
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取logger实例

    Args:
        name: logger名称，通常使用 __name__

    Returns:
        配置好的logger实例
    """
    return logging.getLogger(name)


# 默认配置
if not logging.getLogger().handlers:
    setup_logging()

# 导出的便捷函数
def log_info(message: str, logger_name: Optional[str] = None):
    """记录INFO级别日志"""
    if logger_name:
        logging.getLogger(logger_name).info(message)
    else:
        logging.getLogger(__name__).info(message)


def log_error(message: str, logger_name: Optional[str] = None):
    """记录ERROR级别日志"""
    if logger_name:
        logging.getLogger(logger_name).error(message)
    else:
        logging.getLogger(__name__).error(message)


def log_warning(message: str, logger_name: Optional[str] = None):
    """记录WARNING级别日志"""
    if logger_name:
        logging.getLogger(logger_name).warning(message)
    else:
        logging.getLogger(__name__).warning(message)


def log_debug(message: str, logger_name: Optional[str] = None):
    """记录DEBUG级别日志"""
    if logger_name:
        logging.getLogger(logger_name).debug(message)
    else:
        logging.getLogger(__name__).debug(message)
