"""智能阈值管理器 - 工厂函数"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from src.monitoring.threshold.dataclasses import OptimizationResult

from .manager import IntelligentThresholdManager

_intelligent_threshold_manager = None

def get_intelligent_threshold_manager() -> IntelligentThresholdManager:
    """获取智能阈值管理器单例"""
    global _intelligent_threshold_manager

    if _intelligent_threshold_manager is None:
        _intelligent_threshold_manager = IntelligentThresholdManager()

    return _intelligent_threshold_manager


# 便捷函数
async def create_intelligent_threshold(
    config: Optional[Dict[str, Any]] = None,
) -> IntelligentThresholdManager:
    """创建智能阈值管理器"""
    return IntelligentThresholdManager(config)


async def optimize_all_thresholds() -> Dict[str, OptimizationResult]:
    """优化所有阈值"""
    manager = get_intelligent_threshold_manager()
    return await manager.optimize_thresholds()


async def process_metric(rule_name: str, value: float, timestamp: Optional[datetime] = None) -> Dict[str, Any]:
    """处理指标值"""
    manager = get_intelligent_threshold_manager()
    return await manager.process_metric_value(rule_name, value, timestamp)


if __name__ == "__main__":
    """示例用法"""

    async def main():
        # 创建智能阈值管理器
        manager = IntelligentThresholdManager()

        print("🤖 智能阈值算法和误报优化模块演示")
        print("=" * 50)

        # 模拟数据
        import random

        rule_name = "cpu_usage_high"

        # 模拟CPU使用率数据
        for i in range(50):
            value = random.gauss(60, 15)  # 正态分布，均值60，标准差15
            await manager.process_metric_value(rule_name, value)

        # 获取规则状态
        status = manager.get_threshold_status()
        print(f"\n📊 阈值状态: {status['total_rules']}个规则")

        # 优化阈值
        print("\n🔧 开始优化阈值...")
        results = await manager.optimize_thresholds(rule_name)

        for rule_name, result in results.items():
            print(f"规则: {rule_name}")
            print(f"  当前阈值: {status['rules_status'][rule_name]['current_threshold']:.2f}")
            print(f"  推荐阈值: {result.recommended_threshold:.2f}")
            print(f"  置信度: {result.confidence_score:.3f}")
            print(f"  预期改进: {result.expected_improvement:.3f}")
            print(f"  推理: {result.reasoning}")

        # 应用优化
        if results:
            rule_name = list(results.keys())[0]
            optimization_result = results[rule_name]
            success = await manager.apply_optimization(rule_name, optimization_result)
            print(f"\n✅ 优化应用{'成功' if success else '失败'}")

        # 导出配置
        config = manager.export_configuration()
        print(f"\n💾 配置已导出 ({len(config)}字符)")

        print("\n🎉 演示完成!")

    # 运行演示
    asyncio.run(main())
