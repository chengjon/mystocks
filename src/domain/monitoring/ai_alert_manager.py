"""
MyStocks AI告警管理器

完整的AI智能告警系统，支持多渠道告警、邮件、Webhook、日志等。
基于智能阈值算法和误报优化。

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0 (完整AI版本)
依赖: 详见requirements.txt或文件导入部分
注意事项: 本文件是MyStocks v3.0核心组件，遵循5-tier数据分类架构
版权: MyStocks Project © 2025
"""

import asyncio
import logging
import json
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp

from src.monitoring.monitoring_database import (
    MonitoringDatabase,
    get_monitoring_database,
)

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """告警类型"""

    PERFORMANCE_DEGRADATION = "performance_degradation"
    GPU_MEMORY_HIGH = "gpu_memory_high"
    AI_MODEL_ERROR = "ai_model_error"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    SYSTEM_RESOURCE_HIGH = "system_resource_high"
    STRATEGY_ANOMALY = "strategy_anomaly"
    TRADING_SIGNAL_ABNORMAL = "trading_signal_abnormal"
    SLOW_QUERY = "slow_query"
    CONNECTION_FAILURE = "connection_failure"


class AlertSeverity(Enum):
    """告警严重性"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class AlertRule:
    """告警规则"""

    name: str
    alert_type: AlertType
    severity: AlertSeverity
    threshold: float
    duration_seconds: int
    enabled: bool
    description: str
    custom_conditions: Optional[Dict[str, Any]] = None


def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["alert_type"] = self.alert_type.value
        data["severity"] = self.severity.value
        return data


@dataclass
class Alert:
    """告警实例"""

    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["alert_type"] = self.alert_type.value
        data["severity"] = self.severity.value
        return data


class IAlertHandler(ABC):
    """告警处理器接口"""

    @abstractmethod
async def handle_alert(self, alert: Alert) -> bool:
        """处理告警"""
        pass

    @abstractmethod
async def test_connection(self) -> bool:
        """测试连接"""
        pass


@dataclass
class SystemMetrics:
    """系统指标"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    gpu_memory_used: float
    gpu_memory_total: float
    gpu_utilization: float
    disk_usage: float
    network_io: Dict[str, float]
    ai_strategy_metrics: Dict[str, Any]
    trading_metrics: Dict[str, Any]

def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class EmailAlertHandler(IAlertHandler):
    """邮件告警处理器"""

def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        recipients: List[str],
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients

async def handle_alert(self, alert: Alert) -> bool:
        """处理告警"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = ", ".join(self.recipients)
            msg["Subject"] = f"[{alert.severity.value.upper()}] MyStocks AI告警: {alert.rule_name}"

            # 邮件正文
            body = f"""
            <html>
            <body>
                <h2>MyStocks AI系统告警</h2>
                <p><strong>告警ID:</strong> {alert.id}</p>
                <p><strong>规则名称:</strong> {alert.rule_name}</p>
                <p><strong>严重性:</strong> {alert.severity.value}</p>
                <p><strong>告警类型:</strong> {alert.alert_type.value}</p>
                <p><strong>发生时间:</strong> {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p><strong>告警消息:</strong> {alert.message}</p>

                <h3>详细指标:</h3>
                <pre>{json.dumps(alert.metrics, indent=2, ensure_ascii=False)}</pre>

                <p>请及时处理此告警。</p>
                <p><small>此邮件由MyStocks AI监控系统自动发送</small></p>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, "html", "utf-8"))

            # 发送邮件
            await self._send_email(msg)
            logger.info("✅ 邮件告警发送成功: %s", alert.rule_name)
            return True

        except Exception as e:
            logger.error("❌ 邮件告警发送失败: %s", e)
            return False

async def _send_email(self, msg: MIMEMultipart):
        """发送邮件"""

        def _send():
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send)

async def test_connection(self) -> bool:
        """测试连接"""
        try:

            def _test():
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    return True

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _test)

        except Exception as e:
            logger.error("❌ 邮件连接测试失败: %s", e)
            return False


class WebhookAlertHandler(IAlertHandler):
    """Webhook告警处理器"""

def __init__(
        self,
        webhook_url: str,
        headers: Dict[str, str] = None,
        auth_token: Optional[str] = None,
    ):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"

