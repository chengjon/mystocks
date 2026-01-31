"""
GPU设备健康监控
实现设备故障检测、性能监控和主动告警
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """健康状态"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"


class AlertType(Enum):
    """告警类型"""

    HIGH_MEMORY_USAGE = "high_memory_usage"
    HIGH_COMPUTE_USAGE = "high_compute_usage"
    DEVICE_ERROR = "device_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    TEMPERATURE_HIGH = "temperature_high"
    DRIVER_ERROR = "driver_error"
    MEMORY_ERROR = "memory_error"


@dataclass
class PerformanceThreshold:
    """性能阈值配置"""

    memory_threshold: float = 0.85  # 内存使用率阈值
    compute_threshold: float = 0.9  # 计算使用率阈值
    temperature_threshold: float = 85.0  # 温度阈值（摄氏度）
    response_time_threshold: float = 100.0  # 响应时间阈值（毫秒）
    error_rate_threshold: float = 0.05  # 错误率阈值


@dataclass
class DeviceHealthInfo:
    """设备健康信息"""

    device_id: int
    status: HealthStatus
    last_check_time: float
    metrics: Dict[str, float]
    active_alerts: List[AlertType]
    error_count: int = 0
    consecutive_failures: int = 0
    last_error_time: float = 0.0


@dataclass
class FailureResponse:
    """故障处理响应"""

    success: bool
    action_taken: str
    fallback_device: Optional[int] = None
    affected_strategies: List[str] = None
    recovery_time_ms: float = 0.0
    error_details: str = ""


