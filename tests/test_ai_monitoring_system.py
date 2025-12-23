"""
MyStocks AI监控系统测试

测试AIAlertManager和AIRealtimeMonitor的完整功能。

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0
依赖: pytest, asyncio
注意事项: 本文件是MyStocks v3.0测试组件
版权: MyStocks Project © 2025
"""

import pytest
import asyncio
import time
from datetime import datetime

import sys

sys.path.insert(0, ".")

from src.monitoring.ai_alert_manager import (
    AIAlertManager,
    AlertType,
    AlertSeverity,
    AlertRule,
    Alert,
    SystemMetrics,
)

from src.monitoring.ai_realtime_monitor import (
    AIRealtimeMonitor,
    MonitoringConfig,
    AdaptiveIntervalManager,
)


class TestAIAlertManager:
    """AI告警管理器测试"""

    @pytest.fixture
    def alert_manager(self):
        """创建测试用的告警管理器"""
        return AIAlertManager()

    @pytest.fixture
    def system_metrics(self):
        """创建测试用的系统指标"""
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=85.0,
            memory_usage=75.0,
            gpu_memory_used=6500.0,
            gpu_memory_total=8192.0,
            gpu_utilization=60.0,
            disk_usage=45.0,
            network_io={"bytes_sent": 1000000, "bytes_recv": 2000000},
            ai_strategy_metrics={"win_rate": 0.25, "active_strategies": 3},
            trading_metrics={"sharpe_ratio": 0.45, "data_quality_score": 0.75},
        )

    def test_alert_manager_initialization(self, alert_manager):
        """测试告警管理器初始化"""
        assert alert_manager is not None
        assert len(alert_manager.alert_rules) > 0
        assert len(alert_manager.alert_handlers) > 0  # 应该有默认的日志处理器
        assert alert_manager.active_alerts == {}
        assert alert_manager.alert_history == []

    def test_default_alert_rules(self, alert_manager):
        """测试默认告警规则"""
        rules = alert_manager.get_alert_rules()

        # 检查关键规则是否存在
        rule_names = [rule.name for rule in rules]

        expected_rules = [
            "CPU使用率过高",
            "GPU内存使用率过高",
            "AI策略胜率异常",
            "AI策略回撤过大",
            "数据质量异常",
            "慢查询检测",
        ]

        for expected_rule in expected_rules:
            assert expected_rule in rule_names, f"缺少默认规则: {expected_rule}"

    def test_add_custom_alert_rule(self, alert_manager):
        """测试添加自定义告警规则"""
        initial_count = len(alert_manager.get_alert_rules())

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

        assert len(alert_manager.get_alert_rules()) == initial_count + 1

        # 验证规则可以找到
        rules = alert_manager.get_alert_rules()
        test_rule = next((rule for rule in rules if rule.name == "测试规则"), None)
        assert test_rule is not None
        assert test_rule.threshold == 95.0

    def test_update_alert_rule(self, alert_manager):
        """测试更新告警规则"""
        # 获取第一个规则
        rules = alert_manager.get_alert_rules()
        if not rules:
            pytest.skip("没有可用的告警规则")

        rule = rules[0]
        original_threshold = rule.threshold

        # 更新规则
        success = alert_manager.update_alert_rule(rule.name, {"threshold": 90.0})
        assert success is True

        # 验证更新
        updated_rule = next(
            (r for r in alert_manager.get_alert_rules() if r.name == rule.name), None
        )
        assert updated_rule is not None
        assert updated_rule.threshold == 90.0
        assert updated_rule.threshold != original_threshold

    @pytest.mark.asyncio
    async def test_alert_triggering(self, alert_manager, system_metrics):
        """测试告警触发"""
        # 清空现有活跃告警
        alert_manager.active_alerts.clear()

        # 检查告警条件 (应该触发CPU告警)
        await alert_manager.check_alert_conditions(system_metrics)

        # 验证告警被触发
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) > 0

        # 验证告警信息
        cpu_alert = next(
            (alert for alert in active_alerts if "CPU" in alert.rule_name), None
        )
        assert cpu_alert is not None
        assert cpu_alert.severity == AlertSeverity.WARNING
        assert "CPU使用率过高" in cpu_alert.message

    @pytest.mark.asyncio
    async def test_alert_resolving(self, alert_manager):
        """测试告警解决"""
        # 创建低CPU使用率的指标
        low_cpu_metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=60.0,  # 低于阈值
            memory_usage=75.0,
            gpu_memory_used=6500.0,
            gpu_memory_total=8192.0,
            gpu_utilization=60.0,
            disk_usage=45.0,
            network_io={"bytes_sent": 1000000, "bytes_recv": 2000000},
            ai_strategy_metrics={"win_rate": 0.25, "active_strategies": 3},
            trading_metrics={"sharpe_ratio": 0.45, "data_quality_score": 0.75},
        )

        # 首先触发一个告警
        high_cpu_metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=85.0,  # 高于阈值
            memory_usage=75.0,
            gpu_memory_used=6500.0,
            gpu_memory_total=8192.0,
            gpu_utilization=60.0,
            disk_usage=45.0,
            network_io={"bytes_sent": 1000000, "bytes_recv": 2000000},
            ai_strategy_metrics={"win_rate": 0.25, "active_strategies": 3},
            trading_metrics={"sharpe_ratio": 0.45, "data_quality_score": 0.75},
        )

        await alert_manager.check_alert_conditions(high_cpu_metrics)
        assert len(alert_manager.get_active_alerts()) > 0

        # 然后使用低CPU指标，应该解决告警
        await alert_manager.check_alert_conditions(low_cpu_metrics)

        # 等待一下让告警解决逻辑执行
        await asyncio.sleep(0.1)

        # 验证告警被解决
        active_alerts = alert_manager.get_active_alerts()
        cpu_alerts = [alert for alert in active_alerts if "CPU" in alert.rule_name]
        assert len(cpu_alerts) == 0

    @pytest.mark.asyncio
    async def test_alert_handlers(self, alert_manager):
        """测试告警处理器"""
        # 创建测试告警
        test_alert = Alert(
            id="test_alert_001",
            rule_name="测试规则",
            alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
            severity=AlertSeverity.WARNING,
            message="测试告警消息",
            timestamp=datetime.now(),
            metrics={"test_data": "test_value"},
        )

        # 测试所有处理器
        results = await alert_manager.test_all_handlers()

        # 至少应该有日志处理器
        assert "LogAlertHandler" in results
        assert isinstance(results["LogAlertHandler"], bool)

    def test_alert_acknowledgment(self, alert_manager):
        """测试告警确认"""
        # 添加一个测试告警到历史
        test_alert = Alert(
            id="test_001",
            rule_name="测试规则",
            alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
            severity=AlertSeverity.INFO,
            message="测试告警",
            timestamp=datetime.now(),
            metrics={},
        )

        alert_manager.alert_history.append(test_alert)

        # 确认告警
        success = alert_manager.acknowledge_alert("test_001", "test_user")
        assert success is True

        # 验证告警被确认
        confirmed_alert = next(
            (alert for alert in alert_manager.alert_history if alert.id == "test_001"),
            None,
        )
        assert confirmed_alert is not None
        assert confirmed_alert.acknowledged is True
        assert confirmed_alert.acknowledged_by == "test_user"
        assert confirmed_alert.acknowledged_at is not None

    def test_alert_summary(self, alert_manager):
        """测试告警摘要"""
        summary = alert_manager.get_alert_summary()

        required_fields = [
            "active_alerts_count",
            "total_alerts",
            "critical_alerts",
            "warning_alerts",
            "info_alerts",
            "resolved_alerts",
            "alert_rules_count",
            "enabled_rules_count",
            "active_alert_types",
        ]

        for field in required_fields:
            assert field in summary

        # 验证数据类型
        assert isinstance(summary["active_alerts_count"], int)
        assert isinstance(summary["alert_rules_count"], int)
        assert isinstance(summary["active_alert_types"], list)


