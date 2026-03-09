"""
MyStocks AI实时监控器

AI驱动的实时监控系统，负责系统性能、GPU状态、AI策略性能和交易指标的实时监控。
集成智能阈值算法和自适应监控间隔优化。

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0 (完整AI版本)
依赖: 详见requirements.txt或文件导入部分
注意事项: 本文件是MyStocks v3.0核心组件，遵循5-tier数据分类架构
版权: MyStocks Project © 2025
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.monitoring.ai_alert_manager import (
    AIAlertManager,
    SystemMetrics,
    get_ai_alert_manager,
)
from src.monitoring._ai_realtime_monitor_components import (
    AIStrategyMetricsCollector,
    AdaptiveIntervalManager,
    GPUMetricsCollector,
    MonitoringConfig,
    PerformanceThresholds,
    SystemMetricsCollector,
    TradingMetricsCollector,
)

logger = logging.getLogger(__name__)


class AIRealtimeMonitor:
    """AI实时监控器"""

    def __init__(
        self,
        alert_manager: Optional[AIAlertManager] = None,
        config: Optional[MonitoringConfig] = None,
    ):
        """初始化AI实时监控器"""
        self.alert_manager = alert_manager or get_ai_alert_manager()
        self.config = config or MonitoringConfig()
        self.thresholds = PerformanceThresholds()

        # 监控状态
        self.running = False
        self.monitoring_task = None

        # 指标历史
        self.metrics_history = []
        self.current_metrics = None
        self.max_history_size = self.config.max_history_size

        # 指标收集器
        self.system_collector = SystemMetricsCollector(self.config)
        self.gpu_collector = GPUMetricsCollector(self.config)
        self.ai_strategy_collector = AIStrategyMetricsCollector(self.config)
        self.trading_collector = TradingMetricsCollector(self.config)

        # 自适应间隔管理器
        self.adaptive_manager = AdaptiveIntervalManager(self.config.monitoring_interval)

        # 统计信息
        self.stats = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "avg_cycle_time": 0.0,
            "last_metrics_time": None,
            "monitoring_start_time": None,
        }

        logger.info("✅ AIRealtimeMonitor initialized (interval: %ss)", self.config.monitoring_interval)

    async def start_monitoring(self, duration_seconds: int = 120):
        """启动实时监控"""
        if self.running:
            logger.warning("⚠️ 监控已在运行中")
            return

        self.running = True
        self.stats["monitoring_start_time"] = datetime.now()

        print(f"🔍 开始AI实时监控，时长: {duration_seconds}秒")
        logger.info("🔍 开始AI实时监控，时长: %s秒", duration_seconds)

        try:
            monitoring_start = time.time()
            cycle_count = 0

            while self.running and (time.time() - monitoring_start) < duration_seconds:
                cycle_start_time = time.time()
                cycle_count += 1

                try:
                    # 收集系统指标
                    metrics = await self._collect_all_metrics()

                    if metrics:
                        # 保存指标
                        self.current_metrics = metrics
                        self._save_metrics_history(metrics)

                        # 检查告警条件 (每N次检查一次)
                        if cycle_count % self.config.alert_check_frequency == 0:
                            await self._check_alert_conditions()

                        # 更新统计
                        self.stats["successful_cycles"] += 1
                        cycle_time = time.time() - cycle_start_time
                        self._update_cycle_stats(cycle_time)

                        # 打印状态 (每10次循环打印一次)
                        if cycle_count % 10 == 0:
                            self._print_monitoring_status()
                    else:
                        self.stats["failed_cycles"] += 1
                        logger.warning("⚠️ 指标收集失败")

                    # 等待下一个监控周期 (自适应间隔)
                    if self.running:
                        interval = self.adaptive_manager.get_interval()

                        # 如果启用了自适应间隔，根据系统负载调整
                        if self.config.adaptive_intervals and self.current_metrics:
                            system_metrics = self.current_metrics.get("system", {})
                            interval = self.adaptive_manager.calculate_next_interval(system_metrics)

                        await asyncio.sleep(interval)

                except Exception as e:
                    logger.error("❌ 监控循环异常: %s", e)
                    self.stats["failed_cycles"] += 1
                    await asyncio.sleep(5)  # 错误后短暂等待

                self.stats["total_cycles"] += 1

        except Exception as e:
            logger.error("❌ 监控异常: %s", e)
        finally:
            self.running = False
            self._print_final_stats()
            print("🛑 AI实时监控已停止")
            logger.info("🛑 AI实时监控已停止")

    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        logger.info("🛑 正在停止监控...")

    async def _collect_all_metrics(self) -> Optional[SystemMetrics]:
        """收集所有指标"""
        try:
            # 并行收集各类指标
            tasks = []

            # 系统指标
            if self.system_collector.is_available():
                tasks.append(self.system_collector.collect_metrics())

            # GPU指标
            if self.gpu_collector.is_available():
                tasks.append(self.gpu_collector.collect_metrics())

            # AI策略指标
            if self.ai_strategy_collector.is_available():
                tasks.append(self.ai_strategy_collector.collect_metrics())

            # 交易指标
            if self.trading_collector.is_available():
                tasks.append(self.trading_collector.collect_metrics())

            # 等待所有收集任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 解析结果
            system_metrics = {}
            gpu_metrics = {}
            ai_strategy_metrics = {}
            trading_metrics = {}

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error("❌ 指标收集异常: %s", result)
                    continue

                if i == 0 and self.system_collector.is_available():
                    system_metrics = result
                elif i == 1 and self.gpu_collector.is_available():
                    gpu_metrics = result
                elif i == 2 and self.ai_strategy_collector.is_available():
                    ai_strategy_metrics = result
                elif i == 3 and self.trading_collector.is_available():
                    trading_metrics = result

            # 组合系统指标
            if not system_metrics:
                return None

            combined_metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=system_metrics.get("cpu_usage", 0.0),
                memory_usage=system_metrics.get("memory_usage", 0.0),
                gpu_memory_used=gpu_metrics.get("gpu_memory_used", 0.0),
                gpu_memory_total=gpu_metrics.get("gpu_memory_total", 0.0),
                gpu_utilization=gpu_metrics.get("gpu_utilization", 0.0),
                disk_usage=system_metrics.get("disk_usage", 0.0),
                network_io=system_metrics.get("network_io", {}),
                ai_strategy_metrics=ai_strategy_metrics,
                trading_metrics=trading_metrics,
            )

            self.stats["last_metrics_time"] = datetime.now()
            return combined_metrics

        except Exception as e:
            logger.error("❌ 指标收集失败: %s", e)
            return None

    def _save_metrics_history(self, metrics: SystemMetrics):
        """保存指标历史"""
        self.metrics_history.append(metrics)

        # 保持历史大小限制
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size :]

    async def _check_alert_conditions(self):
        """检查告警条件"""
        try:
            if self.current_metrics:
                await self.alert_manager.check_alert_conditions(self.current_metrics)
        except Exception as e:
            logger.error("❌ 告警检查失败: %s", e)

    def _update_cycle_stats(self, cycle_time: float):
        """更新循环统计"""
        # 更新平均执行时间
        total_cycles = self.stats["total_cycles"]
        if total_cycles <= 1:
            self.stats["avg_cycle_time"] = cycle_time
        else:
            # 移动平均
            current_avg = self.stats["avg_cycle_time"]
            self.stats["avg_cycle_time"] = (current_avg * (total_cycles - 1) + cycle_time) / total_cycles

    def _print_monitoring_status(self):
        """打印监控状态"""
        if not self.current_metrics:
            return

        metrics = self.current_metrics
        status_msg = (
            f"📊 监控状态 | CPU: {metrics.cpu_usage:.1f}% | "
            f"GPU: {metrics.gpu_utilization:.1f}% | "
            f"内存: {metrics.memory_usage:.1f}% | "
            f"循环: {self.stats['successful_cycles']}/{self.stats['total_cycles']}"
        )

        print(status_msg)
        logger.info(status_msg)

    def _print_final_stats(self):
        """打印最终统计"""
        stats = self.stats
        ((datetime.now() - stats["monitoring_start_time"]).total_seconds() if stats["monitoring_start_time"] else 0)

        final_msg = (
            f"📊 监控完成 | 总循环: {stats['total_cycles']} | "
            f"成功: {stats['successful_cycles']} | "
            f"失败: {stats['failed_cycles']} | "
            f"成功率: {stats['successful_cycles'] / max(stats['total_cycles'], 1) * 100:.1f}% | "
            f"平均时间: {stats['avg_cycle_time']:.2f}s"
        )

        print(f"\n{final_msg}")
        logger.info(final_msg)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if not self.current_metrics:
            return {}

        metrics = self.current_metrics

        summary = {
            "monitoring_status": "running" if self.running else "stopped",
            "current_metrics": {
                "cpu_usage": f"{metrics.cpu_usage:.1f}%",
                "memory_usage": f"{metrics.memory_usage:.1f}%",
                "gpu_utilization": f"{metrics.gpu_utilization:.1f}%",
                "gpu_memory_usage": (
                    f"{metrics.gpu_memory_used:.0f}/{metrics.gpu_memory_total:.0f}MB"
                    if metrics.gpu_memory_total > 0
                    else "N/A"
                ),
                "disk_usage": f"{metrics.disk_usage:.1f}%",
                "active_strategies": len(metrics.ai_strategy_metrics.get("strategy_performance", {})),
                "win_rate": (
                    f"{metrics.ai_strategy_metrics.get('win_rate', 0) * 100:.1f}%"
                    if metrics.ai_strategy_metrics.get("win_rate")
                    else "N/A"
                ),
                "daily_return": (
                    f"{metrics.trading_metrics.get('daily_return', 0) * 100:.2f}%"
                    if metrics.trading_metrics.get("daily_return")
                    else "N/A"
                ),
            },
            "statistics": {
                "total_cycles": self.stats["total_cycles"],
                "successful_cycles": self.stats["successful_cycles"],
                "failed_cycles": self.stats["failed_cycles"],
                "success_rate": f"{self.stats['successful_cycles'] / max(self.stats['total_cycles'], 1) * 100:.1f}%",
                "avg_cycle_time": f"{self.stats['avg_cycle_time']:.3f}s",
                "history_size": len(self.metrics_history),
                "monitoring_duration": (
                    f"{(datetime.now() - self.stats['monitoring_start_time']).total_seconds():.0f}s"
                    if self.stats["monitoring_start_time"]
                    else "0s"
                ),
            },
            "configuration": {
                "monitoring_interval": f"{self.adaptive_manager.get_interval():.1f}s",
                "adaptive_intervals": self.config.adaptive_intervals,
                "gpu_monitoring": self.config.enable_gpu_monitoring,
                "ai_strategy_monitoring": self.config.enable_ai_strategy_monitoring,
            },
        }

        return summary

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """获取活跃告警"""
        return [alert.to_dict() for alert in self.alert_manager.get_active_alerts()]

    def update_config(self, config_updates: Dict[str, Any]):
        """更新配置"""
        for key, value in config_updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        logger.info("✅ 更新监控配置: %s", config_updates)

    def set_performance_thresholds(self, thresholds: Dict[str, float]):
        """设置性能阈值"""
        for key, value in thresholds.items():
            if hasattr(self.thresholds, key):
                setattr(self.thresholds, key, value)

        logger.info("✅ 更新性能阈值: %s", thresholds)

    async def run_health_check(self) -> Dict[str, Any]:
        """运行健康检查"""
        health_status = {
            "overall_status": "healthy",
            "checks": {},
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # 检查监控状态
            health_status["checks"]["monitoring_status"] = {
                "status": "running" if self.running else "stopped",
                "message": "监控正常运行" if self.running else "监控未运行",
            }

            # 检查指标收集器
            collectors = {
                "system": self.system_collector,
                "gpu": self.gpu_collector,
                "ai_strategy": self.ai_strategy_collector,
                "trading": self.trading_collector,
            }

            for name, collector in collectors.items():
                available = collector.is_available()
                health_status["checks"][f"{name}_collector"] = {
                    "status": "available" if available else "unavailable",
                    "message": f"{name}指标收集器可用" if available else f"{name}指标收集器不可用",
                }

            # 检查告警系统
            alert_summary = self.alert_manager.get_alert_summary()
            active_alerts = alert_summary["active_alerts_count"]
            health_status["checks"]["alert_system"] = {
                "status": "healthy" if active_alerts == 0 else "warning",
                "message": f"活跃告警数: {active_alerts}" if active_alerts > 0 else "无活跃告警",
            }

            # 检查GPU状态
            if self.config.enable_gpu_monitoring:
                gpu_available = self.gpu_collector.is_available()
                health_status["checks"]["gpu_status"] = {
                    "status": "available" if gpu_available else "unavailable",
                    "message": "GPU监控可用" if gpu_available else "GPU监控不可用",
                }

            # 计算整体状态
            error_checks = [
                check for check in health_status["checks"].values() if check["status"] in ["error", "unavailable"]
            ]
            if error_checks:
                health_status["overall_status"] = "degraded" if active_alerts == 0 else "warning"
            elif active_alerts > 0:
                health_status["overall_status"] = "warning"

        except Exception as e:
            logger.error("❌ 健康检查失败: %s", e)
            health_status["overall_status"] = "error"
            health_status["error"] = str(e)

        return health_status


# 全局AI实时监控器实例 (单例模式)
_ai_realtime_monitor: Optional[AIRealtimeMonitor] = None


def get_ai_realtime_monitor(
    alert_manager: Optional[AIAlertManager] = None,
) -> AIRealtimeMonitor:
    """获取全局AI实时监控器实例 (单例模式)"""
    global _ai_realtime_monitor
    if _ai_realtime_monitor is None:
        _ai_realtime_monitor = AIRealtimeMonitor(alert_manager)
    return _ai_realtime_monitor


if __name__ == "__main__":
    """测试AI实时监控器"""
    import sys

    sys.path.insert(0, ".")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    print("\n测试AIRealtimeMonitor...\n")

    # 创建AI实时监控器
    monitor = AIRealtimeMonitor()

    # 测试1: 健康检查
    print("1. 运行健康检查...")
    health_check = asyncio.run(monitor.run_health_check())
    print(f"   健康状态: {health_check['overall_status']}")
    for check_name, check_result in health_check["checks"].items():
        print(f"   {check_name}: {check_result['status']} - {check_result['message']}")
    print()

    # 测试2: 短时间监控测试
    print("2. 启动30秒监控测试...")
    asyncio.run(monitor.start_monitoring(duration_seconds=30))
    print("   监控测试完成\n")

    # 测试3: 获取监控摘要
    print("3. 获取监控摘要...")
    summary = monitor.get_metrics_summary()
    print(f"   监控状态: {summary.get('monitoring_status', 'unknown')}")
    if summary.get("current_metrics"):
        for key, value in summary["current_metrics"].items():
            print(f"   {key}: {value}")
    print()

    # 测试4: 测试配置更新
    print("4. 测试配置更新...")
    monitor.update_config(
        {
            "monitoring_interval": 3.0,
            "enable_gpu_monitoring": True,
            "adaptive_intervals": True,
        }
    )
    print("   配置更新完成\n")

    # 测试5: 测试阈值设置
    print("5. 测试阈值设置...")
    monitor.set_performance_thresholds({"cpu_warning": 75.0, "gpu_memory_warning": 80.0})
    print("   阈值设置完成\n")

    print("✅ AIRealtimeMonitor 所有测试完成!")
