"""
数据源适配器 - 向后兼容接口

提供与原data_adapter.py相同的接口，但使用新拆分后的适配器模块
"""

from typing import Any, Dict, List, Optional

from .adapters_split.base_adapter import BaseAdapter
from .adapters_split.akshare_adapter import AkshareAdapter
from .adapters_split.efinance_adapter import EfinanceAdapter
from .adapters_split.tdx_adapter import TDXAdapter
from .adapters_split.tushare_adapter import TushareAdapter
from .adapters_split.baostock_adapter import BaostockAdapter
from .adapters_split.byapi_adapter import BYAPIAdapter
from .adapters_split.customer_adapter import CustomerAdapter

import logging

logger = __import__("logging").getLogger(__name__)


class DataAdapter:
    """数据源适配器（向后兼容）"""

    def __init__(self):
        """初始化所有适配器"""
        self.akshare_adapter = AkshareAdapter()
        self.efinance_adapter = EfinanceAdapter()
        self.tdx_adapter = TDXAdapter()
        self.tushare_adapter = TushareAdapter()
        self.baostock_adapter = BaostockAdapter()
        self.byapi_adapter = BYAPIAdapter()
        self.customer_adapter = CustomerAdapter()

        logger.info("数据源适配器初始化完成")

    def get_adapter(self, source_type: str) -> BaseAdapter:
        """
        根据数据源类型获取对应的适配器

        Args:
            source_type: 数据源类型（akshare, efinance, tdx, tushare, baostock, byapi, customer）

        Returns:
            BaseAdapter: 对应的适配器
        """
        adapter_map = {
            "akshare": self.akshare_adapter,
            "efinance": self.efinance_adapter,
            "tdx": self.tdx_adapter,
            "tushare": self.tushare_adapter,
            "baostock": self.baostock_adapter,
            "byapi": self.byapi_adapter,
            "customer": self.customer_adapter,
        }

        adapter = adapter_map.get(source_type.lower())

        if not adapter:
            logger.warning(f"未找到适配器: {source_type}")
            raise ValueError(f"不支持的数据源类型: {source_type}")

        return adapter

    async def get_stock_basic(self, source_type: str, stock_code: str) -> Optional[Dict]:
        """
        获取股票基本信息（自动路由到对应的适配器）

        Args:
            source_type: 数据源类型
            stock_code: 股票代码

        Returns:
            Dict: 股票基本信息，失败返回None
        """
        try:
            adapter = self.get_adapter(source_type)
            return await adapter.get_stock_basic(stock_code)

        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            return None

    async def get_stock_daily(
        self, source_type: str, stock_code: str, start_date: str, end_date: str
    ) -> Optional[List[Dict]]:
        """
        获取日线数据（自动路由到对应的适配器）

        Args:
            source_type: 数据源类型
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            List[Dict]: 日线数据列表，失败返回空列表
        """
        try:
            adapter = self.get_adapter(source_type)
            return await adapter.get_stock_daily(stock_code, start_date, end_date)

        except Exception as e:
            logger.error(f"获取日线数据失败: {e}")
            return []

    async def get_realtime_quotes(self, source_type: str, stock_codes: List[str]) -> Optional[List[Dict]]:
        """
        获取实时行情（自动路由到对应的适配器）

        Args:
            source_type: 数据源类型
            stock_codes: 股票代码列表

        Returns:
            List[Dict]: 实时行情数据列表，失败返回空列表
        """
        try:
            adapter = self.get_adapter(source_type)
            return await adapter.get_realtime_quotes(stock_codes)

        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return []

    async def get_fund_flow(self, source_type: str, stock_code: str, days: int = 5) -> Optional[Dict]:
        """
        获取资金流向（自动路由到对应的适配器）

        Args:
            source_type: 数据源类型
            stock_code: 股票代码
            days: 天数（默认5天）

        Returns:
            Dict: 资金流向数据，失败返回None
        """
        try:
            if source_type.lower() in ["akshare", "efinance", "tdx"]:
                adapter = self.get_adapter(source_type)
                return await adapter.get_fund_flow(stock_code, days)
            else:
                logger.warning(f"{source_type}不支持资金流向查询")
                return None

        except Exception as e:
            logger.error(f"获取资金流向失败: {e}")
            return None

    async def get_board_data(self, source_type: str, board_type: str = "lhb") -> Optional[List[Dict]]:
        """
        获取龙虎榜数据（自动路由到对应的适配器）

        Args:
            source_type: 数据源类型
            board_type: 榜单类型（lhb等）

        Returns:
            List[Dict]: 榜单数据列表，失败返回空列表
        """
        try:
            if source_type.lower() in ["akshare", "baostock", "byapi"]:
                adapter = self.get_adapter(source_type)
                return await adapter.get_board_data(board_type)
            else:
                logger.warning(f"{source_type}不支持{board_type}查询")
                return []

        except Exception as e:
            logger.error(f"获取{board_type}数据失败: {e}")
            return []

    async def check_health(self, source_type: str) -> Optional[str]:
        """
        检查数据源健康状态（自动路由到对应的适配器）

        Args:
            source_type: 数据源类型

        Returns:
            str: 健康状态（healthy/unhealthy/error）
        """
        try:
            adapter = self.get_adapter(source_type)
            return await adapter.check_health()

        except Exception as e:
            logger.error(f"检查健康状态失败: {e}")
            return f"error: {e}"