class TestAIRealtimeMonitor:
    """AI实时监控器测试"""

    @pytest.fixture
    def monitor(self):
        """创建测试用的监控器"""
        config = MonitoringConfig(
            monitoring_interval=1.0,  # 短间隔用于测试
            max_history_size=10,
            enable_gpu_monitoring=True,
            enable_ai_strategy_monitoring=True,
            adaptive_intervals=False,  # 禁用自适应间隔用于测试
        )
        return AIRealtimeMonitor(config=config)

    @pytest.fixture
    def system_metrics(self):
        """创建测试用的系统指标"""
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=85.0,
            memory_usage=75.0,
            gpu_memory_used=6500.0,
            gpu_memory_total=8192.0,
            gpu_utilization=60.0,
            disk_usage=45.0,
            network_io={"bytes_sent": 1000000, "bytes_recv": 2000000},
            ai_strategy_metrics={"win_rate": 0.25, "active_strategies": 3},
            trading_metrics={"sharpe_ratio": 0.45, "data_quality_score": 0.75},
        )

    def test_monitor_initialization(self, monitor):
        """测试监控器初始化"""
        assert monitor is not None
        assert monitor.running is False
        assert monitor.config.monitoring_interval == 1.0
        assert len(monitor.metrics_history) == 0
        assert monitor.current_metrics is None
        assert monitor.stats["total_cycles"] == 0

    @pytest.mark.asyncio
    async def test_metrics_collection(self, monitor):
        """测试指标收集"""
        # 测试系统指标收集器
        assert monitor.system_collector.is_available() is True

        system_metrics = await monitor.system_collector.collect_metrics()
        assert system_metrics is not None
        assert "cpu_usage" in system_metrics
        assert "memory_usage" in system_metrics
        assert "disk_usage" in system_metrics
        assert "timestamp" in system_metrics

        # 测试AI策略指标收集器
        assert monitor.ai_strategy_collector.is_available() is True

        ai_metrics = await monitor.ai_strategy_collector.collect_metrics()
        assert ai_metrics is not None
        assert "active_strategies" in ai_metrics
        assert "win_rate" in ai_metrics

    @pytest.mark.asyncio
    async def test_short_monitoring_session(self, monitor):
        """测试短时间监控会话"""
        # 启动10秒监控
        start_time = time.time()
        await monitor.start_monitoring(duration_seconds=10)
        duration = time.time() - start_time

        # 验证监控运行了足够的时间
        assert duration >= 9.5  # 允许一些误差

        # 验证统计信息
        assert monitor.stats["total_cycles"] > 0
        assert monitor.stats["successful_cycles"] > 0
        assert monitor.current_metrics is not None
        assert len(monitor.metrics_history) > 0

    def test_metrics_summary(self, monitor, system_metrics):
        """测试指标摘要"""
        monitor.current_metrics = system_metrics

        summary = monitor.get_metrics_summary()

        assert "monitoring_status" in summary
        assert "current_metrics" in summary
        assert "statistics" in summary
        assert "configuration" in summary

        # 验证当前指标
        current_metrics = summary["current_metrics"]
        assert "cpu_usage" in current_metrics
        assert "memory_usage" in current_metrics
        assert "gpu_utilization" in current_metrics

        # 验证统计信息
        statistics = summary["statistics"]
        assert "total_cycles" in statistics
        assert "success_rate" in statistics
        assert "avg_cycle_time" in statistics

    @pytest.mark.asyncio
    async def test_health_check(self, monitor):
        """测试健康检查"""
        health_check = await monitor.run_health_check()

        required_fields = ["overall_status", "checks", "timestamp"]
        for field in required_fields:
            assert field in health_check

        # 验证检查项目
        assert "monitoring_status" in health_check["checks"]
        assert "system_collector" in health_check["checks"]
        assert "ai_strategy_collector" in health_check["checks"]
        assert "trading_collector" in health_check["checks"]
        assert "alert_system" in health_check["checks"]

        # 验证状态值
        assert health_check["overall_status"] in [
            "healthy",
            "warning",
            "degraded",
            "error",
        ]

        for check_name, check_result in health_check["checks"].items():
            assert "status" in check_result
            assert "message" in check_result
            assert check_result["status"] in [
                "healthy",
                "warning",
                "error",
                "available",
                "unavailable",
                "stopped",
            ]

    def test_config_updates(self, monitor):
        """测试配置更新"""
        original_interval = monitor.config.monitoring_interval

        monitor.update_config(
            {
                "monitoring_interval": 2.0,
                "enable_gpu_monitoring": False,
                "adaptive_intervals": True,
            }
        )

        assert monitor.config.monitoring_interval == 2.0
        assert monitor.config.monitoring_interval != original_interval
        assert monitor.config.enable_gpu_monitoring is False
        assert monitor.config.adaptive_intervals is True

    def test_performance_thresholds(self, monitor):
        """测试性能阈值设置"""
        original_cpu_warning = monitor.thresholds.cpu_warning

        monitor.set_performance_thresholds(
            {"cpu_warning": 75.0, "gpu_memory_warning": 80.0}
        )

        assert monitor.thresholds.cpu_warning == 75.0
        assert monitor.thresholds.cpu_warning != original_cpu_warning
        assert monitor.thresholds.gpu_memory_warning == 80.0


