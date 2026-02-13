"""
风险管理监控模块

提供实时风险监控、阈值检查、事件记录和指标统计功能
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .risk_base import RiskLevel, RiskEventType, RiskMetrics

logger = __import__("logging").getLogger(__name__)


@dataclass
class MonitoringThreshold:
    """监控阈值配置"""

    var_95_threshold: float = 2.5e-4
    var_99_threshold: float = 4.0e-4
    sharpe_threshold: float = 1.0
    max_drawdown_threshold: float = 0.15
    volatility_threshold: float = 0.30
    position_size_limit: float = 1000000.0
    stop_loss_threshold: float = -0.10


@dataclass
class MonitoringEvent:
    """监控事件记录"""

    event_id: str
    event_type: RiskEventType
    risk_level: RiskLevel
    timestamp: datetime
    portfolio_id: Optional[str]
    stock_code: Optional[str]
    message: str
    metrics_snapshot: Optional[Dict]
    is_alert: bool = False
    is_resolved: bool = False
    notification_sent: bool = False


@dataclass
class MonitoringStatistics:
    """监控统计数据"""

    total_events: int = 0
    alert_events: int = 0
    resolved_events: int = 0
    unresolved_events: int = 0
    last_24h_events: int = 0
    last_7d_events: int = 0
    last_event_timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "total_events": self.total_events,
            "alert_events": self.alert_events,
            "resolved_events": self.resolved_events,
            "unresolved_events": self.unresolved_events,
            "last_24h_events": self.last_24h_events,
            "last_7d_events": self.last_7d_events,
            "last_event_timestamp": self.last_event_timestamp.isoformat() if self.last_event_timestamp else None,
        }


class RiskMonitoring:
    """风险管理监控器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.thresholds = MonitoringThreshold()
        self.event_history: List[MonitoringEvent] = []
        self.statistics = MonitoringStatistics()
        self.is_monitoring = False
        self.last_check_time = None

        logger.info("风险管理监控模块初始化")

    async def check_thresholds(self, portfolio_id: str, current_metrics: RiskMetrics) -> List[MonitoringEvent]:
        """
        检查风险阈值是否被突破

        Args:
            portfolio_id: 投资组合ID
            current_metrics: 当前风险指标

        Returns:
            List[MonitoringEvent]: 触发的事件列表
        """
        events = []

        try:
            if current_metrics.var_95 > self.thresholds.var_95_threshold:
                event = MonitoringEvent(
                    event_id=f"var_95_{datetime.now().isoformat()}",
                    event_type=RiskEventType.THRESHOLD_BREACH,
                    risk_level=RiskLevel.HIGH,
                    timestamp=datetime.now(),
                    portfolio_id=portfolio_id,
                    message=f"方差{current_metrics.var_95:.6f}超过阈值{self.thresholds.var_95_threshold:.6f}",
                    metrics_snapshot=current_metrics.to_dict(),
                    is_alert=True,
                )
                events.append(event)
                self.logger.warning(f"触发高方差告警: {event.message}")

            if current_metrics.var_99 > self.thresholds.var_99_threshold:
                event = MonitoringEvent(
                    event_id=f"var_99_{datetime.now().isoformat()}",
                    event_type=RiskEventType.THRESHOLD_BREACH,
                    risk_level=RiskLevel.CRITICAL,
                    timestamp=datetime.now(),
                    portfolio_id=portfolio_id,
                    message=f"方差{current_metrics.var_99:.6f}超过阈值{self.thresholds.var_99_threshold:.6f}",
                    metrics_snapshot=current_metrics.to_dict(),
                    is_alert=True,
                )
                events.append(event)
                self.logger.error(f"触发临界方差告警: {event.message}")

            if abs(current_metrics.max_drawdown) > self.thresholds.max_drawdown_threshold:
                event = MonitoringEvent(
                    event_id=f"drawdown_{datetime.now().isoformat()}",
                    event_type=RiskEventType.THRESHOLD_BREACH,
                    risk_level=RiskLevel.CRITICAL,
                    timestamp=datetime.now(),
                    portfolio_id=portfolio_id,
                    message=f"最大回撤{current_metrics.max_drawdown:.2%}超过阈值{self.thresholds.max_drawdown_threshold:.2%}",
                    metrics_snapshot=current_metrics.to_dict(),
                    is_alert=True,
                )
                events.append(event)
                self.logger.error(f"触发回撤告警: {event.message}")

            if current_metrics.sharpe_ratio < self.thresholds.sharpe_threshold:
                event = MonitoringEvent(
                    event_id=f"sharpe_{datetime.now().isoformat()}",
                    event_type=RiskEventType.THRESHOLD_BREACH,
                    risk_level=RiskLevel.MEDIUM,
                    timestamp=datetime.now(),
                    portfolio_id=portfolio_id,
                    message=f"夏普比率{current_metrics.sharpe_ratio:.3f}低于阈值{self.thresholds.sharpe_threshold:.3f}",
                    metrics_snapshot=current_metrics.to_dict(),
                    is_alert=True,
                )
                events.append(event)
                self.logger.warning(f"触发夏普比率告警: {event.message}")

            if current_metrics.volatility > self.thresholds.volatility_threshold:
                event = MonitoringEvent(
                    event_id=f"volatility_{datetime.now().isoformat()}",
                    event_type=RiskEventType.THRESHOLD_BREACH,
                    risk_level=RiskLevel.HIGH,
                    timestamp=datetime.now(),
                    portfolio_id=portfolio_id,
                    message=f"波动率{current_metrics.volatility:.3f}超过阈值{self.thresholds.volatility_threshold:.3f}",
                    metrics_snapshot=current_metrics.to_dict(),
                    is_alert=True,
                )
                events.append(event)
                self.logger.warning(f"触发波动率告警: {event.message}")

            for event in events:
                self.event_history.append(event)
                self.statistics.total_events += 1
                if event.is_alert:
                    self.statistics.alert_events += 1
                self.statistics.last_event_timestamp = event.timestamp

        except Exception as e:
            self.logger.error(f"检查阈值失败: {e}")

        return events

    async def record_event(self, event: MonitoringEvent, notify: bool = False) -> None:
        """
        记录风险事件

        Args:
            event: 监控事件
            notify: 是否发送通知
        """
        try:
            event.timestamp = datetime.now()
            self.event_history.append(event)
            self.statistics.total_events += 1

            if event.is_alert:
                self.statistics.alert_events += 1

            self.logger.info(f"记录风险事件: {event.event_type.value} - {event.message}")

            if notify:
                await self._send_alert_notification(event)

        except Exception as e:
            self.logger.error(f"记录事件失败: {e}")

    async def _send_alert_notification(self, event: MonitoringEvent):
        """
        发送告警通知（邮件、Webhook、短信等）
        """
        try:
            if event.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                await self._send_email_alert(event)
                await self._send_webhook_alert(event)

            self.logger.info(f"告警通知已发送: {event.event_id}")

        except Exception as e:
            self.logger.error(f"发送告警通知失败: {e}")

    async def _send_email_alert(self, event: MonitoringEvent):
        """发送邮件告警"""
        try:

            subject = f"[{event.risk_level.value}] 风险告警 - {event.event_id}"
            body = f"""
            风险事件: {event.message}
            
            时间: {event.timestamp}
            风险等级: {event.risk_level.value}
            组合ID: {event.portfolio_id if event.portfolio_id else "N/A"}
            股票代码: {event.stock_code if event.stock_code else "N/A"}
            
            当前指标:
            {event.metrics_snapshot}
            """

            await self._send_email(subject, body)

            self.logger.info(f"邮件告警已发送: {event.event_id}")

        except Exception as e:
            self.logger.error(f"发送邮件告警失败: {e}")

    async def _send_webhook_alert(self, event: MonitoringEvent):
        """发送Webhook告警"""
        try:
            import httpx

            webhook_url = self.get_webhook_url(event.risk_level)

            payload = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "risk_level": event.risk_level.value,
                "message": event.message,
                "timestamp": event.timestamp.isoformat(),
                "portfolio_id": event.portfolio_id if event.portfolio_id else None,
                "stock_code": event.stock_code if event.stock_code else None,
                "metrics": event.metrics_snapshot,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload, timeout=10)

            if response.status_code == 200:
                self.logger.info(f"Webhook告警已发送: {event.event_id}")
            else:
                self.logger.error(f"Webhook告警发送失败: {response.status_code}")

        except Exception as e:
            self.logger.error(f"发送Webhook告警失败: {e}")

    def get_webhook_url(self, risk_level: RiskLevel) -> str:
        """获取Webhook URL"""
        webhook_urls = {
            RiskLevel.LOW: "https://api.example.com/webhook/low",
            RiskLevel.MEDIUM: "https://api.example.com/webhook/medium",
            RiskLevel.HIGH: "https://api.example.com/webhook/high",
            RiskLevel.CRITICAL: "https://api.example.com/webhook/critical",
        }

        return webhook_urls.get(risk_level, "")

    async def send_sms_alert(self, event: MonitoringEvent, phone_numbers: List[str]) -> None:
        """发送短信告警"""
        try:
            import aiohttp

            sms_api_url = self.get_sms_api_url()

            for phone in phone_numbers:
                payload = {"to": phone, "message": f"风险告警: {event.message}", "event_id": event.event_id}

                async with aiohttp.Client() as client:
                    response = await client.post(sms_api_url, json=payload, timeout=10)

                    if response.status_code != 200:
                        self.logger.error(f"短信发送失败: {phone}: {response.status_code}")

            self.logger.info(f"短信告警已发送: {len(phone_numbers)}条")

        except Exception as e:
            self.logger.error(f"发送短信告警失败: {e}")

    def get_sms_api_url(self) -> str:
        """获取短信API URL"""
        import os

        return os.getenv("SMS_API_URL", "")

    async def _send_email(self, subject: str, body: str):
        """发送邮件（内部方法）"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import os

            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME", "")
            smtp_password = os.getenv("SMTP_PASSWORD", "")

            msg = MIMEMultipart()
            msg["From"] = smtp_username
            msg["To"] = os.getenv("ALERT_EMAIL", "")
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()

            self.logger.info(f"邮件已发送: {subject}")

        except Exception as e:
            self.logger.error(f"发送邮件失败: {e}")

    def get_statistics(self) -> Dict:
        """获取监控统计数据"""
        try:
            now = datetime.now()

            last_24h_events = [event for event in self.event_history if (now - event.timestamp) <= timedelta(days=1)]

            self.statistics.last_24h_events = len(last_24h_events)

            last_7d_events = [event for event in self.event_history if (now - event.timestamp) <= timedelta(days=7)]

            self.statistics.last_7d_events = len(last_7d_events)

            alert_events = [event for event in self.event_history if event.is_alert]

            self.statistics.alert_events = len(alert_events)
            self.statistics.unresolved_events = [event for event in self.event_history if not event.is_resolved]

            self.statistics.unresolved_events = len(self.statistics.unresolved_events)

            self.statistics.last_event_timestamp = max([event.timestamp for event in self.event_history], default=None)

            self.logger.info(f"监控统计已更新: 总事件{self.statistics.total_events}条")

        except Exception as e:
            self.logger.error(f"获取统计失败: {e}")

        return self.statistics.to_dict()

    async def start_monitoring(self, portfolio_ids: List[str]) -> None:
        """
        开始监控指定投资组合

        Args:
            portfolio_ids: 投资组合ID列表
        """
        try:
            self.is_monitoring = True
            self.last_check_time = datetime.now()

            self.logger.info(f"开始监控{len(portfolio_ids)}个投资组合")

            for portfolio_id in portfolio_ids:
                await self._check_portfolio_risk(portfolio_id)

        except Exception as e:
            self.logger.error(f"启动监控失败: {e}")

    async def _check_portfolio_risk(self, portfolio_id: str) -> None:
        """检查单个投资组合的风险"""
        try:
            from app.core.database import db_service

            sql = f"""
            SELECT 
                portfolio_id,
                total_value,
                cash_balance,
                position_count
                last_risk_check
            FROM risk_profiles
            WHERE portfolio_id = '{portfolio_id}'
            """

            result = await db_service.fetch_one(sql)

            if result:
                portfolio_value = result["total_value"]
                cash_balance = result["cash_balance"]
                position_count = result["position_count"]

                if position_count > self.thresholds.position_size_limit:
                    event = MonitoringEvent(
                        event_id=f"position_size_{datetime.now().isoformat()}",
                        event_type=RiskEventType.THRESHOLD_BREACH,
                        risk_level=RiskLevel.MEDIUM,
                        timestamp=datetime.now(),
                        portfolio_id=portfolio_id,
                        message=f"持仓数量{position_count}超过阈值{self.thresholds.position_size_limit:.0f}",
                    )
                    await self.record_event(event, notify=True)

                self.logger.info(f"投资组合{portfolio_id}风险检查完成")

        except Exception as e:
            self.logger.error(f"检查投资组合风险失败: {e}")

    async def stop_monitoring(self) -> None:
        """停止监控"""
        self.is_monitoring = False
        self.logger.info("风险管理监控已停止")
