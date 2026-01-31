"""
风险管理仪表盘模块

提供风险仪表盘数据汇总、图表数据、报告生成、实时风险监控UI功能
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .risk_base import RiskMetrics, RiskLevel, RiskProfile
from .risk_base import RiskBase

logger = __import__("logging").getLogger(__name__)


class DashboardChartType(Enum):
    """仪表盘图表类型"""

    RISK_OVERVIEW = "risk_overview"
    VAR_TREND = "var_trend"
    DRAWDOWN = "drawdown"
    SHARPE_RATIO = "sharpe_ratio"
    BETA = "beta"
    VOLATILITY = "volatility"
    PORTFOLIO_COMPARISON = "portfolio_comparison"


class DashboardTimeRange(Enum):
    """仪表盘时间范围"""

    TODAY = "today"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class RiskOverview:
    """风险概览数据"""

    total_portfolios: int = 0
    total_risk_events: int = 0
    high_risk_portfolios: int = 0
    medium_risk_portfolios: int = 0
    low_risk_portfolios: int = 0
    total_alerts_sent: int = 0

    def to_dict(self) -> Dict:
        return {
            "total_portfolios": self.total_portfolios,
            "total_risk_events": self.total_risk_events,
            "high_risk_portfolios": self.high_risk_portfolios,
            "medium_risk_portfolios": self.medium_risk_portfolios,
            "low_risk_portfolios": self.low_risk_portfolios,
            "total_alerts_sent": self.total_alerts_sent,
        }


@dataclass
class PortfolioRiskSummary:
    """投资组合风险汇总"""

    portfolio_id: str = ""
    portfolio_name: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    total_value: float = 0.0
    current_metrics: RiskMetrics = None
    trend: str = "stable"

    def to_dict(self) -> Dict:
        return {
            "portfolio_id": self.portfolio_id,
            "portfolio_name": self.portfolio_name,
            "risk_level": self.risk_level.value,
            "total_value": f"{self.total_value:.0f}",
            "current_metrics": self.current_metrics.to_dict() if self.current_metrics else None,
            "trend": self.trend,
        }


@dataclass
class ChartDataPoint:
    """图表数据点"""

    date: Optional[datetime] = None
    value: float = 0.0
    label: str = ""
    comparison_value: Optional[float] = None
    is_anomaly: bool = False

    def to_dict(self) -> Dict:
        return {
            "date": self.date.isoformat() if self.date else None,
            "value": f"{self.value:.2f}",
            "label": self.label,
            "comparison_value": f"{self.comparison_value:.2f}" if self.comparison_value is not None else None,
            "is_anomaly": self.is_anomaly,
        }


class RiskDashboard(RiskBase):
    """风险仪表盘"""

    def __init__(self):
        super().__init__()
        self.risk_overview = RiskOverview()
        self.portfolio_summaries: List[PortfolioRiskSummary] = []
        self.chart_data: Dict[str, List[ChartDataPoint]] = {}
        self.reports: List[Dict] = []

        logger.info("风险仪表盘模块初始化")

    async def get_risk_dashboard_summary(self, portfolio_ids: Optional[List[str]] = None) -> Dict:
        """
        获取风险仪表盘摘要

        Args:
            portfolio_ids: 投资组合ID列表

        Returns:
            Dict: 仪表盘摘要
        """
        try:
            self._log_request_start("get_risk_dashboard_summary", {"portfolio_ids": portfolio_ids})

            if not portfolio_ids:
                portfolio_ids = []

            risk_overview = await self._calculate_risk_overview(portfolio_ids)
            portfolio_summaries = await self._calculate_portfolio_summaries(portfolio_ids)
            chart_data = await self._prepare_chart_data(portfolio_ids)

            summary = {
                "risk_overview": risk_overview.to_dict(),
                "portfolio_summaries": [s.to_dict() for s in portfolio_summaries],
                "chart_data": chart_data,
            }

            self._log_request_success("get_risk_dashboard_summary", summary)
            return summary

        except Exception as e:
            self._log_request_error("get_risk_dashboard_summary", e)
            return {}

    async def _calculate_risk_overview(self, portfolio_ids: List[str]) -> RiskOverview:
        """计算风险概览"""
        try:
            total_portfolios = len(portfolio_ids)
            high_risk = 0
            medium_risk = 0
            low_risk = 0

            for portfolio_id in portfolio_ids:
                metrics = await self._get_latest_metrics(portfolio_id)

                if metrics:
                    if metrics.var_95 > 0.025:
                        high_risk += 1
                    elif metrics.var_95 > 0.015:
                        medium_risk += 1
                    else:
                        low_risk += 1

            return RiskOverview(
                total_portfolios=total_portfolios,
                total_risk_events=len(self.event_history),
                high_risk_portfolios=high_risk,
                medium_risk_portfolios=medium_risk,
                low_risk_portfolios=low_risk,
                total_alerts_sent=sum(1 for event in self.event_history if event.is_alert),
            )

        except Exception as e:
            self.logger.error(f"计算风险概览失败: {e}")
            return RiskOverview()

    async def _calculate_portfolio_summaries(self, portfolio_ids: List[str]) -> List[PortfolioRiskSummary]:
        """计算投资组合风险汇总"""
        try:
            summaries = []

            for portfolio_id in portfolio_ids[:100]:
                metrics = await self._get_latest_metrics(portfolio_id)

                if not metrics:
                    continue

                current_value = metrics.total_value if hasattr(metrics, "total_value") else 0.0

                trend = await self._calculate_risk_trend(portfolio_id)

                risk_level = RiskLevel.LOW
                if metrics.var_95 > 0.025:
                    risk_level = RiskLevel.HIGH
                elif metrics.var_95 > 0.015:
                    risk_level = RiskLevel.MEDIUM

                summary = PortfolioRiskSummary(
                    portfolio_id=portfolio_id,
                    portfolio_name=f"投资组合{portfolio_id}",
                    risk_level=risk_level,
                    total_value=current_value,
                    current_metrics=metrics,
                    trend=trend,
                )

                summaries.append(summary)

            return summaries

        except Exception as e:
            self.logger.error(f"计算投资组合汇总失败: {e}")
            return []

    async def _prepare_chart_data(self, portfolio_ids: List[str]) -> Dict[str, List[ChartDataPoint]]:
        """准备图表数据"""
        try:
            chart_data = {}

            for chart_type in DashboardChartType:
                chart_data[chart_type.value] = await self._calculate_chart(chart_type, portfolio_ids)

            return chart_data

        except Exception as e:
            self.logger.error(f"准备图表数据失败: {e}")
            return {}

    async def _calculate_chart(self, chart_type: DashboardChartType, portfolio_ids: List[str]) -> List[ChartDataPoint]:
        """计算图表数据"""
        try:
            time_range = DashboardTimeRange.MONTHLY
            days = 30

            if chart_type == DashboardChartType.VAR_TREND:
                return await self._calculate_var_trend(portfolio_ids, days)
            elif chart_type == DashboardChartType.DRAWDOWN:
                return await self._calculate_drawdown(portfolio_ids, days)
            elif chart_type == DashboardChartType.SARPE_RATIO:
                return await self._calculate_sharpe_ratio(portfolio_ids, days)
            elif chart_type == DashboardChartType.BETA:
                return await self._calculate_beta(portfolio_ids, days)
            elif chart_type == DashboardChartType.VOLATILITY:
                return await self._calculate_volatility(portfolio_ids, days)
            else:
                return []

        except Exception as e:
            self.logger.error(f"计算{chart_type.value}图表数据失败: {e}")
            return []

    async def _get_latest_metrics(self, portfolio_id: str) -> Optional[RiskMetrics]:
        """获取最新风险指标"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                var_95, var_99, sharpe_ratio, max_drawdown, beta, volatility,
                total_value, calculated_at
            FROM risk_metrics
            WHERE portfolio_id = '{portfolio_id}'
            ORDER BY calculated_at DESC
            LIMIT 1
            """

            result = await db_service.fetch_one(sql)

            if result:
                return RiskMetrics(
                    var_95=result["var_95"],
                    var_99=result["var_99"],
                    sharpe_ratio=result["sharpe_ratio"],
                    max_drawdown=result["max_drawdown"],
                    beta=result["beta"],
                    volatility=result["volatility"],
                    total_value=result["total_value"],
                    calculated_at=result["calculated_at"],
                )

            return None

        except Exception as e:
            self.logger.error(f"获取最新指标失败: {e}")
            return None

    async def _calculate_risk_trend(self, portfolio_ids: List[str], days: int) -> List[ChartDataPoint]:
        """计算风险趋势"""
        try:
            chart_points = []

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            date_range = []
            current_date = start_date

            while current_date <= end_date:
                date_range.append(current_date)
                current_date += timedelta(days=1)

            for portfolio_id in portfolio_ids[:10]:
                for date in date_range:
                    metrics = await self._get_metrics_by_date(portfolio_id, date)

                    if metrics:
                        chart_point = ChartDataPoint(
                            date=date,
                            value=metrics.var_95,
                            label=f"投资组合{portfolio_id}",
                            is_anomaly=metrics.var_95 > 0.05,
                        )
                        chart_points.append(chart_point)

            return chart_points

        except Exception as e:
            self.logger.error(f"计算风险趋势失败: {e}")
            return []

    async def _calculate_drawdown(self, portfolio_ids: List[str], days: int) -> List[ChartDataPoint]:
        """计算最大回撤"""
        try:
            chart_points = []

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            for portfolio_id in portfolio_ids[:10]:
                drawdowns = await self._get_drawdown_history(portfolio_id, start_date, end_date)

                for drawdown in drawdowns:
                    chart_point = ChartDataPoint(
                        date=drawdown["date"],
                        value=drawdown["max_drawdown"],
                        label=f"投资组合{portfolio_id}",
                        is_anomaly=abs(drawdown["max_drawdown"]) > 0.10,
                    )
                    chart_points.append(chart_point)

            return chart_points

        except Exception as e:
            self.logger.error(f"计算最大回撤失败: {e}")
            return []

    async def _calculate_sharpe_ratio(self, portfolio_ids: List[str], days: int) -> List[ChartDataPoint]:
        """计算夏普比率"""
        try:
            chart_points = []

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            for portfolio_id in portfolio_ids[:10]:
                sharpe_ratios = await self._get_sharpe_history(portfolio_id, start_date, end_date)

                for sharpe in sharpe_ratios:
                    chart_point = ChartDataPoint(
                        date=sharpe["date"],
                        value=sharpe["sharpe_ratio"],
                        label=f"投资组合{portfolio_id}",
                        is_anomaly=sharpe["sharpe_ratio"] < 0.5,
                    )
                    chart_points.append(chart_point)

            return chart_points

        except Exception as e:
            self.logger.error(f"计算夏普比率失败: {e}")
            return []

    async def _calculate_beta(self, portfolio_ids: List[str], days: int) -> List[ChartDataPoint]:
        """计算Beta系数"""
        try:
            chart_points = []

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            for portfolio_id in portfolio_ids[:10]:
                betas = await self._get_beta_history(portfolio_id, start_date, end_date)

                for beta in betas:
                    chart_point = ChartDataPoint(
                        date=beta["date"],
                        value=beta["beta"],
                        label=f"投资组合{portfolio_id}",
                        is_anomaly=beta["beta"] > 2.0,
                    )
                    chart_points.append(chart_point)

            return chart_points

        except Exception as e:
            self.logger.error(f"计算Beta系数失败: {e}")
            return []

    async def _calculate_volatility(self, portfolio_ids: List[str], days: int) -> List[ChartDataPoint]:
        """计算波动率"""
        try:
            chart_points = []

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            for portfolio_id in portfolio_ids[:10]:
                volatilities = await self._get_volatility_history(portfolio_id, start_date, end_date)

                for vol in volatilities:
                    chart_point = ChartDataPoint(
                        date=vol["date"],
                        value=vol["volatility"],
                        label=f"投资组合{portfolio_id}",
                        is_anomaly=vol["volatility"] > 0.4,
                    )
                    chart_points.append(chart_point)

            return chart_points

        except Exception as e:
            self.logger.error(f"计算波动率失败: {e}")
            return []

    async def _get_metrics_by_date(self, portfolio_id: str, date: datetime) -> Optional[RiskMetrics]:
        """按日期获取风险指标"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                var_95, var_99, sharpe_ratio, max_drawdown, beta, volatility,
                calculated_at
            FROM risk_metrics
            WHERE portfolio_id = '{portfolio_id}'
              AND DATE(calculated_at) = '{date.date()}'
            """

            result = await db_service.fetch_one(sql)

            if result:
                return RiskMetrics(
                    var_95=result["var_95"],
                    var_99=result["var_99"],
                    sharpe_ratio=result["sharpe_ratio"],
                    max_drawdown=result["max_drawdown"],
                    beta=result["beta"],
                    volatility=result["volatility"],
                    calculated_at=result["calculated_at"],
                )

            return None

        except Exception as e:
            self.logger.error(f"按日期获取指标失败: {e}")
            return None

    async def _get_drawdown_history(self, portfolio_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """获取回撤历史"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                date, max_drawdown, calculated_at
            FROM risk_metrics
            WHERE portfolio_id = '{portfolio_id}'
              AND date >= '{start_date.date()}'
              AND date <= '{end_date.date()}'
            ORDER BY date ASC
            """

            results = await db_service.fetch_many(sql)

            return [
                {"date": r["date"], "max_drawdown": r["max_drawdown"], "calculated_at": r["calculated_at"]}
                for r in results
            ]

        except Exception as e:
            self.logger.error(f"获取回撤历史失败: {e}")
            return []

    async def _get_sharpe_history(self, portfolio_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """获取夏普比率历史"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                date, sharpe_ratio, calculated_at
            FROM risk_metrics
            WHERE portfolio_id = '{portfolio_id}'
              AND date >= '{start_date.date()}'
              AND date <= '{end_date.date()}'
            ORDER BY date ASC
            """

            results = await db_service.fetch_many(sql)

            return [
                {"date": r["date"], "sharpe_ratio": r["sharpe_ratio"], "calculated_at": r["calculated_at"]}
                for r in results
            ]

        except Exception as e:
            self.logger.error(f"获取夏普比率历史失败: {e}")
            return []

    async def _get_beta_history(self, portfolio_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """获取Beta系数历史"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                date, beta, calculated_at
            FROM risk_metrics
            WHERE portfolio_id = '{portfolio_id}'
              AND date >= '{start_date.date()}'
              AND date <= '{end_date.date()}'
            ORDER BY date ASC
            """

            results = await db_service.fetch_many(sql)

            return [{"date": r["date"], "beta": r["beta"], "calculated_at": r["calculated_at"]} for r in results]

        except Exception as e:
            self.logger.error(f"获取Beta系数历史失败: {e}")
            return []

    async def _get_volatility_history(self, portfolio_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """获取波动率历史"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                date, volatility, calculated_at
            FROM risk_metrics
            WHERE portfolio_id = '{portfolio_id}'
              AND date >= '{start_date.date()}'
              AND date <= '{end_date.date()}'
            ORDER BY date ASC
            """

            results = await db_service.fetch_many(sql)

            return [
                {"date": r["date"], "volatility": r["volatility"], "calculated_at": r["calculated_at"]} for r in results
            ]

        except Exception as e:
            self.logger.error(f"获取波动率历史失败: {e}")
            return []

    async def _calculate_risk_trend(self, portfolio_id: str) -> str:
        """计算风险趋势"""
        try:
            current_metrics = await self._get_latest_metrics(portfolio_id)

            if not current_metrics:
                return "stable"

            one_week_ago = await self._get_metrics_by_date(portfolio_id, datetime.now() - timedelta(weeks=1))

            if not one_week_ago:
                return "stable"

            if current_metrics.var_95 < one_week_ago.var_95:
                return "decreasing"
            elif current_metrics.var_95 > one_week_ago.var_95:
                return "increasing"
            else:
                return "stable"

        except Exception as e:
            self.logger.error(f"计算风险趋势失败: {e}")
            return "unknown"

    async def generate_risk_report(
        self, portfolio_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict:
        """生成风险报告"""
        try:
            self._log_request_start("generate_risk_report", {"portfolio_id": portfolio_id})

            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            chart_data = await self._prepare_chart_data([portfolio_id])

            summary = await self.get_risk_dashboard_summary([portfolio_id])

            report = {
                "portfolio_id": portfolio_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "chart_data": chart_data,
                "summary": summary,
                "generated_at": datetime.now().isoformat(),
            }

            self.reports.append(report)
            self._log_request_success("generate_risk_report", report)

            return report

        except Exception as e:
            self._log_request_error("generate_risk_report", e)
            return {}

    async def get_dashboard(self, portfolio_id: str) -> Dict:
        """获取仪表盘数据（前端接口）"""
        try:
            summary = await self.get_risk_dashboard_summary([portfolio_id])

            return {
                "overview": summary["risk_overview"],
                "portfolio_risk": summary["portfolio_summaries"][0] if summary["portfolio_summaries"] else {},
                "chart_data": summary["chart_data"],
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"获取仪表盘失败: {e}")
            return {}