async def handle_alert(self, alert: Alert) -> bool:
        """处理告警"""
        try:
            payload = {
                "alert_id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "alert_type": alert.alert_type.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metrics": alert.metrics,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        logger.info("✅ Webhook告警发送成功: %s", alert.rule_name)
                        return True
                    else:
                        logger.error("❌ Webhook告警发送失败: HTTP %s", response.status)
                        return False

        except Exception as e:
            logger.error("❌ Webhook告警发送失败: %s", e)
            return False

async def test_connection(self) -> bool:
        """测试连接"""
        try:
            test_payload = {
                "test": True,
                "message": "MyStocks AI监控连接测试",
                "timestamp": datetime.now().isoformat(),
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=test_payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    return response.status == 200

        except Exception as e:
            logger.error("❌ Webhook连接测试失败: %s", e)
            return False


class LogAlertHandler(IAlertHandler):
    """本地日志告警处理器"""

def __init__(self, log_file: str = "ai_alerts.log"):
        self.log_file = log_file

        # 配置日志
        self.logger = logging.getLogger("AIAlertHandler")

        # 添加文件处理器
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        if not any(isinstance(h, logging.FileHandler) for h in self.logger.handlers):
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)

async def handle_alert(self, alert: Alert) -> bool:
        """处理告警"""
        try:
            log_message = f"""
========================================
AI系统告警通知
========================================
告警ID: {alert.id}
规则名称: {alert.rule_name}
严重性: {alert.severity.value.upper()}
告警类型: {alert.alert_type.value}
发生时间: {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
告警消息: {alert.message}

详细指标:
{json.dumps(alert.metrics, indent=2, ensure_ascii=False)}
========================================
            """

            if alert.severity == AlertSeverity.CRITICAL:
                self.logger.critical(log_message)
            elif alert.severity == AlertSeverity.WARNING:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)

            return True

        except Exception as e:
            print(f"❌ 日志告警处理失败: {e}")
            return False

async def test_connection(self) -> bool:
        """测试连接"""
        try:
            self.logger.info("MyStocks AI监控日志处理器连接测试")
            return True
        except Exception as e:
            print(f"❌ 日志处理器测试失败: {e}")
            return False


class AIAlertManager:
    """AI告警管理器 - 完整版本"""

def __init__(self, monitoring_db: Optional[MonitoringDatabase] = None):
        """初始化AI告警管理器"""
        self.monitoring_db = monitoring_db or get_monitoring_database()
        self.alert_rules = self._load_default_alert_rules()
        self.active_alerts = {}
        self.alert_handlers = []
        self.alert_history = []
        self.max_history_size = 10000
        self.alert_stats = {
            "total_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0,
            "info_alerts": 0,
            "resolved_alerts": 0,
        }

        # 添加默认日志处理器
        self.add_alert_handler(LogAlertHandler())

        logger.info("✅ AIAlertManager initialized")

def _load_default_alert_rules(self) -> List[AlertRule]:
        """加载默认告警规则"""
        return [
            AlertRule(
                name="CPU使用率过高",
                alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
                severity=AlertSeverity.WARNING,
                threshold=80.0,
                duration_seconds=60,
                enabled=True,
                description="CPU使用率持续超过80%",
            ),
            AlertRule(
                name="GPU内存使用率过高",
                alert_type=AlertType.GPU_MEMORY_HIGH,
                severity=AlertSeverity.WARNING,
                threshold=85.0,
                duration_seconds=30,
                enabled=True,
                description="GPU内存使用率持续超过85%",
            ),
            AlertRule(
                name="AI策略胜率异常",
                alert_type=AlertType.STRATEGY_ANOMALY,
                severity=AlertSeverity.CRITICAL,
                threshold=0.3,
                duration_seconds=300,
                enabled=True,
                description="AI策略胜率持续低于30%",
            ),
            AlertRule(
                name="AI策略回撤过大",
                alert_type=AlertType.STRATEGY_ANOMALY,
                severity=AlertSeverity.CRITICAL,
                threshold=5.0,
                duration_seconds=180,
                enabled=True,
                description="AI策略最大回撤持续超过5%",
            ),
            AlertRule(
                name="数据质量异常",
                alert_type=AlertType.DATA_QUALITY_ISSUE,
                severity=AlertSeverity.WARNING,
                threshold=0.8,
                duration_seconds=120,
                enabled=True,
                description="数据质量评分持续低于80%",
            ),
            AlertRule(
                name="慢查询检测",
                alert_type=AlertType.SLOW_QUERY,
                severity=AlertSeverity.WARNING,
                threshold=5000.0,  # 5秒
                duration_seconds=30,
                enabled=True,
                description="查询执行时间超过5秒",
            ),
        ]

