"""
风险管理扩展模块

提供高级风险管理、风险预警、风险组合优化、风险报告生成功能
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .risk_base import RiskBase, RiskMetrics, RiskLevel, RiskEventType
from .risk_monitoring import RiskMonitoring
from .risk_calculator import RiskCalculator

logger = __import__("logging").getLogger(__name__)


class RiskStrategyType(Enum):
    """风险管理策略类型"""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    DYNAMIC = "dynamic"
    CUSTOM = "custom"


class RiskObjective(Enum):
    """风险目标"""

    CAPITAL_PRESERVATION = "capital_preservation"
    MAXIMIZE_RETURN = "maximize_return"
    BALANCE = "balance"
    SPECIFIC_SECTOR = "specific_sector"
    ABSOLUTE_RETURN = "absolute_return"


class RiskOptimization:
    """风险优化结果"""

    optimization_id: str = ""
    portfolio_id: str = ""
    strategy_type: RiskStrategyType = RiskStrategyType.CONSERVATIVE
    objective: RiskObjective = RiskObjective.BALANCE
    original_risk: RiskMetrics = None
    optimized_risk: RiskMetrics = None
    expected_return: float = 0.0
    expected_volatility: float = 0.0
    risk_return_ratio: float = 0.0
    optimization_date: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "optimization_id": self.optimization_id,
            "portfolio_id": self.portfolio_id,
            "strategy_type": self.strategy_type.value,
            "objective": self.objective.value,
            "original_risk": self.original_risk.to_dict() if self.original_risk else None,
            "optimized_risk": self.optimized_risk.to_dict() if self.optimized_risk else None,
            "expected_return": f"{self.expected_return:.2%}",
            "expected_volatility": f"{self.expected_volatility:.2%}",
            "risk_return_ratio": f"{self.risk_return_ratio:.2f}",
            "optimization_date": self.optimization_date.isoformat() if self.optimization_date else None,
        }


@dataclass
class RiskEventExtended:
    """扩展风险事件"""

    event_id: str = ""
    event_type: RiskEventType = RiskEventType.MODEL_ERROR
    risk_level: RiskLevel = RiskLevel.LOW
    portfolio_id: str = ""
    stock_code: Optional[str] = None
    message: str = ""
    trigger_condition: str = ""
    trigger_value: float = 0.0
    triggered_at: Optional[datetime] = None
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    action_taken: Optional[str] = None
    action_effect: Optional[Dict[str, Any]] = None
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "risk_level": self.risk_level.value,
            "portfolio_id": self.portfolio_id,
            "stock_code": self.stock_code,
            "message": self.message,
            "trigger_condition": self.trigger_condition,
            "trigger_value": f"{self.trigger_value:.2f}",
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "is_resolved": self.is_resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "action_taken": self.action_taken,
            "action_effect": self.action_effect,
            "notes": self.notes,
        }


class RiskManagementExtended(RiskBase):
    """风险管理扩展类"""

    def __init__(self):
        super().__init__()
        self.risk_monitoring = RiskMonitoring()
        self.risk_calculator = RiskCalculator()
        self.risk_events = []
        self.risk_optimizations = []
        self.risk_thresholds = {
            "var_95_warning": 0.025,
            "var_99_warning": 0.040,
            "sharpe_warning": 1.0,
            "max_drawdown_warning": 0.15,
            "volatility_warning": 0.30,
        }
        self.risk_limits = {
            "max_single_position": 0.20,
            "max_total_position": 0.40,
            "max_sector_exposure": 0.25,
            "max_leverage": 1.5,
            "min_liquidity": 0.10,
        }

        logger.info("风险管理扩展模块初始化")

    async def optimize_risk_profile(
        self,
        portfolio_id: str,
        strategy_type: RiskStrategyType = RiskStrategyType.CONSERVATIVE,
        objective: RiskObjective = RiskObjective.BALANCE,
    ) -> RiskOptimization:
        """
        优化风险配置

        Args:
            portfolio_id: 投资组合ID
            strategy_type: 风险策略
            objective: 风险目标

        Returns:
            RiskOptimization: 优化结果
        """
        try:
            import uuid

            optimization_id = f"opt_{uuid.uuid4()}"

            # 获取当前风险指标
            current_risk = await self._get_portfolio_risk(portfolio_id)

            # 根据策略计算优化后的风险指标
            optimized_risk = self._apply_risk_strategy(current_risk, strategy_type, objective)

            # 计算预期收益率和波动率
            expected_return = optimized_risk.sharpe_ratio * (1 + optimized_risk.var_95) * 0.5
            expected_volatility = optimized_risk.var_95 * (1 + optimized_risk.var_99) * 0.3
            risk_return_ratio = expected_return / expected_volatility if expected_volatility > 0 else 0

            optimization = RiskOptimization(
                optimization_id=optimization_id,
                portfolio_id=portfolio_id,
                strategy_type=strategy_type,
                objective=objective,
                original_risk=current_risk,
                optimized_risk=optimized_risk,
                expected_return=expected_return,
                expected_volatility=expected_volatility,
                risk_return_ratio=risk_return_ratio,
                optimization_date=datetime.now(),
            )

            self.risk_optimizations.append(optimization)

            logger.info(f"风险配置已优化: {portfolio_id} - 策略{strategy_type.value}")
            return optimization

        except Exception as e:
            logger.error(f"优化风险配置失败: {e}")
            raise

    async def _get_portfolio_risk(self, portfolio_id: str) -> RiskMetrics:
        """获取投资组合风险指标"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                var_95, var_99, sharpe_ratio,
                max_drawdown, beta, volatility
            FROM portfolio_risk_metrics
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
                )

            logger.warning(f"未找到投资组合风险指标: {portfolio_id}")
            return RiskMetrics()

        except Exception as e:
            logger.error(f"获取投资组合风险指标失败: {e}")
            raise

    def _apply_risk_strategy(
        self, current_risk: RiskMetrics, strategy_type: RiskStrategyType, objective: RiskObjective
    ) -> RiskMetrics:
        """应用风险策略"""
        optimized_risk = RiskMetrics()

        if strategy_type == RiskStrategyType.CONSERVATIVE:
            # 保守策略：降低风险
            optimized_risk.var_95 = current_risk.var_95 * 0.8
            optimized_risk.var_99 = current_risk.var_99 * 0.7
            optimized_risk.sharpe_ratio = current_risk.sharpe_ratio * 0.9

        elif strategy_type == RiskStrategyType.MODERATE:
            # 中等策略：平衡风险和收益
            if objective == RiskObjective.MAXIMIZE_RETURN:
                optimized_risk.var_95 = current_risk.var_95 * 1.2
                optimized_risk.var_99 = current_risk.var_99 * 1.1
                optimized_risk.sharpe_ratio = current_risk.sharpe_ratio * 1.1
            else:
                optimized_risk.var_95 = current_risk.var_95 * 1.0
                optimized_risk.var_99 = current_risk.var_99 * 1.0
                optimized_risk.sharpe_ratio = current_risk.sharpe_ratio * 1.0

        elif strategy_type == RiskStrategyType.AGGRESSIVE:
            # 激进策略：最大化收益
            optimized_risk.var_95 = current_risk.var_95 * 1.5
            optimized_risk.var_99 = current_risk.var_99 * 1.4
            optimized_risk.sharpe_ratio = current_risk.sharpe_ratio * 1.3

        elif strategy_type == RiskStrategyType.DYNAMIC:
            # 动态策略：基于市场条件调整
            if objective == RiskObjective.BALANCE:
                optimized_risk.var_95 = current_risk.var_95 * 1.0
                optimized_risk.var_99 = current_risk.var_99 * 1.0
                optimized_risk.sharpe_ratio = current_risk.sharpe_ratio * 1.0
            else:
                optimized_risk.var_95 = current_risk.var_95 * 1.2
                optimized_risk.var_99 = current_risk.var_99 * 1.2
                optimized_risk.sharpe_ratio = current_risk.sharpe_ratio * 1.2

        elif strategy_type == RiskStrategyType.CUSTOM:
            # 自定义策略：使用用户提供的参数
            optimized_risk.var_95 = current_risk.var_95 * 1.0
            optimized_risk.var_99 = current_risk.var_99 * 1.0
            optimized_risk.sharpe_ratio = current_risk.sharpe_ratio * 1.0

        return optimized_risk

    async def check_portfolio_risk(self, portfolio_id: str) -> Dict:
        """
        检查投资组合风险

        Args:
            portfolio_id: 投资组合ID

        Returns:
            Dict: 风险检查结果
        """
        try:
            # 获取当前风险指标
            current_risk = await self._get_portfolio_risk(portfolio_id)

            # 检查各项风险阈值
            risk_warnings = []
            risk_level = RiskLevel.LOW

            # 检查方差
            if current_risk.var_95 > self.risk_thresholds["var_95_warning"]:
                risk_warnings.append(
                    {
                        "type": "var_95",
                        "current_value": f"{current_risk.var_95:.2%}",
                        "threshold": f"{self.risk_thresholds['var_95_warning']:.2%}",
                        "severity": "medium",
                    }
                )

                if current_risk.var_95 > self.risk_thresholds["var_99_warning"]:
                    risk_warnings.append(
                        {
                            "type": "var_99",
                            "current_value": f"{current_risk.var_99:.2%}",
                            "threshold": f"{self.risk_thresholds['var_99_warning']:.2%}",
                            "severity": "high",
                        }
                    )

            # 检查最大回撤
            if abs(current_risk.max_drawdown) > self.risk_thresholds["max_drawdown_warning"]:
                risk_warnings.append(
                    {
                        "type": "max_drawdown",
                        "current_value": f"{current_risk.max_drawdown:.2%}",
                        "threshold": f"{abs(self.risk_thresholds['max_drawdown_warning']):.2%}",
                        "severity": "high",
                    }
                )

            # 检查夏普比率
            if current_risk.sharpe_ratio < self.risk_thresholds["sharpe_warning"]:
                risk_warnings.append(
                    {
                        "type": "sharpe_ratio",
                        "current_value": f"{current_risk.sharpe_ratio:.2f}",
                        "threshold": f"{self.risk_thresholds['sharpe_warning']:.2f}",
                        "severity": "medium",
                    }
                )

            # 检查波动率
            if current_risk.volatility > self.risk_thresholds["volatility_warning"]:
                risk_warnings.append(
                    {
                        "type": "volatility",
                        "current_value": f"{current_risk.volatility:.2%}",
                        "threshold": f"{self.risk_thresholds['volatility_warning']:.2%}",
                        "severity": "medium",
                    }
                )

            # 计算综合风险等级
            if len(risk_warnings) >= 3:
                risk_level = RiskLevel.HIGH
            elif len(risk_warnings) >= 1:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW

            # 生成风险报告
            report = self._generate_risk_report(portfolio_id, current_risk, risk_warnings, risk_level)

            self.log_risk_event(portfolio_id, RiskEventType.MODEL_ERROR, risk_level, report["summary"])

            return {
                "portfolio_id": portfolio_id,
                "current_risk": current_risk.to_dict(),
                "risk_warnings": risk_warnings,
                "risk_level": risk_level.value,
                "report": report,
                "checked_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"检查投资组合风险失败: {e}")
            return {
                "portfolio_id": portfolio_id,
                "current_risk": {},
                "risk_warnings": [],
                "risk_level": "error",
                "report": {},
                "checked_at": datetime.now().isoformat(),
                "error": str(e),
            }

    def _generate_risk_report(
        self, portfolio_id: str, current_risk: RiskMetrics, risk_warnings: List[Dict], risk_level: RiskLevel
    ) -> Dict:
        """生成风险报告"""
        try:
            summary_parts = []

            # 风险等级总结
            summary_parts.append(f"综合风险等级: {risk_level.value}")

            # 风险警告总结
            if risk_warnings:
                summary_parts.append(f"发现{len(risk_warnings)}个风险问题")
                for warning in risk_warnings[:3]:
                    severity = warning["severity"]
                    summary_parts.append(f"  - {warning['type']}: {warning['message']} (严重性: {severity})")

            # 建议
            recommendations = self._generate_risk_recommendations(current_risk, risk_warnings)
            for rec in recommendations:
                summary_parts.append(f"  - {rec}")

            summary = "\n".join(summary_parts)

            return {
                "portfolio_id": portfolio_id,
                "current_risk": current_risk.to_dict(),
                "risk_warnings": risk_warnings,
                "risk_level": risk_level.value,
                "recommendations": recommendations,
                "summary": summary,
                "generated_at": datetime.now(),
            }

        except Exception as e:
            logger.error(f"生成风险报告失败: {e}")
            return {}

    def _generate_risk_recommendations(self, current_risk: RiskMetrics, risk_warnings: List[Dict]) -> List[str]:
        """生成风险建议"""
        recommendations = []

        # 基于方差给出建议
        if current_risk.var_95 > 0.040:
            recommendations.append("考虑降低投资组合的持仓比例，以减少整体波动率")

        # 基于夏普比率给出建议
        if current_risk.sharpe_ratio < 0.5:
            recommendations.append("投资组合的夏普比率较低，建议增加高收益资产的配置")
        elif current_risk.sharpe_ratio > 2.0:
            recommendations.append("投资组合的夏普比率较高，建议检查风险资产的配置")

        # 基于最大回撤给出建议
        if abs(current_risk.max_drawdown) > 0.20:
            recommendations.append("投资组合的最大回撤较大，建议设置止损点")

        # 基于Beta值给出建议
        if abs(current_risk.beta) > 1.5:
            recommendations.append("投资组合的Beta系数较高，建议分散行业风险")
        elif abs(current_risk.beta) < 0.5:
            recommendations.append("投资组合的Beta系数较低，建议增加防御性资产")

        if not recommendations:
            recommendations.append("风险水平正常，当前配置合理")

        return recommendations

    async def create_risk_alert(self, portfolio_id: str, risk_level: RiskLevel, message: str) -> RiskEventExtended:
        """
        创建风险告警

        Args:
            portfolio_id: 投资组合ID
            risk_level: 风险等级
            message: 告警消息

        Returns:
            RiskEventExtended: 扩展风险事件
        """
        try:
            import uuid

            event_id = f"event_{uuid.uuid4()}"

            # 创建扩展风险事件
            event = RiskEventExtended(
                event_id=event_id,
                event_type=RiskEventType.THRESHOLD_BREACH,
                risk_level=risk_level,
                portfolio_id=portfolio_id,
                message=message,
                trigger_condition=f"risk_level_{risk_level.value}",
                trigger_value=0.0,
                triggered_at=datetime.now(),
                is_resolved=False,
                notes=f"系统自动检测到{risk_level.value}风险等级",
            )

            self.risk_events.append(event)

            # 记录到日志
            self.log_risk_event(portfolio_id, RiskEventType.THRESHOLD_BREACH, risk_level, f"风险告警创建: {message}")

            logger.info(f"风险告警已创建: {event_id}")
            return event

        except Exception as e:
            logger.error(f"创建风险告警失败: {e}")
            raise

    async def get_risk_event_history(self, portfolio_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取风险事件历史"""
        try:
            # 过滤风险事件
            portfolio_events = [e for e in self.risk_events if e.portfolio_id == portfolio_id]

            # 分页
            start_idx = offset
            end_idx = min(start_idx + limit, len(portfolio_events))
            page_events = portfolio_events[start_idx:end_idx]

            return [event.to_dict() for event in page_events]

        except Exception as e:
            logger.error(f"获取风险事件历史失败: {e}")
            return []

    async def resolve_risk_event(self, event_id: str, action_taken: str, action_effect: Dict[str, Any]) -> bool:
        """
        解决风险事件

        Args:
            event_id: 事件ID
            action_taken: 采取的行动
            action_effect: 行动效果

        Returns:
            bool: 是否解决成功
        """
        try:
            # 查找事件
            event = next((e for e in self.risk_events if e.event_id == event_id), None)

            if not event:
                logger.warning(f"风险事件不存在: {event_id}")
                return False

            event.is_resolved = True
            event.resolved_at = datetime.now()
            event.action_taken = action_taken
            event.action_effect = action_effect
            event.notes = f"系统在{event.resolved_at}执行了{action_taken}操作"

            logger.info(f"风险事件已解决: {event_id}")
            return True

        except Exception as e:
            logger.error(f"解决风险事件失败: {e}")
            return False

    async def get_risk_summary(self, user_id: str) -> Dict:
        """
        获取用户风险摘要

        Args:
            user_id: 用户ID

        Returns:
            Dict: 风险摘要
        """
        try:
            # 获取所有投资组合的风险状态
            from app.core.database import db_service

            sql = f"""
            SELECT 
                portfolio_id,
                COUNT(*) as event_count,
                COUNT(*) as active_alerts,
                SUM(CASE WHEN is_resolved = FALSE THEN 1 ELSE 0) as unresolved_count
            FROM portfolio_risk_events
            WHERE user_id = '{user_id}'
            GROUP BY portfolio_id
            """

            results = await db_service.fetch_many(sql)

            total_portfolios = len(results)
            total_events = sum(r["event_count"] for r in results)
            total_active_alerts = sum(r["active_alerts"] for r in results)
            total_unresolved = sum(r["unresolved_count"] for r in results)

            summary = {
                "user_id": user_id,
                "total_portfolios": total_portfolios,
                "total_events": total_events,
                "total_active_alerts": total_active_alerts,
                "total_unresolved": total_unresolved,
                "generated_at": datetime.now().isoformat(),
            }

            logger.info(f"用户{user_id}风险摘要: {total_portfolios}个投资组合，{total_active_alerts}个活跃告警")
            return summary

        except Exception as e:
            logger.error(f"获取用户风险摘要失败: {e}")
            return {
                "user_id": user_id,
                "total_portfolios": 0,
                "total_events": 0,
                "total_active_alerts": 0,
                "total_unresolved": 0,
                "generated_at": datetime.now().isoformat(),
                "error": str(e),
            }

    async def get_risk_limits(self) -> Dict:
        """获取风险限制配置"""
        return {
            "var_95_warning": f"{self.risk_thresholds['var_95_warning']:.2%}",
            "var_99_warning": f"{self.risk_thresholds['var_99_warning']:.2%}",
            "sharpe_warning": f"{self.risk_thresholds['sharpe_warning']:.2f}",
            "max_drawdown_warning": f"{abs(self.risk_thresholds['max_drawdown_warning']):.2%}",
            "volatility_warning": f"{self.risk_thresholds['volatility_warning']:.2%}",
            "limits": self.risk_limits,
        }

    async def update_risk_thresholds(self, new_thresholds: Dict[str, float]) -> bool:
        """更新风险阈值"""
        try:
            # 更新阈值
            self.risk_thresholds.update(new_thresholds)

            # 验证阈值合理性
            if new_thresholds.get("var_95_warning", 0.0) < 0:
                logger.warning("方差阈值不能为负数")
                return False

            if new_thresholds.get("var_99_warning", 0.0) < new_thresholds.get("var_95_warning", 0.0):
                logger.warning("var_99阈值不能小于var_95阈值")
                return False

            logger.info(f"风险阈值已更新: {new_thresholds}")
            return True

        except Exception as e:
            logger.error(f"更新风险阈值失败: {e}")
            return False

    def log_risk_event(self, portfolio_id: str, event_type: RiskEventType, risk_level: RiskLevel, message: str):
        """记录风险事件"""
        try:
            import uuid

            event = RiskEvent(
                event_id=f"event_{uuid.uuid4()}",
                event_type=event_type,
                risk_level=risk_level,
                portfolio_id=portfolio_id,
                message=message,
            )

            self.events_history.append(event)

            logger.info(f"风险事件记录: {message}")

        except Exception as e:
            logger.error(f"记录风险事件失败: {e}")
