"""
综合服务模块入口

整合所有已创建的服务模块：风险管理、市场数据、交易数据、分析数据、数据适配等
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = __import__("logging").getLogger(__name__)

# 风险管理模块
from .risk_management.risk_base import RiskBase, RiskMetrics, RiskLevel, RiskEventType, RiskProfile
from .risk_management.risk_monitoring import RiskMonitoring, MonitoringThreshold, MonitoringEvent, MonitoringStatistics
from .risk_management.risk_alerts import AlertManager, AlertRule, AlertHistory, AlertChannel
from .risk_management.risk_settings import RiskSettingsManager, RiskSettings, ModelType, TimeHorizon
from .risk_management.risk_calculator import RiskCalculator, CalculationConfig, CalculationResult
from .risk_management.risk_dashboard import (
    RiskDashboard,
    DashboardChartType,
    DashboardTimeRange,
    RiskOverview,
    PortfolioRiskSummary,
    ChartDataPoint,
)

# 市场数据模块
from .market_api import MarketDataService

# 交易数据模块
from .trading_api import TradingDataService, OrderStatus, OrderType, OrderSide, Order, Position, Trade

# 分析数据模块
from .analysis_api import (
    AnalysisDataService,
    IndicatorType,
    TimePeriod,
    AnalysisType,
    IndicatorData,
    FundamentalData,
    AnalysisResult,
)

# 数据适配模块
from .data_api_new import DataApiService

# 数据库服务模块
from .database_service import DatabaseService

# WebSocket服务模块
from .websocket_service import WebSocketService

# 缓存服务模块
from .cache_service import CacheService


class IntegratedServices:
    """
    综合服务管理器

    整合所有已创建的服务模块，提供统一的服务入口点
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 初始化风险管理服务
        self.risk_base = RiskBase()
        self.risk_monitoring = RiskMonitoring()
        self.risk_alerts = AlertManager()
        self.risk_settings = RiskSettingsManager()
        self.risk_calculator = RiskCalculator()
        self.risk_dashboard = RiskDashboard()
        self.risk_management_new = None

        # 初始化市场数据服务
        self.market_data_service = MarketDataService()

        # 初始化交易数据服务
        self.trading_data_service = TradingDataService()

        # 初始化分析数据服务
        self.analysis_data_service = AnalysisDataService()

        # 初始化数据API服务
        self.data_api_service = DataApiService()

        # 初始化数据库服务
        self.database_service = None
        self.websocket_service = None
        self.cache_service = None

        logger.info("综合服务管理器初始化完成")

    async def initialize_all_services(self) -> bool:
        """
        初始化所有服务

        Returns:
            bool: 是否全部初始化成功
        """
        try:
            self.logger.info("开始初始化所有服务...")

            # 初始化数据库服务
            from .database_service import DatabaseService

            self.database_service = DatabaseService()
            self.logger.info("数据库服务已初始化")

            # 初始化WebSocket服务
            from .websocket_service import WebSocketService

            self.websocket_service = WebSocketService()
            self.logger.info("WebSocket服务已初始化")

            # 初始化缓存服务
            from .cache_service import CacheService

            self.cache_service = CacheService()
            self.logger.info("缓存服务已初始化")

            # 初始化风险管理的向后兼容接口
            from .risk_management.risk_management_new import RiskManagementService

            self.risk_management_new = RiskManagementService()
            self.logger.info("风险管理向后兼容接口已初始化")

            # 初始化数据API的向后兼容接口
            from .data_api_new import DataApiService

            self.data_api_service = DataApiService()
            self.logger.info("数据API向后兼容接口已初始化")

            self.logger.info("所有服务初始化完成")
            return True

        except Exception as e:
            self.logger.error(f"服务初始化失败: {e}")
            return False

    def get_risk_metrics(self, returns: List[float], config: Optional[RiskProfile] = None) -> Dict:
        """获取风险指标（路由到风险管理服务）"""
        return self.risk_calculator.calculate_all_metrics(returns, config)

    def calculate_var(self, returns: List[float]) -> float:
        """计算方差（路由到风险管理服务）"""
        return self.risk_calculator.calculate_var(returns)

    def calculate_volatility(self, returns: List[float]) -> float:
        """计算波动率（路由到风险管理服务）"""
        return self.risk_calculator.calculate_percentile(1.0, returns)

    def get_stock_quote(self, source_type: str, stock_code: str) -> Optional[Dict]:
        """获取股票行情（路由到市场数据服务）"""
        return self.market_data_service.get_stock_quote(source_type, stock_code)

    def get_technical_indicator(
        self, source_type: str, symbol: str, indicator_type: str, period: int = 20
    ) -> Optional[Dict]:
        """获取技术指标（路由到分析数据服务）"""
        return self.analysis_data_service.calculate_technical_indicator(source_type, symbol, indicator_type, period)

    def get_fundamental_data(self, source_type: str, symbol: str) -> Optional[Dict]:
        """获取基本面数据（路由到分析数据服务）"""
        return self.analysis_data_service.get_fundamental_data(source_type, symbol)

    async def get_market_overview(self) -> Dict:
        """获取市场概览（整合所有服务）"""
        try:
            self.logger.info("开始生成市场概览...")

            overview = {
                "risk_overview": await self._get_risk_overview(),
                "market_data_status": await self._get_market_data_status(),
                "trading_data_status": await self._get_trading_data_status(),
                "analysis_data_status": await self._get_analysis_data_status(),
                "service_health": {
                    "database_service": self.database_service.check_health()
                    if self.database_service
                    else "unavailable",
                    "websocket_service": self.websocket_service.check_health()
                    if self.websocket_service
                    else "unavailable",
                    "cache_service": self.cache_service.get_health() if self.cache_service else "unavailable",
                },
                "generated_at": datetime.now().isoformat(),
            }

            self.logger.info("市场概览生成完成")
            return overview

        except Exception as e:
            self.logger.error(f"生成市场概览失败: {e}")
            return {}

    async def _get_risk_overview(self) -> Dict:
        """获取风险管理概览"""
        try:
            from .database_service import DatabaseService

            db = DatabaseService()

            sql = "SELECT COUNT(*) as count FROM risk_metrics"
            result = await db.fetch_one(sql)

            return {
                "total_risk_calculations": result["count"] if result else 0,
                "last_calculation_time": datetime.now().isoformat(),
            }
        except Exception as e:
            return {}

    async def _get_market_data_status(self) -> Dict:
        """获取市场数据服务状态"""
        try:
            cache_stats = self.market_data_service.get_cache_stats()

            return {
                "is_available": cache_stats["last_update"] is not None,
                "cache_size": cache_stats["cache_size"],
                "last_update": cache_stats["last_update"],
            }
        except Exception as e:
            return {}

    async def _get_trading_data_status(self) -> Dict:
        """获取交易数据服务状态"""
        try:
            # 这里可以检查交易数据的缓存状态
            return {
                "is_available": True,
                "orders_count": 0,
                "positions_count": 0,
                "trades_count": 0,
                "last_update": datetime.now().isoformat(),
            }
        except Exception as e:
            return {}

    async def _get_analysis_data_status(self) -> Dict:
        """获取分析数据服务状态"""
        try:
            # 这里可以检查分析数据的缓存状态
            return {
                "is_available": True,
                "indicators_count": 0,
                "fundamentals_count": 0,
                "signals_count": 0,
                "trends_count": 0,
                "last_update": datetime.now().isoformat(),
            }
        except Exception as e:
            return {}


