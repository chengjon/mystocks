#!/usr/bin/env python3
"""
GPU性能优化管理器
集成GPU加速系统的智能性能优化和自动调优功能
为MyStocks AI交易系统提供GPU资源的智能化管理

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0
依赖: src.gpu.accelerated.*
注意事项: 这是MyStocks v3.0 GPU性能优化核心模块
版权: MyStocks Project © 2025
"""

import logging
import time
from datetime import datetime
from typing import List, Optional

import numpy as np
import pandas as pd

# GPU相关导入
try:
    import cudf
    import cupy as cp

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    logging.warning("⚠️ GPU库不可用，GPU性能优化管理器将使用模拟模式")

# 导入MyStocks组件
from src.monitoring.ai_alert_manager import (
    AIAlertManager,
    get_ai_alert_manager,
)
from src.monitoring.ai_realtime_monitor import (
    AIRealtimeMonitor,
    get_ai_realtime_monitor,
)
from src.monitoring.gpu_performance_optimizer._gpu_performance_optimizer_reporting import (
    GPUPerformanceOptimizerReportingMixin,
)
from src.monitoring.gpu_performance_optimizer.gpu_optimization_config import (
    GPUOptimizationConfig,
    GPUMetrics,
    OptimizationResult,
)

_gpu_optimizer_instance = None


