"""
Alert Notification System for MyStocks Monitoring

Multi-channel notification support:
- Email (SMTP)
- Slack
- SMS (Twilio)
- Webhooks
- PagerDuty

Features:
- Async notification delivery
- Retry logic with exponential backoff
- Template-based formatting
- Channel preference mapping
- Notification history tracking
"""

import asyncio
import logging
import smtplib
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import sqlite3

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Supported notification channels"""

    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"
    STDOUT = "stdout"  # For testing


class AlertSeverity(Enum):
    """Alert severity levels"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class NotificationConfig:
    """Configuration for a notification channel"""

    channel: NotificationChannel
    enabled: bool
    retry_count: int = 3
    retry_delay: int = 5  # seconds
    timeout: int = 30  # seconds
    config: Dict[str, Any] = None


def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class Alert:
    """Alert data structure"""

    alertname: str
    severity: str
    service: str
    category: str
    instance: str
    summary: str
    description: str
    timestamp: str
    labels: Dict[str, str]
    annotations: Dict[str, str]


@dataclass
class NotificationResult:
    """Result of notification delivery attempt"""

    channel: NotificationChannel
    alert_id: str
    success: bool
    timestamp: datetime
    message: str
    retry_count: int = 0
    delivery_time_ms: float = 0


class NotificationProvider(ABC):
    """Abstract base class for notification providers"""


def __init__(self, config: NotificationConfig):
        self.config = config
        self.retry_count = config.retry_count
        self.retry_delay = config.retry_delay
        self.timeout = config.timeout

    @abstractmethod
async def send(self, recipients: List[str], subject: str, body: str, alert: Alert, **kwargs) -> NotificationResult:
        """Send notification via this channel"""
        pass

async def send_with_retry(
        self, recipients: List[str], subject: str, body: str, alert: Alert, **kwargs
    ) -> NotificationResult:
        """Send with automatic retry logic"""
        for attempt in range(self.retry_count):
            try:
                result = await asyncio.wait_for(
                    self.send(recipients, subject, body, alert, **kwargs),
                    timeout=self.timeout,
                )
                result.retry_count = attempt
                return result
            except asyncio.TimeoutError:
                logger.warning(
                    "Timeout sending via {self.config.channel.value} " f"(attempt {attempt + 1}/{self.retry_count})"
                )
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(self.retry_delay * (2**attempt))
            except Exception as e:
                logger.error("Error sending via %s: %s", self.config.channel.value, e)
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(self.retry_delay * (2**attempt))

        return NotificationResult(
            channel=self.config.channel,
            alert_id=alert.alertname,
            success=False,
            timestamp=datetime.now(),
            message=f"Failed after {self.retry_count} attempts",
            retry_count=self.retry_count,
        )


class EmailNotificationProvider(NotificationProvider):
    """Email notification via SMTP"""

