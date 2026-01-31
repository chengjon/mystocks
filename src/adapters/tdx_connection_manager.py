"""
TDX连接管理器 - 从 tdx_adapter.py 拆分
职责：TDX协议连接、会话管理、重试机制
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict

# 设置日志
logger = logging.getLogger(__name__)


class TdxConnectionManager:
    """TDX连接管理器 - 专注于连接管理和重试机制"""

    def __init__(self):
        """初始化TDX连接管理器"""
        self.connection = None
        self.market_codes = {
            "SH": 0,  # 上交所
            "SZ": 1,  # 深交所
        }
        self.retry_config = {
            "max_retries": 3,
            "retry_delay": 1.0,
            "backoff_factor": 2.0,
        }
        self._connection_attempts = 0

    def create_connection(self):
        """
        创建TDX连接

        Returns:
            connection: 连接对象
        """
        return self._connect_to_tdx_server()

    def get_market_code(self, symbol: str) -> int:
        """
        根据股票代码获取市场代码

        Args:
            symbol: 股票代码，如 "000001", "600000"

        Returns:
            int: 市场代码 (0=上交所, 1=深交所)
        """
        if not symbol or len(symbol) != 6:
            raise ValueError(f"Invalid symbol format: {symbol}")

        # 根据股票代码首位数字判断市场
        first_digit = symbol[0]
        if first_digit in ["0", "3"]:
            return 1  # 深交所
        elif first_digit in ["6"]:
            return 0  # 上交所
        else:
            # 默认为深交所
            return 1

    def _retry_api_call(self, func: Callable) -> Callable:
        """
        API调用重试装饰器

        Args:
            func: 需要重试的函数

        Returns:
            Callable: 装饰后的函数
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(self.retry_config["max_retries"]):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < self.retry_config["max_retries"] - 1:
                        delay = self.retry_config["retry_delay"] * (self.retry_config["backoff_factor"] ** attempt)
                        logger.warning("API call failed (attempt %s), retrying in %ss: %s", attempt + 1, delay, str(e))
                        time.sleep(delay)
                    else:
                        logger.error("API call failed after %s attempts: %s", attempt + 1, str(e))

            raise last_exception

        return wrapper

    def check_connection_health(self) -> bool:
        """
        检查连接健康状态

        Returns:
            bool: 连接是否健康
        """
        return self._test_connection_health()

    def _connect_to_tdx_server(self):
        """
        连接到TDX服务器（内部方法）

        Returns:
            connection: 连接对象
        """
        logger.info("Connecting to TDX server")
        return self.create_connection()

    def _test_connection_health(self) -> bool:
        """
        测试连接健康状态（内部方法）

        Returns:
            bool: 连接是否健康
        """
        if not self.connection:
            return False

        # 简单的健康检查：检查连接状态和时间
        if isinstance(self.connection, dict):
            status = self.connection.get("status")
            created_at = self.connection.get("created_at", 0)

            # 检查连接状态
            if status != "connected":
                return False

            # 检查连接时间（超过30秒认为不健康）
            if time.time() - created_at > 30:
                logger.warning("Connection considered stale")
                return False

        return True

    def close_connection(self):
        """关闭连接"""
        if self.connection:
            logger.info("Closing TDX connection")
            self.connection = None

    def get_connection_status(self) -> Dict[str, Any]:
        """
        获取连接状态信息

        Returns:
            Dict[str, Any]: 连接状态
        """
        return {
            "connected": self.connection is not None,
            "connection_id": self.connection.get("id") if self.connection else None,
            "status": self.connection.get("status") if self.connection else None,
            "connection_attempts": self._connection_attempts,
            "last_check": time.time(),
        }