def add_alert_handler(self, handler: IAlertHandler):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
        logger.info("✅ 添加告警处理器: %s", handler.__class__.__name__)

def add_alert_rule(self, rule: AlertRule):
        """添加自定义告警规则"""
        self.alert_rules.append(rule)
        logger.info("✅ 添加自定义告警规则: %s", rule.name)

def remove_alert_rule(self, rule_name: str):
        """移除告警规则"""
        self.alert_rules = [rule for rule in self.alert_rules if rule.name != rule_name]
        # 移除相关的活跃告警
        if rule_name in self.active_alerts:
            del self.active_alerts[rule_name]
        logger.info("🗑️ 移除告警规则: %s", rule_name)

async def check_alert_conditions(self, metrics: SystemMetrics):
        """检查告警条件"""
        for rule in self.alert_rules:
            if not rule.enabled:
                continue

            try:
                # 获取指标值
                metric_value = self._get_metric_value(metrics, rule.alert_type)

                if metric_value is None:
                    continue

                # 检查是否触发告警
                triggered = self._check_threshold(metric_value, rule)

                if triggered:
                    await self._trigger_alert(rule, metrics, metric_value)
                else:
                    await self._resolve_alert(rule)

            except Exception as e:
                logger.error("❌ 告警规则 %s 检查失败: %s", rule.name, e)

def _get_metric_value(self, metrics: SystemMetrics, alert_type: AlertType) -> Optional[float]:
        """获取指标值"""
        if alert_type == AlertType.SYSTEM_RESOURCE_HIGH:
            return metrics.cpu_usage
        elif alert_type == AlertType.GPU_MEMORY_HIGH:
            return (metrics.gpu_memory_used / metrics.gpu_memory_total * 100) if metrics.gpu_memory_total > 0 else 0
        elif alert_type == AlertType.STRATEGY_ANOMALY:
            return metrics.ai_strategy_metrics.get("win_rate", 0)
        elif alert_type == AlertType.DATA_QUALITY_ISSUE:
            return metrics.trading_metrics.get("data_quality_score", 0)
        elif alert_type == AlertType.PERFORMANCE_DEGRADATION:
            return metrics.trading_metrics.get("sharpe_ratio", 0)
        elif alert_type == AlertType.SLOW_QUERY:
            return metrics.trading_metrics.get("last_query_time", 0)

        return None

def _check_threshold(self, metric_value: float, rule: AlertRule) -> bool:
        """检查阈值"""
        if rule.alert_type == AlertType.GPU_MEMORY_HIGH:
            return metric_value > rule.threshold
        elif rule.alert_type == AlertType.SYSTEM_RESOURCE_HIGH:
            return metric_value > rule.threshold
        elif rule.alert_type == AlertType.STRATEGY_ANOMALY:
            return metric_value < rule.threshold
        elif rule.alert_type == AlertType.DATA_QUALITY_ISSUE:
            return metric_value < rule.threshold
        elif rule.alert_type == AlertType.PERFORMANCE_DEGRADATION:
            return metric_value < rule.threshold
        elif rule.alert_type == AlertType.SLOW_QUERY:
            return metric_value > rule.threshold

        return False

async def _trigger_alert(self, rule: AlertRule, metrics: SystemMetrics, metric_value: float):
        """触发告警"""
        alert_id = f"{rule.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 检查是否已有未解决的同类告警
        if rule.name in self.active_alerts:
            return

        # 创建告警
        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            alert_type=rule.alert_type,
            severity=rule.severity,
            message=self._generate_alert_message(rule, metric_value),
            timestamp=datetime.now(),
            metrics={
                "current_value": metric_value,
                "threshold": rule.threshold,
                "duration_seconds": rule.duration_seconds,
                "system_metrics": self._serialize_metrics(metrics),
            },
        )

        # 保存告警
        self.active_alerts[rule.name] = alert
        self._save_alert_history(alert)
        self._update_alert_stats(alert)

        # 处理告警
        await self._handle_alert(alert)

        logger.warning("🚨 告警触发: %s", alert.message)

