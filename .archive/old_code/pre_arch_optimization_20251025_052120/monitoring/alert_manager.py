"""
# 功能：告警管理模块，支持多渠道告警和告警升级策略
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from monitoring.monitoring_database import MonitoringDatabase, get_monitoring_database

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """告警级别"""

    CRITICAL = "CRITICAL"  # 严重: 需要立即处理
    WARNING = "WARNING"  # 警告: 需要关注
    INFO = "INFO"  # 信息: 仅通知


class AlertType(str, Enum):
    """告警类型"""

    SLOW_QUERY = "SLOW_QUERY"  # 慢查询
    DATA_QUALITY = "DATA_QUALITY"  # 数据质量问题
    SYSTEM_ERROR = "SYSTEM_ERROR"  # 系统错误
    CONNECTION_FAILURE = "CONNECTION_FAILURE"  # 连接失败
    DISK_SPACE = "DISK_SPACE"  # 磁盘空间
    MEMORY_USAGE = "MEMORY_USAGE"  # 内存使用
    CUSTOM = "CUSTOM"  # 自定义告警


class AlertManager:
    """
    告警管理器

    负责接收告警请求,通过配置的渠道发送告警通知,
    并记录到监控数据库。
    """

    def __init__(
        self,
        monitoring_db: Optional[MonitoringDatabase] = None,
        enabled_channels: Optional[List[str]] = None,
    ):
        """
        初始化告警管理器

        Args:
            monitoring_db: 监控数据库实例 (可选)
            enabled_channels: 启用的告警渠道 ['log', 'email', 'webhook']
        """
        self.monitoring_db = monitoring_db or get_monitoring_database()

        # 默认只启用日志渠道 (email和webhook需要额外配置)
        self.enabled_channels = enabled_channels or ["log"]

        # 告警发送统计
        self._total_alerts = 0
        self._sent_alerts = 0
        self._failed_alerts = 0

        # 告警聚合配置 (防止告警风暴)
        self._alert_cooldown = {}  # {alert_key: last_sent_time}
        self._cooldown_seconds = 300  # 5分钟冷却期

        logger.info(f"✅ AlertManager initialized (channels={self.enabled_channels})")

    def send_alert(
        self,
        alert_level: str,
        alert_type: str,
        alert_title: str,
        alert_message: str,
        source: Optional[str] = None,
        classification: Optional[str] = None,
        database_type: Optional[str] = None,
        table_name: Optional[str] = None,
        additional_data: Optional[Dict] = None,
        channels: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        发送告警

        Args:
            alert_level: 告警级别 (CRITICAL/WARNING/INFO)
            alert_type: 告警类型
            alert_title: 告警标题
            alert_message: 告警详细信息
            source: 告警来源 (模块名称)
            classification: 关联数据分类
            database_type: 关联数据库类型
            table_name: 关联表名
            additional_data: 额外数据
            channels: 指定通知渠道 (None则使用默认渠道)

        Returns:
            str: 告警ID (失败返回None)
        """
        self._total_alerts += 1

        # 检查告警冷却期 (防止告警风暴)
        alert_key = f"{alert_type}:{table_name or 'global'}"
        if self._should_suppress_alert(alert_key):
            logger.debug(f"告警被抑制 (冷却期): {alert_title}")
            return None

        # 使用指定渠道或默认渠道
        notification_channels = (
            channels if channels is not None else self.enabled_channels
        )

        # 创建告警记录
        alert_id = self.monitoring_db.create_alert(
            alert_level=alert_level,
            alert_type=alert_type,
            alert_title=alert_title,
            alert_message=alert_message,
            source=source,
            classification=classification,
            database_type=database_type,
            table_name=table_name,
            additional_data=additional_data,
            notification_channels=notification_channels,
        )

        if not alert_id:
            self._failed_alerts += 1
            return None

        # 发送告警到各个渠道
        success = False
        for channel in notification_channels:
            if self._send_to_channel(
                channel, alert_level, alert_title, alert_message, additional_data
            ):
                success = True

        if success:
            self._sent_alerts += 1
            self._alert_cooldown[alert_key] = datetime.now()
        else:
            self._failed_alerts += 1

        return alert_id

    def _should_suppress_alert(self, alert_key: str) -> bool:
        """检查是否应该抑制告警 (冷却期内)"""
        if alert_key not in self._alert_cooldown:
            return False

        last_sent = self._alert_cooldown[alert_key]
        elapsed = (datetime.now() - last_sent).total_seconds()

        return elapsed < self._cooldown_seconds

    def _send_to_channel(
        self,
        channel: str,
        alert_level: str,
        alert_title: str,
        alert_message: str,
        additional_data: Optional[Dict] = None,
    ) -> bool:
        """
        发送告警到指定渠道

        Args:
            channel: 渠道名称 (log/email/webhook)
            alert_level: 告警级别
            alert_title: 告警标题
            alert_message: 告警信息
            additional_data: 额外数据

        Returns:
            bool: 发送是否成功
        """
        try:
            if channel == "log":
                return self._send_to_log(alert_level, alert_title, alert_message)
            elif channel == "email":
                return self._send_to_email(
                    alert_level, alert_title, alert_message, additional_data
                )
            elif channel == "webhook":
                return self._send_to_webhook(
                    alert_level, alert_title, alert_message, additional_data
                )
            else:
                logger.warning(f"未知告警渠道: {channel}")
                return False

        except Exception as e:
            logger.error(f"发送告警失败 (渠道={channel}): {e}")
            return False

    def _send_to_log(
        self, alert_level: str, alert_title: str, alert_message: str
    ) -> bool:
        """发送告警到日志"""
        # 根据告警级别使用不同的日志级别
        if alert_level == "CRITICAL":
            logger.critical(f"🚨 [ALERT] {alert_title}\n{alert_message}")
        elif alert_level == "WARNING":
            logger.warning(f"⚠️  [ALERT] {alert_title}\n{alert_message}")
        else:
            logger.info(f"ℹ️  [ALERT] {alert_title}\n{alert_message}")

        return True

    def _send_to_email(
        self,
        alert_level: str,
        alert_title: str,
        alert_message: str,
        additional_data: Optional[Dict] = None,
    ) -> bool:
        """
        发送告警邮件

        注: 需要配置SMTP服务器信息
        """
        try:
            # TODO: 实现邮件发送逻辑
            # import smtplib
            # from email.mime.text import MIMEText
            # ...

            logger.info(f"📧 邮件告警: {alert_title} (未实现)")
            return False  # 暂未实现

        except Exception as e:
            logger.error(f"发送邮件告警失败: {e}")
            return False

    def _send_to_webhook(
        self,
        alert_level: str,
        alert_title: str,
        alert_message: str,
        additional_data: Optional[Dict] = None,
    ) -> bool:
        """
        发送告警到Webhook

        注: 需要配置Webhook URL
        """
        try:
            # TODO: 实现Webhook发送逻辑
            # import requests
            # payload = {
            #     'alert_level': alert_level,
            #     'alert_title': alert_title,
            #     'alert_message': alert_message,
            #     'timestamp': datetime.now().isoformat()
            # }
            # response = requests.post(webhook_url, json=payload)
            # ...

            logger.info(f"🔗 Webhook告警: {alert_title} (未实现)")
            return False  # 暂未实现

        except Exception as e:
            logger.error(f"发送Webhook告警失败: {e}")
            return False

    def acknowledge_alert(self, alert_id: str, operator: str) -> bool:
        """
        确认告警

        Args:
            alert_id: 告警ID
            operator: 操作人

        Returns:
            bool: 确认是否成功
        """
        success = self.monitoring_db.update_alert_status(
            alert_id=alert_id, alert_status="ACKNOWLEDGED", operator=operator
        )

        if success:
            logger.info(f"✓ 告警已确认: {alert_id} (by {operator})")

        return success

    def resolve_alert(
        self, alert_id: str, operator: str, resolution_notes: Optional[str] = None
    ) -> bool:
        """
        解决告警

        Args:
            alert_id: 告警ID
            operator: 操作人
            resolution_notes: 解决说明

        Returns:
            bool: 解决是否成功
        """
        success = self.monitoring_db.update_alert_status(
            alert_id=alert_id,
            alert_status="RESOLVED",
            operator=operator,
            resolution_notes=resolution_notes,
        )

        if success:
            logger.info(f"✓ 告警已解决: {alert_id} (by {operator})")

        return success

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取告警统计信息

        Returns:
            dict: 统计信息
        """
        stats = {
            "total_alerts": self._total_alerts,
            "sent_alerts": self._sent_alerts,
            "failed_alerts": self._failed_alerts,
            "success_rate": 0.0,
        }

        if self._total_alerts > 0:
            stats["success_rate"] = self._sent_alerts / self._total_alerts * 100

        return stats

    def set_cooldown(self, seconds: int):
        """
        设置告警冷却期

        Args:
            seconds: 冷却时间(秒)
        """
        self._cooldown_seconds = seconds
        logger.info(f"✓ 告警冷却期设置为: {seconds}秒")

    def configure_email(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_addr: str,
        to_addrs: List[str],
    ):
        """
        配置邮件告警

        Args:
            smtp_host: SMTP服务器地址
            smtp_port: SMTP端口
            smtp_user: SMTP用户名
            smtp_password: SMTP密码
            from_addr: 发件人地址
            to_addrs: 收件人地址列表
        """
        # TODO: 保存邮件配置
        logger.info("✓ 邮件告警已配置 (未实现)")

    def configure_webhook(self, webhook_url: str, webhook_secret: Optional[str] = None):
        """
        配置Webhook告警

        Args:
            webhook_url: Webhook URL
            webhook_secret: Webhook密钥 (可选)
        """
        # TODO: 保存Webhook配置
        logger.info("✓ Webhook告警已配置 (未实现)")


# 全局告警管理器实例 (单例模式)
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """获取全局告警管理器实例 (单例模式)"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


