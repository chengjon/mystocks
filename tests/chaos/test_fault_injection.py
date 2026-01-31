#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
故障注入测试系统

提供全面的故障注入能力，用于测试系统的弹性和容错能力。
"""

import asyncio
import json
import random
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil
import pytest

from tests.config.test_config import test_env


class FaultType(Enum):
    """故障类型枚举"""

    NETWORK_DELAY = "network_delay"
    NETWORK_PACKET_LOSS = "network_packet_loss"
    NETWORK_PARTITION = "network_partition"
    DATABASE_TIMEOUT = "database_timeout"
    DATABASE_ERROR = "database_error"
    API_ERROR = "api_error"
    MEMORY_PRESSURE = "memory_pressure"
    CPU_PRESSURE = "cpu_pressure"
    DISK_IO_ERROR = "disk_io_error"
    PROCESS_CRASH = "process_crash"
    TIME_DRIFT = "time_drift"
    CONFIG_ERROR = "config_error"
    RESOURCE_LEAK = "resource_leak"
    CONCURRENCY_ISSUE = "concurrency_issue"
    DATA_CORRUPTION = "data_corruption"
    AUTH_FAILURE = "auth_failure"
    RATE_LIMITING = "rate_limiting"
    LOAD_BALANCER_FAILURE = "load_balancer_failure"
    CACHE_FAILURE = "cache_failure"
    MESSAGE_QUEUE_FAILURE = "message_queue_failure"


class FaultSeverity(Enum):
    """故障严重程度"""

    LOW = "low"  # 轻微影响，系统应正常处理
    MEDIUM = "medium"  # 中等影响，系统可能有短暂问题
    HIGH = "high"  # 严重影响，系统功能受限
    CRITICAL = "critical"  # 关键影响，系统核心功能受损


@dataclass
class FaultInjectionConfig:
    """故障注入配置"""

    fault_type: FaultType
    severity: FaultSeverity
    injection_method: str = "direct"
    target_service: str = "api"
    duration_seconds: int = 30
    probability: float = 0.5  # 触发概率
    parameters: Dict[str, Any] = field(default_factory=dict)
    recovery_time_seconds: int = 10
    enable_metrics: bool = True
    simulate_in_production: bool = False


@dataclass
class FaultInjectionResult:
    """故障注入结果"""

    fault_id: str
    fault_type: FaultType
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    system_metrics_before: Dict[str, Any] = field(default_factory=dict)
    system_metrics_after: Dict[str, Any] = field(default_factory=dict)
    application_metrics: Dict[str, Any] = field(default_factory=dict)
    recovery_time_seconds: Optional[float] = None
    customer_impact: str = "none"


class FaultInjector:
    """故障注入器主类"""

    def __init__(self):
        self.base_url = test_env.API_BASE_URL
        self.configs: List[FaultInjectionConfig] = []
        self.active_faults: Dict[str, FaultInjectionConfig] = {}
        self.fault_results: Dict[str, FaultInjectionResult] = {}
        self.metrics_collector = MetricsCollector()
        self.recovery_monitor = RecoveryMonitor()
        self.control_plane = ControlPlane()
        self.fault_generator = FaultGenerator()

        # 线程池用于并发执行故障
        self.executor = ThreadPoolExecutor(max_workers=5)

        # 统计信息
        self.stats = {
            "total_faults": 0,
            "successful_faults": 0,
            "failed_faults": 0,
            "average_recovery_time": 0.0,
            "system_resilience_score": 0.0,
        }

    def add_fault_config(self, config: FaultInjectionConfig):
        """添加故障配置"""
        self.configs.append(config)
        print(f"✓ 添加故障配置: {config.fault_type.value} (严重程度: {config.severity.value})")

    async def run_comprehensive_fault_injection(self):
        """运行全面的故障注入测试"""
        print("\n🎭 开始故障注入测试")
        print(f"📊 配置的故障类型数量: {len(self.configs)}")

        # 收集基线指标
        baseline_metrics = self.metrics_collector.collect_system_metrics()
        print("📈 基线系统指标已收集")

        results = []

        # 按严重程度排序执行故障
        sorted_configs = sorted(self.configs, key=lambda x: self._get_severity_weight(x.severity))

        for config in sorted_configs:
            print(f"\n⚡ 注入故障: {config.fault_type.value}")

            try:
                result = await self._inject_fault(config, baseline_metrics)
                results.append(result)

                # 故障间隔
                await asyncio.sleep(config.recovery_time_seconds)

            except Exception as e:
                print(f"❌ 故障注入失败 {config.fault_type.value}: {str(e)}")
                error_result = FaultInjectionResult(
                    fault_id=f"failed_{int(time.time())}",
                    fault_type=config.fault_type,
                    start_time=datetime.now(),
                    error_message=str(e),
                )
                results.append(error_result)
                self.stats["failed_faults"] += 1

        # 生成报告
        report = self._generate_fault_injection_report(results)
        print("\n🎭 故障注入测试完成")
        print(f"📊 完整报告: {report}")

        return report

    async def _inject_fault(
        self, config: FaultInjectionConfig, baseline_metrics: Dict[str, Any]
    ) -> FaultInjectionResult:
        """执行单个故障注入"""
        fault_id = f"fault_{int(time.time())}_{config.fault_type.value}"
        start_time = datetime.now()

        # 创建故障结果对象
        result = FaultInjectionResult(
            fault_id=fault_id,
            fault_type=config.fault_type,
            start_time=start_time,
            system_metrics_before=baseline_metrics,
        )

        try:
            print(f"  🔧 开始注入故障: {config.fault_type.value}")

            # 注册故障
            self.active_faults[fault_id] = config
            self.fault_results[fault_id] = result

            # 收集注入前指标
            pre_injection_metrics = self.metrics_collector.collect_system_metrics()

            # 根据故障类型执行注入
            await self._execute_fault_injection(config)

            # 模拟故障持续时间
            await asyncio.sleep(config.duration_seconds)

            # 开始恢复
            print("  🔄 开始恢复系统...")
            recovery_start = datetime.now()

            await self._execute_fault_recovery(config)

            recovery_end = datetime.now()
            recovery_time = (recovery_end - recovery_start).total_seconds()

            # 收集注入后指标
            post_injection_metrics = self.metrics_collector.collect_system_metrics()

            # 更新结果
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            result.recovery_time_seconds = recovery_time
            result.system_metrics_after = post_injection_metrics
            result.success = True
            result.customer_impact = self._assess_customer_impact(config, pre_injection_metrics, post_injection_metrics)

            # 更新统计
            self.stats["successful_faults"] += 1
            self._update_average_recovery_time(recovery_time)

            print(f"  ✅ 故障注入成功，恢复时间: {recovery_time:.2f}秒")
            print(f"  👥 用户影响评估: {result.customer_impact}")

        except Exception as e:
            print(f"  ❌ 故障注入失败: {str(e)}")
            result.error_message = str(e)
            result.end_time = datetime.now()
            self.stats["failed_faults"] += 1

        finally:
            # 清理活动故障
            self.active_faults.pop(fault_id, None)

        return result

    async def _execute_fault_injection(self, config: FaultInjectionConfig):
        """执行具体的故障注入"""
        fault_type = config.fault_type

        if fault_type == FaultType.NETWORK_DELAY:
            await self._inject_network_delay(config)
        elif fault_type == FaultType.NETWORK_PACKET_LOSS:
            await self._inject_network_packet_loss(config)
        elif fault_type == FaultType.NETWORK_PARTITION:
            await self._inject_network_partition(config)
        elif fault_type == FaultType.DATABASE_TIMEOUT:
            await self._inject_database_timeout(config)
        elif fault_type == FaultType.DATABASE_ERROR:
            await self._inject_database_error(config)
        elif fault_type == FaultType.API_ERROR:
            await self._inject_api_error(config)
        elif fault_type == FaultType.MEMORY_PRESSURE:
            await self._inject_memory_pressure(config)
        elif fault_type == FaultType.CPU_PRESSURE:
            await self._inject_cpu_pressure(config)
        elif fault_type == FaultType.DISK_IO_ERROR:
            await self._inject_disk_io_error(config)
        elif fault_type == FaultType.TIME_DRIFT:
            await self._inject_time_drift(config)
        elif fault_type == FaultType.CONFIG_ERROR:
            await self._inject_config_error(config)
        elif fault_type == FaultType.AUTH_FAILURE:
            await self._inject_auth_failure(config)
        elif fault_type == FaultType.RATE_LIMITING:
            await self._inject_rate_limiting(config)
        else:
            # 默认方法：使用控制平面注入
            await self.control_plane.inject_fault(config)

    async def _execute_fault_recovery(self, config: FaultInjectionConfig):
        """执行故障恢复"""
        fault_type = config.fault_type

        if fault_type == FaultType.NETWORK_DELAY:
            await self._recover_network_delay()
        elif fault_type == FaultType.NETWORK_PACKET_LOSS:
            await self._recover_network_packet_loss()
        elif fault_type == FaultType.NETWORK_PARTITION:
            await self._recover_network_partition()
        elif fault_type == FaultType.DATABASE_TIMEOUT:
            await self._recover_database_timeout()
        elif fault_type == FaultType.DATABASE_ERROR:
            await self._recover_database_error()
        elif fault_type == FaultType.API_ERROR:
            await self._recover_api_error()
        elif fault_type == FaultType.MEMORY_PRESSURE:
            await self._recover_memory_pressure()
        elif fault_type == FaultType.CPU_PRESSURE:
            await self._recover_cpu_pressure()
        elif fault_type == FaultType.DISK_IO_ERROR:
            await self._recover_disk_io_error()
        elif fault_type == FaultType.TIME_DRIFT:
            await self._recover_time_drift()
        elif fault_type == FaultType.CONFIG_ERROR:
            await self._recover_config_error()
        elif fault_type == FaultType.AUTH_FAILURE:
            await self._recover_auth_failure()
        elif fault_type == FaultType.RATE_LIMITING:
            await self._recover_rate_limiting()
        else:
            # 默认恢复方法
            await self.control_plane.recover_fault(config)

    # 网络故障注入方法
    async def _inject_network_delay(self, config: FaultInjectionConfig):
        """注入网络延迟故障"""
        delay_ms = config.parameters.get("delay_ms", 1000)
        print(f"    🌐 模拟网络延迟: {delay_ms}ms")

        # 使用tc命令或代理延迟网络请求
        delay_factor = delay_ms / 1000.0

        async def delayed_request(*args, **kwargs):
            await asyncio.sleep(delay_factor)
            return args, kwargs

        # 注册延迟处理器
        self.control_plane.register_delay_handler(delayed_request)

    async def _inject_network_packet_loss(self, config: FaultInjectionConfig):
        """注入网络丢包故障"""
        loss_rate = config.parameters.get("loss_rate", 0.1)
        print(f"    📡 模拟网络丢包: {loss_rate * 100}%")

        # 随机丢弃请求
        async def packet_loss_handler(request_func):
            if random.random() < loss_rate:
                raise Exception("Network packet loss detected")
            return await request_func()

        self.control_plane.register_packet_loss_handler(packet_loss_handler)

    async def _inject_network_partition(self, config: FaultInjectionConfig):
        """注入网络分区故障"""
        partition_duration = config.parameters.get("partition_duration", 30)
        print(f"    🔗 模拟网络分区: {partition_duration}秒")

        # 模拟网络不可达
        await self.control_plane.simulate_network_partition(partition_duration)

    # 数据库故障注入方法
    async def _inject_database_timeout(self, config: FaultInjectionConfig):
        """注入数据库超时故障"""
        timeout_seconds = config.parameters.get("timeout_seconds", 5)
        print(f"    🗄️  模拟数据库超时: {timeout_seconds}秒")

        # 模拟数据库查询超时
        await self.control_plane.simulate_database_timeout(timeout_seconds)

    async def _inject_database_error(self, config: FaultInjectionConfig):
        """注入数据库错误故障"""
        error_type = config.parameters.get("error_type", "connection_error")
        print(f"    🗄️  模拟数据库错误: {error_type}")

        # 模拟数据库连接错误或查询错误
        await self.control_plane.simulate_database_error(error_type)

    # API故障注入方法
    async def _inject_api_error(self, config: FaultInjectionConfig):
        """注入API错误故障"""
        error_code = config.parameters.get("error_code", 500)
        error_rate = config.parameters.get("error_rate", 0.2)
        print(f"    🚫 模拟API错误: {error_code} (错误率: {error_rate * 100}%)")

        # 随机返回API错误
        await self.control_plane.simulate_api_error(error_code, error_rate)

    # 系统资源故障注入方法
    async def _inject_memory_pressure(self, config: FaultInjectionConfig):
        """注入内存压力故障"""
        memory_usage_mb = config.parameters.get("memory_usage_mb", 1024)
        print(f"    💾 模拟内存压力: {memory_usage_mb}MB")

        # 模拟内存使用增加
        await self.control_plane.simulate_memory_pressure(memory_usage_mb)

    async def _inject_cpu_pressure(self, config: FaultInjectionConfig):
        """注入CPU压力故障"""
        cpu_usage_percent = config.parameters.get("cpu_usage_percent", 90)
        print(f"    ⚡ 模拟CPU压力: {cpu_usage_percent}%")

        # 模拟CPU使用率增加
        await self.control_plane.simulate_cpu_pressure(cpu_usage_percent)

    async def _inject_disk_io_error(self, config: FaultInjectionConfig):
        """注入磁盘I/O错误"""
        io_error_rate = config.parameters.get("io_error_rate", 0.1)
        print(f" 💽 模拟磁盘I/O错误: {io_error_rate * 100}%")

        # 模拟磁盘I/O错误
        await self.control_plane.simulate_disk_io_error(io_error_rate)

    # 时间相关故障注入方法
    async def _inject_time_drift(self, config: FaultInjectionConfig):
        """注入时间漂移故障"""
        time_drift_seconds = config.parameters.get("time_drift_seconds", 3600)
        print(f"🕐 模拟时间漂移: {time_drift_seconds}秒")

        # 模拟系统时间偏移
        await self.control_plane.simulate_time_drift(time_drift_seconds)

    # 配置故障注入方法
    async def _inject_config_error(self, config: FaultInjectionConfig):
        """注入配置错误故障"""
        config_key = config.parameters.get("config_key", "database_url")
        config_value = config.parameters.get("config_value", "invalid")
        print(f"⚙️  模拟配置错误: {config_key} = {config_value}")

        # 临时修改配置
        await self.control_plane.simulate_config_error(config_key, config_value)

    # 认证故障注入方法
    async def _inject_auth_failure(self, config: FaultInjectionConfig):
        """注入认证失败故障"""
        auth_failure_rate = config.parameters.get("auth_failure_rate", 0.3)
        print(f"🔐 模拟认证失败: {auth_failure_rate * 100}%")

        # 模拟认证失败
        await self.control_plane.simulate_auth_failure(auth_failure_rate)

    # 限流故障注入方法
    async def _inject_rate_limiting(self, config: FaultInjectionConfig):
        """注入限流故障"""
        requests_per_second = config.parameters.get("requests_per_second", 1)
        print(f"⏱️  模拟限流: {requests_per_second} 请求/秒")

        # 模拟API限流
        await self.control_plane.simulate_rate_limiting(requests_per_second)

    # 恢复方法
    async def _recover_network_delay(self):
        """恢复网络延迟"""
        print("    🌐 恢复网络延迟")
        self.control_plane.unregister_delay_handler()

    async def _recover_network_packet_loss(self):
        """恢复网络丢包"""
        print("    📡 恢复网络丢包")
        self.control_plane.unregister_packet_loss_handler()

    async def _recover_network_partition(self):
        """恢复网络分区"""
        print("    🔗 恢复网络分区")
        self.control_plane.recover_network_partition()

    async def _recover_database_timeout(self):
        """恢复数据库超时"""
        print("    🗄️  恢复数据库超时")
        self.control_plane.recover_database_timeout()

    async def _recover_database_error(self):
        """恢复数据库错误"""
        print("    🗄️  恢复数据库错误")
        self.control_plane.recover_database_error()

    async def _recover_api_error(self):
        """恢复API错误"""
        print("    🚫 恢复API错误")
        self.control_plane.recover_api_error()

    async def _recover_memory_pressure(self):
        """恢复内存压力"""
        print("    💾 恢复内存压力")
        self.control_plane.recover_memory_pressure()

    async def _recover_cpu_pressure(self):
        """恢复CPU压力"""
        print("    ⚡ 恢复CPU压力")
        self.control_plane.recover_cpu_pressure()

    async def _recover_disk_io_error(self):
        """恢复磁盘I/O错误"""
        print(" 💽 恢复磁盘I/O错误")
        self.control_plane.recover_disk_io_error()

    async def _recover_time_drift(self):
        """恢复时间漂移"""
        print("🕐 恢复时间漂移")
        self.control_plane.recover_time_drift()

    async def _recover_config_error(self):
        """恢复配置错误"""
        print("⚙️  恢复配置错误")
        self.control_plane.recover_config_error()

    async def _recover_auth_failure(self):
        """恢复认证失败"""
        print("🔐 恢复认证失败")
        self.control_plane.recover_auth_failure()

    async def _recover_rate_limiting(self):
        """恢复限流"""
        print("⏱️  恢复限流")
        self.control_plane.recover_rate_limiting()

    def _get_severity_weight(self, severity: FaultSeverity) -> int:
        """获取故障严重程度权重"""
        weights = {FaultSeverity.LOW: 1, FaultSeverity.MEDIUM: 2, FaultSeverity.HIGH: 3, FaultSeverity.CRITICAL: 4}
        return weights.get(severity, 1)

    def _assess_customer_impact(
        self, config: FaultInjectionConfig, before_metrics: Dict[str, Any], after_metrics: Dict[str, Any]
    ) -> str:
        """评估客户影响"""
        # 基于指标变化评估影响
        response_time_change = after_metrics.get("avg_response_time", 0) - before_metrics.get("avg_response_time", 0)
        error_rate_change = after_metrics.get("error_rate", 0) - before_metrics.get("error_rate", 0)

        if config.severity == FaultSeverity.CRITICAL:
            return "critical"
        elif config.severity == FaultSeverity.HIGH:
            return "high" if error_rate_change > 0.1 or response_time_change > 1000 else "medium"
        elif config.severity == FaultSeverity.MEDIUM:
            return "medium" if error_rate_change > 0.05 or response_time_change > 500 else "low"
        else:
            return "low"

    def _update_average_recovery_time(self, recovery_time: float):
        """更新平均恢复时间"""
        current_avg = self.stats["average_recovery_time"]
        successful_count = self.stats["successful_faults"]

        if successful_count == 1:
            self.stats["average_recovery_time"] = recovery_time
        else:
            self.stats["average_recovery_time"] = (
                current_avg * (successful_count - 1) + recovery_time
            ) / successful_count

    def _generate_fault_injection_report(self, results: List[FaultInjectionResult]) -> str:
        """生成故障注入测试报告"""
        report_path = f"/tmp/fault_injection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            "test_summary": {
                "total_faults": len(results),
                "successful_faults": len([r for r in results if r.success]),
                "failed_faults": len([r for r in results if not r.success]),
                "test_duration_seconds": (
                    max([(r.end_time - r.start_time).total_seconds() for r in results if r.end_time]) if results else 0
                ),
            },
            "fault_details": [],
            "recovery_analysis": {
                "average_recovery_time": self.stats["average_recovery_time"],
                "fastest_recovery": (
                    min([r.recovery_time_seconds for r in results if r.recovery_time_seconds])
                    if any(r.recovery_time_seconds for r in results)
                    else 0
                ),
                "slowest_recovery": (
                    max([r.recovery_time_seconds for r in results if r.recovery_time_seconds])
                    if any(r.recovery_time_seconds for r in results)
                    else 0
                ),
            },
            "resilience_assessment": self._calculate_resilience_score(results),
            "recommendations": self._generate_fault_injection_recommendations(results),
        }

        # 添加详细的故障信息
        for result in results:
            report["fault_details"].append(
                {
                    "fault_id": result.fault_id,
                    "fault_type": result.fault_type.value,
                    "severity": result.severity.value if hasattr(result, "severity") else "unknown",
                    "success": result.success,
                    "duration_seconds": result.duration_seconds,
                    "recovery_time_seconds": result.recovery_time_seconds,
                    "customer_impact": result.customer_impact,
                    "error_message": result.error_message,
                }
            )

        # 保存报告
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # 更新系统弹性评分
        self.stats["system_resilience_score"] = report["resilience_assessment"]["overall_score"]

        return report_path

    def _calculate_resilience_score(self, results: List[FaultInjectionResult]) -> Dict[str, Any]:
        """计算系统弹性评分"""
        successful_faults = len([r for r in results if r.success])
        total_faults = len(results)

        if total_faults == 0:
            return {"overall_score": 0, "reliability": 0, "recovery_speed": 0, "stability": 0}

        # 可靠性评分
        reliability = (successful_faults / total_faults) * 100

        # 恢复速度评分
        recovery_times = [r.recovery_time_seconds for r in results if r.recovery_time_seconds]
        if recovery_times:
            avg_recovery = sum(recovery_times) / len(recovery_times)
            recovery_speed = max(0, 100 - (avg_recovery / 10))  # 恢复时间越短分数越高
        else:
            recovery_speed = 0

        # 稳定性评分（基于故障持续时间）
        durations = [r.duration_seconds for r in results if r.duration_seconds]
        if durations:
            avg_duration = sum(durations) / len(durations)
            stability = max(0, 100 - (avg_duration / 100))  # 故障持续时间越短分数越高
        else:
            stability = 0

        # 总体评分
        overall_score = round((reliability + recovery_speed + stability) / 3, 2)

        return {
            "overall_score": overall_score,
            "reliability": round(reliability, 2),
            "recovery_speed": round(recovery_speed, 2),
            "stability": round(stability, 2),
        }

    def _generate_fault_injection_recommendations(self, results: List[FaultInjectionResult]) -> List[str]:
        """生成故障注入测试建议"""
        recommendations = []

        # 分析失败的故障
        failed_faults = [r for r in results if not r.success]
        if failed_faults:
            recommendations.append(f"有 {len(failed_faults)} 个故障注入失败，需要改进故障注入机制")

        # 分析恢复时间
        slow_recovery_faults = [r for r in results if r.recovery_time_seconds and r.recovery_time_seconds > 30]
        if slow_recovery_faults:
            recommendations.append(f"有 {len(slow_recovery_faults)} 个故障恢复时间较长（>30秒），需要优化恢复机制")

        # 分析客户影响
        critical_impact_faults = [r for r in results if r.customer_impact == "critical"]
        if critical_impact_faults:
            recommendations.append(f"有 {len(critical_impact_faults)} 个故障对客户造成严重影响，需要优先处理")

        # 分析故障类型
        fault_type_counts = defaultdict(int)
        for result in results:
            fault_type_counts[result.fault_type.value] += 1

        # 找出最常见的故障类型
        if fault_type_counts:
            most_common_fault = max(fault_type_counts, key=fault_type_counts.get)
            if fault_type_counts[most_common_fault] > len(results) * 0.3:
                recommendations.append(f"故障类型 {most_common_fault} 出现频率过高，需要重点优化")

        # 通用建议
        if not recommendations:
            recommendations.append("系统在故障注入测试中表现良好，建议继续监控生产环境")
        else:
            recommendations.append("建议定期运行故障注入测试，持续改进系统弹性")

        return recommendations


class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self.process = psutil.Process()
        self.network_stats = psutil.net_io_counters()

    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            # CPU指标
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # 内存指标
            memory = psutil.virtual_memory()

            # 磁盘指标
            disk = psutil.disk_usage("/")

            # 网络指标
            network = psutil.net_io_counters()

            # 进程指标
            process_memory = self.process.memory_info()
            process_cpu = self.process.cpu_percent()

            # 应用程序指标（模拟）
            app_metrics = {
                "avg_response_time": random.uniform(50, 500),
                "error_rate": random.uniform(0, 0.05),
                "active_connections": random.randint(10, 100),
                "request_count": random.randint(100, 1000),
            }

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {"percent": cpu_percent, "count": cpu_count, "process_percent": process_cpu},
                "memory": {
                    "total_mb": memory.total / 1024 / 1024,
                    "available_mb": memory.available / 1024 / 1024,
                    "percent": memory.percent,
                    "used_mb": memory.used / 1024 / 1024,
                    "process_rss_mb": process_memory.rss / 1024 / 1024,
                },
                "disk": {
                    "total_gb": disk.total / 1024 / 1024 / 1024,
                    "used_gb": disk.used / 1024 / 1024 / 1024,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                    "percent": disk.percent,
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                },
                "application": app_metrics,
            }

        except Exception as e:
            print(f"⚠️  指标收集失败: {str(e)}")
            return {}


class RecoveryMonitor:
    """恢复监控器"""

    def __init__(self):
        self.recovery_events = []
        self.health_checks = {}

    async def monitor_recovery(self, fault_id: str, recovery_start: datetime):
        """监控恢复过程"""
        start_time = datetime.now()

        while True:
            # 检查系统健康状态
            health_status = await self._check_system_health()

            self.recovery_events.append(
                {
                    "fault_id": fault_id,
                    "timestamp": datetime.now().isoformat(),
                    "health_status": health_status,
                    "recovery_duration": (datetime.now() - start_time).total_seconds(),
                }
            )

            if health_status == "healthy":
                print("    ✅ 系统已恢复正常")
                break

            await asyncio.sleep(2)  # 每2秒检查一次

    async def _check_system_health(self) -> str:
        """检查系统健康状态"""
        try:
            # 模拟健康检查
            response = await asyncio.sleep(0.1)  # 模拟API调用
            return "healthy"
        except:
            return "recovering"


class ControlPlane:
    """控制平面 - 用于协调故障注入和恢复"""

    def __init__(self):
        self.delay_handlers = []
        self.packet_loss_handlers = []
        self.fault_active = False

    async def inject_fault(self, config: FaultInjectionConfig):
        """通用故障注入方法"""
        print(f"    🎛️  控制平面注入故障: {config.fault_type.value}")
        self.fault_active = True

    async def recover_fault(self, config: FaultInjectionConfig):
        """通用故障恢复方法"""
        print(f"    🎛️  控制平面恢复故障: {config.fault_type.value}")
        self.fault_active = False

    async def simulate_network_partition(self, duration: int):
        """模拟网络分区"""
        print(f"    🔗 控制平面: 模拟网络分区 {duration} 秒")
        # 实际实现中会使用网络隔离技术

    async def simulate_database_timeout(self, timeout: int):
        """模拟数据库超时"""
        print(f"    🗄️  控制平面: 模拟数据库超时 {timeout} 秒")
        # 实际实现中会使用数据库代理或修改连接池配置

    async def simulate_api_error(self, error_code: int, error_rate: float):
        """模拟API错误"""
        print(f"    🚫 控制平面: 模拟API错误 {error_code} (错误率: {error_rate * 100}%)")
        # 实际实现中会使用API网关或负载均衡器

    async def simulate_memory_pressure(self, memory_mb: int):
        """模拟内存压力"""
        print(f"    💾 控制平面: 模拟内存压力 {memory_mb}MB")
        # 实际实现中会分配内存或修改JVM/GC配置

    async def simulate_cpu_pressure(self, cpu_percent: int):
        """模拟CPU压力"""
        print(f"    ⚡ 控制平面: 模拟CPU压力 {cpu_percent}%")
        # 实际实现中会使用CPU密集型任务

    # 注册处理器方法
    def register_delay_handler(self, handler):
        """注册延迟处理器"""
        self.delay_handlers.append(handler)

    def register_packet_loss_handler(self, handler):
        """注册丢包处理器"""
        self.packet_loss_handlers.append(handler)

    def unregister_delay_handler(self):
        """注销延迟处理器"""
        self.delay_handlers.clear()

    def unregister_packet_loss_handler(self):
        """注销丢包处理器"""
        self.packet_loss_handlers.clear()


class FaultGenerator:
    """故障生成器 - 用于生成随机故障场景"""

    def __init__(self):
        self.fault_templates = [
            {"type": FaultType.NETWORK_DELAY, "severity": FaultSeverity.MEDIUM, "parameters": {"delay_ms": 1000}},
            {"type": FaultType.NETWORK_PACKET_LOSS, "severity": FaultSeverity.MEDIUM, "parameters": {"loss_rate": 0.1}},
            {"type": FaultType.DATABASE_TIMEOUT, "severity": FaultSeverity.HIGH, "parameters": {"timeout_seconds": 5}},
            {
                "type": FaultType.API_ERROR,
                "severity": FaultSeverity.MEDIUM,
                "parameters": {"error_code": 500, "error_rate": 0.2},
            },
            {
                "type": FaultType.MEMORY_PRESSURE,
                "severity": FaultSeverity.HIGH,
                "parameters": {"memory_usage_mb": 2048},
            },
        ]

    def generate_random_fault(self) -> FaultInjectionConfig:
        """生成随机故障配置"""
        template = random.choice(self.fault_templates)

        return FaultInjectionConfig(
            fault_type=template["type"],
            severity=template["severity"],
            parameters=template["parameters"],
            duration_seconds=random.randint(10, 60),
            recovery_time_seconds=random.randint(5, 20),
        )

    def generate_chaos_scenario(self, fault_count: int = 5) -> List[FaultInjectionConfig]:
        """生成混沌工程测试场景"""
        configs = []

        for i in range(fault_count):
            fault = self.generate_random_fault()
            # 增加故障持续时间
            fault.duration_seconds = random.randint(30, 120)
            configs.append(fault)

        return configs


# 使用示例和pytest集成
def demo_fault_injection():
    """演示故障注入系统功能"""
    print("🎭 演示故障注入系统功能")

    # 创建故障注入器
    injector = FaultInjector()

    # 配置故障类型
    configs = [
        FaultInjectionConfig(
            fault_type=FaultType.NETWORK_DELAY,
            severity=FaultSeverity.MEDIUM,
            parameters={"delay_ms": 500},
            duration_seconds=30,
        ),
        FaultInjectionConfig(
            fault_type=FaultType.DATABASE_TIMEOUT,
            severity=FaultSeverity.HIGH,
            parameters={"timeout_seconds": 3},
            duration_seconds=20,
        ),
        FaultInjectionConfig(
            fault_type=FaultType.API_ERROR,
            severity=FaultSeverity.MEDIUM,
            parameters={"error_code": 500, "error_rate": 0.3},
            duration_seconds=15,
        ),
        FaultInjectionConfig(
            fault_type=FaultType.MEMORY_PRESSURE,
            severity=FaultSeverity.HIGH,
            parameters={"memory_usage_mb": 1024},
            duration_seconds=25,
        ),
    ]

    # 添加配置
    for config in configs:
        injector.add_fault_config(config)

    # 运行故障注入测试
    asyncio.run(injector.run_comprehensive_fault_injection())


# pytest测试用例
@pytest.mark.chaos
@pytest.mark.fault_injection
async def test_fault_injection_basic():
    """基本故障注入测试"""
    injector = FaultInjector()

    # 添加一个简单故障配置
    config = FaultInjectionConfig(
        fault_type=FaultType.NETWORK_DELAY, severity=FaultSeverity.LOW, parameters={"delay_ms": 100}, duration_seconds=5
    )

    injector.add_fault_config(config)

    # 运行测试
    results = await injector.run_comprehensive_fault_injection()

    # 验证结果
    assert results is not None
    assert len(injector.fault_results) > 0


@pytest.mark.chaos
@pytest.mark.fault_injection
async def test_fault_injection_recovery():
    """故障恢复测试"""
    injector = FaultInjector()

    # 配置故障
    config = FaultInjectionConfig(
        fault_type=FaultType.API_ERROR,
        severity=FaultSeverity.MEDIUM,
        parameters={"error_code": 500, "error_rate": 0.5},
        duration_seconds=10,
    )

    injector.add_fault_config(config)

    # 运行测试
    results = await injector.run_comprehensive_fault_injection()

    # 验证恢复
    assert results is not None
    for result in injector.fault_results.values():
        assert result.recovery_time_seconds is not None
        assert result.recovery_time_seconds > 0


@pytest.mark.chaos
@pytest.mark.fault_injection
async def test_fault_generator_random():
    """随机故障生成器测试"""
    generator = FaultGenerator()

    # 生成随机故障
    config = generator.generate_random_fault()

    # 验证配置
    assert config.fault_type in FaultType
    assert config.severity in FaultSeverity
    assert config.duration_seconds > 0
    assert config.recovery_time_seconds > 0


@pytest.mark.chaos
@pytest.mark.fault_injection
async def test_chaos_scenario_generation():
    """混沌工程场景生成测试"""
    generator = FaultGenerator()

    # 生成混沌场景
    scenario = generator.generate_chaos_scenario(fault_count=3)

    # 验证场景
    assert len(scenario) == 3
    for config in scenario:
        assert config.fault_type in FaultType
        assert config.severity in FaultSeverity


if __name__ == "__main__":
    # 运行演示
    demo_fault_injection()
