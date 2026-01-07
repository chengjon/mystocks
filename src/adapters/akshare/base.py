"""
# 功能：AkShare数据源适配器，提供A股行情和基本面数据
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import pandas as pd
from typing import Dict, List, Optional, Any
import akshare as ak
import sys
import os
import datetime
from functools import wraps

# 常量定义
MAX_RETRIES = 3
RETRY_DELAY = 1
REQUEST_TIMEOUT = 10

# 将当前目录的父目录的父目录添加到模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.error_handler import retry_on_failure  # noqa: E402
from src.interfaces.data_source import IDataSource  # noqa: E402
from src.utils.date_utils import normalize_date  # noqa: E402
from src.utils.symbol_utils import (  # noqa: E402
    format_stock_code_for_source,
    format_index_code_for_source,
)
from src.utils.column_mapper import ColumnMapper  # noqa: E402

# 统一日志配置
import logging

# 获取或创建logger
logger = logging.getLogger(__name__)

# 确保日志配置已设置
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class AkshareDataSource(IDataSource):
    """Akshare数据源实现

    属性:
        api_timeout (int): API请求超时时间(秒)
        max_retries (int): 最大重试次数
    """

    def __init__(self, api_timeout: int = REQUEST_TIMEOUT, max_retries: int = MAX_RETRIES):
        """初始化Akshare数据源

        Args:
            api_timeout: API请求超时时间(秒)
            max_retries: 最大重试次数
        """
        self.api_timeout = api_timeout
        self.max_retries = max_retries
        logger.info("[Akshare] 数据源初始化完成 (超时: %ss, 重试: %s次)", api_timeout, max_retries)

    def _retry_api_call(self, func):
        """API调用重试装饰器 - 使用统一错误处理"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 使用统一错误处理的重试机制
            retry_decorator = retry_on_failure(
                max_retries=self.max_retries,
                delay=RETRY_DELAY,
                backoff=1.0,
                exceptions=(Exception,),
                context=f"Akshare API调用: {func.__name__}",
            )
            return retry_decorator(func)(*args, **kwargs)

        return wrapper
