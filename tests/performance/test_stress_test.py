#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 压力测试套件

提供高强度的压力测试功能，用于测试系统的极限承载能力
"""

import asyncio
import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

import aiohttp
import psutil

from tests.config.test_config import test_env
from tests.performance._stress_test_runtime_tail import (
    SystemMonitor,
    run_stress_test_example,
)
from tests.performance._stress_test_tail import StressTestSuiteTailMixin


class StressTestType(Enum):
    """压力测试类型"""

    GRADUAL = "gradual"  # 逐步增加负载
    BURST = "burst"  # 突发压力
    EXTREME = "extreme"  # 极限压力
    MEMORY = "memory"  # 内存压力
    CPU = "cpu"  # CPU压力


@dataclass
class StressTestConfig:
    """压力测试配置"""

    test_type: StressTestType = StressTestType.GRADUAL
    initial_users: int = 10
    max_users: int = 1000
    increment_rate: int = 50  # 每次增加的用户数
    increment_interval: int = 30  # 增加间隔（秒）
    max_duration_minutes: int = 30
    failure_threshold: float = 0.3  # 30%失败率阈值
    response_time_threshold: float = 10.0  # 10秒响应时间阈值

    # 监控配置
    monitor_interval: int = 5
    enable_system_monitoring: bool = True

    # 超时配置
    request_timeout: float = 30.0
    connection_timeout: float = 10.0

    # 断路器配置
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 100  # 连续错误数阈值


class StressTestResult:
    """压力测试结果"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.error_messages = []
        self.system_metrics = []
        self.breaking_point = None
        self.recovery_point = None