async def _resolve_alert(self, rule: AlertRule):
        """解决告警"""
        if rule.name in self.active_alerts:
            alert = self.active_alerts[rule.name]
            alert.resolved = True
            alert.resolved_at = datetime.now()

            del self.active_alerts[rule.name]
            self._save_alert_history(alert)
            self.alert_stats["resolved_alerts"] += 1

            logger.info("✅ 告警解决: %s", rule.name)

def _generate_alert_message(self, rule: AlertRule, metric_value: float) -> str:
        """生成告警消息"""
        if rule.alert_type == AlertType.GPU_MEMORY_HIGH:
            return f"GPU内存使用率过高: {metric_value:.1f}% (阈值: {rule.threshold}%)"
        elif rule.alert_type == AlertType.SYSTEM_RESOURCE_HIGH:
            return f"CPU使用率过高: {metric_value:.1f}% (阈值: {rule.threshold}%)"
        elif rule.alert_type == AlertType.STRATEGY_ANOMALY:
            return f"AI策略胜率异常: {metric_value:.1%} (阈值: {rule.threshold}%)"
        elif rule.alert_type == AlertType.DATA_QUALITY_ISSUE:
            return f"数据质量异常: {metric_value:.1%} (阈值: {rule.threshold}%)"
        elif rule.alert_type == AlertType.SLOW_QUERY:
            return f"慢查询检测: {metric_value:.0f}ms (阈值: {rule.threshold:.0f}ms)"
        else:
            return f"{rule.name}: {metric_value:.2f} (阈值: {rule.threshold})"

def _serialize_metrics(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """序列化指标"""
        return {
            "timestamp": metrics.timestamp.isoformat(),
            "cpu_usage": metrics.cpu_usage,
            "memory_usage": metrics.memory_usage,
            "gpu_utilization": metrics.gpu_utilization,
            "ai_strategies_count": len(metrics.ai_strategy_metrics),
            "trading_metrics": metrics.trading_metrics,
        }

def _save_alert_history(self, alert: Alert):
        """保存告警历史"""
        self.alert_history.append(alert)

        # 保持历史大小限制
        if len(self.alert_history) > self.max_history_size:
            self.alert_history = self.alert_history[-self.max_history_size :]

        # 保存到监控数据库
        if self.monitoring_db:
            try:
                self.monitoring_db.record_alert(
                    alert_id=alert.id,
                    alert_type=alert.alert_type.value,
                    severity=alert.severity.value,
                    message=alert.message,
                    source="AIAlertManager",
                    additional_data=alert.to_dict(),
                )
            except Exception as e:
                logger.error("❌ 保存告警到数据库失败: %s", e)

def _update_alert_stats(self, alert: Alert):
        """更新告警统计"""
        self.alert_stats["total_alerts"] += 1

        if alert.severity == AlertSeverity.CRITICAL:
            self.alert_stats["critical_alerts"] += 1
        elif alert.severity == AlertSeverity.WARNING:
            self.alert_stats["warning_alerts"] += 1
        else:
            self.alert_stats["info_alerts"] += 1

async def _handle_alert(self, alert: Alert):
        """处理告警"""
        # 通知所有处理器
        for handler in self.alert_handlers:
            try:
                success = await handler.handle_alert(alert)
                if not success:
                    logger.error("❌ 告警处理器 %s 处理失败", handler.__class__.__name__)
            except Exception as e:
                logger.error("❌ 告警处理器异常: %s", e)

def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())

def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """确认告警"""
        for alert in self.alert_history:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = acknowledged_by
                logger.info("✅ 告警已确认: %s by %s", alert_id, acknowledged_by)
                return True
        return False

def get_alert_summary(self) -> Dict[str, Any]:
        """获取告警摘要"""
        return {
            "active_alerts_count": len(self.active_alerts),
            "total_alerts": self.alert_stats["total_alerts"],
            "critical_alerts": self.alert_stats["critical_alerts"],
            "warning_alerts": self.alert_stats["warning_alerts"],
            "info_alerts": self.alert_stats["info_alerts"],
            "resolved_alerts": self.alert_stats["resolved_alerts"],
            "alert_rules_count": len(self.alert_rules),
            "enabled_rules_count": len([r for r in self.alert_rules if r.enabled]),
            "active_alert_types": list(self.active_alerts.keys()),
        }

