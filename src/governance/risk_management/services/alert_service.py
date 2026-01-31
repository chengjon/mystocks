"""
风险告警服务实现
Risk Alert Service Implementation

实现三级风险预警系统，复用现有的MonitoredNotificationManager。
支持多渠道告警通知和智能去重机制。
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.governance.risk_management.core import IRiskAlertService, RiskAlert

# 复用现有的通知基础设施
try:
    from src.ml_strategy.automation.notification_manager import (
        NotificationLevel,
    )
    from src.governance.risk_management.services.risk_alert_notification_manager import (
        NotificationChannel,
        NotificationConfig,
        RiskAlertNotificationManager,
    )

    NOTIFICATION_AVAILABLE = True
except ImportError:
    # 回退到基础的MonitoredNotificationManager
    try:
        from src.ml_strategy.automation.notification_manager import (
            NotificationLevel,
        )
        from src.ml_strategy.automation.monitored_notification_manager import (
            MonitoredNotificationManager,
            NotificationChannel,
            NotificationConfig,
        )

        RiskAlertNotificationManager = MonitoredNotificationManager  # 兼容性别名
        NOTIFICATION_AVAILABLE = True
    except ImportError:
        NOTIFICATION_AVAILABLE = False

logger = logging.getLogger(__name__)


class RiskAlertService(IRiskAlertService):
    """
    风险告警服务实现

    实现三级预警体系，支持多渠道通知和智能去重。
    复用现有的MonitoredNotificationManager基础设施。
    """

    def __init__(self):
        self.notification_manager = None
        self.alert_history = {}  # 内存缓存，避免重复告警
        self._initialize_notification_manager()

    def _initialize_notification_manager(self):
        """初始化通知管理器"""
        if NOTIFICATION_AVAILABLE:
            # 创建通知配置 (可以后续从配置文件读取)
            notification_config = NotificationConfig(
                channels=[NotificationChannel.EMAIL, NotificationChannel.LOG],
                email_from="risk@mystocks.com",
                email_to=["trader@mystocks.com"],
                rate_limit=300,  # 5分钟内相同告警最多发送一次
            )

            self.notification_manager = RiskAlertNotificationManager(notification_config)
            logger.info("✅ 风险告警服务初始化成功")
        else:
            logger.warning("⚠️ 通知基础设施不可用，告警功能将受限")

    async def evaluate_risk_level(self, metrics: Dict) -> str:
        """
        评估风险等级

        基于各项风险指标综合评估总体风险等级。
        返回: safe/attention/warning/danger
        """
        try:
            # 风险评分计算
            scores = []

            # 1. 波动率风险评分
            volatility = metrics.get("volatility_20d", 0)
            scores.append(self._score_volatility(volatility))

            # 2. 流动性风险评分
            liquidity_score = metrics.get("liquidity_score", 50)
            scores.append(self._score_liquidity(liquidity_score))

            # 3. 集中度风险评分 (如果是组合风险)
            hhi = metrics.get("hhi", 0)
            if hhi > 0:
                scores.append(self._score_concentration(hhi))

            # 4. VaR风险评分
            var_1d = metrics.get("var_1d_95", 0)
            if var_1d > 0:
                scores.append(self._score_var(var_1d))

            # 5. 技术指标风险评分
            technical_score = self._score_technical_indicators(metrics)
            scores.append(technical_score)

            # 综合评分 (取最高风险等级)
            max_score = max(scores) if scores else 0

            return self._map_score_to_level(max_score)

        except Exception as e:
            logger.error("评估风险等级失败: %(e)s")
            return "attention"  # 默认中等风险

    async def generate_alerts(self, risk_metrics: Dict) -> List[RiskAlert]:
        """
        生成风险告警

        基于风险指标生成相应的告警信息。
        实现智能去重，避免重复告警。
        """
        try:
            alerts = []

            # 评估总体风险等级
            overall_risk_level = await self.evaluate_risk_level(risk_metrics)

            # 如果是安全等级，不生成告警
            if overall_risk_level == "safe":
                return alerts

            # 检查是否需要生成告警 (去重逻辑)
            alert_key = self._generate_alert_key(risk_metrics, overall_risk_level)
            if self._should_skip_alert(alert_key, overall_risk_level):
                return alerts

            # 生成具体告警
            symbol = risk_metrics.get("symbol")
            portfolio_id = risk_metrics.get("portfolio_id")

            alert = RiskAlert(
                alert_type="risk_level_change",
                severity=overall_risk_level,
                message=self._generate_alert_message(risk_metrics, overall_risk_level),
                symbol=symbol,
                portfolio_id=portfolio_id,
                metrics=risk_metrics,
                timestamp=datetime.now(),
            )

            alerts.append(alert)

            # 记录告警历史 (用于去重)
            self._record_alert_history(alert_key, overall_risk_level)

            return alerts

        except Exception as e:
            logger.error("生成风险告警失败: %(e)s")
            return []

    async def send_alerts(self, alerts: List[RiskAlert]) -> bool:
        """
        发送告警通知

        通过多渠道发送告警信息。
        使用增强的RiskAlertNotificationManager实现智能告警功能。
        """
        try:
            if not self.notification_manager:
                logger.warning("通知管理器不可用，跳过告警发送")
                return False

            # 检查是否支持高级风险告警功能
            if hasattr(self.notification_manager, "send_risk_alert"):
                # 使用高级风险告警功能
                return await self._send_enhanced_alerts(alerts)
            else:
                # 回退到基础告警功能
                return await self._send_basic_alerts(alerts)

        except Exception as e:
            logger.error("发送告警通知失败: %(e)s")
            return False

    async def _send_enhanced_alerts(self, alerts: List[RiskAlert]) -> bool:
        """使用增强的风险告警功能发送告警"""
        try:
            success_count = 0

            for alert in alerts:
                try:
                    # 确定告警类型
                    alert_type = self._map_alert_to_type(alert)

                    # 发送增强的风险告警
                    if alert.symbol:
                        # 个股风险告警
                        alert_triggers = self._extract_alert_triggers(alert)
                        result = await self.notification_manager.send_stock_risk_alert(
                            symbol=alert.symbol,
                            risk_level=alert.severity,
                            risk_metrics=alert.metrics,
                            alert_triggers=alert_triggers,
                        )
                    elif alert.portfolio_id:
                        # 组合风险告警
                        triggered_alerts = self._extract_triggered_alerts(alert)
                        result = await self.notification_manager.send_portfolio_risk_alert(
                            portfolio_id=alert.portfolio_id,
                            risk_level=alert.severity,
                            risk_metrics=alert.metrics,
                            triggered_alerts=triggered_alerts,
                        )
                    else:
                        # 通用风险告警
                        result = await self.notification_manager.send_risk_alert(
                            alert_type=alert_type,
                            severity=alert.severity,
                            message=alert.message,
                            metrics=alert.metrics,
                        )

                    if result.get("sent", False):
                        success_count += 1
                        logger.info("增强风险告警发送成功: {alert.symbol or alert.portfolio_id} - {alert.severity")
                        if result.get("escalated"):
                            logger.info("告警已升级: {result.get('severity')")
                        if result.get("aggregated_count", 1) > 1:
                            logger.info("告警已聚合: {result['aggregated_count']} 次")
                    else:
                        logger.warning(
                            f"增强风险告警发送失败: {alert.symbol or alert.portfolio_id} - {result.get('reason', 'unknown')}"
                        )

                except Exception as e:
                    logger.error("发送增强告警失败: %(e)s")
                    continue

            return success_count == len(alerts)

        except Exception as e:
            logger.error("增强告警发送过程失败: %(e)s")
            return False

    async def _send_basic_alerts(self, alerts: List[RiskAlert]) -> bool:
        """使用基础告警功能发送告警（兼容模式）"""
        try:
            success_count = 0

            for alert in alerts:
                try:
                    # 转换为通知格式
                    notification_level = self._map_alert_severity_to_notification_level(alert.severity)

                    # 构建通知消息
                    title = self._generate_notification_title(alert)
                    message = self._generate_notification_message(alert)

                    # 发送通知
                    success = await self.notification_manager.send_signal_notification(
                        strategy_name="Risk Management System",
                        symbol=alert.symbol or "PORTFOLIO",
                        signal=alert.severity.upper(),
                        price=0.0,  # 风险告警没有价格
                        context={
                            "alert_type": alert.alert_type,
                            "severity": alert.severity,
                            "message": alert.message,
                            "metrics": alert.metrics,
                        },
                        signal_id=f"risk_alert_{alert.timestamp.strftime('%Y%m%d_%H%M%S')}",
                    )

                    if success:
                        success_count += 1
                        logger.info("基础风险告警发送成功: {alert.symbol or alert.portfolio_id} - {alert.severity")
                    else:
                        logger.warning("基础风险告警发送失败: {alert.symbol or alert.portfolio_id")

                except Exception as e:
                    logger.error("发送基础告警失败: %(e)s")
                    continue

            return success_count == len(alerts)

        except Exception as e:
            logger.error("基础告警发送过程失败: %(e)s")
            return False

    # 私有辅助方法

    def _score_volatility(self, volatility: float) -> int:
        """波动率风险评分 (0-100)"""
        # 年化波动率评分标准
        if volatility < 0.15:  # 15%以下 - 低风险
            return 10
        elif volatility < 0.25:  # 15-25% - 中等风险
            return 30
        elif volatility < 0.40:  # 25-40% - 高风险
            return 60
        else:  # 40%以上 - 极高风险
            return 90

    def _score_liquidity(self, liquidity_score: int) -> int:
        """流动性风险评分 (0-100)"""
        # 流动性评分标准 (0-100, 越高越好)
        if liquidity_score >= 80:  # 流动性极好
            return 10
        elif liquidity_score >= 60:  # 流动性良好
            return 20
        elif liquidity_score >= 40:  # 流动性一般
            return 40
        elif liquidity_score >= 20:  # 流动性较差
            return 70
        else:  # 流动性极差
            return 95

    def _score_concentration(self, hhi: float) -> int:
        """集中度风险评分 (0-100)"""
        # HHI指数评分标准
        if hhi < 0.1:  # 高度分散
            return 10
        elif hhi < 0.2:  # 中等分散
            return 25
        elif hhi < 0.3:  # 中等集中
            return 45
        elif hhi < 0.4:  # 较高集中
            return 70
        else:  # 高度集中
            return 90

    def _score_var(self, var_1d: float) -> int:
        """VaR风险评分 (0-100)"""
        # 1日VaR评分标准 (假设投资额100万)
        if var_1d < 0.02:  # 日损失<2万
            return 15
        elif var_1d < 0.05:  # 日损失<5万
            return 35
        elif var_1d < 0.08:  # 日损失<8万
            return 55
        elif var_1d < 0.12:  # 日损失<12万
            return 75
        else:  # 日损失>12万
            return 95

    def _score_technical_indicators(self, metrics: Dict) -> int:
        """技术指标风险评分 (0-100)"""
        score = 30  # 基础分数

        # RSI超买超卖
        rsi = metrics.get("rsi", 50)
        if rsi > 70 or rsi < 30:
            score += 20

        # MACD信号
        macd_trend = metrics.get("macd_signal", "neutral")
        if macd_trend in ["bearish", "bullish"]:
            score += 10

        # 布林带位置
        bollinger_pos = metrics.get("bollinger_position", "middle")
        if bollinger_pos in ["upper", "lower"]:
            score += 15

        return min(100, score)

    def _map_score_to_level(self, score: int) -> str:
        """将综合评分映射为风险等级"""
        if score >= 80:
            return "danger"
        elif score >= 60:
            return "warning"
        elif score >= 40:
            return "attention"
        else:
            return "safe"

    def _generate_alert_key(self, metrics: Dict, risk_level: str) -> str:
        """生成告警唯一键 (用于去重)"""
        symbol = metrics.get("symbol", "unknown")
        portfolio_id = metrics.get("portfolio_id", "unknown")
        return f"{symbol}_{portfolio_id}_{risk_level}"

    def _should_skip_alert(self, alert_key: str, risk_level: str) -> bool:
        """检查是否应该跳过告警 (去重逻辑)"""
        now = datetime.now()

        # 获取历史告警记录
        history = self.alert_history.get(alert_key, [])

        # 只保留最近30分钟的记录
        recent_history = [record for record in history if (now - record["timestamp"]).total_seconds() < 1800]  # 30分钟

        # 更新历史记录
        self.alert_history[alert_key] = recent_history

        # 检查是否在30分钟内已经发送过相同等级的告警
        for record in recent_history:
            if record["risk_level"] == risk_level:
                logger.info("跳过重复告警: %(alert_key)s (30分钟内已发送)")
                return True

        return False

    def _record_alert_history(self, alert_key: str, risk_level: str):
        """记录告警历史"""
        if alert_key not in self.alert_history:
            self.alert_history[alert_key] = []

        self.alert_history[alert_key].append({"risk_level": risk_level, "timestamp": datetime.now()})

    def _generate_alert_message(self, metrics: Dict, risk_level: str) -> str:
        """生成告警消息"""
        symbol = metrics.get("symbol")
        portfolio_id = metrics.get("portfolio_id")

        target = f"股票{symbol}" if symbol else f"组合{portfolio_id}"

        if risk_level == "danger":
            return f"🚨 紧急告警: {target}风险等级为危险，建议立即采取行动"
        elif risk_level == "warning":
            return f"⚠️ 警告: {target}风险等级为警告，请密切关注"
        elif risk_level == "attention":
            return f"🔔 注意: {target}风险等级为注意，建议关注"
        else:
            return f"ℹ️ 信息: {target}风险指标发生变化"

    def _map_alert_severity_to_notification_level(self, severity: str) -> NotificationLevel:
        """映射告警严重程度到通知级别"""
        mapping = {
            "danger": NotificationLevel.ERROR,
            "warning": NotificationLevel.WARNING,
            "attention": NotificationLevel.INFO,
            "safe": NotificationLevel.DEBUG,
        }
        return mapping.get(severity, NotificationLevel.INFO)

    def _generate_notification_title(self, alert: RiskAlert) -> str:
        """生成通知标题"""
        target = alert.symbol or f"组合{alert.portfolio_id}"
        severity_emoji = {"danger": "🚨", "warning": "⚠️", "attention": "🔔", "safe": "ℹ️"}.get(alert.severity, "ℹ️")

        return f"{severity_emoji} 风险告警 - {target}"

    def _generate_notification_message(self, alert: RiskAlert) -> str:
        """生成通知消息"""
        return alert.message

    # 新增增强告警方法

    def _map_alert_to_type(self, alert: RiskAlert) -> str:
        """映射告警到告警类型"""
        type_mapping = {
            "risk_level_change": "portfolio_risk",
            "var_exceeded": "var_exceeded",
            "concentration_high": "concentration_high",
            "volatility_spike": "volatility_spike",
        }
        return type_mapping.get(alert.alert_type, "general_risk")

    def _extract_alert_triggers(self, alert: RiskAlert) -> List[str]:
        """从告警中提取触发原因"""
        triggers = []

        metrics = alert.metrics or {}

        # 检查VaR触发
        if metrics.get("var_1d_95", 0) > 0.08:
            triggers.append("VaR超限")

        # 检查波动率触发
        if metrics.get("volatility_20d", 0) > 0.40:
            triggers.append("高波动率")

        # 检查集中度触发
        if metrics.get("hhi", 0) > 0.30:
            triggers.append("集中度过高")

        # 检查流动性触发
        if metrics.get("liquidity_score", 50) < 30:
            triggers.append("流动性不足")

        # 如果没有具体触发原因，使用告警类型
        if not triggers:
            triggers.append(alert.alert_type.replace("_", " ").title())

        return triggers

    def _extract_triggered_alerts(self, alert: RiskAlert) -> List[Dict[str, Any]]:
        """从组合告警中提取触发的具体告警"""
        # 这里可以根据实际的告警生成逻辑来提取
        # 暂时返回一个示例告警
        return [
            {
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "triggered_at": alert.timestamp,
            }
        ]


# 创建全局实例
_risk_alert_service_instance: Optional[RiskAlertService] = None


def get_risk_alert_service() -> RiskAlertService:
    """获取风险告警服务实例（单例模式）"""
    global _risk_alert_service_instance
    if _risk_alert_service_instance is None:
        _risk_alert_service_instance = RiskAlertService()
    return _risk_alert_service_instance
