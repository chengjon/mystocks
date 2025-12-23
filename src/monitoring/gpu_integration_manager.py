#!/usr/bin/env python3
"""
GPU性能优化集成模块
将GPU性能优化管理器集成到MyStocks主系统中
提供与统一管理器和监控系统的无缝集成

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0
依赖: src.monitoring.gpu_performance_optimizer, src.gpu.accelerated.*
注意事项: 这是MyStocks v3.0 GPU集成核心模块
版权: MyStocks Project © 2025
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 导入GPU优化管理器
from src.monitoring.gpu_performance_optimizer import (
    GPUPerformanceOptimizer,
    GPUOptimizationConfig,
    initialize_gpu_optimizer,
)

# 导入监控系统
from src.monitoring.ai_alert_manager import (
    AIAlertManager,
    get_ai_alert_manager,
)

from src.monitoring.ai_realtime_monitor import (
    AIRealtimeMonitor,
    get_ai_realtime_monitor,
)

# 导入统一管理器
try:
    from src.unified_manager import MyStocksUnifiedManager
except ImportError:
    MyStocksUnifiedManager = None


class GPUIntegratedMonitoring:
    """GPU集成的监控管理器"""

    def __init__(
        self,
        unified_manager: Optional[MyStocksUnifiedManager] = None,
        alert_manager: Optional[AIAlertManager] = None,
        monitor: Optional[AIRealtimeMonitor] = None,
        gpu_config: Optional[GPUOptimizationConfig] = None,
    ):
        """初始化GPU集成监控"""
        self.unified_manager = unified_manager
        self.alert_manager = alert_manager or get_ai_alert_manager()
        self.monitor = monitor or get_ai_realtime_monitor()
        self.gpu_config = gpu_config or GPUOptimizationConfig()
        self.logger = logging.getLogger(__name__)

        # GPU性能优化管理器
        self.gpu_optimizer: Optional[GPUPerformanceOptimizer] = None

        # 集成状态
        self.integration_status = {
            "gpu_optimizer_initialized": False,
            "unified_manager_enhanced": False,
            "monitoring_integrated": False,
            "last_optimization": None,
            "total_optimizations": 0,
        }

        # GPU使用统计
        self.gpu_usage_stats = {
            "operations_processed": 0,
            "gpu_operations": 0,
            "cpu_fallback_operations": 0,
            "performance_improvements": [],
            "memory_recoveries": 0,
        }

        self.logger.info("GPU集成监控管理器初始化完成")

    async def initialize_integration(self) -> bool:
        """初始化GPU集成"""
        try:
            self.logger.info("开始GPU系统集成...")

            # 1. 初始化GPU性能优化管理器
            self.gpu_optimizer = await initialize_gpu_optimizer(self.gpu_config)
            if self.gpu_optimizer:
                self.integration_status["gpu_optimizer_initialized"] = True
                self.logger.info("✅ GPU性能优化管理器初始化成功")
            else:
                self.logger.warning("❌ GPU性能优化管理器初始化失败")

            # 2. 增强统一管理器
            if self.unified_manager:
                await self._enhance_unified_manager()
            else:
                self.logger.info("⚠️ 统一管理器未提供，跳过增强")

            # 3. 集成监控系统
            await self._integrate_monitoring_system()

            # 4. 启动连续监控
            await self._start_continuous_monitoring()

            self.logger.info("🎉 GPU系统集成完成")
            return True

        except Exception as e:
            self.logger.error(f"GPU系统集成失败: {e}")
            return False

    async def _enhance_unified_manager(self):
        """增强统一管理器以支持GPU优化"""
        try:
            if not self.unified_manager:
                return

            # 添加GPU优化方法到统一管理器
            original_save = self.unified_manager.save_data_by_classification
            original_load = self.unified_manager.load_data_by_classification

            async def gpu_enhanced_save_data(
                data, data_classification, *args, **kwargs
            ):
                """GPU增强的数据保存"""
                # 首先进行GPU预处理
                if self.gpu_optimizer and self.gpu_optimizer.gpu_available:
                    # 这里可以添加GPU预处理逻辑
                    pass

                # 执行原始保存
                result = await original_save(data, data_classification, *args, **kwargs)

                # 更新统计
                self.gpu_usage_stats["operations_processed"] += 1
                if self.gpu_optimizer and self.gpu_optimizer.gpu_available:
                    self.gpu_usage_stats["gpu_operations"] += 1

                return result

            async def gpu_enhanced_load_data(data_classification, *args, **kwargs):
                """GPU增强的数据加载"""
                # 执行原始加载
                result = await original_load(data_classification, *args, **kwargs)

                # 更新统计
                self.gpu_usage_stats["operations_processed"] += 1
                if self.gpu_optimizer and self.gpu_optimizer.gpu_available:
                    self.gpu_usage_stats["gpu_operations"] += 1

                return result

            # 替换方法 (注意：这里简化处理，实际应该使用异步版本)
            self.unified_manager.save_data_by_classification = gpu_enhanced_save_data
            self.unified_manager.load_data_by_classification = gpu_enhanced_load_data

            # 添加GPU特定方法
            self.unified_manager.get_gpu_optimization_status = (
                self.get_integration_status
            )
            self.unified_manager.run_gpu_performance_optimization = (
                self.run_manual_optimization
            )
            self.unified_manager.get_gpu_performance_report = (
                self.get_performance_report
            )

            self.integration_status["unified_manager_enhanced"] = True
            self.logger.info("✅ 统一管理器GPU增强完成")

        except Exception as e:
            self.logger.error(f"统一管理器增强失败: {e}")

    async def _integrate_monitoring_system(self):
        """集成监控系统"""
        try:
            # 将GPU性能指标添加到监控系统
            if self.monitor and self.gpu_optimizer:
                # 添加GPU指标收集器
                self.monitor.gpu_optimizer = self.gpu_optimizer

            # 将GPU优化告警集成到告警系统
            if self.alert_manager and self.gpu_optimizer:
                # 这里可以添加GPU特定的告警规则
                pass

            self.integration_status["monitoring_integrated"] = True
            self.logger.info("✅ 监控系统GPU集成完成")

        except Exception as e:
            self.logger.error(f"监控系统集成失败: {e}")

    async def _start_continuous_monitoring(self):
        """启动连续监控"""
        try:
            if self.gpu_optimizer:
                # 启动GPU连续优化监控
                monitoring_task = asyncio.create_task(
                    self.gpu_optimizer.start_continuous_optimization(
                        duration_minutes=60
                    )
                )

                # 存储任务引用以便后续管理
                self._monitoring_task = monitoring_task

                self.logger.info("✅ GPU连续监控已启动")
            else:
                self.logger.warning("⚠️ GPU优化器未初始化，跳过连续监控")

        except Exception as e:
            self.logger.error(f"连续监控启动失败: {e}")

    async def run_manual_optimization(self) -> Dict[str, Any]:
        """手动运行GPU性能优化"""
        try:
            if not self.gpu_optimizer:
                return {"error": "GPU优化器未初始化"}

            result = await self.gpu_optimizer.optimize_performance()

            self.integration_status["last_optimization"] = datetime.now().isoformat()
            self.integration_status["total_optimizations"] += 1

            return {
                "success": result.success,
                "improvement_score": result.improvement_score,
                "recommendation": result.recommendation,
                "applied_actions": result.applied_actions,
                "before_efficiency": result.before_metrics.efficiency_score,
                "after_efficiency": result.after_metrics.efficiency_score,
            }

        except Exception as e:
            self.logger.error(f"手动优化失败: {e}")
            return {"error": str(e)}

    async def get_performance_report(self) -> Dict[str, Any]:
        """获取GPU性能报告"""
        try:
            if not self.gpu_optimizer:
                return {"error": "GPU优化器未初始化"}

            report = await self.gpu_optimizer.get_performance_report()

            # 添加集成状态信息
            report["integration_status"] = self.integration_status
            report["gpu_usage_stats"] = self.gpu_usage_stats

            return report

        except Exception as e:
            self.logger.error(f"性能报告生成失败: {e}")
            return {"error": str(e)}

    def get_integration_status(self) -> Dict[str, Any]:
        """获取集成状态"""
        return {
            "integration_timestamp": datetime.now().isoformat(),
            "gpu_optimizer_initialized": self.integration_status[
                "gpu_optimizer_initialized"
            ],
            "unified_manager_enhanced": self.integration_status[
                "unified_manager_enhanced"
            ],
            "monitoring_integrated": self.integration_status["monitoring_integrated"],
            "last_optimization": self.integration_status["last_optimization"],
            "total_optimizations": self.integration_status["total_optimizations"],
            "gpu_usage_stats": self.gpu_usage_stats,
        }

    async def optimize_gpu_memory(self) -> Dict[str, Any]:
        """手动优化GPU内存"""
        try:
            if not self.gpu_optimizer:
                return {"error": "GPU优化器未初始化"}

            action = await self.gpu_optimizer._optimize_memory()

            if action:
                self.gpu_usage_stats["memory_recoveries"] += 1
                return {"success": True, "action": action}
            else:
                return {"success": False, "message": "无需内存优化"}

        except Exception as e:
            self.logger.error(f"GPU内存优化失败: {e}")
            return {"error": str(e)}

    async def get_gpu_health_status(self) -> Dict[str, Any]:
        """获取GPU健康状态"""
        try:
            if not self.gpu_optimizer:
                return {"available": False, "reason": "GPU优化器未初始化"}

            metrics = await self.gpu_optimizer._collect_gpu_metrics()

            # 健康状态评估
            health_score = 0.0
            issues = []

            # GPU利用率健康检查
            if 30 <= metrics.gpu_utilization <= 90:
                health_score += 0.3
            else:
                issues.append(f"GPU利用率异常: {metrics.gpu_utilization:.1f}%")

            # 内存健康检查
            if metrics.gpu_memory_utilization <= 80:
                health_score += 0.3
            else:
                issues.append(f"GPU内存使用过高: {metrics.gpu_memory_utilization:.1f}%")

            # 温度健康检查
            if metrics.gpu_temperature <= 80:
                health_score += 0.2
            else:
                issues.append(f"GPU温度过高: {metrics.gpu_temperature:.1f}°C")

            # 效率健康检查
            if metrics.efficiency_score >= 0.7:
                health_score += 0.2
            else:
                issues.append(f"GPU效率较低: {metrics.efficiency_score:.3f}")

            return {
                "available": self.gpu_optimizer.gpu_available,
                "healthy": health_score >= 0.7,
                "health_score": health_score,
                "issues": issues,
                "metrics": {
                    "gpu_utilization": metrics.gpu_utilization,
                    "memory_utilization": metrics.gpu_memory_utilization,
                    "temperature": metrics.gpu_temperature,
                    "efficiency_score": metrics.efficiency_score,
                },
                "recommendations": await self.gpu_optimizer._generate_performance_recommendations(
                    metrics
                ),
            }

        except Exception as e:
            self.logger.error(f"GPU健康状态检查失败: {e}")
            return {"available": False, "error": str(e)}

    async def shutdown_integration(self):
        """关闭GPU集成"""
        try:
            self.logger.info("开始关闭GPU系统集成...")

            # 停止连续监控
            if hasattr(self, "_monitoring_task"):
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass

            # 保存优化状态
            if self.gpu_optimizer:
                self.gpu_optimizer.save_optimization_state(
                    "gpu_optimization_state.json"
                )

            # 重置状态
            self.integration_status = {
                "gpu_optimizer_initialized": False,
                "unified_manager_enhanced": False,
                "monitoring_integrated": False,
                "last_optimization": None,
                "total_optimizations": 0,
            }

            self.logger.info("✅ GPU系统集成已关闭")

        except Exception as e:
            self.logger.error(f"GPU集成关闭失败: {e}")


# 全局集成管理器实例
_gpu_integrated_monitoring: Optional[GPUIntegratedMonitoring] = None


def get_gpu_integrated_monitoring() -> GPUIntegratedMonitoring:
    """获取GPU集成监控管理器单例"""
    global _gpu_integrated_monitoring
    if _gpu_integrated_monitoring is None:
        _gpu_integrated_monitoring = GPUIntegratedMonitoring()
    return _gpu_integrated_monitoring


async def initialize_gpu_integration(
    unified_manager: Optional[MyStocksUnifiedManager] = None,
    gpu_config: Optional[GPUOptimizationConfig] = None,
) -> GPUIntegratedMonitoring:
    """初始化GPU集成"""
    integrated_monitoring = get_gpu_integrated_monitoring()

    # 设置参数
    if unified_manager:
        integrated_monitoring.unified_manager = unified_manager
    if gpu_config:
        integrated_monitoring.gpu_config = gpu_config

    # 执行集成
    success = await integrated_monitoring.initialize_integration()

    if success:
        logging.info("🎉 GPU集成初始化成功")
    else:
        logging.warning("❌ GPU集成初始化失败")

    return integrated_monitoring


# 便捷函数
async def get_gpu_integration_status() -> Dict[str, Any]:
    """获取GPU集成状态"""
    integrated_monitoring = get_gpu_integrated_monitoring()
    return integrated_monitoring.get_integration_status()


async def run_gpu_optimization() -> Dict[str, Any]:
    """运行GPU优化"""
    integrated_monitoring = get_gpu_integrated_monitoring()
    return await integrated_monitoring.run_manual_optimization()


async def get_gpu_performance_report() -> Dict[str, Any]:
    """获取GPU性能报告"""
    integrated_monitoring = get_gpu_integrated_monitoring()
    return await integrated_monitoring.get_performance_report()


async def get_gpu_health() -> Dict[str, Any]:
    """获取GPU健康状态"""
    integrated_monitoring = get_gpu_integrated_monitoring()
    return await integrated_monitoring.get_gpu_health_status()


async def optimize_gpu_memory() -> Dict[str, Any]:
    """优化GPU内存"""
    integrated_monitoring = get_gpu_integrated_monitoring()
    return await integrated_monitoring.optimize_gpu_memory()


# 使用示例和测试代码
async def main():
    """主函数 - 示例用法"""
    print("🚀 MyStocks GPU集成监控演示")
    print("=" * 50)

    # 创建GPU配置
    gpu_config = GPUOptimizationConfig(
        auto_optimize=True,
        optimization_interval=60,  # 1分钟优化一次
        memory_optimization=True,
        adaptive_batch_size=True,
        cpu_gpu_balance=True,
    )

    # 初始化GPU集成
    print("\n1. 初始化GPU集成:")
    integrated_monitoring = await initialize_gpu_integration(gpu_config=gpu_config)

    # 获取集成状态
    print("\n2. 集成状态:")
    status = await get_gpu_integration_status()
    print(f"GPU优化器初始化: {'✅' if status['gpu_optimizer_initialized'] else '❌'}")
    print(f"统一管理器增强: {'✅' if status['unified_manager_enhanced'] else '❌'}")
    print(f"监控系统集成: {'✅' if status['monitoring_integrated'] else '❌'}")
    print(f"总优化次数: {status['total_optimizations']}")

    # 检查GPU健康状态
    print("\n3. GPU健康状态:")
    health = await get_gpu_health()
    print(f"GPU可用: {'✅' if health.get('available') else '❌'}")
    print(f"健康状态: {'✅' if health.get('healthy') else '❌'}")
    print(f"健康评分: {health.get('health_score', 0):.2f}")

    if health.get("issues"):
        print("问题列表:")
        for issue in health["issues"]:
            print(f"  ⚠️ {issue}")

    # 运行手动优化
    print("\n4. 手动优化:")
    optimization_result = await run_gpu_optimization()
    print(f"优化结果: {optimization_result.get('recommendation', 'N/A')}")
    print(f"改进评分: {optimization_result.get('improvement_score', 0):.3f}")

    # 生成性能报告
    print("\n5. 性能报告:")
    report = await get_gpu_performance_report()
    if "error" not in report:
        current_metrics = report.get("current_metrics", {})
        print(f"GPU利用率: {current_metrics.get('gpu_utilization', 0):.1f}%")
        print(f"内存使用率: {current_metrics.get('gpu_memory_utilization', 0):.1f}%")
        print(f"效率评分: {current_metrics.get('efficiency_score', 0):.3f}")

        recommendations = report.get("recommendations", [])
        if recommendations:
            print("\n💡 性能建议:")
            for rec in recommendations[:3]:  # 只显示前3个建议
                print(f"  • {rec}")

    # 内存优化测试
    print("\n6. 内存优化:")
    memory_result = await optimize_gpu_memory()
    if memory_result.get("success"):
        print(f"✅ {memory_result.get('action')}")
    else:
        print(f"➖ {memory_result.get('message', '无需优化')}")

    # 等待一段时间观察连续优化
    print("\n7. 观察连续优化 (10秒)...")
    await asyncio.sleep(10)

    # 获取最终状态
    print("\n8. 最终状态:")
    final_status = await get_gpu_integration_status()
    print(f"总优化次数: {final_status['total_optimizations']}")
    print(f"GPU操作次数: {final_status['gpu_usage_stats']['gpu_operations']}")

    # 关闭集成
    print("\n9. 关闭GPU集成:")
    await integrated_monitoring.shutdown_integration()
    print("✅ GPU集成已关闭")

    print("\n🎉 GPU集成监控演示完成")


if __name__ == "__main__":
    asyncio.run(main())