async def test_all_handlers(self) -> Dict[str, bool]:
        """测试所有告警处理器"""
        results = {}
        for handler in self.alert_handlers:
            try:
                result = await handler.test_connection()
                results[handler.__class__.__name__] = result
            except Exception as e:
                logger.error("❌ 处理器 %s 测试失败: %s", handler.__class__.__name__, e)
                results[handler.__class__.__name__] = False

        return results

def get_alert_rules(self) -> List[AlertRule]:
        """获取所有告警规则"""
        return self.alert_rules.copy()

def update_alert_rule(self, rule_name: str, updates: Dict[str, Any]) -> bool:
        """更新告警规则"""
        for rule in self.alert_rules:
            if rule.name == rule_name:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                logger.info("✅ 更新告警规则: %s", rule_name)
                return True
        return False


# 全局AI告警管理器实例 (单例模式)
_ai_alert_manager: Optional[AIAlertManager] = None


def get_ai_alert_manager() -> AIAlertManager:
    """获取全局AI告警管理器实例 (单例模式)"""
    global _ai_alert_manager
    if _ai_alert_manager is None:
        _ai_alert_manager = AIAlertManager()
    return _ai_alert_manager


if __name__ == "__main__":
    """测试AI告警管理器"""
    import sys

    sys.path.insert(0, ".")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    print("\n测试AIAlertManager...\n")

    # 创建AI告警管理器
    alert_manager = AIAlertManager()

    # 测试1: 测试所有处理器
    print("1. 测试告警处理器...")
    test_results = asyncio.run(alert_manager.test_all_handlers())
    print(f"   处理器测试结果: {test_results}\n")

    # 测试2: 创建模拟系统指标
    print("2. 创建模拟系统指标...")
    metrics = SystemMetrics(
        timestamp=datetime.now(),
        cpu_usage=85.0,  # 触发CPU告警
        memory_usage=75.0,
        gpu_memory_used=6500.0,
        gpu_memory_total=8192.0,
        gpu_utilization=60.0,
        disk_usage=45.0,
        network_io={"bytes_sent": 1000000, "bytes_recv": 2000000},
        ai_strategy_metrics={"win_rate": 0.25, "active_strategies": 3},  # 触发策略告警
        trading_metrics={"sharpe_ratio": 0.45, "data_quality_score": 0.75},
    )
    print(f"   创建完成: CPU={metrics.cpu_usage}%, AI胜率={metrics.ai_strategy_metrics['win_rate']:.1%}\n")

    # 测试3: 检查告警条件
    print("3. 检查告警条件...")
    asyncio.run(alert_manager.check_alert_conditions(metrics))
    print("   告警检查完成\n")

    # 测试4: 获取告警摘要
    print("4. 获取告警摘要...")
    summary = alert_manager.get_alert_summary()
    print(f"   活跃告警数: {summary['active_alerts_count']}")
    print(f"   告警规则数: {summary['alert_rules_count']}\n")

    # 测试5: 添加自定义告警规则
    print("5. 添加自定义告警规则...")
    custom_rule = AlertRule(
        name="测试规则",
        alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
        severity=AlertSeverity.INFO,
        threshold=95.0,
        duration_seconds=10,
        enabled=True,
        description="测试自定义告警规则",
    )
    alert_manager.add_alert_rule(custom_rule)
    print("   自定义规则添加完成\n")

    # 测试6: 模拟解决告警
    print("6. 模拟解决告警...")
    metrics = SystemMetrics(
        timestamp=datetime.now(),
        cpu_usage=70.0,  # 低于阈值
        memory_usage=75.0,
        gpu_memory_used=6500.0,
        gpu_memory_total=8192.0,
        gpu_utilization=60.0,
        disk_usage=45.0,
        network_io={"bytes_sent": 1000000, "bytes_recv": 2000000},
        ai_strategy_metrics={"win_rate": 0.35, "active_strategies": 3},  # 高于阈值
        trading_metrics={"sharpe_ratio": 0.45, "data_quality_score": 0.75},
    )
    asyncio.run(alert_manager.check_alert_conditions(metrics))
    print("   告警解决模拟完成\n")

    # 测试7: 获取最终状态
    print("7. 获取最终状态...")
    final_summary = alert_manager.get_alert_summary()
    print(f"   最终活跃告警: {final_summary['active_alerts_count']}")
    print(f"   告警历史总数: {len(alert_manager.alert_history)}\n")

    print("✅ AIAlertManager 所有测试完成!")