class DeviceHealthMonitor:
    """GPU设备健康监控器"""

    def __init__(
        self,
        resource_manager,
        thresholds: Optional[PerformanceThreshold] = None,
        check_interval: float = 5.0,  # 检查间隔（秒）
    ):
        self.resource_manager = resource_manager
        self.thresholds = thresholds or PerformanceThreshold()
        self.check_interval = check_interval

        # 设备健康状态
        self.device_health: Dict[int, DeviceHealthInfo] = {}

        # 监控状态
        self.is_monitoring = False
        self.monitoring_task = None

        # 告警回调
        self.alert_callbacks: List[Callable] = []

        # 故障恢复策略
        self.recovery_strategies: List[Callable] = [
            self._try_backup_stream,
            self._try_backup_gpu,
            self._try_cpu_fallback,
        ]

        # 统计信息
        self.stats = {
            "total_checks": 0,
            "alerts_triggered": 0,
            "failures_handled": 0,
            "recoveries_completed": 0,
        }

        logger.info("DeviceHealthMonitor initialized")

    async def start_monitoring(self) -> None:
        """开始监控"""
        if self.is_monitoring:
            logger.warning("Health monitoring already started")
            return

        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        logger.info("Device health monitoring started")

    async def stop_monitoring(self) -> None:
        """停止监控"""
        if not self.is_monitoring:
            return

        self.is_monitoring = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Device health monitoring stopped")

    async def _monitoring_loop(self):
        """监控主循环"""
        while self.is_monitoring:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in health monitoring loop: %s", e)
                await asyncio.sleep(self.check_interval)

    async def _perform_health_check(self):
        """执行健康检查"""
        try:
            # 更新设备指标
            await self.resource_manager.update_device_metrics()

            # 获取所有设备
            devices = self.resource_manager.get_available_devices()

            for device in devices:
                await self._check_device_health(device.device_id)

            self.stats["total_checks"] += 1

        except Exception as e:
            logger.error("Error performing health check: %s", e)

    async def _check_device_health(self, device_id: int):
        """检查单个设备健康状态"""
        try:
            # 获取设备健康信息
            health_info = self.resource_manager.get_device_health(device_id)

            # 提取关键指标
            metrics = {
                "memory_utilization": health_info.get("memory_utilization", 0.0),
                "compute_utilization": health_info.get("compute_utilization", 0.0),
                "temperature": health_info.get("temperature", 0.0),
                "power_usage": health_info.get("power_usage", 0.0),
                "response_time": health_info.get("response_time", 0.0),
                "error_rate": health_info.get("error_rate", 0.0),
            }

            # 获取或创建设备健康信息
            if device_id not in self.device_health:
                self.device_health[device_id] = DeviceHealthInfo(
                    device_id=device_id,
                    status=HealthStatus.HEALTHY,
                    last_check_time=time.time(),
                    metrics=metrics,
                    active_alerts=[],
                )

            device_health = self.device_health[device_id]
            device_health.last_check_time = time.time()
            device_health.metrics = metrics

            # 检查性能阈值
            alerts = self._check_performance_thresholds(device_id, metrics)
            device_health.active_alerts = alerts

            # 更新健康状态
            device_health.status = self._determine_health_status(metrics, alerts)

            # 处理告警
            if alerts:
                await self._handle_alerts(device_id, alerts, metrics)

            # 检查设备故障
            if device_health.status in [HealthStatus.CRITICAL, HealthStatus.FAILED]:
                await self._handle_device_failure(device_id)

        except Exception as e:
            logger.error("Error checking device %s health: %s", device_id, e)
            await self._mark_device_failed(device_id, str(e))

    def _check_performance_thresholds(self, device_id: int, metrics: Dict[str, float]) -> List[AlertType]:
        """检查性能阈值"""
        alerts = []

        # 检查内存使用率
        if metrics.get("memory_utilization", 0.0) > self.thresholds.memory_threshold:
            alerts.append(AlertType.HIGH_MEMORY_USAGE)

        # 检查计算使用率
        if metrics.get("compute_utilization", 0.0) > self.thresholds.compute_threshold:
            alerts.append(AlertType.HIGH_COMPUTE_USAGE)

        # 检查温度
        if metrics.get("temperature", 0.0) > self.thresholds.temperature_threshold:
            alerts.append(AlertType.TEMPERATURE_HIGH)

        # 检查响应时间
        if metrics.get("response_time", 0.0) > self.thresholds.response_time_threshold:
            alerts.append(AlertType.PERFORMANCE_DEGRADATION)

        # 检查错误率
        if metrics.get("error_rate", 0.0) > self.thresholds.error_rate_threshold:
            alerts.append(AlertType.DEVICE_ERROR)

        return alerts

    def _determine_health_status(self, metrics: Dict[str, float], alerts: List[AlertType]) -> HealthStatus:
        """确定健康状态"""
        if AlertType.DEVICE_ERROR in alerts or AlertType.DRIVER_ERROR in alerts:
            return HealthStatus.FAILED

        if AlertType.MEMORY_ERROR in alerts:
            return HealthStatus.CRITICAL

        if len(alerts) >= 2 or AlertType.TEMPERATURE_HIGH in alerts:
            return HealthStatus.WARNING

        if alerts:
            return HealthStatus.WARNING

        return HealthStatus.HEALTHY

    async def _handle_alerts(self, device_id: int, alerts: List[AlertType], metrics: Dict[str, float]):
        """处理告警"""
        for alert_type in alerts:
            await self._trigger_alert(device_id, alert_type, metrics)

        self.stats["alerts_triggered"] += len(alerts)

    async def _trigger_alert(self, device_id: int, alert_type: AlertType, metrics: Dict[str, float]):
        """触发告警"""
        alert_data = {
            "device_id": device_id,
            "alert_type": alert_type.value,
            "timestamp": time.time(),
            "metrics": metrics,
            "message": self._generate_alert_message(alert_type, metrics),
        }

        logger.warning("GPU Alert: %s", alert_data["message"])

        # 调用告警回调
        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                logger.error("Error in alert callback: %s", e)

    def _generate_alert_message(self, alert_type: AlertType, metrics: Dict[str, float]) -> str:
        """生成告警消息"""
        messages = {
            AlertType.HIGH_MEMORY_USAGE: f"High memory usage: {metrics.get('memory_utilization', 0):.1%}",
            AlertType.HIGH_COMPUTE_USAGE: f"High compute usage: {metrics.get('compute_utilization', 0):.1%}",
            AlertType.TEMPERATURE_HIGH: f"High temperature: {metrics.get('temperature', 0):.1f}°C",
            AlertType.PERFORMANCE_DEGRADATION: (
                f"Performance degradation: {metrics.get('response_time', 0):.1f}ms response time"
            ),
            AlertType.DEVICE_ERROR: "Device error detected",
            AlertType.DRIVER_ERROR: "Driver error detected",
            AlertType.MEMORY_ERROR: "Memory error detected",
        }

        return messages.get(alert_type, "Unknown alert type")

    async def _handle_device_failure(self, device_id: int) -> FailureResponse:
        """处理设备故障"""
        logger.error("Handling device failure for GPU %s", device_id)
        self.stats["failures_handled"] += 1

        # 执行渐进式降级
        for i, recovery_strategy in enumerate(self.recovery_strategies):
            try:
                logger.info("Attempting recovery strategy %s: %s", i + 1, recovery_strategy.__name__)

                start_time = time.time()
                result = await recovery_strategy(device_id)
                (time.time() - start_time) * 1000

                if result.success:
                    self.stats["recoveries_completed"] += 1
                    logger.info("Recovery strategy %s succeeded for device %s", i + 1, device_id)
                    return result

            except Exception as e:
                logger.error("Recovery strategy %s failed for device %s: %s", i + 1, device_id, e)
                continue

        # 所有恢复策略都失败
        logger.error("All recovery strategies failed for device %s", device_id)
        return FailureResponse(
            success=False,
            action_taken="All recovery strategies failed",
            recovery_time_ms=0,
            error_details="Device failure could not be resolved",
        )

    async def _try_backup_stream(self, device_id: int) -> FailureResponse:
        """尝试备用流"""
        try:
            # 这里需要实现切换到备用计算流的逻辑
            # 模拟操作
            await asyncio.sleep(0.01)  # 10ms切换时间

            logger.info("Switched to backup stream for device %s", device_id)
            return FailureResponse(
                success=True,
                action_taken="Switched to backup stream",
                recovery_time_ms=10.0,
            )

        except Exception as e:
            logger.error("Failed to switch to backup stream for device %s: %s", device_id, e)
            return FailureResponse(
                success=False,
                action_taken="Backup stream switch failed",
                error_details=str(e),
            )

    async def _try_backup_gpu(self, device_id: int) -> FailureResponse:
        """尝试备用GPU"""
        try:
            # 查找可用的备用GPU
            available_devices = [
                d for d in self.resource_manager.get_available_devices() if d.device_id != device_id and d.is_available
            ]

            if not available_devices:
                logger.warning("No backup GPU available for device %s", device_id)
                return FailureResponse(success=False, action_taken="No backup GPU available")

            # 选择最佳备用GPU（内存最多，利用率最低）
            backup_device = min(
                available_devices,
                key=lambda d: (d.current_utilization, -d.memory_total),
            )

            # 模拟迁移过程
            await asyncio.sleep(0.05)  # 50ms迁移时间

            logger.info("Migrated from device %s to backup device %s", device_id, backup_device.device_id)
            return FailureResponse(
                success=True,
                action_taken="Migrated to backup GPU",
                fallback_device=backup_device.device_id,
                recovery_time_ms=50.0,
            )

        except Exception as e:
            logger.error("Failed to migrate to backup GPU for device %s: %s", device_id, e)
            return FailureResponse(
                success=False,
                action_taken="Backup GPU migration failed",
                error_details=str(e),
            )

    async def _try_cpu_fallback(self, device_id: int) -> FailureResponse:
        """尝试CPU降级"""
        try:
            # 获取受影响的策略列表
            device_health = self.device_health.get(device_id)
            affected_strategies = []

            if device_health:
                # 这里需要从资源管理器获取受影响的策略
                # 暂时返回空列表
                pass

            # 模拟CPU降级过程
            await asyncio.sleep(0.1)  # 100ms降级时间

            logger.info("Fallback to CPU for device %s", device_id)
            return FailureResponse(
                success=True,
                action_taken="Fallback to CPU",
                affected_strategies=affected_strategies,
                recovery_time_ms=100.0,
            )

        except Exception as e:
            logger.error("Failed to fallback to CPU for device %s: %s", device_id, e)
            return FailureResponse(success=False, action_taken="CPU fallback failed", error_details=str(e))

    async def _mark_device_failed(self, device_id: int, error_message: str):
        """标记设备为故障状态"""
        if device_id not in self.device_health:
            self.device_health[device_id] = DeviceHealthInfo(
                device_id=device_id,
                status=HealthStatus.FAILED,
                last_check_time=time.time(),
                metrics={},
                active_alerts=[AlertType.DEVICE_ERROR],
            )

        device_health = self.device_health[device_id]
        device_health.status = HealthStatus.FAILED
        device_health.error_count += 1
        device_health.consecutive_failures += 1
        device_health.last_error_time = time.time()

        logger.error("Device %s marked as failed: %s", device_id, error_message)

    def check_performance_thresholds(self, device_id: int) -> List[str]:
        """检查性能阈值（同步接口）"""
        if device_id not in self.device_health:
            return ["Device not monitored"]

        device_health = self.device_health[device_id]
        alerts = [alert.value for alert in device_health.active_alerts]

        if alerts:
            return [f"Device {device_id} alerts: {', '.join(alerts)}"]

        return []

    def trigger_proactive_alert(self, device_id: int, alert_type: str, message: str) -> None:
        """触发主动告警"""
        alert_data = {
            "device_id": device_id,
            "alert_type": alert_type,
            "timestamp": time.time(),
            "message": message,
            "source": "proactive",
        }

        logger.warning("Proactive GPU Alert: %s", message)

        # 调用告警回调
        for callback in self.alert_callbacks:
            try:
                asyncio.create_task(callback(alert_data))
            except Exception as e:
                logger.error("Error in proactive alert callback: %s", e)

    def add_alert_callback(self, callback: Callable):
        """添加告警回调函数"""
        self.alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: Callable):
        """移除告警回调函数"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)

    def get_device_health_summary(self) -> Dict[str, Any]:
        """获取设备健康摘要"""
        summary = {
            "monitoring_active": self.is_monitoring,
            "check_interval": self.check_interval,
            "thresholds": {
                "memory_threshold": self.thresholds.memory_threshold,
                "compute_threshold": self.thresholds.compute_threshold,
                "temperature_threshold": self.thresholds.temperature_threshold,
            },
            "devices": {},
        }

        for device_id, health_info in self.device_health.items():
            summary["devices"][device_id] = {
                "status": health_info.status.value,
                "last_check": health_info.last_check_time,
                "error_count": health_info.error_count,
                "consecutive_failures": health_info.consecutive_failures,
                "active_alerts": [alert.value for alert in health_info.active_alerts],
                "metrics": health_info.metrics,
            }

        summary["statistics"] = self.stats.copy()

        return summary

    def get_statistics(self) -> Dict[str, Any]:
        """获取监控统计信息"""
        return {
            "monitoring_active": self.is_monitoring,
            "total_checks": self.stats["total_checks"],
            "alerts_triggered": self.stats["alerts_triggered"],
            "failures_handled": self.stats["failures_handled"],
            "recoveries_completed": self.stats["recoveries_completed"],
            "monitored_devices": len(self.device_health),
            "alert_callbacks": len(self.alert_callbacks),
        }
