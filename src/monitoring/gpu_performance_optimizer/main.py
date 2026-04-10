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

import asyncio
import logging


# GPU相关导入
try:
    import cudf
    import cupy as cp

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    logging.warning("⚠️ GPU库不可用，GPU性能优化管理器将使用模拟模式")

from src.monitoring.gpu_performance_optimizer.gpu_optimization_config import GPUOptimizationConfig
from src.monitoring.gpu_performance_optimizer.gpu_performance_optimizer import initialize_gpu_optimizer

async def main():
    """主函数 - 示例用法"""
    print("🚀 MyStocks GPU性能优化管理器演示")
    print("=" * 50)

    # 创建配置
    config = GPUOptimizationConfig(
        auto_optimize=True,
        optimization_interval=60,  # 1分钟优化一次
        memory_optimization=True,
        adaptive_batch_size=True,
        cpu_gpu_balance=True,
    )

    # 初始化优化管理器
    optimizer = await initialize_gpu_optimizer(config)

    # 执行单次优化
    print("\n1. 执行性能优化:")
    result = await optimizer.optimize_performance()
    print(f"优化结果: {result.recommendation}")
    print(f"改进评分: {result.improvement_score:.3f}")
    print(f"执行操作: {', '.join(result.applied_actions)}")

    # 生成性能报告
    print("\n2. 生成性能报告:")
    report = await optimizer.get_performance_report()
    current_metrics = report.get("current_metrics", {})
    print(f"GPU利用率: {current_metrics.get('gpu_utilization', 0):.1f}%")
    print(f"内存使用率: {current_metrics.get('gpu_memory_utilization', 0):.1f}%")
    print(f"效率评分: {current_metrics.get('efficiency_score', 0):.3f}")

    # 生成建议
    recommendations = report.get("recommendations", [])
    if recommendations:
        print("\n💡 性能建议:")
        for rec in recommendations:
            print(f"  • {rec}")

    # 启动连续优化 (演示用30秒)
    print("\n3. 启动连续优化监控 (30秒演示):")
    optimization_task = asyncio.create_task(optimizer.start_continuous_optimization(duration_minutes=1))

    # 等待一段时间
    await asyncio.sleep(30)
    optimization_task.cancel()

    try:
        await optimization_task
    except asyncio.CancelledError:
        print("连续优化监控已结束")

    # 保存状态
    print("\n4. 保存优化状态:")
    optimizer.save_optimization_state("gpu_optimization_state.json")
    print("状态保存完成")

    print("\n✅ GPU性能优化管理器演示完成")


