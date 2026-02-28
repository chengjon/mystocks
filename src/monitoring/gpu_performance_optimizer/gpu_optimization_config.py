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
from dataclasses import dataclass
from datetime import datetime
from typing import List


# GPU相关导入
try:
    import cudf
    import cupy as cp

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    logging.warning("⚠️ GPU库不可用，GPU性能优化管理器将使用模拟模式")

# 导入MyStocks组件

@dataclass
class GPUOptimizationConfig:
    """GPU优化配置"""

    # 自动优化设置
    auto_optimize: bool = True
    optimization_interval: int = 300  # 5分钟优化一次
    performance_threshold: float = 0.8  # 80%性能阈值

    # 内存管理
    memory_optimization: bool = True
    memory_gc_threshold: float = 0.85  # 85%内存清理阈值
    max_memory_usage_mb: float = 7000.0  # 7GB内存限制

    # 任务调度优化
    adaptive_batch_size: bool = True
    min_batch_size: int = 100
    max_batch_size: int = 10000
    optimal_batch_size: int = 1000

    # 负载均衡
    cpu_gpu_balance: bool = True
    cpu_threshold: float = 0.7  # CPU使用率超过70%时卸载到GPU
    gpu_threshold: float = 0.9  # GPU使用率超过90%时卸载到CPU

    # 性能分析
    enable_profiling: bool = True
    profile_operations: int = 100  # 每100次操作进行一次性能分析
    enable_predictive_scaling: bool = True

    # 告警设置
    enable_performance_alerts: bool = True
    performance_degradation_threshold: float = 0.15  # 15%性能下降告警


@dataclass
class GPUMetrics:
    """GPU性能指标"""

    timestamp: datetime
    gpu_utilization: float
    gpu_memory_used: float
    gpu_memory_total: float
    gpu_memory_utilization: float
    gpu_temperature: float
    gpu_power_usage: float
    gpu_fan_speed: float
    cuda_memory_pool_used: float
    cuda_memory_pool_total: float
    processing_time: float
    throughput: float  # 处理速度 (MB/s)
    efficiency_score: float  # 效率评分 0-1


@dataclass
class OptimizationResult:
    """优化结果"""

    timestamp: datetime
    optimization_type: str
    before_metrics: GPUMetrics
    after_metrics: GPUMetrics
    improvement_score: float
    applied_actions: List[str]
    recommendation: str
    success: bool


