"""
数据API模块 - 向后兼容接口

提供与原data.py相同的接口，但使用新拆分后的API模块
"""

from typing import Any, Dict, List, Optional

from .market_api import MarketDataService
from .trading_api import TradingDataService
from .analysis_api import AnalysisDataService

import logging

logger = __import__("logging").getLogger(__name__)


class DataApiService:
    """数据API服务（向后兼容）"""

    def __init__(self):
        self.market_data_service = MarketDataService()
        self.trading_data_service = TradingDataService()
        self.analysis_data_service = AnalysisDataService()

        logger.info("数据API服务初始化")

    async def get_stock_basic(self, source_type: str, stock_code: str) -> Optional[Dict]:
        """
        获取股票基本信息（自动路由到对应的API）

        Args:
            source_type: 数据源类型（market, trading, analysis）
            stock_code: 股票代码

        Returns:
            Dict: 股票基本信息，失败返回None
        """
        try:
            if source_type.lower() == "market":
                return await self.market_data_service.get_stock_basic(stock_code)
            elif source_type.lower() == "trading":
                return await self.trading_data_service.get_stock_basic(stock_code)
            elif source_type.lower() == "analysis":
                return await self.analysis_data_service.get_stock_basic(stock_code)
            else:
                logger.warning(f"不支持的数据源类型: {source_type}")
                return None

        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            return None

    async def get_stock_list(
        self, source_type: str, industry: Optional[str] = None, area: Optional[str] = None, limit: int = 100
    ) -> List[Dict]:
        """
        获取股票列表（自动路由到对应的API）

        Args:
            source_type: 数据源类型
            industry: 行业
            area: 区域
            limit: 限制数量

        Returns:
            List[Dict]: 股票列表
        """
        try:
            if source_type.lower() == "market":
                return await self.market_data_service.get_stock_list(industry, area, limit)
            elif source_type.lower() == "trading":
                return []
            elif source_type.lower() == "analysis":
                return []
            else:
                logger.warning(f"不支持的数据源类型: {source_type}")
                return []

        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []

    async def get_stock_quote(self, source_type: str, stock_code: str) -> Optional[Dict]:
        """
        获取股票实时行情（自动路由到对应的API）

        Args:
            source_type: 数据源类型
            stock_code: 股票代码

        Returns:
            Dict: 实时行情数据，失败返回None
        """
        try:
            if source_type.lower() == "market":
                return await self.market_data_service.get_stock_quote(stock_code)
            elif source_type.lower() == "trading":
                return {}
            elif source_type.lower() == "analysis":
                return {}
            else:
                logger.warning(f"不支持的数据源类型: {source_type}")
                return None

        except Exception as e:
            logger.error(f"获取股票行情失败: {e}")
            return None

    async def get_multiple_quotes(self, source_type: str, stock_codes: List[str]) -> List[Dict]:
        """
        批量获取股票行情（自动路由到对应的API）

        Args:
            source_type: 数据源类型
            stock_codes: 股票代码列表

        Returns:
            List[Dict]: 实时行情数据列表
        """
        try:
            if source_type.lower() == "market":
                return await self.market_data_service.get_multiple_quotes(stock_codes)
            elif source_type.lower() == "trading":
                return []
            elif source_type.lower() == "analysis":
                return []
            else:
                logger.warning(f"不支持的数据源类型: {source_type}")
                return []

        except Exception as e:
            logger.error(f"批量获取行情失败: {e}")
            return []

    async def get_technical_indicator(
        self, source_type: str, symbol: str, indicator_type: str, period: int = 20
    ) -> Optional[Dict]:
        """
        获取技术指标（自动路由到对应的API）

        Args:
            source_type: 数据源类型
            symbol: 股票代码
            indicator_type: 指标类型（MA, EMA, MACD等）
            period: 周期

        Returns:
            Dict: 技术指标数据，失败返回None
        """
        try:
            if source_type.lower() == "market":
                return await self.market_data_service.get_technical_indicator(symbol, indicator_type, period)
            elif source_type.lower() == "trading":
                return {}
            elif source_type.lower() == "analysis":
                return {}
            else:
                logger.warning(f"不支持的数据源类型: {source_type}")
                return None

        except Exception as e:
            logger.error(f"获取技术指标失败: {e}")
            return None

    async def get_fundamental_data(self, source_type: str, symbol: str) -> Optional[Dict]:
        """
        获取基本面数据（自动路由到对应的API）

        Args:
            source_type: 数据源类型
            symbol: 股票代码

        Returns:
            Dict: 基本面数据，失败返回None
        """
        try:
            if source_type.lower() == "market":
                return await self.market_data_service.get_fundamental_data(symbol)
            elif source_type.lower() == "trading":
                return {}
            elif source_type.lower() == "analysis":
                return {}
            else:
                logger.warning(f"不支持的数据源类型: {source_type}")
                return None

        except Exception as e:
            logger.error(f"获取基本面数据失败: {e}")
            return None

    async def run_comprehensive_analysis(self, source_type: str, symbol: str) -> Optional[Dict]:
        """
        运行综合分析（自动路由到对应的API）

        Args:
            source_type: 数据源类型
            symbol: 股票代码

        Returns:
            Dict: 综合分析结果，失败返回None
        """
        try:
            if source_type.lower() == "market":
                return await self.market_data_service.run_comprehensive_analysis(symbol)
            elif source_type.lower() == "trading":
                return {}
            elif source_type.lower() == "analysis":
                return await self.analysis_data_service.run_comprehensive_analysis(symbol)
            else:
                logger.warning(f"不支持的数据源类型: {source_type}")
                return None

        except Exception as e:
            logger.error(f"运行综合分析失败: {e}")
            return None

    async def validate_data(self, data: Any, data_type: str) -> Dict:
        """
        验证数据质量（自动路由到对应的API）

        Args:
            data: 待验证数据
            data_type: 数据类型

        Returns:
            Dict: 验证结果
        """
        try:
            if data_type.lower() == "market":
                return await self.market_data_service.validate_data(data, "market")
            elif data_type.lower() == "trading":
                return await self.trading_data_service.validate_data(data, "trading")
            elif data_type.lower() == "analysis":
                return await self.analysis_data_service.validate_data(data, "analysis")
            else:
                logger.warning(f"不支持的数据验证类型: {data_type}")
                return {
                    "is_valid": False,
                    "data_type": data_type,
                    "validation_time": datetime.now().isoformat(),
                    "errors": [f"不支持的数据验证类型: {data_type}"],
                }

        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            return {
                "is_valid": False,
                "data_type": data_type,
                "validation_time": datetime.now().isoformat(),
                "errors": [str(e)],
            }

    async def get_market_overview(self, source_type: str) -> Optional[Dict]:
        """
        获取市场概览（自动路由到对应的API）

        Args:
            source_type: 数据源类型

        Returns:
            Dict: 市场概览数据
        """
        try:
            if source_type.lower() == "market":
                return await self.market_data_service.get_market_overview()
            elif source_type.lower() == "trading":
                return {}
            elif source_type.lower() == "analysis":
                return {}
            else:
                logger.warning(f"不支持的市场概览类型: {source_type}")
                return {}

        except Exception as e:
            logger.error(f"获取市场概览失败: {e}")
            return {}

    async def get_trading_summary(self, user_id: str) -> Optional[Dict]:
        """
        获取交易汇总（自动路由到交易API）

        Args:
            user_id: 用户ID

        Returns:
            Dict: 交易汇总数据
        """
        try:
            return await self.trading_data_service.get_trading_summary(user_id)

        except Exception as e:
            logger.error(f"获取交易汇总失败: {e}")
            return {"status": "error", "message": str(e), "generated_at": datetime.now().isoformat()}

    async def export_data(self, source_type: str, format: str = "json") -> str:
        """
        导出数据（自动路由到对应的API）

        Args:
            source_type: 数据源类型
            format: 格式（json/csv）

        Returns:
            str: 导出内容
        """
        try:
            if format == "json":
                import json

                data = {"source_type": source_type, "exported_at": datetime.now().isoformat()}
                return json.dumps(data, indent=2)

            elif format == "csv":
                import csv
                import io

                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=["source_type", "exported_at"])
                writer.writerow({"source_type": source_type, "exported_at": datetime.now().isoformat()})

                output.seek(0)
                return output.getvalue()

            else:
                logger.warning(f"不支持的导出格式: {format}")
                return ""

        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            return ""