class GPUPerformanceOptimizer(GPUPerformanceOptimizerReportingMixin):
    """GPU性能优化管理器"""

    def __init__(
        self,
        config: Optional[GPUOptimizationConfig] = None,
        alert_manager: Optional[AIAlertManager] = None,
        monitor: Optional[AIRealtimeMonitor] = None,
    ):
        """初始化GPU性能优化管理器"""
        self.config = config or GPUOptimizationConfig()
        self.alert_manager = alert_manager or get_ai_alert_manager()
        self.monitor = monitor or get_ai_realtime_monitor()
        self.logger = logging.getLogger(__name__)

        # GPU状态
        self.gpu_available = GPU_AVAILABLE
        self.gpu_initialized = False

        # 性能指标历史
        self.metrics_history: List[GPUMetrics] = []
        self.optimization_history: List[OptimizationResult] = []
        self.performance_baseline: Optional[GPUMetrics] = None

        # 优化统计
        self.optimization_stats = {
            "total_optimizations": 0,
            "successful_optimizations": 0,
            "performance_improvements": [],
            "memory_recoveries": 0,
            "task_redistributions": 0,
        }

        # 自适应参数
        self.adaptive_params = {
            "current_batch_size": self.config.optimal_batch_size,
            "memory_threshold": self.config.memory_gc_threshold,
            "cpu_gpu_balance_factor": 1.0,
            "last_optimization_time": None,
        }

        # 性能分析器
        self.profiler_enabled = self.config.enable_profiling
        self.operation_count = 0

        self.logger.info("GPU性能优化管理器初始化完成")

    async def initialize(self) -> bool:
        """初始化GPU环境"""
        try:
            if not self.gpu_available:
                self.logger.warning("GPU库不可用，使用模拟模式")
                return False

            # 初始化GPU环境
            if not self.gpu_initialized:
                # 设置GPU内存池
                cp.cuda.set_allocator(cp.cuda.MemoryPool())

                # 获取GPU信息
                device_count = cp.cuda.runtime.getDeviceCount()
                self.logger.info("检测到 %s 个GPU设备", device_count)

                # 初始化基准测试
                await self._initialize_baseline()

                self.gpu_initialized = True
                self.logger.info("GPU环境初始化成功")

            return True

        except Exception as e:
            self.logger.error("GPU初始化失败: %s", e)
            return False

    async def _initialize_baseline(self):
        """初始化性能基准"""
        try:
            # 创建基准测试数据
            test_data = self._create_benchmark_data()

            # 执行基准测试
            baseline_metrics = await self._run_performance_benchmark(test_data)
            self.performance_baseline = baseline_metrics

            self.logger.info("性能基准建立完成 - 效率评分: %s", baseline_metrics.efficiency_score)

        except Exception as e:
            self.logger.error("基准测试失败: %s", e)

    def _create_benchmark_data(self) -> pd.DataFrame:
        """创建基准测试数据"""
        np.random.seed(42)
        n_samples = 10000
        n_features = 100

        data = {f"feature_{i}": np.random.randn(n_samples) for i in range(n_features)}
        data["target"] = np.random.randn(n_samples)
        data["timestamp"] = pd.date_range("2024-01-01", periods=n_samples, freq="1min")

        return pd.DataFrame(data)

    async def _run_performance_benchmark(self, data: pd.DataFrame) -> GPUMetrics:
        """运行性能基准测试"""
        start_time = time.time()

        try:
            # GPU操作基准测试
            if self.gpu_available and self.gpu_initialized:
                # 数据传输到GPU
                data_gpu = cudf.DataFrame(data)

                # GPU计算操作
                gpu_start = time.time()
                result = data_gpu.mean()
                time.time() - gpu_start

                # 清理GPU内存
                del data_gpu, result
                cp.cuda.runtime.deviceSynchronize()

            # 获取GPU指标
            metrics = await self._collect_gpu_metrics()
            metrics.processing_time = time.time() - start_time
            metrics.throughput = len(data) / metrics.processing_time if metrics.processing_time > 0 else 0

            return metrics

        except Exception as e:
            self.logger.error("基准测试失败: %s", e)
            # 返回默认指标
            return GPUMetrics(
                timestamp=datetime.now(),
                gpu_utilization=0.0,
                gpu_memory_used=0.0,
                gpu_memory_total=8192.0,
                gpu_memory_utilization=0.0,
                gpu_temperature=0.0,
                gpu_power_usage=0.0,
                gpu_fan_speed=0.0,
                cuda_memory_pool_used=0.0,
                cuda_memory_pool_total=0.0,
                processing_time=time.time() - start_time,
                throughput=0.0,
                efficiency_score=0.0,
            )

    async def _collect_gpu_metrics(self) -> GPUMetrics:
        """收集GPU指标"""
        if not self.gpu_available:
            # 返回模拟指标
            return GPUMetrics(
                timestamp=datetime.now(),
                gpu_utilization=50.0 + np.random.normal(0, 10),
                gpu_memory_used=4000.0 + np.random.normal(0, 1000),
                gpu_memory_total=8192.0,
                gpu_memory_utilization=50.0,
                gpu_temperature=65.0 + np.random.normal(0, 5),
                gpu_power_usage=150.0 + np.random.normal(0, 20),
                gpu_fan_speed=3000.0 + np.random.normal(0, 200),
                cuda_memory_pool_used=0.0,
                cuda_memory_pool_total=0.0,
                processing_time=0.0,
                throughput=0.0,
                efficiency_score=0.8,
            )

        try:
            # 实际GPU指标收集
            cp.cuda.Device(0)

            # GPU利用率 (模拟)
            gpu_util = 50.0 + np.random.normal(0, 15)

            # GPU内存信息
            memory_info = cp.cuda.mem_get_info()
            memory_used = memory_info[1] - memory_info[0]
            memory_total = memory_info[1]
            memory_utilization = (memory_used / memory_total) * 100 if memory_total > 0 else 0

            # CUDA内存池信息
            pool = cp.cuda.get_default_memory_pool()
            pool_used = pool.used_bytes()
            pool_total = pool.total_bytes()

            # 效率评分计算
            efficiency = self._calculate_efficiency_score(gpu_util, memory_utilization, pool_used, pool_total)

            return GPUMetrics(
                timestamp=datetime.now(),
                gpu_utilization=max(0, min(100, gpu_util)),
                gpu_memory_used=memory_used / 1024 / 1024,  # 转换为MB
                gpu_memory_total=memory_total / 1024 / 1024,  # 转换为MB
                gpu_memory_utilization=memory_utilization,
                gpu_temperature=70.0 + np.random.normal(0, 10),  # 模拟温度
                gpu_power_usage=120.0 + np.random.normal(0, 30),  # 模拟功耗
                gpu_fan_speed=2500.0 + np.random.normal(0, 300),  # 模拟风扇转速
                cuda_memory_pool_used=pool_used / 1024 / 1024,  # 转换为MB
                cuda_memory_pool_total=pool_total / 1024 / 1024,  # 转换为MB
                processing_time=0.0,
                throughput=0.0,
                efficiency_score=efficiency,
            )

        except Exception as e:
            self.logger.error("GPU指标收集失败: %s", e)
            # 返回默认指标
            return GPUMetrics(
                timestamp=datetime.now(),
                gpu_utilization=0.0,
                gpu_memory_used=0.0,
                gpu_memory_total=8192.0,
                gpu_memory_utilization=0.0,
                gpu_temperature=0.0,
                gpu_power_usage=0.0,
                gpu_fan_speed=0.0,
                cuda_memory_pool_used=0.0,
                cuda_memory_pool_total=0.0,
                processing_time=0.0,
                throughput=0.0,
                efficiency_score=0.0,
            )

    def _calculate_efficiency_score(
        self, gpu_util: float, memory_util: float, pool_used: int, pool_total: int
    ) -> float:
        """计算GPU效率评分"""
        try:
            # 利用率评分 (40%)
            utilization_score = min(gpu_util / 100, 1.0) * 0.4

            # 内存使用评分 (30%)
            memory_score = (1 - abs(memory_util - 70) / 100) * 0.3  # 70%为最优内存使用率

            # 内存池效率评分 (30%)
            pool_util = (pool_used / pool_total) if pool_total > 0 else 0
            pool_score = (1 - abs(pool_util - 0.8)) * 0.3  # 80%为最优内存池利用率

            total_score = max(0, utilization_score + memory_score + pool_score)

            return min(1.0, total_score)

        except Exception as e:
            self.logger.error("效率评分计算失败: %s", e)
            return 0.5

    async def optimize_performance(self) -> OptimizationResult:
        """执行性能优化"""
        before_metrics = await self._collect_gpu_metrics()
        applied_actions = []
        improvement_score = 0.0

        try:
            # 内存优化
            if self.config.memory_optimization:
                memory_action = await self._optimize_memory()
                if memory_action:
                    applied_actions.append(memory_action)

            # 批次大小优化
            if self.config.adaptive_batch_size:
                batch_action = await self._optimize_batch_size(before_metrics)
                if batch_action:
                    applied_actions.append(batch_action)

            # CPU-GPU负载均衡
            if self.config.cpu_gpu_balance:
                balance_action = await self._optimize_cpu_gpu_balance()
                if balance_action:
                    applied_actions.append(balance_action)

            # 收集优化后指标
            after_metrics = await self._collect_gpu_metrics()

            # 计算改进评分
            improvement_score = self._calculate_improvement_score(before_metrics, after_metrics)

            # 生成建议
            recommendation = self._generate_optimization_recommendation(before_metrics, after_metrics, applied_actions)

            # 创建优化结果
            result = OptimizationResult(
                timestamp=datetime.now(),
                optimization_type="comprehensive",
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                improvement_score=improvement_score,
                applied_actions=applied_actions,
                recommendation=recommendation,
                success=len(applied_actions) > 0,
            )

            # 记录优化结果
            self.optimization_history.append(result)
            self.optimization_stats["total_optimizations"] += 1
            if improvement_score > 0:
                self.optimization_stats["successful_optimizations"] += 1
                self.optimization_stats["performance_improvements"].append(improvement_score)

            # 更新自适应参数
            self.adaptive_params["last_optimization_time"] = datetime.now()

            # 发送告警通知
            if improvement_score < -0.1:  # 性能下降超过10%
                await self._send_performance_alert(before_metrics, after_metrics, improvement_score)

            self.logger.info("性能优化完成 - 改进评分: %s, 操作: %s个", improvement_score, len(applied_actions))

            return result

        except Exception as e:
            self.logger.error("性能优化失败: %s", e)
            return OptimizationResult(
                timestamp=datetime.now(),
                optimization_type="failed",
                before_metrics=before_metrics,
                after_metrics=before_metrics,
                improvement_score=0.0,
                applied_actions=["error"],
                recommendation=f"优化失败: {str(e)}",
                success=False,
            )

    async def _optimize_memory(self) -> Optional[str]:
        """内存优化"""
        try:
            metrics = await self._collect_gpu_metrics()

            if metrics.gpu_memory_utilization > self.config.memory_gc_threshold * 100:
                # 触发GPU内存清理
                if self.gpu_available:
                    # 清理CUDA内存池
                    pool = cp.cuda.get_default_memory_pool()
                    pool.free_all_blocks()

                    # 强制同步
                    cp.cuda.runtime.deviceSynchronize()

                    self.optimization_stats["memory_recoveries"] += 1
                    return f"GPU内存清理 - 释放 {metrics.gpu_memory_utilization:.1f}% 内存使用"
                else:
                    return "模拟内存清理操作"

            return None

        except Exception as e:
            self.logger.error("内存优化失败: %s", e)
            return None

    async def _optimize_batch_size(self, metrics: GPUMetrics) -> Optional[str]:
        """批次大小优化"""
        try:
            # 基于GPU利用率调整批次大小
            current_batch = self.adaptive_params["current_batch_size"]

            if metrics.gpu_utilization < 50:  # GPU利用率低，增加批次大小
                new_batch = min(current_batch * 1.2, self.config.max_batch_size)
                self.adaptive_params["current_batch_size"] = int(new_batch)
                return f"批次大小优化: {current_batch} → {int(new_batch)} (增加)"

            elif metrics.gpu_utilization > 90:  # GPU利用率过高，减少批次大小
                new_batch = max(current_batch * 0.8, self.config.min_batch_size)
                self.adaptive_params["current_batch_size"] = int(new_batch)
                return f"批次大小优化: {current_batch} → {int(new_batch)} (减少)"

            return None

        except Exception as e:
            self.logger.error("批次大小优化失败: %s", e)
            return None

    async def _optimize_cpu_gpu_balance(self) -> Optional[str]:
        """CPU-GPU负载均衡优化"""
        try:
            # 获取系统负载信息
            cpu_usage = await self._get_cpu_usage()
            gpu_metrics = await self._collect_gpu_metrics()

            balance_factor = self.adaptive_params["cpu_gpu_balance_factor"]

            # 如果CPU使用率高，卸载更多任务到GPU
            if cpu_usage > self.config.cpu_threshold * 100 and gpu_metrics.gpu_utilization < 80:
                new_factor = min(balance_factor * 1.1, 2.0)
                self.adaptive_params["cpu_gpu_balance_factor"] = new_factor
                self.optimization_stats["task_redistributions"] += 1
                return f"负载均衡优化: CPU ({cpu_usage:.1f}%) → GPU卸载因子 {balance_factor:.2f} → {new_factor:.2f}"

            # 如果GPU使用率高，卸载任务到CPU
            elif gpu_metrics.gpu_utilization > self.config.gpu_threshold * 100:
                new_factor = max(balance_factor * 0.9, 0.5)
                self.adaptive_params["cpu_gpu_balance_factor"] = new_factor
                self.optimization_stats["task_redistributions"] += 1
                return (
                    f"负载均衡优化: GPU ({gpu_metrics.gpu_utilization:.1f}%) → "
                    f"CPU卸载因子 {balance_factor:.2f} → {new_factor:.2f}"
                )

            return None

        except Exception as e:
            self.logger.error("负载均衡优化失败: %s", e)
            return None

    async def _get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        try:
            import psutil

            return psutil.cpu_percent(interval=1)
        except ImportError:
            # 模拟CPU使用率
            return 50.0 + np.random.normal(0, 10)

    def _calculate_improvement_score(self, before: GPUMetrics, after: GPUMetrics) -> float:
        """计算改进评分"""
        try:
            # 效率评分改进 (50%)
            efficiency_improvement = after.efficiency_score - before.efficiency_score

            # 处理速度改进 (30%)
            speed_improvement = 0
            if before.processing_time > 0:
                speed_improvement = (before.processing_time - after.processing_time) / before.processing_time

            # 内存使用改进 (20%)
            memory_improvement = (before.gpu_memory_utilization - after.gpu_memory_utilization) / 100

            # 综合评分
            total_score = efficiency_improvement * 0.5 + speed_improvement * 0.3 + memory_improvement * 0.2

            return max(-1.0, min(1.0, total_score))  # 限制在 -1 到 1 之间

        except Exception as e:
            self.logger.error("改进评分计算失败: %s", e)
            return 0.0

    def _generate_optimization_recommendation(self, before: GPUMetrics, after: GPUMetrics, actions: List[str]) -> str:
        """生成优化建议"""
        try:
            improvement = self._calculate_improvement_score(before, after)

            if improvement > 0.2:
                return f"✅ 性能显著提升 (+{improvement:.1%}) - 建议保持当前配置"
            elif improvement > 0.05:
                return f"✅ 性能适度提升 (+{improvement:.1%}) - 当前优化策略有效"
            elif improvement > -0.05:
                return f"➖ 性能基本稳定 ({improvement:.1%}) - 可考虑其他优化方案"
            elif improvement > -0.2:
                return f"⚠️ 性能小幅下降 ({improvement:.1%}) - 检查GPU配置和系统负载"
            else:
                return f"❌ 性能显著下降 ({improvement:.1%}) - 建议检查GPU硬件状态"

        except Exception as e:
            self.logger.error("建议生成失败: %s", e)
            return "优化建议生成失败"



def get_gpu_performance_optimizer() -> GPUPerformanceOptimizer:
    """获取GPU性能优化管理器单例"""
    global _gpu_optimizer_instance
    if _gpu_optimizer_instance is None:
        _gpu_optimizer_instance = GPUPerformanceOptimizer()
    return _gpu_optimizer_instance


async def initialize_gpu_optimizer(
    config: Optional[GPUOptimizationConfig] = None,
) -> GPUPerformanceOptimizer:
    """初始化GPU优化管理器"""
    optimizer = get_gpu_performance_optimizer()
    if config:
        optimizer.config = config

    success = await optimizer.initialize()
    if not success:
        logging.warning("GPU优化管理器初始化失败，将使用模拟模式")

    return optimizer

