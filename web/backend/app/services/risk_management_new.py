"""
风险管理模块 - 向后兼容接口

提供与原risk_management.py相同的接口，但使用新拆分后的风险管理模块
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from .risk_management.risk_base import RiskBase, RiskLevel, RiskEventType, RiskProfile
from .risk_management.risk_monitoring import RiskMonitoring
from .risk_management.risk_alerts import AlertManager, AlertChannel
from .risk_management.risk_settings import RiskSettingsManager
from .risk_management.risk_calculator import RiskCalculator, CalculationConfig
from .risk_management.risk_dashboard import RiskDashboard, DashboardChartType, DashboardTimeRange


logger = __import__("logging").getLogger(__name__)


class RiskManagementService:
    """风险管理服务（向后兼容）"""

    def __init__(self):
        self.risk_base = RiskBase()
        self.monitoring = RiskMonitoring()
        self.alerts = AlertManager()
        self.settings = RiskSettingsManager()
        self.calculator = RiskCalculator()
        self.dashboard = RiskDashboard()

        logger.info("风险管理服务初始化")

    def get_risk_metrics(self, returns: List[float], config: Optional[RiskProfile] = None) -> Dict:
        """
        计算风险指标

        Args:
            returns: 收益率列表
            config: 风险配置

        Returns:
            Dict: 风险指标
        """
        try:
            calc_config = config or CalculationConfig()
            result = self.calculator.calculate_all_metrics(returns, config)

            return result.to_dict()

        except Exception as e:
            logger.error(f"计算风险指标失败: {e}")
            return {}

    def calculate_var(self, returns: List[float]) -> float:
        """
        计算方差

        Args:
            returns: 收益率列表

        Returns:
            float: 方差值
        """
        return self.risk_base.calculate_var(returns)

    def calculate_var_with_return(self, returns: List[float], risk_free_rate: float = 0.03) -> float:
        """
        计算带风险调整的方差

        Args:
            returns: 收益率列表
            risk_free_rate: 无风险利率

        Returns:
            float: 调整后方差
        """
        return self.risk_base.calculate_var_with_return(returns, risk_free_rate)

    def calculate_percentile(self, value: float, distribution: List[float], percentile: float = 95.0) -> float:
        """
        计算百分位

        Args:
            value: 数值
            distribution: 分布列表
            percentile: 百分位（0-100）

        Returns:
            float: 百分位数值
        """
        return self.risk_base.calculate_percentile(value, distribution, percentile)

    def check_risk_thresholds(self, portfolio_id: str, current_metrics: Any) -> List[Dict]:
        """
        检查风险阈值是否被突破

        Args:
            portfolio_id: 投资组合ID
            current_metrics: 当前风险指标

        Returns:
            List[Dict]: 触发的事件列表
        """
        return self.monitoring.check_thresholds(portfolio_id, current_metrics)

    async def create_alert_rule(
        self, rule_name: str, risk_level: RiskLevel, conditions: Dict, channel: AlertChannel = AlertChannel.EMAIL
    ) -> Dict:
        """
        创建告警规则

        Args:
            rule_name: 规则名称
            risk_level: 风险等级
            conditions: 条件配置
            channel: 告警渠道

        Returns:
            Dict: 创建的规则
        """
        return await self.alerts.create_alert_rule(rule_name, risk_level, conditions, channel)

    async def trigger_alert(self, portfolio_id: str, risk_level: RiskLevel, message: str) -> None:
        """
        触发告警

        Args:
            portfolio_id: 投资组合ID
            risk_level: 风险等级
            message: 告警消息
        """
        from .risk_management.risk_base import RiskEvent

        event = RiskEvent(
            event_id=f"alert_{datetime.now().isoformat()}",
            event_type=RiskEventType.THRESHOLD_BREACH,
            risk_level=risk_level,
            timestamp=datetime.now(),
            portfolio_id=portfolio_id,
            message=message,
        )

        await self.monitoring.record_event(event)

    async def check_health(self) -> Dict:
        """
        检查风险管理服务健康状态

        Returns:
            Dict: 健康状态
        """
        try:
            health_check = {
                "risk_base": "healthy",
                "monitoring": self.monitoring.check_health() if self.monitoring else "unavailable",
                "alerts": "healthy",
                "settings": "healthy",
                "calculator": "healthy",
                "dashboard": "healthy",
                "last_check": datetime.now().isoformat(),
            }

            if health_check["monitoring"] != "healthy":
                health_check["message"] = f"监控服务异常: {health_check['monitoring']}"
            else:
                health_check["message"] = "所有服务健康"

            return health_check

        except Exception as e:
            logger.error(f"检查健康状态失败: {e}")
            return {"status": "error", "message": str(e), "last_check": datetime.now().isoformat()}

    async def get_risk_settings(self, user_id: str) -> Optional[Dict]:
        """
        获取风险设置

        Args:
            user_id: 用户ID

        Returns:
            Dict: 风险设置
        """
        return await self.settings.get_settings(user_id)

    async def get_dashboard_summary(
        self, portfolio_id: str, time_range: DashboardTimeRange = DashboardTimeRange.WEEKLY
    ) -> Dict:
        """
        获取仪表盘摘要

        Args:
            portfolio_id: 投资组合ID
            time_range: 时间范围

        Returns:
            Dict: 仪表盘摘要
        """
        try:
            summary = await self.dashboard.get_dashboard(portfolio_id, time_range)

            return {
                "overview": summary.get("overview", {}),
                "portfolio_risk": summary.get("portfolio_risk", {}),
                "chart_data": summary.get("chart_data", {}),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"获取仪表盘摘要失败: {e}")
            return {}

    async def export_risk_report(
        self, portfolio_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> str:
        """
        导出风险报告

        Args:
            portfolio_id: 投资组合ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            str: 报告内容（JSON/CSV格式）
        """
        return await self.dashboard.generate_risk_report(portfolio_id, start_date, end_date)

    async def calculate_portfolio_risk(self, portfolio_id: str) -> Dict:
        """
        计算投资组合风险

        Args:
            portfolio_id: 投资组合ID

        Returns:
            Dict: 风险指标摘要
        """
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                date, close_price, volume
            FROM portfolio_history
            WHERE portfolio_id = '{portfolio_id}'
            ORDER BY date DESC
            LIMIT 252
            """

            result = await db_service.fetch_many(sql)

            if not result:
                return {"status": "error", "message": "无法获取历史数据"}

            returns = [r["close_price"] for r in result]
            risk_metrics = self.get_risk_metrics(returns)

            return {
                "status": "success",
                "portfolio_id": portfolio_id,
                "risk_metrics": risk_metrics,
                "calculated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"计算投资组合风险失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_available_risk_models(self) -> List[str]:
        """
        获取可用的风险模型

        Returns:
            List[str]: 模型列表
        """
        return self.settings.get_available_models()

    def get_available_time_horizons(self) -> List[str]:
        """
        获取可用的时间周期

        Returns:
            List[str]: 时间周期列表
        """
        return self.settings.get_available_time_horizons()

    def get_available_chart_types(self) -> List[str]:
        """
        获取可用的图表类型

        Returns:
            List[str]: 图表类型列表
        """
        return [chart_type.value for chart_type in DashboardChartType]
