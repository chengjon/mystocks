#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 负载测试生成器

提供专业的负载测试功能，包括负载曲线生成、并发控制、性能监控等
"""

import asyncio
import time
import random
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import aiohttp
import psutil
import numpy as np

from tests.config.test_config import test_env


class LoadTestType(Enum):
    """负载测试类型"""

    CONSTANT = "constant"  # 恒定负载
    RAMP_UP = "ramp_up"  # 递增负载
    SPIKE = "spike"  # 峰值负载
    RANDOM = "random"  # 随机负载
    WAVE = "wave"  # 波浪负载


@dataclass
class LoadTestConfig:
    """负载测试配置"""

    test_type: LoadTestType = LoadTestType.RAMP_UP
    target_users: int = 100
    duration_minutes: int = 5
    ramp_up_time: int = 60
    think_time: float = 1.0
    error_threshold: float = 0.05  # 5%错误率阈值
    response_time_threshold: float = 5.0  # 5秒响应时间

    # 用户行为配置
    user_actions: List[Dict[str, Any]] = None
    user_think_times: List[float] = None

    # 系统监控配置
    monitor_interval: int = 5
    enable_system_monitoring: bool = True

    def __post_init__(self):
        if self.user_actions is None:
            self.user_actions = [
                {
                    "name": "browse_market",
                    "weight": 30,
                    "endpoint": "/api/market/market-data/fetch",
                    "params": {"symbol": "600519"},
                },
                {
                    "name": "view_stock",
                    "weight": 40,
                    "endpoint": "/api/market/quote/fetch",
                    "params": {"symbols": ["600519"]},
                },
                {
                    "name": "get_kline",
                    "weight": 20,
                    "endpoint": "/api/market/kline/fetch",
                    "params": {"symbol": "600519", "period": "daily"},
                },
                {
                    "name": "get_index",
                    "weight": 10,
                    "endpoint": "/api/market/index/fetch",
                    "params": {"index_code": "399300"},
                },
            ]

        if self.user_think_times is None:
            self.user_think_times = [0.5, 1.0, 1.5, 2.0]


class LoadGenerator:
    """负载生成器主类"""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.base_url = test_env.API_BASE_URL
        self.session_pool = aiohttp.ClientSession()
        self.results = []
        self.system_metrics = []
        self.test_start_time = None
        self.test_end_time = None

        # 系统监控
        if config.enable_system_monitoring:
            self.system_monitor = SystemMonitor()

    async def run_load_test(self) -> Dict[str, Any]:
        """运行完整的负载测试"""
        print("\n🚀 开始负载测试")
        print(f"⏱️  测试类型: {self.config.test_type.value}")
        print(f"👥 目标用户数: {self.config.target_users}")
        print(f"⏳ 测试时长: {self.config.duration_minutes} 分钟")

        self.test_start_time = datetime.now()

        try:
            # 初始化测试
            await self._initialize_test()

            # 开始系统监控
            if self.config.enable_system_monitoring:
                monitor_task = asyncio.create_task(self._run_system_monitor())

            # 根据测试类型生成负载
            if self.config.test_type == LoadTestType.CONSTANT:
                await self._run_constant_load()
            elif self.config.test_type == LoadTestType.RAMP_UP:
                await self._run_ramp_up_load()
            elif self.config.test_type == LoadTestType.SPIKE:
                await self._run_spike_load()
            elif self.config.test_type == LoadTestType.RANDOM:
                await self._run_random_load()
            elif self.config.test_type == LoadTestType.WAVE:
                await self._run_wave_load()

            # 停止系统监控
            if self.config.enable_system_monitoring:
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass

            # 等待所有用户完成
            await self._wait_for_completion()

        except Exception as e:
            print(f"❌ 负载测试失败: {str(e)}")
            raise

        finally:
            self.test_end_time = datetime.now()
            await self._cleanup()

        # 生成测试报告
        report = self._generate_load_test_report()
        print("\n✅ 负载测试完成")
        print(f"📊 测试报告: {report}")

        return report

    async def _initialize_test(self):
        """初始化测试环境"""
        print("🔄 初始化测试环境...")

        # 预热连接
        await self._warmup_connections()

        # 初始化结果收集器
        self.results = []
        self.system_metrics = []

        # 创建用户任务池
        self.active_users = set()

    async def _warmup_connections(self):
        """预热HTTP连接"""
        print("  🔗 预热HTTP连接...")

        warmup_requests = 5
        for i in range(warmup_requests):
            try:
                async with self.session_pool.get(
                    f"{self.base_url}/api/market/quote/fetch",
                    params={"symbols": ["600519"]},
                ) as response:
                    await response.text()
                await asyncio.sleep(0.1)
            except:
                pass

    async def _run_constant_load(self):
        """运行恒定负载测试"""
        print("🔥 开始恒定负载测试...")

        start_time = time.time()
        end_time = start_time + (self.config.duration_minutes * 60)

        # 恒定数量的并发用户
        active_users = []

        for i in range(self.config.target_users):
            task = asyncio.create_task(self._simulate_user(f"user_{i}"))
            active_users.append(task)
            self.active_users.add(task)

        # 保持负载直到指定时长
        while time.time() < end_time:
            await asyncio.sleep(1)

        # 取消所有用户任务
        for task in active_users:
            task.cancel()

    async def _run_ramp_up_load(self):
        """运行递增负载测试"""
        print("📈 开始递增负载测试...")

        start_time = time.time()
        end_time = start_time + (self.config.duration_minutes * 60)
        ramp_end_time = start_time + self.config.ramp_up_time

        users_per_batch = max(1, self.config.target_users // 10)

        while time.time() < end_time:
            current_time = time.time()

            if current_time < ramp_end_time:
                # 递增阶段
                progress = (current_time - start_time) / self.config.ramp_up_time
                current_users = int(progress * self.config.target_users)

                # 批量启动用户
                if len(self.active_users) < current_users:
                    new_users = current_users - len(self.active_users)
                    for i in range(new_users):
                        task = asyncio.create_task(self._simulate_user(f"user_ramp_{i}"))
                        self.active_users.add(task)

            else:
                # 恒定负载阶段
                if len(self.active_users) < self.config.target_users:
                    missing_users = self.config.target_users - len(self.active_users)
                    for i in range(missing_users):
                        task = asyncio.create_task(self._simulate_user(f"user_const_{i}"))
                        self.active_users.add(task)

            await asyncio.sleep(1)

        # 取消所有用户任务
        for task in list(self.active_users):
            task.cancel()

    async def _run_spike_load(self):
        """运行峰值负载测试"""
        print("⚡ 开始峰值负载测试...")

        start_time = time.time()
        spike_duration = 30  # 30秒峰值
        recovery_time = 60  # 60秒恢复

        for cycle in range(3):  # 3个峰值周期
            print(f"  🔥 峰值周期 {cycle + 1}/3")

            # 峰值阶段
            for i in range(self.config.target_users):
                task = asyncio.create_task(self._simulate_user(f"user_spike_{i}_{cycle}"))
                self.active_users.add(task)

            await asyncio.sleep(spike_duration)

            # 停止峰值
            for task in list(self.active_users):
                task.cancel()

            self.active_users.clear()

            # 恢复时间
            await asyncio.sleep(recovery_time)

    async def _run_random_load(self):
        """运行随机负载测试"""
        print("🎲 开始随机负载测试...")

        start_time = time.time()
        end_time = start_time + (self.config.duration_minutes * 60)

        while time.time() < end_time:
            # 随机生成用户数量
            current_users = random.randint(10, self.config.target_users)

            # 随机创建用户
            for i in range(current_users):
                if len(self.active_users) < current_users:
                    task = asyncio.create_task(self._simulate_user(f"user_random_{i}"))
                    self.active_users.add(task)

            await asyncio.sleep(2)  # 每2秒调整一次

            # 随机停止部分用户
            if len(self.active_users) > current_users // 2:
                to_stop = random.randint(1, len(self.active_users) // 2)
                for _ in range(to_stop):
                    if self.active_users:
                        task = self.active_users.pop()
                        task.cancel()

    async def _run_wave_load(self):
        """运行波浪负载测试"""
        print("🌊 开始波浪负载测试...")

        start_time = time.time()
        end_time = start_time + (self.config.duration_minutes * 60)
        wave_period = 60  # 60秒一个波浪周期

        while time.time() < end_time:
            current_time = time.time() - start_time

            # 计算当前波浪位置 (0-1)
            wave_position = (current_time % wave_period) / wave_period

            # 正弦波负载模式
            load_factor = 0.5 + 0.5 * np.sin(2 * np.pi * wave_position)
            current_users = int(load_factor * self.config.target_users)

            # 调整用户数量
            if len(self.active_users) < current_users:
                new_users = current_users - len(self.active_users)
                for i in range(new_users):
                    task = asyncio.create_task(self._simulate_user(f"user_wave_{i}"))
                    self.active_users.add(task)
            elif len(self.active_users) > current_users:
                to_stop = len(self.active_users) - current_users
                for _ in range(to_stop):
                    if self.active_users:
                        task = self.active_users.pop()
                        task.cancel()

            await asyncio.sleep(2)

    async def _simulate_user(self, user_id: str):
        """模拟单个用户行为"""
        user_start_time = time.time()

        try:
            while True:
                # 选择用户动作
                action = self._select_user_action()

                # 执行动作
                result = await self._execute_user_action(action, user_id)

                # 记录结果
                self.results.append(
                    {
                        "user_id": user_id,
                        "timestamp": datetime.now().isoformat(),
                        "action": action["name"],
                        **result,
                    }
                )

                # 思考时间
                think_time = random.choice(self.config.user_think_times)
                await asyncio.sleep(think_time)

        except asyncio.CancelledError:
            # 用户被正常停止
            pass
        except Exception as e:
            # 记录错误
            self.results.append(
                {
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "action": "error",
                    "status": "failed",
                    "error": str(e),
                }
            )
        finally:
            # 清理用户
            if user_id in self.active_users:
                self.active_users.remove(user_id)

            # 记录用户总时长
            user_duration = time.time() - user_start_time
            self.results.append(
                {
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "action": "completed",
                    "duration_ms": round(user_duration * 1000, 2),
                }
            )

    def _select_user_action(self) -> Dict[str, Any]:
        """根据权重选择用户动作"""
        actions_with_weights = [(action, action["weight"]) for action in self.config.user_actions]
        total_weight = sum(weight for _, weight in actions_with_weights)

        rand = random.uniform(0, total_weight)
        current_weight = 0

        for action, weight in actions_with_weights:
            current_weight += weight
            if rand <= current_weight:
                return action

        return actions_with_weights[0][0]  # 默认返回第一个动作

    async def _execute_user_action(self, action: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """执行用户动作"""
        start_time = time.time()
        success = False
        error_msg = None

        try:
            # 构造请求参数
            params = action["params"].copy()
            params["_user_id"] = user_id  # 添加用户标识

            # 发起请求
            async with self.session_pool.get(
                f"{self.base_url}{action['endpoint']}",
                params=params,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 200:
                    response_text = await response.text()
                    response_size = len(response_text)

                    success = True
                    status_code = response.status
                else:
                    status_code = response.status
                    error_msg = f"HTTP {status_code}"

        except Exception as e:
            status_code = -1
            error_msg = str(e)

        # 计算性能指标
        end_time = time.time()
        response_time = (end_time - start_time) * 1000

        return {
            "status": "success" if success else "failed",
            "response_time_ms": round(response_time, 2),
            "status_code": status_code,
            "error": error_msg,
            "endpoint": action["endpoint"],
        }

    async def _wait_for_completion(self):
        """等待所有用户完成"""
        print("⏳ 等待所有用户完成...")

        while self.active_users:
            await asyncio.sleep(1)

    async def _cleanup(self):
        """清理资源"""
        await self.session_pool.close()

    async def _run_system_monitor(self):
        """运行系统监控"""
        print("📊 开始系统监控...")

        while True:
            try:
                # 收集系统指标
                metrics = self._collect_system_metrics()
                self.system_metrics.append({"timestamp": datetime.now().isoformat(), **metrics})

                await asyncio.sleep(self.config.monitor_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  系统监控错误: {str(e)}")
                await asyncio.sleep(5)

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统性能指标"""
        process = psutil.Process()

        # CPU指标
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()

        # 内存指标
        memory_info = process.memory_info()
        virtual_memory = psutil.virtual_memory()

        # 网络指标
        network_io = psutil.net_io_counters()

        # 磁盘I/O
        disk_io = psutil.disk_io_counters()

        return {
            "cpu_percent": cpu_percent,
            "cpu_freq_mhz": cpu_freq.current if cpu_freq else 0,
            "memory_rss_mb": memory_info.rss / 1024 / 1024,
            "memory_vms_mb": memory_info.vms / 1024 / 1024,
            "memory_percent": virtual_memory.percent,
            "network_bytes_sent": network_io.bytes_sent,
            "network_bytes_recv": network_io.bytes_recv,
            "disk_read_bytes": disk_io.read_bytes if disk_io else 0,
            "disk_write_bytes": disk_io.write_bytes if disk_io else 0,
        }

    def _generate_load_test_report(self) -> str:
        """生成负载测试报告"""
        total_duration = (self.test_end_time - self.test_start_time).total_seconds()

        # 分析结果
        successful_requests = [r for r in self.results if r.get("status") == "success"]
        failed_requests = [r for r in self.results if r.get("status") == "failed"]

        # 计算统计指标
        if successful_requests:
            response_times = [r["response_time_ms"] for r in successful_requests if "response_time_ms" in r]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
        else:
            avg_response_time = max_response_time = min_response_time = 0

        # 计算TPS
        total_requests = len(successful_requests)
        tps = total_requests / total_duration if total_duration > 0 else 0

        # 计算错误率
        error_rate = (
            len(failed_requests) / (len(successful_requests) + len(failed_requests))
            if (len(successful_requests) + len(failed_requests)) > 0
            else 0
        )

        # 生成报告
        report_data = {
            "test_summary": {
                "test_type": self.config.test_type.value,
                "target_users": self.config.target_users,
                "duration_seconds": round(total_duration, 2),
                "start_time": self.test_start_time.isoformat(),
                "end_time": self.test_end_time.isoformat(),
                "total_requests": total_requests,
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
            },
            "performance_metrics": {
                "tps": round(tps, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
                "min_response_time_ms": round(min_response_time, 2),
                "error_rate_percent": round(error_rate * 100, 2),
            },
            "system_metrics": self.system_metrics,
            "threshold_check": {
                "response_time_ok": avg_response_time <= self.config.response_time_threshold * 1000,
                "error_rate_ok": error_rate <= self.config.error_threshold,
            },
            "recommendations": self._generate_load_test_recommendations(avg_response_time, error_rate, tps),
        }

        # 保存报告
        report_path = f"/tmp/load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        return report_path

    def _generate_load_test_recommendations(self, avg_response_time: float, error_rate: float, tps: float) -> List[str]:
        """生成负载测试优化建议"""
        recommendations = []

        # 响应时间建议
        if avg_response_time > self.config.response_time_threshold * 1000:
            recommendations.append(
                f"平均响应时间 {avg_response_time:.0f}ms 超过阈值 {self.config.response_time_threshold * 1000}ms，建议优化性能"
            )

        # 错误率建议
        if error_rate > self.config.error_threshold:
            recommendations.append(
                f"错误率 {error_rate * 100:.1f}% 超过阈值 {self.config.error_threshold * 100}%，需要检查系统稳定性"
            )

        # TPS建议
        if tps < 10:
            recommendations.append(f"TPS较低 ({tps:.1f})，建议增加服务器资源或优化代码")

        # 系统资源建议
        if self.system_metrics:
            avg_cpu = sum(m["cpu_percent"] for m in self.system_metrics) / len(self.system_metrics)
            if avg_cpu > 80:
                recommendations.append(f"平均CPU使用率 {avg_cpu:.1f}% 较高，考虑扩容或优化性能")

        return recommendations


class SystemMonitor:
    """系统监控器"""

    def __init__(self, monitor_interval: int = 5):
        self.monitor_interval = monitor_interval
        self.metrics_history = []

    async def monitor(self, duration_minutes: int) -> List[Dict[str, Any]]:
        """监控系统性能"""
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        while time.time() < end_time:
            metrics = self._collect_metrics()
            self.metrics_history.append(metrics)

            await asyncio.sleep(self.monitor_interval)

        return self.metrics_history

    def _collect_metrics(self) -> Dict[str, Any]:
        """收集当前性能指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_io_read": psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
            "disk_io_write": psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
            "network_io_sent": psutil.net_io_counters().bytes_sent,
            "network_io_recv": psutil.net_io_counters().bytes_recv,
        }


# Pytest测试用例
@pytest.mark.performance
async def test_constant_load():
    """恒定负载测试"""
    config = LoadTestConfig(test_type=LoadTestType.CONSTANT, target_users=50, duration_minutes=1)

    generator = LoadGenerator(config)
    report = await generator.run_load_test()

    # 验证测试结果
    assert generator.results
    assert "performance_metrics" in generator.results

    print(f"📊 恒定负载测试报告: {report}")


@pytest.mark.performance
async def test_ramp_up_load():
    """递增负载测试"""
    config = LoadTestConfig(
        test_type=LoadTestType.RAMP_UP,
        target_users=100,
        duration_minutes=2,
        ramp_up_time=30,
    )

    generator = LoadGenerator(config)
    report = await generator.run_load_test()

    # 验证测试结果
    assert generator.results
    assert len(generator.results) > 0

    print(f"📊 递增负载测试报告: {report}")


@pytest.mark.performance
async def test_spike_load():
    """峰值负载测试"""
    config = LoadTestConfig(test_type=LoadTestType.SPIKE, target_users=200, duration_minutes=3)

    generator = LoadGenerator(config)
    report = await generator.run_load_test()

    # 验证测试结果
    assert generator.results
    assert len(generator.results) > 0

    print(f"📊 峰值负载测试报告: {report}")


@pytest.mark.performance
async def test_wave_load():
    """波浪负载测试"""
    config = LoadTestConfig(test_type=LoadTestType.WAVE, target_users=80, duration_minutes=2)

    generator = LoadGenerator(config)
    report = await generator.run_load_test()

    # 验证测试结果
    assert generator.results
    assert len(generator.results) > 0

    print(f"📊 波浪负载测试报告: {report}")


if __name__ == "__main__":
    # 运行负载测试示例
    async def main():
        # 配置递增负载测试
        config = LoadTestConfig(
            test_type=LoadTestType.RAMP_UP,
            target_users=100,
            duration_minutes=2,
            ramp_up_time=60,
        )

        generator = LoadGenerator(config)
        report = await generator.run_load_test()
        print(f"\n🎯 负载测试报告已保存到: {report}")

    # 运行测试
    import asyncio

    asyncio.run(main())