async def send(self, recipients: List[str], subject: str, body: str, alert: Alert, **kwargs) -> NotificationResult:
        """Send email notification"""
        start_time = datetime.now()

        try:
            # Get SMTP configuration from environment
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER", "")
            smtp_password = os.getenv("SMTP_PASSWORD", "")
            from_addr = os.getenv("SMTP_FROM", smtp_user)

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{alert.severity.upper()}] {subject}"
            msg["From"] = from_addr
            msg["To"] = ", ".join(recipients)

            # Format HTML body
            html_body = self._format_html_email(alert, body)

            # Attach parts
            msg.attach(MIMEText(body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Send via SMTP
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

            delivery_time = (datetime.now() - start_time).total_seconds() * 1000

            logger.info("✅ Email sent to %s recipients (%sms)", len(recipients), delivery_time)

            return NotificationResult(
                channel=NotificationChannel.EMAIL,
                alert_id=alert.alertname,
                success=True,
                timestamp=datetime.now(),
                message=f"Sent to {', '.join(recipients)}",
                delivery_time_ms=delivery_time,
            )

        except Exception as e:
            logger.error("❌ Email delivery failed: %s", e)
            raise

def _format_html_email(self, alert: Alert, body: str) -> str:
        """Format HTML email body"""
        severity_colors = {
            "critical": "#FF0000",
            "warning": "#FFA500",
            "info": "#0066CC",
        }
        color = severity_colors.get(alert.severity, "#000000")

        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="border-left: 5px solid {color}; padding: 10px; background: #f5f5f5;">
                    <h2 style="color: {color}; margin: 0;">
                        [{alert.severity.upper()}] {alert.alertname}
                    </h2>
                    <p><strong>Service:</strong> {alert.service}</p>
                    <p><strong>Category:</strong> {alert.category}</p>
                    <p><strong>Instance:</strong> {alert.instance}</p>
                    <p><strong>Time:</strong> {alert.timestamp}</p>
                    <hr>
                    <p><strong>Summary:</strong></p>
                    <p>{alert.summary}</p>
                    <p><strong>Description:</strong></p>
                    <pre style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
{alert.description}
                    </pre>
                </div>
            </body>
        </html>
        """


class SlackNotificationProvider(NotificationProvider):
    """Slack notification via Webhooks"""

async def send(self, recipients: List[str], subject: str, body: str, alert: Alert, **kwargs) -> NotificationResult:
        """Send Slack notification"""
        start_time = datetime.now()

        try:
            webhook_urls = recipients  # Slack channels are passed as webhook URLs
            slack_webhook = webhook_urls[0] if webhook_urls else os.getenv("SLACK_WEBHOOK_URL")

            if not slack_webhook:
                raise ValueError("Slack webhook URL not configured")

            # Format Slack message
            color = self._get_severity_color(alert.severity)
            message = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"🚨 {alert.alertname}",
                        "title_link": kwargs.get("dashboard_url", ""),
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity.upper(),
                                "short": True,
                            },
                            {"title": "Service", "value": alert.service, "short": True},
                            {
                                "title": "Category",
                                "value": alert.category,
                                "short": True,
                            },
                            {
                                "title": "Instance",
                                "value": alert.instance,
                                "short": True,
                            },
                            {
                                "title": "Summary",
                                "value": alert.summary,
                                "short": False,
                            },
                            {
                                "title": "Description",
                                "value": alert.description,
                                "short": False,
                            },
                            {"title": "Time", "value": alert.timestamp, "short": True},
                        ],
                        "footer": "MyStocks Monitoring",
                        "ts": int(datetime.now().timestamp()),
                    }
                ]
            }

            # Send to each webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    slack_webhook,
                    json=message,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status == 200:
                        delivery_time = (datetime.now() - start_time).total_seconds() * 1000
                        logger.info("✅ Slack notification sent (%sms)", delivery_time)
                        return NotificationResult(
                            channel=NotificationChannel.SLACK,
                            alert_id=alert.alertname,
                            success=True,
                            timestamp=datetime.now(),
                            message="Slack notification delivered",
                            delivery_time_ms=delivery_time,
                        )
                    else:
                        raise Exception(f"Slack API returned {response.status}")

        except Exception as e:
            logger.error("❌ Slack delivery failed: %s", e)
            raise

def _get_severity_color(self, severity: str) -> str:
        """Get Slack color for severity level"""
        colors = {
            "critical": "#FF0000",  # Red
            "warning": "#FFA500",  # Orange
            "info": "#0066CC",  # Blue
        }
        return colors.get(severity, "#808080")


class SMSNotificationProvider(NotificationProvider):
    """SMS notification via Twilio"""

async def send(self, recipients: List[str], subject: str, body: str, alert: Alert, **kwargs) -> NotificationResult:
        """Send SMS notification"""
        start_time = datetime.now()

        try:
            # Get Twilio configuration
            account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
            from_number = os.getenv("TWILIO_PHONE_NUMBER", "")

            if not all([account_sid, auth_token, from_number]):
                raise ValueError("Twilio credentials not configured")

            # Create SMS message (keep it short!)
            sms_body = f"[{alert.severity.upper()}] {alert.alertname}: {alert.summary[:80]}"

            # Send to each recipient
            sent_count = 0
            async with aiohttp.ClientSession() as session:
                for phone_number in recipients:
                    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

                    auth = aiohttp.BasicAuth(account_sid, auth_token)
                    data = {"From": from_number, "To": phone_number, "Body": sms_body}

                    async with session.post(
                        url,
                        data=data,
                        auth=auth,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ) as response:
                        if response.status == 201:
                            sent_count += 1
                        else:
                            logger.warning("Failed to send SMS to %s: %s", phone_number, response.status)

            delivery_time = (datetime.now() - start_time).total_seconds() * 1000

            if sent_count > 0:
                logger.info(f"✅ SMS sent to {sent_count}/{len(recipients)} recipients ({delivery_time:.0f}ms)")
                return NotificationResult(
                    channel=NotificationChannel.SMS,
                    alert_id=alert.alertname,
                    success=True,
                    timestamp=datetime.now(),
                    message=f"SMS sent to {sent_count}/{len(recipients)} numbers",
                    delivery_time_ms=delivery_time,
                )
            else:
                raise Exception("Failed to send SMS to any recipient")

        except Exception as e:
            logger.error("❌ SMS delivery failed: %s", e)
            raise


class WebhookNotificationProvider(NotificationProvider):
    """Generic webhook notification"""

async def send(self, recipients: List[str], subject: str, body: str, alert: Alert, **kwargs) -> NotificationResult:
        """Send webhook notification"""
        start_time = datetime.now()

        try:
            webhook_urls = recipients

            # Format webhook payload
            payload = {
                "alert": asdict(alert),
                "subject": subject,
                "body": body,
                "timestamp": datetime.now().isoformat(),
                "custom_fields": kwargs,
            }

            # Send to each webhook
            sent_count = 0
            async with aiohttp.ClientSession() as session:
                for url in webhook_urls:
                    try:
                        async with session.post(
                            url,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=self.timeout),
                        ) as response:
                            if 200 <= response.status < 300:
                                sent_count += 1
                            else:
                                logger.warning("Webhook returned %s: %s", response.status, url)
                    except Exception as e:
                        logger.warning("Webhook failed (%s): %s", url, e)

            delivery_time = (datetime.now() - start_time).total_seconds() * 1000

            if sent_count > 0:
                logger.info(f"✅ Webhook sent to {sent_count}/{len(webhook_urls)} endpoints ({delivery_time:.0f}ms)")
                return NotificationResult(
                    channel=NotificationChannel.WEBHOOK,
                    alert_id=alert.alertname,
                    success=True,
                    timestamp=datetime.now(),
                    message=f"Webhook delivered to {sent_count}/{len(webhook_urls)} endpoints",
                    delivery_time_ms=delivery_time,
                )
            else:
                raise Exception("Failed to send to any webhook")

        except Exception as e:
            logger.error("❌ Webhook delivery failed: %s", e)
            raise


class AlertNotificationManager:
    """
    Central notification manager for MyStocks alerts
    Coordinates multi-channel delivery with retry logic
    """

def __init__(self, config_file: Optional[str] = None):
        self.providers: Dict[NotificationChannel, NotificationProvider] = {}
        self.notification_history_db = "notification_history.db"
        self.channel_mapping = self._load_channel_mapping()
        self._init_database()
        self._init_providers()

def _load_channel_mapping(self) -> Dict[str, List[NotificationChannel]]:
        """Load severity/category to channel mapping"""
        return {
            "critical_infrastructure": [
                NotificationChannel.PAGERDUTY,
                NotificationChannel.SMS,
                NotificationChannel.SLACK,
            ],
            "critical_other": [NotificationChannel.SLACK, NotificationChannel.EMAIL],
            "warning": [NotificationChannel.SLACK, NotificationChannel.EMAIL],
            "info": [NotificationChannel.SLACK],
        }

def _init_database(self):
        """Initialize notification history database"""
        conn = sqlite3.connect(self.notification_history_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_name TEXT,
                channel TEXT,
                recipients TEXT,
                success BOOLEAN,
                timestamp DATETIME,
                delivery_time_ms REAL,
                message TEXT,
                retry_count INTEGER
            )
        """
        )

        conn.commit()
        conn.close()

def _init_providers(self):
        """Initialize notification providers"""
        # Email
        self.providers[NotificationChannel.EMAIL] = EmailNotificationProvider(
            NotificationConfig(
                channel=NotificationChannel.EMAIL,
                enabled=bool(os.getenv("SMTP_HOST")),
                retry_count=3,
            )
        )

        # Slack
        self.providers[NotificationChannel.SLACK] = SlackNotificationProvider(
            NotificationConfig(
                channel=NotificationChannel.SLACK,
                enabled=bool(os.getenv("SLACK_WEBHOOK_URL")),
                retry_count=2,
            )
        )

        # SMS
        self.providers[NotificationChannel.SMS] = SMSNotificationProvider(
            NotificationConfig(
                channel=NotificationChannel.SMS,
                enabled=bool(os.getenv("TWILIO_ACCOUNT_SID")),
                retry_count=3,
            )
        )

        # Webhook
        self.providers[NotificationChannel.WEBHOOK] = WebhookNotificationProvider(
            NotificationConfig(channel=NotificationChannel.WEBHOOK, enabled=True, retry_count=2)
        )

        logger.info("✅ Initialized %s notification providers", len(self.providers))

async def send_alert(
        self, alert: Alert, recipients_map: Dict[NotificationChannel, List[str]]
    ) -> List[NotificationResult]:
        """
        Send alert via multiple channels to specified recipients
        """
        logger.info("📨 Sending alert: %s via %s channels", alert.alertname, len(recipients_map))

        tasks = []
        for channel, recipients in recipients_map.items():
            if channel not in self.providers:
                logger.warning("⚠️  Channel %s not configured", channel)
                continue

            provider = self.providers[channel]
            if not provider.config.enabled:
                logger.debug("⏭️  Skipping disabled channel: %s", channel)
                continue

            # Create notification task
            task = provider.send_with_retry(
                recipients=recipients,
                subject=alert.alertname,
                body=alert.description,
                alert=alert,
                dashboard_url=self._get_dashboard_url(alert),
            )
            tasks.append(task)

        # Execute all notifications concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        notification_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error("❌ Notification failed: %s", result)
            else:
                notification_results.append(result)
                self._save_notification_history(alert, result)

        return notification_results

async def send_to_on_call(self, alert: Alert) -> List[NotificationResult]:
        """Send critical alert to on-call engineer"""
        # In production, would fetch from on-call schedule service
        on_call_email = os.getenv("ON_CALL_EMAIL", "oncall@mystocks.com")
        on_call_phone = os.getenv("ON_CALL_PHONE", "+1234567890")

        recipients_map = {
            NotificationChannel.SMS: [on_call_phone],
            NotificationChannel.EMAIL: [on_call_email],
            NotificationChannel.SLACK: [os.getenv("SLACK_WEBHOOK_URL", "")],
        }

        return await self.send_alert(alert, recipients_map)

def _get_dashboard_url(self, alert: Alert) -> str:
        """Generate dashboard URL for alert context"""
        base_url = os.getenv("GRAFANA_URL", "http://localhost:3000")
        return f"{base_url}/d/mystocks-monitoring?" f"var-service={alert.service}&" f"var-severity={alert.severity}"

def _save_notification_history(self, alert: Alert, result: NotificationResult):
        """Save notification delivery record"""
        try:
            conn = sqlite3.connect(self.notification_history_db)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO notification_history
                (alert_name, channel, recipients, success, timestamp, delivery_time_ms, message, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    alert.alertname,
                    result.channel.value,
                    "",  # Recipients would be joined from original request
                    result.success,
                    result.timestamp,
                    result.delivery_time_ms,
                    result.message,
                    result.retry_count,
                ),
            )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Failed to save notification history: %s", e)