class CircuitBreaker:
    """断路器模式"""

    def __init__(self, threshold: int = 100, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
        self.lock = threading.Lock()

    def record_failure(self):
        """记录失败"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.threshold:
                self.state = "open"
                print(f"🚫 断路器开启 - 失败次数: {self.failure_count}")

    def record_success(self):
        """记录成功"""
        with self.lock:
            if self.failure_count > 0:
                self.failure_count = max(0, self.failure_count - 5)  # 减少失败计数

            if self.state == "half_open" and self.failure_count == 0:
                self.state = "closed"

    def allow_request(self) -> bool:
        """是否允许请求"""
        with self.lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "half_open"
                    print("🔄 断路器半开状态")
                    return True
                return False

            return True

    def reset(self):
        """重置断路器"""
        with self.lock:
            self.failure_count = 0
            self.state = "closed"


class StressTestSuite(StressTestSuiteTailMixin):
    """压力测试套件"""

    def __init__(self, config: StressTestConfig):
        self.config = config
        self.base_url = test_env.API_BASE_URL
        self.result = StressTestResult()
        self.active_users = []
        self.user_tasks = []
        self.stop_event = threading.Event()

        # 断路器
        self.circuit_breaker = (
            CircuitBreaker(threshold=config.circuit_breaker_threshold) if config.enable_circuit_breaker else None
        )

        # 系统监控
        if config.enable_system_monitoring:
            self.system_monitor = SystemMonitor()

    async def run_stress_test(self) -> Dict[str, Any]:
        """运行压力测试"""
        print("\n🚀 开始压力测试")
        print(f"⚡ 测试类型: {self.config.test_type.value}")
        print(f"🔥 最大用户数: {self.config.max_users}")
        print(f"📈 初始用户数: {self.config.initial_users}")

        self.result.start_time = datetime.now()

        try:
            # 初始化测试
            await self._initialize_test()

            # 根据测试类型执行压力测试
            if self.config.test_type == StressTestType.GRADUAL:
                await self._run_gradual_stress_test()
            elif self.config.test_type == StressTestType.BURST:
                await self._run_burst_stress_test()
            elif self.config.test_type == StressTestType.EXTREME:
                await self._run_extreme_stress_test()
            elif self.config.test_type == StressTestType.MEMORY:
                await self._run_memory_stress_test()
            elif self.config.test_type == StressTestType.CPU:
                await self._run_cpu_stress_test()

        except KeyboardInterrupt:
            print("\n⏹️  手动停止压力测试")
        except Exception as e:
            print(f"❌ 压力测试失败: {str(e)}")
            raise
        finally:
            self.stop_event.set()
            self.result.end_time = datetime.now()
            await self._cleanup()

        # 生成压力测试报告
        report = self._generate_stress_test_report()
        print("\n✅ 压力测试完成")
        print(f"📊 压力测试报告: {report}")

        return report

    async def _initialize_test(self):
        """初始化测试环境"""
        print("🔄 初始化测试环境...")

        # 预热连接
        await self._warmup_connections()

        # 重置结果
        self.result = StressTestResult()
        self.active_users = []
        self.user_tasks = []

        # 创建HTTP会话池
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(
                total=self.config.request_timeout,
                connect=self.config.connection_timeout,
            )
        )

    async def _warmup_connections(self):
        """预热连接"""
        print("  🔗 预热HTTP连接...")

        warmup_requests = 10
        for i in range(warmup_requests):
            try:
                async with self.session.get(
                    f"{self.base_url}/api/market/quote/fetch",
                    params={"symbols": ["600519"]},
                ) as response:
                    await response.text()
                await asyncio.sleep(0.1)
            except Exception:
                pass

    async def _run_gradual_stress_test(self):
        """运行逐步增加的压力测试"""
        print("📈 开始逐步增加压力测试...")

        current_users = self.config.initial_users
        start_time = time.time()
        end_time = start_time + (self.config.max_duration_minutes * 60)

        while not self.stop_event.is_set() and time.time() < end_time:
            # 检查是否达到断路器阈值
            if self._check_breaking_point():
                print(f"🚫 达到断点，当前用户数: {current_users}")
                self.result.breaking_point = current_users
                break

            # 检查系统状态
            if self._check_system_overload():
                print("⚠️  系统过载，停止增加用户")
                break

            # 增加用户
            print(f"👥 增加用户到 {current_users}")
            await self._add_users(current_users - len(self.active_users))

            # 持续运行
            await asyncio.sleep(self.config.increment_interval)

            # 增加用户数
            current_users = min(current_users + self.config.increment_rate, self.config.max_users)

        # 保持当前负载一段时间
        await asyncio.sleep(60)

        # 尝试恢复
        print("🔄 尝试系统恢复...")
        await self._gradual_decrease_users()
        if self.result.breaking_point:
            self.result.recovery_point = len(self.active_users)

    async def _run_burst_stress_test(self):
        """运行突发压力测试"""
        print("💥 开始突发压力测试...")

        burst_durations = [60, 30, 30]  # 三次突发压力
        recovery_times = [60, 45, 30]  # 恢复时间

        for burst_num, (burst_duration, recovery_time) in enumerate(zip(burst_durations, recovery_times), 1):
            print(f"\n💥 突发压力 #{burst_num}/{len(burst_durations)}")

            # 突发阶段
            target_users = min(self.config.max_users, burst_num * 200)
            await self._add_users(target_users)

            # 监控突发阶段
            burst_start = time.time()
            while time.time() - burst_start < burst_duration and not self.stop_event.is_set():
                await asyncio.sleep(5)
                if self._check_breaking_point():
                    print(f"🚫 突发压力 {burst_num} 达到断点")
                    break

            # 停止突发
            await self._remove_all_users()

            # 恢复时间
            print(f"💤 恢复中... {recovery_time}秒")
            await asyncio.sleep(recovery_time)

            # 检查系统是否已经恢复
            if self._check_system_recovered():
                print("✅ 系统已恢复")
            else:
                print("⚠️  系统未完全恢复")

    async def _run_extreme_stress_test(self):
        """运行极限压力测试"""
        print("🔥 开始极限压力测试...")

        # 快速达到最大用户数
        await self._add_users(self.config.max_users)

        # 监控极限状态
        monitor_task = asyncio.create_task(self._monitor_extreme_state())

        # 保持极限状态直到断点或超时
        start_time = time.time()
        timeout = self.config.max_duration_minutes * 60

        while not self.stop_event.is_set() and time.time() - start_time < timeout:
            if self._check_breaking_point():
                print(f"🚫 达到极限断点，用户数: {len(self.active_users)}")
                self.result.breaking_point = len(self.active_users)
                break

            await asyncio.sleep(10)

        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

    async def _run_memory_stress_test(self):
        """运行内存压力测试"""
        print("🧠 开始内存压力测试...")

        # 创建大量内存占用
        memory_intensive_tasks = []

        for i in range(50):  # 50个内存密集型任务
            task = asyncio.create_task(self._memory_intensive_operation(f"memory_task_{i}"))
            memory_intensive_tasks.append(task)

        # 同时运行压力测试
        stress_task = asyncio.create_task(self._run_concurrent_stress())

        # 等待其中一项失败
        done, pending = await asyncio.wait([stress_task, *memory_intensive_tasks], return_when=asyncio.FIRST_COMPLETED)

        # 取消所有任务
        for task in pending:
            task.cancel()

        # 清理内存
        del memory_intensive_tasks

    async def _memory_intensive_operation(self, task_id: str):
        """内存密集型操作"""
        large_data = []
        try:
            while not self.stop_event.is_set():
                # 创建大型数据结构
                data_chunk = {"id": task_id, "data": "x" * (1024 * 1024)}  # 1MB数据
                large_data.append(data_chunk)

                # 限制内存使用
                if len(large_data) > 100:
                    large_data.pop(0)

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            pass

    async def _run_cpu_stress_test(self):
        """运行CPU压力测试"""
        print("🖥️  开始CPU压力测试...")

        # 创建CPU密集型任务
        cpu_tasks = []
        for i in range(10):  # 10个CPU密集型任务
            task = asyncio.create_task(self._cpu_intensive_operation(f"cpu_task_{i}"))
            cpu_tasks.append(task)

        # 同时运行压力测试
        stress_task = asyncio.create_task(self._run_concurrent_stress())

        # 等待其中一项失败
        done, pending = await asyncio.wait([stress_task, *cpu_tasks], return_when=asyncio.FIRST_COMPLETED)

        # 取消所有任务
        for task in pending:
            task.cancel()

    async def _cpu_intensive_operation(self, task_id: str):
        """CPU密集型操作"""
        try:
            while not self.stop_event.is_set():
                # 复杂计算
                result = 0
                for i in range(100000):
                    result += i * i
                # 避免优化掉计算结果
                if result % 1000 == 0:
                    await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            pass

    async def _run_concurrent_stress(self):
        """并发压力测试"""
        await self._run_gradual_stress_test()

    async def _add_users(self, count: int):
        """添加用户"""
        for i in range(count):
            if self.stop_event.is_set():
                break

            user_id = f"stress_user_{len(self.active_users)}"
            task = asyncio.create_task(self._simulate_stress_user(user_id))
            self.active_users.append(user_id)
            self.user_tasks.append(task)

            # 小批量添加
            if i % 10 == 0:
                await asyncio.sleep(0.1)

    async def _remove_all_users(self):
        """移除所有用户"""
        print("👥 停止所有用户...")

        for task in self.user_tasks:
            task.cancel()

        await asyncio.gather(*self.user_tasks, return_exceptions=True)

        self.active_users.clear()
        self.user_tasks.clear()

    async def _gradual_decrease_users(self):
        """逐步减少用户"""
        current_count = len(self.active_users)

        for step in range(0, current_count, 10):
            await self._remove_users(10)
            await asyncio.sleep(5)  # 每次减少后等待系统恢复

    async def _remove_users(self, count: int):
        """移除指定数量的用户"""
        to_remove = min(count, len(self.active_users))

        for i in range(to_remove):
            if self.user_tasks:
                task = self.user_tasks.pop()
                task.cancel()
                self.active_users.pop()

    async def _simulate_stress_user(self, user_id: str):
        """模拟压力用户行为"""
        stress_actions = [
            {
                "name": "heavy_query",
                "weight": 40,
                "endpoint": "/api/market/kline/fetch",
                "params": {"symbol": "600519", "period": "1min"},
            },
            {
                "name": "bulk_data",
                "weight": 30,
                "endpoint": "/api/market/quote/fetch",
                "params": {"symbols": ["600519", "000001", "000002"]},
            },
            {
                "name": "complex_analysis",
                "weight": 20,
                "endpoint": "/api/market/market-data/fetch",
                "params": {"symbol": "600519", "analysis": "detailed"},
            },
            {
                "name": "index_comparison",
                "weight": 10,
                "endpoint": "/api/market/index/fetch",
                "params": {"index_code": "399300"},
            },
        ]

        while not self.stop_event.is_set():
            # 检查断路器
            if self.circuit_breaker and not self.circuit_breaker.allow_request():
                break

            # 选择压力动作
            action = self._select_stress_action(stress_actions)

            # 执行动作
            result = await self._execute_stress_action(action, user_id)

            # 记录结果
            self._record_result(result)

            # 检查断点
            if self._check_breaking_point():
                break

            # 思考时间（较短，增加压力）
            await asyncio.sleep(random.uniform(0.1, 0.5))

    def _select_stress_action(self, actions: List[Dict]) -> Dict:
        """选择压力测试动作"""
        weights = [action["weight"] for action in actions]
        total_weight = sum(weights)
        rand = random.uniform(0, total_weight)

        current_weight = 0
        for action, weight in zip(actions, weights):
            current_weight += weight
            if rand <= current_weight:
                return action

        return actions[0]

    async def _execute_stress_action(self, action: Dict, user_id: str) -> Dict:
        """执行压力测试动作"""
        start_time = time.time()
        success = False
        error_msg = None
        status_code = -1

        try:
            params = action["params"].copy()
            params["_user_id"] = user_id

            async with self.session.get(
                f"{self.base_url}{action['endpoint']}",
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.config.request_timeout),
            ) as response:
                if response.status == 200:
                    await response.text()
                    success = True
                    status_code = response.status
                else:
                    status_code = response.status
                    error_msg = f"HTTP {status_code}"

        except asyncio.TimeoutError:
            status_code = -1
            error_msg = "Request timeout"
        except Exception as e:
            status_code = -1
            error_msg = str(e)

        response_time = (time.time() - start_time) * 1000

        return {
            "user_id": user_id,
            "action": action["name"],
            "status": "success" if success else "failed",
            "response_time_ms": response_time,
            "status_code": status_code,
            "error": error_msg,
        }

    def _record_result(self, result: Dict):
        """记录测试结果"""
        self.result.total_requests += 1

        if result["status"] == "success":
            self.result.successful_requests += 1
            self.result.response_times.append(result["response_time_ms"])

            if self.circuit_breaker:
                self.circuit_breaker.record_success()
        else:
            self.result.failed_requests += 1
            self.result.error_messages.append(result["error"])

            if self.circuit_breaker:
                self.circuit_breaker.record_failure()

    def _check_breaking_point(self) -> bool:
        """检查是否达到断点"""
        total = self.result.total_requests
        if total == 0:
            return False

        failure_rate = self.result.failed_requests / total
        avg_response_time = (
            sum(self.result.response_times) / len(self.result.response_times) if self.result.response_times else 0
        )

        # 断点条件
        breaking_conditions = [
            failure_rate >= self.config.failure_threshold,
            avg_response_time >= self.config.response_time_threshold * 1000,
        ]

        return any(breaking_conditions)

    def _check_system_overload(self) -> bool:
        """检查系统是否过载"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent

            overload_threshold = cpu_percent > 90 or memory_percent > 90
            return overload_threshold
        except Exception:
            return False

    def _check_system_recovered(self) -> bool:
        """检查系统是否恢复"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent

            recovery_threshold = cpu_percent < 70 and memory_percent < 70
            return recovery_threshold
        except Exception:
            return True

    async def _monitor_extreme_state(self):
        """监控极限状态"""
        print("📊 开始监控极限状态...")

        while not self.stop_event.is_set():
            try:
                metrics = self._collect_system_metrics()
                self.result.system_metrics.append(metrics)

                # 打印关键指标
                print(
                    f"   CPU: {metrics['cpu_percent']:.1f}%, "
                    f"内存: {metrics['memory_percent']:.1f}%, "
                    f"活跃用户: {len(self.active_users)}"
                )

                await asyncio.sleep(self.config.monitor_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  监控错误: {str(e)}")
                await asyncio.sleep(5)

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        process = psutil.Process()

        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_rss_mb": process.memory_info().rss / 1024 / 1024,
            "disk_io_read": psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
            "disk_io_write": psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
            "network_io": psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv,
            "active_users": len(self.active_users),
            "total_requests": self.result.total_requests,
            "success_rate": self.result.successful_requests / max(self.result.total_requests, 1),
        }

    async def _cleanup(self):
        """清理资源"""
        await self._remove_all_users()
        if hasattr(self, "session"):
            await self.session.close()

if __name__ == "__main__":
    asyncio.run(run_stress_test_example())
