"""
GPU 风险计算器的组合事件与集中度分析方法集。
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

import numpy as np

from src.governance.risk_management.core import PortfolioRiskMetrics

logger = logging.getLogger(__name__)


class GPURiskCalculatorPortfolioEventsMixin:
    """GPURiskCalculator 方法集 Part 3"""

    async def _publish_risk_event(self, event_type: str, data: Dict[str, Any]):
        """发布风险事件到异步总线"""
        try:
            if self.event_publisher:
                event = {"event_type": event_type, "timestamp": datetime.now().isoformat(), "data": data}
                await self.event_publisher.publish_event(event)
        except Exception:
            logger.error("发布风险事件失败: %(e)s")

    async def _publish_portfolio_risk_event(self, portfolio_id: str, metrics: PortfolioRiskMetrics):
        """发布组合风险更新事件"""
        try:
            if self.event_publisher:
                event_data = {
                    "portfolio_id": portfolio_id,
                    "risk_metrics": {
                        "var_1d_95": metrics.var_1d_95,
                        "max_drawdown": metrics.max_drawdown,
                        "sharpe_ratio": metrics.sharpe_ratio,
                        "beta": metrics.beta,
                        "hhi": metrics.hhi,
                        "top10_ratio": metrics.top10_ratio,
                        "max_single_position": metrics.max_single_position,
                        "risk_score": metrics.risk_score,
                        "risk_level": metrics.risk_level,
                        "timestamp": metrics.timestamp.isoformat(),
                    },
                    "computation_mode": "gpu" if self.gpu_processor else "cpu",
                    "user_id": metrics.user_id,
                }

                await self._publish_risk_event("portfolio_risk_update", event_data)
                logger.debug("✅ 组合风险事件已发布: %(portfolio_id)s")
        except Exception:
            logger.error("发布组合风险事件失败 %(portfolio_id)s: %(e)s")

    async def _publish_portfolio_event(
        self, event_type: str, portfolio_id: str, additional_data: Dict[str, Any] = None
    ):
        """发布组合相关事件"""
        try:
            if self.event_publisher:
                event_data = {
                    "portfolio_id": portfolio_id,
                    "timestamp": datetime.now().isoformat(),
                }
                if additional_data:
                    event_data.update(additional_data)

                await self._publish_risk_event(event_type, event_data)
                logger.debug("✅ 组合事件已发布: %(event_type)s - %(portfolio_id)s")
        except Exception:
            logger.error("发布组合事件失败 %(event_type)s %(portfolio_id)s: %(e)s")

    async def _check_portfolio_alerts(self, portfolio_id: str, metrics: PortfolioRiskMetrics):
        """检查组合风险告警条件"""
        try:
            alerts = []

            if metrics.risk_score >= 80:
                alerts.append(
                    {
                        "alert_type": "high_risk_score",
                        "severity": "critical",
                        "message": f"组合风险评分过高: {metrics.risk_score}",
                        "threshold": 80,
                        "current_value": metrics.risk_score,
                    }
                )

            if metrics.var_1d_95 >= 0.08:
                alerts.append(
                    {
                        "alert_type": "high_var",
                        "severity": "high",
                        "message": f"VaR值过高: {metrics.var_1d_95:.2%}",
                        "threshold": 0.08,
                        "current_value": metrics.var_1d_95,
                    }
                )

            if metrics.max_drawdown >= 0.15:
                alerts.append(
                    {
                        "alert_type": "high_drawdown",
                        "severity": "high",
                        "message": f"最大回撤过高: {metrics.max_drawdown:.2%}",
                        "threshold": 0.15,
                        "current_value": metrics.max_drawdown,
                    }
                )

            if metrics.hhi >= 0.3:
                alerts.append(
                    {
                        "alert_type": "high_concentration",
                        "severity": "medium",
                        "message": f"组合集中度过高 (HHI: {metrics.hhi:.3f})",
                        "threshold": 0.3,
                        "current_value": metrics.hhi,
                    }
                )

            if metrics.max_single_position >= 0.2:
                alerts.append(
                    {
                        "alert_type": "high_single_position",
                        "severity": "medium",
                        "message": f"单一持仓占比过高: {metrics.max_single_position:.2%}",
                        "threshold": 0.2,
                        "current_value": metrics.max_single_position,
                    }
                )

            if alerts:
                await self._publish_risk_event(
                    "portfolio_risk_alerts",
                    {
                        "portfolio_id": portfolio_id,
                        "alerts": alerts,
                        "alert_count": len(alerts),
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                logger.info("⚠️ 发布组合风险告警: %(portfolio_id)s - {len(alerts)} 个告警")

        except Exception:
            logger.error("检查组合告警失败 %(portfolio_id)s: %(e)s")

    async def calculate_portfolio_concentration_analysis(self, portfolio_id: str) -> Dict[str, Any]:
        """计算组合集中度分析并发布事件"""
        try:
            positions = await self._get_portfolio_positions(portfolio_id)
            if not positions:
                return {"error": "no_positions_found"}

            if self.gpu_processor:
                concentration_results = await self.gpu_processor.calculate_portfolio_concentration_gpu(positions)
            else:
                concentration_results = self._calculate_concentration_cpu(positions)

            await self._publish_risk_event(
                "portfolio_concentration_analysis",
                {
                    "portfolio_id": portfolio_id,
                    "concentration_results": concentration_results,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            logger.info("✅ 组合集中度分析完成并发布事件: %(portfolio_id)s")
            return concentration_results

        except Exception as error:
            logger.error("组合集中度分析失败 %(portfolio_id)s: %(e)s")
            await self._publish_risk_event(
                "portfolio_concentration_analysis_failed",
                {
                    "portfolio_id": portfolio_id,
                    "error": str(error),
                    "timestamp": datetime.now().isoformat(),
                },
            )
            return {"error": str(error)}

    def _calculate_concentration_cpu(self, positions: List[Dict]) -> Dict[str, Any]:
        """CPU后备方案计算集中度"""
        try:
            weights = np.array([position["weight"] for position in positions])
            hhi = float(np.sum(weights**2))
            max_single = float(np.max(weights))
            max_idx = np.argmax(weights)
            max_symbol = positions[max_idx]["symbol"]

            if len(weights) <= 10:
                top10_ratio = 1.0
            else:
                sorted_weights = np.sort(weights)[::-1]
                top10_ratio = float(np.sum(sorted_weights[:10]))

            concentration_score = self._calculate_concentration_score_cpu(hhi, max_single, top10_ratio)

            return {
                "hhi": hhi,
                "max_single_position": max_single,
                "max_single_symbol": max_symbol,
                "top10_ratio": top10_ratio,
                "concentration_score": concentration_score,
                "concentration_level": self._get_concentration_level_cpu(concentration_score),
                "computation_time": 0.0,
                "gpu_mode": False,
            }

        except Exception as error:
            logger.error("CPU集中度计算失败: %(e)s")
            return {
                "error": str(error),
                "hhi": 0.0,
                "max_single_position": 0.0,
                "top10_ratio": 0.0,
                "concentration_score": 0,
                "concentration_level": "unknown",
                "computation_time": 0.0,
                "gpu_mode": False,
            }

    def _calculate_concentration_score_cpu(self, hhi: float, max_single: float, top10_ratio: float) -> int:
        """CPU版本的集中度评分计算"""
        score = 0
        if hhi > 0.5:
            score += 40
        elif hhi > 0.25:
            score += 25
        elif hhi > 0.15:
            score += 10

        if max_single > 0.3:
            score += 30
        elif max_single > 0.2:
            score += 20
        elif max_single > 0.1:
            score += 10

        if top10_ratio > 0.8:
            score += 30
        elif top10_ratio > 0.6:
            score += 20
        elif top10_ratio > 0.4:
            score += 10

        return min(100, score)