class TestAdaptiveIntervalManager:
    """自适应间隔管理器测试"""

    def test_interval_calculation(self):
        """测试间隔计算"""
        manager = AdaptiveIntervalManager(
            base_interval=5.0, min_interval=2.0, max_interval=60.0
        )

        # 测试正常负载
        system_metrics = {"cpu_usage": 50, "memory_usage": 50}
        interval = manager.calculate_next_interval(system_metrics)
        assert 2.0 <= interval <= 60.0

        # 测试高负载
        system_metrics = {"cpu_usage": 90, "memory_usage": 85}
        interval = manager.calculate_next_interval(system_metrics)
        assert interval >= manager.base_interval  # 应该增加间隔

        # 测试低负载
        system_metrics = {"cpu_usage": 20, "memory_usage": 25}
        interval = manager.calculate_next_interval(system_metrics)
        assert interval <= manager.base_interval  # 应该减少间隔

    def test_interval_bounds(self):
        """测试间隔边界"""
        manager = AdaptiveIntervalManager(
            base_interval=5.0, min_interval=2.0, max_interval=60.0
        )

        # 多次调用确保不会超出边界
        for _ in range(100):
            system_metrics = {"cpu_usage": 50, "memory_usage": 50}
            interval = manager.calculate_next_interval(system_metrics)
            assert manager.min_interval <= interval <= manager.max_interval


class TestSystemIntegration:
    """系统集成测试"""

    @pytest.mark.asyncio
    async def test_alert_manager_and_monitor_integration(self):
        """测试告警管理器和监控器集成"""
        # 创建集成系统
        alert_manager = AIAlertManager()
        monitor = AIRealtimeMonitor(alert_manager=alert_manager)

        # 启动短时间监控
        await monitor.start_monitoring(duration_seconds=15)

        # 验证系统集成
        assert alert_manager.get_alert_summary() is not None
        assert monitor.get_metrics_summary() is not None

        # 验证监控和告警系统协作
        health_check = await monitor.run_health_check()
        assert "alert_system" in health_check["checks"]


if __name__ == "__main__":
    """运行测试"""
    pytest.main([__file__, "-v", "--tb=short"])