if __name__ == "__main__":
    """测试告警管理器"""
    import sys

    sys.path.insert(0, ".")

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("\n测试AlertManager...\n")

    # 创建告警管理器
    alert_mgr = AlertManager(enabled_channels=["log"])

    # 测试1: INFO级别告警
    print("1. 测试INFO级别告警...")
    alert_id = alert_mgr.send_alert(
        alert_level="INFO",
        alert_type="CUSTOM",
        alert_title="系统启动通知",
        alert_message="MyStocks系统已成功启动",
        source="System",
    )
    print(f"   告警ID: {alert_id}\n")

    # 测试2: WARNING级别告警
    print("2. 测试WARNING级别告警...")
    alert_id = alert_mgr.send_alert(
        alert_level="WARNING",
        alert_type="DATA_QUALITY",
        alert_title="数据缺失率偏高",
        alert_message="daily_kline表数据缺失率达到6%",
        source="DataQualityMonitor",
        classification="DAILY_KLINE",
        database_type="PostgreSQL",
        table_name="daily_kline",
    )
    print(f"   告警ID: {alert_id}\n")

    # 测试3: CRITICAL级别告警
    print("3. 测试CRITICAL级别告警...")
    alert_id = alert_mgr.send_alert(
        alert_level="CRITICAL",
        alert_type="CONNECTION_FAILURE",
        alert_title="数据库连接失败",
        alert_message="无法连接到TDengine数据库",
        source="ConnectionManager",
        database_type="TDengine",
    )
    print(f"   告警ID: {alert_id}\n")

    # 测试4: 告警冷却期 (相同告警被抑制)
    print("4. 测试告警冷却期...")
    alert_mgr.set_cooldown(10)  # 设置10秒冷却期

    alert_id1 = alert_mgr.send_alert(
        alert_level="WARNING",
        alert_type="SLOW_QUERY",
        alert_title="慢查询检测",
        alert_message="查询耗时8秒",
        table_name="daily_kline",
    )
    print(f"   第1次告警ID: {alert_id1}")

    import time

    time.sleep(1)  # 等待1秒

    alert_id2 = alert_mgr.send_alert(
        alert_level="WARNING",
        alert_type="SLOW_QUERY",
        alert_title="慢查询检测",
        alert_message="查询耗时9秒",
        table_name="daily_kline",
    )
    print(f"   第2次告警ID: {alert_id2} (应该被抑制=None)\n")

    # 测试5: 确认和解决告警
    if alert_id:
        print("5. 测试确认和解决告警...")
        alert_mgr.acknowledge_alert(alert_id, operator="admin")
        alert_mgr.resolve_alert(
            alert_id, operator="admin", resolution_notes="问题已修复"
        )
        print("   ✓ 告警已确认并解决\n")

    # 测试6: 显示统计信息
    print("6. 告警统计信息:")
    stats = alert_mgr.get_statistics()
    print(f"   总告警数: {stats['total_alerts']}")
    print(f"   成功发送: {stats['sent_alerts']}")
    print(f"   发送失败: {stats['failed_alerts']}")
    print(f"   成功率: {stats['success_rate']:.2f}%\n")

    print("✅ AlertManager 所有测试完成!")
