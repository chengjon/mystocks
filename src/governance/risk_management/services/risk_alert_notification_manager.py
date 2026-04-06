"""
风险告警专用通知管理器
Risk Alert Notification Manager

扩展MonitoredNotificationManager，支持高级风险告警功能。
实现三级预警体系、智能去重、告警升级等功能。
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.ml_strategy.automation.monitored_notification_manager import (
    MonitoredNotificationManager,
    NotificationConfig,
    NotificationLevel,
)

logger = logging.getLogger(__name__)


class RiskAlertNotificationManager(MonitoredNotificationManager):
    """
    风险告警专用通知管理器

    扩展MonitoredNotificationManager，增加：
    - 三级预警体系 (info/warning/critical)
    - 智能去重机制 (基于内容和时间窗口)
    - 告警升级逻辑 (低级告警升级为高级)
    - 告警抑制 (避免告警风暴)
    - 告警聚合 (相同类型告警合并)
    - 告警历史和趋势分析
    """

    def __init__(
        self,
        config: Optional[NotificationConfig] = None,
        strategy_id: str = "risk_management",
        enable_db_logging: bool = True,
        deduplication_window: int = 300,  # 5分钟去重窗口
        escalation_threshold: int = 3,  # 3次相同告警后升级
        suppression_window: int = 60,  # 1分钟抑制窗口
    ):
        """
        初始化风险告警通知管理器

        Args:
            config: 通知配置
            strategy_id: 策略ID
            enable_db_logging: 启用数据库日志
            deduplication_window: 去重时间窗口(秒)
            escalation_threshold: 升级阈值
            suppression_window: 抑制时间窗口(秒)
        """
        super().__init__(config, strategy_id, enable_db_logging)

        # 风险告警专用配置
        self.deduplication_window = deduplication_window
        self.escalation_threshold = escalation_threshold
        self.suppression_window = suppression_window

        # 告警状态跟踪
        self.alert_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.suppressed_alerts: Dict[str, datetime] = {}
        self.alert_escalation_count: Dict[str, int] = defaultdict(int)

        # 三级预警统计
        self.alert_stats = {
            "info": {"sent": 0, "suppressed": 0, "escalated": 0},
            "warning": {"sent": 0, "suppressed": 0, "escalated": 0},
            "critical": {"sent": 0, "suppressed": 0, "escalated": 0},
        }

        logger.info("✅ 风险告警通知管理器初始化完成")

    async def send_risk_alert(
        self,
        alert_type: str,
        severity: str,
        symbol: Optional[str] = None,
        portfolio_id: Optional[str] = None,
        message: str = "",
        metrics: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        发送风险告警

        Args:
            alert_type: 告警类型 ('var_exceeded', 'concentration_high', 'volatility_spike', etc.)
            severity: 严重程度 ('info', 'warning', 'critical')
            symbol: 股票代码
            portfolio_id: 组合ID
            message: 告警消息
            metrics: 风险指标数据
            context: 额外上下文信息

        Returns:
            发送结果字典
        """
        try:
            alert_key = self._generate_alert_key(alert_type, symbol, portfolio_id)

            # 1. 检查是否应该抑制告警
            if self._is_alert_suppressed(alert_key):
                self.alert_stats[severity]["suppressed"] += 1
                return {
                    "sent": False,
                    "reason": "suppressed",
                    "alert_key": alert_key,
                    "suppressed_until": self.suppressed_alerts[alert_key],
                }

            # 2. 检查是否应该升级告警
            escalated_severity = self._check_alert_escalation(alert_key, severity)
            if escalated_severity != severity:
                logger.info("告警升级: %(severity)s -> %(escalated_severity)s (%(alert_key)s)")
                severity = escalated_severity
                self.alert_stats[severity]["escalated"] += 1

            # 3. 聚合相同类型的告警
            aggregated_alert = self._aggregate_similar_alerts(alert_type, severity, symbol, portfolio_id)

            # 4. 构建告警消息
            full_message = self._build_risk_alert_message(
                alert_type, severity, symbol, portfolio_id, message, metrics, aggregated_alert
            )

            # 5. 发送告警
            success = await self._send_risk_notification(
                alert_type, severity, symbol, portfolio_id, full_message, metrics, context
            )

            # 6. 更新告警历史和状态
            if success:
                self._update_alert_history(alert_key, severity, alert_type)
                self.alert_stats[severity]["sent"] += 1

                # 设置抑制窗口
                if severity == "critical":
                    self.suppressed_alerts[alert_key] = datetime.now() + timedelta(seconds=self.suppression_window)

            return {
                "sent": success,
                "severity": severity,
                "alert_key": alert_key,
                "aggregated_count": aggregated_alert.get("count", 1),
                "escalated": escalated_severity != severity,
            }

        except Exception as e:
            logger.error("发送风险告警失败: %(e)s")
            return {"sent": False, "error": str(e)}

    async def send_portfolio_risk_alert(
        self,
        portfolio_id: str,
        risk_level: str,
        risk_metrics: Dict[str, Any],
        triggered_alerts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        发送组合风险告警

        Args:
            portfolio_id: 组合ID
            risk_level: 风险等级
            risk_metrics: 风险指标
            triggered_alerts: 触发的具体告警列表

        Returns:
            发送结果
        """
        try:
            # 确定告警严重程度
            severity = self._map_risk_level_to_severity(risk_level)

            # 构建告警消息
            message = self._build_portfolio_alert_message(portfolio_id, risk_level, risk_metrics, triggered_alerts)

            # 发送告警
            result = await self.send_risk_alert(
                alert_type="portfolio_risk",
                severity=severity,
                portfolio_id=portfolio_id,
                message=message,
                metrics=risk_metrics,
                context={"triggered_alerts": triggered_alerts},
            )

            return result

        except Exception as e:
            logger.error("发送组合风险告警失败 %(portfolio_id)s: %(e)s")
            return {"sent": False, "error": str(e)}

    async def send_stock_risk_alert(
        self,
        symbol: str,
        risk_level: str,
        risk_metrics: Dict[str, Any],
        alert_triggers: List[str],
    ) -> Dict[str, Any]:
        """
        发送个股风险告警

        Args:
            symbol: 股票代码
            risk_level: 风险等级
            risk_metrics: 风险指标
            alert_triggers: 告警触发原因列表

        Returns:
            发送结果
        """
        try:
            severity = self._map_risk_level_to_severity(risk_level)
            alert_type = "stock_risk_" + "_".join(alert_triggers[:2])  # 取前两个触发原因

            message = self._build_stock_alert_message(symbol, risk_level, risk_metrics, alert_triggers)

            result = await self.send_risk_alert(
                alert_type=alert_type,
                severity=severity,
                symbol=symbol,
                message=message,
                metrics=risk_metrics,
                context={"alert_triggers": alert_triggers},
            )

            return result

        except Exception as e:
            logger.error("发送个股风险告警失败 %(symbol)s: %(e)s")
            return {"sent": False, "error": str(e)}

    def get_alert_statistics(self) -> Dict[str, Any]:
        """
        获取告警统计信息

        Returns:
            告警统计数据
        """
        try:
            total_sent = sum(stats["sent"] for stats in self.alert_stats.values())
            total_suppressed = sum(stats["suppressed"] for stats in self.alert_stats.values())
            total_escalated = sum(stats["escalated"] for stats in self.alert_stats.values())

            return {
                "total_alerts_sent": total_sent,
                "total_alerts_suppressed": total_suppressed,
                "total_alerts_escalated": total_escalated,
                "suppression_rate": total_suppressed / max(1, total_sent + total_suppressed) * 100,
                "escalation_rate": total_escalated / max(1, total_sent) * 100,
                "by_severity": self.alert_stats,
                "active_suppressions": len(self.suppressed_alerts),
                "generated_at": datetime.now(),
            }

        except Exception as e:
            logger.error("获取告警统计失败: %(e)s")
            return {"error": str(e)}

    def clear_expired_suppressions(self):
        """清除过期的告警抑制"""
        try:
            now = datetime.now()
            expired_keys = [key for key, expiry in self.suppressed_alerts.items() if now > expiry]

            for key in expired_keys:
                del self.suppressed_alerts[key]

            if expired_keys:
                logger.info("清除 {len(expired_keys)} 个过期的告警抑制")

        except Exception:
            logger.error("清除过期抑制失败: %(e)s")

    def reset_alert_statistics(self):
        """重置告警统计"""
        try:
            self.alert_stats = {
                "info": {"sent": 0, "suppressed": 0, "escalated": 0},
                "warning": {"sent": 0, "suppressed": 0, "escalated": 0},
                "critical": {"sent": 0, "suppressed": 0, "escalated": 0},
            }
            self.alert_escalation_count.clear()
            logger.info("告警统计已重置")

        except Exception:
            logger.error("重置告警统计失败: %(e)s")

    # 私有方法

    def _generate_alert_key(self, alert_type: str, symbol: Optional[str], portfolio_id: Optional[str]) -> str:
        """生成告警唯一键"""
        target = symbol or f"portfolio_{portfolio_id}" or "system"
        return f"{alert_type}_{target}"

    def _is_alert_suppressed(self, alert_key: str) -> bool:
        """检查告警是否被抑制"""
        if alert_key in self.suppressed_alerts:
            if datetime.now() < self.suppressed_alerts[alert_key]:
                return True
            else:
                # 抑制已过期，删除
                del self.suppressed_alerts[alert_key]
        return False

    def _check_alert_escalation(self, alert_key: str, current_severity: str) -> str:
        """检查告警是否需要升级"""
        # 增加计数
        self.alert_escalation_count[alert_key] += 1

        # 如果达到升级阈值
        if self.alert_escalation_count[alert_key] >= self.escalation_threshold:
            escalation_map = {
                "info": "warning",
                "warning": "critical",
            }
            new_severity = escalation_map.get(current_severity, current_severity)
            if new_severity != current_severity:
                # 重置计数
                self.alert_escalation_count[alert_key] = 0
                return new_severity

        return current_severity

    def _aggregate_similar_alerts(
        self, alert_type: str, severity: str, symbol: Optional[str], portfolio_id: Optional[str]
    ) -> Dict[str, Any]:
        """聚合相同类型的告警"""
        alert_key = self._generate_alert_key(alert_type, symbol, portfolio_id)

        # 获取最近的类似告警
        recent_alerts = [
            alert
            for alert in self.alert_history[alert_key]
            if (datetime.now() - alert["timestamp"]).total_seconds() < 300  # 5分钟内
        ]

        return {
            "count": len(recent_alerts) + 1,
            "recent_alerts": recent_alerts,
        }

    def _build_risk_alert_message(
        self,
        alert_type: str,
        severity: str,
        symbol: Optional[str],
        portfolio_id: Optional[str],
        message: str,
        metrics: Optional[Dict[str, Any]],
        aggregated: Dict[str, Any],
    ) -> str:
        """构建风险告警消息"""
        target = symbol or f"组合{portfolio_id}" or "系统"

        # 严重程度emoji
        severity_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨",
        }.get(severity, "🔔")

        # 告警类型描述
        alert_descriptions = {
            "var_exceeded": "VaR超限",
            "concentration_high": "集中度过高",
            "volatility_spike": "波动率激增",
            "portfolio_risk": "组合风险",
            "stock_risk": "个股风险",
        }

        alert_desc = alert_descriptions.get(alert_type, alert_type)

        # 构建基础消息
        full_message = f"{severity_emoji} [{alert_desc}] {target}\n"

        if message:
            full_message += f"{message}\n"

        # 添加聚合信息
        if aggregated["count"] > 1:
            full_message += f"📊 聚合告警: 过去5分钟内已发生 {aggregated['count']} 次类似告警\n"

        # 添加关键指标
        if metrics:
            full_message += "\n📈 关键指标:\n"
            key_metrics = self._extract_key_metrics(metrics)
            for metric_name, value in key_metrics.items():
                full_message += f"  • {metric_name}: {value}\n"

        # 添加时间戳
        full_message += f"\n⏰ 告警时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return full_message

    async def _send_risk_notification(
        self,
        alert_type: str,
        severity: str,
        symbol: Optional[str],
        portfolio_id: Optional[str],
        message: str,
        metrics: Optional[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
    ) -> bool:
        """发送风险通知"""
        try:
            # 映射严重程度到通知级别
            self._map_severity_to_notification_level(severity)

            # 构建通知标题
            self._build_alert_title(alert_type, severity, symbol, portfolio_id)

            # 构建扩展上下文
            extended_context = {
                "alert_type": alert_type,
                "severity": severity,
                "metrics": metrics or {},
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
            }

            # 使用父类的信号通知方法
            return await self.send_signal_notification(
                strategy_name="Risk Management System",
                symbol=symbol or "SYSTEM",
                signal=severity.upper(),
                price=0.0,
                context=extended_context,
                signal_id=f"risk_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )

        except Exception:
            logger.error("发送风险通知失败: %(e)s")
            return False

    def _update_alert_history(self, alert_key: str, severity: str, alert_type: str):
        """更新告警历史"""
        alert_record = {
            "severity": severity,
            "alert_type": alert_type,
            "timestamp": datetime.now(),
        }

        self.alert_history[alert_key].append(alert_record)

        # 只保留最近100条记录
        if len(self.alert_history[alert_key]) > 100:
            self.alert_history[alert_key] = self.alert_history[alert_key][-100:]

    def _map_risk_level_to_severity(self, risk_level: str) -> str:
        """映射风险等级到告警严重程度"""
        mapping = {
            "safe": "info",
            "low": "info",
            "attention": "warning",
            "medium": "warning",
            "warning": "warning",
            "high": "critical",
            "danger": "critical",
            "critical": "critical",
        }
        return mapping.get(risk_level, "warning")

    def _map_severity_to_notification_level(self, severity: str) -> NotificationLevel:
        """映射告警严重程度到通知级别"""
        mapping = {
            "info": NotificationLevel.INFO,
            "warning": NotificationLevel.WARNING,
            "critical": NotificationLevel.ERROR,
        }
        return mapping.get(severity, NotificationLevel.INFO)

    def _build_portfolio_alert_message(
        self, portfolio_id: str, risk_level: str, risk_metrics: Dict[str, Any], triggered_alerts: List[Dict[str, Any]]
    ) -> str:
        """构建组合告警消息"""
        risk_descriptions = {
            "safe": "风险可控",
            "attention": "需要关注",
            "warning": "风险较高",
            "danger": "风险极高",
        }

        risk_desc = risk_descriptions.get(risk_level, risk_level)

        message = f"组合 {portfolio_id} {risk_desc}\n"
        message += f"触发告警: {len(triggered_alerts)} 个\n"

        # 添加关键指标
        if "var_1d_95" in risk_metrics:
            message += f"VaR(95%): {risk_metrics['var_1d_95']:.2%}\n"
        if "hhi" in risk_metrics:
            message += f"集中度(HHI): {risk_metrics['hhi']:.3f}\n"

        return message

    def _build_stock_alert_message(
        self, symbol: str, risk_level: str, risk_metrics: Dict[str, Any], alert_triggers: List[str]
    ) -> str:
        """构建个股告警消息"""
        message = f"股票 {symbol} 风险等级: {risk_level}\n"
        message += f"触发原因: {', '.join(alert_triggers)}\n"

        # 添加关键指标
        if "volatility_20d" in risk_metrics:
            message += f"波动率: {risk_metrics['volatility_20d']:.2%}\n"

        return message

    def _build_alert_title(
        self, alert_type: str, severity: str, symbol: Optional[str], portfolio_id: Optional[str]
    ) -> str:
        """构建告警标题"""
        severity_prefix = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨",
        }.get(severity, "🔔")

        target = symbol or f"组合{portfolio_id}" or "系统"

        alert_titles = {
            "portfolio_risk": f"{severity_prefix} 组合风险告警",
            "stock_risk": f"{severity_prefix} 个股风险告警",
            "var_exceeded": f"{severity_prefix} VaR超限告警",
            "concentration_high": f"{severity_prefix} 集中度告警",
        }

        title = alert_titles.get(alert_type, f"{severity_prefix} 风险告警")
        return f"{title} - {target}"

    def _extract_key_metrics(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """提取关键指标用于显示"""
        key_metrics = {}

        # 波动率相关
        if "volatility_20d" in metrics:
            key_metrics["波动率(20日)"] = f"{metrics['volatility_20d']:.2%}"
        if "atr_14" in metrics:
            key_metrics["ATR(14)"] = f"{metrics['atr_14']:.2f}"

        # 风险指标
        if "var_1d_95" in metrics:
            key_metrics["VaR(95%,1日)"] = f"{metrics['var_1d_95']:.2%}"
        if "risk_score" in metrics:
            key_metrics["风险评分"] = f"{metrics['risk_score']}"

        # 集中度
        if "hhi" in metrics:
            key_metrics["HHI指数"] = f"{metrics['hhi']:.3f}"
        if "top10_ratio" in metrics:
            key_metrics["前十大占比"] = f"{metrics['top10_ratio']:.1%}"

        # 流动性
        if "liquidity_score" in metrics:
            key_metrics["流动性评分"] = f"{metrics['liquidity_score']}"

        return key_metrics


# 创建全局实例
_risk_alert_notification_manager: Optional[RiskAlertNotificationManager] = None


def get_risk_alert_notification_manager(config: Optional[NotificationConfig] = None) -> RiskAlertNotificationManager:
    """获取风险告警通知管理器实例（单例模式）"""
    global _risk_alert_notification_manager
    if _risk_alert_notification_manager is None:
        _risk_alert_notification_manager = RiskAlertNotificationManager(config)
    return _risk_alert_notification_manager