def get_integrated_services() -> IntegratedServices:
    """
    获取综合服务实例（单例模式）

    Returns:
        IntegratedServices: 综合服务实例
    """
    try:
        if not hasattr(get_integrated_services, "_instance"):
            _instance = IntegratedServices()
        return _instance
    except Exception as e:
        logger.error(f"获取综合服务实例失败: {e}")
        return None


async def initialize_all_services() -> bool:
    """
    初始化所有服务（便捷函数）

    Returns:
        bool: 是否全部初始化成功
    """
    integrated_services = get_integrated_services()
    return await integrated_services.initialize_all_services()


def get_risk_calculator() -> RiskCalculator:
    """获取风险计算器实例"""
    integrated_services = get_integrated_services()
    return integrated_services.risk_calculator


def get_market_data_service() -> MarketDataService:
    """获取市场数据服务实例"""
    integrated_services = get_integrated_services()
    return integrated_services.market_data_service


def get_trading_data_service() -> TradingDataService:
    """获取交易数据服务实例"""
    integrated_services = get_integrated_services()
    return integrated_services.trading_data_service


def get_analysis_data_service() -> AnalysisDataService:
    """获取分析数据服务实例"""
    integrated_services = get_integrated_services()
    return integrated_services.analysis_data_service


def get_data_api_service() -> DataApiService:
    """获取数据API服务实例"""
    integrated_services = get_integrated_services()
    return integrated_services.data_api_service


def get_database_service() -> DatabaseService:
    """获取数据库服务实例"""
    integrated_services = get_integrated_services()
    return integrated_services.database_service


def get_websocket_service() -> WebSocketService:
    """获取WebSocket服务实例"""
    integrated_services = get_integrated_services()
    return integrated_services.websocket_service


def get_cache_service() -> CacheService:
    """获取缓存服务实例"""
    integrated_services = get_integrated_services()
    return integrated_services.cache_service


def get_risk_monitoring() -> RiskMonitoring:
    """获取风险监控实例"""
    integrated_services = get_integrated_services()
    return integrated_services.risk_monitoring


def get_risk_alerts() -> AlertManager:
    """获取风险告警实例"""
    integrated_services = get_integrated_services()
    return integrated_services.risk_alerts


def get_risk_settings() -> RiskSettingsManager:
    """获取风险设置实例"""
    integrated_services = get_integrated_services()
    return integrated_services.risk_settings


def get_risk_dashboard() -> RiskDashboard:
    """获取风险仪表盘实例"""
    integrated_services = get_integrated_services()
    return integrated_services.risk_dashboard