def get_notification_history(self, alert_name: Optional[str] = None, days: int = 7) -> List[Dict]:
        """Retrieve notification history"""
        try:
            conn = sqlite3.connect(self.notification_history_db)
            cursor = conn.cursor()

            cutoff_date = datetime.now() - timedelta(days=days)

            if alert_name:
                cursor.execute(
                    """
                    SELECT * FROM notification_history
                    WHERE alert_name = ? AND timestamp > ?
                    ORDER BY timestamp DESC
                """,
                    (alert_name, cutoff_date),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM notification_history
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                """,
                    (cutoff_date,),
                )

            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            conn.close()
            return results
        except Exception as e:
            logger.error("Failed to retrieve notification history: %s", e)
            return []


# Global instance
_notification_manager: Optional[AlertNotificationManager] = None


def get_notification_manager() -> AlertNotificationManager:
    """Get or create global notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = AlertNotificationManager()
    return _notification_manager


async def send_test_notification(channel: NotificationChannel):
    """Send test notification to verify channel configuration"""
    manager = get_notification_manager()

    test_alert = Alert(
        alertname="TestAlert",
        severity="info",
        service="monitoring",
        category="testing",
        instance="test-instance",
        summary="This is a test notification",
        description="If you received this, the notification channel is working correctly!",
        timestamp=datetime.now().isoformat(),
        labels={},
        annotations={},
    )

    recipients_map = {channel: [os.getenv(f"{channel.name}_RECIPIENT", "")]}

    results = await manager.send_alert(test_alert, recipients_map)
    return results


if __name__ == "__main__":
    # Test notification sending
    logging.basicConfig(level=logging.INFO)

async def test():
        manager = get_notification_manager()

        test_alert = Alert(
            alertname="HighAPIResponseTime",
            severity="warning",
            service="api",
            category="performance",
            instance="api-prod-1",
            summary="API response time is high",
            description="The API p95 response time has exceeded 1 second for the past 5 minutes.",
            timestamp=datetime.now().isoformat(),
            labels={"method": "POST", "endpoint": "/api/market/realtime"},
            annotations={},
        )

        # Send to Slack and email
        recipients_map = {
            NotificationChannel.SLACK: [os.getenv("SLACK_WEBHOOK_URL", "")],
            NotificationChannel.EMAIL: ["recipient@example.com"],
        }

        results = await manager.send_alert(test_alert, recipients_map)
        for result in results:
            print(f"✅ {result.channel.value}: {result.message}")

    asyncio.run(test())
